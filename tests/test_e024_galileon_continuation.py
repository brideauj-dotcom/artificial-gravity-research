import math
import unittest

import numpy as np

from models.e023_galileon_annulus import (
    AnnulusConfig,
    build_spherical_laplacian,
    cell_volume_weights_dimensionless,
    nonlinear_invariant,
    orthonormal_hessian_components,
    principal_coefficients_from_hessian,
    wedge_volume_dimensionless,
)
from models.e024_galileon_continuation import (
    ValidationConfig,
    run_validation,
    smooth_mass_preserving_source,
)
from models.e024_shifted_2hessian import (
    ShiftedGrid,
    branch_diagnostics,
    original_residual,
    shifted_jacobian_vector,
    shifted_residual,
    solve_shifted_continuation,
    surface_flux,
)


class GalileonContinuationTests(unittest.TestCase):
    def test_smooth_source_is_nonnegative_and_preserves_total_charge(self) -> None:
        annulus = AnnulusConfig(
            radial_cells=48,
            angular_cells=24,
            radial_max=40.0,
            inner_radius=8.0,
            outer_radius=30.0,
            half_opening_angle=0.05,
            mu=36.8,
        )
        config = ValidationConfig(
            annulus=annulus,
            radial_smoothing_width=4.0,
            angular_smoothing_width=0.1,
        )
        smooth = smooth_mass_preserving_source(config)
        represented = float(
            np.sum(cell_volume_weights_dimensionless(annulus) * smooth.values)
        )
        expected = annulus.mu * wedge_volume_dimensionless(annulus)
        self.assertGreaterEqual(float(np.min(smooth.values)), 0.0)
        self.assertTrue(math.isclose(represented, expected, rel_tol=2.0e-15))
        self.assertGreater(smooth.radial_inner_transition_cells, 0)
        self.assertGreater(smooth.radial_outer_transition_cells, 0)
        self.assertGreater(smooth.angular_transition_cells, 0)
        self.assertGreater(smooth.radial_inner_cells_per_width, 0.0)
        self.assertGreater(smooth.radial_outer_cells_per_width, 0.0)
        self.assertTrue(
            math.isclose(
                smooth.angular_cells_per_width,
                config.angular_smoothing_width
                / (math.pi / (2.0 * annulus.angular_cells)),
            )
        )

    def test_shifted_and_original_residuals_obey_exact_scaling(self) -> None:
        annulus = AnnulusConfig(
            radial_cells=24,
            angular_cells=12,
            radial_max=18.0,
            inner_radius=2.0,
            outer_radius=6.0,
            half_opening_angle=0.2,
            mu=0.7,
            cubic_coefficient=0.8,
        )
        grid = ShiftedGrid(24, 12, 18.0, 0.2)
        random = np.random.default_rng(24).normal(
            scale=1.0e-3, size=(24, 12)
        )
        source = np.random.default_rng(25).uniform(0.0, 0.4, size=random.shape)
        laplacian = build_spherical_laplacian(annulus)
        original = (
            laplacian @ random.ravel()
            + annulus.cubic_coefficient
            * nonlinear_invariant(random, annulus).ravel()
            - source.ravel()
        ).reshape(source.shape)
        shifted = shifted_residual(
            random, source, grid, annulus.cubic_coefficient
        )
        self.assertTrue(
            np.allclose(
                original,
                2.0 * annulus.cubic_coefficient * shifted,
                rtol=2.0e-11,
                atol=2.0e-11,
            )
        )

    def test_independent_principal_pair_sum_matches_galileon_matrix(self) -> None:
        annulus = AnnulusConfig(
            radial_cells=24,
            angular_cells=12,
            radial_max=18.0,
            inner_radius=2.0,
            outer_radius=6.0,
            cubic_coefficient=0.7,
        )
        grid = ShiftedGrid(24, 12, 18.0, 0.2)
        field = np.random.default_rng(26).normal(
            scale=2.0e-4, size=(24, 12)
        )
        hessian = orthonormal_hessian_components(field, annulus)
        spatial, time = principal_coefficients_from_hessian(
            *hessian, annulus.cubic_coefficient
        )
        independent_spatial, pair, independent_time, _ = branch_diagnostics(
            field, grid, annulus.cubic_coefficient
        )
        self.assertAlmostEqual(independent_spatial, float(np.min(spatial)), places=11)
        self.assertAlmostEqual(
            independent_spatial,
            2.0 * annulus.cubic_coefficient * pair,
            places=12,
        )
        self.assertAlmostEqual(independent_time, float(np.min(time)), places=11)

    def test_shifted_analytic_jacobian_matches_finite_difference(self) -> None:
        grid = ShiftedGrid(20, 10, 12.0, 0.2)
        rng = np.random.default_rng(27)
        field = rng.normal(scale=1.0e-4, size=(20, 10))
        vector = rng.normal(scale=1.0e-4, size=(20, 10))
        source = rng.uniform(0.0, 0.1, size=(20, 10))
        epsilon = 1.0e-6
        finite_difference = (
            shifted_residual(field + epsilon * vector, source, grid, 1.0)
            - shifted_residual(field - epsilon * vector, source, grid, 1.0)
        ) / (2.0 * epsilon)
        analytic = shifted_jacobian_vector(field, vector, grid, 1.0)
        self.assertTrue(
            np.allclose(finite_difference, analytic, rtol=2.0e-6, atol=2.0e-9)
        )

    def test_zero_source_continuation_returns_exact_zero_field(self) -> None:
        grid = ShiftedGrid(20, 10, 12.0, 0.2)
        source = np.zeros((20, 10))
        solution = solve_shifted_continuation(grid, source)
        self.assertEqual(solution.stages, [])
        self.assertEqual(float(np.max(np.abs(solution.field))), 0.0)
        self.assertEqual(solution.relative_original_residual_l2, 0.0)
        self.assertGreater(solution.minimum_spatial_principal, 0.0)

    def test_manufactured_quadratic_closes_flux_on_uniform_grid(self) -> None:
        grid = ShiftedGrid(120, 12, 12.0, 0.0)
        radial = (
            np.arange(grid.radial_cells, dtype=float) + 0.5
        ) * grid.radial_max / grid.radial_cells
        coefficient = 0.01
        field = 0.5 * coefficient * (
            radial[:, None] ** 2 - grid.radial_max**2
        ) * np.ones((1, grid.angular_cells))
        source_value = 3.0 * coefficient + 6.0 * coefficient**2
        source = np.full_like(field, source_value)
        residual = original_residual(field, source, grid, 1.0)
        interior = residual[2:-2]
        self.assertLess(float(np.max(np.abs(interior))), 2.0e-10)
        radius = 6.0
        expected = 4.0 * math.pi * source_value * radius**3 / 3.0
        original_flux = surface_flux(field, grid, 1.0, radius, "original")
        shifted_flux = surface_flux(field, grid, 1.0, radius, "shifted")
        self.assertTrue(math.isclose(original_flux, expected, rel_tol=2.0e-3))
        self.assertTrue(math.isclose(shifted_flux, expected, rel_tol=2.0e-3))

    def test_weak_smooth_annulus_agrees_between_solver_families(self) -> None:
        annulus = AnnulusConfig(
            radial_cells=28,
            angular_cells=14,
            radial_max=12.0,
            inner_radius=2.0,
            outer_radius=5.0,
            half_opening_angle=0.2,
            mu=0.05,
            cubic_coefficient=1.0,
        )
        report = run_validation(
            ValidationConfig(
                annulus=annulus,
                radial_smoothing_width=1.0,
                angular_smoothing_width=0.2,
                picard_mixing=0.2,
                picard_update_tolerance=1.0e-10,
                picard_residual_tolerance=3.0e-3,
                picard_max_iterations=3_000,
                continuation_steps=4,
            )
        )
        self.assertTrue(report["picard_reference"]["converged"])
        self.assertLess(
            report["shifted_continuation"]["relative_original_residual_l2"],
            1.0e-7,
        )
        self.assertLess(
            report["formulation_comparison"][
                "volume_weighted_field_relative_difference"
            ],
            2.0e-5,
        )
        self.assertGreater(
            report["shifted_continuation"]["minimum_spatial_principal"], 0.0
        )


if __name__ == "__main__":
    unittest.main()

import math
import unittest

import numpy as np

from models.e023_galileon_annulus import (
    AnnulusConfig,
    G,
    cell_centres,
    build_spherical_laplacian,
    cosmological_galileon_scale_ev,
    dimensionless_gradient_to_acceleration_m_s2,
    gradient_components,
    physical_density_kg_m3,
    orthonormal_hessian_components,
    principal_coefficients_from_hessian,
    radial_grid,
    represented_source_volume_dimensionless,
    sample_ray,
    solve_annular_wedge,
    spherical_wedge_source,
    wedge_volume_dimensionless,
)


class GalileonAnnulusTests(unittest.TestCase):
    def test_documented_radial_mapping_reaches_outer_boundary(self) -> None:
        config = AnnulusConfig(radial_cells=40, angular_cells=12)
        _, radial, faces, _ = radial_grid(config)
        self.assertAlmostEqual(float(faces[0]), 0.0)
        self.assertAlmostEqual(float(faces[-1]), config.radial_max, places=12)
        self.assertTrue(np.all(np.diff(radial) > 0.0))
        self.assertLess(radial[1] - radial[0], radial[-1] - radial[-2])

    def test_linear_uniform_sphere_recovers_analytic_force(self) -> None:
        mu = 0.7
        source_radius = 4.0
        config = AnnulusConfig(
            radial_cells=120,
            angular_cells=12,
            radial_max=20.0,
            radial_mapping_alpha=0.2,
            inner_radius=0.0,
            outer_radius=source_radius,
            half_opening_angle=math.pi / 2.0,
            mu=mu,
            cubic_coefficient=0.0,
        )
        solution = solve_annular_wedge(config)
        radial_component, angular_component, _ = gradient_components(
            solution.linear_field, config
        )
        radial, _ = cell_centres(config)
        mask = (radial > 0.5) & (radial < 3.5)
        analytic_inside = mu * radial[mask] / 3.0
        numerical_inside = radial_component[mask, config.angular_cells // 2]
        self.assertTrue(
            np.allclose(numerical_inside, analytic_inside, rtol=0.025, atol=2e-3)
        )
        mask = (radial > 5.0) & (radial < 12.0)
        analytic_outside = mu * source_radius**3 / (3.0 * radial[mask] ** 2)
        numerical_outside = radial_component[mask, config.angular_cells // 2]
        self.assertTrue(
            np.allclose(numerical_outside, analytic_outside, rtol=0.035, atol=2e-3)
        )
        self.assertLess(float(np.max(np.abs(angular_component))), 2e-10)
        self.assertTrue(solution.converged)

    def test_discrete_laplacian_equals_hessian_trace(self) -> None:
        config = AnnulusConfig(
            radial_cells=28,
            angular_cells=14,
            radial_max=18.0,
            inner_radius=2.0,
            outer_radius=6.0,
        )
        random = np.random.default_rng(23).normal(
            size=(config.radial_cells, config.angular_cells)
        )
        h_rr, _, h_tt, h_pp = orthonormal_hessian_components(random, config)
        matrix_trace = (
            build_spherical_laplacian(config) @ random.ravel()
        ).reshape(random.shape)
        self.assertTrue(
            np.allclose(matrix_trace, h_rr + h_tt + h_pp, rtol=2e-13)
        )

    def test_isotropic_hessian_principal_coefficients(self) -> None:
        alpha = 0.3
        shape = (2, 3)
        h_rr = np.full(shape, alpha)
        h_tt = np.full(shape, alpha)
        h_pp = np.full(shape, alpha)
        h_rt = np.zeros(shape)
        spatial, time = principal_coefficients_from_hessian(
            h_rr, h_rt, h_tt, h_pp, cubic_coefficient=0.8
        )
        self.assertTrue(np.allclose(spatial, 1.0 + 4.0 * 0.8 * alpha))
        self.assertTrue(np.allclose(time, 1.0 + 6.0 * 0.8 * alpha))

    def test_deliberately_unhealthy_hessian_is_flagged(self) -> None:
        h_rr = np.array([[-1.0]])
        zeros = np.zeros((1, 1))
        spatial, time = principal_coefficients_from_hessian(
            h_rr, zeros, zeros, zeros, cubic_coefficient=1.0
        )
        self.assertLess(float(spatial[0, 0]), 0.0)
        self.assertLess(float(time[0, 0]), 0.0)

    def test_mild_nonlinear_case_converges_from_linear_branch(self) -> None:
        config = AnnulusConfig(
            radial_cells=48,
            angular_cells=24,
            radial_max=12.0,
            inner_radius=2.0,
            outer_radius=5.0,
            half_opening_angle=0.2,
            mu=0.05,
            cubic_coefficient=1.0,
            mixing=0.2,
            update_tolerance=1.0e-7,
            residual_tolerance=3.0e-3,
            max_iterations=2_000,
        )
        solution = solve_annular_wedge(config)
        self.assertTrue(solution.converged)
        self.assertLess(solution.relative_update, config.update_tolerance)
        self.assertLess(solution.relative_residual_l2, config.residual_tolerance)
        self.assertGreater(solution.minimum_spatial_principal_eigenvalue, 0.0)
        self.assertGreater(solution.minimum_time_kinetic_coefficient, 0.0)

    def test_exact_centre_is_zero_and_ratio_is_undefined(self) -> None:
        config = AnnulusConfig(
            radial_cells=36,
            angular_cells=18,
            radial_max=12.0,
            inner_radius=2.0,
            outer_radius=5.0,
            half_opening_angle=0.2,
            mu=0.0,
            cubic_coefficient=0.0,
        )
        solution = solve_annular_wedge(config)
        ray = sample_ray(solution, maximum_radius=6.0, samples=31)
        self.assertEqual(ray["centre_linear_gradient"], 0.0)
        self.assertEqual(ray["centre_nonlinear_gradient"], 0.0)
        self.assertIsNone(ray["centre_ratio"])

    def test_source_volume_and_physical_conversions_scale_cleanly(self) -> None:
        config = AnnulusConfig(
            radial_cells=20,
            angular_cells=10,
            radial_max=40.0,
            inner_radius=8.0,
            outer_radius=30.0,
            half_opening_angle=0.05,
        )
        expected = (
            4.0
            * math.pi
            / 3.0
            * math.sin(0.05)
            * (30.0**3 - 8.0**3)
        )
        self.assertTrue(math.isclose(wedge_volume_dimensionless(config), expected))
        radial, angular = cell_centres(config)
        represented = represented_source_volume_dimensionless(
            config, spherical_wedge_source(config, radial, angular)
        )
        self.assertTrue(math.isclose(represented, expected, rel_tol=2e-15))
        lambda_ev = cosmological_galileon_scale_ev()
        density = physical_density_kg_m3(36.8, lambda_ev, 1.0)
        doubled = physical_density_kg_m3(73.6, lambda_ev, 1.0)
        self.assertTrue(math.isclose(doubled / density, 2.0))
        acceleration = dimensionless_gradient_to_acceleration_m_s2(
            1.0, 1.0, lambda_ev, 1.0
        )
        scaled = dimensionless_gradient_to_acceleration_m_s2(
            2.0, 3.0, lambda_ev, 1.0
        )
        self.assertTrue(math.isclose(scaled / acceleration, 6.0))

    def test_linear_spherical_physical_force_matches_two_beta_squared(self) -> None:
        beta = 0.7
        mu = 2.3
        source_radius = 1.8
        probe_radius = 4.2
        r0_m = 0.6
        lambda_ev = cosmological_galileon_scale_ev()
        dimensionless_gradient = (
            mu * source_radius**3 / (3.0 * probe_radius**2)
        )
        scalar_acceleration = dimensionless_gradient_to_acceleration_m_s2(
            dimensionless_gradient, r0_m, lambda_ev, beta
        )
        density = physical_density_kg_m3(mu, lambda_ev, beta)
        source_mass = (
            density * 4.0 * math.pi / 3.0 * (source_radius * r0_m) ** 3
        )
        newtonian_acceleration = (
            G * source_mass / (probe_radius * r0_m) ** 2
        )
        self.assertTrue(
            math.isclose(
                scalar_acceleration,
                2.0 * beta**2 * newtonian_acceleration,
                rel_tol=2.0e-3,
            )
        )

    def test_invalid_configuration_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            AnnulusConfig(inner_radius=9.0, outer_radius=8.0).validate()
        with self.assertRaises(ValueError):
            AnnulusConfig(radial_mapping_alpha=-0.1).validate()


if __name__ == "__main__":
    unittest.main()

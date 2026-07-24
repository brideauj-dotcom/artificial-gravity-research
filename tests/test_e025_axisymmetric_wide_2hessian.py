import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from models.e025_axisymmetric_wide_2hessian import (
    AxisymmetricGrid,
    SmoothAnnulusSpec,
    active_jacobian_matrix,
    build_system,
    continuous_smooth_normalization,
    directional_resolution,
    field_from_callable,
    independent_residual_diagnostics,
    interpolate_field,
    interpolated_cylindrical_derivatives,
    load_continuation_checkpoint,
    monotone_operator,
    monotone_sigma_extension,
    monotone_sigma_gradient,
    primitive_meridional_bases,
    run_smoke,
    sampled_axisymmetric_charge,
    scheme_diagnostics,
    shifted_residual,
    solve_linear_reference,
    solve_continuation,
    spherical_flux_diagnostic,
    smooth_annulus_source,
)


class AxisymmetricWideTwoHessianTests(unittest.TestCase):
    def test_directional_bases_are_orthogonal_and_refine(self) -> None:
        previous = math.inf
        expected_counts = {1: 2, 2: 4, 3: 8}
        for radius in (1, 2, 3):
            bases = primitive_meridional_bases(radius)
            self.assertEqual(len(bases), expected_counts[radius])
            for first, second in bases:
                perpendicular = (-second, first)
                self.assertEqual(
                    first * perpendicular[0] + second * perpendicular[1], 0
                )
                self.assertEqual(math.gcd(first, abs(second)), 1)
            resolution = directional_resolution(radius)
            self.assertLess(resolution, previous)
            previous = resolution

    def test_monotone_extension_matches_sigma2_and_is_nondecreasing(self) -> None:
        rng = np.random.default_rng(2501)
        admissible = rng.uniform(0.05, 2.0, size=(100, 3))
        expected = (
            admissible[:, 0] * admissible[:, 1]
            + admissible[:, 0] * admissible[:, 2]
            + admissible[:, 1] * admissible[:, 2]
        )
        self.assertTrue(
            np.allclose(monotone_sigma_extension(admissible), expected)
        )
        increments = rng.uniform(0.0, 1.0, size=admissible.shape)
        self.assertTrue(
            np.all(
                monotone_sigma_extension(admissible + increments)
                >= monotone_sigma_extension(admissible)
            )
        )
        unhealthy = np.array([-5.0, -5.0, 1.0])
        raw_sigma2 = (
            unhealthy[0] * unhealthy[1]
            + unhealthy[0] * unhealthy[2]
            + unhealthy[1] * unhealthy[2]
        )
        self.assertEqual(float(raw_sigma2), 15.0)
        self.assertEqual(float(monotone_sigma_extension(unhealthy)), -25.0)

    def test_monotone_extension_gradient_matches_finite_difference(self) -> None:
        rng = np.random.default_rng(2502)
        values = rng.uniform(0.1, 2.0, size=(40, 3))
        vectors = rng.normal(size=values.shape)
        epsilon = 1.0e-7
        finite_difference = (
            monotone_sigma_extension(values + epsilon * vectors)
            - monotone_sigma_extension(values - epsilon * vectors)
        ) / (2.0 * epsilon)
        analytic = np.sum(monotone_sigma_gradient(values) * vectors, axis=1)
        self.assertTrue(
            np.allclose(finite_difference, analytic, rtol=2.0e-7, atol=1.0e-8)
        )

    def test_nonconvex_admissible_quadratic_is_exact_through_boundary(self) -> None:
        radial_max = 2.0
        cubic_coefficient = 1.0
        radial_eigenvalue = 1.0
        axial_eigenvalue = -0.25

        def shifted_exact(rho: float, z: float) -> float:
            return (
                0.5 * radial_eigenvalue * rho**2
                + 0.5 * axial_eigenvalue * z**2
            )

        def shift(rho: float, z: float) -> float:
            return (rho**2 + z**2) / (8.0 * cubic_coefficient)

        def field_exact(rho: float, z: float) -> float:
            return shifted_exact(rho, z) - shift(rho, z)

        system = build_system(
            AxisymmetricGrid(radial_max, 0.25, directional_radius=2),
            cubic_coefficient,
            boundary_phi=field_exact,
        )
        field = field_from_callable(system, field_exact)
        operator, _, curvatures = monotone_operator(system, field)
        expected = radial_eigenvalue**2 + (
            2.0 * radial_eigenvalue * axial_eigenvalue
        )
        self.assertLess(float(np.max(np.abs(operator - expected))), 2.0e-13)
        pair, spatial, time = scheme_diagnostics(system, curvatures)
        self.assertGreater(pair, 0.0)
        self.assertGreater(spatial, 0.0)
        self.assertGreater(time, 0.0)
        self.assertTrue(
            any(
                np.any(np.abs(operator_.boundary_offset) > 0.0)
                for pair_ in system.meridional_operators
                for operator_ in pair_
            )
        )
        # At this node the outward radial leg is shortened by the circular
        # boundary while the inward leg retains its full grid length.  The
        # unequal-distance formula must still be exact for the quadratic.
        node = int(system.index_map[7, 2])
        primary = system.meridional_operators[0][0]
        primary_curvature = (
            primary.matrix @ field + primary.boundary_offset + system.shift
        )
        self.assertAlmostEqual(
            float(primary_curvature[node]), radial_eigenvalue, places=12
        )

    def test_rotated_nonconvex_quadratic_improves_with_directional_radius(self) -> None:
        angle = 0.3
        rotation = np.array(
            [
                [math.cos(angle), -math.sin(angle)],
                [math.sin(angle), math.cos(angle)],
            ]
        )
        meridional_hessian = rotation @ np.diag([-0.2, 1.4]) @ rotation.T
        azimuthal_eigenvalue = 1.0
        exact_sigma2 = (
            -0.2 * 1.4
            + -0.2 * azimuthal_eigenvalue
            + 1.4 * azimuthal_eigenvalue
        )
        errors: list[float] = []
        for radius in (1, 2, 3):
            candidates: list[float] = []
            for first, second in primitive_meridional_bases(radius):
                direction = np.array([first, second], dtype=float)
                direction /= np.linalg.norm(direction)
                perpendicular = np.array([-direction[1], direction[0]])
                curvatures = np.array(
                    [
                        direction @ meridional_hessian @ direction,
                        perpendicular @ meridional_hessian @ perpendicular,
                        azimuthal_eigenvalue,
                    ]
                )
                candidates.append(float(monotone_sigma_extension(curvatures)))
            errors.append(min(candidates) - exact_sigma2)
        self.assertGreater(errors[0], errors[1])
        self.assertGreater(errors[1], errors[2])
        self.assertLess(errors[2], 0.01 * exact_sigma2)

    def test_nonlinear_manufactured_solution_converges(self) -> None:
        radial_max = 2.0
        cubic_coefficient = 1.0
        coefficient = 0.04

        def shifted_exact(rho: float, z: float) -> float:
            return 0.5 * (rho**2 + z**2) + coefficient * rho**2 * z**2

        def shift(rho: float, z: float) -> float:
            return (rho**2 + z**2) / (8.0 * cubic_coefficient)

        def field_exact(rho: float, z: float) -> float:
            return shifted_exact(rho, z) - shift(rho, z)

        def exact_sigma2(rho: np.ndarray, z: np.ndarray) -> np.ndarray:
            radial = 1.0 + 2.0 * coefficient * z**2
            axial = 1.0 + 2.0 * coefficient * rho**2
            mixed = 4.0 * coefficient * rho * z
            return radial**2 + 2.0 * radial * axial - mixed**2

        errors: list[float] = []
        for spacing in (0.25, 0.125, 0.0625):
            system = build_system(
                AxisymmetricGrid(radial_max, spacing, directional_radius=3),
                cubic_coefficient,
                boundary_phi=field_exact,
            )
            field = field_from_callable(system, field_exact)
            operator, _, _ = monotone_operator(system, field)
            error = operator - exact_sigma2(system.rho, system.z)
            errors.append(float(np.sqrt(np.mean(error**2))))
        self.assertLess(errors[1], 0.55 * errors[0])
        self.assertLess(errors[2], 0.55 * errors[1])

    def test_directional_refinement_reduces_rotated_solution_error(self) -> None:
        radial_max = 2.0
        spacing = 0.0625
        coefficient = 0.04

        def shifted_exact(rho: float, z: float) -> float:
            return 0.5 * (rho**2 + z**2) + coefficient * rho**2 * z**2

        def field_exact(rho: float, z: float) -> float:
            return shifted_exact(rho, z) - (rho**2 + z**2) / 8.0

        def exact_sigma2(rho: np.ndarray, z: np.ndarray) -> np.ndarray:
            radial = 1.0 + 2.0 * coefficient * z**2
            axial = 1.0 + 2.0 * coefficient * rho**2
            mixed = 4.0 * coefficient * rho * z
            return radial**2 + 2.0 * radial * axial - mixed**2

        errors: list[float] = []
        for directional_radius in (1, 2, 3):
            system = build_system(
                AxisymmetricGrid(radial_max, spacing, directional_radius),
                boundary_phi=field_exact,
            )
            field = field_from_callable(system, field_exact)
            operator, _, _ = monotone_operator(system, field)
            interior = (
                system.rho**2 + system.z**2
                < (radial_max - directional_radius * spacing) ** 2
            )
            error = operator - exact_sigma2(system.rho, system.z)
            errors.append(float(np.sqrt(np.mean(error[interior] ** 2))))
        self.assertLess(errors[1], 0.5 * errors[0])
        self.assertLess(errors[2], errors[1])

    def test_joint_refinement_escapes_a_fixed_directional_plateau(self) -> None:
        radial_max = 2.0
        coefficient = 0.04

        def field_exact(rho: float, z: float) -> float:
            shifted = 0.5 * (rho**2 + z**2) + coefficient * rho**2 * z**2
            return shifted - (rho**2 + z**2) / 8.0

        def exact_sigma2(rho: np.ndarray, z: np.ndarray) -> np.ndarray:
            radial = 1.0 + 2.0 * coefficient * z**2
            axial = 1.0 + 2.0 * coefficient * rho**2
            mixed = 4.0 * coefficient * rho * z
            return radial**2 + 2.0 * radial * axial - mixed**2

        def interior_error(spacing: float, directional_radius: int) -> float:
            system = build_system(
                AxisymmetricGrid(radial_max, spacing, directional_radius),
                boundary_phi=field_exact,
            )
            field = field_from_callable(system, field_exact)
            operator, _, _ = monotone_operator(system, field)
            interior = (
                system.rho**2 + system.z**2
                < (radial_max - directional_radius * spacing) ** 2
            )
            error = operator - exact_sigma2(system.rho, system.z)
            return float(np.sqrt(np.mean(error[interior] ** 2)))

        fixed = [
            interior_error(spacing, 2)
            for spacing in (0.0625, 0.03125, 0.015625)
        ]
        self.assertLess(fixed[1], fixed[0])
        self.assertGreater(fixed[2], 0.95 * fixed[1])

        joint = [
            interior_error(spacing, radius)
            for spacing, radius in ((0.125, 2), (0.0625, 3), (0.03125, 4))
        ]
        self.assertLess(joint[1], 0.55 * joint[0])
        self.assertLess(joint[2], 0.55 * joint[1])

    def test_zero_source_returns_exact_zero_field(self) -> None:
        system = build_system(AxisymmetricGrid(2.0, 0.5, 2))
        source = np.zeros(system.size)
        solution = solve_continuation(system, source)
        self.assertEqual(solution.stages, [])
        self.assertEqual(float(np.max(np.abs(solution.field))), 0.0)
        self.assertEqual(solution.relative_residual_l2, 0.0)
        self.assertGreater(solution.minimum_pair_sum, 0.0)

    def test_small_source_continuation_closes_residual_on_admissible_branch(self) -> None:
        system = build_system(AxisymmetricGrid(3.0, 0.5, 2))
        source = 0.015 * np.exp(
            -((system.rho - 1.2) / 0.7) ** 4 - (system.z / 0.6) ** 4
        )
        solution = solve_continuation(system, source, continuation_steps=3)
        residual = shifted_residual(system, solution.field, source)
        relative = float(np.linalg.norm(residual) / (np.linalg.norm(source) / 2.0))
        self.assertLess(relative, 1.0e-7)
        self.assertGreater(solution.minimum_pair_sum, 0.0)
        self.assertGreater(solution.minimum_time_kinetic, 0.0)
        self.assertEqual(len(solution.stages), 3)

    def test_assembled_active_jacobian_matches_matrix_free_action(self) -> None:
        from models.e025_axisymmetric_wide_2hessian import (
            _jacobian_action,
            _linearized_zero_matrix,
        )

        system = build_system(AxisymmetricGrid(3.0, 0.5, 2))
        rng = np.random.default_rng(2503)
        field = rng.normal(scale=0.01, size=system.size)
        vector = rng.normal(size=system.size)
        _, active, curvatures = monotone_operator(system, field)
        nodes = np.arange(system.size)
        gradient = monotone_sigma_gradient(curvatures[active, nodes])
        expected = _jacobian_action(system, active, gradient, vector)
        assembled = active_jacobian_matrix(system, active, gradient) @ vector
        self.assertTrue(np.allclose(assembled, expected, rtol=2.0e-13, atol=2.0e-13))
        zero_field = np.zeros(system.size)
        _, zero_active, zero_curvatures = monotone_operator(system, zero_field)
        zero_gradient = monotone_sigma_gradient(
            zero_curvatures[zero_active, np.arange(system.size)]
        )
        zero_jacobian = active_jacobian_matrix(
            system, zero_active, zero_gradient
        )
        difference = zero_jacobian - _linearized_zero_matrix(system)
        self.assertLess(float(np.max(np.abs(difference.data))), 2.0e-13)

    def test_active_ilu_closes_small_source_with_recorded_setup(self) -> None:
        system = build_system(AxisymmetricGrid(3.0, 0.5, 2))
        source = 0.015 * np.exp(
            -((system.rho - 1.2) / 0.7) ** 4 - (system.z / 0.6) ** 4
        )
        solution = solve_continuation(
            system,
            source,
            continuation_steps=3,
            preconditioner_kind="active_ilu",
        )
        self.assertLess(solution.relative_residual_l2, 1.0e-7)
        self.assertGreater(solution.minimum_pair_sum, 0.0)
        self.assertTrue(
            all(stage.preconditioner_kind == "active_ilu" for stage in solution.stages)
        )
        self.assertTrue(
            all(stage.preconditioner_setups > 0 for stage in solution.stages)
        )
        self.assertTrue(
            all(stage.preconditioner_factor_nnz_max > 0 for stage in solution.stages)
        )

    def test_checkpoint_roundtrip_resume_and_source_fingerprint(self) -> None:
        system = build_system(AxisymmetricGrid(3.0, 0.5, 2))
        source = 0.012 * np.exp(
            -((system.rho - 1.2) / 0.7) ** 4 - (system.z / 0.6) ** 4
        )
        with tempfile.TemporaryDirectory() as directory:
            checkpoint_path = Path(directory) / "continuation.npz"
            uninterrupted = solve_continuation(
                system,
                source,
                continuation_steps=3,
                checkpoint_path=checkpoint_path,
            )
            checkpoint = load_continuation_checkpoint(
                checkpoint_path,
                system,
                source,
                continuation_steps=3,
                relative_tolerance=1.0e-8,
                newton_max_iterations=15,
                gmres_relative_tolerance=1.0e-9,
                gmres_max_iterations=30,
            )
            self.assertTrue(checkpoint.stage_complete)
            self.assertEqual(checkpoint.completed_amplitude, 1.0)
            resumed = solve_continuation(
                system,
                source,
                continuation_steps=3,
                checkpoint_path=checkpoint_path,
                resume_checkpoint=True,
            )
            self.assertTrue(
                np.allclose(resumed.field, uninterrupted.field, rtol=0.0, atol=0.0)
            )
            self.assertEqual(len(resumed.stages), 3)
            with self.assertRaises(ValueError):
                load_continuation_checkpoint(
                    checkpoint_path,
                    system,
                    source * 1.001,
                    continuation_steps=3,
                    relative_tolerance=1.0e-8,
                    newton_max_iterations=15,
                    gmres_relative_tolerance=1.0e-9,
                    gmres_max_iterations=30,
                )
            changed_boundary_system = build_system(
                AxisymmetricGrid(3.0, 0.5, 2),
                boundary_phi=lambda rho, z: 0.001 * (rho**2 + z**2),
            )
            with self.assertRaisesRegex(ValueError, "system_digest"):
                load_continuation_checkpoint(
                    checkpoint_path,
                    changed_boundary_system,
                    source,
                    continuation_steps=3,
                    relative_tolerance=1.0e-8,
                    newton_max_iterations=15,
                    gmres_relative_tolerance=1.0e-9,
                    gmres_max_iterations=30,
                )

    def test_incomplete_checkpoint_resumes_after_last_accepted_newton_step(self) -> None:
        import models.e025_axisymmetric_wide_2hessian as e025

        system = build_system(AxisymmetricGrid(3.0, 0.5, 2))
        source = 0.015 * np.exp(
            -((system.rho - 1.2) / 0.7) ** 4 - (system.z / 0.6) ** 4
        )
        uninterrupted = solve_continuation(
            system,
            source,
            continuation_steps=2,
        )
        real_gmres = e025.sparse_linalg.gmres
        calls = [0]

        def interrupt_second_correction(*args, **kwargs):
            calls[0] += 1
            if calls[0] == 2:
                return np.zeros(args[0].shape[0]), 1
            return real_gmres(*args, **kwargs)

        with tempfile.TemporaryDirectory() as directory:
            checkpoint_path = Path(directory) / "interrupted.npz"
            with patch.object(
                e025.sparse_linalg,
                "gmres",
                side_effect=interrupt_second_correction,
            ):
                with self.assertRaisesRegex(RuntimeError, "GMRES failed"):
                    solve_continuation(
                        system,
                        source,
                        continuation_steps=2,
                        checkpoint_path=checkpoint_path,
                    )
            checkpoint = load_continuation_checkpoint(
                checkpoint_path,
                system,
                source,
                continuation_steps=2,
                relative_tolerance=1.0e-8,
                newton_max_iterations=15,
                gmres_relative_tolerance=1.0e-9,
                gmres_max_iterations=30,
            )
            self.assertFalse(checkpoint.stage_complete)
            self.assertEqual(checkpoint.completed_amplitude, 0.0)
            self.assertEqual(checkpoint.target_amplitude, 0.5)
            self.assertEqual(checkpoint.current_newton_iterations, 1)
            with self.assertRaisesRegex(ValueError, "change preconditioner"):
                solve_continuation(
                    system,
                    source,
                    continuation_steps=2,
                    preconditioner_kind="active_ilu",
                    checkpoint_path=checkpoint_path,
                    resume_checkpoint=True,
                )
            resumed = solve_continuation(
                system,
                source,
                continuation_steps=2,
                checkpoint_path=checkpoint_path,
                resume_checkpoint=True,
            )
            self.assertTrue(
                np.allclose(resumed.field, uninterrupted.field, rtol=0.0, atol=1.0e-13)
            )
            self.assertEqual(
                [stage.amplitude for stage in resumed.stages],
                [0.5, 1.0],
            )

    def test_inadmissible_initial_field_is_rejected_before_residual_exit(self) -> None:
        system = build_system(AxisymmetricGrid(3.0, 0.5, 2))
        source = np.full(system.size, 0.01)
        inadmissible = field_from_callable(
            system, lambda rho, z: -10.0 * (rho**2 + z**2)
        )
        with self.assertRaisesRegex(ValueError, "admissible normal branch"):
            solve_continuation(system, source, initial_field=inadmissible)

    def test_centered_postprocessor_is_exact_for_quadratic(self) -> None:
        coefficient = 0.08

        def exact(rho: float, z: float) -> float:
            return 0.5 * coefficient * (rho**2 + z**2)

        source_value = 3.0 * coefficient + 6.0 * coefficient**2
        system = build_system(
            AxisymmetricGrid(4.0, 0.25, 2), boundary_phi=exact
        )
        field = field_from_callable(system, exact)
        points_rho = np.array([0.0, 0.6, 1.1])
        points_z = np.array([0.4, 0.0, 0.9])
        phi_r, phi_z, h_rr, h_rz, h_zz = interpolated_cylindrical_derivatives(
            system, field, points_rho, points_z
        )
        self.assertTrue(np.allclose(phi_r, coefficient * points_rho, atol=2.0e-14))
        self.assertTrue(np.allclose(phi_z, coefficient * points_z, atol=2.0e-14))
        self.assertTrue(np.allclose(h_rr, coefficient, atol=3.0e-14))
        self.assertTrue(np.allclose(h_zz, coefficient, atol=3.0e-14))
        self.assertTrue(np.allclose(h_rz, 0.0, atol=3.0e-14))
        diagnostics = independent_residual_diagnostics(
            system, field, np.full(system.size, source_value)
        )
        self.assertLess(diagnostics["original_relative_volume_l2"], 2.0e-12)
        self.assertLess(diagnostics["white_root_relative_volume_l2"], 2.0e-12)
        self.assertGreater(diagnostics["minimum_normal_branch_factor"], 0.0)

    def test_linear_reference_and_spherical_flux_match_quadratic(self) -> None:
        coefficient = 0.06

        def exact(rho: float, z: float) -> float:
            return 0.5 * coefficient * (rho**2 + z**2)

        system = build_system(
            AxisymmetricGrid(4.0, 0.25, 2), boundary_phi=exact
        )
        exact_field = field_from_callable(system, exact)
        solved = solve_linear_reference(
            system, np.full(system.size, 3.0 * coefficient)
        )
        self.assertTrue(np.allclose(solved, exact_field, rtol=1.0e-12, atol=1.0e-12))
        radius = 1.25
        flux = spherical_flux_diagnostic(system, exact_field, radius)
        expected = 4.0 * math.pi * radius**3 * (
            coefficient + 2.0 * coefficient**2
        )
        self.assertAlmostEqual(flux, expected, places=10)

    def test_interpolator_preserves_bilinear_field(self) -> None:
        system = build_system(AxisymmetricGrid(4.0, 0.5, 2))
        field = field_from_callable(
            system, lambda rho, z: 1.0 + 2.0 * rho + 3.0 * z + rho * z
        )
        rho = np.array([0.2, 0.75, 1.4])
        z = np.array([0.3, 0.6, 1.1])
        expected = 1.0 + 2.0 * rho + 3.0 * z + rho * z
        self.assertTrue(np.allclose(interpolate_field(system, field, rho, z), expected))

    def test_fixed_smooth_source_normalization_is_continuous_not_grid_fitted(self) -> None:
        normalization = continuous_smooth_normalization(SmoothAnnulusSpec())
        self.assertTrue(
            math.isclose(normalization, 0.9969846439090065, rel_tol=2.0e-13)
        )

    def test_independent_sampled_source_charge_converges_without_renormalizing(self) -> None:
        errors: list[float] = []
        for spacing in (1.0, 0.5):
            system = build_system(AxisymmetricGrid(40.0, spacing, 1))
            source, metadata = smooth_annulus_source(system)
            sampled = sampled_axisymmetric_charge(system, source)
            self.assertAlmostEqual(sampled, metadata["sampled_charge"])
            errors.append(abs(float(metadata["sampled_charge_relative_error"])))
        self.assertLess(errors[1], 0.15 * errors[0])
        self.assertGreater(errors[1], 0.0)

    def test_cli_smoke_report_is_explicitly_provisional(self) -> None:
        report = run_smoke(
            radial_max=3.0,
            spacing=0.5,
            directional_radius=2,
            source_amplitude=0.01,
            continuation_steps=3,
        )
        solver = report["solver"]
        self.assertLess(solver["relative_residual_l2"], 1.0e-7)
        self.assertGreater(solver["minimum_pair_sum"], 0.0)
        self.assertTrue(
            any("full mu=36.8" in item for item in report["limitations"])
        )


if __name__ == "__main__":
    unittest.main()

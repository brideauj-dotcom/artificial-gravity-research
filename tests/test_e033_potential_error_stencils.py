from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

import numpy as np

import models.e033_potential_error_stencils as e033


class E033PotentialErrorStencilTests(unittest.TestCase):
    def test_strategy_is_frozen_and_never_advances_lineage(self) -> None:
        provenance = e033.implementation_provenance()
        strategy = provenance["strategy"]
        self.assertEqual(
            strategy["verification_amplitudes"],
            [49.0 / 96.0, 25.0 / 48.0],
        )
        self.assertEqual(strategy["accepted_baseline_amplitude"], 0.5)
        self.assertEqual(
            strategy["nested_reconstruction_steps"],
            [0.25, 0.5],
        )
        self.assertEqual(strategy["patch_shape"], [5, 5])
        self.assertEqual(strategy["recovery"]["rank"], 6)
        self.assertIn("immutable", strategy["lineage_policy"])
        self.assertIn("e030_campaign", provenance["modules"])
        for values in provenance["modules"].values():
            self.assertFalse(Path(values["path"]).is_absolute())

    def test_quadratic_recovery_has_fixed_well_conditioned_design(self) -> None:
        self.assertEqual(e033.QUADRATIC_DESIGN.shape, (25, 6))
        self.assertEqual(np.linalg.matrix_rank(e033.QUADRATIC_DESIGN), 6)
        self.assertAlmostEqual(
            np.linalg.cond(e033.QUADRATIC_DESIGN),
            3.7363768878060846,
            places=11,
        )

    def test_quadratic_recovery_reproduces_declared_polynomial(self) -> None:
        validation = e033.manufactured_validation()
        gate = validation["quadratic_polynomial_gate"]
        self.assertTrue(gate["passed"])
        self.assertLess(
            gate["all_six_basis_monomials_max_fit_residual"],
            2.0e-14,
        )
        self.assertLess(
            gate[
                "maximum_component_error_across_both_scales_and_recovery"
            ],
            2.0e-13,
        )

    def test_component_stencil_is_linear_in_potential_error(self) -> None:
        rng = np.random.default_rng(3301)
        coarse = rng.normal(size=(5, 5))
        error = rng.normal(size=(5, 5))
        fine = coarse + error
        for stride in (1, 2):
            fine_components = e033._centered_component_ledgers(
                fine,
                6.0,
                stride=stride,
            )["components"]
            coarse_components = e033._centered_component_ledgers(
                coarse,
                6.0,
                stride=stride,
            )["components"]
            error_components = e033._centered_component_ledgers(
                error,
                6.0,
                stride=stride,
            )["components"]
            np.testing.assert_allclose(
                fine_components - coarse_components,
                error_components,
                rtol=0.0,
                atol=2.0e-14,
            )

    def test_nested_detail_ledgers_close_all_four_components(self) -> None:
        rng = np.random.default_rng(3302)
        patch = rng.normal(size=(5, 5))
        quarter = e033._centered_component_ledgers(
            patch,
            6.0,
            stride=1,
        )["components"]
        half = e033._centered_component_ledgers(
            patch,
            6.0,
            stride=2,
        )["components"]
        nested = e033._nested_detail_ledgers(
            patch,
            6.0,
        )["components"]
        np.testing.assert_allclose(
            quarter - half,
            nested,
            rtol=0.0,
            atol=2.0e-14,
        )

    def test_quadratic_recovery_is_linear_and_reports_residuals(self) -> None:
        rng = np.random.default_rng(3303)
        coarse = rng.normal(size=(5, 5))
        error = rng.normal(size=(5, 5))
        fine = coarse + error
        fine_recovery = e033._quadratic_recovery(fine, 6.0)
        coarse_recovery = e033._quadratic_recovery(coarse, 6.0)
        error_recovery = e033._quadratic_recovery(error, 6.0)
        np.testing.assert_allclose(
            fine_recovery["components"] - coarse_recovery["components"],
            error_recovery["components"],
            rtol=0.0,
            atol=2.0e-14,
        )
        self.assertGreater(error_recovery["residual_l2"], 0.0)
        self.assertEqual(error_recovery["rank"], 6)
        np.testing.assert_allclose(
            error_recovery["component_weights"] @ error.reshape(-1),
            error_recovery["components"],
            rtol=0.0,
            atol=2.0e-14,
        )

    def test_patch_mapping_is_exact_ordered_and_rejects_drift(self) -> None:
        def system(spacing: float) -> SimpleNamespace:
            coordinates = np.arange(
                int(round(10.0 / spacing)) + 1,
                dtype=float,
            ) * spacing
            rho_mesh, z_mesh = np.meshgrid(
                coordinates,
                coordinates,
                indexing="ij",
            )
            index_map = np.arange(
                rho_mesh.size,
                dtype=int,
            ).reshape(rho_mesh.shape)
            return SimpleNamespace(
                grid=SimpleNamespace(spacing=spacing),
                rho=rho_mesh.reshape(-1),
                z=z_mesh.reshape(-1),
                index_map=index_map,
            )

        fine = system(0.125)
        coarse = system(0.25)
        fine_nodes, coarse_nodes = e033._patch_nodes(
            fine,
            coarse,
            (3.0, 1.0),
        )
        self.assertEqual(fine_nodes.size, 25)
        self.assertEqual(coarse_nodes.size, 25)
        np.testing.assert_array_equal(
            fine.rho[fine_nodes],
            coarse.rho[coarse_nodes],
        )
        np.testing.assert_array_equal(
            fine.z[fine_nodes],
            coarse.z[coarse_nodes],
        )
        np.testing.assert_array_equal(
            coarse.rho[coarse_nodes].reshape(5, 5)[:, 0],
            np.arange(2.5, 3.51, 0.25),
        )
        with self.assertRaises(ValueError):
            e033._patch_nodes(fine, coarse, (3.1, 1.0))
        with self.assertRaises(ValueError):
            e033._patch_nodes(system(0.1), coarse, (3.0, 1.0))

    def test_controls_retain_smooth_and_alias_ambiguity(self) -> None:
        controls = e033.manufactured_validation()[
            "controls_not_acceptance_tests"
        ]
        quartic = controls[
            "smooth_axial_quartic_with_zero_center_continuum_hessian"
        ]
        nyquist = controls["axial_nyquist_mode"]
        long_wave = controls["long_wave_cosine_kh_0p25"]
        self.assertNotEqual(
            quartic["components_0p25"][2],
            quartic["components_0p5"][2],
        )
        self.assertAlmostEqual(nyquist["components_0p5"][2], 0.0)
        self.assertLess(nyquist["components_0p25"][2], 0.0)
        self.assertAlmostEqual(
            nyquist["analytic_center_components"][2],
            -(np.pi**2) / e033.COMMON_NODE_STEP**2,
        )
        for row in (quartic, nyquist, long_wave):
            self.assertEqual(
                row["quadratic_component_vector_nearest_scale"]["nearest"],
                "0.5_centered",
            )
        self.assertIn("non-identifying", controls["interpretation"])

    def test_decision_retains_nonidentifying_control_result(self) -> None:
        def point(pair: str, vector: str) -> dict:
            return {
                "descriptive_scale_comparison": {
                    "quadratic_pair_nearest_scale": {"nearest": pair},
                    "quadratic_component_vector_nearest_scale": {
                        "nearest": vector
                    },
                }
            }

        comparisons = [
            {
                "points": [
                    point("0.5_centered", "0.5_centered"),
                    point("0.5_centered", "0.5_centered"),
                ]
            }
        ]
        result = e033._decision(
            comparisons,
            e033.manufactured_validation(),
        )
        self.assertEqual(
            result["status"],
            "nonidentifying_mixed_recovery_result",
        )
        self.assertTrue(
            result["all_three_distinct_controls_are_also_nearer_0p5"]
        )
        comparisons[0]["points"][0] = point(
            "0.25_centered",
            "0.5_centered",
        )
        self.assertEqual(
            e033._decision(
                comparisons,
                e033.manufactured_validation(),
            )["status"],
            "nonidentifying_mixed_recovery_result",
        )

    def test_nearest_scale_tie_is_not_forced_to_inner(self) -> None:
        result = e033._nearest_scale_comparison(0.0, 2.0, 1.0)
        self.assertEqual(
            result["nearest"],
            "equidistant_within_roundoff",
        )

    def test_endpoint_schedule_drift_fails_before_any_solve(self) -> None:
        with mock.patch.object(
            e033.e031,
            "VERIFICATION_AMPLITUDES",
            (49.0 / 96.0,),
        ):
            with self.assertRaisesRegex(RuntimeError, "schedule drifted"):
                e033.run_campaign()


if __name__ == "__main__":
    unittest.main()

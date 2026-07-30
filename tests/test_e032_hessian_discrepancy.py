from pathlib import Path
import unittest

import numpy as np

import models.e025_axisymmetric_wide_2hessian as e025
import models.e032_hessian_discrepancy as e032
from models.e025_axisymmetric_wide_2hessian import AxisymmetricGrid


class E032HessianDiscrepancyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.system = e025.build_system(AxisymmetricGrid(8.0, 0.5, 2))

    def test_strategy_is_bounded_and_never_advances_lineage(self) -> None:
        provenance = e032.implementation_provenance()
        strategy = provenance["strategy"]
        self.assertEqual(
            strategy["verification_amplitudes"],
            [49.0 / 96.0, 25.0 / 48.0],
        )
        self.assertEqual(strategy["accepted_baseline_amplitude"], 0.5)
        self.assertEqual(
            strategy["reconstruction_steps"],
            [0.25, 0.5],
        )
        self.assertEqual(strategy["hotspot"], [8.75, 0.75])
        self.assertIn("immutable", strategy["lineage_policy"])
        for values in provenance["modules"].values():
            self.assertFalse(Path(values["path"]).is_absolute())

    def test_pair_identity_is_trace_minus_largest_eigenvalue(self) -> None:
        components = np.array([0.3, -0.2, 0.7, 0.1])
        matrix = e032._matrix_from_components(components)
        eigenvalues, pair = e032._shifted_eigenvalues_and_pair(
            components,
            0.25,
        )
        expected = np.trace(matrix) - np.linalg.eigvalsh(matrix)[-1] + 0.5
        self.assertAlmostEqual(float(pair), float(expected), places=14)
        self.assertAlmostEqual(
            float(pair),
            float(eigenvalues[0] + eigenvalues[1]),
            places=14,
        )

    def test_first_order_decomposition_closes_for_commuting_change(self) -> None:
        coarse = np.array([1.0, 0.0, 2.0, 4.0])
        fine = np.array([1.5, 0.0, 2.25, 5.0])
        result = e032._spectral_pair_decomposition(coarse, fine, 0.25)
        self.assertAlmostEqual(
            result["pair_difference_fine_minus_coarse"],
            0.75,
            places=14,
        )
        self.assertAlmostEqual(
            result["coarse_top_eigenvector_linearization_remainder"],
            0.0,
            places=14,
        )
        self.assertAlmostEqual(result["exact_closure_error"], 0.0, places=14)

    def test_eigenvector_rotation_is_retained_as_exact_remainder(self) -> None:
        coarse = np.array([0.0, 0.0, 2.0, 1.0])
        fine = np.array([0.0, 0.75, 2.0, 1.0])
        result = e032._spectral_pair_decomposition(coarse, fine, 0.25)
        self.assertNotEqual(
            result["coarse_top_eigenvector_linearization_remainder"],
            0.0,
        )
        closed = (
            result["first_order_sum"]
            + result["coarse_top_eigenvector_linearization_remainder"]
        )
        self.assertAlmostEqual(
            closed,
            result["pair_difference_fine_minus_coarse"],
            places=14,
        )

    def test_shapley_attribution_is_order_neutral_and_closes(self) -> None:
        coarse = np.array([0.2, 0.1, 0.5, 0.3])
        fine = np.array([0.4, -0.2, 0.1, 0.6])
        result = e032._shapley_pair_attribution(coarse, fine, 0.25)
        self.assertEqual(result["replacement_order_count"], 24)
        self.assertAlmostEqual(result["closure_error"], 0.0, places=14)
        self.assertAlmostEqual(
            sum(result["component_contributions"].values()),
            result["actual_pair_difference"],
            places=14,
        )
        self.assertEqual(
            set(result["coalition_marginal_envelopes"]),
            set(e032.COMPONENT_NAMES),
        )

    def test_hoffman_wielandt_and_pair_bounds_hold(self) -> None:
        result = e032._spectral_pair_decomposition(
            np.array([0.2, 0.1, 0.5, 0.3]),
            np.array([0.4, -0.2, 0.1, 0.6]),
            0.25,
        )
        bounds = result["perturbation_bounds"]
        self.assertTrue(bounds["hoffman_wielandt_l2_le_frobenius"])
        self.assertLessEqual(
            bounds["absolute_pair_difference"],
            bounds["two_times_spectral_norm_pair_bound"] + 1.0e-14,
        )

    def test_quadratic_field_reconstructs_axisymmetric_hessian(self) -> None:
        field = self.system.rho**2 + self.system.z**2
        points = np.array([[0.0, 1.0], [1.0, 1.0]])
        bundle = e032._component_bundle(
            self.system,
            field,
            points,
            difference_step=0.5,
        )
        np.testing.assert_allclose(
            bundle["components"],
            np.array([[2.0, 0.0, 2.0, 2.0]] * 2),
            rtol=0.0,
            atol=1.0e-12,
        )

    def test_dominance_summary_uses_canonical_step_only(self) -> None:
        def point(radial: float, mixed: float) -> dict:
            envelopes = {
                "radial": {
                    "minimum": radial,
                    "maximum": radial,
                },
                "mixed": {
                    "minimum": mixed,
                    "maximum": mixed,
                },
                "axial": {
                    "minimum": 0.0,
                    "maximum": 0.0,
                },
                "azimuthal": {
                    "minimum": 0.0,
                    "maximum": 0.0,
                },
            }
            return {
                "shapley_attribution": {
                    "component_contributions": {
                        "radial": radial,
                        "mixed": mixed,
                        "axial": 0.0,
                        "azimuthal": 0.0,
                    },
                    "coalition_marginal_envelopes": envelopes,
                },
                "trace_difference": radial,
                "spectral_selection_response": mixed,
                "coarse_top_eigenvector_linearization_remainder": 0.01,
                "pair_difference_fine_minus_coarse": radial + mixed,
            }

        sensitivity = {
            "steps": [
                {
                    "difference_step": 0.125,
                    "points": [point(100.0, 0.0)] * 4,
                },
                {
                    "difference_step": 0.25,
                    "points": [
                        point(0.1, 0.5),
                        point(0.2, 0.1),
                        point(0.3, 0.1),
                        point(0.4, 0.1),
                    ],
                },
                {
                    "difference_step": 0.5,
                    "points": [
                        point(0.2, 0.1),
                        point(0.2, 0.1),
                        point(0.3, 0.1),
                        point(0.4, 0.1),
                    ],
                },
            ]
        }
        result = e032._dominance_summary(sensitivity)
        self.assertEqual(
            result[
                "canonical_hotspot_dominant_absolute_shapley_component"
            ],
            "mixed",
        )
        self.assertEqual(
            result[
                "canonical_lobe_dominant_mean_absolute_shapley_component"
            ],
            "radial",
        )


if __name__ == "__main__":
    unittest.main()

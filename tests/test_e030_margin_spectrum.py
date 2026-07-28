from pathlib import Path
import unittest
from unittest import mock

import numpy as np

import models.e025_axisymmetric_wide_2hessian as e025
import models.e029_cone_safe_campaign as e029
import models.e030_margin_spectrum as e030
from models.e025_axisymmetric_wide_2hessian import AxisymmetricGrid
from models.e026_nonsymmetric_amg import AmgConfiguration


class E030MarginSpectrumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.system = e025.build_system(AxisymmetricGrid(8.0, 0.5, 1))
        cls.full_source = np.full(cls.system.size, 0.02)

    def test_strategy_is_bounded_and_never_advances_lineage(self) -> None:
        provenance = e030.implementation_provenance()
        strategy = provenance["strategy"]
        self.assertEqual(
            strategy["verification_amplitudes"],
            [49.0 / 96.0, 25.0 / 48.0],
        )
        self.assertEqual(strategy["accepted_baseline_amplitude"], 0.5)
        self.assertEqual(
            strategy["prediction_max_amplitude"], 13.0 / 24.0
        )
        for values in provenance["modules"].values():
            self.assertFalse(Path(values["path"]).is_absolute())
        self.assertIn(
            "accepted lineage remains",
            strategy["lineage_policy"].lower(),
        )

    def test_weighted_quantiles_use_positive_volume_weight(self) -> None:
        values = np.array([4.0, 1.0, 3.0, 2.0])
        weights = np.array([0.0, 1.0, 3.0, 2.0])
        quantiles = e030._weighted_quantiles(
            values, weights, (0.0, 0.5, 1.0)
        )
        self.assertEqual(quantiles["0"], 1.0)
        self.assertEqual(quantiles["0.5"], 2.0)
        self.assertEqual(quantiles["1"], 3.0)
        with self.assertRaises(ValueError):
            e030._weighted_quantiles(values, -weights)

    def test_identical_fields_have_zero_threshold_free_deficit(self) -> None:
        field = np.zeros(self.system.size)
        spectrum = e030.margin_deficit_spectrum(
            self.system,
            field,
            field,
            self.full_source,
        )
        for weighted in spectrum["spectra"].values():
            self.assertEqual(
                weighted["weighted_mean_positive_deficit"], 0.0
            )
            self.assertEqual(
                weighted["weighted_rms_positive_deficit"], 0.0
            )
            self.assertEqual(
                set(weighted["positive_deficit_quantiles"].values()),
                {0.0},
            )
            self.assertEqual(
                weighted["baseline_margin_quantiles"],
                weighted["current_margin_quantiles"],
            )

    def test_deficit_spectrum_separates_support_and_charge_weights(
        self,
    ) -> None:
        field = np.zeros(self.system.size)
        positive_nodes = np.flatnonzero(
            e025.nodal_volume_weights(self.system) > 0.0
        )[:3]
        source = np.zeros(self.system.size)
        source[positive_nodes] = [1.0, 10.0, 100.0]
        with mock.patch.object(
            e030,
            "_matched_pair_values",
            side_effect=[
                (np.array([1.0, 1.0, 1.0]), positive_nodes),
                (np.array([0.0, 0.5, 1.0]), positive_nodes),
            ],
        ):
            spectrum = e030.margin_deficit_spectrum(
                self.system,
                field,
                field,
                source,
            )
        support = spectrum["spectra"]["source_support_volume"]
        charge = spectrum["spectra"]["source_charge"]
        self.assertNotEqual(support["total_weight"], charge["total_weight"])
        self.assertNotEqual(
            support["weighted_mean_positive_deficit"],
            charge["weighted_mean_positive_deficit"],
        )
        self.assertGreater(support["weighted_mean_positive_deficit"], 0.0)
        self.assertGreater(charge["weighted_mean_positive_deficit"], 0.0)

    def test_affine_pair_components_do_not_add_shift_to_tangent(self) -> None:
        components = {
            "base_radial": np.array([0.0]),
            "base_mixed": np.array([0.0]),
            "base_axial": np.array([0.0]),
            "base_azimuthal": np.array([0.0]),
            "tangent_radial": np.array([-1.0]),
            "tangent_mixed": np.array([0.0]),
            "tangent_axial": np.array([-2.0]),
            "tangent_azimuthal": np.array([-3.0]),
        }
        baseline = e030._pair_from_affine_components(
            components, 0.0, 0.25
        )
        advanced = e030._pair_from_affine_components(
            components, 0.1, 0.25
        )
        np.testing.assert_allclose(baseline, [0.5])
        np.testing.assert_allclose(advanced, [0.0], atol=1.0e-15)

    def test_affine_components_reproduce_direct_matched_pairs(self) -> None:
        rng = np.random.default_rng(260728)
        baseline = rng.normal(scale=1.0e-3, size=self.system.size)
        tangent = rng.normal(scale=1.0e-3, size=self.system.size)
        components = e030._matched_affine_components(
            self.system, baseline, tangent
        )
        direct_baseline, baseline_nodes = e030._matched_pair_values(
            self.system, baseline
        )
        affine_baseline = e030._pair_from_affine_components(
            components, 0.0, self.system.shift
        )
        np.testing.assert_array_equal(
            components["global_nodes"], baseline_nodes
        )
        np.testing.assert_allclose(
            affine_baseline, direct_baseline, rtol=0.0, atol=1.0e-14
        )
        delta = 1.0 / 96.0
        direct_advanced, advanced_nodes = e030._matched_pair_values(
            self.system, baseline + delta * tangent
        )
        affine_advanced = e030._pair_from_affine_components(
            components, delta, self.system.shift
        )
        np.testing.assert_array_equal(baseline_nodes, advanced_nodes)
        np.testing.assert_allclose(
            affine_advanced, direct_advanced, rtol=0.0, atol=1.0e-14
        )

    def test_stage6_tangent_has_correct_source_sign(self) -> None:
        configuration = AmgConfiguration()
        linear = e025.solve_linear_reference(
            self.system, self.full_source
        )
        field, _stage = e029.solve_cone_safe_stage(
            self.system,
            self.full_source,
            linear / 2.0,
            e030.BASELINE_AMPLITUDE,
            configuration,
            newton_max_iterations=10,
        )
        tangent, report = e030.solve_stage6_tangent(
            self.system,
            self.full_source,
            field,
            configuration,
        )
        self.assertLess(
            report["direct_tangent_residual_ratio"],
            configuration.gmres_relative_tolerance,
        )
        epsilon = 1.0e-5
        residual_before = e025.shifted_residual(
            self.system,
            field,
            e030.BASELINE_AMPLITUDE * self.full_source,
        )
        residual_after = e025.shifted_residual(
            self.system,
            field + epsilon * tangent,
            (e030.BASELINE_AMPLITUDE + epsilon) * self.full_source,
        )
        source_scale = np.linalg.norm(
            self.full_source / (2.0 * self.system.cubic_coefficient)
        )
        directional_error = np.linalg.norm(
            residual_after - residual_before
        ) / (epsilon * source_scale)
        self.assertLess(directional_error, 1.0e-3)

    def test_crossing_scan_censors_baseline_and_bisects_new_crossing(
        self,
    ) -> None:
        positive_nodes = np.flatnonzero(
            e025.nodal_volume_weights(self.system) > 0.0
        )[:2]
        source = np.zeros(self.system.size)
        source[positive_nodes] = 1.0
        base_pairs = np.array([0.03, 0.01])
        components = {
            "global_nodes": positive_nodes,
            "base_radial": base_pairs / 2.0 - self.system.shift,
            "base_mixed": np.zeros(2),
            "base_axial": base_pairs / 2.0 - self.system.shift,
            "base_azimuthal": base_pairs / 2.0 - self.system.shift,
            "tangent_radial": np.array([-0.5, 0.0]),
            "tangent_mixed": np.zeros(2),
            "tangent_axial": np.array([-0.5, 0.0]),
            "tangent_azimuthal": np.array([-0.5, 0.0]),
        }
        with (
            mock.patch.object(
                e030,
                "_matched_affine_components",
                return_value=components,
            ),
            mock.patch.object(
                e029,
                "matched_tail_diagnostics",
                return_value={"thresholds": {}},
            ),
            mock.patch.object(
                e030,
                "margin_deficit_spectrum",
                return_value={"spectra": {}},
            ),
        ):
            spectrum = e030.tangent_crossing_spectrum(
                self.system,
                source,
                np.zeros(self.system.size),
                np.zeros(self.system.size),
            )
        low_tail = spectrum["threshold_crossings"]["0.02"]
        self.assertEqual(low_tail["preexisting_node_count"], 1)
        self.assertEqual(low_tail["new_crossing_node_count"], 1)
        self.assertAlmostEqual(
            low_tail["earliest_new_crossing"]["amplitude"],
            0.51,
            places=12,
        )

    def test_verification_schedule_is_exact_and_sequential(self) -> None:
        baseline = np.zeros(self.system.size)
        tangent = np.ones(self.system.size)
        first = np.full(self.system.size, 1.0)
        second = np.full(self.system.size, 2.0)
        stage_rows = [
            {"amplitude": e030.VERIFICATION_AMPLITUDES[0]},
            {"amplitude": e030.VERIFICATION_AMPLITUDES[1]},
        ]
        with (
            mock.patch.object(
                e029,
                "solve_cone_safe_stage",
                side_effect=[
                    (first.copy(), stage_rows[0].copy()),
                    (second.copy(), stage_rows[1].copy()),
                ],
            ) as solve,
            mock.patch.object(
                e029,
                "matched_tail_diagnostics",
                return_value={"thresholds": {}},
            ),
            mock.patch.object(
                e029,
                "evaluate_tail_gate",
                return_value={"passes": False},
            ),
            mock.patch.object(
                e030,
                "margin_deficit_spectrum",
                return_value={"spectra": {}},
            ),
            mock.patch.object(
                e030,
                "prediction_error_spectrum",
                return_value={},
            ),
        ):
            final, rows = e030._run_verifications(
                self.system,
                self.full_source,
                baseline,
                tangent,
                {"0.02": {}, "0.05": {}},
                AmgConfiguration(),
            )
        np.testing.assert_array_equal(final, second)
        self.assertEqual(
            [row["amplitude"] for row in rows],
            list(e030.VERIFICATION_AMPLITUDES),
        )
        self.assertEqual(solve.call_count, 2)
        np.testing.assert_array_equal(solve.call_args_list[0].args[2], baseline)
        np.testing.assert_array_equal(solve.call_args_list[1].args[2], first)


if __name__ == "__main__":
    unittest.main()

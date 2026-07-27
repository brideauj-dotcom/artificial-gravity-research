import copy
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import numpy as np

import models.e025_axisymmetric_wide_2hessian as e025
import models.e026_nonsymmetric_amg as e026
from models.e025_axisymmetric_wide_2hessian import AxisymmetricGrid
from models.e026_nonsymmetric_amg import AmgConfiguration
import models.e029_cone_safe_campaign as e029


class E029ConeSafeCampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.system = e025.build_system(AxisymmetricGrid(8.0, 0.5, 1))

    def test_zero_field_passes_every_shifted_gamma2_reconstruction(self) -> None:
        field = np.zeros(self.system.size)
        diagnostics = e029.full_gamma_diagnostics(self.system, field)
        self.assertTrue(diagnostics["passes"])
        for summary in diagnostics["reconstructions"].values():
            self.assertGreater(summary["minimum_sigma1"]["value"], 0.0)
            self.assertGreater(summary["minimum_pair_sum"]["value"], 0.0)
            self.assertGreater(summary["minimum_sigma2"]["value"], 0.0)
            self.assertEqual(
                summary["nonpositive_counts"],
                {"sigma1": 0, "pair": 0, "sigma2": 0},
            )

    def test_gamma_summary_rejects_positive_sigma2_outside_gamma2(self) -> None:
        eigenvalues = np.array([[-5.0, -5.0, 1.0]])
        summary = e029._gamma_summary(
            eigenvalues,
            np.array([1.0]),
            np.array([2.0]),
        )
        self.assertGreater(summary["minimum_sigma2"]["value"], 0.0)
        self.assertLess(summary["minimum_sigma1"]["value"], 0.0)
        self.assertLess(summary["minimum_pair_sum"]["value"], 0.0)
        self.assertFalse(summary["passes"])

    def test_tail_gate_freezes_all_predeclared_non_broadening_metrics(
        self,
    ) -> None:
        baseline = {
            "thresholds": {
                "0.05": {
                    "node_count": 4,
                    "positive_weight_node_count": 3,
                    "component_count": 1,
                    "source_support_weight_fraction": 0.2,
                    "source_transition_weight_fraction": 0.25,
                    "components": [
                        {"source_support_weight_fraction": 0.2}
                    ],
                },
                "0.02": {
                    "node_count": 1,
                    "positive_weight_node_count": 1,
                    "component_count": 1,
                    "source_support_weight_fraction": 0.05,
                    "source_transition_weight_fraction": 0.06,
                    "components": [
                        {"source_support_weight_fraction": 0.05}
                    ],
                },
            }
        }
        caps = e029.tail_caps_from_baseline(baseline)
        self.assertTrue(e029.evaluate_tail_gate(baseline, caps)["passes"])
        broadened = copy.deepcopy(baseline)
        broadened["thresholds"]["0.02"]["node_count"] = 2
        self.assertFalse(e029.evaluate_tail_gate(broadened, caps)["passes"])

    def test_connected_components_use_meridional_four_neighbors(self) -> None:
        weights = e025.nodal_volume_weights(self.system)
        support = np.ones(self.system.size, dtype=bool)
        by_coordinate = {
            (
                round(float(rho), 8),
                round(float(z), 8),
            ): index
            for index, (rho, z) in enumerate(
                zip(self.system.rho, self.system.z)
            )
        }
        nodes = np.array(
            [
                by_coordinate[(1.0, 1.0)],
                by_coordinate[(1.5, 1.0)],
                by_coordinate[(3.0, 3.0)],
            ]
        )
        components = e029._connected_components(
            self.system,
            nodes,
            weights,
            support,
            float(np.sum(weights)),
        )
        self.assertEqual(len(components), 2)
        self.assertEqual(
            sorted(component["node_count"] for component in components),
            [1, 2],
        )

    def test_small_cone_safe_stage_records_segment_audits(self) -> None:
        full_source = np.full(self.system.size, 0.02)
        full_linear = e025.solve_linear_reference(self.system, full_source)
        field, stage = e029.solve_cone_safe_stage(
            self.system,
            full_source,
            full_linear / 12.0,
            1.0 / 12.0,
            AmgConfiguration(),
            newton_max_iterations=8,
        )
        self.assertEqual(field.shape, (self.system.size,))
        self.assertLess(stage["relative_residual_l2"], 1.0e-7)
        self.assertTrue(stage["full_gamma"]["passes"])
        self.assertGreater(len(stage["history"]), 0)
        for row in stage["history"]:
            self.assertTrue(row["full_gamma"]["passes"])
            self.assertTrue(row["segment_audit"]["passes"])
            self.assertEqual(
                row["segment_audit"]["sample_count"],
                e029.SEGMENT_INTERIOR_SAMPLES,
            )
            samples = row["segment_audit"]["samples"]
            self.assertEqual(len(samples), e029.SEGMENT_INTERIOR_SAMPLES)
            self.assertEqual(
                [item["fraction"] for item in samples],
                [index / 10.0 for index in range(1, 10)],
            )
            for item in samples:
                self.assertEqual(len(item["field_sha256"]), 64)
                self.assertTrue(item["diagnostics"]["passes"])

    def test_segment_audit_records_a_forced_failing_sample(self) -> None:
        field = np.zeros(self.system.size)
        passing = e029.full_gamma_diagnostics(self.system, field)
        failing = copy.deepcopy(passing)
        failing["passes"] = False
        responses = [copy.deepcopy(passing) for _ in range(9)]
        responses[4] = failing
        with mock.patch.object(
            e029,
            "full_gamma_diagnostics",
            side_effect=responses,
        ):
            audit = e029._segment_cone_audit(
                self.system,
                field,
                field,
            )
        self.assertFalse(audit["passes"])
        self.assertEqual(len(audit["samples"]), 9)
        self.assertEqual(audit["samples"][4]["fraction"], 0.5)
        self.assertFalse(audit["samples"][4]["diagnostics"]["passes"])

    def test_artifact_reports_bind_role_and_exact_field(self) -> None:
        fine = np.arange(5, dtype=float)
        coarse = np.arange(3, dtype=float)
        report = {
            "fine_output_field_sha256": e029._sha256_array(fine),
            "coarse_output_field_sha256": e029._sha256_array(coarse),
        }
        fine_report = e029.artifact_report(report, "fine", fine)
        self.assertEqual(fine_report["artifact_role"], "fine")
        self.assertEqual(
            fine_report["output_field_sha256"],
            report["fine_output_field_sha256"],
        )
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "fine.npz"
            e026.save_campaign_artifact(artifact, fine, fine_report)
            loaded_field, loaded_report = e026.load_campaign_artifact(artifact)
        np.testing.assert_array_equal(loaded_field, fine)
        self.assertEqual(loaded_report["artifact_role"], "fine")
        with self.assertRaises(ValueError):
            e029.artifact_report(report, "fine", coarse)
        with self.assertRaises(ValueError):
            e029.artifact_report(report, "invalid", fine)

    def test_strategy_fingerprint_is_relocatable_and_rational_schedule_fixed(
        self,
    ) -> None:
        provenance = e029.implementation_provenance()
        for values in provenance["modules"].values():
            self.assertFalse(values["path"].startswith("/"))
        self.assertEqual(e029.TARGET_AMPLITUDES, (13.0 / 24.0, 14.0 / 24.0))
        self.assertEqual(e029.SEGMENT_INTERIOR_SAMPLES, 9)
        self.assertEqual(e029.MATCHED_DIFFERENCE_STEP, 0.25)
        self.assertEqual(e029.COMMON_WINDOW_RADIUS, 78.5)


if __name__ == "__main__":
    unittest.main()

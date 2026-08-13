import json
import math
from pathlib import Path
import tempfile
import unittest

import models.e041_sme_joint_region_audit as e041


class E041SmeJointRegionAuditTests(unittest.TestCase):
    def test_table_ii_marginals_are_transcribed(self) -> None:
        record = e041.combined_analysis_public_record()
        table = record["coefficient_table"]
        self.assertEqual(
            [
                (
                    row["label"],
                    row["central_in_1e_minus9_m2"],
                    row["marginal_2sigma_in_1e_minus9_m2"],
                )
                for row in table
            ],
            [
                ("XXXX", 6.4, 32.9),
                ("XXXY", 0.0, 8.1),
                ("XXXZ", -2.0, 2.6),
                ("XXYY", -0.9, 10.9),
                ("XXYZ", 1.1, 1.2),
                ("XXZZ", -2.6, 17.1),
                ("XYYY", 3.9, 8.1),
                ("XYYZ", -0.6, 1.2),
                ("XYZZ", -1.0, 1.0),
                ("XZZZ", -8.1, 10.3),
                ("YYYY", 7.0, 32.9),
                ("YYYZ", 0.3, 2.6),
                ("YYZZ", -2.5, 17.1),
                ("YZZZ", 3.6, 10.2),
            ],
        )

    def test_public_record_does_not_invent_joint_products(self) -> None:
        record = e041.combined_analysis_public_record()
        self.assertEqual(record["audit_date"], "2026-08-13")
        self.assertGreaterEqual(len(record["audited_surfaces"]), 5)
        self.assertTrue(
            all(record["not_recovered_on_audited_surfaces"].values())
        )
        self.assertFalse(record["supplement_recovered_on_audited_surfaces"])
        self.assertFalse(record["statistical_independence_claimed"])
        self.assertEqual(
            record["source_package_contents"], ["paper.tex", "fig1.eps"]
        )

    def test_same_marginals_permit_incompatible_projection_variances(self) -> None:
        demo = e041.projection_nonidentifiability_demo()
        self.assertEqual(demo["shared_marginal_variances"], [1.0, 1.0])
        self.assertTrue(math.isclose(demo["projection_variance_positive"], 3.98))
        self.assertTrue(math.isclose(demo["projection_variance_negative"], 0.02))
        self.assertTrue(math.isclose(demo["projection_variance_ratio"], 199.0))
        self.assertGreater(demo["projection_standard_deviation_ratio"], 14.0)

    def test_covariance_and_quadratic_form_validate_inputs(self) -> None:
        with self.assertRaises(ValueError):
            e041.covariance_pair(1.1)
        with self.assertRaises(ValueError):
            e041.quadratic_form((1.0,), ((1.0, 0.0), (0.0, 1.0)))
        with self.assertRaises(ValueError):
            e041.projection_nonidentifiability_demo(1.0)

    def test_marginal_box_has_no_claimed_simultaneous_coverage(self) -> None:
        diagnostic = e041.marginal_coverage_diagnostic()
        self.assertGreater(
            diagnostic["independence_product_joint_coverage"], 0.50
        )
        self.assertLess(
            diagnostic["independence_product_joint_coverage"], 0.53
        )
        self.assertTrue(
            math.isclose(
                diagnostic["arbitrary_dependence_frechet_lower"],
                0.362996305451,
                rel_tol=1e-10,
            )
        )
        self.assertTrue(
            math.isclose(
                diagnostic["arbitrary_dependence_frechet_upper"],
                0.9544997361036416,
            )
        )
        self.assertFalse(diagnostic["is_valid_joint_region_for_2016_fit"])

    def test_2026_design_is_proposal_not_measured_torque(self) -> None:
        design = e041.stripe_design_public_record()
        self.assertEqual(
            design["status"], "proposal_and_parameter_optimization_not_measurement"
        )
        self.assertTrue(design["matrix_structure_equations_published"])
        self.assertEqual(design["matrix_dimensions"]["A2"], "4x4")
        self.assertEqual(
            design["published_root_rule"]["A1_A2_A3"],
            "square root of absolute determinant",
        )
        self.assertFalse(design["dimensionally_consistent_common_transfer_units"])
        self.assertFalse(design["full_numerical_transfer_matrix_entries_published"])
        self.assertFalse(design["measured_five_stripe_harmonics_published"])
        self.assertFalse(design["measured_five_stripe_same_harmonic_noise_published"])

    def test_four_gates_fail_closed_at_constraints(self) -> None:
        gates = e041.e041_gates()
        self.assertEqual(
            set(gates),
            {
                "1_source_coupling",
                "2_constraints_validity",
                "3_absolute_scale",
                "4_falsification",
            },
        )
        self.assertEqual(gates["1_source_coupling"]["status"], "partial")
        self.assertEqual(gates["2_constraints_validity"]["status"], "failed")
        self.assertEqual(gates["3_absolute_scale"]["status"], "unknown")
        self.assertEqual(gates["4_falsification"]["status"], "partial")

    def test_portfolio_refresh_is_diverse_and_only_p017_was_deepened(self) -> None:
        candidates = e041.portfolio_refresh()
        self.assertEqual(len(candidates), 6)
        self.assertEqual(len({item["category"] for item in candidates}), 6)
        self.assertEqual(candidates[0]["id"], "P-017")
        self.assertEqual(
            [
                item["id"]
                for item in candidates
                if item["disposition"] == "deepened_then_parked_in_e041"
            ],
            ["P-017"],
        )

    def test_survival_rule_forbids_torque_propagation(self) -> None:
        decision = e041.survival_rule_evaluation()
        self.assertFalse(decision["joint_region_available"])
        self.assertFalse(decision["full_numerical_five_stripe_transfer_available"])
        self.assertFalse(decision["absolute_allowed_torque_propagation_authorized"])
        self.assertIsNone(decision["allowed_harmonic_snr"])
        self.assertEqual(
            decision["disposition"],
            "parked_joint_region_and_transfer_not_recoverable",
        )

    def test_scope_records_no_fit_torque_or_resource_expansion(self) -> None:
        resources = e041.run_analysis()["resource_accounting"]
        self.assertTrue(all(value == 0 for value in resources.values()))

    def test_cli_writes_identical_deterministic_reports(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first_path = Path(directory) / "e041-first.json"
            second_path = Path(directory) / "e041-second.json"
            exit_code = e041.main(["--report-json", str(first_path)])
            second_exit_code = e041.main(
                ["--report-json", str(second_path)]
            )
            self.assertEqual(
                first_path.read_bytes(), second_path.read_bytes()
            )
            report = json.loads(first_path.read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(second_exit_code, 0)
        self.assertEqual(report["provenance"]["campaign"], "E-041")
        self.assertEqual(
            report["decision"]["status"],
            "parked_joint_region_and_transfer_not_recoverable",
        )


if __name__ == "__main__":
    unittest.main()

import json
import math
from pathlib import Path
import tempfile
import unittest

import models.e042_agbresa_trial_audit as e042


class E042AgbresaTrialAuditTests(unittest.TestCase):
    @staticmethod
    def _find_outcome(system: str) -> dict:
        return next(
            row for row in e042.outcome_matrix() if row["system"] == system
        )

    def test_mean_mechanics_reproduce_loaded_radii_and_gradient(self) -> None:
        audit = e042.mechanics_audit()
        self.assertTrue(
            math.isclose(
                audit["mean_omega_rad_s"],
                3.193952531149623,
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                audit["derived_mean_1g_com_radius_m"],
                0.9613106659602458,
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                audit["derived_mean_2g_foot_radius_m"],
                1.9226213319204917,
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                audit["derived_acceleration_gradient_g_per_m"],
                1.040246442081351,
                rel_tol=1e-12,
            )
        )
        self.assertTrue(audit["mean_2g_radius_inside_reported_foot_range"])

    def test_apparatus_radius_is_not_misused_as_loaded_foot_radius(self) -> None:
        audit = e042.mechanics_audit()
        self.assertTrue(
            math.isclose(
                audit["g_level_at_apparatus_radius_at_mean_rpm"],
                3.9529364799091344,
                rel_tol=1e-12,
            )
        )
        self.assertNotEqual(
            audit["apparatus_radius_m"],
            audit["derived_mean_2g_foot_radius_m"],
        )
        self.assertIn("not the participant foot radius", audit["geometry_correction"])
        self.assertIn("motor", audit["reaction_ledger"])

    def test_mechanics_helpers_validate_inputs(self) -> None:
        with self.assertRaises(ValueError):
            e042.acceleration_m_s2(-1.0, 30.0)
        with self.assertRaises(ValueError):
            e042.acceleration_m_s2(1.0, -30.0)
        with self.assertRaises(ValueError):
            e042.radius_for_g(1.0, 0.0)
        with self.assertRaises(ValueError):
            e042.radius_for_g(-1.0, 30.0)

    def test_nominal_dose_and_adherence_denominators_are_explicit(self) -> None:
        dose = e042.nominal_dose_audit()
        self.assertEqual(dose["nominal_plateau_hours_per_participant"], 30.0)
        self.assertEqual(dose["nominal_com_g_hours_per_participant"], 30.0)
        self.assertEqual(dose["nominal_foot_g_hours_per_participant"], 60.0)
        self.assertTrue(
            math.isclose(dose["nominal_fraction_of_campaign_time"], 1 / 48)
        )
        events = dose["specific_tolerability_report"]
        self.assertEqual(events["sessions"], 960)
        self.assertEqual(events["prematurely_terminated"], 10)
        self.assertEqual(events["presyncope_terminations"], 7)
        self.assertEqual(events["severe_motion_sickness_terminations"], 1)
        self.assertEqual(events["biopsy_pain_terminations"], 2)
        self.assertEqual(events["participants_with_termination"], 6)
        self.assertFalse(dose["exact_delivered_minutes_recoverable_from_public_reports"])

    def test_registered_and_reported_intermittent_breaks_are_not_conflated(self) -> None:
        discrepancy = e042.nominal_dose_audit()[
            "intermittent_break_discrepancy"
        ]
        self.assertEqual(discrepancy["registry_minutes"], 5)
        self.assertEqual(discrepancy["primary_reports_minutes"], 3)
        self.assertFalse(discrepancy["resolved"])

    def test_prospective_record_does_not_supply_conventional_randomization(self) -> None:
        design = e042.registry_and_design_audit()
        self.assertTrue(design["prospective"])
        self.assertFalse(design["conventional_random_sequence_for_all_participants"])
        self.assertIn("semi-random", design["allocation"])
        self.assertFalse(design["sequence_generation_details_recovered"])
        self.assertFalse(design["allocation_concealment_details_recovered"])
        self.assertFalse(design["sham_centrifuge_control"])
        self.assertFalse(
            design[
                "prospectively_linked_protocol_or_sap_supplying_endpoint_hierarchy_recovered"
            ]
        )

    def test_endpoint_appendix_lists_bmd_but_not_specific_bmat_primary(self) -> None:
        appendix = e042.registry_and_design_audit()[
            "prospective_appendix_audit"
        ]
        self.assertTrue(appendix["lumbar_spine_dxa_bmd_explicitly_listed"])
        self.assertFalse(appendix["bone_marrow_adipose_tissue_term_present"])
        self.assertFalse(appendix["fat_fraction_term_present"])
        self.assertTrue(appendix["broad_mri_vertebral_composition_endpoint_present"])
        self.assertFalse(appendix["publication_primary_bmat_hierarchy_recoverable"])

    def test_bmat_is_signal_not_regimen_specific_prevention(self) -> None:
        bmat = self._find_outcome("lumbar_bone_marrow_adipose_tissue")
        self.assertEqual(
            bmat["descriptive_control_minus_continuous_percentage_points"],
            5.14,
        )
        self.assertEqual(
            bmat["descriptive_control_minus_intermittent_percentage_points"],
            3.93,
        )
        self.assertEqual(bmat["controlled_omnibus_p"], 0.032)
        self.assertFalse(bmat["pairwise_controlled_contrasts_reported"])
        self.assertIsNone(bmat["pairwise_control_vs_continuous_effect_ci_p"])
        self.assertIsNone(bmat["pairwise_control_vs_intermittent_effect_ci_p"])
        self.assertFalse(bmat["multiple_testing_correction"])
        self.assertEqual(bmat["decision"], "qualified_positive_controlled_signal")

    def test_within_arm_bmd_significance_does_not_establish_efficacy(self) -> None:
        bmd = self._find_outcome("lumbar_bone_mineral_density")
        self.assertEqual(bmd["control_within_arm_p"], 0.007)
        self.assertEqual(bmd["continuous_within_arm_p"], 0.036)
        self.assertFalse(bmd["controlled_between_arm_difference_significant"])
        self.assertEqual(bmd["decision"], "controlled_efficacy_not_demonstrated")
        killed = {
            row["claim"]: row["supported"] for row in e042.claim_kill_matrix()
        }
        self.assertFalse(killed["30 minutes per day prevented lumbar BMD loss"])

    def test_orthostatic_signal_retains_baseline_imbalance(self) -> None:
        outcome = self._find_outcome("orthostatic_tolerance_time_to_presyncope")
        self.assertEqual(outcome["bedrest_by_countermeasure_interaction_p"], 0.0249)
        self.assertEqual(outcome["post_bedrest_between_group_p"], 0.5279)
        self.assertEqual(outcome["baseline_between_group_p"], 0.047)
        self.assertEqual(
            outcome["derived_post_seconds_mean"],
            {"control": 575, "continuous": 611, "intermittent": 600},
        )
        self.assertIn("baseline-advantaged control", outcome["qualification"])

    def test_companion_results_forbid_blanket_multisystem_claim(self) -> None:
        aerobic = self._find_outcome("aerobic_exercise_capacity")
        cardiac = self._find_outcome("cardiac_structure_and_function")
        autonomic = self._find_outcome("autonomic_cardiovascular_control")
        muscle = self._find_outcome("muscle_function")
        self.assertFalse(aerobic["vo2max_group_by_time_significant"])
        self.assertFalse(cardiac["between_group_differences_observed"])
        self.assertFalse(autonomic["bedrest_by_intervention_interactions_observed"])
        self.assertFalse(muscle["post_hoc_arm_contrasts_performed"])
        self.assertIn("muscle contractions", muscle["qualification"])
        decision = e042.survival_rule_evaluation()
        self.assertFalse(decision["multipurpose_countermeasure_pass"])
        self.assertFalse(decision["continuous_vs_intermittent_superiority_identified"])

    def test_safety_uses_session_and_participant_denominators(self) -> None:
        safety = self._find_outcome("tolerability_and_safety")
        self.assertTrue(
            math.isclose(safety["premature_termination_fraction"], 10 / 960)
        )
        self.assertTrue(
            math.isclose(safety["presyncope_termination_fraction"], 7 / 960)
        )
        self.assertEqual(safety["participants_with_termination_fraction"], 6 / 16)
        self.assertIn("2 continuous-arm", safety["frequent_isolated_pvcs"])

    def test_four_gates_and_category_boundary_are_frozen(self) -> None:
        gates = e042.p022_gates()
        self.assertEqual(
            set(gates),
            {
                "1_source_coupling",
                "2_constraints_validity",
                "3_absolute_scale",
                "4_falsification",
            },
        )
        self.assertEqual(gates["1_source_coupling"]["status"], "passed")
        self.assertEqual(gates["2_constraints_validity"]["status"], "partial")
        self.assertEqual(gates["3_absolute_scale"]["status"], "passed")
        self.assertEqual(gates["4_falsification"]["status"], "passed")
        self.assertFalse(e042.survival_rule_evaluation()["real_curvature_or_inertial_control"])

    def test_portfolio_is_diverse_and_only_p022_was_deepened(self) -> None:
        portfolio = e042.portfolio_refresh()
        self.assertEqual([item["id"] for item in portfolio], ["P-022", "P-023", "P-024", "P-025", "P-026"])
        self.assertEqual(len({item["category"] for item in portfolio}), 5)
        self.assertEqual(
            [item["id"] for item in portfolio if item["disposition"].startswith("deepened")],
            ["P-022"],
        )
        self.assertEqual(portfolio[1]["disposition"], "queue_e043_same_unit_force_reaction_audit")

    def test_broad_program_stays_parked_and_resources_stay_zero(self) -> None:
        decision = e042.survival_rule_evaluation()
        self.assertFalse(decision["broad_e008_reopened"])
        future = e042.future_falsification_design()
        self.assertFalse(future["queued"])
        self.assertIn(
            "every prospectively required domain",
            future["design_if_reopened"]["kill_rule"],
        )
        resources = e042.run_analysis()["resource_accounting"]
        self.assertTrue(all(value == 0 for value in resources.values()))

    def test_cli_writes_identical_deterministic_reports(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first_path = Path(directory) / "e042-first.json"
            second_path = Path(directory) / "e042-second.json"
            first_exit = e042.main(["--report-json", str(first_path)])
            second_exit = e042.main(["--report-json", str(second_path)])
            self.assertEqual(first_path.read_bytes(), second_path.read_bytes())
            report = json.loads(first_path.read_text(encoding="utf-8"))
        self.assertEqual(first_exit, 0)
        self.assertEqual(second_exit, 0)
        self.assertEqual(report["provenance"]["campaign"], "E-042")
        self.assertEqual(
            report["decision"]["status"],
            "bounded_endpoint_signals_but_multipurpose_claim_rejected",
        )
        self.assertFalse(report["decision"]["broad_program_reopened"])


if __name__ == "__main__":
    unittest.main()

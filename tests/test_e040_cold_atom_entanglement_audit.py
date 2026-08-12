import json
import math
from pathlib import Path
import tempfile
import unittest

import models.e040_cold_atom_entanglement_audit as e040


class E040ColdAtomEntanglementAuditTests(unittest.TestCase):
    def test_frozen_oblate_geometry_is_self_consistent(self) -> None:
        geometry = e040.oblate_geometry()
        self.assertTrue(math.isclose(geometry["volume_m3"], 1.0e-6))
        self.assertTrue(math.isclose(
            geometry["equatorial_radius_m"],
            0.010_625_627_802_375_215,
            rel_tol=1.0e-12,
        ))
        self.assertTrue(math.isclose(
            geometry["minimum_center_spacing_m"],
            0.004_228_946_469_893_669,
            rel_tol=1.0e-12,
        ))
        self.assertEqual(geometry["screen_or_hardware_clearance_m"], 0.0)

    def test_quantum_signal_and_snr_are_absolute_and_reproducible(self) -> None:
        signal = e040.quantum_signal_budget()
        self.assertTrue(math.isclose(
            signal["dimensionless_lambda"],
            1.676_521_009_399_964_7e-19,
            rel_tol=1.0e-12,
        ))
        self.assertTrue(math.isclose(
            signal["covariance_signal_atoms_squared"],
            41_913.025_234_999_12,
            rel_tol=1.0e-12,
        ))
        self.assertTrue(math.isclose(
            signal["ideal_quantum_limited_snr"],
            0.118_547_937_454_843_06,
            rel_tol=1.0e-12,
        ))
        self.assertLess(signal["ideal_quantum_limited_snr"], 1.0)
        self.assertTrue(signal["perturbative_lambda_N_condition_satisfied"])
        self.assertTrue(math.isclose(
            signal[
                "point_mass_acceleration_per_atom_from_other_ensemble_m_s2"
            ],
            8.236_320_588_389_41e-19,
            rel_tol=1.0e-11,
        ))
        self.assertTrue(math.isclose(
            signal["point_mass_force_between_ensemble_masses_N"],
            1.817_712_263_913_728_4e-31,
            rel_tol=1.0e-11,
        ))

    def test_snr_one_requires_far_more_than_frozen_trials(self) -> None:
        signal = e040.quantum_signal_budget()
        self.assertTrue(math.isclose(
            signal["effective_trials_required_for_snr_one"],
            355_780.384_095_990_4,
            rel_tol=1.0e-12,
        ))
        self.assertGreater(
            signal["effective_trials_required_for_snr_one"],
            signal["effective_independent_trials"] * 70.0,
        )
        self.assertGreater(
            signal["minimum_elapsed_years_per_setup_for_snr_one"],
            2.25,
        )

    def test_ideal_variations_do_not_become_detector_qualification(self) -> None:
        diagnostic = e040.ideal_sensitivity_diagnostic()
        self.assertTrue(math.isclose(
            diagnostic[
                "ideal_snr_at_baseline_density_under_inferred_schedule"
            ],
            0.374_881_494_272_488_5,
            rel_tol=1.0e-12,
        ))
        self.assertGreater(
            diagnostic[
                "ideal_density_for_snr_one_cm3_under_inferred_schedule"
            ],
            1.0e13,
        )
        self.assertLess(
            diagnostic[
                "ideal_density_for_snr_one_cm3_under_inferred_schedule"
            ],
            2.0e13,
        )
        self.assertFalse(diagnostic["qualified_detector_regime_established"])

    def test_classical_formula_is_diagnostic_not_a_covariance_prediction(self) -> None:
        classical = e040.classical_countermodel_diagnostic(0.1)
        self.assertTrue(math.isclose(
            classical["sqrt_vartheta"],
            4.772_585_082_288_505_4e-5,
            rel_tol=1.0e-12,
        ))
        self.assertTrue(math.isclose(
            classical["vartheta"],
            2.277_756_836_768_278e-9,
            rel_tol=1.0e-12,
        ))
        self.assertFalse(classical["maps_to_cold_atom_covariance"])
        self.assertFalse(classical["maps_to_cold_atom_snr"])
        self.assertIsNone(classical["fraction_of_quantum_covariance"])

    def test_confounders_fail_closed_when_same_observable_bounds_are_absent(self) -> None:
        ledger = e040.apparatus_and_confounder_ledger()
        self.assertEqual(ledger["predeclared_max_fraction_of_target"], 0.10)
        self.assertTrue(all(
            item["same_covariance_bound"] is None
            for item in ledger["confounders"]
        ))
        self.assertTrue(all(
            not item["qualified_below_fraction"]
            for item in ledger["confounders"]
        ))
        self.assertIn(
            "equal and opposite",
            ledger["source_and_reaction"]["field_reaction"],
        )

    def test_four_progressive_gates_are_explicit(self) -> None:
        gates = e040.e040_gates()
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
        self.assertEqual(gates["3_absolute_scale"]["status"], "partial")
        self.assertEqual(gates["4_falsification"]["status"], "partial")

    def test_portfolio_refresh_is_diverse_and_only_p012_was_deepened(self) -> None:
        candidates = e040.portfolio_refresh()
        self.assertEqual(len(candidates), 6)
        self.assertEqual(len({item["category"] for item in candidates}), 6)
        self.assertEqual(candidates[0]["id"], "P-012")
        self.assertEqual(candidates[1]["id"], "P-017")
        self.assertEqual(
            [
                item["id"]
                for item in candidates
                if item["disposition"] == "deepened_then_parked_in_e040"
            ],
            ["P-012"],
        )
        for candidate in candidates:
            self.assertEqual(
                set(candidate["gates"]),
                {
                    "1_source_coupling",
                    "2_constraints_validity",
                    "3_absolute_scale",
                    "4_falsification",
                },
            )

    def test_survival_rule_parks_p012_without_broad_theory_claim(self) -> None:
        decision = e040.survival_rule_evaluation()
        self.assertFalse(decision["survived"])
        self.assertFalse(decision["classical_covariance_mapping_available"])
        self.assertIsNone(
            decision["classical_covariance_below_predeclared_fraction"]
        )
        self.assertFalse(
            decision["all_dominant_backgrounds_below_predeclared_fraction"]
        )
        self.assertEqual(
            decision["disposition"],
            "parked_no_joint_detector_or_model_qualification",
        )
        report = e040.run_analysis()
        self.assertIn("not a rejection", report["decision"]["claim_boundary"])
        self.assertIn("E-041", report["decision"]["next_best_step"])

    def test_scope_records_no_numerical_or_hardware_expansion(self) -> None:
        resources = e040.run_analysis()["resource_accounting"]
        self.assertEqual(resources["pde_builds"], 0)
        self.assertEqual(resources["pde_solves"], 0)
        self.assertEqual(resources["hardware_actions"], 0)
        self.assertEqual(resources["checkpoint_reads_or_writes"], 0)
        self.assertEqual(resources["compute_expansion"], 0)

    def test_invalid_countermodel_geometry_ratio_is_rejected(self) -> None:
        for value in (0.0, -0.1, 1.1):
            with self.assertRaises(ValueError):
                e040.classical_countermodel_diagnostic(value)

    def test_cli_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "e040.json"
            exit_code = e040.main(["--report-json", str(path)])
            report = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(report["provenance"]["campaign"], "E-040")
        self.assertEqual(
            report["decision"]["status"],
            "parked_no_joint_detector_or_model_qualification",
        )


if __name__ == "__main__":
    unittest.main()

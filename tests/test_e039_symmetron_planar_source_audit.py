import json
import math
from pathlib import Path
import tempfile
import unittest

import models.e039_symmetron_planar_source_audit as e039


class E039SymmetronPlanarSourceAuditTests(unittest.TestCase):
    def test_meter_conversion_has_the_correct_exponent(self) -> None:
        self.assertTrue(math.isclose(
            e039.METER_TO_INVERSE_EV,
            5.067_730_716_156_395e6,
            rel_tol=1.0e-12,
        ))
        self.assertTrue(math.isclose(
            e039.inverse_ev_to_meters(e039.meters_to_inverse_ev(1.0)),
            1.0,
            rel_tol=1.0e-15,
        ))

    def test_public_notebook_source_is_about_one_trillion_too_thin(self) -> None:
        audit = e039.source_unit_audit()
        self.assertGreater(
            audit["conversion_factor_correct_over_notebook"],
            1.0e12,
        )
        self.assertLess(
            audit["conversion_factor_correct_over_notebook"],
            1.01e12,
        )
        self.assertTrue(math.isclose(
            audit["notebook_encoded_R_inverse_eV"],
            1.518e-8,
            rel_tol=1.0e-15,
        ))
        self.assertLess(
            audit["notebook_encoded_R_equivalent_m"],
            3.1e-15,
        )
        self.assertGreater(
            audit["notebook_encoded_R_equivalent_m"],
            2.9e-15,
        )

    def test_thin_sheet_asymptotic_reproduces_reported_chi_zero(self) -> None:
        audit = e039.source_unit_audit()
        self.assertLess(
            audit["thin_sheet_relative_error_vs_reported"],
            1.0e-8,
        )
        self.assertTrue(math.isclose(
            audit["thin_sheet_chi_from_notebook_R"],
            e039.NOTEBOOK_REPORTED_CHI_0,
            rel_tol=1.0e-8,
        ))

    def test_correct_source_is_in_the_deep_screening_regime(self) -> None:
        audit = e039.source_unit_audit()
        self.assertLess(audit["m_in_R_notebook"], 1.0e-4)
        self.assertGreater(audit["m_in_R_physical"], 5.0e7)
        self.assertLess(
            audit["physical_thick_wall_surface_chi_estimate"],
            2.1e-5,
        )
        self.assertLess(
            audit["physical_center_chi_log10_upper_estimate"],
            -2.0e7,
        )

    def test_cannex_thresholds_are_prospective_not_measured(self) -> None:
        detector = e039.detector_and_geometry_audit()["detector"]
        self.assertEqual(detector["separation_um"], [3.0, 30.0])
        self.assertEqual(detector["projected_pressure_sensitivity_Pa"], 1.0e-9)
        self.assertEqual(
            detector["projected_pressure_gradient_sensitivity_Pa_per_m"],
            1.0e-3,
        )
        self.assertIn("prospective", detector["threshold_status"])
        self.assertIn("not achieved", detector["threshold_status"])

    def test_measured_nulls_are_geometry_overlays_only(self) -> None:
        overlays = e039.detector_and_geometry_audit()[
            "nonplanar_constraint_overlays"
        ]
        self.assertEqual(len(overlays), 4)
        self.assertTrue(all(
            item["use"] == "parameter exclusion only" for item in overlays
        ))
        self.assertTrue(all(
            item["planar_loop_profile_transfer_allowed"] is False
            for item in overlays
        ))
        neutron = next(
            item for item in overlays if "Dvorak" in item["experiment"]
        )
        self.assertIsNone(neutron["published_scalar_phase_threshold_rad"])

    def test_all_four_gates_are_explicit_and_fail_closed(self) -> None:
        gates = e039.e039_gates()
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
        self.assertEqual(gates["3_absolute_scale"]["status"], "failed")
        self.assertEqual(gates["4_falsification"]["status"], "partial")

    def test_survival_rule_parks_without_reopening_the_model_family(self) -> None:
        result = e039.survival_rule_evaluation()
        self.assertFalse(result["physical_source_instantiated_by_public_notebook"])
        self.assertFalse(
            result["corrected_benchmark_has_validated_numerical_result"]
        )
        self.assertTrue(result["preprint_large_D_or_R_accuracy_warning_applies"])
        self.assertFalse(result["qualified_corrected_absolute_planar_signal"])
        self.assertFalse(result["measured_planar_source_modulated_threshold"])
        self.assertFalse(result["survived"])
        self.assertEqual(
            result["disposition"],
            "parked_source_unit_and_detector_scale_gates_failed",
        )
        self.assertIn("materially new", result["reopen_condition"])

    def test_portfolio_is_diverse_and_only_p008_was_deepened(self) -> None:
        candidates = e039.portfolio_refresh()
        self.assertEqual(len(candidates), 6)
        self.assertEqual(len({item["category"] for item in candidates}), 6)
        selected = [
            item["id"]
            for item in candidates
            if item["disposition"] == "deepened_then_parked_in_e039"
        ]
        self.assertEqual(selected, ["P-008"])
        self.assertEqual(candidates[1]["id"], "P-012")
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

    def test_report_preserves_scope_and_claim_boundaries(self) -> None:
        report = e039.run_analysis()
        self.assertEqual(
            report["decision"]["status"],
            "parked_source_unit_and_detector_scale_gates_failed",
        )
        self.assertIn("not the abstract", report["decision"]["claim_boundary"])
        self.assertIn("E-040", report["decision"]["next_best_step"])
        self.assertEqual(report["portfolio"]["selected_for_deepening"], "P-008")
        self.assertIn(
            "No candidate supports practical artificial gravity",
            report["portfolio"]["screen_result"],
        )
        self.assertEqual(report["resource_accounting"]["pde_builds"], 0)
        self.assertEqual(report["resource_accounting"]["pde_solves"], 0)
        self.assertEqual(report["resource_accounting"]["hardware_actions"], 0)
        self.assertEqual(
            report["resource_accounting"]["checkpoint_reads_or_writes"],
            0,
        )

    def test_negative_distances_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            e039.meters_to_inverse_ev(-1.0)
        with self.assertRaises(ValueError):
            e039.inverse_ev_to_meters(-1.0)
        with self.assertRaises(ValueError):
            e039.thin_sheet_surface_value(-1.0)

    def test_cli_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "e039.json"
            exit_code = e039.main(["--report-json", str(path)])
            report = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(report["provenance"]["campaign"], "E-039")
        self.assertEqual(
            report["provenance"]["public_code_commit"],
            e039.PUBLIC_CODE_COMMIT,
        )


if __name__ == "__main__":
    unittest.main()

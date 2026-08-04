import json
import math
from pathlib import Path
import tempfile
import unittest

import models.e038_bl_short_range_signal as e038


class E038BLShortRangeSignalTests(unittest.TestCase):
    def test_canonical_normalization_and_material_response_are_frozen(self) -> None:
        self.assertTrue(math.isclose(
            e038.pure_neutron_alpha_per_g_squared(),
            1.3670458518002497e37,
            rel_tol=1.0e-14,
        ))
        self.assertTrue(math.isclose(
            e038.au_si_silica_response_factor(),
            0.3065680716648778,
            rel_tol=1.0e-14,
        ))
        audit = e038.normalization_audit()
        self.assertIn("4*pi", audit["potential_SI"])
        self.assertAlmostEqual(
            audit["phase_ratio_potential_normalized_over_canonical"],
            4.0 * math.pi,
        )
        self.assertEqual(
            audit["normalization_finding"],
            "internal_4pi_discrepancy_under_canonical_normalization",
        )

    def test_final_microscope_screen_kills_useful_long_range_force(self) -> None:
        bound = e038.microscope_long_range_bound()
        self.assertTrue(math.isclose(bound["eta_95_conservative"], 6.881975845356424e-15, rel_tol=1.0e-14))
        self.assertTrue(math.isclose(
            bound["epsilon_B_minus_L_95_approx"],
            4.3583530244485915e-25,
            rel_tol=1.0e-14,
        ))
        self.assertTrue(math.isclose(
            bound["canonical_g_X_95_approx"],
            1.319805706372805e-25,
            rel_tol=1.0e-14,
        ))
        self.assertLess(
            bound["typical_neutral_matter_force_fraction_vs_gravity"],
            6.0e-14,
        )

    def test_short_range_recast_fails_the_proposal_phase_threshold(self) -> None:
        rows = {row["range_um"]: row for row in e038.optomechanical_josephson_rows()}
        self.assertEqual(set(rows), {5.0, 10.0, 20.0, 48.0})
        self.assertEqual(rows[10.0]["generic_alpha_sign_used"], "repulsive_alpha_less_than_zero")
        self.assertAlmostEqual(rows[10.0]["generic_alpha_95_anchor_approx"], 1.4e4)
        expected_phases = {
            5.0: 1.4505515828881093e-4,
            10.0: 4.511144105731006e-5,
            20.0: 6.791844962524036e-5,
            48.0: 1.680733668964917e-8,
        }
        for range_um, row in rows.items():
            self.assertEqual(row["B_minus_L_response_factor"], 0.25)
            self.assertTrue(math.isclose(
                row["canonical_phase_at_limit_rad"],
                expected_phases[range_um],
                rel_tol=1.0e-14,
            ))
            self.assertLess(row["canonical_phase_at_limit_rad"], 1.0e-3)
            self.assertLess(row["coupling_headroom_limit_over_threshold"], 1.0)

    def test_detector_scale_is_below_fitted_template_scale(self) -> None:
        scale = e038.levitated_detector_scale_check()
        self.assertTrue(math.isclose(scale["maximum_allowed_pattern_template_force_N"], 8.584e-20, rel_tol=1.0e-3))
        self.assertGreater(scale["published_fitted_template_scale_over_allowed_force"], 58.0)
        self.assertNotIn("instantaneous_sensitivity_over_allowed_force", scale)
        self.assertIn("N/sqrt(Hz)", scale["noise_density_comparison"])

    def test_modulated_source_waveform_and_reaction_are_explicit(self) -> None:
        source = e038.modulated_source_definition()
        self.assertTrue(math.isclose(source["peak_to_peak_translation_m"], 170.0e-6))
        self.assertTrue(math.isclose(source["amplitude_m"], 85.0e-6))
        self.assertEqual(source["frequency_Hz"], 3.0)
        self.assertIn("sinusoidal idealization", source["waveform_status"])
        self.assertIn("recorded", source["waveform_status"])
        self.assertTrue(math.isclose(
            source["maximum_velocity_m_per_s"],
            2.0 * math.pi * 3.0 * 85.0e-6,
            rel_tol=1.0e-14,
        ))
        self.assertTrue(math.isclose(
            source["maximum_acceleration_m_per_s2"],
            (2.0 * math.pi * 3.0) ** 2 * 85.0e-6,
            rel_tol=1.0e-14,
        ))
        self.assertTrue(math.isclose(
            source["generic_Yukawa_alpha1_lambda10um_template_force_N"],
            5.0e-24,
            rel_tol=1.0e-14,
        ))
        self.assertIsNone(source["ordinary_Newtonian_moving_pattern_background_N"])
        self.assertIsNone(source["moving_mass_kg"])

    def test_proposal_threshold_is_not_a_measured_voltage_floor(self) -> None:
        self.assertTrue(math.isclose(
            e038.equivalent_josephson_voltage(1.0e-3),
            5.485099637896729e-21,
            rel_tol=1.0e-14,
        ))

    def test_phase_formula_scales_quadratically_and_has_absolute_force(self) -> None:
        phase = e038.josephson_phase(1.0e-16, 10.0e-6)
        self.assertTrue(math.isclose(
            e038.josephson_phase(2.0e-16, 10.0e-6),
            4.0 * phase,
            rel_tol=1.0e-14,
        ))
        signal = e038.josephson_single_pair_energy_and_force(1.0e-15, 10.0e-6)
        self.assertGreater(signal["surface_energy_per_Cooper_pair_J"], 0.0)
        self.assertTrue(math.isclose(
            signal["surface_force_per_Cooper_pair_N"],
            signal["surface_energy_per_Cooper_pair_J"] / 10.0e-6,
            rel_tol=1.0e-14,
        ))

    def test_published_phase_benchmark_is_reproduced_after_convention_mapping(self) -> None:
        benchmark = e038.normalization_audit()["published_potential_normalized_benchmark"]
        self.assertTrue(math.isclose(benchmark["phase_rad"], 0.0028758640128923813, rel_tol=1.0e-12))
        self.assertTrue(math.isclose(benchmark["phase_rad_at_0p1_um"], 0.0030100681863688946, rel_tol=1.0e-12))

    def test_long_range_microscope_limit_is_not_extended_to_micron_rows(self) -> None:
        for row in e038.optomechanical_josephson_rows():
            self.assertFalse(row["microscope_long_range_bound_applicable"])

    def test_survival_rule_fails_closed_on_signal_and_unqualified_confounders(self) -> None:
        result = e038.survival_rule_evaluation()
        self.assertEqual(result["qualifying_adjacent_range_pairs_um"], [])
        self.assertIsNone(result["background_reference_phase_rad"])
        self.assertFalse(
            result["all_josephson_confounders_have_measured_phase_bounds"]
        )
        self.assertFalse(
            result[
                "all_josephson_confounders_below_one_fifth_allowed_phase"
            ]
        )
        self.assertFalse(result["josephson_channel_survived"])
        self.assertFalse(result["levitated_allowed_force_reaches_reference"])
        self.assertFalse(
            result[
                "all_force_confounders_have_qualified_same_template_bounds"
            ]
        )
        self.assertFalse(result["levitated_channel_survived"])
        self.assertFalse(result["survived"])
        self.assertEqual(result["disposition"], "park_fail_closed")

    def test_portfolio_is_diverse_and_only_bl_is_deepened(self) -> None:
        candidates = e038.portfolio_refresh()
        self.assertEqual(len(candidates), 5)
        self.assertEqual(len({candidate["category"] for candidate in candidates}), 5)
        selected = [
            candidate["id"]
            for candidate in candidates
            if candidate["disposition"] == "deepened_then_parked_in_e038"
        ]
        self.assertEqual(selected, ["P-003"])
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

    def test_decision_does_not_promote_proposal_threshold_to_measured_noise(self) -> None:
        report = e038.run_analysis()
        self.assertEqual(
            report["decision"]["status"],
            "parked_scale_and_measured_background_gate_failed",
        )
        self.assertIn("P-008", report["decision"]["next_best_step"])
        self.assertIn(
            "No candidate supports practical artificial gravity",
            report["portfolio"]["screen_result"],
        )
        self.assertEqual(report["resource_accounting"]["pde_solves"], 0)
        self.assertEqual(report["resource_accounting"]["pde_builds"], 0)
        self.assertEqual(report["resource_accounting"]["hardware_actions"], 0)
        self.assertEqual(report["resource_accounting"]["checkpoint_reads_or_writes"], 0)

    def test_cli_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "e038.json"
            exit_code = e038.main(["--report-json", str(path)])
            report = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(report["portfolio"]["selected_for_deepening"], "P-003")
        self.assertEqual(report["provenance"]["campaign"], "E-038")


if __name__ == "__main__":
    unittest.main()

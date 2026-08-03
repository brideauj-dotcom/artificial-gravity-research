import json
import math
from pathlib import Path
import tempfile
import unittest

import models.e037_portfolio_funnel as e037


class E037PortfolioFunnelTests(unittest.TestCase):
    def test_portfolio_is_genuinely_categorized_and_deepens_one_candidate(self) -> None:
        candidates = e037.portfolio_candidates()
        self.assertEqual(len(candidates), 7)
        self.assertEqual(len({candidate["category"] for candidate in candidates}), 6)
        selected = [
            candidate
            for candidate in candidates
            if candidate["disposition"] == "deepened_in_e037_as_small_sample_analog"
        ]
        self.assertEqual([candidate["id"] for candidate in selected], ["P-001"])
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

    def test_water_full_cancellation_requires_about_1354_tesla_squared_per_meter(self) -> None:
        product = e037.magnetic_gradient_product_for_acceleration(
            e037.STANDARD_GRAVITY
        )
        self.assertAlmostEqual(product, 1354.207439076045)
        self.assertAlmostEqual(product / 16.0, 84.63796494225281)

    def test_terrestrial_partial_g_and_free_space_body_force_are_not_confused(self) -> None:
        rows = {row["case"]: row for row in e037.diamagnetic_scale_table()}
        near_zero = rows["terrestrial 0.01g residual"]
        free_space = rows["free-space 0.01g magnetic body force"]
        self.assertAlmostEqual(
            near_zero["required_abs_B_dB_dz_T2_per_m"],
            1340.6653646852844,
        )
        self.assertAlmostEqual(
            free_space["required_abs_B_dB_dz_T2_per_m"],
            13.54207439076045,
        )
        self.assertAlmostEqual(
            near_zero["required_abs_B_dB_dz_T2_per_m"]
            / free_space["required_abs_B_dB_dz_T2_per_m"],
            99.0,
        )

    def test_one_percent_specific_susceptibility_mismatch_leaves_point_zero_one_g(self) -> None:
        ledger = e037.susceptibility_mismatch_ledger()
        row = next(
            item
            for item in ledger["rows"]
            if item["case"] == "full_cancellation"
            and item["specific_susceptibility_fractional_mismatch"] == 0.01
        )
        self.assertEqual(row["absolute_residual_error_fraction_g"], 0.01)
        self.assertAlmostEqual(
            row["absolute_residual_error_m_s2"],
            0.01 * e037.STANDARD_GRAVITY,
        )
        self.assertIn("1-percent", ledger["decisive_bound"])

    def test_local_field_energy_is_reported_without_claiming_system_energy(self) -> None:
        report = e037.run_analysis()
        self.assertAlmostEqual(
            report["resource_scale"]["local_magnetic_energy_density_at_16T_J_m3"],
            101_859_163.57881302,
        )
        self.assertIn("not total stored magnet energy", report["resource_scale"]["meaning"])

    def test_adjacent_absolute_scales_park_lab_gravity_waves(self) -> None:
        checks = e037.adjacent_scale_checks()
        sail = checks["ideal_ACS3_scale_solar_sail"]
        wave = checks["optimistic_1GJ_1kHz_gravity_bounds"]
        self.assertAlmostEqual(sail["acceleration_m_s2"], 4.539806275871592e-05)
        self.assertAlmostEqual(wave["wave_zone_distance_m"], 299_792.458)
        self.assertLess(wave["near_zone_acceleration_scale_m_s2"], 8.0e-19)
        self.assertLess(wave["wave_zone_strain_scale"], 2.0e-40)
        self.assertLess(
            wave["relative_acceleration_over_1m_baseline_m_s2"],
            3.0e-33,
        )

    def test_falsification_design_preserves_nonuniversal_interpretation(self) -> None:
        design = e037.falsification_design()
        self.assertGreaterEqual(len(design["predeclared_physics_gates"]), 4)
        self.assertGreaterEqual(len(design["kill_conditions"]), 4)
        self.assertIn("never real curvature", design["interpretation_if_passed"])
        self.assertIn("reaction", design["source_and_reaction_measurement"])

    def test_analysis_says_no_practical_artificial_gravity_candidate(self) -> None:
        report = e037.run_analysis()
        self.assertEqual(report["portfolio"]["selected_for_deepening"], "P-001")
        self.assertIn("No candidate supports practical artificial gravity", report["portfolio"]["screen_result"])
        self.assertEqual(
            report["decision"]["status"],
            "small_sample_analog_survives_no_real_gravity_candidate",
        )
        self.assertEqual(report["resource_accounting"]["pde_solves"], 0)
        self.assertEqual(report["resource_accounting"]["hardware_actions"], 0)

    def test_cli_writes_portfolio_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "e037.json"
            exit_code = e037.main(["--report-json", str(path)])
            report = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(report["portfolio"]["candidate_count"], 7)
        self.assertEqual(report["decision"]["selected_candidate"], "P-001")


if __name__ == "__main__":
    unittest.main()

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import models.e035_coupled_grid_preregistration as e035


class E035CoupledGridPreregistrationTests(unittest.TestCase):
    def test_exact_unknown_counts_match_strict_quarter_disk(self) -> None:
        self.assertEqual(
            [
                e035.exact_quarter_disk_unknowns(e035.RADIAL_MAX, spacing)
                for spacing, _ in e035.GRID_SPECIFICATIONS
                + (e035.FOURTH_GRID_SPECIFICATION,)
            ],
            [322_319, 1_288_052, 5_149_725, 20_593_789],
        )

    def test_new_positive_support_policy_distinguishes_e034_proxy(self) -> None:
        geometry = e035.coupled_grid_geometry()
        rows = geometry["candidate_grids"]
        self.assertEqual(
            [row["nominal_inner_radius_transition_cells"] for row in rows],
            [6.4, 12.8, 25.6],
        )
        self.assertEqual(
            [
                row["positive_support_transition_cells_infimum"]
                for row in rows
            ],
            [4.0, 8.0, 16.0],
        )
        self.assertFalse(geometry["source_transition_audit"]["passed"])
        audit = geometry["source_transition_audit"]
        self.assertIn("positive support", audit["comparison_to_e034_half_height_proxy"])
        self.assertIn("new E-035", audit["criterion_status"])

    def test_coupled_directional_path_is_not_geometric_order_family(self) -> None:
        geometry = e035.coupled_grid_geometry()
        self.assertTrue(geometry["coupled_monotonicity_passed"])
        self.assertFalse(geometry["single_parameter_geometrically_similar_family"])
        ratios = geometry["directional_resolution_ratios"]
        self.assertGreater(ratios[0], ratios[1])
        self.assertTrue(all(1.0 < ratio < 1.3 for ratio in ratios))
        self.assertIn("contraction index", geometry["rate_interpretation"])
        self.assertIn("not a pure spatial order", geometry["rate_interpretation"])

    def test_common_points_map_by_exact_integer_restriction(self) -> None:
        preregistration = e035.common_node_preregistration()
        self.assertEqual(
            [row["coarsest_index_multiplier"] for row in preregistration["grid_maps"]],
            [1, 2, 4],
        )
        self.assertEqual(
            preregistration["grid_maps"][0]["indices"],
            [[70, 6], [46, 4], [48, 4], [50, 4]],
        )
        self.assertEqual(
            preregistration["grid_maps"][2]["indices"],
            [[280, 24], [184, 16], [192, 16], [200, 16]],
        )
        self.assertIn("No interpolation", preregistration["restriction_policy"])

    def test_resource_envelope_blocks_finest_and_fourth_grids(self) -> None:
        resources = e035.resource_feasibility()
        candidates = resources["candidate_grids"]
        self.assertEqual(
            [row["status"] for row in candidates],
            [
                "one_campaign_core_within_caps_full_screen_unbudgeted",
                "one_campaign_core_within_caps_full_screen_unbudgeted",
                "blocked_by_conservative_peak_envelope",
            ],
        )
        self.assertFalse(resources["complete_candidate_sequence_feasible"])
        self.assertFalse(resources["fourth_grid_feasible"])
        self.assertIn("one-standard-campaign core", resources["method"])
        self.assertIn(
            "tolerances are not frozen",
            resources["complete_candidate_sequence_feasibility_status"],
        )
        self.assertEqual(
            resources["caps"]["effective_hard_cap_after_reserve_bytes"],
            e035.HARD_RSS_CAP_BYTES,
        )
        self.assertGreater(
            resources["fourth_grid"]["calibrated_static_bytes"],
            64 * e035.GIB,
        )
        self.assertGreater(
            candidates[-1]["projected_full_peak_upper_bytes"],
            e035.HARD_RSS_CAP_BYTES,
        )

    def test_runtime_projection_exceeds_one_nightly_window_at_h_1_over_32(self) -> None:
        finest = e035.resource_feasibility()["candidate_grids"][-1]
        self.assertGreater(
            finest["projected_one_standard_campaign_core_seconds_lower"],
            e035.NIGHTLY_GRID_WALL_CAP_SECONDS,
        )
        self.assertGreater(
            finest["projected_one_standard_campaign_core_seconds_upper"],
            finest["projected_one_standard_campaign_core_seconds_lower"],
        )

    def test_protocol_prohibits_gci_and_strengthens_solver_separation(self) -> None:
        protocol = e035.derivative_protocol()
        screen = protocol["coupled_path_screen"]
        self.assertEqual(screen["name"], "effective coupled-path contraction index")
        self.assertIn("Grid Convergence Index", screen["prohibited_interpretations"])
        separation = protocol["solver_discretization_separation"]
        self.assertEqual(separation["one_percent_threshold"], 0.01)
        self.assertIn("does not operationalize", separation["literature_context"])
        self.assertIn("not frozen", separation["tolerance_schedule_status"])
        self.assertEqual(
            protocol["design_status"],
            "incomplete_prospective_design_not_executable",
        )

    def test_analysis_is_successful_but_screen_is_blocked(self) -> None:
        report = e035.run_analysis()
        self.assertTrue(report["decision"]["analysis_completed"])
        self.assertFalse(report["decision"]["screen_authorized"])
        self.assertEqual(
            report["decision"]["status"], "blocked_before_nonlinear_solve"
        )
        self.assertIn(
            "new_full_positive_support_six_cell_policy",
            report["decision"]["failed_gates"],
        )
        self.assertNotIn(
            "single_parameter_geometric_refinement_gate",
            report["decision"]["failed_gates"],
        )
        self.assertIn(
            "future_derivative_protocol_not_executable",
            report["decision"]["failed_gates"],
        )
        self.assertEqual(report["resource_accounting"]["pde_solves"], 0)

    def test_analysis_never_builds_or_solves_a_pde(self) -> None:
        with mock.patch.object(e035.e025, "build_system") as build, mock.patch.object(
            e035.e025, "solve_continuation"
        ) as solve, mock.patch.object(e035.np, "load") as load:
            report = e035.run_analysis()
        build.assert_not_called()
        solve.assert_not_called()
        load.assert_not_called()
        self.assertFalse(report["decision"]["screen_authorized"])

    def test_cli_writes_blocked_report_without_treating_it_as_tool_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "e035.json"
            exit_code = e035.main(["--report-json", str(path)])
            report = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(
            report["decision"]["status"], "blocked_before_nonlinear_solve"
        )
        self.assertEqual(report["resource_accounting"]["checkpoint_reads"], 0)


if __name__ == "__main__":
    unittest.main()

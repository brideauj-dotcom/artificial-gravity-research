import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import numpy as np

import models.e036_actual_solution_enclosure as e036


class E036ActualSolutionEnclosureTests(unittest.TestCase):
    def test_masks_are_fully_enumerated_with_frozen_digests(self) -> None:
        report = e036.enumerate_common_masks()
        self.assertEqual(report["strict_quarter_disk_node_count"], 322_319)
        self.assertEqual(report["restriction_multipliers"], [1, 2, 4])
        self.assertEqual(
            {
                name: row["count"]
                for name, row in report["masks"].items()
            },
            {
                "full_positive_source_support": 3_513,
                "radial_transition": 1_503,
                "angular_transition": 3_290,
                "inner_feature_rectangle": 2_145,
                "global_interior": 307_852,
            },
        )
        self.assertEqual(
            report["masks"]["global_interior"][
                "sha256_le_u32_index_pairs"
            ],
            "35e2e1dad2fd9c444fa08e5fc76bb388274c473bd7bb393d8b0737a3ef3818be",
        )

    def test_every_mask_has_valid_support_on_every_candidate_grid(self) -> None:
        masks = e036.enumerate_common_masks()["masks"]
        self.assertTrue(
            all(row["all_native_recovery_supports_valid"] for row in masks.values())
        )
        self.assertTrue(
            all(
                count == 0
                for row in masks.values()
                for count in row["invalid_supports"].values()
            )
        )
        self.assertAlmostEqual(
            masks["global_interior"]["minimum_curved_boundary_clearance"][
                "h=0.125,m=4"
            ],
            1.1478836682235851,
        )

    def test_recovery_rows_reproduce_a_general_quadratic(self) -> None:
        report = e036.executable_recovery_definitions()
        self.assertTrue(report["quadratic_reproduction_passed"])
        self.assertLess(report["quadratic_reproduction_linf_max"], 2.0e-11)
        self.assertTrue(report["scale_covariance_passed"])
        self.assertEqual(len(report["rows"]), 9)
        self.assertTrue(report["reflected_axis_validation_passed"])
        self.assertEqual(
            len(report["reflected_axis_validation"]["rows"]),
            18,
        )

    def test_reflected_rows_coalesce_and_apply_at_axis_and_first_node(self) -> None:
        report = e036.reflected_axis_recovery_validation()
        self.assertTrue(report["passed"])
        self.assertLess(report["maximum_abs_error"], 2.0e-11)
        self.assertEqual(
            {row["axial_index"] for row in report["rows"]},
            {0, 1},
        )
        self.assertTrue(
            all(
                row["expected_components"][1] != 0.0
                or row["mixed_rho_z2_control_expected"] != 0.0
                for row in report["rows"]
                if row["axial_index"] == 1
            )
        )

    def test_q2h_row_norm_exposes_h_inverse_square_amplification(self) -> None:
        rows = [
            row
            for row in e036.executable_recovery_definitions()["rows"]
            if row["recovery"] == "Q_2h"
        ]
        radial_norms = [row["row_l1_norms"][0] for row in rows]
        np.testing.assert_allclose(
            radial_norms,
            [73.14285714285715, 292.5714285714286, 1170.2857142857144],
            rtol=0.0,
            atol=2.0e-12,
        )

    def test_solver_schedule_is_exact_but_dormant(self) -> None:
        protocol = e036.frozen_validation_protocol()
        self.assertEqual(
            protocol["design_status"],
            "fully_frozen_with_executable_gates_not_authorized",
        )
        schedule = protocol["solver_schedule"]
        self.assertEqual(
            [
                schedule[name]["nonlinear_relative_l2"]
                for name in ("standard", "tight_1", "tight_2")
            ],
            [1.0e-7, 1.0e-8, 1.0e-9],
        )
        self.assertEqual(schedule["shared"]["gmres_total_inner_cap"], 2000)
        self.assertEqual(schedule["shared"]["target_amplitude"], 0.5)
        self.assertEqual(schedule["shared"]["line_search_max_dyadic_halvings"], 24)
        self.assertIn("independently runs all six targets", schedule["shared"]["initialization"])
        self.assertEqual(protocol["runtime_budget"]["projected_campaign_cores"], 9)
        self.assertAlmostEqual(
            protocol["runtime_budget"]["projected_core_hours_low_estimate"],
            4.062973399216329,
        )
        self.assertAlmostEqual(
            protocol["runtime_budget"]["projected_core_hours_high_estimate"],
            5.900419732347402,
        )
        self.assertIn(
            "not a demonstrated lower bound",
            protocol["runtime_budget"]["excluded_work"],
        )

    def test_orientation_and_eigengap_require_verified_error_bounds(self) -> None:
        protocol = e036.frozen_validation_protocol()
        self.assertIn("zero is excluded", protocol["orientation"]["gate"])
        self.assertIn(
            "twice the verified spectral-norm matrix-error radius",
            protocol["eigengap"]["gate"],
        )
        self.assertTrue(protocol["evaluator_self_tests"]["all_passed"])

    def test_executable_interval_separation_and_eigengap_gates_reject_controls(self) -> None:
        self.assertTrue(
            e036.solver_separation_gate(10.0, (0.02, 0.02), (0.01, 0.01))["passed"]
        )
        self.assertFalse(
            e036.solver_separation_gate(1.0, (0.02, 0.02), (0.01, 0.01))["passed"]
        )
        self.assertTrue(
            e036.orientation_interval_gate(
                (1.0, 0.5),
                (0.05, 0.05, 0.05),
                (10.0, 20.0, 40.0),
                (2.0, 2.0, 2.0),
                component="radial",
                axial_index=6,
            )["passed"]
        )
        self.assertFalse(
            e036.orientation_interval_gate(
                (1.0, -0.5),
                (0.05, 0.05, 0.05),
                (10.0, 20.0, 40.0),
                (2.0, 2.0, 2.0),
                component="radial",
                axial_index=6,
            )["passed"]
        )
        self.assertTrue(
            e036.eigengap_gate(np.asarray((1.0,)), np.asarray((0.1,)))["passed"]
        )
        self.assertFalse(
            e036.eigengap_gate(np.asarray((0.2,)), np.asarray((0.1,)))["passed"]
        )

    def test_exact_row_action_equivalence_is_bitwise(self) -> None:
        fixture = e036._equivalence_self_test_fixture()
        snapshot = e036._derive_tiny_equivalence_snapshot(fixture)
        self.assertTrue(
            e036._tiny_row_action_equivalence(fixture, fixture)["passed"]
        )
        self.assertEqual(
            snapshot["operator_snapshot"]["manifest"]["system_sha256"],
            e036._tiny_equivalence_expected_lineage(fixture)["system_sha256"],
        )
        self.assertEqual(
            snapshot["operator_snapshot"]["row_actions"]["zero"]["shape"],
            [25, 4],
        )
        self.assertEqual(
            snapshot["nonlinear_snapshot"]["active_jacobian_actions"]["shape"],
            [65, 4],
        )
        self.assertEqual(
            snapshot["nonlinear_snapshot"]["exact_tie_masks"]["shape"],
            [12, 4],
        )
        self.assertEqual(
            sum(name.startswith("tie_selection_") for name in snapshot["nonlinear_snapshot"]),
            16,
        )
        signed_zero_source = fixture["target_source"].copy()
        signed_zero_source[-1] = 0.0
        signed_zero = {**fixture, "target_source": signed_zero_source}
        self.assertFalse(
            e036._tiny_row_action_equivalence(fixture, signed_zero)["passed"]
        )

        changed_data = fixture["system"]["operators"][
            e036.CANONICAL_OPERATOR_NAMES[0]
        ]["data"].copy()
        changed_data[0] += 1.0
        changed_first = {
            **fixture["system"]["operators"][e036.CANONICAL_OPERATOR_NAMES[0]],
            "data": changed_data,
        }
        changed_operators = dict(fixture["system"]["operators"])
        changed_operators[e036.CANONICAL_OPERATOR_NAMES[0]] = changed_first
        changed_candidate = {
            **fixture,
            "system": {**fixture["system"], "operators": changed_operators},
        }
        self.assertFalse(
            e036._tiny_row_action_equivalence(
                fixture,
                changed_candidate,
            )["passed"]
        )

    def test_equivalence_inventory_matches_retained_e025_operator_order(self) -> None:
        self.assertEqual(len(e036.CANONICAL_OPERATOR_NAMES), 25)
        self.assertNotIn("linear_laplacian", e036.CANONICAL_OPERATOR_NAMES)
        self.assertEqual(e036.CANONICAL_OPERATOR_NAMES[-1], "azimuthal_24")
        self.assertEqual(
            len(e036.CANONICAL_OPERATOR_NAMES[:-1]),
            2 * len(e036.BASELINE_DIRECTIONAL_BASES),
        )

    def test_equivalence_executor_rejects_noncanonical_csr_and_lineage(self) -> None:
        fixture = e036._equivalence_self_test_fixture()
        first_name = e036.CANONICAL_OPERATOR_NAMES[0]
        first = fixture["system"]["operators"][first_name]
        invalid_indptr = first["indptr"].copy()
        invalid_indptr[-1] -= 1
        invalid_first = {**first, "indptr": invalid_indptr}
        invalid_operators = dict(fixture["system"]["operators"])
        invalid_operators[first_name] = invalid_first
        with self.assertRaises(ValueError):
            e036._derive_tiny_equivalence_snapshot(
                {
                    **fixture,
                    "system": {
                        **fixture["system"],
                        "operators": invalid_operators,
                    },
                }
            )

        unsorted_first = {
            "indptr": np.asarray((0, 2, 3, 4, 5), dtype=np.int64),
            "indices": np.asarray((1, 0, 1, 2, 3), dtype=np.int64),
            "data": np.ones(5, dtype=np.float64),
        }
        unsorted_operators = dict(fixture["system"]["operators"])
        unsorted_operators[first_name] = unsorted_first
        with self.assertRaisesRegex(ValueError, "sorted and coalesced"):
            e036._derive_tiny_equivalence_snapshot(
                {
                    **fixture,
                    "system": {
                        **fixture["system"],
                        "operators": unsorted_operators,
                    },
                }
            )

        wrong_lineage = e036._tiny_equivalence_expected_lineage(fixture)
        wrong_lineage["system_sha256"] = "a" * 64
        with self.assertRaisesRegex(ValueError, "system_sha256"):
            e036._derive_tiny_equivalence_snapshot(
                fixture,
                expected_lineage=wrong_lineage,
            )

        with self.assertRaisesRegex(ValueError, "immutable accepted"):
            e036.derive_stage6_equivalence_snapshot(fixture)

    def test_equivalence_vector_generator_is_frozen_and_reproducible(self) -> None:
        radial = np.asarray((2, 3, 4, 5), dtype=np.int64)
        axial = np.asarray((0, 1, 2, 3), dtype=np.int64)
        first = e036.required_equivalence_vectors(radial, axial)
        second = e036.required_equivalence_vectors(radial, axial)
        self.assertEqual(tuple(first), e036.REQUIRED_ROW_ACTION_NAMES)
        self.assertEqual(len(first), 65)
        for name in first:
            self.assertEqual(first[name].tobytes(), second[name].tobytes())

    def test_coupled_path_and_operator_spread_gate_is_exhaustive(self) -> None:
        base = np.asarray(
            ((1.0, 0.5, -1.0, 0.25), (0.5, -0.25, 0.75, -0.5))
        )
        recovered = np.asarray(
            [
                [grid * recovery * base for recovery in (1.0, 0.8, 0.6)]
                for grid in (4.0, 2.0, 1.0)
            ]
        )
        one_mask = e036.coupled_path_metrics(recovered, np.asarray((1.0, 2.0)))
        metrics = {mask: one_mask for mask in e036.MASK_NAMES}
        orientations = {key: True for key in e036.FIXED_ORIENTATION_KEYS}
        self.assertTrue(
            e036.coupled_path_screen_gate(
                metrics,
                orientations,
                solution_schedule="tight_2",
                verified_root_error_enclosure=True,
            )["screen_authorized"]
        )
        self.assertFalse(
            e036.coupled_path_screen_gate(
                metrics,
                orientations,
                solution_schedule="tight_2",
                verified_root_error_enclosure=False,
            )["screen_authorized"]
        )
        with self.assertRaises(ValueError):
            e036.coupled_path_screen_gate(
                {mask: one_mask for mask in e036.MASK_NAMES[:-1]},
                orientations,
                solution_schedule="tight_2",
                verified_root_error_enclosure=True,
            )

    def test_transfer_band_is_constructed_from_frozen_e034_cutoff(self) -> None:
        outside, cutoff = e036.frozen_outside_origin_band(
            (32, 32),
            spacing=0.125,
            recovery="Q_2h",
            component="mixed",
        )
        self.assertEqual(outside.shape, (32, 32))
        self.assertGreater(np.count_nonzero(outside), 0)
        self.assertEqual(
            cutoff,
            e036.frozen_transfer_cutoffs()["Q_2h:mixed"],
        )
        with self.assertRaises(ValueError):
            e036.transfer_parity_metrics(
                np.ones((32, 32)),
                np.ones((32, 32)),
                spacing=0.125,
                recovery="C_h",
                component="azimuthal",
                detrend="affine",
            )

    def test_transfer_tile_uses_even_and_mixed_odd_axis_reflection(self) -> None:
        radial = np.arange(80, dtype=float)[:, None]
        axial = np.arange(40, dtype=float)[None, :]
        field = radial + 10.0 * axial
        even_tile, weights = e036.transfer_tile(
            field,
            (30, 1),
            0.125,
            "radial",
        )
        mixed_tile, _ = e036.transfer_tile(
            field,
            (30, 1),
            0.125,
            "mixed",
        )
        self.assertEqual(even_tile.shape, (32, 32))
        self.assertTrue(np.all(weights > 0.0))
        zero_column = 15
        self.assertTrue(np.all(mixed_tile[:, zero_column] == 0.0))
        self.assertTrue(
            np.allclose(
                mixed_tile[:, zero_column - 1],
                -even_tile[:, zero_column - 1],
            )
        )
        metrics = e036.transfer_parity_metrics(
            even_tile,
            weights,
            spacing=0.125,
            recovery="C_h",
            component="radial",
            detrend="affine",
        )
        self.assertLess(metrics["parseval_relative_error"], 1.0e-12)

    def test_between_node_counterexample_keeps_nonzero_hessian(self) -> None:
        report = e036.nodal_between_node_counterexample()
        self.assertEqual(report["family"], "e_h(x)=h^2*sin(2*pi*x/h)")
        for row in report["rows"]:
            self.assertEqual(
                row["second_derivative_linf"], 4.0 * math.pi**2
            )
        self.assertGreater(
            report["rows"][0]["potential_linf"],
            report["rows"][-1]["potential_linf"],
        )

    def test_actual_solution_enclosure_is_rejected_not_overclaimed(self) -> None:
        audit = e036.actual_solution_enclosure_audit()
        self.assertFalse(audit["all_required_terms_certified"])
        self.assertEqual(
            audit["decision"],
            "no_rigorous_actual_solution_derivative_enclosure_available",
        )
        self.assertIn("not a theorem", audit["interpretation"])
        statuses = {item["term"]: item["status"] for item in audit["obligations"]}
        self.assertEqual(
            statuses["recovery_operator"],
            "completed_but_implementation_only",
        )
        self.assertEqual(statuses["between_node_hessian"], "missing_nodal_counterexample_remains")

    def test_analysis_parks_line_without_build_load_or_solve(self) -> None:
        with mock.patch.object(e036.e035.e025, "build_system") as build, mock.patch.object(
            e036.e035.e025, "solve_continuation"
        ) as solve, mock.patch.object(e036.np, "load") as load:
            report = e036.run_analysis()
        build.assert_not_called()
        solve.assert_not_called()
        load.assert_not_called()
        self.assertEqual(
            report["decision"]["status"],
            "parked_no_validated_actual_solution_enclosure",
        )
        self.assertTrue(
            report["decision"]["mathematical_gate_definitions_complete"]
        )
        self.assertFalse(
            report["decision"]["full_baseline_equivalence_executed"]
        )
        self.assertFalse(report["decision"]["screen_authorized"])
        self.assertFalse(report["decision"]["enclosure_available"])
        self.assertEqual(report["resource_accounting"]["pde_solves"], 0)
        self.assertFalse(report["accepted_lineage"]["changed"])

    def test_cli_serializes_negative_closure_as_completed_research(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "e036.json"
            exit_code = e036.main(["--report-json", str(path)])
            report = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(
            report["decision"]["status"],
            "parked_no_validated_actual_solution_enclosure",
        )
        self.assertEqual(report["resource_accounting"]["checkpoint_reads"], 0)


if __name__ == "__main__":
    unittest.main()

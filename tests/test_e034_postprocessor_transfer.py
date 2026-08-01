import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np

import models.e034_postprocessor_transfer as e034


class E034PostprocessorTransferTests(unittest.TestCase):
    def test_strategy_is_checkpoint_free_and_frozen(self) -> None:
        provenance = e034.implementation_provenance()
        strategy = provenance["strategy"]
        self.assertEqual(provenance["campaign"], "E-034")
        self.assertEqual(strategy["grid_spacing"], 0.25)
        self.assertEqual(
            strategy["postprocessors"],
            ["centered_0p25", "centered_0p5", "quadratic_5x5"],
        )
        self.assertIn("No checkpoint", strategy["lineage_policy"])
        self.assertEqual(strategy["mode_bank_sizes"], {
            "lower_band": 17,
            "grid_scale": 17,
        })
        for values in provenance["modules"].values():
            self.assertFalse(Path(values["path"]).is_absolute())

    def test_centered_symbols_match_direct_frozen_weights(self) -> None:
        weights = e034._component_weights(e034.REFERENCE_RHO)
        for theta_rho, theta_z in (
            (0.13, -0.29),
            (0.47 * math.pi, 0.32 * math.pi),
            (-0.91 * math.pi, 0.72 * math.pi),
        ):
            for name, stride in (("centered_0p25", 1), ("centered_0p5", 2)):
                direct = e034._symbols_from_weights(
                    weights[name],
                    theta_rho,
                    theta_z,
                )
                analytic = e034.centered_symbols(
                    theta_rho,
                    theta_z,
                    stride=stride,
                )
                np.testing.assert_allclose(
                    analytic,
                    direct,
                    rtol=0.0,
                    atol=e034.SYMBOL_ABSOLUTE_TOLERANCE,
                )

    def test_quadratic_weights_have_closed_integer_form(self) -> None:
        weights = e034._component_weights(e034.REFERENCE_RHO)[
            "quadratic_5x5"
        ]
        offsets = np.arange(-2, 3, dtype=float)
        radial, axial = np.meshgrid(offsets, offsets, indexing="ij")
        h = e034.GRID_SPACING
        expected = np.stack(
            (
                (radial**2 - 2.0) / (35.0 * h**2),
                radial * axial / (100.0 * h**2),
                (axial**2 - 2.0) / (35.0 * h**2),
                radial / (50.0 * h * e034.REFERENCE_RHO),
            )
        )
        np.testing.assert_allclose(weights, expected, rtol=0.0, atol=2.0e-14)

    def test_quadratic_symbols_match_weight_transform(self) -> None:
        weights = e034._component_weights(e034.REFERENCE_RHO)[
            "quadratic_5x5"
        ]
        for theta_rho, theta_z in (
            (0.09 * math.pi, -0.18 * math.pi),
            (0.57 * math.pi, 0.39 * math.pi),
            (math.pi, -math.pi),
        ):
            direct = e034._symbols_from_weights(
                weights,
                theta_rho,
                theta_z,
            )
            analytic = e034.quadratic_symbols(theta_rho, theta_z)
            np.testing.assert_allclose(
                analytic,
                direct,
                rtol=0.0,
                atol=e034.SYMBOL_ABSOLUTE_TOLERANCE,
            )

    def test_all_postprocessors_reach_the_continuum_at_long_wave(self) -> None:
        theta_rho = 1.0e-4
        theta_z = -0.7e-4
        continuum = e034.continuum_symbols(theta_rho, theta_z)
        for name in e034.POSTPROCESSOR_NAMES:
            discrete = e034._closed_symbols(
                name,
                theta_rho,
                theta_z,
                e034.REFERENCE_RHO,
            )
            np.testing.assert_allclose(
                discrete / continuum,
                np.ones(4),
                rtol=2.0e-8,
                atol=0.0,
            )

    def test_general_quadratic_is_reproduced_by_all_three_operators(self) -> None:
        errors = e034.exact_symbol_validation()[
            "general_degree_two_polynomial_maximum_component_errors"
        ]
        self.assertEqual(set(errors), set(e034.POSTPROCESSOR_NAMES))
        self.assertLess(max(errors.values()), 2.0e-13)

    def test_analytic_nulls_are_actual_symbol_nulls(self) -> None:
        alpha = math.acos(-3.0 / 4.0)
        beta = math.acos(-1.0 / 4.0)
        box = 2.0 * math.pi / 5.0
        self.assertLess(
            abs(e034.quadratic_symbols(alpha, 0.23)[0]),
            2.0e-14,
        )
        self.assertLess(
            abs(e034.quadratic_symbols(0.23, box)[0]),
            2.0e-14,
        )
        self.assertLess(
            abs(e034.quadratic_symbols(beta, 0.31)[1]),
            2.0e-14,
        )
        self.assertLess(
            abs(e034.quadratic_symbols(0.31, box)[3]),
            2.0e-14,
        )
        self.assertLess(
            abs(e034.centered_symbols(math.pi, 0.2, stride=2)[0]),
            2.0e-14,
        )

    def test_declared_high_band_sign_reversals_occur(self) -> None:
        low = 0.25 * math.pi
        middle = 0.60 * math.pi
        high = 0.90 * math.pi
        self.assertLess(
            e034.normalized_transfer(
                "centered_0p5", "mixed", low, high
            ),
            0.0,
        )
        self.assertLess(
            e034.normalized_transfer(
                "centered_0p5", "azimuthal", high, low
            ),
            0.0,
        )
        self.assertLess(
            e034.normalized_transfer(
                "quadratic_5x5", "radial", low, middle
            ),
            0.0,
        )
        self.assertLess(
            e034.normalized_transfer(
                "quadratic_5x5", "mixed", low, high
            ),
            0.0,
        )
        self.assertLess(
            e034.normalized_transfer(
                "quadratic_5x5", "radial", math.pi, 0.0
            ),
            0.0,
        )

    def test_resolution_cutoffs_hit_predeclared_gains(self) -> None:
        report = e034.resolution_map()
        self.assertEqual(len(report["rows"]), 12)
        for row in report["rows"]:
            ten = row["ten_percent_relative_amplitude"]
            half = row["half_amplitude"]
            self.assertAlmostEqual(ten["gain_at_cutoff"], 0.9, places=11)
            self.assertAlmostEqual(half["gain_at_cutoff"], 0.5, places=11)
            self.assertLess(ten["theta_cutoff"], half["theta_cutoff"])
            self.assertLessEqual(
                ten["sampled_monotonicity_violation"],
                2.0e-15,
            )
            self.assertLessEqual(
                half["sampled_monotonicity_violation"],
                2.0e-15,
            )
            self.assertAlmostEqual(
                ten["minimum_gain_on_201x201_square"],
                0.9,
                places=11,
            )
            self.assertAlmostEqual(
                half["minimum_gain_on_201x201_square"],
                0.5,
                places=11,
            )
            self.assertLessEqual(
                ten["minimum_vs_corner_absolute_error"],
                2.0e-12,
            )
            self.assertLessEqual(
                half["minimum_vs_corner_absolute_error"],
                2.0e-12,
            )

    def test_quadratic_transverse_filter_narrows_resolution(self) -> None:
        rows = {
            (row["postprocessor"], row["component"]): row
            for row in e034.resolution_map()["rows"]
        }
        quadratic = rows[("quadratic_5x5", "radial")][
            "ten_percent_relative_amplitude"
        ]["theta_cutoff_over_pi"]
        centered = rows[("centered_0p5", "radial")][
            "ten_percent_relative_amplitude"
        ]["theta_cutoff_over_pi"]
        self.assertLess(quadratic, centered)
        self.assertAlmostEqual(quadratic, 0.08771880195509017, places=12)

    def test_reciprocal_lattice_alias_is_sample_exact(self) -> None:
        alias = e034.exact_symbol_validation()["reciprocal_lattice_alias"]
        self.assertLess(
            alias["maximum_patch_sample_error"],
            e034.SYMBOL_ABSOLUTE_TOLERANCE,
        )
        self.assertGreater(alias["maximum_continuum_symbol_difference"], 100.0)

    def test_disjoint_mode_banks_reproduce_all_twelve_targets(self) -> None:
        result = e034.mode_mixture_nonuniqueness()
        self.assertTrue(result["passed"])
        self.assertLess(
            result["maximum_absolute_measurement_residual"],
            e034.MIXTURE_ABSOLUTE_TOLERANCE,
        )
        self.assertGreater(
            result["minimum_lower_vs_grid_patch_l2_separation"],
            0.25,
        )
        for comparison in result["comparisons"]:
            for label in ("lower_band_fit", "grid_scale_fit"):
                fit = comparison[label]
                self.assertEqual(fit["rank"], 12)
                self.assertEqual(fit["nullity"], 5)
                self.assertLess(
                    fit["maximum_absolute_measurement_residual"],
                    e034.MIXTURE_ABSOLUTE_TOLERANCE,
                )
            self.assertNotEqual(
                comparison["lower_band_fit"]["patch_sha256"],
                comparison["grid_scale_fit"]["patch_sha256"],
            )

    def test_three_grid_gate_couples_source_and_directional_refinement(self) -> None:
        gate = e034.preregistered_three_grid_gate()
        self.assertEqual(
            gate["status"],
            "predeclared_screen_pending_e035_resource_feasibility",
        )
        self.assertEqual(gate["minimum_grid_count"], 3)
        self.assertEqual(gate["refinement_ratio"], 2.0)
        self.assertTrue(gate["coupled_geometry_preflight_passed"])
        self.assertEqual(
            [
                (row["spacing"], row["directional_radius"])
                for row in gate["candidate_grids"]
            ],
            [(0.125, 4), (0.0625, 5), (0.03125, 6)],
        )
        self.assertEqual(
            [row["minimum_source_transition_cells"] for row in gate["candidate_grids"]],
            [6.4, 12.8, 25.6],
        )
        for key in (
            "h_over_directional_resolution",
            "maximum_wide_stencil_physical_reach",
        ):
            values = [row[key] for row in gate["candidate_grids"]]
            self.assertGreater(values[0], values[1])
            self.assertGreater(values[1], values[2])
        self.assertEqual(
            gate["fourth_grid_rate_check"]["spacing"],
            0.015625,
        )
        self.assertIn(
            "cannot be tested with three grids",
            gate["apparent_order_screen"]["fourth_grid_rule"],
        )
        self.assertIn(
            "norms erase sign",
            gate["apparent_order_screen"]["orientation_rule"],
        )
        self.assertIn("GCI alone", gate["stop_rules"][-1])

    def test_failed_gates_are_retained_in_report(self) -> None:
        failed_validation = {
            "passed": False,
            "preserved_evidence": "synthetic symbol drift",
        }
        failed_mixtures = {
            "passed": False,
            "preserved_evidence": "synthetic rank loss",
        }
        with mock.patch.object(
            e034,
            "exact_symbol_validation",
            return_value=failed_validation,
        ), mock.patch.object(
            e034,
            "mode_mixture_nonuniqueness",
            return_value=failed_mixtures,
        ):
            report = e034.run_analysis()
        self.assertFalse(report["decision"]["passed"])
        self.assertEqual(
            report["decision"]["failed_gates"],
            ["exact_symbol_validation", "manufactured_nonuniqueness"],
        )
        self.assertEqual(
            report["exact_symbol_validation"]["preserved_evidence"],
            "synthetic symbol drift",
        )
        self.assertEqual(
            report["mode_mixture_nonuniqueness"]["preserved_evidence"],
            "synthetic rank loss",
        )

    def test_analysis_never_calls_pde_or_checkpoint_entry_points(self) -> None:
        with mock.patch.object(
            e034.e033,
            "run_campaign",
            side_effect=AssertionError("E-033 campaign must not run"),
        ), mock.patch.object(
            e034.e033.e029,
            "_validate_accepted_stage6",
            side_effect=AssertionError("checkpoint must not load"),
        ):
            report = e034.run_analysis()
        self.assertTrue(report["decision"]["passed"])

    def test_cli_serializes_failed_gate_before_nonzero_exit(self) -> None:
        validation = e034.exact_symbol_validation()
        validation["passed"] = False
        validation["preserved_evidence"] = "synthetic CLI drift"
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "failed-e034.json"
            with mock.patch.object(
                e034,
                "exact_symbol_validation",
                return_value=validation,
            ), mock.patch.object(
                sys,
                "argv",
                ["e034", "--report-json", str(report_path)],
            ):
                with self.assertRaisesRegex(SystemExit, "1"):
                    e034.main()
            payload = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertFalse(payload["decision"]["passed"])
        self.assertEqual(
            payload["decision"]["failed_gates"],
            ["exact_symbol_validation"],
        )
        self.assertEqual(
            payload["exact_symbol_validation"]["preserved_evidence"],
            "synthetic CLI drift",
        )

    def test_complete_analysis_retains_nonphysical_decision(self) -> None:
        report = e034.run_analysis()
        self.assertEqual(
            report["decision"]["status"],
            "qualified_nonidentifying_transfer_functions",
        )
        self.assertIn("not a continuum", report["epistemic_status"])
        self.assertTrue(report["exact_symbol_validation"]["passed"])
        self.assertTrue(report["mode_mixture_nonuniqueness"]["passed"])
        self.assertEqual(report["runtime_provenance"]["numpy_version"], np.__version__)
        self.assertTrue(
            any("No checkpoint" in limitation for limitation in report["limitations"])
        )


if __name__ == "__main__":
    unittest.main()

from pathlib import Path
import unittest
from unittest import mock

import numpy as np

import models.e025_axisymmetric_wide_2hessian as e025
import models.e031_common_space_persistence as e031
from models.e025_axisymmetric_wide_2hessian import AxisymmetricGrid
from models.e026_nonsymmetric_amg import AmgConfiguration


class E031CommonSpacePersistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fine = e025.build_system(AxisymmetricGrid(8.0, 0.5, 2))
        cls.coarse = e025.build_system(AxisymmetricGrid(8.0, 1.0, 1))

    def test_strategy_is_bounded_and_never_advances_lineage(self) -> None:
        provenance = e031.implementation_provenance()
        strategy = provenance["strategy"]
        self.assertEqual(
            strategy["verification_amplitudes"],
            [49.0 / 96.0, 25.0 / 48.0],
        )
        self.assertEqual(strategy["accepted_baseline_amplitude"], 0.5)
        self.assertIn("strictly greater", strategy["stability_screen"])
        self.assertIn("immutable", strategy["lineage_policy"])
        for values in provenance["modules"].values():
            self.assertFalse(Path(values["path"]).is_absolute())

    def test_exact_two_to_one_common_node_map(self) -> None:
        coarse_nodes = np.arange(self.coarse.size)
        fine_nodes = e031._coarse_to_fine_nodes(
            self.fine,
            self.coarse,
            coarse_nodes,
        )
        np.testing.assert_array_equal(
            self.fine.rho[fine_nodes],
            self.coarse.rho,
        )
        np.testing.assert_array_equal(
            self.fine.z[fine_nodes],
            self.coarse.z,
        )

    def test_line_graph_has_expected_positive_bar(self) -> None:
        values = np.array([0.0, 2.0, 1.0])
        rho = np.arange(3, dtype=float)
        z = np.zeros(3)
        edges = np.array([[0, 1], [1, 2]])
        result = e031.lower_star_h0_persistence(
            values,
            rho,
            z,
            edges,
            np.zeros(3, dtype=bool),
        )
        positive = [
            row for row in result["finite_bars"] if row["lifetime"] > 0.0
        ]
        self.assertEqual(len(positive), 1)
        self.assertEqual(positive[0]["birth"], 1.0)
        self.assertEqual(positive[0]["death"], 2.0)
        self.assertEqual(positive[0]["lifetime"], 1.0)
        self.assertEqual(len(result["essential_bars"]), 1)
        self.assertEqual(result["essential_bars"][0]["birth"], 0.0)
        self.assertIsNone(result["essential_bars"][0]["death"])

    def test_equal_level_batch_creates_no_positive_artifact(self) -> None:
        result = e031.lower_star_h0_persistence(
            np.zeros(4),
            np.array([0.0, 1.0, 0.0, 1.0]),
            np.array([0.0, 0.0, 1.0, 1.0]),
            np.array([[0, 1], [0, 2], [1, 3], [2, 3]]),
            np.zeros(4, dtype=bool),
        )
        self.assertTrue(
            all(row["lifetime"] == 0.0 for row in result["finite_bars"])
        )
        self.assertEqual(len(result["essential_bars"]), 1)

    def test_open_death_branch_metadata_is_edge_order_invariant(self) -> None:
        values = np.array([0.0, 2.0, 1.0, 2.0])
        rho = np.array([0.0, 1.0, 2.0, 3.0])
        z = np.zeros(4)
        edges = np.array([[0, 1], [1, 2], [2, 3]])
        boundary = np.array([False, False, True, False])
        first = e031.lower_star_h0_persistence(
            values,
            rho,
            z,
            edges,
            boundary,
        )
        second = e031.lower_star_h0_persistence(
            values,
            rho,
            z,
            edges[::-1],
            boundary,
        )
        first_positive = [
            row for row in first["finite_bars"] if row["lifetime"] > 0.0
        ]
        second_positive = [
            row for row in second["finite_bars"] if row["lifetime"] > 0.0
        ]
        self.assertEqual(first_positive, second_positive)
        self.assertEqual(
            first_positive[0]["dying_branch_open_sublevel_node_count"],
            1,
        )
        self.assertTrue(
            first_positive[0][
                "dying_branch_open_sublevel_touches_crop_boundary"
            ]
        )

    def test_stability_screen_is_strict_at_equality(self) -> None:
        equality = e031._finite_feature_stability_screen(0.2, 0.1)
        self.assertFalse(equality["strictly_exceeds_twice_epsilon"])
        self.assertEqual(
            equality["interpretation"],
            "diagonal_match_permitted_feature_unresolved",
        )
        above = e031._finite_feature_stability_screen(
            np.nextafter(0.2, np.inf),
            0.1,
        )
        self.assertTrue(above["strictly_exceeds_twice_epsilon"])

    def test_threshold_uses_strict_less_than_and_finite_interval(self) -> None:
        values = np.array([0.0, 0.02, 0.01])
        rho = np.arange(3, dtype=float)
        z = np.zeros(3)
        edges = np.array([[0, 1], [1, 2]])
        persistence = e031.lower_star_h0_persistence(
            values,
            rho,
            z,
            edges,
            np.zeros(3, dtype=bool),
        )
        rows = e031._threshold_components(
            values,
            rho,
            z,
            edges,
            np.zeros(3, dtype=bool),
            np.ones(3),
            np.ones(3),
            persistence,
            threshold=0.02,
        )
        self.assertEqual(len(rows), 2)
        finite = [
            row
            for row in rows
            if row["persistence_interval"]["death"] is not None
        ]
        self.assertEqual(len(finite), 1)
        self.assertEqual(
            finite[0]["persistence_interval"]["lifetime"],
            0.01,
        )

    def test_common_spectra_keep_volume_and_charge_separate(self) -> None:
        baseline_fine = np.array([1.0, 1.0, 1.0])
        current_fine = np.array([0.0, 0.5, 1.0])
        baseline_coarse = np.array([1.0, 1.0, 1.0])
        current_coarse = np.array([0.0, 0.0, 1.0])
        result = e031.common_deficit_spectra(
            baseline_fine,
            current_fine,
            baseline_coarse,
            current_coarse,
            np.array([1.0, 10.0, 100.0]),
            np.ones(3),
        )
        volume = result["spectra"]["source_support_volume"]
        charge = result["spectra"]["source_charge"]
        self.assertNotEqual(
            volume["fine"]["weighted_mean_positive_deficit"],
            charge["fine"]["weighted_mean_positive_deficit"],
        )
        self.assertGreater(
            volume["coarse_to_fine_mean_deficit_ratio"],
            1.0,
        )

    def test_transient_schedule_is_exact_and_sequential(self) -> None:
        system = self.coarse
        source = np.full(system.size, 0.02)
        baseline = np.zeros(system.size)
        first = np.ones(system.size)
        second = np.full(system.size, 2.0)
        stage_rows = [
            {"amplitude": e031.VERIFICATION_AMPLITUDES[0]},
            {"amplitude": e031.VERIFICATION_AMPLITUDES[1]},
        ]
        with (
            mock.patch.object(
                e031.e029,
                "solve_cone_safe_stage",
                side_effect=[
                    (first.copy(), stage_rows[0].copy()),
                    (second.copy(), stage_rows[1].copy()),
                ],
            ) as solve,
            mock.patch.object(
                e031.e029,
                "matched_tail_diagnostics",
                return_value={"thresholds": {}},
            ),
            mock.patch.object(
                e031.e029,
                "evaluate_tail_gate",
                return_value={"passes": False},
            ),
            mock.patch.object(
                e031.e030,
                "margin_deficit_spectrum",
                return_value={"spectra": {}},
            ),
        ):
            fields, rows = e031._solve_transient_endpoints(
                system,
                source,
                baseline,
                {"0.02": {}, "0.05": {}},
                AmgConfiguration(),
            )
        self.assertEqual(
            [row["amplitude"] for row in rows],
            list(e031.VERIFICATION_AMPLITUDES),
        )
        self.assertEqual(solve.call_count, 2)
        np.testing.assert_array_equal(
            solve.call_args_list[0].args[2],
            baseline,
        )
        np.testing.assert_array_equal(
            solve.call_args_list[1].args[2],
            first,
        )
        np.testing.assert_array_equal(
            fields[f"{e031.VERIFICATION_AMPLITUDES[1]:.17g}"],
            second,
        )


if __name__ == "__main__":
    unittest.main()

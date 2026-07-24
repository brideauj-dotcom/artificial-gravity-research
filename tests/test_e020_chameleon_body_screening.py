import math
import unittest

from models.e020_chameleon_body_screening import (
    Body,
    body_screening_case,
    chamber_scale_to_unscreen_body_m,
    chamber_field_ev,
    externally_driven_unscreened_requirement,
    scalar_acceleration_m_s2,
    thin_shell_charge,
    two_body_acceleration_ceiling_m_s2,
    two_body_scalar_acceleration_m_s2,
)


class ChameleonBodyScreeningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.human = Body("human proxy", mass_kg=70.0, radius_m=0.3)

    def test_one_meter_dark_energy_field_scale(self) -> None:
        field_ev = chamber_field_ev(1.0)
        self.assertAlmostEqual(field_ev, 1.5992060, places=6)

    def test_n1_chamber_field_scales_as_length_two_thirds(self) -> None:
        short = chamber_field_ev(0.1)
        long = chamber_field_ev(10.0)
        self.assertAlmostEqual(long / short, 100.0 ** (2.0 / 3.0), places=12)

    def test_thin_shell_charge_is_unscreened_below_transition(self) -> None:
        field_ev = chamber_field_ev(1.0)
        case = body_screening_case(self.human, 1.0)
        transition = float(case["beta_at_screening_transition"])
        self.assertEqual(
            thin_shell_charge(transition / 10.0, self.human, field_ev), 1.0
        )

    def test_acceleration_saturates_above_screening_transition(self) -> None:
        case = body_screening_case(self.human, 1.0)
        transition = float(case["beta_at_screening_transition"])
        field_ev = float(case["ambient_field_ev"])

        accelerations = []
        for beta in (transition * 10.0, transition * 1.0e6):
            charge = thin_shell_charge(beta, self.human, field_ev)
            accelerations.append(
                scalar_acceleration_m_s2(beta, charge, field_ev, 1.0)
            )

        self.assertTrue(
            math.isclose(accelerations[0], accelerations[1], rel_tol=1e-12)
        )
        self.assertTrue(
            math.isclose(
                accelerations[0],
                float(case["saturated_acceleration_m_s2"]),
                rel_tol=1e-12,
            )
        )

    def test_human_scale_ceiling_is_far_below_partial_gravity(self) -> None:
        case = body_screening_case(self.human, 1.0, target_g=0.01)
        self.assertAlmostEqual(
            float(case["saturated_acceleration_m_s2"]),
            1.1186165e-13,
            delta=1e-20,
        )
        self.assertGreater(float(case["target_to_saturated_ratio"]), 8.0e11)
        self.assertLess(
            float(case["max_unscreened_pair_force_ratio_at_body_transition"]),
            1.0e-5,
        )
        self.assertGreater(
            float(case["no_source_screening_mass_equivalent_at_1m_kg"]),
            2.0e14,
        )
        self.assertLess(
            float(case["adjacent_source_max_unscreened_mass_at_body_transition_kg"]),
            300.0,
        )

    def test_unscreening_scale_inverts_chamber_field(self) -> None:
        required_scale = chamber_scale_to_unscreen_body_m(1.0, self.human)
        required_field = chamber_field_ev(required_scale)
        transition_field = (
            2.0
            * 2.435e27
            * self.human.compactness()
        )
        self.assertGreater(required_scale, 1.0e4)
        self.assertTrue(
            math.isclose(required_field, transition_field, rel_tol=1e-12)
        )

    def test_nonoverlapping_pair_bound_has_expected_geometry_factor(self) -> None:
        case = body_screening_case(self.human, 1.0)
        pair_bound = two_body_acceleration_ceiling_m_s2(
            self.human,
            float(case["ambient_field_ev"]),
            source_radius_m=1.0,
            separation_m=1.3,
        )
        self.assertTrue(
            math.isclose(
                pair_bound,
                float(case["saturated_acceleration_m_s2"]) / 1.3**2,
                rel_tol=1e-12,
            )
        )

    def test_explicit_screened_pairs_do_not_exceed_pair_bound(self) -> None:
        field_ev = chamber_field_ev(1.0)
        source = Body("source", mass_kg=1.0e8, radius_m=0.2)
        bound = two_body_acceleration_ceiling_m_s2(
            self.human, field_ev, source.radius_m, separation_m=1.0
        )
        for beta in (1.0e-6, 1.0e-3, 1.0, 1.0e6):
            acceleration = two_body_scalar_acceleration_m_s2(
                beta, source, self.human, field_ev, separation_m=1.0
            )
            self.assertLessEqual(acceleration, bound * (1.0 + 1.0e-12))

    def test_pair_ceiling_is_attained_at_both_screening_transitions(self) -> None:
        case = body_screening_case(self.human, 1.0)
        beta = float(case["beta_at_screening_transition"])
        field_ev = float(case["ambient_field_ev"])
        source = Body(
            "transition source",
            float(case["adjacent_source_max_unscreened_mass_at_body_transition_kg"]),
            float(case["adjacent_source_radius_m"]),
        )
        separation = float(case["adjacent_source_center_separation_m"])
        explicit = two_body_scalar_acceleration_m_s2(
            beta, source, self.human, field_ev, separation
        )
        ceiling = two_body_acceleration_ceiling_m_s2(
            self.human, field_ev, source.radius_m, separation
        )
        self.assertTrue(math.isclose(explicit, ceiling, rel_tol=1e-12))

    def test_externally_driven_case_is_labeled_and_quantified(self) -> None:
        requirement = externally_driven_unscreened_requirement(
            1.0, self.human, 0.01 * 9.80665, 1.0
        )
        self.assertAlmostEqual(
            requirement["optimistic_field_floor_to_unscreen_ev"],
            843.8593,
            delta=1.0e-3,
        )
        self.assertAlmostEqual(
            requirement["required_field_excursion_ev"],
            2.6569185e9,
            delta=1.0e5,
        )
        self.assertAlmostEqual(
            requirement["canonical_gradient_energy_density_j_m3"],
            2.865e6,
            delta=2.0e3,
        )

    def test_invalid_inputs_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            chamber_field_ev(0.0)
        with self.assertRaises(ValueError):
            thin_shell_charge(0.0, self.human, 1.0)
        with self.assertRaises(ValueError):
            Body("bad", 1.0, 0.0).compactness()
        with self.assertRaises(ValueError):
            body_screening_case(self.human, 0.1)
        with self.assertRaises(ValueError):
            two_body_acceleration_ceiling_m_s2(
                self.human, 1.0, source_radius_m=1.0, separation_m=1.29
            )


if __name__ == "__main__":
    unittest.main()

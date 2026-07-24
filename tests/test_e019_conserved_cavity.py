import math
import unittest

from models.e019_conserved_cavity import (
    C,
    G,
    closed_cavity_source,
    emitted_pulse_source,
    field_only_source,
)


class ConservedCavityModelTests(unittest.TestCase):
    def test_field_only_matches_compact_energy_scale(self) -> None:
        source = field_only_source(1.0)
        expected = -G / C**2
        self.assertAlmostEqual(source.exact_acceleration(1.0), expected, places=45)

    def test_closed_cavity_cancels_monopole_and_dipole(self) -> None:
        source = closed_cavity_source(7.0, 0.02, 0.003)
        self.assertTrue(math.isclose(source.moment(0), 0.0, abs_tol=1e-15))
        self.assertTrue(math.isclose(source.moment(1), 0.0, abs_tol=1e-15))
        self.assertEqual(source.first_nonzero_moment(), 2)

    def test_closed_cavity_far_field_is_quadrupolar(self) -> None:
        source = closed_cavity_source(1.0, 0.01)
        a_at_one = abs(source.exact_acceleration(1.0))
        a_at_two = abs(source.exact_acceleration(2.0))
        effective_power = math.log(a_at_one / a_at_two) / math.log(2.0)
        self.assertAlmostEqual(effective_power, 4.0, delta=2e-4)

    def test_closed_cavity_leading_scale_is_energy_times_length_squared(self) -> None:
        energy = 9.0
        length = 0.04
        radius = 3.0
        source = closed_cavity_source(energy, length)
        expected = 3.0 * G * energy * length**2 / (4.0 * C**2 * radius**4)
        leading = source.multipole_acceleration(radius, max_order=2)
        self.assertAlmostEqual(leading / expected, 1.0, delta=1e-12)

    def test_multipole_matches_exact_closed_cavity_field(self) -> None:
        source = closed_cavity_source(1.0, 0.01)
        exact = source.exact_acceleration(1.0)
        multipole = source.multipole_acceleration(1.0, max_order=6)
        self.assertAlmostEqual(multipole / exact, 1.0, delta=1e-8)

    def test_emitted_pulse_recoil_cancels_monopole_and_dipole(self) -> None:
        elapsed = 0.005 / C
        source = emitted_pulse_source(3.0, elapsed, support_mass_kg=2.0)
        self.assertTrue(math.isclose(source.moment(0), 0.0, abs_tol=1e-15))
        self.assertTrue(math.isclose(source.moment(1), 0.0, abs_tol=1e-15))
        self.assertEqual(source.first_nonzero_moment(), 2)

    def test_first_order_pulse_recoil_is_support_mass_independent(self) -> None:
        elapsed = 0.005 / C
        light_support = emitted_pulse_source(1.0, elapsed, support_mass_kg=0.1)
        heavy_support = emitted_pulse_source(1.0, elapsed, support_mass_kg=100.0)
        self.assertTrue(
            math.isclose(
                light_support.exact_acceleration(1.0),
                heavy_support.exact_acceleration(1.0),
                rel_tol=1e-13,
                abs_tol=1e-44,
            )
        )

    def test_multipole_rejects_probe_inside_source(self) -> None:
        source = closed_cavity_source(1.0, 0.01)
        with self.assertRaises(ValueError):
            source.multipole_acceleration(0.001)


if __name__ == "__main__":
    unittest.main()

"""Independent count-statistics and geometry checks; no solver/checkpoint access."""

import math
import unittest

import models.e044_axion_helicity_audit as audit


class E044OpticalBudgetTests(unittest.TestCase):
    def assertRelative(self, actual, expected, tolerance=1e-11):
        self.assertTrue(
            math.isclose(actual, expected, rel_tol=tolerance, abs_tol=0.0),
            (actual, expected),
        )

    def test_count_budget_counts_incident_photons_not_circulating_power(self):
        result = audit.photon_counting_budget()
        photons = result["incident_optical_energy_j"] / result["photon_energy_j"]
        self.assertRelative(result["counting_sigma_rad"], photons ** -0.5)
        self.assertRelative(result["incident_power_w"], 157.07963267948966)
        self.assertRelative(result["counting_sigma_rad"], 6.771581582047851e-15)
        self.assertFalse(result["resource_tuple_demonstrated"])
        # Neither stored/circulating power nor a proposal normalization is a
        # measurement of detector information or of electrical facility energy.
        self.assertGreater(
            result["circulating_power_w"], result["incident_power_w"] * 1000
        )

    def test_two_color_allocation_minimizes_independent_photon_variance(self):
        base = audit.photon_counting_budget()
        for ratio in (1.000000532, 1.02, 2.0, 5.0):
            with self.subTest(ratio=ratio):
                result = audit.two_color_budget(ratio)
                w1, w2 = result["weights"]
                fraction = result["optimal_power_fraction_low_frequency"]
                exposure = base["incident_power_w"] * base["time_s"]
                e1 = base["photon_energy_j"]

                def variance(power_fraction):
                    # Each color's photon count is independently inferred
                    # from its share of total incident energy.
                    n1 = exposure * power_fraction / e1
                    n2 = exposure * (1.0 - power_fraction) / (e1 * ratio)
                    return w1 * w1 / n1 + w2 * w2 / n2

                predicted = result["optimal_counting_sigma_rad"] ** 2
                self.assertRelative(predicted, variance(fraction))
                grid_minimum = min(variance(i / 2000) for i in range(1, 2000))
                self.assertLessEqual(predicted, grid_minimum * (1 + 1e-13))
                # The reported stationary point must improve both nearby
                # allocations, independently of the closed-form minimizer.
                self.assertLess(variance(fraction), variance(fraction - 0.001))
                self.assertLess(variance(fraction), variance(fraction + 0.001))

    def test_adjacent_modes_fail_ideal_scale_while_octave_retains_conditional_margin(self):
        adjacent = audit.two_color_budget(1 + audit.WAVELENGTH_M / (2 * audit.LENGTH_M))
        octave = audit.two_color_budget(2.0)
        self.assertRelative(adjacent["optimal_counting_sigma_rad"], 2.545708377155485e-8)
        self.assertRelative(octave["optimal_counting_sigma_rad"], 2.3119625676143636e-14)
        self.assertRelative(octave["optimal_power_fraction_low_frequency"], 0.5857864376269049)
        signal = 7.366e-12  # rounded independent same-source comparison
        self.assertLess(signal / adjacent["optimal_counting_sigma_rad"], 0.0003)
        self.assertGreater(signal / octave["optimal_counting_sigma_rad"], 300)

    def test_two_color_estimator_cancels_length_but_cannot_identify_rotation(self):
        for ratio in (1.000000532, 2.0, 3.0):
            result = audit.two_color_budget(ratio)
            weights = result["weights"]
            # Two physically distinct achromatic decompositions produce the
            # same spectral observations, including a common length nuisance.
            first = [2.0 + 5.0 + k * 0.25 for k in (1.0, ratio)]
            second = [3.0 + 4.0 + k * 0.25 for k in (1.0, ratio)]
            self.assertEqual(first, second)
            estimate = math.fsum(w * y for w, y in zip(weights, first))
            self.assertAlmostEqual(estimate, 7.0, places=7)
            self.assertFalse(result["rejects_achromatic_rotation"])
        # Adding a third frequency cannot remove that null direction. Even a
        # restricted quadratic chromatic term leaves the two constant columns
        # identical, whereas arbitrary coating values add further degeneracy.
        frequencies = (1.0, 1.5, 2.0)
        design = [(1.0, 1.0, k, k * k) for k in frequencies]
        null_vector = (1.0, -1.0, 0.0, 0.0)
        self.assertEqual(
            [math.fsum(a * b for a, b in zip(row, null_vector)) for row in design],
            [0.0, 0.0, 0.0],
        )

    def test_vertical_rocking_harmonics_agree_with_direct_integration(self):
        samples = 4096
        angle = math.radians(1)
        values = []
        for i in range(samples):
            theta = 2 * math.pi * (i + 0.5) / samples
            values.append((theta, math.cos(angle * math.cos(theta))))
        harmonic1 = 2 * math.fsum(y * math.cos(t) for t, y in values) / samples
        harmonic2 = 2 * math.fsum(y * math.cos(2 * t) for t, y in values) / samples
        result = audit.report()["rocking"]
        self.assertAlmostEqual(harmonic1, result["about_vertical_first_harmonic"], places=13)
        self.assertLess(harmonic2, 0.0)
        self.assertRelative(
            -harmonic2,
            result["one_degree_second_harmonic_small_angle_fraction"],
            tolerance=3e-5,
        )

    def test_null_axis_geometry_and_sinusoidal_exposure(self):
        for latitude in (-90.0, -45.0, 0.0, 45.0, 90.0):
            with self.subTest(latitude=latitude):
                projections = []
                for i in range(256):
                    theta = 2 * math.pi * (i + 0.5) / 256
                    result = audit.orientation_projection(theta, latitude)
                    axis, direction = result["axis"], result["cavity_direction"]
                    self.assertAlmostEqual(sum(x * x for x in axis), 1.0, places=14)
                    self.assertAlmostEqual(sum(x * x for x in direction), 1.0, places=14)
                    self.assertAlmostEqual(sum(a * n for a, n in zip(axis, direction)), 0.0, places=14)
                    projections.append(result["vertical_projection"])
                # For a peak-amplitude template, actual Fisher exposure is
                # integral(f^2 dt); 300 calendar days is not 300 days of DC
                # information. The inclined null plane adds cos(latitude)^2.
                expected = math.cos(math.radians(latitude)) ** 2 / 2
                self.assertRelative(sum(p * p for p in projections) / 256, expected)

    def test_peak_amplitude_noise_uses_integrated_template_information(self):
        templates = [
            audit.orientation_projection(2 * math.pi * (i + 0.5) / 1024, 0.0)["vertical_projection"]
            for i in range(1024)
        ]
        information_fraction = math.fsum(f * f for f in templates) / len(templates)
        for result, constant_key in (
            (audit.photon_counting_budget(), "counting_sigma_rad"),
            (audit.two_color_budget(2.0), "optimal_counting_sigma_rad"),
            (audit.two_color_budget(1.000000532), "optimal_counting_sigma_rad"),
        ):
            self.assertRelative(
                result["full_rotation_peak_counting_sigma_rad"] ** 2,
                result[constant_key] ** 2 / information_fraction,
            )

    def test_reflected_spin_convention_uses_angular_rate_and_group_delay(self):
        omega = 2 * math.pi * 0.003
        # Reflected on-resonance cavity group delay is 4FL/(pi*c).
        # Opposite helicities have angular-frequency difference 2*omega.
        reflection_delay = 4 * audit.FINESSE * audit.LENGTH_M / (math.pi * audit.C_M_S)
        reflected = audit.spin_rotation_phase_rad(omega, convention_factor=2.0)
        self.assertRelative(reflected, 2 * omega * reflection_delay)
        self.assertRelative(audit.spin_rotation_phase_rad(-omega, convention_factor=2.0), -reflected)
        self.assertRelative(audit.spin_rotation_phase_rad(omega), reflected / 2)

    def test_qualification_retains_missing_and_unbounded_backgrounds(self):
        signal = 1e-12
        bounds = {name: 0.0 for name in audit.REQUIRED_BACKGROUNDS}
        self.assertFalse(audit.qualification(signal, None, bounds)["qualified"])
        self.assertFalse(audit.qualification(signal, signal * 1.01, bounds)["qualified"])
        for missing in audit.REQUIRED_BACKGROUNDS:
            with self.subTest(missing=missing):
                incomplete = dict(bounds)
                incomplete[missing] = None
                result = audit.qualification(signal, signal / 10, incomplete)
                self.assertFalse(result["qualified"])
                self.assertIn(missing, result["missing_backgrounds"])
                excessive = dict(bounds)
                excessive[missing] = signal / 10
                result = audit.qualification(signal, signal / 10, excessive)
                self.assertFalse(result["qualified"])
                self.assertIn(missing, result["failing_backgrounds"])

    def test_related_observable_comparators_do_not_pass_current_gate(self):
        result = audit.report()
        self.assertFalse(result["qualification"]["qualified"])
        self.assertIsNone(result["qualification"]["same_observable_measured_sigma_rad"])
        self.assertTrue(result["measured_noise_comparators"])
        for comparator in result["measured_noise_comparators"]:
            self.assertFalse(comparator["same_magpi_observable"])
        for geometry in result["rotation"]:
            self.assertIsNone(geometry["null_axis_measured_rejection"])

    def test_qualification_requires_explicit_measurement_and_transfer_attestations(self):
        signal = 1e-12
        bounds = {name: 0.01 * signal for name in audit.REQUIRED_BACKGROUNDS}
        for same, calibrated in ((False, False), (True, False), (False, True), (1, True), (True, "yes")):
            with self.subTest(same=same, calibrated=calibrated):
                result = audit.qualification(
                    signal, 0.1 * signal, bounds,
                    same_observable_and_resources_verified=same,
                    transfer_and_template_verified=calibrated,
                )
                self.assertFalse(result["qualified"])
        # Synthetic inputs only: this exercises the gate, not experimental
        # evidence. Current report must keep both attestations false.
        synthetic = audit.qualification(
            signal, 0.1 * signal, bounds,
            same_observable_and_resources_verified=True,
            transfer_and_template_verified=True,
        )
        self.assertTrue(synthetic["qualified"])
        self.assertEqual(synthetic["status"], "qualified_precision_test_only")

    def test_optical_helpers_reject_nonfinite_and_invalid_inputs(self):
        for bad in (math.nan, math.inf, -math.inf):
            calls = [
                lambda: audit.photon_counting_budget(power_w=bad),
                lambda: audit.photon_counting_budget(time_s=bad),
                lambda: audit.photon_counting_budget(wavelength_m=bad),
                lambda: audit.photon_counting_budget(finesse=bad),
                lambda: audit.two_color_budget(bad),
                lambda: audit.spin_rotation_phase_rad(bad),
                lambda: audit.spin_rotation_phase_rad(1.0, convention_factor=bad),
                lambda: audit.orientation_projection(bad, 45.0),
                lambda: audit.orientation_projection(0.0, bad),
                lambda: audit.rotation_budget(1e-12, modulation_hz=bad),
                lambda: audit.qualification(1e-12, bad, {}),
                lambda: audit.qualification(1e-12, None, {audit.REQUIRED_BACKGROUNDS[0]: bad}),
            ]
            for index, call in enumerate(calls):
                with self.subTest(value=bad, operation=index):
                    with self.assertRaises(ValueError):
                        call()
        for bad_ratio in (-1.0, 0.0, 1.0):
            with self.assertRaises(ValueError):
                audit.two_color_budget(bad_ratio)
        with self.assertRaises(ValueError):
            audit.photon_counting_budget(time_s=0.0)
        with self.assertRaises(ValueError):
            audit.orientation_projection(0.0, 90.01)


if __name__ == "__main__":
    unittest.main()

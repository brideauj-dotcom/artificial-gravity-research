import math
import unittest

from models.e019_conserved_tensor import (
    ConservedCavityTensor,
    IncompleteFieldOnlyTensor,
    RetardedLineMetric,
    stochastic_noise_projection,
)


class ConservedTensorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = ConservedCavityTensor(
            energy_j=1.0,
            length_m=0.01,
            frequency_hz=100e6,
            grid_cells=1001,
        )

    def test_energy_ledger_closes(self) -> None:
        ledger = self.source.energy_ledger()
        self.assertAlmostEqual(ledger["positive_field_region_J"], 1.0, delta=1e-12)
        self.assertAlmostEqual(
            ledger["negative_apparatus_region_J"], -1.0, delta=2e-8
        )
        self.assertAlmostEqual(ledger["net_J"], 0.0, delta=2e-8)

    def test_monopole_and_dipole_vanish(self) -> None:
        self.assertAlmostEqual(abs(self.source.energy_moment(0)), 0.0, delta=2e-8)
        self.assertAlmostEqual(abs(self.source.energy_moment(1)), 0.0, delta=1e-14)
        self.assertGreater(abs(self.source.energy_moment(2)), 0.0)

    def test_source_is_divergence_free(self) -> None:
        residual = self.source.source_conservation_residual()
        self.assertLess(residual["energy_equation_relative"], 1e-8)
        self.assertLess(residual["momentum_equation_relative"], 1e-8)

    def test_retarded_solution_is_in_harmonic_gauge(self) -> None:
        solver = RetardedLineMetric(self.source)
        residual = solver.harmonic_gauge_residual(1.0)
        self.assertLess(residual["nu_0_relative"], 2e-4)
        self.assertLess(residual["nu_x_relative"], 2e-4)

    def test_field_only_comparison_fails_harmonic_gauge(self) -> None:
        invalid = IncompleteFieldOnlyTensor(self.source)
        residual = RetardedLineMetric(invalid).harmonic_gauge_residual(1.0)
        self.assertGreater(residual["nu_0_relative"], 0.5)

    def test_low_frequency_tidal_limit_matches_static_t00(self) -> None:
        source = ConservedCavityTensor(
            energy_j=1.0,
            length_m=0.01,
            frequency_hz=1e3,
            grid_cells=1001,
        )
        solver = RetardedLineMetric(source)
        retarded = solver.tidal_amplitude(1.0)[
            "tidal_gradient_per_s2"
        ]
        static = solver.instantaneous_scalar_tidal_gradient(1.0)
        self.assertIsInstance(retarded, complex)
        self.assertTrue(math.isclose(abs(retarded), abs(static), rel_tol=2e-4))

    def test_tidal_signal_scales_linearly_with_energy(self) -> None:
        doubled = ConservedCavityTensor(
            energy_j=2.0,
            length_m=0.01,
            frequency_hz=100e6,
            grid_cells=1001,
        )
        first = RetardedLineMetric(self.source).tidal_amplitude(1.0)[
            "tidal_gradient_per_s2"
        ]
        second = RetardedLineMetric(doubled).tidal_amplitude(1.0)[
            "tidal_gradient_per_s2"
        ]
        self.assertIsInstance(first, complex)
        self.assertIsInstance(second, complex)
        self.assertTrue(math.isclose(abs(second / first), 2.0, rel_tol=1e-10))

    def test_tidal_solution_converges_with_grid_refinement(self) -> None:
        coarse = ConservedCavityTensor(
            energy_j=1.0,
            length_m=0.01,
            frequency_hz=100e6,
            grid_cells=501,
        )
        fine = ConservedCavityTensor(
            energy_j=1.0,
            length_m=0.01,
            frequency_hz=100e6,
            grid_cells=2001,
        )
        coarse_tidal = RetardedLineMetric(coarse).tidal_amplitude(1.0)[
            "tidal_gradient_per_s2"
        ]
        fine_tidal = RetardedLineMetric(fine).tidal_amplitude(1.0)[
            "tidal_gradient_per_s2"
        ]
        self.assertIsInstance(coarse_tidal, complex)
        self.assertIsInstance(fine_tidal, complex)
        self.assertTrue(
            math.isclose(abs(coarse_tidal), abs(fine_tidal), rel_tol=1e-5)
        )

    def test_stochastic_projection_preserves_noise_ratio(self) -> None:
        result = stochastic_noise_projection(
            modulation_frequency_hz=100e6,
            optical_wavelength_m=1.55e-6,
            mean_photons=4.5,
            kappa_hz=100e6,
            tidal_transfer_per_j=2e-31,
            baseline_m=1.0,
        )
        expected = math.sqrt(2.0 * (4.5 + 1.0))
        self.assertTrue(
            math.isclose(
                result["squeezed_to_coherent_ASD_ratio"], expected, rel_tol=1e-12
            )
        )

    def test_on_axis_probe_inside_source_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            RetardedLineMetric(self.source).bar_h_upper_amplitude(0.0)


if __name__ == "__main__":
    unittest.main()

"""Independent source-transfer checks and constraint-scope regressions for E-044."""
import math
import unittest

import numpy as np

from models import e044_axion_helicity_audit as audit


class E044SourceTransferTests(unittest.TestCase):
    def test_massless_field_matches_coulomb_endpoints(self):
        # Shell theorem: fixed total charge has the point-source exterior field.
        radius, height, length = 3.0, 0.7, 1.1
        source_mass, coupling = 17.0, 2.3e-20
        lower = radius + height
        expected = (coupling * source_mass / audit.U_KG
                    * audit.HBAR_C_EV_M / (4 * math.pi)
                    * (1 / lower - 1 / (lower + length)))
        actual = audit.field_difference_ev(
            0.0, coupling, radius_m=radius, source_mass_kg=source_mass,
            height_m=height, length_m=length)
        self.assertTrue(math.isclose(actual, expected, rel_tol=1e-14))

    def test_uniform_sphere_matches_independent_volume_quadrature(self):
        # Directly integrate the Yukawa Green function over source volume.
        # This reference uses no analytic angular or radial source form factor.
        nodes, weights = np.polynomial.legendre.leggauss(64)
        radial, radial_weight = (nodes + 1) / 2, weights / 2
        radius, height, length = 3.0, 1.2, 2.1
        lower, upper = radius + height, radius + height + length
        source_r = radius * radial[:, None]
        d_lower = np.sqrt(lower**2 + source_r**2
                          - 2 * lower * source_r * nodes[None, :])
        d_upper = np.sqrt(upper**2 + source_r**2
                          - 2 * upper * source_r * nodes[None, :])
        volume_weights = (1.5 * radial[:, None]**2
                          * radial_weight[:, None] * weights[None, :])
        source_mass, coupling = 19.0, 7e-22
        normalization = (coupling * source_mass / audit.U_KG
                         * audit.HBAR_C_EV_M / (4 * math.pi))
        for mass_radius in (0.0, 0.01, 0.05, 0.7, 3.0, 10.0):
            with self.subTest(mass_radius=mass_radius):
                inverse_range = mass_radius / radius
                integral = np.sum(volume_weights * (
                    np.exp(-inverse_range * d_lower) / d_lower
                    - np.exp(-inverse_range * d_upper) / d_upper))
                expected = normalization * float(integral)
                actual = audit.field_difference_ev(
                    inverse_range * audit.HBAR_C_EV_M, coupling,
                    radius_m=radius, source_mass_kg=source_mass,
                    height_m=height, length_m=length)
                self.assertTrue(math.isclose(actual, expected, rel_tol=3e-12),
                                (mass_radius, actual, expected))

    def test_surface_factor_matches_radial_average_across_branch(self):
        nodes, weights = np.polynomial.legendre.leggauss(80)
        radii, weights = (nodes + 1) / 2, weights / 2
        self.assertEqual(audit.surface_form_factor(0), 1)
        for y in (1e-10, 0.049, 0.05, 0.051, 0.1, 1, 10, 50):
            with self.subTest(y=y):
                expected = float(np.sum(weights * 3 * radii**2
                    * np.exp(-y) * np.sinh(y * radii) / (y * radii)))
                self.assertTrue(math.isclose(audit.surface_form_factor(y),
                                            expected, rel_tol=3e-12))
        # The near-surface layer, not exp(-mR), controls large-mR suppression.
        for y in (1e4, 1e8, 1e100):
            scaled = audit.surface_form_factor(y) * y * y
            self.assertTrue(math.isclose(scaled, 1.5 * (1 - 1 / y),
                                        rel_tol=1e-14))

    def test_source_dimension_and_coupling_scaling(self):
        original = dict(radius_m=2.0, height_m=0.4, length_m=0.9,
                        source_mass_kg=13.0)
        mass = 0.2 * audit.HBAR_C_EV_M
        phase = audit.phase_rad(mass, 3e-20, 2e-11, **original)
        scale = 7.0
        larger = {key: value * scale if key.endswith('_m') else value
                  for key, value in original.items()}
        # Fixed charge, fixed m*length: a larger system gives potential /scale.
        self.assertTrue(math.isclose(
            audit.phase_rad(mass / scale, 3e-20, 2e-11, **larger),
            phase / scale, rel_tol=1e-14))
        self.assertTrue(math.isclose(
            audit.phase_rad(mass, 6e-20, 6e-11, **original),
            6 * phase, rel_tol=1e-14))
        delta_phi = audit.field_difference_ev(mass, 3e-20, **original)
        # g_gamma is supplied in GeV^-1 while phi is returned in eV.
        expected = (4 * audit.FINESSE / math.pi) * (2e-11 / 1e9) * delta_phi
        self.assertTrue(math.isclose(phase, expected, rel_tol=1e-14))

    def test_fixed_coupling_signal_decreases_with_mass_and_source_height(self):
        phases = [audit.phase_rad(mass, 6.6e-25, 6.3e-13)
                  for mass in (0, 1e-15, 1e-14, 1e-13, 1e-12,
                               1e-10, 1e-8, 1e-6, 1e-5)]
        self.assertTrue(all(a > b >= 0 for a, b in zip(phases, phases[1:])))
        near = audit.phase_rad(1e-7, 6.6e-25, 6.3e-13)
        farther = audit.phase_rad(1e-7, 6.6e-25, 6.3e-13, height_m=10)
        self.assertLess(farther, near)
        self.assertEqual(audit.phase_rad(0, 0, 6.3e-13), 0)
        self.assertEqual(audit.phase_rad(0, 6.6e-25, 0), 0)

    def test_five_sphere_comparison_matches_disjoint_layer_integration(self):
        result = audit.source_model_sensitivity()
        spheres = result['full_spheres']
        self.assertEqual([s['radius_m'] for s in spheres],
                         [6371000, 6341000, 5701000, 3480000, 1221000])
        self.assertEqual([s['mass_fraction'] for s in spheres],
                         [0.5, 0.1333, 0.1715, 0.1929, 0.0023])
        self.assertTrue(math.isclose(sum(s['mass_fraction'] for s in spheres), 1))
        self.assertFalse(result['is_certified_uncertainty_bound'])
        self.assertFalse(result['is_current_allowed_signal_envelope'])
        self.assertEqual(result['lower_endpoint_from_center_m'],
                         audit.EARTH_RADIUS_M + audit.HEIGHT_M)
        nodes, weights = np.polynomial.legendre.leggauss(100)
        fractions = [s['radius_m'] / audit.EARTH_RADIUS_M for s in spheres]
        boundaries = sorted([0.0, *fractions])
        # Independently reconstruct disjoint layer densities, then integrate
        # the angle-averaged Yukawa kernel; no full-sphere form factor is used.
        for row in result['comparisons']:
            y = row['mass_ev'] * audit.EARTH_RADIUS_M / audit.HBAR_C_EV_M

            def integrate(lo, hi, density):
                x = (hi-lo)*(nodes+1)/2 + lo
                kernel = np.ones_like(x) if y == 0 else np.exp(-y)*np.sinh(y*x)/(y*x)
                return float(np.sum(weights*(hi-lo)/2 * density*x*x*kernel))

            layered = 0.0
            for lo, hi in zip(boundaries, boundaries[1:]):
                midpoint = (lo+hi)/2
                density = sum(3*s['mass_fraction']/a**3
                              for s, a in zip(spheres, fractions) if a > midpoint)
                layered += integrate(lo, hi, density)
            uniform = integrate(0.0, 1.0, 3.0)
            self.assertTrue(math.isclose(row['five_sphere_to_uniform_ratio'],
                                        layered/uniform, rel_tol=2e-12))
            if y == 0:
                self.assertTrue(math.isclose(layered, 1.0, rel_tol=1e-14))
                self.assertTrue(math.isclose(row['five_sphere_to_uniform_ratio'],
                                            1.0, rel_tol=1e-14))


class E044PhysicalScaleTests(unittest.TestCase):
    def test_fifth_force_matches_independent_si_newton_ratio(self):
        # Compare V_scalar/V_Newton directly in SI. This avoids the model's
        # eV gradient, atomic-mass energy and acceleration conversion chain.
        hbar_c_si = audit.H_J_S * audit.C_M_S / (2 * math.pi)
        relative_strength = (audit.LONG_RANGE_G_B**2 * hbar_c_si
                             / (4 * math.pi * audit.G_SI * audit.U_KG**2))
        newton_acceleration = (audit.G_SI * audit.EARTH_MASS_KG
                               / audit.EARTH_RADIUS_M**2)
        result = audit.massless_physical_scales()
        expected = relative_strength * newton_acceleration
        # HBAR_C_EV_M is rounded separately from exact SI h and c.
        self.assertTrue(math.isclose(
            result['conditional_fifth_force_acceleration_m_s2'], expected,
            rel_tol=1e-9))
        self.assertTrue(math.isclose(
            result['conditional_force_on_70kg_n'], 70 * expected,
            rel_tol=1e-9))
        self.assertTrue(math.isclose(relative_strength, 5.954851714e-12,
                                    rel_tol=1e-9))

    def test_local_gradient_energy_matches_si_coulomb_source(self):
        # A massless canonical source has local gradient energy
        # u = (hbar*c) g_B^2 Q^2 / (32*pi^2*r^4), in J/m^3.
        # This checks the powers of hbar*c without an eV^4 conversion.
        hbar_c_si = audit.H_J_S * audit.C_M_S / (2 * math.pi)
        charge = audit.EARTH_MASS_KG / audit.U_KG
        expected = (hbar_c_si * audit.LONG_RANGE_G_B**2 * charge**2
                    / (32 * math.pi**2 * audit.EARTH_RADIUS_M**4))
        result = audit.massless_physical_scales()
        self.assertTrue(math.isclose(result['local_gradient_energy_j_m3'],
                                    expected, rel_tol=1e-9))
        self.assertFalse(result['local_gradient_energy_is_full_apparatus_energy'])
        self.assertFalse(result['is_measured_or_controllable_source'])


class E044ConstraintScopeTests(unittest.TestCase):
    def test_pulsar_anchor_is_present_direct_product_not_prospective_limit(self):
        # Witte et al. v2 Eq20 is the present, approximate interpulse anchor;
        # Eq22's four-times-smaller value requires an unverified sign geometry.
        self.assertEqual(audit.PULSAR_PRODUCT_ANCHOR_GEV_INVERSE, 8e-39)
        for mass in (0.0, 1e-15, audit.LONG_RANGE_MAX_EV):
            with self.subTest(mass=mass):
                result = audit.pulsar_product_scenario(mass)
                self.assertEqual(result['product_gev_inverse'], 8e-39)
                self.assertIsNone(result['confidence'])
                self.assertEqual(result['status'],
                    'approximate_pulsar_model_anchor_not_global_envelope')
                self.assertNotIn('g_b_envelope', result)
                self.assertNotIn('g_gev_inverse', result)
                # The arbitrary factorization cannot set independent limits.
                for scalar in (2e-25, 6.6e-25):
                    expected = audit.phase_rad(mass, scalar, 8e-39 / scalar)
                    self.assertTrue(math.isclose(result['phase_ceiling_rad'],
                                                expected, rel_tol=1e-14))
        old_product = audit.LONG_RANGE_G_B * audit.PHOTON_SCENARIOS[
            'cluster_model']['g_gev_inverse']
        self.assertTrue(math.isclose(old_product / 8e-39, 51.975,
                                    rel_tol=1e-14))

    def test_pulsar_anchor_rejects_masses_beyond_audited_band(self):
        for mass in (math.nextafter(audit.LONG_RANGE_MAX_EV, math.inf),
                     1e-12, 1e-9):
            with self.subTest(mass=mass):
                result = audit.pulsar_product_scenario(mass)
                self.assertIsNone(result['phase_ceiling_rad'])
                self.assertEqual(result['status'], 'outside_audited_pulsar_scope')
                self.assertNotIn('product_gev_inverse', result)
        for mass in (-1e-15, math.inf, math.nan):
            with self.subTest(invalid_mass=mass):
                with self.assertRaises(ValueError):
                    audit.pulsar_product_scenario(mass)

    def test_report_propagates_pulsar_anchor_to_noise_and_rotation_budgets(self):
        report = audit.report()
        rows = report['pulsar_direct_product']
        self.assertEqual([row['mass_ev'] for row in rows], [0.0, 1e-15, 1e-14])
        for row in rows:
            self.assertEqual(row['product_gev_inverse'], 8e-39)
            self.assertIsNone(row['confidence'])
            self.assertFalse(row['prospective_eq22_used'])
            self.assertFalse(row['dark_matter_or_qcd_mass_relation_required'])
            self.assertFalse(row['stronger_death_line_numerical_curve_recovered'])
        for row in report['long_range_scenarios']:
            self.assertFalse(row['includes_direct_pulsar_product_constraint'])
        budget = report['pulsar_budget']
        ratio = 51.975
        self.assertTrue(math.isclose(budget['conditional_signal_rad'],
                                    1.41725065008e-13, rel_tol=1e-10))
        self.assertTrue(math.isclose(
            budget['cluster_comparison_to_pulsar_phase_ratio'], ratio,
            rel_tol=1e-14))
        # Same apparatus and integration: noise is unchanged while every
        # signal-derived residual budget tightens with the smaller product.
        for key in ('equivalent_differential_length_m',
                    'max_coherent_length_background_m',
                    'one_sided_white_length_asd_for_snr_one_m_sqrt_hz'):
            self.assertTrue(math.isclose(budget[key],
                report['required_residuals'][key] / ratio, rel_tol=1e-14))
        for name, old in report['two_color'].items():
            self.assertTrue(math.isclose(budget['full_rotation_peak_ideal_snr'][name],
                old['full_rotation_peak_ideal_snr'] / ratio, rel_tol=1e-14))
        for old, new in zip(report['rotation'], budget['rotation']):
            self.assertEqual(new['earth_vertical_phase_rad'],
                             old['earth_vertical_phase_rad'])
            self.assertTrue(math.isclose(new['earth_vertical_to_signal_ratio'],
                old['earth_vertical_to_signal_ratio'] * ratio, rel_tol=1e-14))
            self.assertTrue(math.isclose(new['max_coherent_axial_rate_residual_rad_s'],
                old['max_coherent_axial_rate_residual_rad_s'] / ratio, rel_tol=1e-14))
        self.assertFalse(budget['qualification']['qualified'])
        self.assertIsNone(budget['qualification']['same_observable_measured_sigma_rad'])

    def test_massless_and_finite_range_microscope_limits_are_distinct(self):
        # Recoverable primary-source anchors: Fayet2025 v2 Eq25/Table6.
        rows = dict(audit.MICROSCOPE_TABLE)
        self.assertEqual(rows[0], 6.4e-25)
        self.assertEqual(rows[1e-14], 6.6e-25)
        self.assertEqual(rows[1e-12], 2.17e-23)
        self.assertEqual(rows[1e-11], 8e-16)
        self.assertGreater(rows[1e-12], 30 * rows[0])
        self.assertGreaterEqual(audit.LONG_RANGE_G_B, rows[1e-14])

    def test_scenario_scope_stops_without_extrapolation_or_joint_confidence(self):
        for scenario in audit.PHOTON_SCENARIOS:
            edge = audit.long_range_scenario(audit.LONG_RANGE_MAX_EV, scenario)
            beyond = audit.long_range_scenario(
                math.nextafter(audit.LONG_RANGE_MAX_EV, math.inf), scenario)
            with self.subTest(scenario=scenario):
                self.assertGreater(edge['phase_ceiling_rad'], 0)
                self.assertIsNone(edge['qualified_joint_confidence'])
                self.assertIsNone(beyond['phase_ceiling_rad'])
                self.assertIsNone(beyond['qualified_joint_confidence'])
                self.assertEqual(beyond['status'], 'outside_audited_combined_scope')
                self.assertNotIn('product_gev_inverse', beyond)

    def test_constraints_keep_astrophysical_and_laboratory_provenance_separate(self):
        cluster = audit.PHOTON_SCENARIOS['cluster_model']
        solar = audit.PHOTON_SCENARIOS['solar_helioscope']
        laboratory = audit.PHOTON_SCENARIOS['laboratory_only']
        self.assertIn('Bayesian', cluster['confidence'])
        self.assertIn('beta=100', cluster['confidence'])
        self.assertIn('not laboratory-only', solar['scope'])
        self.assertEqual(solar['g_gev_inverse'], 5.8e-11)
        self.assertEqual(laboratory['source'], 'arXiv:2512.14110v3')
        self.assertEqual(laboratory['g_gev_inverse'], 1.5e-9)

    def test_diagnostic_report_cannot_claim_high_mass_allowed_signal(self):
        report = audit.report()
        self.assertFalse(report['model']['dark_matter_assumed'])
        self.assertFalse(report['model']['source_geometry_is_certified_earth_model'])
        self.assertFalse(report['qualification']['qualified'])
        for row in report['microscope_only_sparse_diagnostic']:
            self.assertFalse(row['full_allowed_region_qualified'])
        for row in report['fixed_coupling_mass_sensitivity']:
            self.assertFalse(row['is_current_allowed_envelope'])

    def test_unknown_background_or_noise_cannot_pass_qualification(self):
        phase = audit.phase_rad(0, 6.6e-25, 6.3e-13)
        bounds = {name: phase / 100 for name in audit.REQUIRED_BACKGROUNDS}
        self.assertFalse(audit.qualification(phase, None, bounds)['qualified'])
        for name in audit.REQUIRED_BACKGROUNDS:
            with self.subTest(background=name):
                unknown = {**bounds, name: None}
                result = audit.qualification(phase, phase / 2, unknown)
                self.assertFalse(result['qualified'])
                self.assertIn(name, result['missing_backgrounds'])


if __name__ == '__main__':
    unittest.main()

import math
import unittest

from models.e021_galileon_planar_screen import (
    axial_fractional_variation,
    cosmological_galileon_scale_ev,
    cube_sample_field_quality,
    cubic_cutoff_length_m,
    cubic_density_nonlinearity_mu,
    cubic_vainshtein_radius_m,
    default_case,
    disk_axis_shape_factor,
    finite_edge_nonlinearity_index,
    galileon_scale_from_crossover_ev,
    newtonian_disk_acceleration_m_s2,
    radius_for_axial_uniformity_m,
    scalar_disk_acceleration_m_s2,
    spherical_background_kinetic_z,
    thin_disk_field_geometry_integral,
)


class GalileonPlanarScreenTests(unittest.TestCase):
    def test_finite_disk_recovers_plane_limit(self) -> None:
        self.assertGreater(disk_axis_shape_factor(1.0e10, 1.0), 0.999999999)

    def test_unscreened_scalar_to_newtonian_ratio(self) -> None:
        sigma = 1234.0
        scalar = scalar_disk_acceleration_m_s2(
            sigma, radius_m=10.0, axial_distance_m=2.0, beta=0.7
        )
        newtonian = newtonian_disk_acceleration_m_s2(
            sigma, radius_m=10.0, axial_distance_m=2.0
        )
        self.assertTrue(math.isclose(scalar / newtonian, 2.0 * 0.7**2))

    def test_off_axis_quadrature_recovers_axis_formula(self) -> None:
        radius = 11.0
        axial_distance = 2.0
        _, integrated = thin_disk_field_geometry_integral(
            radius, 0.0, axial_distance, radial_cells=100, azimuthal_cells=180
        )
        analytic = 2.0 * math.pi * disk_axis_shape_factor(
            radius, axial_distance
        )
        self.assertTrue(
            math.isclose(abs(integrated), analytic, rel_tol=2.0e-4)
        )

    def test_environmental_kinetic_factor_suppresses_response(self) -> None:
        sigma = 100.0
        unsuppressed = scalar_disk_acceleration_m_s2(sigma, 10.0, 2.0, 1.0)
        suppressed = scalar_disk_acceleration_m_s2(
            sigma, 10.0, 2.0, 1.0, kinetic_z=1.0e6
        )
        self.assertTrue(math.isclose(unsuppressed / suppressed, 1.0e6))

    def test_environment_raises_cubic_cutoff_energy(self) -> None:
        bare_length = cubic_cutoff_length_m(1.0e-12)
        dressed_length = cubic_cutoff_length_m(1.0e-12, kinetic_z=1.0e8)
        self.assertTrue(math.isclose(bare_length / dressed_length, 1.0e4))

    def test_uniformity_solver_hits_ten_percent(self) -> None:
        radius = radius_for_axial_uniformity_m(2.0, 1.0, 0.10)
        self.assertAlmostEqual(radius, 11.7228353, places=6)
        self.assertAlmostEqual(
            axial_fractional_variation(radius, 2.0, 1.0), 0.10, places=12
        )

    def test_cube_sampling_exposes_lateral_field(self) -> None:
        radius = radius_for_axial_uniformity_m(2.0, 1.0, 0.10)
        quality = cube_sample_field_quality(radius, 2.0, 1.0)
        self.assertLess(quality["minimum_magnitude_ratio"], 0.91)
        self.assertGreater(quality["maximum_magnitude_ratio"], 1.10)
        self.assertGreater(quality["maximum_lateral_ratio"], 0.07)

    def test_cube_quadrature_is_stable_under_refinement(self) -> None:
        radius = radius_for_axial_uniformity_m(2.0, 1.0, 0.10)
        coarse = thin_disk_field_geometry_integral(
            radius, math.sqrt(2.0), 1.0, radial_cells=100, azimuthal_cells=180
        )
        fine = thin_disk_field_geometry_integral(
            radius, math.sqrt(2.0), 1.0, radial_cells=200, azimuthal_cells=360
        )
        coarse_magnitude = math.hypot(*coarse)
        fine_magnitude = math.hypot(*fine)
        self.assertTrue(
            math.isclose(coarse_magnitude, fine_magnitude, rel_tol=2.0e-4)
        )

    def test_edge_index_matches_global_vainshtein_identity(self) -> None:
        sigma = 1.0e8
        radius = 12.0
        beta = 1.3
        lambda_ev = cosmological_galileon_scale_ev()
        disk_mass = math.pi * radius**2 * sigma
        r_v = cubic_vainshtein_radius_m(disk_mass, beta, lambda_ev)
        local_index = finite_edge_nonlinearity_index(
            sigma, radius, beta, lambda_ev
        )
        self.assertTrue(
            math.isclose(local_index, 0.25 * (r_v / radius) ** 3, rel_tol=1e-12)
        )

    def test_spherical_background_factor_uses_exact_cubic_scaling(self) -> None:
        lambda_ev = cosmological_galileon_scale_ev()
        mass = 1.0e12
        distance = 10.0
        r_v = cubic_vainshtein_radius_m(mass, 1.0, lambda_ev)
        z = spherical_background_kinetic_z(mass, distance, 1.0, lambda_ev)
        self.assertTrue(math.isclose(z, math.sqrt(1.0 + (r_v / distance) ** 3)))

    def test_larger_crossover_has_lower_bare_galileon_scale(self) -> None:
        short = galileon_scale_from_crossover_ev(1.0e20)
        long = galileon_scale_from_crossover_ev(1.0e23)
        self.assertGreater(short, long)

    def test_default_case_exposes_both_mass_and_screening_failures(self) -> None:
        case = default_case()
        self.assertGreater(float(case["free_beta_1_disk_mass_kg"]), 5.0e10)
        self.assertGreater(
            float(case["cosmological_edge_nonlinearity_index"]), 1.0e33
        )
        self.assertGreater(float(case["earth_background_kinetic_z"]), 1.0e15)
        self.assertGreater(
            float(case["earth_background_required_disk_mass_kg"]), 1.0e26
        )
        self.assertGreater(float(case["isolated_sun_background_z_at_1_au"]), 1.0e11)
        self.assertGreater(
            float(case["isolated_sun_background_z_at_100_au"]), 1.0e8
        )
        self.assertGreater(
            float(case["published_plate_limit_newtonian_to_scalar_ratio"]),
            100.0,
        )
        self.assertTrue(
            math.isclose(
                float(case["galaxy_offset_limit_newtonian_to_scalar_ratio"]),
                6.25,
            )
        )
        self.assertGreater(
            float(case["published_plate_limit_total_target_disk_mass_kg"]),
            1.0e11,
        )
        self.assertLess(
            float(case["free_beta_1_total_target_disk_mass_kg"]),
            float(case["free_beta_1_disk_mass_kg"]),
        )
        self.assertGreater(
            float(case["source_mu_over_published_antiscreening_ceiling"]),
            1.0e32,
        )
        self.assertGreater(
            float(case["osmium_equivalent_source_thickness_m"]), 6.0e3
        )
        self.assertGreater(
            float(case["one_percent_thin_osmium_disk_radius_m"]), 6.0e5
        )

    def test_density_mu_scales_linearly_with_density_and_coupling(self) -> None:
        lambda_ev = cosmological_galileon_scale_ev()
        baseline = cubic_density_nonlinearity_mu(1.0, 1.0, lambda_ev)
        scaled = cubic_density_nonlinearity_mu(3.0, 2.0, lambda_ev)
        self.assertTrue(math.isclose(scaled / baseline, 6.0))

    def test_density_mu_reconstructs_uniform_disk_edge_index(self) -> None:
        radius = 12.0
        thickness = 0.3
        density = 4.0e3
        beta = 0.7
        lambda_ev = cosmological_galileon_scale_ev()
        mu = cubic_density_nonlinearity_mu(density, beta, lambda_ev)
        edge = finite_edge_nonlinearity_index(
            density * thickness, radius, beta, lambda_ev
        )
        self.assertTrue(
            math.isclose(edge, mu * thickness / (2.0 * radius), rel_tol=1e-12)
        )

    def test_invalid_inputs_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            disk_axis_shape_factor(0.0, 1.0)
        with self.assertRaises(ValueError):
            radius_for_axial_uniformity_m(1.0, 1.0, 0.1)
        with self.assertRaises(ValueError):
            finite_edge_nonlinearity_index(1.0, 1.0, 0.0, 1.0)
        with self.assertRaises(ValueError):
            cubic_density_nonlinearity_mu(0.0, 1.0, 1.0)
        with self.assertRaises(ValueError):
            cubic_cutoff_length_m(1.0, 0.0)


if __name__ == "__main__":
    unittest.main()

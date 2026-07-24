#!/usr/bin/env python3
"""E-021 finite planar cubic-Galileon engineering screen.

This model compares three levels that must not be conflated:

1. An exactly infinite plane, for which the cubic Galileon invariant vanishes.
2. A finite disk evaluated with the *linear* scalar solution.  This is a
   reference geometry, not a nonlinear finite-disk solution or a strict upper
   bound; nonlinear annular geometries can locally anti-screen.
3. Necessary-condition diagnostics for when the finite edge or an ambient
   spherical Vainshtein background makes that linear envelope inconsistent.

The canonical static field equation is written

  laplacian(phi) + c3/Lambda^3 *
      [(laplacian(phi))^2 - (d_i d_j phi)^2] = beta rho/M_Pl,

and test matter feels ``a_phi = -beta grad(phi)/M_Pl``.  The model uses the
reduced Planck mass.  It does not claim that a Galileon exists, solve the full
finite nonlinear PDE, establish an ultraviolet completion, or provide
reactionless propulsion.
"""

from __future__ import annotations

import argparse
import json
import math


C = 299_792_458.0
G = 6.67430e-11
EV_J = 1.602_176_634e-19
HBAR_C_EV_M = 1.973_269_804e-7
HBAR_EV_S = 6.582_119_569e-16
REDUCED_PLANCK_MASS_EV = 2.435e27
STANDARD_GRAVITY_M_S2 = 9.80665
MPC_M = 3.085_677_581_491_367e22
EARTH_MASS_KG = 5.9722e24
EARTH_RADIUS_M = 6.371e6
SUN_MASS_KG = 1.98847e30
ASTRONOMICAL_UNIT_M = 1.495_978_707e11
OSMIUM_DENSITY_KG_M3 = 22_590.0


def cosmological_galileon_scale_ev(hubble_km_s_mpc: float = 70.0) -> float:
    """Return ``Lambda=(M_Pl (hbar H0)^2)^(1/3)`` in electronvolts.

    ``70 km/s/Mpc`` is an illustrative round cosmological benchmark, not a
    claim about which present Hubble-constant inference is preferred.
    """

    if hubble_km_s_mpc <= 0.0:
        raise ValueError("Hubble benchmark must be positive")
    hubble_s_inverse = hubble_km_s_mpc * 1000.0 / MPC_M
    return (
        REDUCED_PLANCK_MASS_EV * (HBAR_EV_S * hubble_s_inverse) ** 2
    ) ** (1.0 / 3.0)


def galileon_scale_from_crossover_ev(crossover_m: float) -> float:
    """Return ``Lambda=(M_Pl/r_c^2)^(1/3)`` for a crossover length."""

    if crossover_m <= 0.0:
        raise ValueError("crossover length must be positive")
    crossover_ev_inverse = crossover_m / HBAR_C_EV_M
    return (
        REDUCED_PLANCK_MASS_EV / crossover_ev_inverse**2
    ) ** (1.0 / 3.0)


def disk_axis_shape_factor(radius_m: float, axial_distance_m: float) -> float:
    """Return the finite-disk factor relative to an infinite plane.

    The linear scalar and Newtonian disk fields share
    ``f=1-z/sqrt(z^2+R^2)`` on the symmetry axis.
    """

    if radius_m <= 0.0:
        raise ValueError("disk radius must be positive")
    if axial_distance_m < 0.0:
        raise ValueError("axial distance must be non-negative")
    return 1.0 - axial_distance_m / math.hypot(axial_distance_m, radius_m)


def thin_disk_field_geometry_integral(
    radius_m: float,
    radial_distance_m: float,
    axial_distance_m: float,
    radial_cells: int = 160,
    azimuthal_cells: int = 360,
) -> tuple[float, float]:
    """Numerically integrate the off-axis thin-disk field geometry.

    Returns radial and axial components in units of ``G Sigma``.  The same
    dimensionless vector applies to the linear scalar field, multiplied by
    ``2 beta^2/Z``.  Midpoint cells are sufficient here because all E-021
    target points remain at least one metre away from the source plane.
    """

    if radius_m <= 0.0:
        raise ValueError("disk radius must be positive")
    if radial_distance_m < 0.0:
        raise ValueError("radial distance must be non-negative")
    if axial_distance_m <= 0.0:
        raise ValueError("target must lie away from the source plane")
    if radial_cells < 8 or azimuthal_cells < 16:
        raise ValueError("quadrature grid is too coarse")

    radial_step = radius_m / radial_cells
    azimuthal_step = 2.0 * math.pi / azimuthal_cells
    radial_component = 0.0
    axial_component = 0.0
    for radial_index in range(radial_cells):
        source_radius = (radial_index + 0.5) * radial_step
        area_weight = source_radius * radial_step * azimuthal_step
        for azimuthal_index in range(azimuthal_cells):
            azimuth = (azimuthal_index + 0.5) * azimuthal_step
            delta_radial = source_radius * math.cos(azimuth) - radial_distance_m
            delta_transverse = source_radius * math.sin(azimuth)
            distance_squared = (
                delta_radial**2
                + delta_transverse**2
                + axial_distance_m**2
            )
            inverse_distance_cubed = distance_squared ** -1.5
            radial_component += (
                area_weight * delta_radial * inverse_distance_cubed
            )
            axial_component -= (
                area_weight * axial_distance_m * inverse_distance_cubed
            )
    return radial_component, axial_component


def cube_sample_field_quality(
    radius_m: float,
    center_distance_m: float,
    half_size_m: float,
) -> dict[str, float]:
    """Sample linear disk field quality on a 3 x 3 x 3 target cube."""

    if center_distance_m <= half_size_m:
        raise ValueError("target cube must stay on one side of the disk")
    center_field = abs(
        thin_disk_field_geometry_integral(radius_m, 0.0, center_distance_m)[1]
    )
    magnitude_ratios: list[float] = []
    lateral_ratios: list[float] = []
    for x in (-half_size_m, 0.0, half_size_m):
        for y in (-half_size_m, 0.0, half_size_m):
            radial_distance = math.hypot(x, y)
            for axial_distance in (
                center_distance_m - half_size_m,
                center_distance_m,
                center_distance_m + half_size_m,
            ):
                radial_field, axial_field = thin_disk_field_geometry_integral(
                    radius_m, radial_distance, axial_distance
                )
                magnitude_ratios.append(
                    math.hypot(radial_field, axial_field) / center_field
                )
                lateral_ratios.append(abs(radial_field) / center_field)
    return {
        "minimum_magnitude_ratio": min(magnitude_ratios),
        "maximum_magnitude_ratio": max(magnitude_ratios),
        "maximum_lateral_ratio": max(lateral_ratios),
    }


def axial_fractional_variation(
    radius_m: float, center_distance_m: float, half_depth_m: float
) -> float:
    """Maximum on-axis variation relative to the field at cabin center."""

    if center_distance_m <= half_depth_m:
        raise ValueError("cabin must stay on one side of the source disk")
    if half_depth_m <= 0.0:
        raise ValueError("cabin half-depth must be positive")
    center = disk_axis_shape_factor(radius_m, center_distance_m)
    near = disk_axis_shape_factor(radius_m, center_distance_m - half_depth_m)
    far = disk_axis_shape_factor(radius_m, center_distance_m + half_depth_m)
    return max(abs(near / center - 1.0), abs(far / center - 1.0))


def radius_for_axial_uniformity_m(
    center_distance_m: float,
    half_depth_m: float,
    fractional_tolerance: float,
) -> float:
    """Solve for the smallest disk radius meeting an on-axis tolerance."""

    if not 0.0 < fractional_tolerance < 1.0:
        raise ValueError("fractional tolerance must lie between zero and one")
    low = max(1.0e-12, half_depth_m * 1.0e-9)
    high = max(center_distance_m, half_depth_m)
    while axial_fractional_variation(high, center_distance_m, half_depth_m) > fractional_tolerance:
        high *= 2.0
    for _ in range(100):
        middle = 0.5 * (low + high)
        if axial_fractional_variation(
            middle, center_distance_m, half_depth_m
        ) > fractional_tolerance:
            low = middle
        else:
            high = middle
    return high


def scalar_disk_acceleration_m_s2(
    surface_density_kg_m2: float,
    radius_m: float,
    axial_distance_m: float,
    beta: float,
    kinetic_z: float = 1.0,
) -> float:
    """Linear finite-disk scalar reference acceleration.

    ``kinetic_z`` is the local kinetic renormalization multiplying the
    perturbation equation.  The controlling response is ``beta^2/Z``.
    """

    if surface_density_kg_m2 < 0.0:
        raise ValueError("surface density must be non-negative")
    if beta <= 0.0:
        raise ValueError("matter coupling beta must be positive")
    if kinetic_z <= 0.0:
        raise ValueError("kinetic renormalization must be positive")
    shape = disk_axis_shape_factor(radius_m, axial_distance_m)
    return 4.0 * math.pi * G * beta**2 * surface_density_kg_m2 * shape / kinetic_z


def newtonian_disk_acceleration_m_s2(
    surface_density_kg_m2: float,
    radius_m: float,
    axial_distance_m: float,
) -> float:
    """Newtonian on-axis acceleration of the same thin disk."""

    if surface_density_kg_m2 < 0.0:
        raise ValueError("surface density must be non-negative")
    shape = disk_axis_shape_factor(radius_m, axial_distance_m)
    return 2.0 * math.pi * G * surface_density_kg_m2 * shape


def required_surface_density_kg_m2(
    target_acceleration_m_s2: float,
    radius_m: float,
    axial_distance_m: float,
    beta: float,
    kinetic_z: float = 1.0,
) -> float:
    """Invert the linear disk reference field for surface density."""

    if target_acceleration_m_s2 <= 0.0:
        raise ValueError("target acceleration must be positive")
    unit_response = scalar_disk_acceleration_m_s2(
        1.0, radius_m, axial_distance_m, beta, kinetic_z
    )
    return target_acceleration_m_s2 / unit_response


def mass_kg_to_ev(mass_kg: float) -> float:
    if mass_kg <= 0.0:
        raise ValueError("mass must be positive")
    return mass_kg * C**2 / EV_J


def surface_density_ev3(surface_density_kg_m2: float) -> float:
    """Convert kg/m^2 to natural-unit energy per area, eV^3."""

    if surface_density_kg_m2 <= 0.0:
        raise ValueError("surface density must be positive")
    return surface_density_kg_m2 * C**2 / EV_J * HBAR_C_EV_M**2


def mass_density_ev4(mass_density_kg_m3: float) -> float:
    """Convert kg/m^3 to natural-unit energy density, eV^4."""

    if mass_density_kg_m3 <= 0.0:
        raise ValueError("mass density must be positive")
    return mass_density_kg_m3 * C**2 / EV_J * HBAR_C_EV_M**3


def cubic_density_nonlinearity_mu(
    mass_density_kg_m3: float,
    beta: float,
    lambda_ev: float,
) -> float:
    """Return the annular-disk paper's density parameter ``mu``.

    Ogawa, Hiramatsu, and Kobayashi define

      mu = beta rho_0/(Lambda^3 M_Pl).

    Their reported anti-screening becomes hard to see above roughly
    ``mu=10^3`` in the geometry they studied.  This is a source-density
    diagnostic, not a universal anti-screening threshold.
    """

    if beta <= 0.0:
        raise ValueError("matter coupling beta must be positive")
    if lambda_ev <= 0.0:
        raise ValueError("Lambda must be positive")
    return (
        beta
        * mass_density_ev4(mass_density_kg_m3)
        / (lambda_ev**3 * REDUCED_PLANCK_MASS_EV)
    )


def cubic_vainshtein_radius_m(
    mass_kg: float,
    beta: float,
    lambda_ev: float,
    cubic_coefficient: float = 1.0,
) -> float:
    """Return the spherical cubic-Galileon Vainshtein radius.

    This follows the normalization
    ``r_V^3=2 c3 beta M/(pi Lambda^3 M_Pl)``.  Applying a spherical radius to
    a disk is a global nonlinearity diagnostic, not a finite-disk solution.
    """

    if beta <= 0.0:
        raise ValueError("matter coupling beta must be positive")
    if lambda_ev <= 0.0:
        raise ValueError("Lambda must be positive")
    if cubic_coefficient <= 0.0:
        raise ValueError("cubic coefficient must be positive")
    radius_ev_inverse_cubed = (
        2.0
        * cubic_coefficient
        * beta
        * mass_kg_to_ev(mass_kg)
        / (math.pi * lambda_ev**3 * REDUCED_PLANCK_MASS_EV)
    )
    return radius_ev_inverse_cubed ** (1.0 / 3.0) * HBAR_C_EV_M


def finite_edge_nonlinearity_index(
    surface_density_kg_m2: float,
    radius_m: float,
    beta: float,
    lambda_ev: float,
    cubic_coefficient: float = 1.0,
) -> float:
    """Return a local necessary-condition index for the linear disk profile.

    The free finite-disk solution has an axial Hessian scale near its center
    of ``beta Sigma/(2 M_Pl R)``.  Multiplying by ``c3/Lambda^3`` gives

      epsilon_edge = c3 beta Sigma/(2 Lambda^3 M_Pl R)
                   = (r_V/R)^3/4,

    where the second identity uses the disk mass ``pi R^2 Sigma``.  Values
    much larger than one invalidate the unscreened finite-disk solution.  The
    index does not predict the nonlinear force or exclude local anti-screening.
    """

    if radius_m <= 0.0:
        raise ValueError("disk radius must be positive")
    if beta <= 0.0:
        raise ValueError("matter coupling beta must be positive")
    if lambda_ev <= 0.0:
        raise ValueError("Lambda must be positive")
    if cubic_coefficient <= 0.0:
        raise ValueError("cubic coefficient must be positive")
    radius_ev_inverse = radius_m / HBAR_C_EV_M
    return (
        cubic_coefficient
        * beta
        * surface_density_ev3(surface_density_kg_m2)
        / (
            2.0
            * lambda_ev**3
            * REDUCED_PLANCK_MASS_EV
            * radius_ev_inverse
        )
    )


def spherical_background_kinetic_z(
    source_mass_kg: float,
    distance_m: float,
    beta: float,
    lambda_ev: float,
    cubic_coefficient: float = 1.0,
) -> float:
    """Local radial-plate kinetic factor in a spherical cubic background.

    Linearizing a radial planar perturbation about the exact spherical cubic
    profile gives ``Z=sqrt(1+(r_V/r)^3)`` in this normalization.
    """

    if distance_m <= 0.0:
        raise ValueError("distance must be positive")
    r_v = cubic_vainshtein_radius_m(
        source_mass_kg, beta, lambda_ev, cubic_coefficient
    )
    return math.sqrt(1.0 + (r_v / distance_m) ** 3)


def cubic_cutoff_length_m(lambda_ev: float, kinetic_z: float = 1.0) -> float:
    """Return the minimal cubic fluctuation cutoff wavelength estimate.

    For a cubic interaction suppressed by ``Lambda^3``, canonical
    normalization on a background with kinetic factor ``Z`` raises the local
    cutoff energy by ``sqrt(Z)`` and lowers its wavelength by the same factor.
    This is an EFT estimate, not a statement about a UV completion.
    """

    if lambda_ev <= 0.0:
        raise ValueError("Lambda must be positive")
    if kinetic_z <= 0.0:
        raise ValueError("kinetic renormalization must be positive")
    return HBAR_C_EV_M / (lambda_ev * math.sqrt(kinetic_z))


def default_case() -> dict[str, float | str]:
    target = 0.01 * STANDARD_GRAVITY_M_S2
    center_distance = 2.0
    cabin_half_depth = 1.0
    tolerance = 0.10
    beta = 1.0
    radius = radius_for_axial_uniformity_m(
        center_distance, cabin_half_depth, tolerance
    )
    cube_quality = cube_sample_field_quality(
        radius, center_distance, cabin_half_depth
    )
    shape = disk_axis_shape_factor(radius, center_distance)
    sigma = required_surface_density_kg_m2(
        target, radius, center_distance, beta
    )
    disk_mass = math.pi * radius**2 * sigma
    lambda_cosmological = cosmological_galileon_scale_ev()
    illustrative_thickness = 0.10
    reference_density = sigma / illustrative_thickness
    reference_density_mu = cubic_density_nonlinearity_mu(
        reference_density, beta, lambda_cosmological
    )
    osmium_equivalent_thickness = sigma / OSMIUM_DENSITY_KG_M3
    one_percent_thin_osmium_radius = osmium_equivalent_thickness / 0.01
    one_percent_thin_osmium_mass = (
        math.pi * one_percent_thin_osmium_radius**2 * sigma
    )
    published_annular_mu_ceiling = 1.0e3
    edge_index = finite_edge_nonlinearity_index(
        sigma, radius, beta, lambda_cosmological
    )
    r_v_disk = cubic_vainshtein_radius_m(
        disk_mass, beta, lambda_cosmological
    )
    earth_z = spherical_background_kinetic_z(
        EARTH_MASS_KG, EARTH_RADIUS_M, beta, lambda_cosmological
    )
    earth_r_v = cubic_vainshtein_radius_m(
        EARTH_MASS_KG, beta, lambda_cosmological
    )
    human_r_v = cubic_vainshtein_radius_m(70.0, beta, lambda_cosmological)
    sun_r_v = cubic_vainshtein_radius_m(
        SUN_MASS_KG, beta, lambda_cosmological
    )
    sun_z_at_one_au = spherical_background_kinetic_z(
        SUN_MASS_KG,
        ASTRONOMICAL_UNIT_M,
        beta,
        lambda_cosmological,
    )
    sun_z_at_hundred_au = spherical_background_kinetic_z(
        SUN_MASS_KG,
        100.0 * ASTRONOMICAL_UNIT_M,
        beta,
        lambda_cosmological,
    )
    llr_crossover_m = 150.0 * MPC_M
    llr_lambda = galileon_scale_from_crossover_ev(llr_crossover_m)
    llr_edge_index = finite_edge_nonlinearity_index(
        sigma, radius, beta, llr_lambda
    )
    llr_earth_z = spherical_background_kinetic_z(
        EARTH_MASS_KG, EARTH_RADIUS_M, beta, llr_lambda
    )
    galaxy_delta_g_over_g_limit = 0.16
    galaxy_beta_limit = math.sqrt(galaxy_delta_g_over_g_limit / 2.0)
    galaxy_limited_sigma = required_surface_density_kg_m2(
        target, radius, center_distance, galaxy_beta_limit
    )
    galaxy_limited_mass = math.pi * radius**2 * galaxy_limited_sigma
    galaxy_limited_edge_index = finite_edge_nonlinearity_index(
        galaxy_limited_sigma,
        radius,
        galaxy_beta_limit,
        lambda_cosmological,
    )
    direct_plate_beta_effective_limit = 0.05
    limited_sigma = required_surface_density_kg_m2(
        target,
        radius,
        center_distance,
        direct_plate_beta_effective_limit,
    )
    limited_mass = math.pi * radius**2 * limited_sigma
    pure_newtonian_sigma = (
        target
        / (
            2.0
            * math.pi
            * G
            * disk_axis_shape_factor(radius, center_distance)
        )
    )
    pure_newtonian_mass = math.pi * radius**2 * pure_newtonian_sigma

    return {
        "epistemic_status": (
            "linear finite-disk reference plus necessary-condition screening "
            "diagnostics; not a nonlinear device solution or strict force bound"
        ),
        "target_acceleration_m_s2": target,
        "cabin_center_distance_m": center_distance,
        "cabin_half_depth_m": cabin_half_depth,
        "axial_fractional_tolerance": tolerance,
        "required_disk_radius_m": radius,
        "center_shape_factor": shape,
        "linear_cube_minimum_magnitude_ratio": cube_quality[
            "minimum_magnitude_ratio"
        ],
        "linear_cube_maximum_magnitude_ratio": cube_quality[
            "maximum_magnitude_ratio"
        ],
        "linear_cube_maximum_lateral_ratio": cube_quality[
            "maximum_lateral_ratio"
        ],
        "linear_cube_maximum_lateral_acceleration_m_s2": (
            target * cube_quality["maximum_lateral_ratio"]
        ),
        "free_beta_1_surface_density_kg_m2": sigma,
        "free_beta_1_disk_mass_kg": disk_mass,
        "free_beta_1_newtonian_acceleration_m_s2": (
            newtonian_disk_acceleration_m_s2(
                sigma, radius, center_distance
            )
        ),
        "pure_newtonian_total_target_disk_mass_kg": pure_newtonian_mass,
        "free_beta_1_total_target_disk_mass_kg": (
            pure_newtonian_mass / (1.0 + 2.0 * beta**2)
        ),
        "cosmological_lambda_ev": lambda_cosmological,
        "illustrative_source_thickness_m": illustrative_thickness,
        "illustrative_source_mass_density_kg_m3": reference_density,
        "osmium_equivalent_source_thickness_m": osmium_equivalent_thickness,
        "one_percent_thin_osmium_disk_radius_m": (
            one_percent_thin_osmium_radius
        ),
        "one_percent_thin_osmium_disk_mass_kg": one_percent_thin_osmium_mass,
        "illustrative_source_density_mu": reference_density_mu,
        "density_mu_reconstructed_edge_index": (
            reference_density_mu * illustrative_thickness / (2.0 * radius)
        ),
        "published_annular_antiscreening_mu_ceiling": (
            published_annular_mu_ceiling
        ),
        "source_mu_over_published_antiscreening_ceiling": (
            reference_density_mu / published_annular_mu_ceiling
        ),
        "cosmological_edge_nonlinearity_index": edge_index,
        "cosmological_disk_vainshtein_radius_m": r_v_disk,
        "lambda_needed_for_edge_index_1_ev": (
            lambda_cosmological * edge_index ** (1.0 / 3.0)
        ),
        "beta_needed_for_edge_index_1_at_fixed_target_and_lambda": edge_index,
        "earth_vainshtein_radius_m": earth_r_v,
        "earth_background_kinetic_z": earth_z,
        "earth_beta_squared_over_z": beta**2 / earth_z,
        "bare_cubic_cutoff_length_m": cubic_cutoff_length_m(
            lambda_cosmological
        ),
        "earth_dressed_cubic_cutoff_length_m": cubic_cutoff_length_m(
            lambda_cosmological, earth_z
        ),
        "earth_background_required_disk_mass_kg": disk_mass * earth_z,
        "earth_background_newtonian_to_scalar_ratio": earth_z / (2.0 * beta**2),
        "human_proxy_vainshtein_radius_m": human_r_v,
        "sun_vainshtein_radius_m": sun_r_v,
        "isolated_sun_background_z_at_1_au": sun_z_at_one_au,
        "isolated_sun_background_z_at_100_au": sun_z_at_hundred_au,
        "isolated_sun_1_au_required_disk_mass_kg": (
            disk_mass * sun_z_at_one_au
        ),
        "isolated_sun_100_au_required_disk_mass_kg": (
            disk_mass * sun_z_at_hundred_au
        ),
        "standard_llr_crossover_benchmark_mpc": 150.0,
        "standard_llr_crossover_lambda_ev": llr_lambda,
        "standard_llr_edge_nonlinearity_index": llr_edge_index,
        "standard_llr_earth_background_kinetic_z": llr_earth_z,
        "standard_llr_earth_background_required_disk_mass_kg": (
            disk_mass * llr_earth_z
        ),
        "standard_llr_earth_background_newtonian_to_scalar_ratio": (
            llr_earth_z / (2.0 * beta**2)
        ),
        "standard_llr_earth_dressed_cutoff_length_m": cubic_cutoff_length_m(
            llr_lambda, llr_earth_z
        ),
        "galaxy_offset_delta_g_over_g_1sigma_limit": (
            galaxy_delta_g_over_g_limit
        ),
        "galaxy_offset_mapped_beta_limit": galaxy_beta_limit,
        "galaxy_offset_limit_disk_mass_kg": galaxy_limited_mass,
        "galaxy_offset_limit_edge_nonlinearity_index": (
            galaxy_limited_edge_index
        ),
        "galaxy_offset_limit_newtonian_to_scalar_ratio": (
            1.0 / (2.0 * galaxy_beta_limit**2)
        ),
        "galaxy_offset_limit_total_target_disk_mass_kg": (
            pure_newtonian_mass / (1.0 + 2.0 * galaxy_beta_limit**2)
        ),
        "published_plate_beta_effective_limit": direct_plate_beta_effective_limit,
        "published_plate_limit_surface_density_kg_m2": limited_sigma,
        "published_plate_limit_disk_mass_kg": limited_mass,
        "published_plate_limit_newtonian_to_scalar_ratio": (
            1.0 / (2.0 * direct_plate_beta_effective_limit**2)
        ),
        "published_plate_limit_total_target_disk_mass_kg": (
            pure_newtonian_mass
            / (1.0 + 2.0 * direct_plate_beta_effective_limit**2)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()
    case = default_case()
    if args.json:
        print(json.dumps(case, indent=2, sort_keys=True))
        return
    for key, value in case.items():
        if isinstance(value, float):
            print(f"{key}: {value:.8e}")
        else:
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()

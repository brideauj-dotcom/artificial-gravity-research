"""E-043 same-unit audit of PSI-9 EHD/DEP liquid-film control.

This module freezes the published parabolic-flight and terrestrial apparatus,
recomputes pressure, bubble-force, electric-stress, heat-capacity, and real-GR
scales, and records what the public artifacts do and do not measure.  It is an
evidence and dimensional-analysis artifact, not a hardware action, a steady-
microgravity qualification, or a claim of real gravity, inertial control, or
reactionless propulsion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


CAMPAIGN = "E-043"
AUDIT_DATE = "2026-08-15"

NASA_PSI_DOI = "10.60555/18fc-8d56"
PRIMARY_PAPER_DOI = "10.1115/1.4055566"
EHD_MODEL_DOI = "10.1063/1.5121164"
NASA_NTRS_ID = "20190032021"

VACUUM_PERMITTIVITY_F_M = 8.854e-12
LIGHT_SPEED_M_S = 299_792_458.0
GRAVITATIONAL_CONSTANT_M3_KG_S2 = 6.67430e-11
STANDARD_GRAVITY_M_S2 = 9.81  # value used in the primary paper's force audit

FILM_HEIGHT_M = 2.0e-3
FLIGHT_HEATER_AREA_PAPER_M2 = 2.25e-4
FLIGHT_HEATER_AREA_DATA_GUIDE_M2 = 2.36e-4
FLIGHT_HEATER_SIDE_DATA_GUIDE_M = 0.625 * 0.0254
FLIGHT_HEATER_AREA_GEOMETRIC_M2 = FLIGHT_HEATER_SIDE_DATA_GUIDE_M**2
GROUND_HEATER_AREA_M2 = 1.0e-4
EHD_ELECTRODE_GAP_M = 254.0e-6
EHD_VOLTAGE_V = 1500.0
DEP_HEATER_GAP_M = 1.6e-3
DEP_VOLTAGE_V = 2000.0
DEP_REPORTED_MAX_FIELD_V_M = 5.0e6
PUMP_REPORTED_PRESSURE_PA = 50.0

BUBBLE_RADIUS_M = 0.1e-3
BUBBLE_REPORTED_BUOYANCY_N = 6.02e-8
BUBBLE_REPORTED_DEP_FORCE_N = 55.0e-8
NOVEC_RELATIVE_PERMITTIVITY_USED_BY_PAPER = 7.4
NOVEC_SURFACE_TENSION_N_M_AT_25C = 13.6e-3


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _gate(status: str, statement: str) -> dict[str, str]:
    if status not in {"passed", "partial", "failed", "unknown"}:
        raise ValueError(f"invalid gate status: {status}")
    return {"status": status, "statement": statement}


def _require_nonnegative(name: str, value: float) -> None:
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be finite and nonnegative")


def _require_positive(name: str, value: float) -> None:
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")


def implementation_provenance() -> dict[str, Any]:
    path = Path(__file__).resolve()
    return {
        "campaign": CAMPAIGN,
        "campaign_schema": 1,
        "audit_date": AUDIT_DATE,
        "module": {
            "path": str(path.relative_to(path.parents[1])),
            "sha256": _sha256_file(path),
        },
        "primary_identifiers": {
            "nasa_psi_investigation_doi": NASA_PSI_DOI,
            "primary_heat_transfer_paper_doi": PRIMARY_PAPER_DOI,
            "ehd_conduction_model_doi": EHD_MODEL_DOI,
            "nasa_ntrs_presentation_id": NASA_NTRS_ID,
        },
        "scope": (
            "published PSI-9 parabolic-flight and terrestrial apparatus; "
            "no hardware, new field solve, CFD, COMSOL reconstruction, or scale-up"
        ),
    }


def novec_properties(temp_c: float) -> dict[str, float]:
    """Return the paper's temperature correlations, without extrapolation."""
    if not math.isfinite(temp_c) or not -135.0 <= temp_c <= 61.0:
        raise ValueError("temperature lies outside the paper's liquid range")
    temp_k = temp_c + 273.15
    density = -2.2690 * temp_k + 2157.737
    relative_permittivity = -0.026 * temp_c + 7.3969
    conductivity = 2.2907e-9 + 1.20114e-8 * math.exp(
        -2.0 * ((temp_c - 18.5706) / 20.295) ** 2
    )
    permittivity = relative_permittivity * VACUUM_PERMITTIVITY_F_M
    return {
        "temperature_c": temp_c,
        "density_kg_m3": density,
        "relative_permittivity": relative_permittivity,
        "permittivity_f_m": permittivity,
        "conductivity_s_m": conductivity,
        "charge_relaxation_time_s": permittivity / conductivity,
    }


def electromechanics_and_thermal_confounder_audit() -> dict[str, Any]:
    """Freeze the force law and one declared thermal-gradient sensitivity.

    The sensitivity is not a reconstruction of PSI-9.  It asks how large the
    ordinary DC electrothermal stress would be if a 15 K gradient lay parallel
    to the mean DEP field across the published 1.6 mm gap.
    """
    properties = novec_properties(15.0)
    epsilon_liquid = properties["permittivity_f_m"]
    conductivity = properties["conductivity_s_m"]
    mean_field = electric_field_v_m(DEP_VOLTAGE_V, DEP_HEATER_GAP_M)
    gaussian_conductivity = conductivity - 2.2907e-9
    conductivity_derivative = gaussian_conductivity * (
        -4.0 * (15.0 - 18.5706) / 20.295**2
    )
    alpha_epsilon_per_k = -0.026 / properties["relative_permittivity"]
    beta_sigma_per_k = conductivity_derivative / conductivity
    sensitivity_delta_t_k = 15.0
    permittivity_gradient_pressure = (
        0.5
        * epsilon_liquid
        * abs(alpha_epsilon_per_k)
        * sensitivity_delta_t_k
        * mean_field**2
    )
    thermocharge_pressure = (
        epsilon_liquid
        * abs(alpha_epsilon_per_k - beta_sigma_per_k)
        * sensitivity_delta_t_k
        * mean_field**2
    )
    return {
        "electroquasistatic_definitions": {
            "field": "curl(E)=0; E=-grad(phi); div(epsilon*E)=rho_free",
            "maxwell_stress": "T_M=epsilon*(E outer E - 0.5*E^2*I)",
            "korteweg_helmholtz_body_force": (
                "f_e=rho_free*E - 0.5*E^2*grad(epsilon) + "
                "0.5*grad[rho*(d epsilon/d rho)_T*E^2]"
            ),
            "integrated_force_identity": (
                "integral_V(rho_free*E - 0.5*E^2*grad(epsilon))dV "
                "= surface_integral(T_M*n)dA for one consistent material model"
            ),
            "sharp_interface_rule": (
                "use either the bulk permittivity-gradient representation or "
                "the liquid-vapor Maxwell-traction jump, never both"
            ),
            "incompressible_limit": (
                "electrostriction is absorbable into pressure only within one "
                "isothermal incompressible phase; a boiling interface still "
                "requires a consistent thermodynamic pressure convention"
            ),
        },
        "dimension_checks": {
            "rho_free_times_E": "(C/m3)*(N/C)=N/m3",
            "epsilon_times_E_squared": "(F/m)*(V2/m2)=J/m3=Pa",
            "divergence_of_maxwell_stress": "Pa/m=N/m3",
        },
        "recoverability": {
            "volume_body_force_recoverable": False,
            "surface_integrated_force_recoverable": False,
            "reason": (
                "the public record has no charge-density map, field-gradient "
                "map, mesh/edge radii, velocity field, or electrode/support loads"
            ),
        },
        "declared_15k_parallel_gradient_sensitivity_not_psi_measurement": {
            "temperature_c": 15.0,
            "temperature_span_k": sensitivity_delta_t_k,
            "gap_m": DEP_HEATER_GAP_M,
            "mean_field_v_m": mean_field,
            "d_log_epsilon_d_t_per_k": alpha_epsilon_per_k,
            "d_log_sigma_d_t_per_k": beta_sigma_per_k,
            "permittivity_gradient_pressure_scale_pa": (
                permittivity_gradient_pressure
            ),
            "dc_thermocharge_coulomb_pressure_scale_pa": thermocharge_pressure,
            "interpretation": (
                "the conditional thermocharge scale is comparable with the "
                "reported 50 Pa pump head, so the unpublished temperature field "
                "cannot be treated as a negligible confounder"
            ),
        },
        "joule_heating_characteristic_not_volume_integral": {
            "sigma_e_squared_w_m3": conductivity * mean_field**2,
            "uniform_1cm2_by_1p6mm_example_w": (
                conductivity * mean_field**2 * GROUND_HEATER_AREA_M2 * DEP_HEATER_GAP_M
            ),
            "terminal_power_remains_the_conservative_public_bound_w": 0.6,
        },
    }


def electric_field_v_m(voltage_v: float, gap_m: float) -> float:
    """Return a field-magnitude scale from nonnegative voltage magnitude/gap."""
    _require_nonnegative("voltage", voltage_v)
    _require_positive("gap", gap_m)
    return voltage_v / gap_m


def maxwell_energy_density_pa(permittivity_f_m: float, field_v_m: float) -> float:
    _require_nonnegative("permittivity", permittivity_f_m)
    _require_nonnegative("field", field_v_m)
    return 0.5 * permittivity_f_m * field_v_m * field_v_m


def hydrostatic_pressure_pa(density_kg_m3: float, height_m: float) -> float:
    _require_nonnegative("density", density_kg_m3)
    _require_nonnegative("height", height_m)
    return density_kg_m3 * STANDARD_GRAVITY_M_S2 * height_m


def inferred_density_contrast_from_reported_buoyancy() -> float:
    """Return the paper-implied liquid-minus-vapor density, not liquid density."""
    volume = 4.0 * math.pi * BUBBLE_RADIUS_M**3 / 3.0
    return BUBBLE_REPORTED_BUOYANCY_N / (volume * STANDARD_GRAVITY_M_S2)


def field_and_pressure_audit() -> dict[str, Any]:
    epsilon_liquid = (
        NOVEC_RELATIVE_PERMITTIVITY_USED_BY_PAPER * VACUUM_PERMITTIVITY_F_M
    )
    density_from_15c_correlation = novec_properties(15.0)["density_kg_m3"]
    ehd_gap_field = electric_field_v_m(EHD_VOLTAGE_V, EHD_ELECTRODE_GAP_M)
    dep_mean_field = electric_field_v_m(DEP_VOLTAGE_V, DEP_HEATER_GAP_M)
    ehd_maxwell = maxwell_energy_density_pa(epsilon_liquid, ehd_gap_field)
    dep_maxwell_max = maxwell_energy_density_pa(
        epsilon_liquid, DEP_REPORTED_MAX_FIELD_V_M
    )
    dep_maxwell_mean = maxwell_energy_density_pa(epsilon_liquid, dep_mean_field)
    dep_interface_mean = 0.5 * (
        epsilon_liquid - VACUUM_PERMITTIVITY_F_M
    ) * dep_mean_field**2
    dep_interface_max = 0.5 * (
        epsilon_liquid - VACUUM_PERMITTIVITY_F_M
    ) * DEP_REPORTED_MAX_FIELD_V_M**2
    hydrostatic_from_correlation = hydrostatic_pressure_pa(
        density_from_15c_correlation, FILM_HEIGHT_M
    )
    return {
        "published_geometry": {
            "film_height_m": FILM_HEIGHT_M,
            "flight_heater_area_paper_m2": FLIGHT_HEATER_AREA_PAPER_M2,
            "flight_heater_area_data_guide_m2": FLIGHT_HEATER_AREA_DATA_GUIDE_M2,
            "flight_heater_area_from_0p625in_square_m2": (
                FLIGHT_HEATER_AREA_GEOMETRIC_M2
            ),
            "flight_heater_area_consistent": False,
            "ground_heater_area_m2": GROUND_HEATER_AREA_M2,
            "ehd_electrode_gap_m": EHD_ELECTRODE_GAP_M,
            "ehd_reference_voltage_v": EHD_VOLTAGE_V,
            "dep_to_grounded_heater_gap_m": DEP_HEATER_GAP_M,
            "dep_voltage_v": DEP_VOLTAGE_V,
        },
        "derived_fields": {
            "ehd_gap_average_field_v_m": ehd_gap_field,
            "dep_gap_average_field_v_m": dep_mean_field,
            "dep_reported_comsol_max_field_v_m": DEP_REPORTED_MAX_FIELD_V_M,
        },
        "same_unit_pressure_scales": {
            "paper_reported_ehd_pump_pressure_pa_at_1p5kv": (
                PUMP_REPORTED_PRESSURE_PA
            ),
            "reconstructed_2mm_hydrostatic_from_15c_correlation_pa": (
                hydrostatic_from_correlation
            ),
            "pump_to_2mm_hydrostatic_ratio": (
                PUMP_REPORTED_PRESSURE_PA / hydrostatic_from_correlation
            ),
            "pump_equivalent_acceleration_g_across_2mm_film": (
                PUMP_REPORTED_PRESSURE_PA / hydrostatic_from_correlation
            ),
            "ehd_gap_maxwell_energy_density_pa": ehd_maxwell,
            "pump_pressure_to_ehd_gap_maxwell_ratio": (
                PUMP_REPORTED_PRESSURE_PA / ehd_maxwell
            ),
            "dep_liquid_maxwell_energy_density_at_reported_max_pa": dep_maxwell_max,
            "dep_liquid_maxwell_energy_density_at_gap_average_pa": dep_maxwell_mean,
            "dep_interface_contrast_pressure_at_gap_average_pa": dep_interface_mean,
            "dep_interface_contrast_pressure_at_reported_max_pa": dep_interface_max,
            "loose_single_face_max_traction_ceiling_n": {
                "journal_flight_heater_area": (
                    dep_maxwell_max * FLIGHT_HEATER_AREA_PAPER_M2
                ),
                "data_guide_flight_heater_area": (
                    dep_maxwell_max * FLIGHT_HEATER_AREA_DATA_GUIDE_M2
                ),
                "geometric_flight_heater_area": (
                    dep_maxwell_max * FLIGHT_HEATER_AREA_GEOMETRIC_M2
                ),
                "ground_heater_area": dep_maxwell_max * GROUND_HEATER_AREA_M2,
            },
        },
        "provenance_limits": {
            "pump_pressure_measured_in_this_experiment": False,
            "pump_reference_voltage_matches_data_guide_flights_1_and_3": False,
            "pump_flow_rate_reported": False,
            "hydraulic_power_recoverable": False,
            "comsol_field_or_mesh_released": False,
            "dep_field_measured": False,
            "integrated_total_electrode_force_recoverable": False,
            "warning": (
                "pressure and field maxima are scale anchors, not a recovered "
                "volume force map or a hydraulic-efficiency measurement; the "
                "single-face maximum-traction products put the local edge field "
                "everywhere and are neither useful bubble force nor net apparatus force"
            ),
            "flight_voltage_warning": (
                "the NASA data-guide matrices put Flights 1 and 3 at 1.0 kV and "
                "only excluded Flight 4 at 1.5 kV, while journal Fig. 11 captions "
                "label flight EHD cases 1.5 kV; the 50 Pa at 1.5 kV reference "
                "must not be assigned to Flights 1 and 3"
            ),
            "geometry_warning": (
                "the journal reports 2.25 cm2, the NASA data guide uses 2.36 "
                "cm2, and its stated 0.625 inch square is 2.520 cm2; absolute "
                "flight heat capacity therefore requires an area sensitivity"
            ),
        },
    }


def bubble_force_audit() -> dict[str, Any]:
    density_contrast = inferred_density_contrast_from_reported_buoyancy()
    liquid_density = novec_properties(15.0)["density_kg_m3"]
    bubble_volume = 4.0 * math.pi * BUBBLE_RADIUS_M**3 / 3.0
    effective_buoyancy_mass = density_contrast * bubble_volume
    displaced_liquid_mass = liquid_density * bubble_volume
    epsilon_liquid = (
        NOVEC_RELATIVE_PERMITTIVITY_USED_BY_PAPER * VACUUM_PERMITTIVITY_F_M
    )
    dipole_coefficient = abs(
        2.0
        * math.pi
        * BUBBLE_RADIUS_M**3
        * epsilon_liquid
        * (VACUUM_PERMITTIVITY_F_M - epsilon_liquid)
        / (VACUUM_PERMITTIVITY_F_M + 2.0 * epsilon_liquid)
    )
    implied_gradient_e_squared = BUBBLE_REPORTED_DEP_FORCE_N / dipole_coefficient
    capillary_circumference_scale = (
        2.0 * math.pi * BUBBLE_RADIUS_M * NOVEC_SURFACE_TENSION_N_M_AT_25C
    )
    laplace_pressure = (
        2.0 * NOVEC_SURFACE_TENSION_N_M_AT_25C / BUBBLE_RADIUS_M
    )
    dc_permittivity_clausius_mossotti = (
        VACUUM_PERMITTIVITY_F_M - epsilon_liquid
    ) / (VACUUM_PERMITTIVITY_F_M + 2.0 * epsilon_liquid)
    dc_conductivity_limit = -0.5
    maxwell_wagner_time = (
        VACUUM_PERMITTIVITY_F_M + 2.0 * epsilon_liquid
    ) / (2.0 * novec_properties(15.0)["conductivity_s_m"])
    return {
        "paper_inputs": {
            "bubble_radius_m": BUBBLE_RADIUS_M,
            "bubble_radius_source": (
                "Zuber-based correlation estimate from paper Eq. 4 at 2 W/cm2 "
                "and 15 C superheat; not a measured flight bubble-size distribution"
            ),
            "reported_buoyancy_force_n": BUBBLE_REPORTED_BUOYANCY_N,
            "reported_max_dep_force_n": BUBBLE_REPORTED_DEP_FORCE_N,
            "dep_force_source": (
                "bubble-free COMSOL field-gradient calculation plus spherical "
                "dilute-bubble DEP formula; not a direct force measurement"
            ),
        },
        "reconstructed_scales": {
            "liquid_minus_vapor_density_inferred_from_reported_buoyancy_kg_m3": (
                density_contrast
            ),
            "effective_buoyancy_mass_kg": effective_buoyancy_mass,
            "liquid_density_from_15c_correlation_kg_m3": liquid_density,
            "displaced_liquid_mass_from_15c_correlation_kg": displaced_liquid_mass,
            "dep_to_buoyancy_ratio": (
                BUBBLE_REPORTED_DEP_FORCE_N / BUBBLE_REPORTED_BUOYANCY_N
            ),
            "dep_force_per_displaced_liquid_mass_m_s2": (
                BUBBLE_REPORTED_DEP_FORCE_N / displaced_liquid_mass
            ),
            "dep_force_per_displaced_liquid_mass_in_g": (
                BUBBLE_REPORTED_DEP_FORCE_N
                / displaced_liquid_mass
                / STANDARD_GRAVITY_M_S2
            ),
            "implied_gradient_e_squared_v2_m3": implied_gradient_e_squared,
            "bubble_radius_to_dep_grate_feature_width": (
                BUBBLE_RADIUS_M / 0.508e-3
            ),
            "local_electric_capillary_number_epsilon_e2_a_over_gamma": (
                epsilon_liquid
                * DEP_REPORTED_MAX_FIELD_V_M**2
                * BUBBLE_RADIUS_M
                / NOVEC_SURFACE_TENSION_N_M_AT_25C
            ),
            "capillary_circumference_force_scale_n": capillary_circumference_scale,
            "dep_to_capillary_circumference_scale": (
                BUBBLE_REPORTED_DEP_FORCE_N / capillary_circumference_scale
            ),
            "laplace_pressure_scale_pa": laplace_pressure,
            "permittivity_clausius_mossotti_factor": (
                dc_permittivity_clausius_mossotti
            ),
            "low_frequency_leaky_dielectric_factor_if_vapor_conductivity_is_zero": (
                dc_conductivity_limit
            ),
            "coefficient_magnitude_shift_from_permittivity_to_dc_limit": (
                abs(dc_conductivity_limit / dc_permittivity_clausius_mossotti) - 1.0
            ),
            "maxwell_wagner_time_s_using_paper_force_permittivity": (
                maxwell_wagner_time
            ),
            "maxwell_wagner_frequency_hz": (
                1.0 / (2.0 * math.pi * maxwell_wagner_time)
            ),
        },
        "interpretation": (
            "the published DEP magnitude is about 9.14 times one-g buoyancy "
            "for the assumed bubble; dividing force by correlated displaced-"
            "liquid mass gives an 8.90g force-per-mass scale, not a measured "
            "bubble acceleration because added mass, drag, walls, and contact "
            "forces intervene; bubble/contact-line capillarity, flow "
            "inertia, drag, coalescence, interface charge, and the actual field-"
            "distorted shape must be measured before attributing departure to "
            "the spherical point-dipole DEP model alone; at DC the leaky-"
            "dielectric coefficient and tangential interface charge also need testing"
        ),
    }


def thermal_performance_audit() -> dict[str, Any]:
    flight_baseline_dryout_flux_w_cm2 = 5.5
    flight_dep_dryout_flux_w_cm2 = 7.0
    ground_baseline_chf_w_cm2 = 9.76
    ground_combined_chf_w_cm2 = 15.63
    flight_increment_w = (
        flight_dep_dryout_flux_w_cm2 - flight_baseline_dryout_flux_w_cm2
    ) * (FLIGHT_HEATER_AREA_PAPER_M2 * 1.0e4)
    ground_increment_w = (
        ground_combined_chf_w_cm2 - ground_baseline_chf_w_cm2
    ) * (GROUND_HEATER_AREA_M2 * 1.0e4)
    return {
        "parabolic_flight": {
            "microgravity_segment_duration_s": [15, 20],
            "hypergravity_segment_duration_s": [20, 30],
            "reported_ehd_electrical_steady_state_time": (
                "several minutes; no exact duration reported"
            ),
            "number_of_parabolas": 120,
            "flight_days": 4,
            "data_guide_intro_flight_days": 3,
            "flight_day_count_consistent": False,
            "individual_condition_files": 118,
            "missing_flight_4_condition_files": [23, 24],
            "data_guide_voltage_matrix": {
                "flights_1_and_3_ehd_v": 1000.0,
                "flight_4_ehd_v": 1500.0,
                "dep_on_v": 2000.0,
                "dc_actuation": True,
            },
            "journal_figure_11_ehd_caption_v": 1500.0,
            "journal_caption_and_data_guide_flight_voltage_consistent": False,
            "flight_4_hardware_and_publication_limit": (
                "a dimensionally unspecified wider-slit DEP grate, fresh fluid, "
                "possible noncondensables, and a breaker interruption make Flight "
                "4 separate; its data were not used in the journal result"
            ),
            "baseline_dryout_heat_flux_w_cm2": flight_baseline_dryout_flux_w_cm2,
            "dep_dryout_heat_flux_w_cm2": flight_dep_dryout_flux_w_cm2,
            "reported_relative_increase": 0.273,
            "reconstructed_absolute_baseline_capacity_w": (
                flight_baseline_dryout_flux_w_cm2
                * FLIGHT_HEATER_AREA_PAPER_M2
                * 1.0e4
            ),
            "reconstructed_absolute_dep_capacity_w": (
                flight_dep_dryout_flux_w_cm2
                * FLIGHT_HEATER_AREA_PAPER_M2
                * 1.0e4
            ),
            "reconstructed_incremental_capacity_w": flight_increment_w,
            "heater_area_sensitivity": {
                "journal_2p25_cm2_increment_w": flight_increment_w,
                "data_guide_2p36_cm2_increment_w": (
                    (flight_dep_dryout_flux_w_cm2 - flight_baseline_dryout_flux_w_cm2)
                    * FLIGHT_HEATER_AREA_DATA_GUIDE_M2
                    * 1.0e4
                ),
                "geometric_0p625in_square_increment_w": (
                    (flight_dep_dryout_flux_w_cm2 - flight_baseline_dryout_flux_w_cm2)
                    * FLIGHT_HEATER_AREA_GEOMETRIC_M2
                    * 1.0e4
                ),
            },
            "steady_state": False,
            "true_chf_identified": False,
            "paper_caveat": (
                "flight dryout is not necessarily CHF because the gravity "
                "segments and thermal response are transient; each 15-20 s zero-g "
                "window is far shorter than the reported several-minute electrical "
                "steady-state time"
            ),
            "raw_temperature_electrical_pressure_acceleration_files_documented": True,
            "calibrated_flow_force_or_film_thickness_series_documented": False,
        },
        "terrestrial_updated_heater": {
            "baseline_chf_w_cm2": ground_baseline_chf_w_cm2,
            "combined_ehd_dep_chf_w_cm2": ground_combined_chf_w_cm2,
            "relative_increase": (
                ground_combined_chf_w_cm2 / ground_baseline_chf_w_cm2 - 1.0
            ),
            "reconstructed_absolute_baseline_capacity_w": (
                ground_baseline_chf_w_cm2 * GROUND_HEATER_AREA_M2 * 1.0e4
            ),
            "reconstructed_absolute_combined_capacity_w": (
                ground_combined_chf_w_cm2 * GROUND_HEATER_AREA_M2 * 1.0e4
            ),
            "reconstructed_incremental_capacity_w": ground_increment_w,
            "reported_max_combined_hv_power_w": 0.4,
            "capacity_gain_per_reported_max_hv_w": ground_increment_w / 0.4,
        },
        "electrical_and_system_energy": {
            "reported_all_condition_current_below_a": 0.3e-3,
            "reported_all_condition_hv_power_at_most_w": 0.6,
            "nasa_data_guide_flight_current_below_a": 0.1e-3,
            "nasa_data_guide_flight_hv_power_below_w": 0.1,
            "published_summary_bounds_contradict": False,
            "published_summary_scopes_identical": False,
            "published_bound_interpretation": (
                "the flight-only NASA limits are nested within the journal's "
                "looser all-condition limits and the 0.4 W ground maximum; they "
                "do not provide synchronized per-branch or whole-system power"
            ),
            "average_power_only_described_as_substantially_lower": True,
            "flight_capacity_gain_per_reported_overall_max_hv_w": (
                flight_increment_w / 0.6
            ),
            "not_a_cop_warning": (
                "incremental CHF/dryout capacity divided by a reported HV-power "
                "ceiling is a capacity-leverage diagnostic, not coefficient of "
                "performance: simultaneous branch powers, flow work, and chiller "
                "power/heat rejection were not published"
            ),
        },
        "measurement_uncertainty": {
            "heat_flux_relative": 0.031,
            "heat_transfer_coefficient_relative": 0.14,
            "temperature_difference_c": 0.7,
            "ehd_current_a": 2.5e-6,
            "dep_current_a": 2.5e-6,
        },
        "noncomparability_warning": (
            "flight and later terrestrial tests used different heater areas and "
            "DEP hardware, so their absolute capacities are not a gravity-only comparison"
        ),
    }


def real_curvature_field_energy_screen() -> dict[str, Any]:
    epsilon_liquid = (
        NOVEC_RELATIVE_PERMITTIVITY_USED_BY_PAPER * VACUUM_PERMITTIVITY_F_M
    )
    energy_density = maxwell_energy_density_pa(
        epsilon_liquid, DEP_REPORTED_MAX_FIELD_V_M
    )
    deliberately_optimistic_volume = (
        FLIGHT_HEATER_AREA_GEOMETRIC_M2 * FILM_HEIGHT_M
    )
    energy = energy_density * deliberately_optimistic_volume
    mass_equivalent = energy / LIGHT_SPEED_M_S**2
    probe_distance = 0.01
    acceleration = (
        GRAVITATIONAL_CONSTANT_M3_KG_S2
        * mass_equivalent
        / probe_distance**2
    )
    einstein_curvature_scale = (
        8.0
        * math.pi
        * GRAVITATIONAL_CONSTANT_M3_KG_S2
        * energy_density
        / LIGHT_SPEED_M_S**4
    )
    return {
        "assumption": (
            "the reported local maximum field fills the largest heater-area "
            "interpretation, a 0.625 inch square by 2 mm liquid volume; this "
            "deliberately favorable screen overstates the published bubble-free "
            "field-map volume but is not a rigorous apparatus energy upper bound"
        ),
        "electric_energy_density_j_m3": energy_density,
        "field_energy_j": energy,
        "mass_equivalent_kg": mass_equivalent,
        "optimistic_acceleration_at_1cm_m_s2": acceleration,
        "ratio_to_standard_gravity": acceleration / STANDARD_GRAVITY_M_S2,
        "einstein_equation_curvature_scale_m_minus_2": einstein_curvature_scale,
        "decision": (
            "ordinary field energy sources genuine GR curvature, but this fails "
            "the useful engineered-curvature scale by roughly 27.5 orders of "
            "magnitude in the deliberately favorable compact-source estimate; a "
            "closed supply chiefly redistributes existing system energy into the field"
        ),
    }


def reaction_and_energy_ledger() -> dict[str, Any]:
    return {
        "electrical_source": (
            "high-voltage supplies separate charge and establish fields; their "
            "electrodes receive the equal-and-opposite Maxwell/Coulomb reaction"
        ),
        "fluid_and_phase": (
            "EHD heterocharge layers push liquid radially; DEP shifts vapor toward "
            "lower field while liquid, interfaces, heater, and electrode receive reaction"
        ),
        "thermal_source_sink": (
            "the resistance heater supplies phase-change heat and the chilled "
            "condenser loop removes it; neither power nor momentum is source-free"
        ),
        "structure": (
            "heater pedestal, pump disk, chamber, wiring, power supplies, baseplate, "
            "flight rack, aircraft or spacecraft carry the closing reaction"
        ),
        "net_vehicle_implication": (
            "internal EHD/DEP circulation cannot accelerate a closed vehicle; absent "
            "coupling to an external field, plasma, or body, only exported radiation "
            "or expelled mass would provide conventional thrust"
        ),
        "missing_energy_terms": [
            "branch-resolved simultaneous voltage-current traces",
            "pump flow rate and hydraulic power delta_p times Q",
            "chiller coolant flow, inlet/outlet enthalpy, and electrical power",
            "time-resolved stored electric and interfacial energy",
            "heat leak through chamber, pedestal, wiring, and ambient",
        ],
    }


def claim_kill_matrix() -> list[dict[str, Any]]:
    return [
        {
            "claim": "the apparatus demonstrated electrically controlled thin-film boiling in transient microgravity",
            "supported": True,
            "reason": (
                "the campaign reports 120 parabolas, and baseline/EHD/DEP/combined "
                "states appear across the published dataset; only 118 individual "
                "condition files are listed and Flight 4 was excluded from the paper"
            ),
        },
        {
            "claim": "the published result contains useful absolute device-scale force and pressure anchors",
            "supported": True,
            "reason": "50 Pa pump pressure and 5.5e-7 N assumed-bubble DEP force are explicitly reported, though modeled rather than directly measured",
        },
        {
            "claim": "the experiment measured a complete volume-force field or hydraulic efficiency",
            "supported": False,
            "reason": "no differential-pressure trace, flow rate, released field map, or integrated support-force measurement is public",
        },
        {
            "claim": "the flight established a steady-microgravity critical heat flux",
            "supported": False,
            "reason": "15-20 s unsteady microgravity segments produced dryout points that the paper distinguishes from true CHF",
        },
        {
            "claim": "the reported electrical power establishes whole-system cooling efficiency",
            "supported": False,
            "reason": "simultaneous branch telemetry, hydraulic work, condenser heat rejection, and chiller power are absent",
        },
        {
            "claim": "the local bubble force is universal simulated gravity for arbitrary matter",
            "supported": False,
            "reason": "EHD/DEP coupling depends on charge, permittivity, phase interface, geometry, temperature, and conductivity",
        },
        {
            "claim": "PSI-9 generated detectable or useful real gravity, modified inertia, or reactionless propulsion",
            "supported": False,
            "reason": (
                "ordinary electromagnetic and thermal forces close through electrodes, "
                "fluid, supports, supplies, and vehicle; ordinary field energy does "
                "source genuine but negligible GR curvature"
            ),
        },
    ]


def p023_gates() -> dict[str, dict[str, str]]:
    return {
        "1_source_coupling": _gate(
            "passed",
            "DC electrodes, heterocharge Coulomb pumping, permittivity-gradient "
            "DEP, electrode/support reaction, and heater/chiller energy channels "
            "are identified; measured system-energy closure is not claimed",
        ),
        "2_constraints_validity": _gate(
            "partial",
            "ordinary continuum electromechanics is applicable at device scale, "
            "but breakdown, field-enhanced dissociation, temperature-dependent "
            "properties, capillarity, transient flight, and hardware changes limit transfer",
        ),
        "3_absolute_scale": _gate(
            "passed",
            "reported/model-derived 50 Pa pressure, 5.5e-7 N bubble DEP force, "
            "27.3% transient-flight dryout and 60.1% ground CHF gains are meaningful "
            "for this small thermal device; useful-curvature and universal-loading scales fail",
        ),
        "4_falsification": _gate(
            "partial",
            "baseline/EHD/DEP/combined controls and thermal observables were executed, "
            "but direct force/flow/reaction, closed energy, and steady-microgravity "
            "measurements remain required for mechanism and scale-up qualification",
        ),
    }


def falsification_design() -> dict[str, Any]:
    return {
        "hardware_action_authorized": False,
        "frozen_geometry": (
            "repeat the published 254 um EHD gap, 1.6 mm DEP-heater gap, "
            "2 mm HFE-7100 film, and four electrical states before changing geometry"
        ),
        "measurements": [
            "differential pump pressure and liquid flow rate for hydraulic power",
            "calibrated PIV or equivalent velocity field plus interferometric film height",
            "bubble radius, contact radius, trajectory, acceleration, and coalescence",
            "field-map validation or released geometry/mesh with uncertainty",
            "six-axis electrode/chamber reaction force synchronized to voltage and current",
            "heater power and condenser coolant mass flow, inlet/outlet temperature, and chiller power",
        ],
        "controls": [
            "baseline, EHD only, DEP only, and combined states",
            "no-heat, subcooled/no-boil, nucleate-boiling, and near-dryout states",
            "voltage magnitude and polarity scans separating V-squared DEP from directional EHD pumping",
            "a separate DEP-only small-signal frequency diagnostic around the conditional 31 Hz Maxwell-Wagner scale, not a like-for-like DC EHD repetition",
            "matched gravity segments or a steady microgravity platform",
            "temperature, conductivity, dissolved gas, contamination, vibration, and acceleration histories",
        ],
        "closure_equations": {
            "fluid_control_volume_momentum": (
                "dP_fluid/dt = surface_integral[(-p*I + tau)*n]dA + "
                "integral(rho*g_effective)dV + either integral(f_electric)dV "
                "or surface_integral(T_M*n)dA within combined uncertainty; "
                "never include both electrical representations and do not add "
                "support reaction separately to this fluid control volume"
            ),
            "sealed_cell_momentum": (
                "dP_cell/dt = F_external_support + F_external_gravity_and_aircraft "
                "+ external momentum flux within combined uncertainty; all internal "
                "EM, pressure, viscous, capillary, and phase-change tractions cancel"
            ),
            "energy": (
                "P_heater + sum(VI)_HV + P_chiller = Q_rejected + "
                "dU_system/dt + losses within combined uncertainty"
            ),
            "hydraulic_efficiency": "eta_h = delta_p * Q / sum(VI)_EHD",
        },
        "kill_rule": (
            "do not recommend scale-up unless pressure, flow, electrode/support "
            "reaction, and energy residuals close within combined uncertainty, "
            "the thermal gain survives steady microgravity, and each dominant "
            "capillary, thermal, vibration, and electrochemical confounder is below "
            "one tenth of the attributed signal"
        ),
    }


def portfolio_refresh() -> list[dict[str, Any]]:
    """Distinct replacement screen; detailed source notes live in the ledgers."""
    return [
        {
            "id": "P-023",
            "category": "electrohydrodynamic_simulated_gravity_fluid_control",
            "gates": p023_gates(),
            "disposition": "deepened_retain_device_scale_thermal_analog_only",
        },
        {
            "id": "P-027",
            "category": "nanofabricated_mutual_newtonian_gravity_precision_test",
            "primary_source": "10.1103/mnrd-3bm2",
            "absolute_scale": {
                "tungsten_mass_each_kg": 0.032,
                "center_separation_m": 0.030,
                "newtonian_force_n": 7.59e-11,
                "newtonian_acceleration_m_s2": 2.37e-9,
                "projected_mode_splitting_hz": 0.7e-6,
                "projected_detection_time_h": 2.0,
                "projected_quality_factor": 1.0e6,
                "quality_factor_measured_in_vacuum": False,
            },
            "gates": {
                "1_source_coupling": _gate("passed", "ordinary mutually attracting source/test masses and torsion support are explicit"),
                "2_constraints_validity": _gate("partial", "weak-field Newtonian theory applies, but the projected vacuum Q was not measured and electrostatic, tilt, thermal, and vibration backgrounds need same-frequency bounds"),
                "3_absolute_scale": _gate("passed", "two 32 g masses at 30 mm give 7.6e-11 N and a projected 0.7 microhertz mode split; this is metrology scale and fails as artificial gravity"),
                "4_falsification": _gate("partial", "source modulation and geometry reversal are concrete; full same-harmonic budget needs audit"),
            },
            "disposition": "retain_real_gravity_precision_calibration_only",
        },
        {
            "id": "P-028",
            "category": "earth_sourced_axion_gradient_polarization_interferometry",
            "primary_source": "10.1103/PhysRevD.109.015025",
            "absolute_scale": {
                "current_limit_benchmark_finesse": 1.0e4,
                "current_limit_benchmark_arm_m": 1.0,
                "current_limit_benchmark_phase_rad": 6.0e-12,
                "projected_rf_power_w": 1.0e6,
                "projected_integration_days": 300,
                "projected_product_coupling_improvement_up_to": 1.0e5,
                "projected_mass_ceiling_ev": 4.0e-11,
            },
            "gates": {
                "1_source_coupling": _gate("partial", "Earth source and axion-photon coupling are specified, but the hypothetical field is not controllable"),
                "2_constraints_validity": _gate("partial", "allowed mass-coupling range and geophysical source model need a current overlay"),
                "3_absolute_scale": _gate("partial", "the current-limit benchmark phase is about 6e-12 rad for finesse 1e4 and 1 m, while stronger reach is projection-only and provides no bulk acceleration"),
                "4_falsification": _gate("passed", "helicity, orientation, sidereal, and null-channel reversals are concrete"),
            },
            "disposition": "candidate_next_product_constraint_and_noise_audit",
        },
        {
            "id": "P-029",
            "category": "digital_quantum_cosmological_particle_creation_analog",
            "primary_source": "10.1038/s41598-025-87015-6",
            "absolute_scale": {
                "qubits": 4,
                "two_qubit_gates_per_observable": 96,
                "one_qubit_gates_per_observable": 226,
                "estimated_raw_observable_error": 0.52,
            },
            "gates": {
                "1_source_coupling": _gate("passed", "qubit gates emulate a time-dependent mode Hamiltonian and hardware carries all reaction"),
                "2_constraints_validity": _gate("partial", "mapping is valid only for the encoded finite-dimensional dynamics and device noise"),
                "3_absolute_scale": _gate("passed", "four-qubit populations are measurable, although the raw observable error is about 52 percent; real curvature scale fails by construction"),
                "4_falsification": _gate("partial", "analytic occupations and no-expansion circuits are concrete, but public reproducibility and scaling artifacts are limited"),
            },
            "disposition": "retain_analog_dynamics_only",
        },
        {
            "id": "P-030",
            "category": "common_propellant_chemical_electrospray_external_reaction_propulsion",
            "primary_source": "NASA NTRS 20250008918 and 20240007811",
            "absolute_scale": {
                "chemical_thrust_n": 0.1,
                "chemical_specific_impulse_s": 215.0,
                "electrospray_total_thrust_n": [20e-6, 80e-6],
                "electrospray_specific_impulse_s": [1800.0, 2800.0],
            },
            "gates": {
                "1_source_coupling": _gate("passed", "propellant exhaust carries momentum in both operating modes"),
                "2_constraints_validity": _gate("partial", "chemistry, feed sharing, lifetime, plume, and mode-switching remain engineering limits"),
                "3_absolute_scale": _gate("passed", "0.1 N chemical and 20-80 microN electrospray thrust are spacecraft-relevant external-reaction scales but fail as internal gravity"),
                "4_falsification": _gate("passed", "thrust, mass flow, orbit change, refill, plume, and mode telemetry define direct tests, with flight execution pending"),
            },
            "disposition": "retain_conventional_propulsion_engineering_only",
        },
        {
            "id": "P-031",
            "category": "high_frequency_spacetime_fluctuation_interferometry",
            "primary_sources": [
                "10.1103/PhysRevX.15.011034",
                "arXiv:2410.09175",
            ],
            "absolute_scale": {
                "gquest_arm_m": 5.0,
                "gquest_circulating_power_w": 1.0e4,
                "gquest_peak_displacement_asd_m_sqrt_hz": 3.0e-22,
                "gquest_peak_frequency_hz": 17.6e6,
                "gquest_projected_five_sigma_time_s": 1.0e5,
                "quest_measured_strain_asd_sqrt_hz": 3.0e-20,
                "quest_reference_frequency_hz": 40.0e6,
            },
            "gates": {
                "1_source_coupling": _gate("unknown", "interferometer response is explicit but the stochastic spacetime source is ambient, hypothetical, and not an actuator"),
                "2_constraints_validity": _gate("partial", "model spectra and detector transfer/noise assumptions require one-convention audit"),
                "3_absolute_scale": _gate("passed", "the 5 m design targets 3e-22 m/sqrt(Hz) at 17.6 MHz and QUEST measured about 3e-20 strain/sqrt(Hz) at 40 MHz; generation fails"),
                "4_falsification": _gate("passed", "twin-interferometer correlation, angle, spectrum, dark-count, carrier-leakage, and injection controls are explicit"),
            },
            "disposition": "retain_precision_spacetime_watch_not_generation",
        },
    ]


def survival_rule_evaluation() -> dict[str, Any]:
    return {
        "device_scale_force_anchor_recovered": True,
        "device_scale_thermal_performance_recovered": True,
        "direct_volume_force_measurement_recovered": False,
        "hydraulic_efficiency_recovered": False,
        "whole_system_energy_efficiency_recovered": False,
        "steady_microgravity_chf_recovered": False,
        "useful_universal_acceleration": False,
        "ordinary_em_field_energy_sources_real_curvature": True,
        "useful_engineered_spacetime_curvature": False,
        "inertial_control_or_reactionless_propulsion": False,
        "disposition": "retain_device_scale_thermal_analog_force_and_scaleup_partial",
        "reopen_or_deepen_condition": (
            "direct pressure-flow-force and closed thermal/electrical data in "
            "steady microgravity, or materially new primary evidence"
        ),
    }


def run_analysis() -> dict[str, Any]:
    decision = survival_rule_evaluation()
    return {
        "provenance": implementation_provenance(),
        "field_and_pressure": field_and_pressure_audit(),
        "electromechanics_and_thermal_confounders": (
            electromechanics_and_thermal_confounder_audit()
        ),
        "bubble_force": bubble_force_audit(),
        "thermal_performance": thermal_performance_audit(),
        "real_curvature_field_energy_screen": real_curvature_field_energy_screen(),
        "reaction_and_energy_ledger": reaction_and_energy_ledger(),
        "claim_kill_matrix": claim_kill_matrix(),
        "gates": p023_gates(),
        "falsification_design": falsification_design(),
        "portfolio_refresh": portfolio_refresh(),
        "decision": {
            "status": decision["disposition"],
            "survived_as_device_scale_spacecraft_fluid_opportunity": True,
            "survived_as_useful_universal_or_curvature_gravity": False,
            "standard_gr_curvature_from_field_energy_exists_but_is_negligible": True,
            "mechanism_and_scaleup_fully_qualified": False,
            "category_boundary": (
                "electromagnetic control of a specified dielectric liquid and "
                "vapor interface, not universal free fall, curvature, or inertia control"
            ),
            "next_best_step": (
                "run E-044 as a no-hardware P-028 product-constraint and detector-"
                "noise audit: update both couplings in one convention, recompute "
                "the allowed helicity phase, and require measured birefringence, "
                "thermal, and mechanical backgrounds below one tenth"
            ),
        },
        "resource_accounting": {
            "pde_builds": 0,
            "pde_solves": 0,
            "comsol_reconstructions": 0,
            "hardware_actions": 0,
            "checkpoint_state_loads_for_research": 0,
            "checkpoint_writes": 0,
            "compute_expansion": 0,
        },
    }


def _write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-json",
        type=Path,
        help="optional path for the deterministic JSON audit report",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = run_analysis()
    if args.report_json is not None:
        _write_report(args.report_json, report)
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

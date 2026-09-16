"""E-044: conditional sourced-ALP phase and optical qualification audit.

Analytic, no PDE/checkpoint access. The scalar couples ONLY to baryon number;
no dark-matter abundance is assumed. Constraint products below are scenario
ceilings, not a joint-confidence region, detection forecast, or device claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

AUDIT_DATE = "2026-09-16"
HBAR_C_EV_M = 1.973269804e-7
C_M_S = 299792458.0
H_J_S = 6.62607015e-34
EV_J = 1.602176634e-19
G_SI = 6.67430e-11
U_KG = 1.66053906892e-27
EARTH_MASS_KG = 5.9722e24
EARTH_RADIUS_M = 6371000.0
EARTH_ROTATION_RAD_S = 7.2921150e-5
FINESSE = 1.0e4
LENGTH_M = 1.0
HEIGHT_M = 0.1
WAVELENGTH_M = 1064e-9
CIRCULATING_POWER_W = 1.0e6
INTEGRATION_S = 300.0 * 86400.0
LONG_RANGE_MAX_EV = 1.0e-14
LONG_RANGE_G_B = 6.6e-25  # conservative envelope, not massless Table 6 value
PULSAR_PRODUCT_ANCHOR_GEV_INVERSE = 8e-39

# Fayet 2025 Table 6: spin ZERO, baryon-only, 95% CL. These are sparse
# MICROSCOPE-only limits, NOT the full allowed coupling envelope.
MICROSCOPE_TABLE = (
    (0.0, 6.4e-25), (1e-14, 6.6e-25), (2e-14, 6.9e-25),
    (5e-14, 8.5e-25), (1e-13, 1.21e-24), (2e-13, 2.11e-24),
    (5e-13, 6.1e-24), (1e-12, 2.17e-23), (2e-12, 1.89e-22),
    (5e-12, 6.8e-20), (1e-11, 8e-16),
)
PHOTON_SCENARIOS = {
    "cluster_model": {
        "g_gev_inverse": 6.3e-13,
        "source": "10.1093/mnras/stab3464",
        "confidence": "99.7% Bayesian credibility, beta=100 cluster model",
        "scope": "author light-mass limiting extension; used only at m<=1e-14 eV",
    },
    "solar_helioscope": {
        "g_gev_inverse": 5.8e-11,
        "source": "10.1103/PhysRevLett.133.221005",
        "confidence": "95% CL, solar Primakoff production model",
        "scope": "CAST m approximately below 0.02 eV; not laboratory-only",
    },
    "laboratory_only": {
        "g_gev_inverse": 1.5e-9,
        "source": "arXiv:2512.14110v3",
        "confidence": "95% CL, ALPS II light shining through a wall",
        "scope": "m approximately below 0.1 meV; no astrophysical source required",
    },
}
# Same units alone do not authorize transfer between these observables.
MEASURED_NOISE_COMPARATORS = (
    {"source": "10.1103/r33m-v1kn", "observable": "linear-polarization equivalent single-pass length",
     "frequency_hz": 0.003, "asd_m_sqrt_hz": 4e-14, "duration_h": 20.0,
     "configuration": "19m three-frequency cavity", "same_magpi_observable": False},
    {"source": "10.1103/r33m-v1kn", "observable": "linear-polarization equivalent single-pass length",
     "frequency_hz": 0.003, "asd_m_sqrt_hz": 1.3e-13, "duration_h": 15.0,
     "configuration": "rotating half-wave plate; not whole-cavity rotation", "same_magpi_observable": False},
)
REQUIRED_BACKGROUNDS = (
    "birefringence_and_polarization_mixing", "differential_thermal_length",
    "coating_noise", "mechanical_pointing_and_stress", "magnetic_response",
    "spin_rotation_and_geometric_phase", "rotation_synchronous_pickup",
)


def _nonnegative(name: str, value: float) -> None:
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")


def _positive(name: str, value: float) -> None:
    _nonnegative(name, value)
    if value == 0:
        raise ValueError(f"{name} must be positive")


def surface_form_factor(y: float) -> float:
    """e^-y * 3(y cosh y - sinh y)/y^3, cancellation/overflow safe."""
    _nonnegative("mR", y)
    if y < 0.05:
        # Taylor of the unscaled uniform-volume average sinh(yu)/(yu).
        unscaled = 1 + y*y/10 + y**4/280 + y**6/15120 + y**8/1330560
        return math.exp(-y) * unscaled
    # Written in inverse powers to avoid overflow even for large finite y.
    inv = 1 / y
    return 1.5 * inv * inv * ((1-inv) + (1+inv)*math.exp(-2*y))


def field_difference_ev(mass_ev: float, g_b: float, *, radius_m: float = EARTH_RADIUS_M,
                        source_mass_kg: float = EARTH_MASS_KG,
                        height_m: float = HEIGHT_M, length_m: float = LENGTH_M) -> float:
    """Magnitude |phi(lower)-phi(upper)| outside a homogeneous baryon sphere.

    Free canonical scalar, g_L=g_(B-L)=0, Q_B=M/u, static weak source.
    Baryon-to-mass and interior-composition corrections are not precision fitted.
    Uses the exact exterior Yukawa solution and stable endpoint subtraction.
    """
    for name, value in (("mass", mass_ev), ("g_b magnitude", g_b), ("height", height_m)):
        _nonnegative(name, value)
    for name, value in (("radius", radius_m), ("source mass", source_mass_kg), ("length", length_m)):
        _positive(name, value)
    q = mass_ev / HBAR_C_EV_M
    r = radius_m + height_m
    endpoint = (length_m/r - math.expm1(-q*length_m)) / (r+length_m)
    return (g_b * source_mass_kg/U_KG * HBAR_C_EV_M/(4*math.pi)
            * surface_form_factor(q*radius_m) * math.exp(-q*height_m) * endpoint)


def phase_rad(mass_ev: float, g_b: float, g_gamma_gev_inverse: float,
              *, finesse: float = FINESSE, **source_geometry: float) -> float:
    """Magnitude of opposite-helicity, single-ended REFLECTED cavity phase."""
    _positive("finesse", finesse)
    _nonnegative("photon coupling magnitude", g_gamma_gev_inverse)
    return (4*finesse/math.pi * g_gamma_gev_inverse*1e-9
            * field_difference_ev(mass_ev, g_b, **source_geometry))


def source_model_sensitivity() -> dict:
    """Reproduce a uniform versus five-full-sphere source comparison.

    Fayet arXiv:2507.02723v2 Table 3 / Eqs73-80 supplies the radii,
    excess densities and rounded mass fractions. Use its kilometre radii
    and rounded mass fractions, whose sum is one, with this audit's total
    Earth mass. The separately rounded published densities are provenance
    inputs, not another normalization. Baryon charge is M/u in both models.
    Every sphere uses the same exterior detector endpoints. Unit coupling
    extracts a transfer coefficient only, not a physical parameter point.
    This is a model comparison, not a certified density uncertainty bound.
    """
    radii_km = (6371.0, 6341.0, 5701.0, 3480.0, 1221.0)
    weights = (0.5, 0.1333, 0.1715, 0.1929, 0.0023)
    density_increments = (2.755, 0.745, 1.319, 6.522, 1.8)
    lower = EARTH_RADIUS_M + HEIGHT_M
    spheres = [
        {"radius_m": radius*1000, "mass_fraction": weight,
         "published_excess_density_g_cm3": density,
         "normalized_excess_density_kg_m3":
             weight*EARTH_MASS_KG/(4*math.pi/3*(radius*1000)**3)}
        for radius, weight, density in zip(radii_km, weights, density_increments)]
    comparisons = []
    for mass in (0.0, 1e-15, 1e-14, 1e-13, 1e-12, 1e-11):
        uniform = field_difference_ev(mass, 1.0)
        layered = math.fsum(field_difference_ev(
            mass, 1.0, radius_m=sphere["radius_m"],
            source_mass_kg=EARTH_MASS_KG*sphere["mass_fraction"],
            height_m=lower-sphere["radius_m"], length_m=LENGTH_M)
            for sphere in spheres)
        ratio = layered/uniform
        comparisons.append({"mass_ev": mass,
                            "uniform_field_difference_per_unit_g_b_ev": uniform,
                            "five_sphere_field_difference_per_unit_g_b_ev": layered,
                            "five_sphere_to_uniform_ratio": ratio,
                            "relative_change_percent": 100*(ratio-1)})
    return {"source": "arXiv:2507.02723v2 Table 3 and Eqs73-80",
            "construction": "superposed full spheres; mass fractions are not disjoint shell masses",
            "normalization": "published rounded mass fractions at common fixed total Earth mass; B/m=1/u",
            "total_source_mass_kg": EARTH_MASS_KG,
            "earth_radius_m": EARTH_RADIUS_M,
            "lower_endpoint_from_center_m": lower,
            "upper_endpoint_from_center_m": lower+LENGTH_M,
            "full_spheres": spheres,
            "comparisons": comparisons,
            "is_certified_uncertainty_bound": False,
            "is_current_allowed_signal_envelope": False}


def long_range_scenario(mass_ev: float, scenario: str) -> dict:
    """Reject extending the audited joint-scope comparison beyond its mass band."""
    _nonnegative("mass", mass_ev)
    photon = PHOTON_SCENARIOS[scenario]
    if mass_ev > LONG_RANGE_MAX_EV:
        return {"mass_ev": mass_ev, "scenario": scenario, "phase_ceiling_rad": None,
                "qualified_joint_confidence": None,
                "status": "outside_audited_combined_scope"}
    return {"mass_ev": mass_ev, "scenario": scenario,
            "g_b_envelope": LONG_RANGE_G_B, **photon,
            "product_gev_inverse": LONG_RANGE_G_B * photon["g_gev_inverse"],
            "phase_ceiling_rad": phase_rad(mass_ev, LONG_RANGE_G_B, photon["g_gev_inverse"]),
            "includes_direct_pulsar_product_constraint": False,
            "qualified_joint_confidence": None,
            "status": "conditional_ceiling_not_joint_confidence_or_detection"}


def pulsar_product_scenario(mass_ev: float) -> dict:
    """Approximate PRESENT interpulse constraint, not an independent g_B bound.

    Witte et al. arXiv:2512.11023v2 Appendix B Eqs19-20. The source states
    m roughly below 1e-12 eV; this audit conservatively uses its own <=1e-14
    band. The stronger death-line curve has no recovered numerical table.
    Eq22's 2e-39 is prospective, requiring an unverified sign/geometry test.
    Unit couplings below merely extract the linear product transfer; they
    are not a physical point or a claim about separate coupling strengths.
    """
    _nonnegative("mass", mass_ev)
    if mass_ev > LONG_RANGE_MAX_EV:
        return {"mass_ev": mass_ev, "phase_ceiling_rad": None,
                "confidence": None, "status": "outside_audited_pulsar_scope"}
    return {"mass_ev": mass_ev,
            "product_gev_inverse": PULSAR_PRODUCT_ANCHOR_GEV_INVERSE,
            "phase_ceiling_rad": phase_rad(mass_ev, 1.0, PULSAR_PRODUCT_ANCHOR_GEV_INVERSE),
            "source": "arXiv:2512.11023v2 Appendix B Eqs19-20; arXiv:2609.08840v1",
            "confidence": None,
            "source_mass_scope_ev_approx": 1e-12,
            "assumptions": "APR 1-solar-mass scalar source, dipolar return-current geometry, near-surface radio pair cascades",
            "dark_matter_or_qcd_mass_relation_required": False,
            "stronger_death_line_numerical_curve_recovered": False,
            "prospective_eq22_used": False,
            "status": "approximate_pulsar_model_anchor_not_global_envelope"}


def length_equivalent_m(phase: float, *, wavelength_m: float = WAVELENGTH_M,
                        finesse: float = FINESSE) -> float:
    _nonnegative("phase", phase)
    _positive("wavelength", wavelength_m)
    _positive("finesse", finesse)
    return phase / ((4*finesse/math.pi)*(2*math.pi/wavelength_m))


def photon_counting_budget(*, power_w: float = CIRCULATING_POWER_W,
                           time_s: float = INTEGRATION_S,
                           wavelength_m: float = WAVELENGTH_M,
                           finesse: float = FINESSE) -> dict:
    """Declared one-channel count normalization; proposal Eq10 differs by 2.

    P0=pi*Pcav/(2F), sigma=1/sqrt(N). Optical incident energy is not electrical,
    cryogenic or total facility energy. No duty-cycle or technical-noise claim.
    """
    for name, value in (("power", power_w), ("time", time_s),
                        ("wavelength", wavelength_m), ("finesse", finesse)):
        _positive(name, value)
    p0 = math.pi*power_w/(2*finesse)
    e = H_J_S*C_M_S/wavelength_m
    sigma = math.sqrt(e/(p0*time_s))
    return {"circulating_power_w": power_w, "time_s": time_s,
            "incident_power_w": p0, "incident_optical_energy_j": p0*time_s,
            "photon_energy_j": e, "counting_sigma_rad": sigma,
            "full_rotation_peak_counting_sigma_rad": math.sqrt(2)*sigma,
            "proposal_eq10_sigma_rad": sigma/2,
            "template_convention": "counting_sigma is constant-phase; peak sinusoid uses time/2 effective exposure",
            "resource_tuple_demonstrated": False}


def two_color_budget(frequency_ratio: float, *, power_w: float = CIRCULATING_POWER_W,
                     time_s: float = INTEGRATION_S) -> dict:
    """A+k_i L nuisance removal, same calibrated F, independent shot counts.

    Ratio is nu2/nu1>1. Fixed TOTAL circulating power is allocated optimally
    across colors. Arbitrary dispersive coating terms and achromatic rotation
    are NOT removed. This is an ideal estimator, not demonstrated subtraction.
    """
    _positive("frequency ratio", frequency_ratio)
    if frequency_ratio <= 1:
        raise ValueError("distinct increasing optical frequencies required")
    w1 = frequency_ratio/(frequency_ratio-1)
    w2 = -1/(frequency_ratio-1)
    term1, term2 = w1, abs(w2)*math.sqrt(frequency_ratio)
    budget = photon_counting_budget(power_w=power_w, time_s=time_s)
    return {"frequency_ratio": frequency_ratio, "weights": [w1, w2],
            "equal_independent_phase_noise_penalty": math.hypot(w1, w2),
            "optimal_power_fraction_low_frequency": term1/(term1+term2),
            "fixed_total_power_counting_penalty": term1+term2,
            "optimal_counting_sigma_rad": (term1+term2)*budget["counting_sigma_rad"],
            "full_rotation_peak_counting_sigma_rad": math.sqrt(2)*(term1+term2)*budget["counting_sigma_rad"],
            "assumptions": "two independent photon-count channels, exact gains, one common length nuisance",
            "rejects_achromatic_rotation": False}


def spin_rotation_phase_rad(omega_parallel_rad_s: float, *, convention_factor: float = 1.0,
                            finesse: float = FINESSE, length_m: float = LENGTH_M) -> float:
    """Nominal PRA2025 Eq4 scale; factor=2 is reflected-MAGPI rederivation.

    The factors 1 and 2 are sensitivity examples, NOT a rigorously bounded
    interval for an unbuilt instrument. Its angular transfer must be calibrated.
    """
    if not math.isfinite(omega_parallel_rad_s):
        raise ValueError("angular rate must be finite")
    for name, value in (("factor", convention_factor), ("finesse", finesse), ("length", length_m)):
        _positive(name, value)
    return convention_factor*4*finesse/math.pi*length_m/C_M_S*omega_parallel_rad_s


def rotation_budget(signal_phase: float, latitude_deg: float = 45.0,
                    modulation_hz: float = 0.003) -> list[dict]:
    _positive("signal phase", signal_phase)
    if not math.isfinite(latitude_deg) or abs(latitude_deg) > 90:
        raise ValueError("latitude must be within +/-90 degrees")
    _positive("modulation frequency", modulation_hz)
    out = []
    lat = math.radians(latitude_deg)
    for factor in (1.0, 2.0):
        transfer = spin_rotation_phase_rad(1.0, convention_factor=factor)
        equivalent = signal_phase/transfer
        vertical = transfer*EARTH_ROTATION_RAD_S*math.sin(lat)
        out.append({"convention_factor": factor, "latitude_deg": latitude_deg,
                    "earth_vertical_phase_rad": vertical,
                    "earth_vertical_to_signal_ratio": abs(vertical)/signal_phase,
                    "signal_equivalent_axial_rate_rad_s": equivalent,
                    "max_coherent_axial_rate_residual_rad_s": 0.1*equivalent,
                    "modulation_hz": modulation_hz,
                    "small_axial_wobble_tolerance_rad": 0.1*equivalent/(2*math.pi*modulation_hz),
                    "null_axis_ideal_signal_fraction": math.cos(lat),
                    "null_axis_measured_rejection": None})
    return out


def orientation_projection(phase_angle_rad: float, latitude_deg: float) -> dict:
    """Ideal n rotates perpendicular to Earth's spin axis in local N,E,U.

    Rotor axis a=(cos(lat),0,sin(lat)); n0=(-sin(lat),0,cos(lat));
    n=n0*cos(theta)+E*sin(theta). Both Earth and deliberate axial rotation
    have a.n=0. Does not include flexure, finite aperture, or optical phases.
    """
    if not math.isfinite(phase_angle_rad) or not math.isfinite(latitude_deg) or abs(latitude_deg)>90:
        raise ValueError("finite angle and physical latitude required")
    lat = math.radians(latitude_deg)
    a = (math.cos(lat), 0.0, math.sin(lat))
    n = (-math.sin(lat)*math.cos(phase_angle_rad), math.sin(phase_angle_rad),
         math.cos(lat)*math.cos(phase_angle_rad))
    return {"axis": a, "cavity_direction": n,
            "axis_dot_cavity": sum(x*y for x,y in zip(a,n)), "vertical_projection": n[2]}


def massless_physical_scales() -> dict:
    """Conditional B-only Earth force and local scalar-gradient energy scales.

    Assumes both source and neutral test body's B/m=1/u. Curvature is only
    the dimensional Einstein-equation scale 8*pi*G*u/c^4, not a solved metric.
    The whole Earth is the source; this is not a laboratory actuator.
    """
    grad = (LONG_RANGE_G_B * EARTH_MASS_KG/U_KG * HBAR_C_EV_M**2
            / (4*math.pi*EARTH_RADIUS_M**2))
    u_ev = U_KG*C_M_S**2/EV_J
    acceleration = C_M_S**2 * LONG_RANGE_G_B*grad/(u_ev*HBAR_C_EV_M)
    energy_density = 0.5*grad**2 * EV_J/HBAR_C_EV_M**3
    return {"field_gradient_ev2": grad, "test_body_baryons_per_kg": 1/U_KG,
            "conditional_fifth_force_acceleration_m_s2": acceleration,
            "conditional_force_on_70kg_n": 70*acceleration,
            "local_gradient_energy_j_m3": energy_density,
            "dimensional_curvature_source_scale_m_inverse2": 8*math.pi*G_SI*energy_density/C_M_S**4,
            "ordinary_earth_acceleration_m_s2": G_SI*EARTH_MASS_KG/EARTH_RADIUS_M**2,
            "local_gradient_energy_is_full_apparatus_energy": False,
            "is_measured_or_controllable_source": False}


def qualification(signal_phase: float, measured_sigma_rad: float | None,
                  coherent_background_bounds: dict[str, float | None], *,
                  same_observable_and_resources_verified: bool = False,
                  transfer_and_template_verified: bool = False) -> dict:
    """Unknown is not zero; caller must verify linked measurement provenance.

    Numerical inputs alone cannot attest a matched instrument or transfer.
    These mandatory opt-in attestations are not evidence generated by code.
    """
    _positive("signal phase", signal_phase)
    if measured_sigma_rad is not None:
        _nonnegative("measured sigma", measured_sigma_rad)
    missing, failing = [], []
    for name in REQUIRED_BACKGROUNDS:
        bound = coherent_background_bounds.get(name)
        if bound is None:
            missing.append(name)
        else:
            _nonnegative(name, bound)
            if bound >= 0.1*signal_phase:
                failing.append(name)
    passed = (same_observable_and_resources_verified is True
              and transfer_and_template_verified is True
              and measured_sigma_rad is not None and measured_sigma_rad <= signal_phase
              and not missing and not failing)
    return {"qualified": passed, "same_observable_measured_sigma_rad": measured_sigma_rad,
            "same_observable_and_resources_verified": same_observable_and_resources_verified,
            "transfer_and_template_verified": transfer_and_template_verified,
            "missing_backgrounds": missing, "failing_backgrounds": failing,
            "status": "qualified_precision_test_only" if passed else "parked_no_measured_helicity_noise_and_rotation_budget"}


def report() -> dict:
    signal = long_range_scenario(0.0, "cluster_model")["phase_ceiling_rad"]
    leq = length_equivalent_m(signal)
    counting = photon_counting_budget()
    adjacent_ratio = 1 + WAVELENGTH_M/(2*LENGTH_M)
    colored = {"adjacent_longitudinal_modes": two_color_budget(adjacent_ratio),
               "octave_separated_modes": two_color_budget(2.0)}
    for budget in colored.values():
        budget["conditional_ceiling_to_ideal_sigma"] = signal/budget["optimal_counting_sigma_rad"]
        budget["full_rotation_peak_ideal_snr"] = signal/budget["full_rotation_peak_counting_sigma_rad"]
    pulsar_signal = pulsar_product_scenario(0.0)["phase_ceiling_rad"]
    pulsar_leq = length_equivalent_m(pulsar_signal)
    pulsar_snr = {name: pulsar_signal/budget["full_rotation_peak_counting_sigma_rad"]
                  for name, budget in colored.items()}
    module = Path(__file__)
    return {
        "campaign": "E-044", "audit_date": AUDIT_DATE,
        "module_sha256": hashlib.sha256(module.read_bytes()).hexdigest(),
        "category": "hypothetical baryon-sourced new-interaction precision test",
        "model": {"source": "homogeneous Earth; baryon charge M/u", "radius_m": EARTH_RADIUS_M,
                  "mass_kg": EARTH_MASS_KG, "lower_height_m": HEIGHT_M, "length_m": LENGTH_M,
                  "finesse": FINESSE, "wavelength_m": WAVELENGTH_M,
                  "g_L": 0, "g_B_minus_L": 0, "dark_matter_assumed": False,
                  "source_geometry_is_certified_earth_model": False},
        "long_range_scenarios": [long_range_scenario(m, s) for m in (0.0,1e-15,1e-14)
                                  for s in PHOTON_SCENARIOS],
        "pulsar_direct_product": [pulsar_product_scenario(m) for m in (0.0,1e-15,1e-14)],
        "pulsar_budget": {
            "reference": "approximate present interpulse anchor; stronger death-line curve not tabulated",
            "conditional_signal_rad": pulsar_signal,
            "cluster_comparison_to_pulsar_phase_ratio": signal/pulsar_signal,
            "full_rotation_peak_ideal_snr": pulsar_snr,
            "octave_earth_axis_null_45deg_ideal_snr": pulsar_snr["octave_separated_modes"]/math.sqrt(2),
            "octave_unit_peak_time_for_ideal_snr_five_s": INTEGRATION_S*(5/pulsar_snr["octave_separated_modes"])**2,
            "equivalent_differential_length_m": pulsar_leq,
            "max_coherent_length_background_m": 0.1*pulsar_leq,
            "one_sided_white_length_asd_for_snr_one_m_sqrt_hz": pulsar_leq*math.sqrt(INTEGRATION_S),
            "rotation": rotation_budget(pulsar_signal),
            "qualification": qualification(pulsar_signal,None,{})},
        "microscope_only_sparse_diagnostic": [
            {"mass_ev": m, "g_b_95cl": g,
             "source_transfer_per_unit_product_rad_gev": phase_rad(m,1.0,1.0),
             "alps_product_phase_ceiling_rad": phase_rad(m,g,1.5e-9),
             "full_allowed_region_qualified": False,
             "warning": "satellite-only scalar recast; other force bounds may be stronger"}
            for m,g in MICROSCOPE_TABLE],
        "fixed_coupling_mass_sensitivity": [
            {"mass_ev": 10.0**i, "phase_rad": phase_rad(10.0**i,LONG_RANGE_G_B,6.3e-13),
             "is_current_allowed_envelope": False} for i in range(-18,-4)],
        "counting_only": counting,
        "conditional_massless_physical_scales": massless_physical_scales(),
        "earth_source_model_sensitivity": source_model_sensitivity(),
        "two_color": colored,
        "two_color_signal_reference": "selected cluster/source comparison omits direct pulsar bound; see pulsar_budget",
        "required_residuals": {"reference": "selected cluster/source comparison omits direct pulsar bound",
                               "conditional_signal_rad": signal,
                               "equivalent_differential_length_m": leq,
                               "max_coherent_length_background_m": 0.1*leq,
                               "one_sided_white_length_asd_for_snr_one_m_sqrt_hz": leq*math.sqrt(INTEGRATION_S),
                               "white_integration_assumption_demonstrated": False},
        "measured_noise_comparators": MEASURED_NOISE_COMPARATORS,
        "rotation": rotation_budget(signal),
        "rotation_signal_reference": "selected cluster/source comparison omits direct pulsar bound; see pulsar_budget",
        "rocking": {"about_vertical_first_harmonic": 0.0,
                    "one_degree_second_harmonic_small_angle_fraction": math.radians(1)**2/4,
                    "scope": "light mass, theta small, quasi-static field; full rotation gives unsuppressed first harmonic"},
        "qualification": qualification(signal,None,{}),
        "gates": {"source_and_reaction": "passed_at_model_level",
                  "constraints_and_validity": "partial_conditional_long_range_only",
                  "absolute_scale": "partial_precision_only_no_demonstrated_joint_resource_tuple",
                  "falsification": "partial_controls_defined_residuals_unmeasured"},
        "reaction_ledger": ["Earth baryon source, scalar field, and probe exchange momentum",
                            "laser, mirrors, retarders and detector exchange energy and angular momentum",
                            "motor, bearings, support and Earth take rotation and optical reactions",
                            "circulating optical power is not exported propulsive power or stored field energy"],
        "not_established": ["ALP existence", "new acceleration control", "engineered spacetime curvature",
                            "reactionless propulsion", "a current globally allowed product envelope"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    encoded = json.dumps(report(), indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()

"""E-038 short-range B-L constraint and detector-signal audit.

This is a closed-form, no-hardware, no-PDE audit of one hypothetical new
interaction.  The convention is frozen to a canonically normalized massive
vector ``X_mu`` with

    L_int = g_X X_mu J_(B-L)^mu

and neutral-atom charge ``Q_(B-L) = N`` (neutron number).  In SI units the
static potential is

    V(r) = +g_X^2 hbar*c Q1 Q2 exp(-r/lambda)/(4*pi*r).

Like charges repel and unlike charges attract.  Momentum is exchanged between
source and detector through the vector field; supports close the laboratory
reaction ledger.  This model is a speculative fifth-force parametrization,
not evidence for a new field, artificial gravity, or inertial control.

The short-range anchors below are sparse published numerical values and
deliberately conservative reads of primary exclusion plots.  They are a
transparent screening recast, not a new combined exclusion result.  The 2026
levitated experiment is used for its measured detector architecture, while
stronger earlier laboratory constraints set the allowed signal scale.  The
Josephson calculation audits the geometry proposed by Cheng, Sheng, and
Yanagida (2025).  Its ``1e-3 rad`` threshold is a proposal-level
phase-resolution assumption, not a measured apparatus floor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


CAMPAIGN = "E-038"
HBAR = 1.054_571_817e-34
HBAR_C = 3.161_526_773_496_690_3e-26  # J m
HBAR_C_EV_UM = 0.197_326_980_4
SPEED_OF_LIGHT = 299_792_458.0
GRAVITATIONAL_CONSTANT = 6.674_30e-11
ATOMIC_MASS_UNIT = 1.660_539_066_60e-27
FINE_STRUCTURE_CONSTANT = 7.297_352_569_3e-3
ELEMENTARY_EM_COUPLING = math.sqrt(4.0 * math.pi * FINE_STRUCTURE_CONSTANT)
ELEMENTARY_CHARGE = 1.602_176_634e-19

# Final MICROSCOPE result (Touboul et al. 2022), Ti-Pt Earth-source Eotvos
# parameter, with statistical and systematic errors kept separate in source.
MICROSCOPE_ETA_CENTRAL = -1.5e-15
MICROSCOPE_ETA_STAT = 2.3e-15
MICROSCOPE_ETA_SYST = 1.5e-15
MICROSCOPE_B_MINUS_L_COEFFICIENT = 3.623e34

# Geometry proposed in Cheng, Sheng, and Yanagida (2025).
JOSEPHSON_NEUTRON_DENSITY_M3 = 6.8e29
JOSEPHSON_SOURCE_DISTANCE_M = 1.0e-6
JOSEPHSON_ELECTRODE_SEPARATION_M = 1.0e-7
JOSEPHSON_SOURCE_THICKNESS_M = 1.0e-2
JOSEPHSON_INTEGRATION_TIME_S = 60.0
JOSEPHSON_PHASE_THRESHOLD_RAD = 1.0e-3
JOSEPHSON_SOURCE_AREA_M2 = 1.0e-4

# Conservative repulsive-sign generic-Yukawa anchors from directly relevant
# laboratory literature, rather than the less constraining
# 2026 sensor-architecture paper alone.  The 5 and 20 um values are rounded
# upward from published exclusion plots / paper summaries and intentionally
# weak; 10 um is the explicit 95% abstract value from Geraci et al. (2008),
# and 48 um is the explicit |alpha|<=1 anchor from Tan et al. (2020).
# These sparse points are used only at their stated ranges: no interpolation or
# extrapolation is represented as an official global curve.
GLOBAL_REPULSIVE_ALPHA_ANCHORS = {
    5.0: {
        "abs_alpha_limit": 1.0e5,
        "source": "Chen et al. 2016 repulsive-sign exclusion plot",
        "quality": "rounded_up_plot_read_screening_anchor",
    },
    10.0: {
        "abs_alpha_limit": 1.4e4,
        "source": "Geraci et al. 2008 explicit 95-percent abstract anchor",
        "quality": "published_numeric_anchor",
    },
    20.0: {
        "abs_alpha_limit": 1.0e4,
        "source": "Chiaverini et al. 2003 conservative published-scale anchor",
        "quality": "rounded_up_paper_scale_screening_anchor",
    },
    48.0: {
        "abs_alpha_limit": 1.0,
        "source": "Tan et al. 2020 explicit abstract anchor",
        "quality": "published_numeric_anchor",
    },
}

# The newer levitated sensor is retained as the measured detector/noise
# architecture, not treated as the global exclusion envelope.
LEVITATED_REFERENCE_RANGE_UM = 10.0
LEVITATED_REFERENCE_ALPHA = 1.0e6
LEVITATED_REFERENCE_TEMPLATE_FORCE_N = 5.0e-18
LEVITATED_FORCE_SENSITIVITY_N_PER_SQRT_HZ = 1.0e-17
LEVITATED_ATTRACTOR_PEAK_TO_PEAK_M = 170.0e-6
LEVITATED_ATTRACTOR_AMPLITUDE_M = LEVITATED_ATTRACTOR_PEAK_TO_PEAK_M / 2.0
LEVITATED_DRIVE_FREQUENCY_HZ = 3.0
LEVITATED_PATTERN_PITCH_M = 25.0e-6
LEVITATED_FACE_GAP_M = 6.0e-6
LEVITATED_TARGET_DIAMETER_M = 10.0e-6

# Natural-isotope-average atomic masses and proton numbers.  The B-L charge
# fraction of a neutral atom is approximated as (A-Z)/A.
ATOMIC_COMPOSITION = {
    "Au": {"atomic_mass_u": 196.966_57, "protons": 79.0},
    "Si": {"atomic_mass_u": 28.085, "protons": 14.0},
    "O": {"atomic_mass_u": 15.999, "protons": 8.0},
}
DENSITY_KG_M3 = {"Au": 19_300.0, "Si": 2_330.0}

# A deliberately weak charge-product conversion for heterogeneous historical
# short-range experiments when their exact isotope/material response is not
# re-fit here.  Stable neutral matter has N/A roughly 0.5-0.6, so 0.25 is the
# low-end product.  The exact Au/Si-SiO2 patterned response is kept separate.
CONSERVATIVE_CONSTRAINT_MATERIAL_RESPONSE = 0.25


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def implementation_provenance() -> dict[str, Any]:
    path = Path(__file__).resolve()
    return {
        "campaign": CAMPAIGN,
        "campaign_schema": 1,
        "module": {
            "path": str(path.relative_to(path.parents[1])),
            "sha256": _sha256_file(path),
        },
        "calculation_scope": (
            "closed-form order-of-magnitude constraint/signal audit; no PDE, "
            "new fit, hardware actuation, or experimental data generation"
        ),
    }


def _gate(status: str, statement: str) -> dict[str, str]:
    if status not in {"passed", "partial", "failed", "unknown"}:
        raise ValueError(f"invalid gate status: {status}")
    return {"status": status, "statement": statement}


def neutron_fraction(element: str) -> float:
    composition = ATOMIC_COMPOSITION[element]
    return (
        composition["atomic_mass_u"] - composition["protons"]
    ) / composition["atomic_mass_u"]


def silica_neutron_fraction() -> float:
    silicon = ATOMIC_COMPOSITION["Si"]
    oxygen = ATOMIC_COMPOSITION["O"]
    neutrons = (
        silicon["atomic_mass_u"]
        - silicon["protons"]
        + 2.0 * (oxygen["atomic_mass_u"] - oxygen["protons"])
    )
    mass = silicon["atomic_mass_u"] + 2.0 * oxygen["atomic_mass_u"]
    return neutrons / mass


def au_si_silica_response_factor() -> float:
    """Map pure-neutron Yukawa strength to the Au/Si-SiO2 mass template.

    The optomechanical experiment fits a mass-coupled generic Yukawa force.
    Its patterned source contrast is proportional to ``rho_Au-rho_Si``.  A
    B-L vector instead weights each material by its neutron/mass fraction, and
    the silica target contributes a further neutron/mass factor.
    """

    source_ratio = (
        DENSITY_KG_M3["Au"] * neutron_fraction("Au")
        - DENSITY_KG_M3["Si"] * neutron_fraction("Si")
    ) / (DENSITY_KG_M3["Au"] - DENSITY_KG_M3["Si"])
    return silica_neutron_fraction() * source_ratio


def pure_neutron_alpha_per_g_squared() -> float:
    """Return alpha_N/g_X^2 relative to Newtonian gravity for neutrons."""

    return HBAR_C / (
        4.0 * math.pi * GRAVITATIONAL_CONSTANT * ATOMIC_MASS_UNIT**2
    )


def g_from_generic_alpha(alpha: float, response_factor: float) -> float:
    if alpha < 0.0 or response_factor <= 0.0:
        raise ValueError("alpha must be nonnegative and response positive")
    return math.sqrt(
        alpha / (pure_neutron_alpha_per_g_squared() * response_factor)
    )


def mass_ev_from_range_um(range_um: float) -> float:
    if range_um <= 0.0:
        raise ValueError("range must be positive")
    return HBAR_C_EV_UM / range_um


def josephson_phase(
    coupling_g: float,
    range_m: float,
    *,
    neutron_density_m3: float = JOSEPHSON_NEUTRON_DENSITY_M3,
    source_distance_m: float = JOSEPHSON_SOURCE_DISTANCE_M,
    electrode_separation_m: float = JOSEPHSON_ELECTRODE_SEPARATION_M,
    source_thickness_m: float = JOSEPHSON_SOURCE_THICKNESS_M,
    integration_time_s: float = JOSEPHSON_INTEGRATION_TIME_S,
) -> float:
    """Return the canonical B-L phase difference for an infinite slab.

    The Cooper pair has ``|Q_(B-L)|=2``.  Integrating the canonical Yukawa
    potential over the slab cancels the explicit factor of two and gives

      Delta phi = g_X^2 c n lambda^2 tau exp(-d/lambda)
                  (1-exp(-b/lambda))(1-exp(-delta/lambda)).
    """

    values = (
        coupling_g,
        range_m,
        neutron_density_m3,
        source_distance_m,
        electrode_separation_m,
        source_thickness_m,
        integration_time_s,
    )
    if any(value < 0.0 for value in values) or range_m == 0.0:
        raise ValueError(
            "geometry, time, density, and coupling must be nonnegative"
        )
    return (
        coupling_g**2
        * SPEED_OF_LIGHT
        * neutron_density_m3
        * range_m**2
        * integration_time_s
        * math.exp(-source_distance_m / range_m)
        * (1.0 - math.exp(-source_thickness_m / range_m))
        * (1.0 - math.exp(-electrode_separation_m / range_m))
    )


def josephson_single_pair_energy_and_force(
    coupling_g: float,
    range_m: float,
) -> dict[str, float]:
    """Return surface energy and force magnitude for one Cooper pair."""

    if coupling_g < 0.0 or range_m <= 0.0:
        raise ValueError("coupling must be nonnegative and range positive")
    energy = (
        coupling_g**2
        * HBAR_C
        * JOSEPHSON_NEUTRON_DENSITY_M3
        * range_m**2
        * math.exp(-JOSEPHSON_SOURCE_DISTANCE_M / range_m)
        * (1.0 - math.exp(-JOSEPHSON_SOURCE_THICKNESS_M / range_m))
    )
    return {
        "surface_energy_per_Cooper_pair_J": energy,
        "surface_force_per_Cooper_pair_N": energy / range_m,
    }


def microscope_long_range_bound() -> dict[str, Any]:
    """Conservative 95% screen using final MICROSCOPE Ti-Pt errors.

    Fayet's published B-L coefficient used the same Ti/Pt composition lever arm
    but predates the final result.  Combining it with the final errors is a
    transparent approximate recast, not an official MICROSCOPE limit.
    """

    sigma = math.hypot(MICROSCOPE_ETA_STAT, MICROSCOPE_ETA_SYST)
    eta_95 = abs(MICROSCOPE_ETA_CENTRAL) + 1.96 * sigma
    epsilon_limit = math.sqrt(
        eta_95 / MICROSCOPE_B_MINUS_L_COEFFICIENT
    )
    g_limit = ELEMENTARY_EM_COUPLING * epsilon_limit
    alpha_neutron = pure_neutron_alpha_per_g_squared() * g_limit**2
    return {
        "applicability": "Earth-source / effectively long range only",
        "eta_95_conservative": eta_95,
        "epsilon_B_minus_L_95_approx": epsilon_limit,
        "canonical_g_X_95_approx": g_limit,
        "pure_neutron_alpha_95_approx": alpha_neutron,
        "typical_neutral_matter_force_fraction_vs_gravity": 0.25 * alpha_neutron,
        "status": "kills_useful_long_range_composition_force",
        "caveat": (
            "combines Fayet's published composition coefficient with the final "
            "MICROSCOPE errors; this is an order-of-magnitude recast, not the "
            "collaboration's official B-L likelihood"
        ),
    }


def equivalent_josephson_voltage(
    phase_rad: float,
    integration_time_s: float = JOSEPHSON_INTEGRATION_TIME_S,
) -> float:
    if phase_rad < 0.0 or integration_time_s <= 0.0:
        raise ValueError("phase must be nonnegative and time positive")
    return HBAR * phase_rad / (2.0 * ELEMENTARY_CHARGE * integration_time_s)


def optomechanical_josephson_rows() -> list[dict[str, Any]]:
    """Recast sparse current repulsive-alpha anchors into Josephson limits."""

    response = CONSERVATIVE_CONSTRAINT_MATERIAL_RESPONSE
    rows: list[dict[str, Any]] = []
    for range_um, anchor in GLOBAL_REPULSIVE_ALPHA_ANCHORS.items():
        alpha_anchor = float(anchor["abs_alpha_limit"])
        range_m = range_um * 1.0e-6
        coupling_limit = g_from_generic_alpha(alpha_anchor, response)
        potential_normalized_coupling_limit = coupling_limit / math.sqrt(
            4.0 * math.pi
        )
        phase_limit = josephson_phase(coupling_limit, range_m)
        phase_coefficient = josephson_phase(1.0, range_m)
        phase_threshold_coupling = math.sqrt(
            JOSEPHSON_PHASE_THRESHOLD_RAD / phase_coefficient
        )
        single_pair = josephson_single_pair_energy_and_force(
            coupling_limit, range_m
        )
        rows.append(
            {
                "range_um": range_um,
                "mediator_mass_eV": mass_ev_from_range_um(range_um),
                "generic_alpha_95_anchor_approx": alpha_anchor,
                "generic_alpha_sign_used": "repulsive_alpha_less_than_zero",
                "constraint_source": anchor["source"],
                "constraint_quality": anchor["quality"],
                "microscope_long_range_bound_applicable": False,
                "B_minus_L_response_factor": response,
                "response_assumption": (
                    "conservative generic q_source*q_target=0.25; no "
                    "historical-experiment material refit"
                ),
                "canonical_g_X_limit_approx": coupling_limit,
                "potential_normalized_g_C_limit_approx": (
                    potential_normalized_coupling_limit
                ),
                "canonical_phase_at_limit_rad": phase_limit,
                "proposal_phase_threshold_rad": JOSEPHSON_PHASE_THRESHOLD_RAD,
                "canonical_g_X_for_proposal_threshold": phase_threshold_coupling,
                "coupling_headroom_limit_over_threshold": (
                    coupling_limit / phase_threshold_coupling
                ),
                **single_pair,
                "interpretation": (
                    "the conservative sparse laboratory anchor puts the ideal "
                    "phase below 1e-3 rad; additionally no measured Josephson "
                    "source-modulated noise floor exists"
                ),
            }
        )
    return rows


def normalization_audit() -> dict[str, Any]:
    range_m = HBAR_C_EV_UM / 0.01 * 1.0e-6
    benchmark = josephson_phase(1.0e-16, range_m)
    return {
        "frozen_convention": "L_int = g_X X_mu J_(B-L)^mu",
        "potential_SI": (
            "+g_X^2*hbar*c*Q1*Q2*exp(-r/lambda)/(4*pi*r)"
        ),
        "ordinary_neutral_atom_charge": "neutron number N",
        "force_sign": "like ordinary matter repels; opposite B-L charges attract",
        "published_Josephson_equation": (
            "writes g_(B-L)^2 Q exp(-m r)/r without an explicit 1/(4*pi)"
        ),
        "published_appendix_vertex": (
            "uses the same g_(B-L) as the Lagrangian vertex coupling"
        ),
        "normalization_finding": "internal_4pi_discrepancy_under_canonical_normalization",
        "benchmark_only_mapping": (
            "define a separate potential-normalized reproduction parameter "
            "g_C, with g_X = sqrt(4*pi) * g_C"
        ),
        "phase_ratio_potential_normalized_over_canonical": 4.0 * math.pi,
        "coupling_reach_ratio": math.sqrt(4.0 * math.pi),
        "canonical_benchmark": {
            "g_X": 1.0e-16,
            "mediator_mass_eV": 0.01,
            "range_um": range_m * 1.0e6,
            "phase_rad": benchmark,
        },
        "published_potential_normalized_benchmark": {
            "g_C": 1.0e-16,
            "equivalent_g_X": math.sqrt(4.0 * math.pi) * 1.0e-16,
            "mediator_mass_eV": 0.01,
            "source_distance_um": 1.0,
            "integration_time_s": 60.0,
            "phase_rad": josephson_phase(
                math.sqrt(4.0 * math.pi) * 1.0e-16,
                range_m,
            ),
            "phase_rad_at_0p1_um": josephson_phase(
                math.sqrt(4.0 * math.pi) * 1.0e-16,
                range_m,
                source_distance_m=0.1e-6,
            ),
        },
        "model_validity": [
            "minimal anomaly-free gauged B-L requires additional fermion content such as three right-handed neutrinos",
            "mediator mass requires a Higgs or Stueckelberg completion",
            "screen assumes negligible kinetic mixing and no environmental screening",
            "macroscopic neutral matter is represented by natural-isotope-average neutron/mass fractions",
        ],
        "caveat": (
            "the proposal's potential and appendix vertex cannot both use the "
            "same canonically normalized coupling as written; g_C is introduced "
            "here only to reproduce its plotted benchmark, and is not a repair "
            "or reinterpretation of the paper"
        ),
    }


def modulated_source_definition() -> dict[str, Any]:
    """Freeze the published levitated attractor drive and reaction scale."""

    angular_frequency = 2.0 * math.pi * LEVITATED_DRIVE_FREQUENCY_HZ
    maximum_velocity = angular_frequency * LEVITATED_ATTRACTOR_AMPLITUDE_M
    maximum_acceleration = (
        angular_frequency**2 * LEVITATED_ATTRACTOR_AMPLITUDE_M
    )
    return {
        "architecture": "published_2026_levitated_Au_Si_pattern",
        "source_materials": "density-patterned Au/Si attractor",
        "target": "approximately 10 um diameter silica sphere",
        "coupling": "canonical B-L vector to neutron number",
        "waveform_status": (
            "E-038 sinusoidal idealization of the reported oscillation; the "
            "paper uses a recorded per-measurement trajectory not extracted here"
        ),
        "relative_coordinate": (
            "x(t) = x0 + A*sin(2*pi*f*t), lateral to the source face"
        ),
        "peak_to_peak_translation_m": LEVITATED_ATTRACTOR_PEAK_TO_PEAK_M,
        "amplitude_m": LEVITATED_ATTRACTOR_AMPLITUDE_M,
        "frequency_Hz": LEVITATED_DRIVE_FREQUENCY_HZ,
        "pattern_pitch_m_approx": LEVITATED_PATTERN_PITCH_M,
        "face_gap_m_approx": LEVITATED_FACE_GAP_M,
        "target_diameter_m_approx": LEVITATED_TARGET_DIAMETER_M,
        "maximum_velocity_m_per_s": maximum_velocity,
        "maximum_acceleration_m_per_s2": maximum_acceleration,
        "actuator_support_reaction_N_per_kg_moving_mass": maximum_acceleration,
        "moving_mass_kg": None,
        "generic_Yukawa_alpha1_lambda10um_template_force_N": (
            LEVITATED_REFERENCE_TEMPLATE_FORCE_N / LEVITATED_REFERENCE_ALPHA
        ),
        "ordinary_Newtonian_moving_pattern_background_N": None,
        "reaction_ledger": (
            "the drive actuator accelerates the patterned attractor and the "
            "stage/support carries equal opposite mechanical reaction; the "
            "hypothetical field transfers equal opposite momentum between "
            "attractor and sphere"
        ),
        "mass_caveat": (
            "the moving attractor/stage mass was not recovered in this audit, "
            "so drive reaction is reported per kilogram rather than inventing "
            "an absolute support force; velocity and acceleration are likewise "
            "for the stated sinusoidal idealization, not the recorded path"
        ),
    }


def source_reaction_and_confounders() -> dict[str, Any]:
    source_volume_m3 = JOSEPHSON_SOURCE_AREA_M2 * JOSEPHSON_SOURCE_THICKNESS_M
    return {
        "primary_modulated_source": modulated_source_definition(),
        "secondary_ideal_phase_source": {
            "material": "carbon plate as proposed",
            "neutron_density_m3": JOSEPHSON_NEUTRON_DENSITY_M3,
            "area_m2": JOSEPHSON_SOURCE_AREA_M2,
            "thickness_m": JOSEPHSON_SOURCE_THICKNESS_M,
            "volume_m3": source_volume_m3,
            "neutron_count": JOSEPHSON_NEUTRON_DENSITY_M3 * source_volume_m3,
        },
        "secondary_ideal_phase_detector": (
            "two Josephson electrodes separated by 100 nm, with the near "
            "electrode 1 um from the source and a 60 s phase integration"
        ),
        "reaction_ledger": (
            "the driven Au/Si attractor and levitated sphere exchange equal "
            "field momentum, while the actuator and support carry the source "
            "drive reaction; in the secondary ideal phase geometry, the carbon "
            "plate, Cooper pairs, lattice, package, plate mount, and supports "
            "close the reaction ledger"
        ),
        "levitated_force_confounders": [
            {"name": "mechanical drive pickup from the moving Au/Si attractor and support", "measured_force_bound_N": None, "status": "published_null_exists_same_template_bound_not_recovered_in_e038"},
            {"name": "ordinary Newtonian moving-pattern force and density-model residual", "measured_force_bound_N": None, "status": "not_calculated_in_e038"},
            {"name": "electromagnetic and scattered-light drive-correlated force", "measured_force_bound_N": None, "status": "published_null_exists_same_template_bound_not_recovered_in_e038"},
        ],
        "josephson_phase_confounders": [
            {"name": "source-insertion contact and patch potentials", "measured_phase_bound_rad": None, "status": "unknown"},
            {"name": "capacitive pickup and electrode electrochemical equilibration", "measured_phase_bound_rad": None, "status": "unknown"},
            {"name": "Casimir/electrostatic stress and package strain", "measured_phase_bound_rad": None, "status": "unknown"},
            {"name": "vibration, thermal drift, and critical-current drift", "measured_phase_bound_rad": None, "status": "unknown"},
            {"name": "magnetic contamination, trapped flux, and phase slips", "measured_phase_bound_rad": None, "status": "unknown"},
            {"name": "gauge-invariant potential-to-junction-phase transfer", "measured_phase_bound_rad": None, "status": "unvalidated"},
        ],
        "minimum_controls": [
            "drive-frequency, phase-reversal, speed-scaling, harmonic, and multidimensional spatial-template nulls",
            "equal-density or composition-swapped patterned-source null with a measured support-motion channel",
            "randomized near/far source position with blinded phase labels",
            "density- and geometry-matched source with different neutron fraction",
            "dummy junction and electrically isolated source-motion monitor",
            "distance scan across the frozen 5-48 um range law",
            "independent voltage, temperature, vibration, strain, and magnetic channels",
            "explicit source/support recoil bound and full electromagnetic null budget",
        ],
        "kill_threshold": (
            "retain only if either (a) at least two adjacent ranges have allowed "
            "phase at or above 1e-3 rad and every phase confounder is below "
            "one-fifth of that phase, or (b) allowed patterned force reaches the "
            "rounded published fitted-template scale and every force confounder "
            "is below one-fifth of the allowed force; unknown or unqualified "
            "bounds fail closed"
        ),
    }


def levitated_detector_scale_check() -> dict[str, Any]:
    """Compare the global 10-um bound with demonstrated detector reach."""

    global_alpha = float(
        GLOBAL_REPULSIVE_ALPHA_ANCHORS[LEVITATED_REFERENCE_RANGE_UM][
            "abs_alpha_limit"
        ]
    )
    pattern_response = au_si_silica_response_factor()
    maximum_effective_pattern_alpha = (
        global_alpha
        * pattern_response
        / CONSERVATIVE_CONSTRAINT_MATERIAL_RESPONSE
    )
    maximum_template_force = (
        LEVITATED_REFERENCE_TEMPLATE_FORCE_N
        * maximum_effective_pattern_alpha
        / LEVITATED_REFERENCE_ALPHA
    )
    return {
        "range_um": LEVITATED_REFERENCE_RANGE_UM,
        "published_template_force_at_reference_alpha_N": (
            LEVITATED_REFERENCE_TEMPLATE_FORCE_N
        ),
        "published_reference_alpha": LEVITATED_REFERENCE_ALPHA,
        "global_repulsive_alpha_anchor": global_alpha,
        "global_constraint_response_assumption": (
            CONSERVATIVE_CONSTRAINT_MATERIAL_RESPONSE
        ),
        "Au_Si_silica_pattern_response": pattern_response,
        "maximum_effective_pattern_alpha": maximum_effective_pattern_alpha,
        "maximum_allowed_pattern_template_force_N": maximum_template_force,
        "demonstrated_force_sensitivity_N_per_sqrt_Hz": (
            LEVITATED_FORCE_SENSITIVITY_N_PER_SQRT_HZ
        ),
        "published_fitted_template_scale_over_allowed_force": (
            LEVITATED_REFERENCE_TEMPLATE_FORCE_N / maximum_template_force
        ),
        "noise_density_comparison": (
            "not formed: N/sqrt(Hz) cannot be divided by N without a specified "
            "measurement bandwidth or integration-time estimator"
        ),
        "status": "allowed_force_below_rounded_fitted_template_scale",
        "caveat": (
            "template-force and alpha values are rounded from paper text/figures; "
            "this is a conservative scale comparison, not a combined likelihood"
        ),
    }


def survival_rule_evaluation() -> dict[str, Any]:
    rows = sorted(optomechanical_josephson_rows(), key=lambda row: row["range_um"])
    above_threshold = [
        row["canonical_phase_at_limit_rad"] >= JOSEPHSON_PHASE_THRESHOLD_RAD
        for row in rows
    ]
    adjacent_pairs = [
        [rows[index]["range_um"], rows[index + 1]["range_um"]]
        for index in range(len(rows) - 1)
        if above_threshold[index] and above_threshold[index + 1]
    ]
    source_audit = source_reaction_and_confounders()
    phase_confounders = source_audit["josephson_phase_confounders"]
    phase_bounds_complete = all(
        item["measured_phase_bound_rad"] is not None
        for item in phase_confounders
    )
    qualifying_ranges = {
        range_um for pair in adjacent_pairs for range_um in pair
    }
    background_reference_phase = (
        min(
            row["canonical_phase_at_limit_rad"]
            for row in rows
            if row["range_um"] in qualifying_ranges
        )
        if qualifying_ranges
        else None
    )
    phase_bounds_below_one_fifth = (
        background_reference_phase is not None
        and phase_bounds_complete
        and all(
            float(item["measured_phase_bound_rad"])
            < background_reference_phase / 5.0
            for item in phase_confounders
        )
    )
    phase_survived = bool(adjacent_pairs) and phase_bounds_below_one_fifth

    detector_scale = levitated_detector_scale_check()
    maximum_allowed_force = detector_scale[
        "maximum_allowed_pattern_template_force_N"
    ]
    force_confounders = source_audit["levitated_force_confounders"]
    force_bounds_complete = all(
        item["measured_force_bound_N"] is not None for item in force_confounders
    )
    allowed_force_reaches_reference = (
        maximum_allowed_force >= LEVITATED_REFERENCE_TEMPLATE_FORCE_N
    )
    force_bounds_below_one_fifth = (
        force_bounds_complete
        and all(
            float(item["measured_force_bound_N"]) < maximum_allowed_force / 5.0
            for item in force_confounders
        )
    )
    force_survived = (
        allowed_force_reaches_reference and force_bounds_below_one_fifth
    )
    survived = phase_survived or force_survived
    return {
        "required_adjacent_signal_points": 2,
        "qualifying_adjacent_range_pairs_um": adjacent_pairs,
        "all_josephson_confounders_have_measured_phase_bounds": (
            phase_bounds_complete
        ),
        "background_reference_phase_rad": background_reference_phase,
        "all_josephson_confounders_below_one_fifth_allowed_phase": (
            phase_bounds_below_one_fifth
        ),
        "josephson_channel_survived": phase_survived,
        "levitated_allowed_force_N": maximum_allowed_force,
        "levitated_reference_template_force_N": (
            LEVITATED_REFERENCE_TEMPLATE_FORCE_N
        ),
        "levitated_allowed_force_reaches_reference": (
            allowed_force_reaches_reference
        ),
        "all_force_confounders_have_qualified_same_template_bounds": (
            force_bounds_complete
        ),
        "all_force_confounders_below_one_fifth_allowed_force": (
            force_bounds_below_one_fifth
        ),
        "levitated_channel_survived": force_survived,
        "survived": survived,
        "disposition": (
            "retain_as_precision_test" if survived else "park_fail_closed"
        ),
    }


def portfolio_refresh() -> list[dict[str, Any]]:
    """Return distinct post-E-037 opportunities without deepening variants."""

    return [
        {
            "id": "P-003",
            "name": "short-range B-L vector",
            "category": "hypothetical_new_interaction_precision_test",
            "gates": {
                "1_source_coupling": _gate("passed", "canonical vector coupling; published driven Au/Si attractor and silica target; reported drive envelope with an explicit E-038 sinusoidal kinematic idealization; field and per-mass support reaction; secondary carbon/Josephson geometry are frozen"),
                "2_constraints_validity": _gate("partial", "current micron-scale generic Yukawa data leave only a narrow approximate window; long-range MICROSCOPE bounds kill useful bulk reach"),
                "3_absolute_scale": _gate("failed", "conservative sparse anchors put ideal phase below 1e-3 rad and the allowed patterned force about 58 times below the rounded published fitted-template scale"),
                "4_falsification": _gate("passed", "range, composition, near/far, phase/harmonic, and environmental controls are concrete; published levitated nulls are not reduced here to same-template force bounds, Newtonian pattern background is uncalculated, and Josephson bounds are unknown, so qualification fails closed"),
            },
            "disposition": "deepened_then_parked_in_e038",
        },
        {
            "id": "P-008",
            "name": "quantum-corrected symmetron profile",
            "category": "hypothetical_screened_scalar_precision_test",
            "gates": {
                "1_source_coupling": _gate("partial", "density-dependent coupling is specified at model level, but E-039 must freeze a planar source, boundaries, and support reaction"),
                "2_constraints_validity": _gate("partial", "atom and neutron null tests are strong; a 2026 one-loop planar correction is materially new but not evidence"),
                "3_absolute_scale": _gate("unknown", "no common allowed geometry-specific signal above a frozen detector floor has been shown"),
                "4_falsification": _gate("partial", "a no-PDE planar-detector audit with nonplanar experiments used only as parameter exclusions can park the candidate"),
            },
            "disposition": "next_bounded_no_PDE_constraint_audit",
        },
        {
            "id": "P-009",
            "name": "ultralight scalar dark-matter gradiometry",
            "category": "ambient_new_interaction_precision_metrology",
            "gates": {
                "1_source_coupling": _gate("partial", "a frozen dilaton coupling is explicit but the Galactic field is assumed and not controllable"),
                "2_constraints_validity": _gate("partial", "clock, equivalence-principle, interferometer, and astrophysical constraints are mass dependent"),
                "3_absolute_scale": _gate("unknown", "injected-phase recovery validates analysis, but no frozen allowed scalar-DM mass/coupling has been converted into a physical phase"),
                "4_falsification": _gate("passed", "coherent-frequency, baseline, species, sidereal, and injection tests are available"),
            },
            "disposition": "retain_as_precision_search_not_generation",
        },
        {
            "id": "P-010",
            "name": "optical analogue-horizon backreaction",
            "category": "analog_dynamics_not_real_curvature",
            "gates": {
                "1_source_coupling": _gate("passed", "pump, Kerr medium, photons, and pump recoil close optical energy-momentum accounting"),
                "2_constraints_validity": _gate("passed", "valid only as nonlinear dispersive optics, not an astrophysical horizon"),
                "3_absolute_scale": _gate("passed", "single-photon correlations and pump backreaction are measurable at laboratory optical scales"),
                "4_falsification": _gate("passed", "horizon/no-horizon dispersion, partner coincidences, and photon-energy accounting are direct controls"),
            },
            "disposition": "retain_as_adjacent_analog_only",
        },
        {
            "id": "P-011",
            "name": "electric solar-wind sail",
            "category": "external_reaction_propulsion_not_internal_gravity",
            "gates": {
                "1_source_coupling": _gate("passed", "biased tethers deflect solar-wind ions and the wind closes the momentum ledger"),
                "2_constraints_validity": _gate("partial", "plasma theory is credible but prior flight attempts did not cleanly deploy the tether"),
                "3_absolute_scale": _gate("partial", "modeled baseline is roughly 1 N for 100 kg, but flight-demonstrated thrust remains unknown; even the design scale is only about 1e-3 g and not cabin gravity"),
                "4_falsification": _gate("passed", "voltage modulation with solar-wind and attitude monitoring is a direct flight test"),
            },
            "disposition": "retain_as_conventional_propulsion_engineering",
        },
    ]


def source_ledger() -> list[dict[str, str]]:
    return [
        {
            "key": "Fayet_2018",
            "citation": "P. Fayet, Phys. Rev. D 97, 055039 (2018), arXiv:1712.00856",
            "use": "B-L charge convention and equivalence-principle normalization",
        },
        {
            "key": "MICROSCOPE_final",
            "citation": "P. Touboul et al., Phys. Rev. Lett. 129, 121102 (2022), arXiv:2209.15487",
            "use": "final Ti-Pt Eotvos parameter for the long-range screen",
        },
        {
            "key": "optomechanical_2026",
            "citation": "Gautam Venugopalan et al., Sci. Rep. 16, 5180 (2026), arXiv:2412.13167v2",
            "use": "measured 6-um-separation force sensitivity and patterned-force template scale",
        },
        {
            "key": "Geraci_2008",
            "citation": "A. A. Geraci et al., Phys. Rev. D 78, 022002 (2008), arXiv:0802.2350",
            "use": "explicit 95-percent |alpha|=14000 exclusion anchor at 10 um",
        },
        {
            "key": "Chen_2016",
            "citation": "Y.-J. Chen et al., Phys. Rev. Lett. 116, 221102 (2016), arXiv:1410.7267",
            "use": "repulsive-sign Au/Si Casimir-less constraints near 5 um",
        },
        {
            "key": "Tan_2020",
            "citation": "W.-H. Tan et al., Phys. Rev. Lett. 124, 051301 (2020)",
            "use": "explicit |alpha|<=1 anchor at 48 um",
        },
        {
            "key": "Chiaverini_2003",
            "citation": "J. Chiaverini et al., Phys. Rev. Lett. 90, 151101 (2003), arXiv:hep-ph/0209325",
            "use": "conservative published-scale anchor near 20 um",
        },
        {
            "key": "Josephson_proposal",
            "citation": "Y. Cheng, J. Sheng, and T. T. Yanagida, Phys. Lett. B 860, 139156 (2025), arXiv:2402.14514",
            "use": "carbon-source/Josephson geometry and proposal phase threshold",
        },
        {
            "key": "symmetron_refresh",
            "citation": "2026 one-loop planar symmetron correction, arXiv:2606.28423",
            "use": "materially new assumption for a future bounded replacement screen",
        },
        {
            "key": "atom_gradiometer_2026",
            "citation": "C. F. A. Baynham et al., Nature 654, 622-628 (2026), DOI:10.1038/s41586-026-10617-1",
            "use": "injected coherent-phase recovery for an ambient scalar-DM precision candidate",
        },
        {
            "key": "optical_analogues_2026",
            "citation": "Nature Communications DOI:10.1038/s41467-026-73812-8; Nature DOI:10.1038/s41586-026-10720-3",
            "use": "single-photon analogue signal and optical pump-backreaction bookkeeping",
        },
        {
            "key": "electric_sail",
            "citation": "P. Janhunen et al., Rev. Sci. Instrum. 81, 111301 (2010)",
            "use": "external-reaction propulsion baseline",
        },
    ]


def run_analysis() -> dict[str, Any]:
    rows = optomechanical_josephson_rows()
    candidates = portfolio_refresh()
    return {
        "provenance": implementation_provenance(),
        "model": normalization_audit(),
        "constraints": {
            "long_range": microscope_long_range_bound(),
            "short_range_recast": {
                "status": "approximate_screen_not_official_exclusion",
                "constraint_material_response_assumption": (
                    CONSERVATIVE_CONSTRAINT_MATERIAL_RESPONSE
                ),
                "levitated_Au_Si_silica_pattern_response": (
                    au_si_silica_response_factor()
                ),
                "rows": rows,
            },
            "detector_scale_check": levitated_detector_scale_check(),
        },
        "source_reaction_and_confounders": source_reaction_and_confounders(),
        "survival_rule": survival_rule_evaluation(),
        "portfolio": {
            "candidate_count": len(candidates),
            "candidates": candidates,
            "selected_for_deepening": "P-003",
            "screen_result": (
                "No candidate supports practical artificial gravity or bulk "
                "inertial control; P-003 fails the current absolute-scale and "
                "measured-background gates and is parked"
            ),
        },
        "decision": {
            "status": "parked_scale_and_measured_background_gate_failed",
            "selected_candidate": "P-003",
            "constraint_result": (
                "conservative sparse laboratory anchors put the ideal Josephson "
                "phase below 1e-3 rad across the audited 5-48 um points"
            ),
            "physics_result": (
                "long-range useful force is excluded and micron-range B-L is "
                "composition dependent, nonuniversal, and exponentially local"
            ),
            "next_best_step": (
                "screen P-008 with one bounded no-PDE quantum-corrected "
                "symmetron planar-detector audit, using nonplanar experiments "
                "only as parameter exclusions; park it if no window reopens"
            ),
        },
        "sources": source_ledger(),
        "resource_accounting": {
            "pde_builds": 0,
            "pde_solves": 0,
            "new_numerical_fits": 0,
            "hardware_actions": 0,
            "checkpoint_reads_or_writes": 0,
            "new_compute_or_resource_purchase": 0,
        },
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-json", type=Path)
    args = parser.parse_args(argv)
    report = run_analysis()
    if args.report_json is not None:
        _write_json(args.report_json, report)
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""E-037 diversified opportunity portfolio and diamagnetic scale audit.

This module implements the post-E-036 strategy change.  It screens genuinely
different opportunities through four progressive gates:

1. a specified source/actuator, coupling, and reaction ledger;
2. compatibility with constraints and the model's validity regime;
3. an absolute acceleration/force/curvature/signal/resource scale;
4. a falsifiable experiment with important confounders.

Only one candidate is deepened: diamagnetic gravity compensation for small
water-like samples.  It survives all four gates as an established,
nonuniversal electromagnetic body-force simulator.  It does not generate
spacetime curvature and does not demonstrate inertial control.  The worked
bound shows why material-specific susceptibility is the decisive confounder:
when a magnet exactly cancels gravity for water, a one-percent mismatch in
specific susceptibility leaves a one-percent-g differential acceleration.

No candidate in this screen supports practical artificial gravity or bulk
inertial control.  Real-curvature, new-interaction precision tests, analog
dynamics, gravity-like body forces, and acceleration systems remain labeled
separately throughout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import time
from typing import Any


CAMPAIGN = "E-037"
STANDARD_GRAVITY = 9.80665
MU0 = 4.0 * math.pi * 1.0e-7
SPEED_OF_LIGHT = 299_792_458.0
GRAVITATIONAL_CONSTANT = 6.67430e-11
WATER_DENSITY = 1_000.0
WATER_VOLUME_SUSCEPTIBILITY = -9.1e-6
REFERENCE_LOCAL_FIELD_T = 16.0
SOLAR_IRRADIANCE_1_AU = 1_361.0
ACS3_SAIL_AREA_M2 = 80.0
ACS3_TOTAL_MASS_KG = 16.0


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
            "closed-form order-of-magnitude portfolio screen; no PDE, field "
            "solver, hardware actuation, or experimental data generation"
        ),
    }


def _gate(
    status: str,
    statement: str,
) -> dict[str, str]:
    allowed = {"passed", "partial", "failed", "unknown"}
    if status not in allowed:
        raise ValueError(f"invalid gate status: {status}")
    return {"status": status, "statement": statement}


def portfolio_candidates() -> list[dict[str, Any]]:
    """Return a diversified, explicitly categorized four-gate portfolio."""

    return [
        {
            "id": "P-001",
            "name": "diamagnetic gravity compensation for small samples",
            "category": "gravity_like_body_force_not_curvature",
            "source_and_reaction": (
                "superconducting solenoid plus gradient/Maxwell coil; induced "
                "sample magnetization couples through force density "
                "chi*grad(B^2)/(2*mu0*(1+chi)); "
                "equal reaction is carried by electromagnetic stress into the "
                "coil, cryostat, and support"
            ),
            "gates": {
                "1_source_coupling": _gate("passed", "standard electromagnetism with closed reaction ledger"),
                "2_constraints_validity": _gate(
                    "partial",
                    "valid for linear material susceptibility; field exposure, "
                    "material heterogeneity, convection, conductivity, and "
                    "small high-field volume limit biological interpretation",
                ),
                "3_absolute_scale": _gate(
                    "passed",
                    "about 1.35e3 T^2/m cancels 1g for water; the published "
                    "ideal simulation reaches about 4004 microliters below "
                    "0.01g residual and its practical-coil simulation about 3450",
                ),
                "4_falsification": _gate(
                    "passed",
                    "field-map and multi-susceptibility phantom measurements can "
                    "test force law, uniformity, and differential loading",
                ),
            },
            "disposition": "deepened_in_e037_as_small_sample_analog",
        },
        {
            "id": "P-002",
            "name": "solar-photon sail acceleration",
            "category": "inertial_acceleration_system_not_internal_gravity",
            "source_and_reaction": (
                "solar photons transfer momentum to a reflective sail; the "
                "radiation source and reflected photons close momentum bookkeeping"
            ),
            "gates": {
                "1_source_coupling": _gate("passed", "radiation pressure and reaction momentum are explicit"),
                "2_constraints_validity": _gate(
                    "passed",
                    "standard electrodynamics; deployment, reflectivity, thermal "
                    "distortion, attitude control, and payload are engineering limits",
                ),
                "3_absolute_scale": _gate(
                    "passed",
                    "ideal ACS3-scale acceleration is about 4.5e-5 m/s^2 at 1 AU, "
                    "useful for low-thrust spacecraft but not cabin artificial gravity",
                ),
                "4_falsification": _gate("passed", "orbit changes versus sail attitude and solar flux are flight-testable"),
            },
            "disposition": "retain_as_propulsion_baseline_not_deepened",
        },
        {
            "id": "P-003",
            "name": "short-range B-L Yukawa force with modulated attractor",
            "category": "hypothetical_new_interaction_precision_test",
            "source_and_reaction": (
                "neutron-rich source and target carry B-L charge and exchange a "
                "massive vector; mutual source/target momentum exchange is explicit"
            ),
            "gates": {
                "1_source_coupling": _gate("partial", "a vector-mediator coupling and mutual reaction are identified, but E-038 must freeze normalization, range, source composition, and detector geometry"),
                "2_constraints_validity": _gate("partial", "equivalence-principle and inverse-square constraints leave only model/range-specific windows"),
                "3_absolute_scale": _gate("unknown", "possible detector phase/force, but composition dependence makes useful universal acceleration implausible"),
                "4_falsification": _gate("unknown", "near/far modulation and isotopic tagging are promising controls, but E-038 must freeze the detector observable, noise budget, geometry, and kill threshold"),
            },
            "disposition": "next_cheap_new_interaction_signal_envelope",
        },
        {
            "id": "P-004",
            "name": "axionlike spin-dependent force from a polarized rotor",
            "category": "hypothetical_new_interaction_precision_test",
            "source_and_reaction": (
                "shielded polarized-spin rotor couples through a finite-range "
                "spin potential to a comagnetometer; motor/source carries torque"
            ),
            "gates": {
                "1_source_coupling": _gate("passed", "conditional spin-spin interaction and reaction torque are explicit"),
                "2_constraints_validity": _gate("passed", "dedicated null searches already bound the coupling in tested ranges"),
                "3_absolute_scale": _gate("passed", "sub-femtotesla spin signal is meaningful for the labeled precision test, but unpolarized bulk acceleration averages away and fails the artificial-gravity objective"),
                "4_falsification": _gate("passed", "source rotation, phase, shielding, and null orientations are established controls"),
            },
            "disposition": "park_for_artificial_gravity_retain_as_precision_spin_physics",
        },
        {
            "id": "P-005",
            "name": "negative-effective-mass spin-orbit-coupled condensate",
            "category": "analog_dynamics_not_inertial_mass_control",
            "source_and_reaction": (
                "Raman lasers and trap engineer band curvature for condensate "
                "quasiparticles; laser/trap apparatus and interactions retain momentum"
            ),
            "gates": {
                "1_source_coupling": _gate("passed", "the synthetic dispersion and apparatus coupling are specified"),
                "2_constraints_validity": _gate("passed", "valid in the measured cold-atom band and mean-field regime"),
                "3_absolute_scale": _gate("passed", "order-1 m/s^2 atomic-cloud dynamics are meaningful for the labeled analog, but do not change positive bare mass or external spacetime"),
                "4_falsification": _gate("passed", "dispersion, expansion reversal, and instability are directly imaged"),
            },
            "disposition": "retain_only_as_analog_control_tool",
        },
        {
            "id": "P-006",
            "name": "controlled laboratory gravitational-wave quadrupole",
            "category": "real_spacetime_curvature",
            "source_and_reaction": (
                "driven mechanical or electromagnetic quadrupole radiates under "
                "standard GR; actuator reaction and radiated energy are explicit"
            ),
            "gates": {
                "1_source_coupling": _gate("partial", "quadrupole stress-energy couples through GR, but no concrete actuator geometry, stress, motion, and reaction design is specified"),
                "2_constraints_validity": _gate("passed", "weak-field GR is valid; material stress and speed bound the source"),
                "3_absolute_scale": _gate("failed", "1 GJ has a near-zone gravitational-acceleration scale only about 7.4e-19 m/s^2 at 1 m; at one 1-kHz wavelength the optimistic wave-zone-onset strain proxy is about 1.1e-40"),
                "4_falsification": _gate("failed", "near-field gravity, vibration, and electromagnetic pickup dominate the radiative signal"),
            },
            "disposition": "park_after_scale_bound_no_simulation",
        },
        {
            "id": "P-007",
            "name": "miniature source-mass atom-interferometer calibration",
            "category": "real_curvature_precision_test",
            "source_and_reaction": (
                "centimeter-scale ordinary mass sources Newtonian curvature and "
                "receives the equal gravitational reaction from atomic probes"
            ),
            "gates": {
                "1_source_coupling": _gate("passed", "ordinary mass-energy and Newtonian/weak-field coupling are explicit"),
                "2_constraints_validity": _gate("passed", "standard gravity has been detected with a 0.19 kg in-vacuum source"),
                "3_absolute_scale": _gate("passed", "nanometer-per-second-squared signals are meaningful for the labeled metrology objective but many orders below artificial gravity"),
                "4_falsification": _gate("passed", "source translation, isotope/species comparison, and geometry reversal provide controls"),
            },
            "disposition": "retain_as_precision_calibration_not_field_generation_opportunity",
        },
    ]


def magnetic_gradient_product_for_acceleration(
    acceleration_m_s2: float,
    *,
    density_kg_m3: float = WATER_DENSITY,
    volume_susceptibility: float = WATER_VOLUME_SUSCEPTIBILITY,
) -> float:
    """Return |B dB/dz| in T^2/m for a linear isotropic diamagnet."""

    if acceleration_m_s2 < 0.0 or density_kg_m3 <= 0.0:
        raise ValueError("acceleration must be nonnegative and density positive")
    if not -1.0 < volume_susceptibility < 0.0:
        raise ValueError("this audit requires a weak diamagnetic susceptibility")
    return (
        MU0
        * (1.0 + volume_susceptibility)
        * density_kg_m3
        * acceleration_m_s2
        / abs(volume_susceptibility)
    )


def diamagnetic_scale_table() -> list[dict[str, Any]]:
    """Calculate terrestrial compensation and free-space body-force setpoints."""

    cases = (
        ("full terrestrial cancellation", 1.0, 0.0),
        ("terrestrial 0.01g residual", 0.99, 0.01),
        ("terrestrial lunar 0.165g residual", 0.835, 0.165),
        ("terrestrial Mars 0.38g residual", 0.62, 0.38),
        ("free-space 0.01g magnetic body force", 0.01, None),
    )
    rows = []
    for label, magnetic_fraction_g, terrestrial_residual_g in cases:
        product = magnetic_gradient_product_for_acceleration(
            magnetic_fraction_g * STANDARD_GRAVITY
        )
        rows.append(
            {
                "case": label,
                "magnetic_acceleration_fraction_g": magnetic_fraction_g,
                "terrestrial_residual_fraction_g": terrestrial_residual_g,
                "required_abs_B_dB_dz_T2_per_m": product,
                "gradient_if_local_B_is_16T_T_per_m": (
                    product / REFERENCE_LOCAL_FIELD_T
                ),
            }
        )
    return rows


def susceptibility_mismatch_ledger() -> dict[str, Any]:
    """Quantify differential loading from specific-susceptibility mismatch."""

    mismatch_fractions = (0.001, 0.01, 0.05, 0.10)
    compensation_cases = (
        ("near_microgravity_0.01g", 0.99),
        ("lunar_0.165g", 0.835),
        ("Mars_0.38g", 0.62),
        ("full_cancellation", 1.0),
    )
    rows = []
    for label, magnetic_fraction in compensation_cases:
        for mismatch in mismatch_fractions:
            rows.append(
                {
                    "case": label,
                    "specific_susceptibility_fractional_mismatch": mismatch,
                    "absolute_residual_error_fraction_g": (
                        magnetic_fraction * mismatch
                    ),
                    "absolute_residual_error_m_s2": (
                        magnetic_fraction * mismatch * STANDARD_GRAVITY
                    ),
                }
            )
    return {
        "specific_susceptibility": "chi/(rho*(1+chi))",
        "formula": (
            "if water compensation fraction is f and another constituent's "
            "specific response is (1+epsilon) times water, its acceleration "
            "differs from the target by |f*epsilon|*g"
        ),
        "rows": rows,
        "decisive_bound": (
            "At full water cancellation, a 1-percent specific-susceptibility "
            "mismatch leaves 0.01g differential loading."
        ),
    }


def adjacent_scale_checks() -> dict[str, Any]:
    """Preserve cheap absolute scales for two non-selected candidates."""

    ideal_solar_pressure = 2.0 * SOLAR_IRRADIANCE_1_AU / SPEED_OF_LIGHT
    ideal_solar_force = ideal_solar_pressure * ACS3_SAIL_AREA_M2
    ideal_solar_acceleration = ideal_solar_force / ACS3_TOTAL_MASS_KG
    source_energy = 1.0e9
    near_zone_distance = 1.0
    frequency = 1.0e3
    wave_zone_distance = SPEED_OF_LIGHT / frequency
    detector_baseline = 1.0
    near_zone_acceleration = (
        GRAVITATIONAL_CONSTANT
        * source_energy
        / (SPEED_OF_LIGHT**2 * near_zone_distance**2)
    )
    strain_bound = (
        4.0
        * GRAVITATIONAL_CONSTANT
        * source_energy
        / (SPEED_OF_LIGHT**4 * wave_zone_distance)
    )
    relative_acceleration = (
        0.5
        * (2.0 * math.pi * frequency) ** 2
        * strain_bound
        * detector_baseline
    )
    return {
        "ideal_ACS3_scale_solar_sail": {
            "pressure_Pa": ideal_solar_pressure,
            "force_N": ideal_solar_force,
            "acceleration_m_s2": ideal_solar_acceleration,
            "acceleration_fraction_g": ideal_solar_acceleration / STANDARD_GRAVITY,
            "limits": "perfect normal reflection at 1 AU; actual sail performance is lower",
        },
        "optimistic_1GJ_1kHz_gravity_bounds": {
            "near_zone_distance_m": near_zone_distance,
            "near_zone_acceleration_scale_m_s2": near_zone_acceleration,
            "wave_zone_distance_m": wave_zone_distance,
            "wave_zone_strain_scale": strain_bound,
            "relative_acceleration_over_1m_baseline_m_s2": relative_acceleration,
            "limits": (
                "the near-zone value is the gravity scale of the total source "
                "energy, not a radiative signal; the radiative value places the "
                "same optimistic quadrupolar energy scale at a one-wavelength "
                "wave-zone-onset proxy, not an asymptotic far-zone point, and "
                "still ignores stress, velocity, geometry, coherence, and "
                "radiation-efficiency penalties; a true far-zone value is smaller"
            ),
        },
    }


def falsification_design() -> dict[str, Any]:
    """Define a small-sample diamagnetic analog validation experiment."""

    return {
        "objective": (
            "Test whether a measured B-field/gradient map predicts tunable "
            "effective acceleration and differential loading across a 4 mL "
            "water-like volume without mistaking magnetic compensation for gravity."
        ),
        "source_and_reaction_measurement": (
            "record solenoid and gradient-coil currents, cryogenic/electrical "
            "power, support load, and specimen force so the apparatus reaction "
            "is explicit rather than labeled reactionless"
        ),
        "phantoms": [
            "water reference with measured density and susceptibility",
            "saline/gel standards spanning independently measured chi/rho",
            "layered two-material phantom exposing internal differential stress",
        ],
        "setpoints": [
            "field-off 1g control",
            "high-B near-zero-gradient field-only control",
            "0.38g Mars residual",
            "0.01g near-microgravity residual",
            "gradient-current sign reversal at matched background B where stable",
        ],
        "measurements": [
            "independent B and dB/dz map with calibration uncertainty",
            "three-axis specimen acceleration/position and restoring stiffness",
            "temperature, vibration, convection/flow, and support-force channels",
            "pre/post susceptibility and density for every phantom",
        ],
        "predeclared_physics_gates": [
            "water residual magnitude <=0.01g throughout at least 4000 microliters",
            "acceleration direction and magnitude follow chi*grad(B^2)/(2*mu0*rho*(1+chi)) within the combined metrology interval",
            "multi-material differential acceleration follows the measured specific-susceptibility mismatch ledger",
            "field-only and gradient-reversal controls exclude thermal, vibration, convection, ferromagnetic, and container-force aliases",
        ],
        "kill_conditions": [
            "usable volume fails the 0.01g residual map",
            "unmodeled material-specific differential loading exceeds the experiment's gravity-dose tolerance",
            "matched-B controls show direct field or heating effects comparable to the claimed gravity-dependent outcome",
            "force/reaction ledger fails to close within calibrated uncertainty",
        ],
        "interpretation_if_passed": (
            "validated electromagnetic low-gravity simulator for specified "
            "materials and sample volume; never real curvature, universal gravity, "
            "human-scale artificial gravity, or inertial control"
        ),
    }


def source_ledger() -> list[dict[str, Any]]:
    return [
        {
            "citation": "Berry and Geim, Of flying frogs and levitrons, Eur. J. Phys. 18 (1997) 307-313",
            "doi": "10.1088/0143-0807/18/4/012",
            "use": "diamagnetic stability and approximately 16 T demonstration",
        },
        {
            "citation": "Sanavandi and Guo, A magnetic levitation based low-gravity simulator with an unprecedented large functional volume, npj Microgravity 7 (2021) 40",
            "doi": "10.1038/s41526-021-00174-4",
            "use": "force law, water properties, ideal 4004-microliter and practical-coil 3450-microliter V1% simulations, Mars partial-g design, and resource caveats",
        },
        {
            "citation": "Herranz et al., Microgravity simulation by diamagnetic levitation: effects of a strong gradient magnetic field on the transcriptional profile of Drosophila melanogaster, BMC Genomics 13 (2012) 52",
            "doi": "10.1186/1471-2164-13-52",
            "use": "strong-field biological-control and practical container confounders",
        },
        {
            "citation": "Yingchun Leng et al., Measurement of the Earth Tides with a Diamagnetic-Levitated Micro-Oscillator at Room Temperature, PRL 132 (2024) 123601",
            "doi": "10.1103/PhysRevLett.132.123601",
            "use": "modern diamagnetic force-control and gravimetry benchmark, not artificial gravity",
        },
        {
            "citation": "Jaffe et al., Testing sub-gravitational forces on atoms from a miniature in-vacuum source mass, Nature Physics 13 (2017) 938-942",
            "doi": "10.1038/nphys4189",
            "use": "real-curvature precision-source portfolio benchmark",
        },
        {
            "citation": "NASA, Advanced Composite Solar Sail System mission and 80 m2/16 kg technical description",
            "url": "https://ntrs.nasa.gov/citations/20230008378",
            "use": "standard reaction-propulsion portfolio benchmark",
        },
        {
            "citation": "Touboul et al., MICROSCOPE Mission: Final Results of the Test of the Equivalence Principle, PRL 129 (2022) 121102",
            "doi": "10.1103/PhysRevLett.129.121102",
            "use": "long-range composition-dependent-force constraint anchor for P-003",
        },
        {
            "citation": "Optomechanical vector sensing of new forces at 6 micron separation, Scientific Reports (2026)",
            "doi": "10.1038/s41598-026-35656-6",
            "use": "short-range modulated-attractor signature and confounder anchor for P-003/E-038",
        },
        {
            "citation": "Xu et al., Constraints on Axion Mediated Dipole-Dipole Interactions, PRL 134 (2025) 181801",
            "doi": "10.1103/PhysRevLett.134.181801",
            "use": "polarized-source, shielding, phase-control, and subfemtotesla benchmark for P-004",
        },
        {
            "citation": "Khamehchi et al., Negative-Mass Hydrodynamics in a Spin-Orbit-Coupled Bose-Einstein Condensate, PRL 118 (2017) 155301",
            "doi": "10.1103/PhysRevLett.118.155301",
            "use": "band-dispersion analog and apparatus-reaction anchor for P-005",
        },
        {
            "citation": "Blanchet, Gravitational Radiation from Post-Newtonian Sources and Inspiralling Compact Binaries, Living Reviews in Relativity 17 (2014) 2",
            "doi": "10.12942/lrr-2014-2",
            "use": "quadrupole scaling, radiation-zone requirement, and reaction accounting anchor for P-006",
        },
    ]


def run_analysis() -> dict[str, Any]:
    started = time.perf_counter()
    candidates = portfolio_candidates()
    selected = [
        candidate
        for candidate in candidates
        if candidate["disposition"] == "deepened_in_e037_as_small_sample_analog"
    ]
    if len(selected) != 1:
        raise RuntimeError("E-037 must deepen exactly one candidate")
    return {
        "epistemic_status": (
            "diversified mechanism screen plus closed-form adjacent-science "
            "scale audit; no practical artificial gravity or inertial control found"
        ),
        "focus_question": (
            "Can diamagnetic field-gradient compensation provide a quantitatively "
            "honest, falsifiable partial-gravity analog for small samples, and "
            "what material-specific bound prevents calling it universal gravity?"
        ),
        "implementation_provenance": implementation_provenance(),
        "portfolio": {
            "candidate_count": len(candidates),
            "candidates": candidates,
            "selected_for_deepening": selected[0]["id"],
            "screen_result": (
                "No candidate supports practical artificial gravity or bulk "
                "inertial control. P-001 survives for small-sample analog use."
            ),
        },
        "diamagnetic_scale_table": diamagnetic_scale_table(),
        "susceptibility_mismatch": susceptibility_mismatch_ledger(),
        "resource_scale": {
            "local_magnetic_energy_density_at_16T_J_m3": (
                REFERENCE_LOCAL_FIELD_T**2 / (2.0 * MU0)
            ),
            "meaning": (
                "local field energy density only, not total stored magnet energy, "
                "cryogenic load, structural stress, or electrical power"
            ),
        },
        "adjacent_scale_checks": adjacent_scale_checks(),
        "falsification_design": falsification_design(),
        "sources": source_ledger(),
        "decision": {
            "analysis_completed": True,
            "status": "small_sample_analog_survives_no_real_gravity_candidate",
            "selected_candidate": "P-001",
            "classification": "established_nonuniversal_electromagnetic_body_force",
            "main_result": (
                "Water-like 1g compensation requires |B dB/dz| about 1.35e3 "
                "T^2/m. The scale is achievable only in compact high-field "
                "systems, and a 1-percent specific-susceptibility mismatch leaves "
                "about 0.01g differential loading at full compensation."
            ),
            "next_best_step": (
                "E-038: perform the distinct short-range B-L source-to-signal "
                "and current-constraint envelope before any hardware or deeper model"
            ),
        },
        "resource_accounting": {
            "elapsed_seconds": time.perf_counter() - started,
            "pde_builds": 0,
            "pde_solves": 0,
            "hardware_actions": 0,
        },
    }


def _write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-json", type=Path)
    args = parser.parse_args(argv)
    report = run_analysis()
    if args.report_json is not None:
        _write_report(args.report_json, report)
    decision = report["decision"]
    print(
        f"{CAMPAIGN}: status={decision['status']}; "
        f"selected={decision['selected_candidate']}; "
        f"pde_solves={report['resource_accounting']['pde_solves']}; "
        f"elapsed={report['resource_accounting']['elapsed_seconds']:.3f}s"
    )
    return 0 if decision["analysis_completed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

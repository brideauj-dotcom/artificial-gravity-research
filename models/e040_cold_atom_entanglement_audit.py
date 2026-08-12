"""E-040 cold-atom gravitational-entanglement signal audit.

This module reproduces a deliberately frozen, favorable benchmark from the
cold-atom proposal of Howl, Cooper, and Hackermueller, *Physical Review A*
114, 023306 (2026), DOI ``10.1103/l62d-gz5c``.  It then records why the
proposal cannot yet discriminate its quantum-gravity calculation from the
classical-gravity/quantum-matter countermodel of Aziz and Howl, *Nature* 646,
813-817 (2025), DOI ``10.1038/s41586-025-09595-7``.

The calculation is a source-to-detector scale audit, not experimental
evidence.  It creates no gravitational field beyond the ordinary Newtonian
interaction of the atoms and provides no artificial gravity, inertial
control, spacetime engineering, or propulsion capability.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


CAMPAIGN = "E-040"
QUANTUM_PROPOSAL_DOI = "10.1103/l62d-gz5c"
CLASSICAL_COUNTERMODEL_DOI = "10.1038/s41586-025-09595-7"

G_SI = 6.674_30e-11
HBAR_SI = 1.054_571_817_646_156_5e-34
# 2022 CODATA atomic mass constant (NIST value used by the audit).
ATOMIC_MASS_UNIT_KG = 1.660_539_068_92e-27
CAESIUM_133_MASS_U = 132.905_451_961_0

# Frozen favorable benchmark.  N is the total atom number in each of two
# interferometers.  The density and oblate geometry follow the proposal's
# 40-dB example; d=2c is the non-overlap limiting case used for its quoted
# approximately 23-fold enhancement over equal-volume spheres.
ATOM_NUMBER = 1.0e12
NUMBER_DENSITY_M3 = 1.0e18  # 10^12 cm^-3
ELLIPTICITY = 0.98
OBLATE_ENHANCEMENT = 23.0
INTERACTION_TIME_S = 1.0e3
SQUEEZING_DB_EACH_INTERFEROMETER = 40.0
REPETITIONS_PER_SETUP = 1_000
INDEPENDENT_SETUPS = 5
MAX_CLASSICAL_OR_BACKGROUND_FRACTION = 0.10


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


def implementation_provenance() -> dict[str, Any]:
    path = Path(__file__).resolve()
    return {
        "campaign": CAMPAIGN,
        "campaign_schema": 1,
        "module": {
            "path": str(path.relative_to(path.parents[1])),
            "sha256": _sha256_file(path),
        },
        "quantum_proposal_doi": QUANTUM_PROPOSAL_DOI,
        "classical_countermodel_doi": CLASSICAL_COUNTERMODEL_DOI,
        "calculation_scope": (
            "closed-form signal, resource, countermodel-domain, and "
            "confounder audit; no PDE, hardware action, checkpoint access, "
            "or experimental-data generation"
        ),
    }


def caesium_atom_mass_kg() -> float:
    return CAESIUM_133_MASS_U * ATOMIC_MASS_UNIT_KG


def oblate_geometry() -> dict[str, float]:
    """Return the uniform-oblate geometry at the frozen density.

    With ellipticity ``e=sqrt(1-c**2/a**2)``, the volume is
    ``4*pi*a**2*c/3``.  The most favorable non-overlap spacing is ``d=2c``.
    This is a touching-cloud limit with no allowance for a conducting screen,
    trap hardware, or clearance, so it is an upper-envelope signal geometry.
    """

    if not 0.0 < ELLIPTICITY < 1.0:
        raise ValueError("ellipticity must lie strictly between zero and one")
    if ATOM_NUMBER <= 0.0 or NUMBER_DENSITY_M3 <= 0.0:
        raise ValueError("atom number and density must be positive")
    polar_to_equatorial = math.sqrt(1.0 - ELLIPTICITY**2)
    volume_m3 = ATOM_NUMBER / NUMBER_DENSITY_M3
    equatorial_radius_m = (
        3.0 * volume_m3 / (4.0 * math.pi * polar_to_equatorial)
    ) ** (1.0 / 3.0)
    polar_radius_m = polar_to_equatorial * equatorial_radius_m
    center_spacing_m = 2.0 * polar_radius_m
    return {
        "volume_m3": volume_m3,
        "equatorial_radius_m": equatorial_radius_m,
        "polar_radius_m": polar_radius_m,
        "minimum_center_spacing_m": center_spacing_m,
        "minimum_superposition_size_m": 10.0 * center_spacing_m,
        "polar_to_equatorial_ratio": polar_to_equatorial,
        "screen_or_hardware_clearance_m": 0.0,
    }


def quantum_signal_budget() -> dict[str, Any]:
    """Return the proposal's perturbative covariance and ideal SNR scales.

    For the favorable oblate geometry, ``lambda = eta*G*m**2*t/(hbar*d)``.
    At the optimum beam-splitter phase and ``lambda*N << 1``, the covariance
    is ``S=lambda*N**2/4`` and the unsqueezed ideal SNR is
    ``sqrt(M)*lambda*N``.  Squeezing each interferometer by ``r`` dB raises
    the SNR by ``10**(r/10)`` under the paper's variance convention.
    Independent setups are treated only as additional independent trials.
    """

    geometry = oblate_geometry()
    mass_kg = caesium_atom_mass_kg()
    spacing_m = geometry["minimum_center_spacing_m"]
    lambda_phase = (
        OBLATE_ENHANCEMENT
        * G_SI
        * mass_kg**2
        * INTERACTION_TIME_S
        / (HBAR_SI * spacing_m)
    )
    lambda_n = lambda_phase * ATOM_NUMBER
    covariance_atoms_squared = lambda_phase * ATOM_NUMBER**2 / 4.0
    squeezing_gain = 10.0 ** (SQUEEZING_DB_EACH_INTERFEROMETER / 10.0)
    effective_trials = REPETITIONS_PER_SETUP * INDEPENDENT_SETUPS
    snr = math.sqrt(effective_trials) * lambda_n * squeezing_gain
    trials_required = 1.0 / (lambda_n * squeezing_gain) ** 2
    trials_per_setup_required = trials_required / INDEPENDENT_SETUPS
    minimum_elapsed_s_per_setup = (
        trials_per_setup_required * INTERACTION_TIME_S
    )
    return {
        "atom_species": "caesium-133",
        "atom_mass_kg": mass_kg,
        "mass_per_interferometer_kg": ATOM_NUMBER * mass_kg,
        "atom_number_per_interferometer": ATOM_NUMBER,
        "number_density_m3": NUMBER_DENSITY_M3,
        "interaction_time_s": INTERACTION_TIME_S,
        "center_spacing_m": spacing_m,
        "oblate_energy_enhancement": OBLATE_ENHANCEMENT,
        "dimensionless_lambda": lambda_phase,
        "dimensionless_lambda_times_N": lambda_n,
        "perturbative_lambda_N_condition_satisfied": lambda_n < 1.0e-2,
        "covariance_signal_atoms_squared": covariance_atoms_squared,
        "interaction_energy_per_atom_pair_J": (
            lambda_phase * HBAR_SI / INTERACTION_TIME_S
        ),
        "point_mass_acceleration_per_atom_from_other_ensemble_m_s2": (
            G_SI * (ATOM_NUMBER * mass_kg) / spacing_m**2
        ),
        "point_mass_force_between_ensemble_masses_N": (
            G_SI * (ATOM_NUMBER * mass_kg) ** 2 / spacing_m**2
        ),
        "point_mass_potential_energy_between_ensemble_masses_J": (
            -G_SI * (ATOM_NUMBER * mass_kg) ** 2 / spacing_m
        ),
        "point_mass_scale_note": (
            "absolute ordinary-Newtonian reference scales only; the oblate "
            "mode-integral enhancement applies to the phase, not these "
            "point-mass force references"
        ),
        "squeezing_db_each_interferometer": (
            SQUEEZING_DB_EACH_INTERFEROMETER
        ),
        "squeezing_snr_gain": squeezing_gain,
        "repetitions_per_setup": REPETITIONS_PER_SETUP,
        "independent_setups": INDEPENDENT_SETUPS,
        "effective_independent_trials": effective_trials,
        "ideal_quantum_limited_snr": snr,
        "effective_trials_required_for_snr_one": trials_required,
        "trials_per_setup_required_for_snr_one": trials_per_setup_required,
        "minimum_elapsed_s_per_setup_for_snr_one": minimum_elapsed_s_per_setup,
        "minimum_elapsed_years_per_setup_for_snr_one": (
            minimum_elapsed_s_per_setup / (365.25 * 24.0 * 3600.0)
        ),
        "geometry_is_favorable_touching_limit": True,
        "density_convention": (
            "N/n is assigned to one full interferometer, matching the "
            "proposal's narrative estimate; assigning n separately to each "
            "half-populated arm would give d=3.36 mm and ideal SNR about "
            "0.149, which does not qualify a jointly demonstrated tuple"
        ),
        "signal_status": "modeled detector covariance, not a measurement",
    }


def ideal_sensitivity_diagnostic() -> dict[str, Any]:
    """Expose how the frozen SNR changes under two unqualified ideal variations.

    Figure 3 says that its repetition schedule has ``M about 1000`` at
    ``t=10000 s`` but does not publish a complete schedule.  If one *infers* a
    fixed live-time product ``M*t``, then ``t=1000 s`` would have 10000
    repetitions per setup.  This is not promoted to a demonstrated resource.

    At fixed atom number and oblate ellipticity, ``d`` scales as ``n**(-1/3)``
    and the ideal SNR scales as ``n**(1/3)``.  The density needed for unity SNR
    under that inferred repetition schedule is reported only to show that the
    single frozen tuple is not a global no-signal bound.  It carries no
    collision, loss, squeezing, trap, detector, or background qualification.
    """

    baseline = quantum_signal_budget()
    inferred_repetitions_per_setup = 10_000
    inferred_effective_trials = (
        inferred_repetitions_per_setup * INDEPENDENT_SETUPS
    )
    inferred_snr = (
        baseline["dimensionless_lambda_times_N"]
        * baseline["squeezing_snr_gain"]
        * math.sqrt(inferred_effective_trials)
    )
    density_for_unity_m3 = NUMBER_DENSITY_M3 / inferred_snr**3
    spacing_for_unity_m = (
        baseline["center_spacing_m"]
        * (NUMBER_DENSITY_M3 / density_for_unity_m3) ** (1.0 / 3.0)
    )
    return {
        "figure_caption_anchor_t_s": 1.0e4,
        "figure_caption_anchor_repetitions": 1_000,
        "fixed_live_time_schedule_is_inference_not_published_tuple": True,
        "inferred_repetitions_per_setup_at_1e3_s": (
            inferred_repetitions_per_setup
        ),
        "inferred_effective_trials_at_1e3_s": inferred_effective_trials,
        "ideal_snr_at_baseline_density_under_inferred_schedule": inferred_snr,
        "ideal_density_for_snr_one_m3_under_inferred_schedule": (
            density_for_unity_m3
        ),
        "ideal_density_for_snr_one_cm3_under_inferred_schedule": (
            density_for_unity_m3 / 1.0e6
        ),
        "ideal_spacing_for_snr_one_m_under_inferred_schedule": (
            spacing_for_unity_m
        ),
        "qualified_detector_regime_established": False,
        "qualification_failures": (
            "40-dB squeezing, atom number, density, coherence, geometry, "
            "readout, classical-model covariance, and backgrounds are not "
            "demonstrated or bounded together"
        ),
    }


def classical_countermodel_diagnostic(r_over_d: float = 0.1) -> dict[str, Any]:
    """Return the 2025 model's N00N-sphere amplitude scale.

    The paper's Eq. (10) gives

    ``sqrt(vartheta) = (6/25) G**2 m**2 M**3 (R/d) t / hbar**3``.

    Squaring produces ``vartheta``.  This is recorded only as a domain
    diagnostic.  That derivation uses two uniform spherical *whole-object*
    N00N states, ``d >> R`` and ``Delta x >> R`` (or its stated small-Delta-x
    rescaling), and does not derive the four-mode coherent-state covariance
    measured in the cold-atom proposal.  It therefore cannot be subtracted
    from, or compared numerically with, ``S`` or its SNR.
    """

    if not 0.0 < r_over_d <= 1.0:
        raise ValueError("R/d must lie in (0, 1]")
    atom_mass = caesium_atom_mass_kg()
    total_mass = ATOM_NUMBER * atom_mass
    sqrt_vartheta = (
        (6.0 / 25.0)
        * G_SI**2
        * atom_mass**2
        * total_mass**3
        * r_over_d
        * INTERACTION_TIME_S
        / HBAR_SI**3
    )
    return {
        "r_over_d": r_over_d,
        "sqrt_vartheta": sqrt_vartheta,
        "vartheta": sqrt_vartheta**2,
        "derivation_state": "two uniform spherical whole-object N00N states",
        "cold_atom_state": "two four-mode binomial coherent interferometers",
        "cold_atom_observable": "one-open-interferometer atom-number covariance",
        "maps_to_cold_atom_covariance": False,
        "maps_to_cold_atom_snr": False,
        "fraction_of_quantum_covariance": None,
        "validity_note": (
            "R/d=0.1 matches the paper's d=10R figure convention; even then "
            "the state, geometry, perturbative observable, and readout differ"
        ),
    }


def apparatus_and_confounder_ledger() -> dict[str, Any]:
    return {
        "source_and_reaction": {
            "source": (
                "two caesium atom interferometers; each atom cloud is both "
                "source and detector through ordinary Newtonian mass density"
            ),
            "actuators": (
                "laser beam splitters plus optical or magnetic traps create "
                "and recombine the spatial modes"
            ),
            "field_reaction": (
                "the two atom ensembles exchange equal and opposite Newtonian "
                "momentum; no reactionless thrust is present"
            ),
            "apparatus_reaction": (
                "lasers, traps, optional conductor, vacuum vessel, and mounts "
                "take recoil and support forces; their transfer functions are "
                "not modeled in the proposal's covariance budget"
            ),
        },
        "predeclared_max_fraction_of_target": (
            MAX_CLASSICAL_OR_BACKGROUND_FRACTION
        ),
        "confounders": [
            {
                "name": "inter-interferometer electromagnetic coupling",
                "proposed_control": "large separation or conducting membrane",
                "same_covariance_bound": None,
                "qualified_below_fraction": False,
            },
            {
                "name": "s-wave and magnetic dipole-dipole self-interactions",
                "proposed_control": (
                    "Feshbach tuning; effective s-wave scale must be four to "
                    "five orders below the Bohr radius or cancel dipolar terms"
                ),
                "same_covariance_bound": None,
                "qualified_below_fraction": False,
            },
            {
                "name": "background-gas and three-body loss",
                "proposed_control": (
                    "about 1e-9 Pa for a 1e3-s background-collision time; the "
                    "paper's three-body example is erbium at another density"
                ),
                "same_covariance_bound": None,
                "qualified_below_fraction": False,
            },
            {
                "name": "trap, laser, beam-splitter, and detector noise",
                "proposed_control": "common-mode operation and calibration",
                "same_covariance_bound": None,
                "qualified_below_fraction": False,
            },
            {
                "name": "screen, support, vibration, and thermal coupling",
                "proposed_control": "matched screen/no-screen and source controls",
                "same_covariance_bound": None,
                "qualified_below_fraction": False,
            },
        ],
        "component_coincidence": {
            "40_db_squeezing_at_1e12_atoms": False,
            "1e3_s_coherence_at_1e12_atoms": False,
            "single_atom_resolved_covariance_at_1e12_dynamic_range": False,
            "all_frozen_resources_demonstrated_together": False,
        },
    }


def e040_gates() -> dict[str, dict[str, str]]:
    return {
        "1_source_coupling": _gate(
            "passed",
            "ordinary Newtonian mass-density coupling, atom source/detector, "
            "laser/trap actuators, field reaction, and apparatus reaction "
            "channels are explicit at model level",
        ),
        "2_constraints_validity": _gate(
            "partial",
            "the weak-field perturbative quantum calculation is controlled, "
            "but the required components have not operated together and the "
            "classical-gravity/QFT alternative has a different state domain",
        ),
        "3_absolute_scale": _gate(
            "partial",
            "the frozen touching-cloud tuple gives ideal SNR below one; ideal "
            "density/repetition variations can reach unity algebraically, but "
            "no atom number, 40-dB squeezing, long coherence, geometry, and "
            "readout tuple is jointly demonstrated or background-qualified",
        ),
        "4_falsification": _gate(
            "partial",
            "the covariance experiment and controls are concrete, but no "
            "executable classical-model covariance or same-observable bounds "
            "place every dominant background below one tenth of the target",
        ),
    }


def portfolio_refresh() -> list[dict[str, Any]]:
    """Return five distinct replacements plus the closed P-012 candidate."""

    return [
        {
            "id": "P-012",
            "category": "real_gravity_quantum_precision_witness",
            "gates": e040_gates(),
            "disposition": "deepened_then_parked_in_e040",
        },
        {
            "id": "P-017",
            "category": "lorentz_violating_gravity_precision_force",
            "gates": {
                "1_source_coupling": _gate(
                    "partial",
                    "dimension-six pure-gravity SME coefficients and striped "
                    "source/test masses are explicit; the full actuator and "
                    "support transfer ledger remains to be frozen",
                ),
                "2_constraints_validity": _gate(
                    "partial",
                    "the linearized EFT and existing 14-coefficient bounds are "
                    "available, but a recoverable joint likelihood, covariance, "
                    "or other rigorous simultaneous region must first be verified",
                ),
                "3_absolute_scale": _gate(
                    "unknown",
                    "published transfer matrices imply detector-scale torques, "
                    "not artificial gravity; no allowed joint torque envelope "
                    "has been reproduced",
                ),
                "4_falsification": _gate(
                    "partial",
                    "sidereal harmonics and orthogonal stripe controls are "
                    "specific, but same-harmonic noise is not yet compared",
                ),
            },
            "disposition": "next_bounded_joint_constraint_torque_audit_e041",
        },
        {
            "id": "P-018",
            "category": "dark_photon_laboratory_field_generation",
            "gates": {
                "1_source_coupling": _gate(
                    "passed",
                    "kinetic mixing, driven SRF emitter, wall, receiver, RF "
                    "reaction, and thermal dissipation are explicit",
                ),
                "2_constraints_validity": _gate(
                    "passed",
                    "the minimal massive-vector model is directly constrained "
                    "over the experiment's stated mass band",
                ),
                "3_absolute_scale": _gate(
                    "passed",
                    "a detector-scale exclusion was measured; the mechanism "
                    "fails as gravity or bulk acceleration",
                ),
                "4_falsification": _gate(
                    "passed",
                    "emitter-off, detuning, leakage, microphonic, thermal, and "
                    "frequency-drift controls are executable",
                ),
            },
            "disposition": "retain_as_new_interaction_precision_watch_only",
        },
        {
            "id": "P-019",
            "category": "antimatter_real_gravity_precision_test",
            "gates": {
                "1_source_coupling": _gate(
                    "passed",
                    "Earth supplies ordinary gravity and magnetic-trap release "
                    "provides the actuator with apparatus reaction",
                ),
                "2_constraints_validity": _gate(
                    "passed",
                    "weak-field free fall and the magnetic nuisance model are "
                    "within tested regimes",
                ),
                "3_absolute_scale": _gate(
                    "passed",
                    "the Earth-gravity response is measurable but provides no "
                    "local field generation or propulsion",
                ),
                "4_falsification": _gate(
                    "passed",
                    "trap reversal and annihilation-location likelihoods test "
                    "gravity against magnetic gradients",
                ),
            },
            "disposition": "retain_as_equivalence_principle_watch_only",
        },
        {
            "id": "P-020",
            "category": "acoustic_simulated_gravity_small_samples",
            "gates": {
                "1_source_coupling": _gate(
                    "passed",
                    "an ultrasonic standing wave exerts radiation pressure; "
                    "air, transducer, reflector, and sample close momentum",
                ),
                "2_constraints_validity": _gate(
                    "partial",
                    "droplet-scale levitation is established, while streaming, "
                    "heating, deformation, and atomization limit scaling",
                ),
                "3_absolute_scale": _gate(
                    "passed",
                    "microlitre droplets are supported against 1g; the result "
                    "fails universal, bulk, and human-scale gravity",
                ),
                "4_falsification": _gate(
                    "passed",
                    "mapped pressure, residual acceleration, composition, "
                    "temperature, and streaming controls are concrete",
                ),
            },
            "disposition": "retain_as_small_sample_support_analog_only",
        },
        {
            "id": "P-021",
            "category": "laser_ablation_external_reaction_propulsion",
            "gates": {
                "1_source_coupling": _gate(
                    "passed",
                    "laser ablation ejects plume momentum and the target recoils",
                ),
                "2_constraints_validity": _gate(
                    "passed",
                    "impulse coupling is measured within material, pulse, and "
                    "plasma-shielding limits",
                ),
                "3_absolute_scale": _gate(
                    "passed",
                    "micropropulsion and debris impulses are meaningful; the "
                    "power and propellant scale fails internal artificial gravity",
                ),
                "4_falsification": _gate(
                    "passed",
                    "impulse balance, mass loss, plume angle, crater evolution, "
                    "and thermal controls are measurable",
                ),
            },
            "disposition": "retain_as_conventional_propulsion_only",
        },
    ]


def survival_rule_evaluation() -> dict[str, Any]:
    signal = quantum_signal_budget()
    classical = classical_countermodel_diagnostic()
    ledger = apparatus_and_confounder_ledger()
    classical_mapping_available = classical["maps_to_cold_atom_covariance"]
    # Mapping availability and the numerical threshold are separate gates.
    # The audited sources provide neither a same-observable calculation nor a
    # threshold result, so leave the latter explicitly unresolved.
    classical_below_fraction: bool | None = None
    backgrounds_bounded = all(
        item["qualified_below_fraction"] for item in ledger["confounders"]
    )
    components_coincident = ledger["component_coincidence"][
        "all_frozen_resources_demonstrated_together"
    ]
    survived = (
        signal["ideal_quantum_limited_snr"] >= 1.0
        and classical_below_fraction is True
        and backgrounds_bounded
        and components_coincident
    )
    return {
        "requires_snr_at_least_one": True,
        "ideal_quantum_limited_snr_at_frozen_benchmark": signal[
            "ideal_quantum_limited_snr"
        ],
        "classical_covariance_mapping_available": classical_mapping_available,
        "classical_covariance_below_predeclared_fraction": (
            classical_below_fraction
        ),
        "all_dominant_backgrounds_below_predeclared_fraction": (
            backgrounds_bounded
        ),
        "all_frozen_resources_demonstrated_together": components_coincident,
        "survived": survived,
        "disposition": (
            "retain_for_deepening"
            if survived
            else "parked_no_joint_detector_or_model_qualification"
        ),
        "reopen_condition": (
            "a simultaneous demonstrated resource set with SNR at least one, "
            "an executable prediction of the same covariance for the classical "
            "alternative, and every dominant same-observable background below "
            "one tenth of the target, or explicit user direction"
        ),
    }


def run_analysis() -> dict[str, Any]:
    signal = quantum_signal_budget()
    decision = survival_rule_evaluation()
    return {
        "provenance": implementation_provenance(),
        "geometry": oblate_geometry(),
        "quantum_signal_budget": signal,
        "ideal_sensitivity_diagnostic": ideal_sensitivity_diagnostic(),
        "classical_countermodel_diagnostic": (
            classical_countermodel_diagnostic()
        ),
        "apparatus_and_confounder_ledger": apparatus_and_confounder_ledger(),
        "gates": e040_gates(),
        "portfolio_refresh": portfolio_refresh(),
        "decision": {
            "status": decision["disposition"],
            "survived": decision["survived"],
            "claim_boundary": (
                "a negative detector/discrimination audit of this frozen "
                "proposal, not a rejection of quantum gravity, atom "
                "interferometry, or every gravity-mediated-entanglement test"
            ),
            "reopen_condition": decision["reopen_condition"],
            "next_best_step": (
                "run E-041 outside cold-atom entanglement, first verifying "
                "whether a rigorous joint 14-coefficient region is recoverable "
                "before any striped-source torque propagation"
            ),
        },
        "resource_accounting": {
            "pde_builds": 0,
            "pde_solves": 0,
            "hardware_actions": 0,
            "checkpoint_reads_or_writes": 0,
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

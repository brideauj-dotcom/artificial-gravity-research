"""E-039 reproducibility audit of a finite planar symmetron benchmark.

This is a closed-form, no-PDE, no-hardware audit of the CANNEX-like benchmark
in Millington and Udemba (2026), arXiv:2606.28423v1, and its public
Mathematica notebook at commit
``7a9a010a3bf83ae4c423869dc0afc404222a6b26``.

The screened-scalar model is kept hypothetical.  In the canonical convention
used here,

    A(phi) = 1 + phi**2/(2 M**2),
    V_eff = (rho/M**2 - mu**2) phi**2/2 + lambda phi**4/4,

and the source occupies ``-R <= x <= R``.  Source and detector exchange
momentum through the scalar field; their mounts close the mechanical reaction
ledger.  No result below is experimental evidence for a new interaction,
artificial gravity, inertial control, or propulsion.

The central reproducibility check is dimensional.  The public notebook uses
``1 m = 5.06e-6 eV^-1`` although ``1 m = 5.0677307e6 eV^-1``.  Its nominal
``R = 3 mm`` is therefore encoded as a roughly 3-fm half-thickness, a factor
of about 10**12 too small.  A thin-sheet matching approximation reproduces
the notebook's reported ``chi_0 = 0.355981767...`` from that encoded value,
so the error propagates into the displayed benchmark rather than being an
unused annotation.  Correcting the unit puts the plate in a deeply screened
regime that the preprint itself says its Heun implementation cannot evaluate
reliably.  This invalidates the physical CANNEX interpretation of the reported
numeric profile; it does not reject the paper's abstract finite-slab equations
or symmetron theory in general.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


CAMPAIGN = "E-039"
PAPER_ARXIV = "2606.28423v1"
PUBLIC_CODE_COMMIT = "7a9a010a3bf83ae4c423869dc0afc404222a6b26"
PUBLIC_NOTEBOOK = "planar_symmetron_quantum_corrections.nb"

# CODATA exact/derived conversion used by the audit.
HBAR_C_EV_M = 1.973_269_804_593_025e-7
METER_TO_INVERSE_EV = 1.0 / HBAR_C_EV_M

# The paper/notebook CANNEX-like benchmark.  R is the half-thickness, so the
# physical source is a 6-mm silica plate.
MU_EV = 1.0e-1
COUPLING_SCALE_M_EV = 1.0e6
SELF_COUPLING = 0.9
SOURCE_HALF_THICKNESS_M = 3.0e-3
SILICA_DENSITY_EV4 = 2.648 * 5.61e32 / 1.30e14
NOTEBOOK_METER_TO_INVERSE_EV = 5.06e-6
NOTEBOOK_REPORTED_CHI_0 = 0.355_981_767_096_225_1

# CANNEX values are design goals/projections, not achieved measured floors in
# the cited 2024 final-design paper.  They are retained to prevent a prospective
# threshold from being promoted to a measurement.
CANNEX_SEPARATION_UM = (3.0, 30.0)
CANNEX_PROJECTED_PRESSURE_PA = 1.0e-9
CANNEX_PROJECTED_PRESSURE_GRADIENT_PA_PER_M = 1.0e-3
CANNEX_100_DAY_PRESSURE_PA_AT_20_UM = 0.259e-9
CANNEX_100_DAY_GRADIENT_PA_PER_M_AT_20_UM = 0.0179e-3


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
        "paper": PAPER_ARXIV,
        "public_code_commit": PUBLIC_CODE_COMMIT,
        "public_notebook": PUBLIC_NOTEBOOK,
        "calculation_scope": (
            "closed-form dimensional and asymptotic reproducibility audit; "
            "no PDE build/solve, one-loop recomputation, new fit, hardware "
            "action, checkpoint access, or experimental-data generation"
        ),
    }


def _gate(status: str, statement: str) -> dict[str, str]:
    if status not in {"passed", "partial", "failed", "unknown"}:
        raise ValueError(f"invalid gate status: {status}")
    return {"status": status, "statement": statement}


def meters_to_inverse_ev(distance_m: float) -> float:
    if distance_m < 0.0:
        raise ValueError("distance must be nonnegative")
    return distance_m * METER_TO_INVERSE_EV


def inverse_ev_to_meters(distance_inverse_ev: float) -> float:
    if distance_inverse_ev < 0.0:
        raise ValueError("distance must be nonnegative")
    return distance_inverse_ev * HBAR_C_EV_M


def density_screening_ratio() -> float:
    """Return D = rho/(mu^2 M^2) for the notebook benchmark."""

    return SILICA_DENSITY_EV4 / (MU_EV**2 * COUPLING_SCALE_M_EV**2)


def thin_sheet_surface_value(half_thickness_inverse_ev: float) -> float:
    """Return the constant-interior thin-sheet matching approximation.

    For ``m_in R << 1``, set ``chi_0 ~= chi_R`` and integrate the classical
    field equation from the symmetry plane to the surface.  Matching to the
    vacuum exterior gives

        1 - chi_R**2 = sqrt(2) mu R (D - 1) chi_R.

    The stable positive root is used.  This is a diagnostic approximation,
    not a replacement for a finite-slab solution outside its thin-sheet
    regime.
    """

    if half_thickness_inverse_ev < 0.0:
        raise ValueError("half-thickness must be nonnegative")
    coefficient = (
        math.sqrt(2.0)
        * MU_EV
        * half_thickness_inverse_ev
        * (density_screening_ratio() - 1.0)
    )
    return 2.0 / (math.sqrt(coefficient**2 + 4.0) + coefficient)


def thick_wall_surface_value() -> float:
    """Return the linear dense-interior, semi-infinite surface estimate.

    With ``q=sqrt(D-1)``, matching ``chi' = mu*q*chi`` inside to
    ``chi'=mu*(1-chi**2)/sqrt(2)`` outside gives the stable positive root.
    This bounds the order of the classical surface value for ``q mu R >> 1``;
    it is not a one-loop result or a detector prediction.
    """

    q = math.sqrt(density_screening_ratio() - 1.0)
    return 2.0 / (
        math.sqrt(2.0 * q**2 + 4.0) + math.sqrt(2.0) * q
    )


def source_unit_audit() -> dict[str, Any]:
    encoded_r = (
        SOURCE_HALF_THICKNESS_M * NOTEBOOK_METER_TO_INVERSE_EV
    )
    physical_r = meters_to_inverse_ev(SOURCE_HALF_THICKNESS_M)
    encoded_equivalent_m = inverse_ev_to_meters(encoded_r)
    q = math.sqrt(density_screening_ratio() - 1.0)
    encoded_exponent = q * MU_EV * encoded_r
    physical_exponent = q * MU_EV * physical_r
    thin_value = thin_sheet_surface_value(encoded_r)
    thick_surface = thick_wall_surface_value()
    # In the linear dense interior, a symmetric slab has
    # chi_0/chi_R = 1/cosh(m_in R) < 2 exp(-m_in R).  Recording the
    # logarithm avoids an uninformative floating-point underflow to zero.
    center_log10_upper = (
        math.log10(2.0 * thick_surface)
        - physical_exponent / math.log(10.0)
    )
    return {
        "paper_source_half_thickness_m": SOURCE_HALF_THICKNESS_M,
        "paper_source_full_thickness_m": 2.0 * SOURCE_HALF_THICKNESS_M,
        "notebook_meter_to_inverse_eV": (
            NOTEBOOK_METER_TO_INVERSE_EV
        ),
        "correct_meter_to_inverse_eV": METER_TO_INVERSE_EV,
        "conversion_factor_correct_over_notebook": (
            METER_TO_INVERSE_EV / NOTEBOOK_METER_TO_INVERSE_EV
        ),
        "notebook_encoded_R_inverse_eV": encoded_r,
        "correct_R_inverse_eV": physical_r,
        "notebook_encoded_R_equivalent_m": encoded_equivalent_m,
        "notebook_encoded_full_thickness_equivalent_m": (
            2.0 * encoded_equivalent_m
        ),
        "mu_R_notebook": MU_EV * encoded_r,
        "mu_R_physical": MU_EV * physical_r,
        "density_screening_ratio_D": density_screening_ratio(),
        "interior_mass_over_mu_q": q,
        "m_in_R_notebook": encoded_exponent,
        "m_in_R_physical": physical_exponent,
        "reported_chi_0": NOTEBOOK_REPORTED_CHI_0,
        "thin_sheet_chi_from_notebook_R": thin_value,
        "thin_sheet_relative_error_vs_reported": abs(
            thin_value - NOTEBOOK_REPORTED_CHI_0
        ) / NOTEBOOK_REPORTED_CHI_0,
        "physical_thick_wall_surface_chi_estimate": thick_surface,
        "physical_center_chi_log10_upper_estimate": center_log10_upper,
        "finding": "notebook_half_thickness_is_approximately_1e12_too_small",
        "propagation": (
            "the thin-sheet matching value reproduces the reported chi_0, "
            "linking the conversion error to the displayed benchmark"
        ),
    }


def detector_and_geometry_audit() -> dict[str, Any]:
    separation_dimensionless = [
        MU_EV * meters_to_inverse_ev(value * 1.0e-6)
        for value in CANNEX_SEPARATION_UM
    ]
    return {
        "source": {
            "material": "silicon dioxide",
            "geometry": "laterally infinite planar idealization",
            "support_reaction": (
                "source mount and detector mount close the mechanical "
                "reaction ledger; neither support transfer function is "
                "modeled by the preprint benchmark"
            ),
        },
        "detector": {
            "name": "CANNEX parallel-plate concept",
            "observable": "pressure and pressure gradient between plates",
            "separation_um": list(CANNEX_SEPARATION_UM),
            "mu_times_separation": separation_dimensionless,
            "projected_pressure_sensitivity_Pa": (
                CANNEX_PROJECTED_PRESSURE_PA
            ),
            "projected_pressure_gradient_sensitivity_Pa_per_m": (
                CANNEX_PROJECTED_PRESSURE_GRADIENT_PA_PER_M
            ),
            "projected_100_day_pressure_Pa_at_about_20_um": (
                CANNEX_100_DAY_PRESSURE_PA_AT_20_UM
            ),
            "projected_100_day_gradient_Pa_per_m_at_about_20_um": (
                CANNEX_100_DAY_GRADIENT_PA_PER_M_AT_20_UM
            ),
            "threshold_status": (
                "prospective design targets, not achieved measured "
                "source-modulated thresholds"
            ),
        },
        "nonplanar_constraint_overlays": [
            {
                "experiment": "Panda et al. 2024 lattice atom interferometer",
                "geometry": "finite cylindrical source and atomic probe",
                "measured_observable": "source-mass acceleration anomaly",
                "measured_95_percent_abs_anomaly_bound_m_per_s2": 13.0e-9,
                "use": "parameter exclusion only",
                "planar_loop_profile_transfer_allowed": False,
            },
            {
                "experiment": "Yin et al. 2025 levitated force sensor",
                "geometry": "rotating finite source and levitated magnet",
                "measured_observable": "pattern-correlated force",
                "best_reported_95_percent_force_limit_N": 0.334_429_79e-15,
                "use": "parameter exclusion only",
                "planar_loop_profile_transfer_allowed": False,
            },
            {
                "experiment": "Dvorak et al. 2026 neutron interferometer",
                "geometry": "finite vacuum chamber and neutron paths",
                "measured_observable": "integrated neutron phase",
                "published_scalar_phase_threshold_rad": None,
                "use": "parameter exclusion only",
                "planar_loop_profile_transfer_allowed": False,
            },
            {
                "experiment": "Zhao et al. 2022 HUST torsion balance",
                "geometry": "finite patterned plates plus shielding foil",
                "measured_observable": "pattern-correlated torque",
                "measured_one_sigma_torque_resolution_N_m": 1.0e-17,
                "use": "parameter exclusion only",
                "planar_loop_profile_transfer_allowed": False,
            },
        ],
        "absolute_signal_status": (
            "not qualified: the reported relative force correction is built "
            "on the mis-scaled source, and no corrected two-plate pressure or "
            "pressure-gradient signal was computed"
        ),
        "geometry_rule": (
            "nonplanar nulls may constrain common model parameters, but the "
            "finite-planar one-loop profile may not be applied to them without "
            "a controlled response calculation"
        ),
    }


def e039_gates() -> dict[str, dict[str, str]]:
    return {
        "1_source_coupling": _gate(
            "partial",
            "the scalar coupling and nominal slab are explicit, but the public "
            "executable source is about 1e12 too thin and the two-plate detector "
            "plus full support/backreaction observable are not instantiated",
        ),
        "2_constraints_validity": _gate(
            "failed",
            "the corrected plate lies at m_in R about 5e7, within the regime "
            "the preprint says its Heun evaluation cannot cover reliably; a "
            "systematic constraint reassessment is explicitly left for future work",
        ),
        "3_absolute_scale": _gate(
            "failed",
            "the reported roughly 10-percent relative profile has no qualified "
            "absolute CANNEX pressure or gradient after correcting R; the cited "
            "CANNEX 1 nPa and 1 mPa/m values are prospective design targets",
        ),
        "4_falsification": _gate(
            "partial",
            "a corrected planar two-plate calculation would be falsifiable, but "
            "current atom, levitated, and neutron nulls are nonplanar overlays "
            "and no measured planar threshold is frozen",
        ),
    }


def survival_rule_evaluation() -> dict[str, Any]:
    audit = source_unit_audit()
    source_valid = math.isclose(
        audit["notebook_encoded_R_inverse_eV"],
        audit["correct_R_inverse_eV"],
        rel_tol=1.0e-6,
    )
    corrected_benchmark_has_validated_numerical_result = False
    qualified_absolute_signal = False
    measured_planar_threshold = False
    survived = (
        source_valid
        and corrected_benchmark_has_validated_numerical_result
        and qualified_absolute_signal
        and measured_planar_threshold
    )
    return {
        "requires_correct_physical_source": True,
        "physical_source_instantiated_by_public_notebook": source_valid,
        "corrected_benchmark_has_validated_numerical_result": (
            corrected_benchmark_has_validated_numerical_result
        ),
        "preprint_large_D_or_R_accuracy_warning_applies": True,
        "qualified_corrected_absolute_planar_signal": (
            qualified_absolute_signal
        ),
        "measured_planar_source_modulated_threshold": (
            measured_planar_threshold
        ),
        "survived": survived,
        "disposition": (
            "retain_for_deepening"
            if survived
            else "parked_source_unit_and_detector_scale_gates_failed"
        ),
        "reopen_condition": (
            "materially new corrected physical-thickness calculation with "
            "explicit detector response and a measured planar threshold, or "
            "explicit user direction"
        ),
    }


def portfolio_refresh() -> list[dict[str, Any]]:
    """Return genuinely distinct opportunities after the P-008 closure."""

    return [
        {
            "id": "P-008",
            "name": "quantum-corrected planar symmetron profile",
            "category": "hypothetical_screened_scalar_precision_test",
            "gates": e039_gates(),
            "disposition": "deepened_then_parked_in_e039",
        },
        {
            "id": "P-012",
            "name": "cold-atom gravitationally induced entanglement",
            "category": "real_gravity_quantum_precision_witness",
            "gates": {
                "1_source_coupling": _gate(
                    "partial",
                    "Newtonian mass-density coupling and atom-number covariance "
                    "are explicit; trap, laser, shield, and support reaction "
                    "ledgers need freezing",
                ),
                "2_constraints_validity": _gate(
                    "partial",
                    "weak-field dynamics are controlled, but classical-gravity "
                    "quantum-field models can also produce entanglement",
                ),
                "3_absolute_scale": _gate(
                    "partial",
                    "detector-scale proposals require near-Planck total mass "
                    "and long integration; no gravitational entanglement has "
                    "been measured",
                ),
                "4_falsification": _gate(
                    "partial",
                    "mass, distance, time, covariance, electromagnetic, "
                    "collision, loss, trap, and shield scalings can "
                    "discriminate models if predeclared",
                ),
            },
            "disposition": "next_bounded_no_hardware_discrimination_audit",
        },
        {
            "id": "P-013",
            "name": "directional reactor-neutrino force",
            "category": "standard_model_precision_force",
            "gates": {
                "1_source_coupling": _gate(
                    "partial",
                    "weak coupling and reactor flux are explicit; finite-core "
                    "geometry and support ledger are not frozen",
                ),
                "2_constraints_validity": _gate(
                    "passed",
                    "low-energy Standard Model calculation is controlled when "
                    "angular and energy spreads are retained",
                ),
                "3_absolute_scale": _gate(
                    "failed",
                    "even an ideal directional signal is about 1e2-1e3 below "
                    "current fifth-force sensitivity before realistic smearing",
                ),
                "4_falsification": _gate(
                    "partial",
                    "reactor on/off and directional torque tests exist but "
                    "operations-correlated backgrounds dominate",
                ),
            },
            "disposition": "park_until_material_sensitivity_or_flux_change",
        },
        {
            "id": "P-014",
            "name": "minimal Einstein-Cartan torsion",
            "category": "real_spacetime_torsion_theory",
            "gates": {
                "1_source_coupling": _gate(
                    "passed",
                    "intrinsic spin sources algebraic torsion and a local "
                    "four-fermion interaction",
                ),
                "2_constraints_validity": _gate(
                    "passed",
                    "minimal Einstein-Cartan theory has no propagating vacuum "
                    "torsion",
                ),
                "3_absolute_scale": _gate(
                    "failed",
                    "exterior torsion is exactly zero and local corrections are "
                    "Planck suppressed outside extreme density",
                ),
                "4_falsification": _gate(
                    "failed",
                    "a separated polarized source cannot generate the claimed "
                    "remote field in the minimal theory",
                ),
            },
            "disposition": "park_minimal_theory",
        },
        {
            "id": "P-015",
            "name": "configurable curved-spacetime BEC simulator",
            "category": "analog_dynamics_not_real_curvature",
            "gates": {
                "1_source_coupling": _gate(
                    "passed",
                    "trap and interaction ramps create an acoustic metric while "
                    "atoms, lasers, and trap close the reaction ledger",
                ),
                "2_constraints_validity": _gate(
                    "passed",
                    "interpretation is valid only in the hydrodynamic phonon "
                    "regime",
                ),
                "3_absolute_scale": _gate(
                    "passed",
                    "curvature-sign and pair-correlation signals are measured "
                    "analog observables, not real spacetime curvature",
                ),
                "4_falsification": _gate(
                    "passed",
                    "curvature sign, ramp history, and correlation controls "
                    "have been executed",
                ),
            },
            "disposition": "retain_as_analog_benchmark_only",
        },
        {
            "id": "P-016",
            "name": "E.T.PACK electrodynamic tether",
            "category": "external_reaction_propulsion_not_internal_gravity",
            "gates": {
                "1_source_coupling": _gate(
                    "passed",
                    "I dL cross B exchanges momentum with the ionosphere and "
                    "geomagnetic field",
                ),
                "2_constraints_validity": _gate(
                    "partial",
                    "hardware is qualified but orbital plasma/current "
                    "performance awaits flight demonstration",
                ),
                "3_absolute_scale": _gate(
                    "partial",
                    "a 420-m tether in 30 microtesla gives 0.0126 N per ampere; "
                    "current and orientation are mission dependent",
                ),
                "4_falsification": _gate(
                    "passed",
                    "deployment, current-voltage response, and orbit residuals "
                    "can be preregistered against drag and plasma controls",
                ),
            },
            "disposition": "watch_2026_2027_flight_not_internal_gravity",
        },
    ]


def source_ledger() -> list[dict[str, str]]:
    return [
        {
            "key": "planar_symmetron_preprint",
            "citation": "P. Millington and M. Udemba, arXiv:2606.28423v1 (2026)",
            "use": (
                "finite-planar equations, claimed CANNEX benchmark, and "
                "stated numerical validity limits"
            ),
        },
        {
            "key": "planar_symmetron_public_code",
            "citation": f"mudemba/planar-symmetron-quantum-corrections commit {PUBLIC_CODE_COMMIT}",
            "use": "executable source values and meter-to-inverse-eV conversion",
        },
        {
            "key": "CANNEX_design",
            "citation": "Haghmoradi et al., Physics 6, 355-419 (2024), arXiv:2403.10998",
            "use": "parallel-plate geometry and prospective pressure/gradient targets",
        },
        {
            "key": "nonplanar_symmetron_nulls",
            "citation": (
                "Panda et al., Nature 631, 515-520 (2024); Yin et al., "
                "Nature Astronomy 9, 598-607 (2025); Dvorak et al., "
                "arXiv:2606.03440v1 (2026)"
            ),
            "use": "constraint overlays only; no finite-planar one-loop profile transfer",
        },
        {
            "key": "portfolio_refresh",
            "citation": (
                "PRA accepted article 10.1103/l62d-gz5c; Nature 2025 "
                "DOI:10.1038/s41586-025-09595-7; JHEP 02 (2023) 092; "
                "Rev. Mod. Phys. 48, 393 (1976); Nature 611, 260-264 "
                "(2022); E.T.PACK EIC status (2026)"
            ),
            "use": "five genuinely distinct replacement opportunities",
        },
    ]


def run_analysis() -> dict[str, Any]:
    candidates = portfolio_refresh()
    return {
        "provenance": implementation_provenance(),
        "model": {
            "canonical_convention": {
                "matter_coupling": "A(phi)=1+phi^2/(2 M^2)",
                "effective_potential": "(rho/M^2-mu^2)phi^2/2+lambda phi^4/4",
                "source_domain": "-R <= x <= R",
            },
            "benchmark": {
                "mu_eV": MU_EV,
                "M_eV": COUPLING_SCALE_M_EV,
                "lambda": SELF_COUPLING,
                "rho_silica_eV4": SILICA_DENSITY_EV4,
            },
        },
        "source_unit_audit": source_unit_audit(),
        "detector_and_geometry": detector_and_geometry_audit(),
        "gates": e039_gates(),
        "survival_rule": survival_rule_evaluation(),
        "portfolio": {
            "candidate_count": len(candidates),
            "candidates": candidates,
            "selected_for_deepening": "P-008",
            "screen_result": (
                "No candidate supports practical artificial gravity or bulk "
                "inertial control; P-008 fails the physical-source and absolute-"
                "detector-scale gates, while P-012 is the next bounded precision audit"
            ),
        },
        "decision": {
            "status": "parked_source_unit_and_detector_scale_gates_failed",
            "selected_candidate": "P-008",
            "reproducibility_result": (
                "the public notebook's inverse-eV conversion makes the nominal "
                "3-mm half-thickness approximately 1e12 too small, and a thin-"
                "sheet asymptotic reconstruction reproduces its reported chi_0"
            ),
            "physics_result": (
                "correcting R gives m_in R about 5e7, outside the preprint's "
                "reported reliable numerical regime; no corrected absolute "
                "planar detector signal is established"
            ),
            "claim_boundary": (
                "this parks the reported CANNEX-scale numerical opportunity, "
                "not the abstract finite-slab formalism or symmetron models generally"
            ),
            "next_best_step": (
                "run E-040 as a bounded no-hardware P-012 audit: freeze the "
                "accepted 2026 cold-atom geometry and covariance/SNR budget, "
                "then compare quantum-gravity and classical-gravity entanglement scalings"
            ),
        },
        "sources": source_ledger(),
        "resource_accounting": {
            "pde_builds": 0,
            "pde_solves": 0,
            "one_loop_recomputations": 0,
            "new_numerical_fits": 0,
            "hardware_actions": 0,
            "checkpoint_reads_or_writes": 0,
            "new_compute_or_resource_purchase": 0,
        },
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


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

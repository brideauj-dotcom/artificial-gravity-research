"""E-041 public joint-region audit for the dimension-six gravity SME.

The 2016 combined HUST/IU analysis reports a simultaneous fit of fourteen
effective coefficients, but its public record contains only marginal central
values and marginal ``2 sigma`` widths.  This module records the public-data
inventory and demonstrates why those marginals do not identify an exact or
stated-confidence projection through the proposed 2026 five-stripe transfer
without an actual joint likelihood, covariance, samples, or equivalent
simultaneous region.

This is a statistical-identifiability and source-quality audit.  It performs
no PDE solve, apparatus simulation, hardware action, or claim of observed
Lorentz violation, artificial gravity, inertial control, spacetime
engineering, or propulsion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Sequence


CAMPAIGN = "E-041"
COMBINED_ANALYSIS_DOI = "10.1103/PhysRevLett.117.071102"
STRIPE_DESIGN_DOI = "10.3390/sym18040559"

# Table II of Shao et al. (2016).  The quoted widths are explicitly 2 sigma
# and have units 1e-9 m^2.  "Independent coefficients" names a coordinate
# basis/identifiable degrees of freedom; it does not state statistical
# independence; no covariance was recovered on the audited surfaces below.
COEFFICIENT_TABLE_2SIGMA_1E_MINUS9_M2 = (
    ("XXXX", 6.4, 32.9),
    ("XXXY", 0.0, 8.1),
    ("XXXZ", -2.0, 2.6),
    ("XXYY", -0.9, 10.9),
    ("XXYZ", 1.1, 1.2),
    ("XXZZ", -2.6, 17.1),
    ("XYYY", 3.9, 8.1),
    ("XYYZ", -0.6, 1.2),
    ("XYZZ", -1.0, 1.0),
    ("XZZZ", -8.1, 10.3),
    ("YYYY", 7.0, 32.9),
    ("YYYZ", 0.3, 2.6),
    ("YYZZ", -2.5, 17.1),
    ("YZZZ", 3.6, 10.2),
)


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
        "combined_analysis_doi": COMBINED_ANALYSIS_DOI,
        "stripe_design_doi": STRIPE_DESIGN_DOI,
        "scope": (
            "public statistical-artifact inventory and analytical "
            "non-identifiability demonstration; no fit reconstruction, "
            "torque propagation, PDE, hardware, or checkpoint access"
        ),
    }


def combined_analysis_public_record() -> dict[str, Any]:
    """Return the dated public-artifact audit without universal absence claims."""

    return {
        "fit_description": "simultaneous fit of 14 effective coefficients",
        "coefficient_basis_size": len(COEFFICIENT_TABLE_2SIGMA_1E_MINUS9_M2),
        "coefficient_table": [
            {
                "label": label,
                "central_in_1e_minus9_m2": central,
                "marginal_2sigma_in_1e_minus9_m2": width,
            }
            for label, central, width in COEFFICIENT_TABLE_2SIGMA_1E_MINUS9_M2
        ],
        "publicly_exposed": {
            "fourteen_central_values": True,
            "fourteen_marginal_2sigma_widths": True,
            "thirty_six_fourier_central_values_and_marginal_errors": True,
            "analytical_sidereal_harmonic_form": True,
        },
        "audit_date": "2026-08-13",
        "audited_surfaces": [
            "APS article record and outbound supplement links",
            "arXiv 1607.06095 abstract, PDF, and source archive",
            "Indiana University and HUST article repositories located by title/DOI",
            "Crossref and DataCite DOI metadata and relations",
            "Zenodo and HEPData title/DOI searches",
        ],
        "not_recovered_on_audited_surfaces": {
            "coefficient_covariance_or_correlation": True,
            "joint_likelihood_or_chi_square": True,
            "posterior_or_likelihood_samples": True,
            "joint_confidence_ellipsoid_or_contour": True,
            "fourier_mode_covariance": True,
            "numerical_combined_design_matrix": True,
            "nuisance_parameter_covariance": True,
            "raw_time_series_or_fit_residuals": True,
        },
        "source_package_contents": ["paper.tex", "fig1.eps"],
        "supplement_recovered_on_audited_surfaces": False,
        "statistical_independence_claimed": False,
        "interpretation_note": (
            "independent coefficients denotes an identifiable coordinate "
            "basis, not a diagonal covariance or probabilistic independence"
        ),
    }


def covariance_pair(rho: float) -> tuple[tuple[float, float], ...]:
    """Return a unit-variance two-parameter covariance with correlation rho."""

    if not -1.0 <= rho <= 1.0:
        raise ValueError("rho must lie in [-1, 1]")
    return ((1.0, rho), (rho, 1.0))


def quadratic_form(
    vector: Sequence[float], matrix: Sequence[Sequence[float]]
) -> float:
    if len(vector) != len(matrix) or any(
        len(row) != len(vector) for row in matrix
    ):
        raise ValueError("matrix must be square and match vector length")
    return sum(
        vector[i] * matrix[i][j] * vector[j]
        for i in range(len(vector))
        for j in range(len(vector))
    )


def projection_nonidentifiability_demo(rho_abs: float = 0.99) -> dict[str, Any]:
    """Show that identical marginals permit incompatible harmonic errors.

    For a harmonic proportional to ``k1+k2``, covariance matrices with
    correlations ``+rho`` and ``-rho`` have identical unit marginal
    variances.  Their harmonic variances are respectively ``2+2 rho`` and
    ``2-2 rho``.  Thus marginal widths alone cannot determine even one linear
    transfer uncertainty, much less a fourteen-parameter support function.
    """

    if not 0.0 < rho_abs < 1.0:
        raise ValueError("rho_abs must lie strictly between zero and one")
    transfer = (1.0, 1.0)
    positive = covariance_pair(rho_abs)
    negative = covariance_pair(-rho_abs)
    variance_positive = quadratic_form(transfer, positive)
    variance_negative = quadratic_form(transfer, negative)
    return {
        "transfer_vector": list(transfer),
        "shared_marginal_variances": [1.0, 1.0],
        "positive_correlation": rho_abs,
        "negative_correlation": -rho_abs,
        "projection_variance_positive": variance_positive,
        "projection_variance_negative": variance_negative,
        "projection_variance_ratio": (
            variance_positive / variance_negative
        ),
        "projection_standard_deviation_ratio": math.sqrt(
            variance_positive / variance_negative
        ),
        "both_covariances_positive_definite": True,
        "conclusion": (
            "the same published marginals permit materially different "
            "uncertainty for the same linear torque harmonic"
        ),
    }


def marginal_coverage_diagnostic(
    marginal_coverage: float = 0.954_499_736_103_641_6,
    dimensions: int = 14,
) -> dict[str, Any]:
    """Return the product coverage under an explicitly hypothetical model.

    The product is *not* assigned to the 2016 fit. It merely shows that under
    independent Gaussian coordinates, fourteen marginal two-sigma intervals
    would cover jointly only about 52 percent, not 95 percent. Under arbitrary
    dependence, the Frechet/Bonferroni bounds are much wider. Neither result
    supplies a stated-confidence joint region for the actual fit.
    """

    if not 0.0 < marginal_coverage < 1.0 or dimensions < 1:
        raise ValueError("invalid coverage or dimension")
    return {
        "hypothesis_only": "independent Gaussian coordinates",
        "marginal_coverage": marginal_coverage,
        "dimensions": dimensions,
        "independence_product_joint_coverage": marginal_coverage**dimensions,
        "arbitrary_dependence_frechet_lower": max(
            0.0, dimensions * marginal_coverage - (dimensions - 1)
        ),
        "arbitrary_dependence_frechet_upper": marginal_coverage,
        "is_valid_joint_region_for_2016_fit": False,
        "reason": (
            "no fit covariance or joint distribution was recovered on the "
            "audited public surfaces; a Cartesian product of marginals has no "
            "stated simultaneous coverage and is not a qualified 95-percent "
            "region for this audit"
        ),
    }


def required_ellipsoid_projection_formula() -> dict[str, str]:
    return {
        "joint_region": "(k-mu)^T Sigma^-1 (k-mu) <= q",
        "harmonic": "tau=a^T k",
        "support_radius": "sqrt(q * a^T Sigma a)",
        "missing_inputs": (
            "Sigma or an equivalent joint likelihood/region, plus the full "
            "numerical five-stripe harmonic transfer vector a"
        ),
    }


def stripe_design_public_record() -> dict[str, Any]:
    """Record the 2026 proposal disclosures without treating them as data."""

    return {
        "status": "proposal_and_parameter_optimization_not_measurement",
        "source_and_test_material": "tungsten",
        "plate_dimensions_mm": [19.8, 19.8, 1.3],
        "surface_gap_mm": [0.4, 1.0],
        "shield": "30 um BeCu foil; closest test-mass distance about 200 um",
        "source_gap_modulation": True,
        "matrix_structure_equations_published": True,
        "matrix_dimensions": {
            "A1": "2x2",
            "A2": "4x4",
            "A3": "4x4",
            "A4": "2x2",
            "A5": "2x2",
        },
        "geometric_integral_definition_published": True,
        "determinant_root_maxima_published": True,
        "published_root_rule": {
            "A1_A2_A3": "square root of absolute determinant",
            "A4_A5": "fourth root of absolute determinant",
        },
        "dimensionally_consistent_common_transfer_units": False,
        "dimensional_issue": (
            "a determinant of an n by n matrix with transfer entries Gamma "
            "has units Gamma^n; common Gamma units require an nth root. The "
            "paper uses the dimensionally correct square root for A1, but "
            "square roots for A2/A3 (4 by 4) and fourth roots for A4/A5 "
            "(2 by 2). This can preserve rankings inside one "
            "fixed matrix group but not the claimed common units or an "
            "absolute cross-group transfer interpretation."
        ),
        "five_stripe_selected_by_determinant_metric": True,
        "full_numerical_transfer_matrix_entries_published": False,
        "machine_readable_geometry_or_code_published": False,
        "numerical_optimum_angles_tabulated": False,
        "measured_five_stripe_harmonics_published": False,
        "measured_five_stripe_same_harmonic_noise_published": False,
        "estimated_noise_Nm": {
            "C0_total": 11.7e-16,
            "Cm_Sm_total_estimated": 0.45e-16,
        },
        "noise_note": (
            "the paper calls these uncertainties estimated for the proposed "
            "design; they are not measured five-stripe source-modulated data"
        ),
        "data_availability": (
            "article contributions only; further inquiries directed to authors"
        ),
    }


def e041_gates() -> dict[str, dict[str, str]]:
    return {
        "1_source_coupling": _gate(
            "partial",
            "the nonminimal pure-gravity SME coupling and tungsten stripe "
            "source/test concept are explicit, but exact numerical transfer, "
            "actuator, and support ledgers were not recovered in the audited "
            "paper and linked artifacts",
        ),
        "2_constraints_validity": _gate(
            "failed",
            "the 2016 simultaneous fit exposes marginal two-sigma results, but "
            "no stated-confidence joint 14-parameter region was recovered; "
            "the preregistered propagation is therefore unauthorized",
        ),
        "3_absolute_scale": _gate(
            "unknown",
            "no justified jointly allowed absolute torque can be computed; "
            "artificial-gravity scale was not evaluated because the proposal "
            "is a precision test and supplies no artificial-gravity evidence",
        ),
        "4_falsification": _gate(
            "partial",
            "sidereal/source modulation is concrete, but no measured five-"
            "stripe harmonics or complete same-unit background budget was "
            "recovered in the audited proposal artifacts",
        ),
    }


def portfolio_refresh() -> list[dict[str, Any]]:
    """Return distinct leads after parking P-017; none is promoted here."""

    return [
        {
            "id": "P-017",
            "category": "lorentz_violating_gravity_precision_force",
            "gates": e041_gates(),
            "disposition": "deepened_then_parked_in_e041",
        },
        {
            "id": "P-022",
            "category": "human_scale_rotational_inertial_gravity",
            "gates": {
                "1_source_coupling": _gate(
                    "passed",
                    "a short-arm centrifuge produces inertial loading and "
                    "reacts through its rotor, motor, bearings, and facility",
                ),
                "2_constraints_validity": _gate(
                    "partial",
                    "mechanics is established, while a recent long bed-rest "
                    "trial still requires dose, adaptation, and population "
                    "generalization",
                ),
                "3_absolute_scale": _gate(
                    "passed",
                    "the trial delivered about 1g at estimated center of mass "
                    "and 2g at the feet, a meaningful but strongly graded "
                    "conventional inertial load rather than localized curvature",
                ),
                "4_falsification": _gate(
                    "partial",
                    "radius, rpm, dose, physiology, and a non-centrifuged bed-"
                    "rest comparator are concrete, but endpoint hierarchy and "
                    "cross-system efficacy still require the E-042 audit",
                ),
            },
            "disposition": "retain_as_established_human_scale_baseline",
        },
        {
            "id": "P-023",
            "category": "electrohydrodynamic_simulated_gravity_fluid_control",
            "gates": {
                "1_source_coupling": _gate(
                    "passed",
                    "electrodes drive dielectric-fluid body forces and close "
                    "reaction through the power supply and structure",
                ),
                "2_constraints_validity": _gate(
                    "partial",
                    "fluid and electrostatic regimes are specified but "
                    "geometry, charge injection, heating, and stability remain "
                    "application-specific",
                ),
                "3_absolute_scale": _gate(
                    "partial",
                    "spacecraft bubble and liquid-film control is demonstrated "
                    "at apparatus scale, but no same-unit force-density or "
                    "flow-performance bound was audited here; real curvature "
                    "and universal acceleration fail",
                ),
                "4_falsification": _gate(
                    "partial",
                    "applied EHD and DEP potentials, heat flux, film height, "
                    "gravity state, and bubble/film observations are recorded; "
                    "a same-unit force, heating, and reaction audit remains",
                ),
            },
            "disposition": "retain_as_spacecraft_fluid_analog_only",
        },
        {
            "id": "P-024",
            "category": "superconducting_levitated_real_gravity_sensor",
            "gates": {
                "1_source_coupling": _gate(
                    "passed",
                    "ordinary source gravity acts on a levitated milligram "
                    "sensor while magnetic suspension and mounts close reaction",
                ),
                "2_constraints_validity": _gate(
                    "passed",
                    "weak-field Newtonian response and calibrated magnetic "
                    "readout operate in a measured regime",
                ),
                "3_absolute_scale": _gate(
                    "passed",
                    "a 2.4 kg source produced a modeled 1030 aN coupling to the "
                    "0.4 mg sensor with 0.5 fN/sqrt(Hz) force noise; this is "
                    "meaningful metrology, not an artificial-gravity source",
                ),
                "4_falsification": _gate(
                    "partial",
                    "source modulation and calibration are concrete, but the "
                    "measured response was 0.35 +/- 0.02 of the modeled force "
                    "and platform motion, tilt, SQUID-cable effects, and excess "
                    "vibration remain identified confounders",
                ),
            },
            "disposition": "retain_as_real_curvature_metrology_only",
        },
        {
            "id": "P-025",
            "category": "mechanical_array_ambient_dark_matter_force_search",
            "gates": {
                "1_source_coupling": _gate(
                    "partial",
                    "a passing dark-matter field or object is ambient rather "
                    "than actuated; mechanical response and supports are specified",
                ),
                "2_constraints_validity": _gate(
                    "partial",
                    "coupling and coherence assumptions are model-dependent "
                    "and existing constraints must be overlaid",
                ),
                "3_absolute_scale": _gate(
                    "failed",
                    "pure-gravity reach requires about 80 dB quantum-noise "
                    "reduction with 100^3 sensors totaling about 600 tonnes; "
                    "new long-range "
                    "interactions may remain detector-scale",
                ),
                "4_falsification": _gate(
                    "partial",
                    "coherent tracks, array timing, injections, seismic "
                    "rejection, and vetoes are definable but not demonstrated "
                    "at target scale",
                ),
            },
            "disposition": "park_pure_gravity_retain_new_interaction_watch",
        },
        {
            "id": "P-026",
            "category": "pellet_beam_external_reaction_propulsion",
            "gates": {
                "1_source_coupling": _gate(
                    "passed",
                    "accelerated pellets transfer ordinary momentum to the "
                    "spacecraft and carry equal reaction",
                ),
                "2_constraints_validity": _gate(
                    "partial",
                    "ballistic and momentum physics is standard but long-range "
                    "beam generation, capture, pointing, and losses are unvalidated",
                ),
                "3_absolute_scale": _gate(
                    "partial",
                    "the Phase-I concept models pellets above 120 km/s and a "
                    "1 ton payload to 500 AU in under 20 years, not demonstrated "
                    "performance; internal artificial gravity fails",
                ),
                "4_falsification": _gate(
                    "partial",
                    "pellet speed, divergence, capture efficiency, momentum "
                    "transfer, debris, and thermal loads need proof-of-concept "
                    "tests",
                ),
            },
            "disposition": "retain_as_conventional_propulsion_concept_only",
        },
    ]


def survival_rule_evaluation() -> dict[str, Any]:
    joint_region_available = False
    full_transfer_available = False
    return {
        "joint_region_available": joint_region_available,
        "full_numerical_five_stripe_transfer_available": full_transfer_available,
        "absolute_allowed_torque_propagation_authorized": (
            joint_region_available and full_transfer_available
        ),
        "allowed_harmonic_snr": None,
        "background_fraction_tests": None,
        "survived": False,
        "disposition": "parked_joint_region_and_transfer_not_recoverable",
        "prohibited_substitutions": [
            "diagonal covariance inferred from marginal widths",
            "Cartesian product of marginal two-sigma intervals as a joint region",
            "one-at-a-time Tables III/IV limits as simultaneous constraints",
            "determinant-root maxima as full harmonic transfer matrices",
            "estimated proposal noise as measured five-stripe data",
        ],
        "reopen_condition": (
            "location or release of the 2016 joint likelihood, covariance, "
            "samples, or "
            "equivalent repeatable fit products together with a complete "
            "numerical five-stripe transfer and measured same-harmonic budget, "
            "or explicit user direction"
        ),
    }


def run_analysis() -> dict[str, Any]:
    decision = survival_rule_evaluation()
    return {
        "provenance": implementation_provenance(),
        "combined_analysis_public_record": combined_analysis_public_record(),
        "projection_nonidentifiability": projection_nonidentifiability_demo(),
        "marginal_coverage_diagnostic": marginal_coverage_diagnostic(),
        "required_projection_formula": required_ellipsoid_projection_formula(),
        "stripe_design_public_record": stripe_design_public_record(),
        "gates": e041_gates(),
        "portfolio_refresh": portfolio_refresh(),
        "decision": {
            "status": decision["disposition"],
            "survived": decision["survived"],
            "claim_boundary": (
                "a public statistical and transfer-artifact limitation, not "
                "evidence against Lorentz violation or every SME experiment"
            ),
            "reopen_condition": decision["reopen_condition"],
            "next_best_step": (
                "run E-042 as a bounded human-outcome audit of the distinct "
                "short-arm centrifuge bed-rest evidence, freezing dose, radius, "
                "rpm, endpoints, adverse effects, and generalization limits"
            ),
        },
        "resource_accounting": {
            "pde_builds": 0,
            "pde_solves": 0,
            "fit_reconstructions": 0,
            "torque_propagations": 0,
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

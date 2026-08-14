"""E-042 bounded evidence audit of the 60-day AGBRESA trial.

This module freezes the human-loading geometry and nominal dose, separates
controlled between-arm evidence from within-arm change, records the prospective
registry limitations, and applies the four portfolio gates.  It is an evidence
and dimensional-analysis artifact, not a clinical recommendation, hardware
design, experiment, or claim of real spacetime curvature, inertial control, or
propulsion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


CAMPAIGN = "E-042"
AUDIT_DATE = "2026-08-14"
STANDARD_GRAVITY_M_S2 = 9.80665
MEAN_RPM = 30.5
RPM_RANGE = (29.1, 32.2)
APPARATUS_RADIUS_M = 3.8
REPORTED_FOOT_RADIUS_RANGE_M = (1.729, 2.113)

TRIAL_REGISTRY = "DRKS00015677"
BONE_DOI = "10.1093/jbmr/zjaf119"
TOLERABILITY_DOI = "10.1371/journal.pone.0239228"
PROTOCOL_DOI = "10.3389/fphys.2022.976926"
MUSCLE_DOI = "10.1007/s00421-021-04673-w"
ORTHOSTATIC_DOI = "10.1007/s10286-023-00959-5"
CARDIAC_DOI = "10.1002/ehf2.13103"
AUTONOMIC_DOI = "10.3389/fcvm.2023.1250727"


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
        "audit_date": AUDIT_DATE,
        "module": {
            "path": str(path.relative_to(path.parents[1])),
            "sha256": _sha256_file(path),
        },
        "primary_identifiers": {
            "registry": TRIAL_REGISTRY,
            "bone_bmat_doi": BONE_DOI,
            "tolerability_doi": TOLERABILITY_DOI,
            "protocol_doi": PROTOCOL_DOI,
            "muscle_aerobic_doi": MUSCLE_DOI,
            "orthostatic_doi": ORTHOSTATIC_DOI,
            "cardiac_doi": CARDIAC_DOI,
            "autonomic_doi": AUTONOMIC_DOI,
        },
        "scope": (
            "one registered 60-day bed-rest platform and its directly relevant "
            "primary reports; no broad centrifuge survey or hardware expansion"
        ),
    }


def acceleration_m_s2(radius_m: float, rpm: float) -> float:
    if radius_m < 0.0 or rpm < 0.0:
        raise ValueError("radius and rpm must be nonnegative")
    omega = rpm * 2.0 * math.pi / 60.0
    return omega * omega * radius_m


def radius_for_g(g_level: float, rpm: float) -> float:
    if g_level < 0.0 or rpm <= 0.0:
        raise ValueError("g level must be nonnegative and rpm positive")
    omega = rpm * 2.0 * math.pi / 60.0
    return g_level * STANDARD_GRAVITY_M_S2 / (omega * omega)


def mechanics_audit() -> dict[str, Any]:
    omega = MEAN_RPM * 2.0 * math.pi / 60.0
    com_radius = radius_for_g(1.0, MEAN_RPM)
    foot_radius = radius_for_g(2.0, MEAN_RPM)
    sensitivity = []
    for rpm in RPM_RANGE:
        sensitivity.append(
            {
                "rpm": rpm,
                "derived_1g_radius_m": radius_for_g(1.0, rpm),
                "derived_2g_radius_m": radius_for_g(2.0, rpm),
            }
        )
    return {
        "established_relation": "a = omega^2 r",
        "mean_rpm": MEAN_RPM,
        "reported_rpm_range": list(RPM_RANGE),
        "mean_omega_rad_s": omega,
        "apparatus_radius_m": APPARATUS_RADIUS_M,
        "reported_foot_plate_radius_range_m": list(
            REPORTED_FOOT_RADIUS_RANGE_M
        ),
        "derived_mean_1g_com_radius_m": com_radius,
        "derived_mean_2g_foot_radius_m": foot_radius,
        "derived_acceleration_gradient_g_per_m": omega * omega
        / STANDARD_GRAVITY_M_S2,
        "g_level_at_apparatus_radius_at_mean_rpm": acceleration_m_s2(
            APPARATUS_RADIUS_M, MEAN_RPM
        )
        / STANDARD_GRAVITY_M_S2,
        "reported_inner_ear_g_approx": 0.30,
        "rpm_endpoint_sensitivity": sensitivity,
        "mean_2g_radius_inside_reported_foot_range": (
            REPORTED_FOOT_RADIUS_RANGE_M[0]
            <= foot_radius
            <= REPORTED_FOOT_RADIUS_RANGE_M[1]
        ),
        "geometry_correction": (
            "3.8 m is the apparatus radius, not the participant foot radius; "
            "the individually positioned foot plates were 1.729-2.113 m from "
            "the rotation axis"
        ),
        "reaction_ledger": (
            "centripetal loading reacts through participant restraints and "
            "foot plate into the arm, rotor, motor, bearings, facility, and Earth"
        ),
        "category_boundary": (
            "ordinary rotating-frame inertial loading with a steep head-to-foot "
            "gradient; not universal free fall or engineered spacetime curvature"
        ),
    }


def nominal_dose_audit() -> dict[str, Any]:
    days = 60
    plateau_minutes_per_day = 30
    nominal_hours = days * plateau_minutes_per_day / 60.0
    return {
        "participants_completed_hdt60": 24,
        "participants_per_arm": 8,
        "sex_distribution": {
            "all": {"men": 16, "women": 8},
            "control": {"men": 6, "women": 2},
            "continuous": {"men": 5, "women": 3},
            "intermittent": {"men": 5, "women": 3},
        },
        "control": "strict 6-degree head-down bed rest; no centrifugation",
        "continuous": "one 30-minute plateau per day",
        "intermittent": "six 5-minute plateaus per day",
        "intermittent_break_discrepancy": {
            "registry_minutes": 5,
            "primary_reports_minutes": 3,
            "resolved": False,
        },
        "nominal_plateau_days": days,
        "nominal_plateau_minutes_per_day": plateau_minutes_per_day,
        "nominal_plateau_hours_per_participant": nominal_hours,
        "nominal_fraction_of_campaign_time": nominal_hours / (days * 24.0),
        "nominal_com_g_hours_per_participant": nominal_hours,
        "nominal_foot_g_hours_per_participant": 2.0 * nominal_hours,
        "nominal_inner_ear_g_hours_per_participant": 0.30 * nominal_hours,
        "dose_proxy_warning": (
            "g-hours are only an integrated mechanical exposure proxy and do "
            "not establish physiological equivalence, efficacy, or a minimum dose"
        ),
        "specific_tolerability_report": {
            "sessions": 960,
            "prematurely_terminated": 10,
            "participants_with_termination": 6,
            "presyncope_terminations": 7,
            "severe_motion_sickness_terminations": 1,
            "biopsy_pain_terminations": 2,
            "serious_adverse_events": 0,
        },
        "later_protocol_overview": {
            "interrupted_sessions": 12,
            "participants": 7,
            "aborted_sessions": 10,
            "resumed_after_break": 2,
            "classification_disagrees_with_specific_report": True,
        },
        "exact_delivered_minutes_recoverable_from_public_reports": False,
        "exercise_coupling": (
            "participants could use trained calf, trunk, and gluteal muscle "
            "contractions to avoid presyncope; activation varied substantially"
        ),
    }


def registry_and_design_audit() -> dict[str, Any]:
    return {
        "registration": TRIAL_REGISTRY,
        "registration_date": "2018-10-02",
        "trial_year": 2019,
        "prospective": True,
        "registered_target_n": 24,
        "allocation": (
            "semi-random: campaign 1 was random within sex balance; campaign 2 "
            "and four late recruits were allocated to balance age, sex, height, "
            "and weight across and between campaigns; assignments were revealed "
            "after baseline on bed-rest day 1"
        ),
        "conventional_random_sequence_for_all_participants": False,
        "allocation_concealment_details_recovered": False,
        "sequence_generation_details_recovered": False,
        "sham_centrifuge_control": False,
        "participant_blinding_feasible": False,
        "strict_outcome_assessor_and_analyst_blinding": False,
        "prospectively_linked_protocol_or_sap_supplying_endpoint_hierarchy_recovered": False,
        "individual_participant_data_public": False,
        "registered_outcome_hierarchy": (
            "both primary and secondary registry fields point to the same "
            "17-page investigator endpoint appendix"
        ),
        "prospective_appendix_audit": {
            "document_date": "2018-09-28",
            "lumbar_spine_dxa_bmd_explicitly_listed": True,
            "bone_marrow_adipose_tissue_term_present": False,
            "fat_fraction_term_present": False,
            "broad_mri_vertebral_composition_endpoint_present": True,
            "publication_primary_bmat_hierarchy_recoverable": False,
        },
        "baseline_imbalances": {
            "bone_paper_bmi_p": 0.043,
            "orthostatic_time_to_presyncope_p": 0.047,
        },
        "analog_limit": (
            "supine restricted-motion bed rest is not ambulatory spaceflight, "
            "free locomotion, or high-rpm rotating-habitat adaptation"
        ),
    }


def outcome_matrix() -> list[dict[str, Any]]:
    return [
        {
            "system": "lumbar_bone_marrow_adipose_tissue",
            "paper_defined_primary": True,
            "prospective_specific_hierarchy_recovered": False,
            "control_change_percentage_points_95ci": [3.93, -0.28, 8.14],
            "continuous_change_percentage_points_95ci": [-1.21, -4.01, 1.59],
            "intermittent_change_percentage_points_95ci": [0.0, -2.48, 2.48],
            "descriptive_control_minus_continuous_percentage_points": 5.14,
            "descriptive_control_minus_intermittent_percentage_points": 3.93,
            "controlled_omnibus_p": 0.032,
            "pairwise_controlled_contrasts_reported": False,
            "pairwise_control_vs_continuous_effect_ci_p": None,
            "pairwise_control_vs_intermittent_effect_ci_p": None,
            "multiple_testing_correction": False,
            "decision": "qualified_positive_controlled_signal",
            "qualification": (
                "semi-random allocation, small unshammed n=8 arms, unclear "
                "prospective primary status, no pairwise contrasts, BMI "
                "imbalance, and no multiplicity correction"
            ),
        },
        {
            "system": "lumbar_bone_mineral_density",
            "prospectively_listed": True,
            "control_hdt60_change_g_cm2_95ci": [-0.028, -0.045, -0.010],
            "control_within_arm_p": 0.007,
            "continuous_hdt30_change_g_cm2_95ci": [-0.019, -0.037, -0.002],
            "continuous_within_arm_p": 0.036,
            "controlled_between_arm_difference_significant": False,
            "decision": "controlled_efficacy_not_demonstrated",
            "qualification": (
                "absence of a within-arm significant loss is not evidence that "
                "an arm differs from control; the paper reports no intervention difference"
            ),
        },
        {
            "system": "orthostatic_tolerance_time_to_presyncope",
            "prospectively_listed_primary": True,
            "change_seconds_mean_sd": {
                "control": [-801, 354],
                "continuous": [-323, 235],
                "intermittent": [-296, 508],
            },
            "baseline_seconds_mean": {
                "control": 1376,
                "continuous": 934,
                "intermittent": 896,
            },
            "derived_post_seconds_mean": {
                "control": 575,
                "continuous": 611,
                "intermittent": 600,
            },
            "bedrest_by_countermeasure_interaction_p": 0.0249,
            "post_bedrest_between_group_p": 0.5279,
            "baseline_between_group_p": 0.047,
            "decision": "qualified_positive_change_score_interaction_signal",
            "qualification": (
                "prospective endpoint and corrected analysis, but semi-random "
                "allocation, only eight per arm, baseline-advantaged control, "
                "convergent post means, and passive tilt/LBNP may not predict active standing"
            ),
        },
        {
            "system": "aerobic_exercise_capacity",
            "vo2max_group_by_time_significant": False,
            "decision": "failed_for_30_minute_passive_protocol",
        },
        {
            "system": "muscle_function",
            "group_by_time_results": {
                "jump_power": {
                    "p": 0.001,
                    "p_relation": "less_than",
                    "percent_changes_iag_cag_control": [-25, -26, -33],
                },
                "plantar_flexion_strength": {
                    "p": 0.003,
                    "percent_changes_iag_cag_control": [-35, -31, -48],
                },
                "plantar_flexion_rate_of_force_development": {
                    "p": 0.020,
                    "percent_changes_iag_cag_control": [-28, -12, -40],
                },
            },
            "post_hoc_arm_contrasts_performed": False,
            "decision": "partial_mitigation_not_maintenance",
            "qualification": (
                "multiple outcomes and no post-hoc arm contrasts; variable "
                "anti-presyncope muscle contractions are a treatment-component confounder"
            ),
        },
        {
            "system": "cardiac_structure_and_function",
            "between_group_differences_observed": False,
            "decision": "failed_to_abolish_cardiovascular_deconditioning",
        },
        {
            "system": "autonomic_cardiovascular_control",
            "bedrest_by_intervention_interactions_observed": False,
            "decision": "failed_to_prevent_autonomic_control_changes",
        },
        {
            "system": "tolerability_and_safety",
            "premature_termination_fraction": 10 / 960,
            "presyncope_termination_fraction": 7 / 960,
            "participants_with_termination_fraction": 6 / 16,
            "continuous_motion_sickness_mean": 3.05,
            "intermittent_motion_sickness_mean": 1.58,
            "motion_sickness_group_p": 0.001,
            "frequent_isolated_pvcs": "2 continuous-arm participants on 14 days",
            "decision": "feasible_under_medical_supervision_with_nonzero_events",
            "qualification": (
                "healthy screened participants, symptom-triggered muscle pumping, "
                "restricted head motion, and no sham limit generalization"
            ),
        },
    ]


def claim_kill_matrix() -> list[dict[str, Any]]:
    return [
        {
            "claim": "the apparatus delivered meaningful axial inertial loading",
            "supported": True,
            "reason": "reported rpm/radii agree with a=omega^2 r at 1g COM and 2g feet",
        },
        {
            "claim": "30 minutes per day prevented vertebral BMAT accumulation",
            "supported": False,
            "reason": (
                "a qualified controlled omnibus signal exists, but specific "
                "preregistration, pairwise superiority, multiplicity control, and replication do not"
            ),
        },
        {
            "claim": "30 minutes per day prevented lumbar BMD loss",
            "supported": False,
            "reason": "the paper explicitly reports no significant between-arm differences",
        },
        {
            "claim": "30 minutes per day is a validated multipurpose countermeasure",
            "supported": False,
            "reason": (
                "aerobic capacity and cardiac deconditioning failed while muscle, "
                "BMAT, and orthostatic results were endpoint-specific and qualified"
            ),
        },
        {
            "claim": "intermittent dosing is physiologically superior to continuous dosing",
            "supported": False,
            "reason": "no robust direct efficacy contrast established schedule superiority",
        },
        {
            "claim": "the trial establishes a minimum effective artificial-gravity dose",
            "supported": False,
            "reason": "only one nominal plateau duration and two schedules were tested",
        },
        {
            "claim": "the trial demonstrates flight efficacy or rotating-habitat comfort",
            "supported": False,
            "reason": "bed-rest analog, restricted head motion, medical supervision, and no locomotion",
        },
        {
            "claim": "centrifugation creates real spacetime curvature or inertial control",
            "supported": False,
            "reason": "all loading and backreaction are ordinary rotating-frame mechanics",
        },
    ]


def p022_gates() -> dict[str, dict[str, str]]:
    return {
        "1_source_coupling": _gate(
            "passed",
            "the motor-driven centrifuge, participant contact loading, and "
            "reaction through rotor, supports, facility, and Earth are explicit",
        ),
        "2_constraints_validity": _gate(
            "partial",
            "mechanics and supervised 60-day feasibility are compatible with "
            "known physics, but small-sample inference, endpoint hierarchy, "
            "bed-rest external validity, and protocol-report discrepancies remain",
        ),
        "3_absolute_scale": _gate(
            "passed",
            "29.1-32.2 rpm produced about 0.30g at the inner ear, 1g at estimated "
            "COM, and 2g at the feet for a nominal 30 hours per participant",
        ),
        "4_falsification": _gate(
            "passed",
            "a prospective semi-random concurrent comparator and measurable system-specific "
            "outcomes produced both positive and negative results; sham absence, "
            "muscle pumping, baseline imbalance, and multiplicity are identified",
        ),
    }


def portfolio_refresh() -> list[dict[str, Any]]:
    return [
        {
            "id": "P-022",
            "category": "human_scale_rotational_inertial_gravity",
            "gates": p022_gates(),
            "disposition": "deepened_bounded_signals_broad_program_remains_parked",
        },
        {
            "id": "P-023",
            "category": "electrohydrodynamic_simulated_gravity_fluid_control",
            "gates": {
                "1_source_coupling": _gate("passed", "electrodes and dielectric-fluid coupling are explicit"),
                "2_constraints_validity": _gate("partial", "charge injection, heating, stability, and geometry need audit"),
                "3_absolute_scale": _gate("partial", "apparatus-scale fluid control is relevant; same-unit force density is unaudited"),
                "4_falsification": _gate("partial", "film and bubble observables exist; reaction and thermal budgets remain"),
            },
            "disposition": "queue_e043_same_unit_force_reaction_audit",
        },
        {
            "id": "P-024",
            "category": "superconducting_levitated_real_gravity_sensor",
            "gates": {
                "1_source_coupling": _gate("passed", "ordinary source gravity and magnetic suspension are explicit"),
                "2_constraints_validity": _gate("passed", "weak-field Newtonian response is measured in its validity regime"),
                "3_absolute_scale": _gate("passed", "modeled 1030 aN coupling and 0.5 fN/sqrt(Hz noise are detector-meaningful"),
                "4_falsification": _gate("partial", "0.35 +/- 0.02 response and tilt, platform, cable, and vibration confounders remain"),
            },
            "disposition": "retain_real_gravity_metrology_only",
        },
        {
            "id": "P-025",
            "category": "mechanical_array_new_interaction_search",
            "gates": {
                "1_source_coupling": _gate("partial", "ambient dark-matter coupling is model-dependent rather than actuated"),
                "2_constraints_validity": _gate("partial", "existing force constraints and coherence assumptions need freezing"),
                "3_absolute_scale": _gate("failed", "pure gravity requires about 80 dB noise reduction and roughly 600 tonnes of sensors"),
                "4_falsification": _gate("partial", "coherent tracks and vetoes are definable but not demonstrated at scale"),
            },
            "disposition": "park_pure_gravity_retain_new_interaction_watch",
        },
        {
            "id": "P-026",
            "category": "pellet_beam_external_reaction_propulsion",
            "gates": {
                "1_source_coupling": _gate("passed", "pellets carry momentum and close reaction conventionally"),
                "2_constraints_validity": _gate("partial", "beam generation, divergence, capture, debris, and heating are unvalidated"),
                "3_absolute_scale": _gate("partial", "Phase-I trajectory scale is modeled, not demonstrated"),
                "4_falsification": _gate("partial", "speed, divergence, capture, and thermal tests are concrete but undone"),
            },
            "disposition": "retain_conventional_propulsion_concept_only",
        },
    ]


def survival_rule_evaluation() -> dict[str, Any]:
    return {
        "mechanical_source_and_reaction_pass": True,
        "human_scale_loading_pass": True,
        "qualified_bmat_signal": True,
        "qualified_orthostatic_signal": True,
        "lumbar_bmd_controlled_efficacy_pass": False,
        "aerobic_capacity_pass": False,
        "multipurpose_countermeasure_pass": False,
        "minimum_dose_identified": False,
        "continuous_vs_intermittent_superiority_identified": False,
        "spaceflight_generalization_authorized": False,
        "real_curvature_or_inertial_control": False,
        "disposition": "bounded_endpoint_signals_but_multipurpose_claim_rejected",
        "broad_e008_reopened": False,
        "reopen_condition": (
            "materially new prospectively hierarchical and adequately powered "
            "human evidence with objective delivered-dose records and appropriate "
            "sham and exercise controls, or explicit user direction"
        ),
    }


def future_falsification_design() -> dict[str, Any]:
    return {
        "queued": False,
        "reason": "broad centrifuge program E-008 remains parked",
        "design_if_reopened": {
            "arms": [
                "bed-rest control with sham handling",
                "centrifugation only",
                "matched exercise only",
                "centrifugation plus matched exercise",
            ],
            "requirements": [
                "allocation concealment and preregistered sequence",
                "one multiplicity-controlled primary endpoint per system",
                "powered between-arm contrasts and sex-stratified recruitment",
                "participant-level rpm, radius, plateau time, interruptions, and muscle activation",
                "prespecified adverse-event and adherence analysis",
                "active-standing and ambulatory transfer endpoints",
            ],
            "kill_rule": (
                "retain a multipurpose claim only if multiplicity-controlled "
                "between-arm benefits survive in every prospectively required "
                "domain; otherwise park it"
            ),
        },
    }


def run_analysis() -> dict[str, Any]:
    decision = survival_rule_evaluation()
    return {
        "provenance": implementation_provenance(),
        "mechanics": mechanics_audit(),
        "dose": nominal_dose_audit(),
        "registry_and_design": registry_and_design_audit(),
        "outcomes": outcome_matrix(),
        "claim_kill_matrix": claim_kill_matrix(),
        "gates": p022_gates(),
        "portfolio_refresh": portfolio_refresh(),
        "future_falsification_design": future_falsification_design(),
        "decision": {
            "status": decision["disposition"],
            "survived_as_bounded_human_inertial_opportunity": True,
            "survived_as_multipurpose_or_flight_countermeasure": False,
            "broad_program_reopened": decision["broad_e008_reopened"],
            "claim_boundary": (
                "endpoint-specific evidence from one small bed-rest trial, not "
                "real gravity, universal loading, flight efficacy, or a minimum dose"
            ),
            "next_best_step": (
                "run E-043 on P-023 as a distinct same-unit electrohydrodynamic "
                "fluid-force, heating, and full-reaction audit"
            ),
        },
        "resource_accounting": {
            "pde_builds": 0,
            "pde_solves": 0,
            "clinical_interventions": 0,
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

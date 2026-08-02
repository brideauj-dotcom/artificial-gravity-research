"""E-035 no-solve feasibility and preregistration audit.

E-034 proposed a fixed coupled sequence

    (h, m) = (1/8, 4), (1/16, 5), (1/32, 6)

at ``R=80`` as a possible screen for derivative contraction.  This module
audits that proposal before any new nonlinear solve.  It computes exact grid
counts, applies a newly explicit *full positive-support* source-transition
criterion, projects memory and one-campaign core runtime from the retained
E-028 baseline, and records what remains to be specified before a common-node
derivative protocol could be frozen.

The audit deliberately does not load a checkpoint, build a PDE system, solve
an equation, or write a field.  Its result is a numerical-method boundary for
a hypothetical PDE.  It is not evidence for a physical field, artificial
gravity, inertial control, spacetime engineering, faster-than-light travel,
or propulsion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
import time
from typing import Any

import numpy as np

import models.e025_axisymmetric_wide_2hessian as e025
import models.e033_potential_error_stencils as e033
import models.e034_postprocessor_transfer as e034


CAMPAIGN = "E-035"
RADIAL_MAX = 80.0
GRID_SPECIFICATIONS = (
    (0.125, 4),
    (0.0625, 5),
    (0.03125, 6),
)
FOURTH_GRID_SPECIFICATION = (0.015625, 7)
BASELINE_SPACING = 0.125
BASELINE_DIRECTIONAL_RADIUS = 4
MINIMUM_SOURCE_TRANSITION_CELLS = 6.0
GIB = 1024**3

# Proposed project resource policies. They are operating limits, not physics
# or numerical-analysis theorems. E-035 enforces the limits that can be tested
# from its projections and labels the rest as future measured gates.
SOFT_RSS_CAP_BYTES = 32 * GIB
HARD_RSS_CAP_BYTES = 40 * GIB
MINIMUM_HOST_RESERVE_BYTES = 16 * GIB
RESOURCE_TARGET_HOST_MEMORY_BYTES = 64 * GIB
SYSTEM_BUILD_WALL_CAP_SECONDS = 15.0 * 60.0
NIGHTLY_GRID_WALL_CAP_SECONDS = 55.0 * 60.0

# Retained E-028 h=1/8,m=4 measurements.  The peak is the maximum across the
# first five accepted stages, rather than the smaller invocation-local value
# in the final stage-6 report.  These values are embedded so E-035 never needs
# to load or mutate the immutable checkpoint.
E028_RESOURCE_BASELINE = {
    "accepted_checkpoint_sha256": (
        "ff82363833c84e416e020a8df56d6067b6b1f7612c41f30f6499d6b95690babb"
    ),
    "unknowns": 322_319,
    "directional_bases": 12,
    "stored_directional_operators": 25,
    "rss_before_build_bytes": 69_582_848,
    "rss_after_build_bytes": 637_386_752,
    "campaign_peak_rss_bytes": 1_968_783_360,
    "build_seconds": 15.211359665961936,
    "stage_1_through_6_seconds": 163.80988170701312,
    "stage_1_through_6_solver_seconds": 118.28265807894059,
    "stage_1_through_6_other_seconds": 45.527223628072534,
    "stage_1_through_6_newton_iterations": 42,
    "stage_1_through_6_gmres_iterations": 1_685,
}

# A no-solve E-035 build-accounting calibration on the same baseline grid.
# It sums CSR data/indices/indptr, boundary offsets, coordinates, and index
# map.  It excludes Python construction lists, temporaries, curvature arrays,
# AMG, and Krylov storage, which are represented by the empirical peak range.
E035_STATIC_BASELINE = {
    "unknowns": 322_319,
    "directional_bases": 12,
    "stored_directional_operators": 25,
    "csr_bytes": 317_833_452,
    "boundary_offset_bytes": 64_463_800,
    "coordinate_bytes": 5_157_104,
    "index_map_bytes": 3_287_048,
    "accounted_static_bytes": 390_741_404,
    "build_accounting_seconds": 14.09,
    "provenance_status": (
        "transcribed no-solve measurement independently repeated 2026-08-02; "
        "no durable raw calibration report was retained"
    ),
}

FIXED_POINTS = (
    (8.75, 0.75),
    (5.75, 0.5),
    (6.0, 0.5),
    (6.25, 0.5),
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def implementation_provenance() -> dict[str, Any]:
    """Fingerprint the audit and imported numerical definitions it uses."""

    repository_root = Path(__file__).resolve().parents[1]
    paths = {
        "e035_audit": Path(__file__).resolve(),
        "e034_provisional_gate": Path(e034.__file__).resolve(),
        "e033_recovery": Path(e033.__file__).resolve(),
        "e025_grid_and_source": Path(e025.__file__).resolve(),
        "research_requirements": repository_root / "requirements-research.txt",
    }
    return {
        "campaign": CAMPAIGN,
        "campaign_schema": 1,
        "modules": {
            name: {
                "path": str(path.relative_to(repository_root)),
                "sha256": _sha256_file(path),
            }
            for name, path in paths.items()
        },
        "lineage_policy": (
            "No checkpoint or retained field is read or written. Accepted "
            "lineage remains immutable E-028 stage 6/12."
        ),
    }


def runtime_provenance() -> dict[str, Any]:
    """Record the lightweight runtime used for deterministic arithmetic."""

    try:
        physical_memory = int(
            os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
        )
    except (AttributeError, OSError, ValueError):
        physical_memory = None
    return {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "host_physical_memory_bytes": physical_memory,
    }


def exact_quarter_disk_unknowns(radial_max: float, spacing: float) -> int:
    """Count nodes satisfying rho>=0, z>=0, rho^2+z^2<R^2 exactly."""

    if radial_max <= 0.0 or spacing <= 0.0:
        raise ValueError("radial_max and spacing must be positive")
    intervals_float = radial_max / spacing
    intervals = int(round(intervals_float))
    if not math.isclose(
        intervals_float, intervals, rel_tol=0.0, abs_tol=1.0e-12
    ):
        raise ValueError("radial_max must be an integer multiple of spacing")
    squared_radius = intervals * intervals
    return sum(
        math.isqrt(squared_radius - radial_index * radial_index - 1) + 1
        for radial_index in range(intervals)
    )


def _grid_row(spacing: float, directional_radius: int) -> dict[str, Any]:
    source = e025.SmoothAnnulusSpec()
    bases = e025.primitive_meridional_bases(directional_radius)
    delta_theta = e025.directional_resolution(directional_radius)
    positive_support_inner_radius = (
        source.inner_radius - source.radial_smoothing_width / 2.0
    )
    nominal_transition_width = (
        source.inner_radius * source.angular_smoothing_width
    )
    positive_support_transition_infimum = (
        positive_support_inner_radius * source.angular_smoothing_width
    )
    return {
        "spacing": spacing,
        "directional_radius": directional_radius,
        "unknowns": exact_quarter_disk_unknowns(RADIAL_MAX, spacing),
        "directional_bases": len(bases),
        "stored_directional_operators": 2 * len(bases) + 1,
        "directional_resolution_radians": delta_theta,
        "h_over_directional_resolution": spacing / delta_theta,
        "maximum_wide_stencil_physical_reach": spacing
        * max(math.hypot(first, second) for first, second in bases),
        "nominal_inner_radius_transition_width": nominal_transition_width,
        "nominal_inner_radius_transition_cells": (
            nominal_transition_width / spacing
        ),
        "positive_support_inner_radius": positive_support_inner_radius,
        "positive_support_transition_width_infimum": (
            positive_support_transition_infimum
        ),
        "positive_support_transition_cells_infimum": (
            positive_support_transition_infimum / spacing
        ),
    }


def coupled_grid_geometry() -> dict[str, Any]:
    """Audit coupled spatial, directional, source, and common-node geometry."""

    candidate_rows = [_grid_row(*specification) for specification in GRID_SPECIFICATIONS]
    fourth = _grid_row(*FOURTH_GRID_SPECIFICATION)
    directional_ratios = [
        candidate_rows[index]["directional_resolution_radians"]
        / candidate_rows[index + 1]["directional_resolution_radians"]
        for index in range(len(candidate_rows) - 1)
    ]
    fourth_directional_ratio = (
        candidate_rows[-1]["directional_resolution_radians"]
        / fourth["directional_resolution_radians"]
    )
    directional_effective_exponents = [
        math.log2(ratio)
        for ratio in directional_ratios + [fourth_directional_ratio]
    ]
    source_gate_passes = all(
        row["positive_support_transition_cells_infimum"]
        >= MINIMUM_SOURCE_TRANSITION_CELLS
        for row in candidate_rows
    )
    coupled_monotonicity_passes = all(
        candidate_rows[index + 1]["h_over_directional_resolution"]
        < candidate_rows[index]["h_over_directional_resolution"]
        and candidate_rows[index + 1][
            "maximum_wide_stencil_physical_reach"
        ]
        < candidate_rows[index]["maximum_wide_stencil_physical_reach"]
        for index in range(len(candidate_rows) - 1)
    )
    return {
        "radial_max": RADIAL_MAX,
        "candidate_grids": candidate_rows,
        "fourth_grid": fourth,
        "source_transition_audit": {
            "minimum_required_cells": MINIMUM_SOURCE_TRANSITION_CELLS,
            "passed": source_gate_passes,
            "coarsest_wide_reach_over_positive_support_transition": (
                candidate_rows[0]["maximum_wide_stencil_physical_reach"]
                / candidate_rows[0][
                    "positive_support_transition_width_infimum"
                ]
            ),
            "coarsest_wide_reach_is_smaller_than_transition": (
                candidate_rows[0]["maximum_wide_stencil_physical_reach"]
                < candidate_rows[0][
                    "positive_support_transition_width_infimum"
                ]
            ),
            "comparison_to_e034_half_height_proxy": (
                "E-034 correctly evaluated the half-height proxy "
                "inner_radius*angular_smoothing_width=0.8 r0, which gives "
                "6.4 cells at h=0.125 r0. That proxy does not certify the full "
                "positive support. The radial window has positive support "
                "arbitrarily close to r=5 r0, where the local tangential scale "
                "tends to 0.5 r0 and spans only 4 cells. No source-amplitude "
                "cutoff was preregistered."
            ),
            "epistemic_limit": (
                "The 0.5 r0 value is the positive-support infimum of the local "
                "tangential scale; the source amplitude tends to zero at the "
                "exact inner endpoint. It equals 0.5 m only under the fiducial "
                "r0=1 m translation. A later amplitude cutoff would define a "
                "different protocol."
            ),
            "criterion_status": (
                "new E-035 prospective policy, not a retroactive reinterpretation "
                "of E-034's half-height proxy"
            ),
        },
        "coupled_monotonicity_passed": coupled_monotonicity_passes,
        "spatial_refinement_ratio": 2.0,
        "directional_resolution_ratios": directional_ratios,
        "fourth_directional_resolution_ratio": fourth_directional_ratio,
        "directional_effective_exponents_against_h_halving": (
            directional_effective_exponents
        ),
        "single_parameter_geometrically_similar_family": False,
        "rate_interpretation": (
            "Because h halves while directional resolution changes by "
            "nonconstant factors near 1.2, log2(D_coarse/D_fine) is only an "
            "effective contraction index along this coupled path. It is not "
            "a pure spatial order, Richardson extrapolate, or GCI input."
        ),
    }


def common_node_preregistration() -> dict[str, Any]:
    """Record exact mapped points and the still-incomplete mask design."""

    grid_maps = []
    for spacing, directional_radius in GRID_SPECIFICATIONS:
        indices = []
        for rho, z in FIXED_POINTS:
            radial_index = int(round(rho / spacing))
            axial_index = int(round(z / spacing))
            if not math.isclose(
                radial_index * spacing, rho, rel_tol=0.0, abs_tol=1.0e-13
            ) or not math.isclose(
                axial_index * spacing, z, rel_tol=0.0, abs_tol=1.0e-13
            ):
                raise RuntimeError("a frozen ROI point is not an exact node")
            indices.append([radial_index, axial_index])
        grid_maps.append(
            {
                "spacing": spacing,
                "directional_radius": directional_radius,
                "indices": indices,
                "coarsest_index_multiplier": int(
                    round(BASELINE_SPACING / spacing)
                ),
            }
        )
    return {
        "design_status": "incomplete_prospective_design_not_executable",
        "exactly_enumerated_scope": (
            "Only the four signed diagnostic points and their integer maps are "
            "enumerated. Whole masks, boundary-valid supports, and recovery "
            "weights are not yet generated or validated."
        ),
        "unresolved_prerequisites": [
            "enumerate every h=0.125 mask node and exact 2^level restriction map",
            "verify every native support stays inside the declared domain treatment",
            "freeze even-z reflection at z=0 and the rho-axis exclusion rule",
            "generate and validate scale-covariant C_h, C_2h, and Q_2h weights",
        ],
        "restriction_policy": (
            "Evaluate every native field with its native shrinking-support "
            "operator, then restrict values to the h=0.125 node set by exact "
            "integer index maps. No interpolation or moving extremum is used."
        ),
        "fixed_points_rho_z": [list(point) for point in FIXED_POINTS],
        "grid_maps": grid_maps,
        "candidate_mask_predicates_not_enumerated": {
            "full_positive_source_support": (
                "25<rho^2+z^2<1089 and 0<=z<rho*tan(0.1)"
            ),
            "radial_transition": (
                "full_positive_source_support and "
                "(25<rho^2+z^2<121 or 729<rho^2+z^2<1089)"
            ),
            "angular_transition": (
                "25<rho^2+z^2<1089 and 0<z<rho*tan(0.1)"
            ),
            "inner_feature_rectangle": "4<=rho<=12 and 0<=z<=4",
            "global_interior": (
                "rho>=0.5 and sqrt(rho^2+z^2)<=78.5"
            ),
            "priority_rule": (
                "Source and transition masks are primary. The global mask is "
                "secondary because quiet far volume can dilute local error."
            ),
        },
        "candidate_quadrature_not_validated": (
            "Use the same h=0.125 cylindrical weights for every restricted "
            "field: 4*pi*h0^2*rho with half weight at z=0. The common factor "
            "may cancel only after it is recorded."
        ),
        "candidate_native_recovery_families_not_generated": {
            "C_h": "native centered support radius h_j",
            "C_2h": "native centered support radius 2*h_j",
            "Q_2h": (
                "the exact E-033 dimensionless degree-two design with support "
                "radius 2*h_j; no adaptive patch, weights, or axis fallback"
            ),
        },
        "recovery_stability": {
            "design_rank": int(e033.QUADRATIC_RANK),
            "design_condition_number_2": float(
                e033.QUADRATIC_SINGULAR_VALUES[0]
                / e033.QUADRATIC_SINGULAR_VALUES[-1]
            ),
            "scaled_weight_rule": (
                "h_j^2*w is identical across grids for pure/mixed second "
                "derivatives and h_j*rho*w is identical for the local "
                "azimuthal component, within 128 machine eps"
            ),
            "manufactured_gate_scope": (
                "Polynomial and band-limited manufactured tests validate the "
                "postprocessor implementation only; they do not enclose the "
                "unknown nonlinear solution's Hessian error."
            ),
            "status": (
                "requirements only; per-grid weights, reflected-axis behavior, "
                "and boundary-valid supports remain unimplemented"
            ),
        },
    }


def resource_feasibility() -> dict[str, Any]:
    """Project retained-operator memory and runtime without allocating grids."""

    baseline = E028_RESOURCE_BASELINE
    static = E035_STATIC_BASELINE
    baseline_unknowns = baseline["unknowns"]
    baseline_bases = baseline["directional_bases"]
    baseline_operators = baseline["stored_directional_operators"]
    build_increment = (
        baseline["rss_after_build_bytes"] - baseline["rss_before_build_bytes"]
    )
    post_build_peak = (
        baseline["campaign_peak_rss_bytes"]
        - baseline["rss_after_build_bytes"]
    )
    per_operator_node_bytes = (
        static["csr_bytes"] + static["boundary_offset_bytes"]
    ) / (static["stored_directional_operators"] * static["unknowns"])
    fixed_node_bytes = (
        static["coordinate_bytes"] + static["index_map_bytes"]
    ) / static["unknowns"]

    host_memory = RESOURCE_TARGET_HOST_MEMORY_BYTES
    host_limit = host_memory - MINIMUM_HOST_RESERVE_BYTES
    effective_hard_cap = min(HARD_RSS_CAP_BYTES, host_limit)
    rows = []
    for specification in GRID_SPECIFICATIONS + (FOURTH_GRID_SPECIFICATION,):
        geometry = _grid_row(*specification)
        unknowns = geometry["unknowns"]
        bases = geometry["directional_bases"]
        operators = geometry["stored_directional_operators"]
        unknown_ratio = unknowns / baseline_unknowns
        basis_ratio = bases / baseline_bases
        operator_work_ratio = (
            unknowns * operators / (baseline_unknowns * baseline_operators)
        )
        basis_work_ratio = unknown_ratio * basis_ratio
        projected_build_peak = (
            baseline["rss_before_build_bytes"]
            + build_increment * operator_work_ratio
        )
        projected_peak_lower = (
            projected_build_peak + post_build_peak * unknown_ratio
        )
        projected_peak_upper = (
            projected_build_peak + post_build_peak * basis_work_ratio
        )
        calibrated_static = unknowns * (
            per_operator_node_bytes * operators + fixed_node_bytes
        )
        curvature_tensor_bytes = 3 * bases * unknowns * 8
        candidate_array_bytes = bases * unknowns * 8
        gmres_restart_50_basis_bytes = 53 * unknowns * 8
        projected_build_seconds = baseline["build_seconds"] * operator_work_ratio
        projected_stage_seconds_lower = (
            baseline["stage_1_through_6_solver_seconds"] * unknown_ratio
            + baseline["stage_1_through_6_other_seconds"] * basis_work_ratio
        )
        projected_stage_seconds_upper = (
            baseline["stage_1_through_6_seconds"] * basis_work_ratio
        )
        projected_total_seconds_lower = (
            projected_build_seconds + projected_stage_seconds_lower
        )
        projected_total_seconds_upper = (
            projected_build_seconds + projected_stage_seconds_upper
        )
        if projected_build_peak > effective_hard_cap:
            status = "blocked_before_build"
        elif projected_build_seconds > SYSTEM_BUILD_WALL_CAP_SECONDS:
            status = "blocked_by_system_build_wall_cap"
        elif projected_peak_upper > effective_hard_cap:
            status = "blocked_by_conservative_peak_envelope"
        elif projected_peak_upper > SOFT_RSS_CAP_BYTES:
            status = "marginal_above_soft_cap"
        elif projected_total_seconds_lower > NIGHTLY_GRID_WALL_CAP_SECONDS:
            status = "blocked_by_nightly_wall_cap"
        else:
            status = "one_campaign_core_within_caps_full_screen_unbudgeted"
        rows.append(
            {
                **geometry,
                "calibrated_static_bytes": int(math.ceil(calibrated_static)),
                "one_curvature_tensor_bytes": curvature_tensor_bytes,
                "one_candidate_array_bytes": candidate_array_bytes,
                "gmres_restart_50_basis_bytes": gmres_restart_50_basis_bytes,
                "projected_build_peak_bytes": int(math.ceil(projected_build_peak)),
                "projected_full_peak_lower_bytes": int(
                    math.ceil(projected_peak_lower)
                ),
                "projected_full_peak_upper_bytes": int(
                    math.ceil(projected_peak_upper)
                ),
                "projected_build_seconds": projected_build_seconds,
                "projected_stage_1_through_6_seconds_lower": (
                    projected_stage_seconds_lower
                ),
                "projected_stage_1_through_6_seconds_upper": (
                    projected_stage_seconds_upper
                ),
                "projected_one_standard_campaign_core_seconds_lower": (
                    projected_total_seconds_lower
                ),
                "projected_one_standard_campaign_core_seconds_upper": (
                    projected_total_seconds_upper
                ),
                "status": status,
            }
        )
    candidate_rows = rows[: len(GRID_SPECIFICATIONS)]
    fourth = rows[-1]
    complete_core_within_caps = all(
        row["status"] == "one_campaign_core_within_caps_full_screen_unbudgeted"
        for row in candidate_rows
    )
    complete_protocol_runtime_budgeted = False
    return {
        "method": (
            "The build increment scales with unknowns times stored operators. "
            "The post-build lower envelope scales with unknowns; the upper "
            "envelope scales with unknowns times directional bases. Runtime "
            "uses the same split for solver and residual/diagnostic work. "
            "Iteration counts are held fixed. E-028's retained stage timers "
            "exclude native-linear, stage-preflight, report, and checkpoint "
            "work. The estimates also omit the proposed tighter-tolerance "
            "replays. They are one-standard-campaign core projections and "
            "strict lower bounds on any complete screen, not total runtime or "
            "feasibility guarantees."
        ),
        "baseline": baseline,
        "static_build_calibration": static,
        "caps": {
            "soft_rss_bytes": SOFT_RSS_CAP_BYTES,
            "hard_rss_bytes": HARD_RSS_CAP_BYTES,
            "minimum_host_reserve_bytes": MINIMUM_HOST_RESERVE_BYTES,
            "system_build_wall_seconds": SYSTEM_BUILD_WALL_CAP_SECONDS,
            "nightly_grid_wall_seconds": NIGHTLY_GRID_WALL_CAP_SECONDS,
            "host_physical_memory_bytes": host_memory,
            "host_scope": "declared E-035 target host, not the current CI runner",
            "effective_hard_cap_after_reserve_bytes": effective_hard_cap,
        },
        "candidate_grids": candidate_rows,
        "fourth_grid": fourth,
        "complete_candidate_sequence_core_within_caps": complete_core_within_caps,
        "complete_protocol_runtime_budgeted": complete_protocol_runtime_budgeted,
        "complete_candidate_sequence_feasible": (
            complete_core_within_caps and complete_protocol_runtime_budgeted
        ),
        "complete_candidate_sequence_feasibility_status": (
            "blocked even under one-standard-campaign core estimates; complete "
            "protocol runtime is not budgeted because its tolerances are not frozen"
        ),
        "fourth_grid_feasible": False,
        "runtime_limit": (
            "The h=1/32 lower projection exceeds a complete nightly window "
            "before untimed pre/post work, iteration degradation, or tighter "
            "solver replays. A future "
            "campaign would have to checkpoint accepted stages and never "
            "start work that cannot reach a safe handoff before the cap."
        ),
        "representation_limit": (
            "The current system retains every directional CSR and offset; "
            "curvatures and candidates scale as bases*unknowns. Matrix-free, "
            "on-demand, or compressed storage would be a separately "
            "fingerprinted method requiring operator-equivalence tests."
        ),
    }


def derivative_protocol() -> dict[str, Any]:
    """Return the prospective but intentionally incomplete screen design."""

    return {
        "design_status": "incomplete_prospective_design_not_executable",
        "unresolved_prerequisites": [
            "enumerated full-mask maps and boundary-valid native supports",
            "exact tolerance, Krylov, cap, restart, and initialization schedule",
            "validated residual-to-output or contraction-tail root-error enclosure",
            "reproducible taper, detrend, FFT, symbol, parity, and eigengap rules",
            "resource budget including every required solve and untimed stage work",
        ],
        "primary_matrix": (
            "M(H)=[[phi_rr,phi_rz,0],[phi_rz,phi_zz,0],"
            "[0,0,phi_r/rho]]"
        ),
        "primary_norms": {
            "weighted_l2": (
                "D_j,2=sqrt(sum_x w_x ||M_j-M_(j+1)||_F^2/sum_x w_x)"
            ),
            "linf": "D_j,inf=max_x ||M_j-M_(j+1)||_2",
            "componentwise": (
                "Report weighted L2 and Linf for radial, mixed, axial, and "
                "azimuthal components on every fixed mask."
            ),
            "same_grid_operator_spread": (
                "A_j,p=max_(q,q') ||M_j^q-M_j^q'||_p for the three frozen "
                "native recovery families"
            ),
        },
        "coupled_path_screen": {
            "formula": "q_p=log2(D_0,p/D_1,p)",
            "name": "effective coupled-path contraction index",
            "necessary_conditions": [
                "D_j,p is computed between the most-tightly-solved fields",
                "D_1,p<D_0,p after a separately validated root-error enclosure exists",
                "q_p is finite and positive on every primary mask/norm",
                "A_2,p<A_1,p<A_0,p",
                "signed component differences at every fixed point retain orientation",
            ],
            "prohibited_interpretations": [
                "pure spatial apparent order",
                "Richardson extrapolate",
                "Grid Convergence Index",
                "continuum Hessian certificate",
            ],
        },
        "solver_discretization_separation": {
            "candidate_sensitivity_formula": (
                "S_j,p=max(||M_j,std-M_j,tight1||_p, "
                "||M_j,tight1-M_j,tight2||_p); D_j,p is formed only from "
                "tight2 fields; require (S_j,p+S_(j+1),p)/D_j,p<=0.01 and "
                "the second replay change to contract"
            ),
            "one_percent_threshold": 0.01,
            "tolerance_schedule_status": (
                "not frozen: nonlinear and GMRES tolerances, iteration caps, "
                "restart, preconditioner rebuild, and path initialization must "
                "be specified before costs or results are comparable"
            ),
            "classification": (
                "observed solver sensitivity screen, not a rigorous "
                "algebraic-root error enclosure"
            ),
            "literature_context": (
                "This project-defined sensitivity ratio is motivated by, but "
                "does not operationalize or prove, the recommendation that "
                "iterative error be well below discretization error. Residual "
                "or replay-output reduction alone is not an error bound."
            ),
            "alternative": (
                "A validated residual-to-derivative a posteriori enclosure "
                "for the actual solution may replace the two tighter replays."
            ),
        },
        "transfer_band_occupancy": {
            "design_status": "requirements_only_not_reproducibly_frozen",
            "physical_tiles": (
                "Candidate only: for each mapped point use the half-open "
                "4 r0 by 4 r0 tile "
                "[rho0-2,rho0+2) by [z0-2,z0+2) at native h. Even-reflect "
                "negative z; rho=0 remains excluded."
            ),
            "preprocessing": (
                "Affine-detrend radial/mixed/axial and constant-detrend local "
                "azimuthal data; apply one separable periodic Hann taper and "
                "record its normalization before a unitary 2D FFT."
            ),
            "measure": (
                "For each component/operator, report derivative-weighted "
                "spectral energy inside and outside E-034's project-defined "
                "90-percent operator-amplitude origin square."
            ),
            "gate": (
                "Both absolute outside-band derivative RMS and its total-energy "
                "fraction must strictly contract. A finest fraction cap and "
                "absolute noise/error floor must be fixed before use."
            ),
            "parity_diagnostics": (
                "Record absolute projections and normalized correlations with "
                "(-1)^i, (-1)^j, and (-1)^(i+j). Their exact weighting, signal "
                "floor, and finest-grid caps remain to be specified."
            ),
            "project_policy_note": (
                "The 90-percent square is inherited as a project diagnostic, "
                "not a literature-derived acceptance threshold. No absolute "
                "or fractional acceptance threshold is yet frozen."
            ),
            "scope_limit": (
                "Windowed local spectra diagnose transfer occupancy; they do "
                "not enclose the global derivative error."
            ),
            "unresolved_reproducibility": (
                "Hann convention, weighted detrend, unitary-FFT normalization "
                "and wavenumbers, discrete component symbols, null/sign-band "
                "handling, and absolute thresholds are not yet defined."
            ),
        },
        "nonlinear_outputs": {
            "pair_margin": (
                "Report only after component contraction, with eigengap and "
                "eigenbranch-stability ledgers. As conservative project policy, "
                "do not apply Richardson/GCI to this nonsmooth derived output."
            ),
            "status": (
                "signed-orientation signal floors, symmetry-zero exemptions, "
                "and Weyl/eigengap branch thresholds are not yet frozen"
            ),
            "topology": (
                "Thresholded counts and components are stability diagnostics, "
                "not smooth extrapolation quantities."
            ),
        },
        "independent_enclosure_requirement": (
            "A continuum claim requires a derivative-error enclosure for the "
            "actual nonlinear solution and fixed ROI. Manufactured recovery "
            "tests alone validate implementation and do not supply it."
        ),
    }


def stop_rules() -> list[str]:
    """Return hard stops, including unresolved conditions that forbid a run."""

    return [
        "stop before a solve because E-035's new full-positive-support six-cell policy fails on h=0.125",
        "stop before a solve while the complete fixed three-grid sequence exceeds the conservative resource envelope",
        "stop before a build if projected or measured RSS exceeds the soft cap without a dedicated resource approval",
        "stop immediately at the hard RSS cap or if the minimum host reserve cannot be maintained",
        "stop before Newton if the system build exceeds its RSS or wall cap",
        "stop at the last accepted checkpoint if a stage cannot finish within the nightly handoff window",
        "stop on any inherited provenance, source, domain, path, residual, Krylov, cone, tail, flux, force, or branch gate",
        "stop if h/delta_theta or physical stencil reach fails to decrease",
        "stop while replay changes remain only a sensitivity proxy and no validated root-error enclosure exists",
        "stop if component orientation oscillates, a primary difference is unresolved, or recovery spread fails to contract",
        "stop if transfer-band occupancy or parity remains unresolved; do not label it noise",
        "stop if any ROI, mask, source cutoff, recovery, threshold, or cap would need post-outcome adjustment",
        "do not shrink R, change the source, lower m, skip a grid, advance amplitude, or substitute a post hoc recovery",
        "do not infer continuum convergence, a physical field, or propulsion from a three-grid contraction screen",
    ]


def run_analysis() -> dict[str, Any]:
    """Run the deterministic, checkpoint-free E-035 audit."""

    started = time.perf_counter()
    geometry = coupled_grid_geometry()
    resources = resource_feasibility()
    common_nodes = common_node_preregistration()
    protocol = derivative_protocol()
    failed_gates = []
    if not geometry["source_transition_audit"]["passed"]:
        failed_gates.append("new_full_positive_support_six_cell_policy")
    if not resources["complete_candidate_sequence_feasible"]:
        failed_gates.append("complete_three_grid_resource_gate")
    if not resources["fourth_grid_feasible"]:
        failed_gates.append("fourth_grid_resource_gate")
    if protocol["design_status"] != "fully_frozen_executable_protocol":
        failed_gates.append("future_derivative_protocol_not_executable")
    failed_gates.append("actual_solution_derivative_enclosure_not_yet_defined")
    decision_status = "blocked_before_nonlinear_solve"
    return {
        "epistemic_status": (
            "no-solve numerical-method feasibility and preregistration audit "
            "for a hypothetical PDE; not a continuum solution, detected "
            "field, artificial gravity, inertial control, spacetime "
            "engineering, FTL, or propulsion result"
        ),
        "focus_question": (
            "Is the fixed R=80 source-resolved coupled-grid derivative screen "
            "computationally feasible and scientifically identifying before "
            "any new nonlinear solve?"
        ),
        "implementation_provenance": implementation_provenance(),
        "runtime_provenance": runtime_provenance(),
        "geometry": geometry,
        "common_node_preregistration": common_nodes,
        "resource_feasibility": resources,
        "derivative_protocol": protocol,
        "stop_rules": stop_rules(),
        "decision": {
            "analysis_completed": True,
            "screen_authorized": False,
            "status": decision_status,
            "failed_gates": failed_gates,
            "interpretation_limits": [
                (
                    "The non-geometric h/m path may support an empirical "
                    "contraction screen, but it does not justify pure-spatial "
                    "Richardson order, extrapolation, or GCI."
                )
            ],
            "main_result": (
                "The fixed screen is not authorized. Under E-035's new full-"
                "positive-support policy its source transition has only four "
                "coarsest cells; even a one-standard-campaign core projection "
                "for h=1/32 exceeds the memory/runtime policy; the h=1/64 "
                "fourth grid exceeds 64 GiB in retained static storage before "
                "solver temporaries; and the future derivative protocol is "
                "not yet executable or fully specified."
            ),
            "blank_space_classification": (
                "blocked for the frozen sequence/current representation; "
                "unclear whether an actual-solution derivative enclosure can "
                "replace the infeasible fourth grid"
            ),
            "next_best_step": (
                "E-036 should remain no-solve and derive a two-parameter "
                "spatial/directional derivative-error enclosure applicable "
                "to the actual fixed ROI, including source-transition and "
                "curved-boundary terms. If that cannot be made rigorous, "
                "preflight an exactly equivalent on-demand operator storage "
                "method before reconsidering any finer campaign."
            ),
        },
        "resource_accounting": {
            "elapsed_seconds": time.perf_counter() - started,
            "checkpoint_reads": 0,
            "field_reads": 0,
            "pde_builds": 0,
            "pde_solves": 0,
        },
    }


def _write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
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
        f"screen_authorized={decision['screen_authorized']}; "
        f"elapsed={report['resource_accounting']['elapsed_seconds']:.3f}s"
    )
    return 0 if decision["analysis_completed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

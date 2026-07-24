#!/usr/bin/env python3
"""E-028 six-cell continuation campaign for the independent 2-Hessian solve.

This driver combines the E-025 axisymmetric wide-directional discretization
with E-026's fixed nonsymmetric AMG corrector.  Its canonical problem is the
``R=80``, ``h=0.125``, ``m=4`` broad smooth ``mu=36.8`` annulus.  The first
source stage starts from the native fine-grid Poisson predictor
``(1/12) phi_linear``; a raw prolonged coarse solution is deliberately not
used because E-026 showed that its outer cutoff leaves the fine field outside
the admissible branch.

Each completed source-amplitude stage is written atomically as a digest-
checked artifact.  A resumed campaign reconstructs and fingerprints
the exact fine operator and source, rebuilds every active Jacobian and AMG
hierarchy, and rechecks the branch before using a saved field.  The nonlinear,
Krylov, line-search, and wide-stencil gates are unchanged from E-026.

This is numerical validation of a hypothetical cubic-Galileon PDE.  It is not
evidence for a new field, useful artificial gravity, inertial control, FTL
travel, or reactionless propulsion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import resource
import sys
import time
from typing import Any, Callable

import numpy as np
from scipy.sparse import linalg as sparse_linalg

import models.e025_axisymmetric_wide_2hessian as e025
import models.e026_nonsymmetric_amg as e026
from models.e025_axisymmetric_wide_2hessian import (
    AxisymmetricGrid,
    ContinuationStage,
    WideSolution,
    active_jacobian_matrix,
    annulus_diagnostics,
    build_system,
    monotone_operator,
    monotone_sigma_gradient,
    scheme_diagnostic_details,
    scheme_diagnostics,
    shifted_rhs,
    smooth_annulus_source,
    solve_linear_reference,
)
from models.e026_nonsymmetric_amg import (
    AmgConfiguration,
    build_fixed_hierarchy,
    configuration_provenance,
    hierarchy_diagnostics,
    matrix_diagnostics,
    runtime_provenance,
    save_campaign_artifact,
    spatial_principal_crosschecks,
)


CANONICAL_RADIAL_MAX = 80.0
CANONICAL_SPACING = 0.125
CANONICAL_DIRECTIONAL_RADIUS = 4
CANONICAL_CONTINUATION_STEPS = 12
NONLINEAR_RELATIVE_TOLERANCE = 1.0e-7
NEWTON_MAX_ITERATIONS = 20

DEFAULT_CHECKPOINT = (
    Path(__file__).resolve().parent
    / "checkpoints"
    / "e028_h0125_m4_campaign_checkpoint.npz"
)
DEFAULT_FIRST_STAGE_ARTIFACT = (
    Path(__file__).resolve().parent
    / "checkpoints"
    / "e028_h0125_m4_1of12_pgsa.npz"
)
DEFAULT_FULL_SOURCE_ARTIFACT = (
    Path(__file__).resolve().parent
    / "checkpoints"
    / "e028_h0125_m4_full_source_pgsa.npz"
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_array(values: np.ndarray) -> str:
    array = np.ascontiguousarray(np.asarray(values, dtype=np.float64))
    return hashlib.sha256(array.view(np.uint8)).hexdigest()


def peak_rss_bytes() -> int:
    """Return the process high-water RSS in bytes on macOS and Linux."""

    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def implementation_provenance() -> dict[str, Any]:
    """Fingerprint this driver and both numerical modules it composes."""

    paths = {
        "e028_campaign": Path(__file__).resolve(),
        "e025_operator": Path(e025.__file__).resolve(),
        "e026_amg": Path(e026.__file__).resolve(),
        "research_requirements": Path(__file__).resolve().parents[1]
        / "requirements-research.txt",
    }
    return {
        "modules": {
            name: {"path": str(path), "sha256": _sha256_file(path)}
            for name, path in paths.items()
        },
        "artifact_format": 2,
        "campaign_checkpoint_schema": 1,
    }


def scaled_source_metadata(
    metadata: dict[str, float], amplitude: float
) -> dict[str, float]:
    """Scale charge and pointwise source values for one continuation stage."""

    if not 0.0 < amplitude <= 1.0:
        raise ValueError("source amplitude must lie in (0, 1]")
    result = dict(metadata)
    for key in (
        "nominal_charge",
        "sampled_charge",
        "minimum_source",
        "maximum_source",
    ):
        result[key] = float(metadata[key]) * amplitude
    result["full_source_amplitude"] = amplitude
    return result


def _canonical_json(values: Any) -> str:
    return json.dumps(
        values,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def save_campaign_checkpoint(
    path: str | Path,
    field: np.ndarray,
    full_linear_field: np.ndarray,
    report: dict[str, Any],
) -> None:
    """Atomically preserve an accepted field and the expensive native solve."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.tmp")
    metadata = {
        "format_version": 1,
        "field_sha256": _sha256_array(field),
        "full_linear_field_sha256": _sha256_array(full_linear_field),
        "report": report,
        "report_sha256": hashlib.sha256(
            _canonical_json(report).encode("utf-8")
        ).hexdigest(),
    }
    with temporary.open("wb") as handle:
        np.savez_compressed(
            handle,
            field=np.asarray(field, dtype=np.float64),
            full_linear_field=np.asarray(full_linear_field, dtype=np.float64),
            metadata=np.array(_canonical_json(metadata)),
        )
    temporary.replace(destination)


def load_campaign_checkpoint(
    path: str | Path,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Load and integrity-check an E-028 accepted-state checkpoint."""

    with np.load(Path(path), allow_pickle=False) as payload:
        field = np.asarray(payload["field"], dtype=float)
        full_linear_field = np.asarray(payload["full_linear_field"], dtype=float)
        metadata = json.loads(str(payload["metadata"].item()))
    if metadata.get("format_version") != 1:
        raise ValueError("unsupported E-028 checkpoint format")
    if field.ndim != 1 or full_linear_field.shape != field.shape:
        raise ValueError("E-028 checkpoint arrays have invalid shapes")
    if not np.all(np.isfinite(field)) or not np.all(np.isfinite(full_linear_field)):
        raise ValueError("E-028 checkpoint arrays must be finite")
    if _sha256_array(field) != metadata.get("field_sha256"):
        raise ValueError("E-028 checkpoint field digest does not match")
    if _sha256_array(full_linear_field) != metadata.get(
        "full_linear_field_sha256"
    ):
        raise ValueError("E-028 checkpoint linear-field digest does not match")
    report = metadata.get("report")
    if not isinstance(report, dict):
        raise ValueError("E-028 checkpoint report is missing")
    report_sha256 = hashlib.sha256(
        _canonical_json(report).encode("utf-8")
    ).hexdigest()
    if report_sha256 != metadata.get("report_sha256"):
        raise ValueError("E-028 checkpoint report digest does not match")
    if report.get("output_field_sha256") != _sha256_array(field):
        raise ValueError("E-028 checkpoint report and field digests disagree")
    return field, full_linear_field, report


def _canonical_grid() -> AxisymmetricGrid:
    return AxisymmetricGrid(
        CANONICAL_RADIAL_MAX,
        CANONICAL_SPACING,
        CANONICAL_DIRECTIONAL_RADIUS,
    )


def _branch_summary(system: Any, field: np.ndarray) -> dict[str, Any]:
    _, _, curvatures = monotone_operator(system, field)
    pair, spatial, time_coefficient = scheme_diagnostics(system, curvatures)
    details = scheme_diagnostic_details(system, field)
    all_time = 1.0 + 2.0 * system.cubic_coefficient * (
        np.sum(curvatures, axis=-1) - 3.0 * system.shift
    )
    time_frame, time_node = np.unravel_index(
        int(np.argmin(all_time)), all_time.shape
    )
    return {
        "minimum_pair_sum": pair,
        "minimum_spatial_principal": spatial,
        "minimum_time_kinetic": time_coefficient,
        "details": details,
        "all_frame_time_minimum": {
            "value": float(all_time[time_frame, time_node]),
            "frame_index": int(time_frame),
            "basis": list(system.bases[time_frame]),
            "rho": float(system.rho[time_node]),
            "z": float(system.z[time_node]),
        },
        "passes": bool(pair > 0.0 and spatial > 0.0 and time_coefficient > 0.0),
    }


def _sparse_storage_bytes(matrix: Any) -> int:
    values = matrix.tocsr()
    return int(values.data.nbytes + values.indices.nbytes + values.indptr.nbytes)


def _hierarchy_storage_bytes(hierarchy: Any) -> dict[str, Any]:
    level_rows: list[dict[str, int]] = []
    for index, level in enumerate(hierarchy.levels):
        row = {
            "level": index,
            "operator_bytes": _sparse_storage_bytes(level.A),
            "prolongation_bytes": (
                _sparse_storage_bytes(level.P) if hasattr(level, "P") else 0
            ),
            "restriction_bytes": (
                _sparse_storage_bytes(level.R) if hasattr(level, "R") else 0
            ),
        }
        row["stored_sparse_bytes"] = (
            row["operator_bytes"]
            + row["prolongation_bytes"]
            + row["restriction_bytes"]
        )
        level_rows.append(row)
    return {
        "levels": level_rows,
        "operator_bytes": sum(row["operator_bytes"] for row in level_rows),
        "transfer_bytes": sum(
            row["prolongation_bytes"] + row["restriction_bytes"]
            for row in level_rows
        ),
        "stored_sparse_bytes": sum(
            row["stored_sparse_bytes"] for row in level_rows
        ),
        "scope_note": (
            "Counts CSR A/P/R arrays only. Peak RSS is authoritative because "
            "PyAMG keep=True also retains setup objects and temporaries."
        ),
    }


def _solve_linear_corrector_strict(
    jacobian: Any,
    residual: np.ndarray,
    system: Any,
    configuration: AmgConfiguration,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Apply one fixed hierarchy and enforce the direct requested tolerance."""

    positive_matrix = (-jacobian).tocsr()
    setup_started = time.perf_counter()
    hierarchy = build_fixed_hierarchy(positive_matrix, system, configuration)
    setup_seconds = time.perf_counter() - setup_started
    hierarchy_report = hierarchy_diagnostics(hierarchy)
    hierarchy_report["storage_bytes"] = _hierarchy_storage_bytes(hierarchy)
    rss_after_setup = peak_rss_bytes()
    preconditioner = hierarchy.aspreconditioner(cycle=configuration.cycle)
    history: list[float] = []
    solve_started = time.perf_counter()
    correction, info = sparse_linalg.gmres(
        positive_matrix,
        residual,
        M=preconditioner,
        rtol=configuration.gmres_relative_tolerance,
        atol=0.0,
        restart=min(configuration.gmres_restart, positive_matrix.shape[0]),
        maxiter=configuration.gmres_max_restart_cycles,
        callback=lambda value: history.append(float(value)),
        callback_type="pr_norm",
    )
    solve_seconds = time.perf_counter() - solve_started
    true_ratio = float(
        np.linalg.norm(residual - positive_matrix @ correction)
        / np.linalg.norm(residual)
    )
    maximum_inner = (
        configuration.gmres_restart * configuration.gmres_max_restart_cycles
    )
    strict = bool(
        info == 0
        and true_ratio < configuration.gmres_relative_tolerance
        and len(history) <= maximum_inner
    )
    return np.asarray(correction, dtype=float), {
        "gmres_info": int(info),
        "inner_iterations": len(history),
        "maximum_inner_iterations": maximum_inner,
        "requested_true_residual_tolerance": (
            configuration.gmres_relative_tolerance
        ),
        "true_linear_residual_ratio": true_ratio,
        "passes_inexact_newton_gate": bool(true_ratio < 1.0),
        "passes_requested_true_residual_gate": bool(
            true_ratio < configuration.gmres_relative_tolerance
        ),
        "passes_strict_krylov_gate": strict,
        "setup_seconds": setup_seconds,
        "solve_seconds": solve_seconds,
        "preconditioned_residual_first": history[0] if history else None,
        "preconditioned_residual_last": history[-1] if history else None,
        "hierarchy": hierarchy_report,
        "peak_rss_bytes_after_setup": rss_after_setup,
        "peak_rss_bytes_after_solve": peak_rss_bytes(),
    }


def _strict_close_stage(
    system: Any,
    source: np.ndarray,
    initial_field: np.ndarray,
    configuration: AmgConfiguration,
    *,
    nonlinear_relative_tolerance: float,
    newton_max_iterations: int,
    prior_history: list[dict[str, Any]] | None = None,
    accepted_step_callback: (
        Callable[[np.ndarray, list[dict[str, Any]]], None] | None
    ) = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Close one stage without a near-tolerance bypass or weak Krylov gate."""

    field = np.asarray(initial_field, dtype=float).copy()
    stage_scale = max(
        float(np.linalg.norm(source)) / (2.0 * system.cubic_coefficient),
        np.finfo(float).tiny,
    )
    history = list(prior_history or [])
    total_setup_seconds = sum(
        float(row["linear"]["setup_seconds"]) for row in history
    )
    total_solve_seconds = sum(
        float(row["linear"]["solve_seconds"]) for row in history
    )
    for newton_iteration in range(len(history) + 1, newton_max_iterations + 1):
        operator, active, curvatures = monotone_operator(system, field)
        pair, spatial, time_coefficient = scheme_diagnostics(system, curvatures)
        if pair <= 0.0 or spatial <= 0.0 or time_coefficient <= 0.0:
            raise RuntimeError(
                "E-028 field failed a branch gate before the residual shortcut"
            )
        residual = operator - shifted_rhs(source, system.cubic_coefficient)
        residual_norm = float(np.linalg.norm(residual))
        relative_before = residual_norm / stage_scale
        if relative_before < nonlinear_relative_tolerance:
            break
        nodes = np.arange(system.size)
        active_gradient = monotone_sigma_gradient(curvatures[active, nodes])
        jacobian = active_jacobian_matrix(system, active, active_gradient)
        correction, linear_report = _solve_linear_corrector_strict(
            jacobian, residual, system, configuration
        )
        if not linear_report["passes_strict_krylov_gate"]:
            raise RuntimeError(
                "E-028 strict Krylov failure: "
                f"info={linear_report['gmres_info']}; "
                f"true_ratio={linear_report['true_linear_residual_ratio']:.6e}; "
                f"requested={configuration.gmres_relative_tolerance:.6e}; "
                f"inner={linear_report['inner_iterations']}; "
                f"cap={linear_report['maximum_inner_iterations']}"
            )

        accepted = False
        step = 1.0
        for _ in range(24):
            trial = field + step * correction
            trial_operator, _, trial_curvatures = monotone_operator(system, trial)
            trial_residual = trial_operator - shifted_rhs(
                source, system.cubic_coefficient
            )
            trial_pair, trial_spatial, trial_time = scheme_diagnostics(
                system, trial_curvatures
            )
            sufficient_decrease = float(np.linalg.norm(trial_residual)) < (
                residual_norm * (1.0 - 1.0e-4 * step)
            )
            if (
                sufficient_decrease
                and trial_pair > 0.0
                and trial_spatial > 0.0
                and trial_time > 0.0
            ):
                field = trial
                accepted = True
                relative_after = float(np.linalg.norm(trial_residual) / stage_scale)
                break
            step *= 0.5
        if not accepted:
            raise RuntimeError(
                "E-028 branch-safe line search failed with no 2x-tolerance "
                f"bypass; relative_residual={relative_before:.6e}; "
                f"pair/spatial/time={pair:.6e}/{spatial:.6e}/"
                f"{time_coefficient:.6e}"
            )

        total_setup_seconds += float(linear_report["setup_seconds"])
        total_solve_seconds += float(linear_report["solve_seconds"])
        row = {
            "newton_iteration": newton_iteration,
            "relative_residual_before": relative_before,
            "relative_residual_after": relative_after,
            "accepted_step": step,
            "minimum_pair_sum": trial_pair,
            "minimum_spatial_principal": trial_spatial,
            "minimum_time_kinetic": trial_time,
            "wide_location_details": _branch_summary(system, field),
            "linear": linear_report,
        }
        history.append(row)
        if accepted_step_callback is not None:
            accepted_step_callback(field, history)

    final_operator, _, final_curvatures = monotone_operator(system, field)
    final_residual = final_operator - shifted_rhs(source, system.cubic_coefficient)
    relative_l2 = float(np.linalg.norm(final_residual) / stage_scale)
    source_linf_scale = max(
        float(np.max(source)) / (2.0 * system.cubic_coefficient),
        np.finfo(float).tiny,
    )
    relative_linf = float(np.max(np.abs(final_residual)) / source_linf_scale)
    pair, spatial, time_coefficient = scheme_diagnostics(system, final_curvatures)
    if relative_l2 >= nonlinear_relative_tolerance:
        raise RuntimeError(
            "E-028 stage exhausted the Newton cap without the strict nonlinear "
            f"gate; residual={relative_l2:.6e}"
        )
    if pair <= 0.0 or spatial <= 0.0 or time_coefficient <= 0.0:
        raise RuntimeError("E-028 converged residual is outside the wide branch")
    return field, {
        "configuration": configuration_provenance(configuration),
        "newton_iterations": len(history),
        "summed_gmres_inner_iterations": int(
            sum(row["linear"]["inner_iterations"] for row in history)
        ),
        "summed_setup_seconds": total_setup_seconds,
        "summed_solve_seconds": total_solve_seconds,
        "relative_residual_l2": relative_l2,
        "relative_residual_linf": relative_linf,
        "minimum_pair_sum": pair,
        "minimum_spatial_principal": spatial,
        "minimum_time_kinetic": time_coefficient,
        "history": history,
    }


def _stage_preflight(
    system: Any,
    stage_source: np.ndarray,
    field: np.ndarray,
) -> tuple[np.ndarray, Any, dict[str, Any]]:
    operator, active, curvatures = monotone_operator(system, field)
    residual = operator - shifted_rhs(stage_source, system.cubic_coefficient)
    nodes = np.arange(system.size)
    active_gradient = monotone_sigma_gradient(curvatures[active, nodes])
    jacobian = active_jacobian_matrix(system, active, active_gradient)
    pair, spatial, time_coefficient = scheme_diagnostics(system, curvatures)
    stage_scale = max(
        float(np.linalg.norm(stage_source))
        / (2.0 * system.cubic_coefficient),
        np.finfo(float).tiny,
    )
    return residual, jacobian, {
        "relative_residual_l2": float(np.linalg.norm(residual) / stage_scale),
        "minimum_pair_sum": pair,
        "minimum_spatial_principal": spatial,
        "minimum_time_kinetic": time_coefficient,
        "matrix": matrix_diagnostics(
            jacobian,
            rho=system.rho,
            z=system.z,
            radial_max=system.grid.radial_max,
        ),
        "peak_rss_bytes": peak_rss_bytes(),
    }


def solve_one_stage(
    system: Any,
    full_source: np.ndarray,
    initial_field: np.ndarray,
    amplitude: float,
    configuration: AmgConfiguration,
    *,
    nonlinear_relative_tolerance: float = NONLINEAR_RELATIVE_TOLERANCE,
    newton_max_iterations: int = NEWTON_MAX_ITERATIONS,
    prior_history: list[dict[str, Any]] | None = None,
    accepted_step_callback: (
        Callable[[np.ndarray, list[dict[str, Any]]], None] | None
    ) = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Close one absolute full-source fraction under the E-026 gates."""

    configuration.validate()
    if not 0.0 < amplitude <= 1.0:
        raise ValueError("stage amplitude must lie in (0, 1]")
    source = amplitude * np.asarray(full_source, dtype=float)
    field = np.asarray(initial_field, dtype=float)
    if source.shape != (system.size,) or field.shape != (system.size,):
        raise ValueError("stage arrays do not match the fine-grid system")
    if not np.all(np.isfinite(field)):
        raise ValueError("stage field must be finite")

    _residual, _jacobian, preflight = _stage_preflight(system, source, field)
    if (
        preflight["minimum_pair_sum"] <= 0.0
        or preflight["minimum_spatial_principal"] <= 0.0
        or preflight["minimum_time_kinetic"] <= 0.0
    ):
        raise ValueError("stage predictor is outside the admissible normal branch")

    started = time.perf_counter()
    solved_field, nonlinear = _strict_close_stage(
        system,
        source,
        field,
        configuration,
        nonlinear_relative_tolerance=nonlinear_relative_tolerance,
        newton_max_iterations=newton_max_iterations,
        prior_history=prior_history,
        accepted_step_callback=accepted_step_callback,
    )
    elapsed = time.perf_counter() - started
    return solved_field, {
        "amplitude": amplitude,
        "target_source_digest": e025._source_digest(source),
        "preflight": preflight,
        "configuration": configuration_provenance(configuration),
        "nonlinear": nonlinear,
        "elapsed_seconds": elapsed,
        "peak_rss_bytes_after": peak_rss_bytes(),
    }


def _maximum_hierarchy_metric(stage: dict[str, Any], key: str) -> int:
    values = [
        int(row["linear"]["hierarchy"][key])
        for row in stage["nonlinear"]["history"]
    ]
    return max(values, default=0)


def _maximum_hierarchy_storage_bytes(stage: dict[str, Any]) -> int:
    values = [
        int(row["linear"]["hierarchy"]["storage_bytes"]["stored_sparse_bytes"])
        for row in stage["nonlinear"]["history"]
    ]
    return max(values, default=0)


def _current_diagnostics(
    system: Any,
    full_source: np.ndarray,
    full_source_metadata: dict[str, float],
    full_linear_field: np.ndarray,
    field: np.ndarray,
    stage: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    amplitude = float(stage["amplitude"])
    nonlinear = stage["nonlinear"]
    stage_record = ContinuationStage(
        amplitude=amplitude,
        newton_iterations=int(nonlinear["newton_iterations"]),
        gmres_iterations=int(nonlinear["summed_gmres_inner_iterations"]),
        relative_residual_l2=float(nonlinear["relative_residual_l2"]),
        minimum_pair_sum=float(nonlinear["minimum_pair_sum"]),
        minimum_spatial_principal=float(nonlinear["minimum_spatial_principal"]),
        minimum_time_kinetic=float(nonlinear["minimum_time_kinetic"]),
        preconditioner_kind=(
            f"active_{stage['configuration']['requested']['kind']}"
        ),
        preconditioner_setups=int(nonlinear["newton_iterations"]),
        preconditioner_setup_seconds=float(nonlinear["summed_setup_seconds"]),
        preconditioner_factor_nnz_max=0,
    )
    solution = WideSolution(
        system=system,
        source=amplitude * full_source,
        field=field,
        linear_field=amplitude * full_linear_field,
        stages=[stage_record],
        relative_residual_l2=float(nonlinear["relative_residual_l2"]),
        relative_residual_linf=float(nonlinear["relative_residual_linf"]),
        minimum_pair_sum=float(nonlinear["minimum_pair_sum"]),
        minimum_spatial_principal=float(nonlinear["minimum_spatial_principal"]),
        minimum_time_kinetic=float(nonlinear["minimum_time_kinetic"]),
    )
    diagnostics = annulus_diagnostics(
        solution,
        scaled_source_metadata(full_source_metadata, amplitude),
    )
    packaged_solver = diagnostics["solver"]
    packaged_solver.pop("maximum_preconditioner_factor_nnz", None)
    for key in (
        "operator_nonzeros",
        "transfer_nonzeros",
        "stored_sparse_nonzeros",
    ):
        packaged_solver[f"maximum_preconditioner_{key}"] = (
            _maximum_hierarchy_metric(stage, key)
        )
    packaged_solver["maximum_preconditioner_stored_sparse_bytes"] = (
        _maximum_hierarchy_storage_bytes(stage)
    )
    for row in packaged_solver["stages"]:
        row.pop("preconditioner_factor_nnz_max", None)
        for key in (
            "operator_nonzeros",
            "transfer_nonzeros",
            "stored_sparse_nonzeros",
        ):
            row[f"preconditioner_{key}_max"] = _maximum_hierarchy_metric(
                stage, key
            )
        row["preconditioner_stored_sparse_bytes_max"] = (
            _maximum_hierarchy_storage_bytes(stage)
        )
    crosschecks = spatial_principal_crosschecks(
        system,
        field,
        float(nonlinear["minimum_spatial_principal"]),
    )
    return diagnostics, crosschecks


def _base_report(
    system: Any,
    full_source: np.ndarray,
    source_metadata: dict[str, float],
    configuration: AmgConfiguration,
    preparation: dict[str, Any],
) -> dict[str, Any]:
    directional_resolution = e025.directional_resolution(
        system.grid.directional_radius
    )
    physical_reach = max(
        math.hypot(*basis) for basis in system.bases
    ) * system.grid.spacing
    source_transition_scale = 0.8
    return {
        "epistemic_status": (
            "joint-refinement numerics for a hypothetical PDE; not a detected "
            "field, useful artificial gravity, inertial control, FTL result, "
            "or propulsion result"
        ),
        "focus_question": (
            "Can the native fine-grid 1/12 Poisson predictor enter and then "
            "continue the six-cell full-source branch without relaxing any "
            "nonlinear, Krylov, or admissibility gate?"
        ),
        "runtime_provenance": runtime_provenance(),
        "implementation_provenance": implementation_provenance(),
        "configuration": {
            "grid": {
                "radial_max": system.grid.radial_max,
                "spacing": system.grid.spacing,
                "directional_radius": system.grid.directional_radius,
                "unknowns": system.size,
                "bases": len(system.bases),
                "directional_resolution_rad": directional_resolution,
                "spacing_over_directional_resolution": (
                    system.grid.spacing / directional_resolution
                ),
                "maximum_primitive_stencil_reach": physical_reach,
                "source_transition_scale": source_transition_scale,
                "transition_cells": (
                    source_transition_scale / system.grid.spacing
                ),
                "stencil_reach_over_transition_scale": (
                    physical_reach / source_transition_scale
                ),
            },
            "continuation_steps": CANONICAL_CONTINUATION_STEPS,
            "nonlinear_relative_tolerance": NONLINEAR_RELATIVE_TOLERANCE,
            "newton_max_iterations": NEWTON_MAX_ITERATIONS,
            "amg": configuration_provenance(configuration),
        },
        "operator_and_source": {
            "system_digest": e025._system_digest(system),
            "full_source_digest": e025._source_digest(full_source),
            "full_source_metadata": source_metadata,
        },
        "preparation": preparation,
    }


def _report_after_stage(
    base: dict[str, Any],
    system: Any,
    full_source: np.ndarray,
    source_metadata: dict[str, float],
    full_linear_field: np.ndarray,
    field: np.ndarray,
    stages: list[dict[str, Any]],
    requested_stop_stage: int,
) -> dict[str, Any]:
    current = stages[-1]
    diagnostics, crosschecks = _current_diagnostics(
        system,
        full_source,
        source_metadata,
        full_linear_field,
        field,
        current,
    )
    completed_stage = len(stages)
    report = dict(base)
    report.update(
        {
            "campaign": {
                "completed_stage": completed_stage,
                "completed_amplitude": completed_stage
                / CANONICAL_CONTINUATION_STEPS,
                "requested_stop_stage": requested_stop_stage,
                "stages": stages,
            },
            "current_stage_diagnostics": diagnostics,
            "spatial_principal_crosschecks": crosschecks,
            "resource_accounting": {
                "peak_rss_bytes": peak_rss_bytes(),
                "peak_rss_gib": peak_rss_bytes() / 1024.0**3,
                "maximum_hierarchy_operator_nonzeros": max(
                    _maximum_hierarchy_metric(stage, "operator_nonzeros")
                    for stage in stages
                ),
                "maximum_hierarchy_transfer_nonzeros": max(
                    _maximum_hierarchy_metric(stage, "transfer_nonzeros")
                    for stage in stages
                ),
                "maximum_hierarchy_stored_sparse_nonzeros": max(
                    _maximum_hierarchy_metric(stage, "stored_sparse_nonzeros")
                    for stage in stages
                ),
                "maximum_hierarchy_stored_sparse_bytes": max(
                    _maximum_hierarchy_storage_bytes(stage) for stage in stages
                ),
                "storage_scope_note": (
                    "Sparse bytes count A/P/R CSR arrays only; peak RSS also "
                    "captures retained setup objects, temporaries, and Krylov vectors."
                ),
            },
            "output_field_sha256": _sha256_array(field),
            "limitations": [
                "A partial-source stage is a solver and branch-reach result, not a full-source observable.",
                "A positive wide-stencil gate does not override a conflicting fixed or centered crosscheck.",
                "This six-cell point alone cannot establish continuum or outer-box convergence.",
                "A later outer-box comparison must use fixed physical flux spheres; the default diagnostic radii vary with box size.",
                "The published Cartesian monotone-scheme theorem does not automatically cover the cylindrical reflected-axis and curved-boundary adaptation.",
                "Density, material, asymmetry, target, EFT, and propulsion continuations remain blocked.",
            ],
        }
    )
    return report


def _preflight_checkpoint_report(
    base: dict[str, Any],
    field: np.ndarray,
    requested_stop_stage: int,
) -> dict[str, Any]:
    report = dict(base)
    report.update(
        {
            "campaign": {
                "completed_stage": 0,
                "completed_amplitude": 0.0,
                "requested_stop_stage": requested_stop_stage,
                "stages": [],
                "pending_stage": 1,
                "pending_amplitude": 1.0 / CANONICAL_CONTINUATION_STEPS,
            },
            "output_field_sha256": _sha256_array(field),
            "limitations": [
                "This artifact contains only the branch-checked native fine-grid predictor.",
                "No nonlinear source stage has yet converged.",
            ],
        }
    )
    return report


def _in_progress_checkpoint_report(
    base: dict[str, Any],
    field: np.ndarray,
    stages: list[dict[str, Any]],
    stage_number: int,
    history: list[dict[str, Any]],
    requested_stop_stage: int,
) -> dict[str, Any]:
    """Describe accepted Newton work without quoting target observables."""

    report = dict(base)
    report.update(
        {
            "campaign": {
                "completed_stage": len(stages),
                "completed_amplitude": len(stages)
                / CANONICAL_CONTINUATION_STEPS,
                "requested_stop_stage": requested_stop_stage,
                "stages": stages,
                "in_progress_stage": stage_number,
                "in_progress_amplitude": stage_number
                / CANONICAL_CONTINUATION_STEPS,
                "accepted_newton_history": history,
            },
            "resource_accounting": {
                "peak_rss_bytes": peak_rss_bytes(),
                "peak_rss_gib": peak_rss_bytes() / 1024.0**3,
            },
            "output_field_sha256": _sha256_array(field),
            "limitations": [
                "This checkpoint contains accepted Newton work for an incomplete source stage.",
                "No force, flux, or completed-target observable is quoted.",
            ],
        }
    )
    return report


def _validate_resume_report(
    report: dict[str, Any],
    system: Any,
    full_source: np.ndarray,
    configuration: AmgConfiguration,
) -> tuple[int, list[dict[str, Any]], dict[str, Any] | None]:
    expected = {
        "system_digest": e025._system_digest(system),
        "full_source_digest": e025._source_digest(full_source),
    }
    actual = report.get("operator_and_source", {})
    for key, value in expected.items():
        if actual.get(key) != value:
            raise ValueError(f"resume artifact {key} does not match")
    if report.get("implementation_provenance") != implementation_provenance():
        raise ValueError("resume implementation fingerprints do not match")
    if report.get("runtime_provenance") != runtime_provenance():
        raise ValueError("resume runtime provenance does not match")
    if report.get("configuration", {}).get("amg") != configuration_provenance(
        configuration
    ):
        raise ValueError("resume artifact AMG configuration does not match")
    campaign = report.get("campaign")
    if not isinstance(campaign, dict):
        raise ValueError("resume artifact has no campaign state")
    completed = int(campaign.get("completed_stage", -1))
    stages = campaign.get("stages")
    if not isinstance(stages, list) or len(stages) != completed:
        raise ValueError("resume stage history is inconsistent")
    if not 0 <= completed <= CANONICAL_CONTINUATION_STEPS:
        raise ValueError("resume completed stage is invalid")
    in_progress: dict[str, Any] | None = None
    if "in_progress_stage" in campaign:
        stage_number = int(campaign["in_progress_stage"])
        history = campaign.get("accepted_newton_history")
        if stage_number != completed + 1 or not isinstance(history, list):
            raise ValueError("resume in-progress stage is inconsistent")
        in_progress = {"stage_number": stage_number, "history": history}
    return completed, stages, in_progress


def _require_resume_crosscheck_clear(
    report: dict[str, Any],
    completed_stage: int,
    requested_stop_stage: int,
) -> None:
    """Prevent a saved scientific-gate conflict crossing an invocation."""

    crosschecks = report.get("spatial_principal_crosschecks")
    conflict = bool(
        isinstance(crosschecks, dict)
        and crosschecks.get("crosscheck_conflicts_with_wide_gate")
    )
    if conflict and requested_stop_stage > completed_stage:
        raise RuntimeError(
            "E-028 saved fixed/centered admissibility conflict is a hard stop "
            "before any later continuation stage"
        )


def _default_output_artifact(
    stop_after_stage: int,
    preconditioner_kind: str,
) -> Path:
    """Choose a configuration-labeled artifact path without aliasing PG-SA."""

    directory = Path(__file__).resolve().parent / "checkpoints"
    if stop_after_stage == CANONICAL_CONTINUATION_STEPS:
        stage_label = "full_source"
    else:
        stage_label = f"{stop_after_stage}of12"
    return directory / (
        f"e028_h0125_m4_{stage_label}_{preconditioner_kind}.npz"
    )


def run_canonical_campaign(
    *,
    stop_after_stage: int = 1,
    checkpoint_path: str | Path = DEFAULT_CHECKPOINT,
    output_artifact: str | Path | None = None,
    resume: bool = False,
    configuration: AmgConfiguration = AmgConfiguration(),
) -> tuple[np.ndarray, dict[str, Any]]:
    """Run or resume the canonical E-028 campaign through a requested stage."""

    if not 1 <= stop_after_stage <= CANONICAL_CONTINUATION_STEPS:
        raise ValueError("stop_after_stage must lie between 1 and 12")
    configuration.validate()
    checkpoint = Path(checkpoint_path)
    if checkpoint.exists() and not resume:
        raise FileExistsError(
            f"checkpoint already exists: {checkpoint}; pass resume=True"
        )

    peak_before = peak_rss_bytes()
    build_started = time.perf_counter()
    system = build_system(_canonical_grid())
    build_seconds = time.perf_counter() - build_started
    peak_after_build = peak_rss_bytes()
    full_source, source_metadata = smooth_annulus_source(system)

    if resume:
        field, full_linear_field, prior_report = load_campaign_checkpoint(
            checkpoint
        )
        completed_stage, stages, in_progress = _validate_resume_report(
            prior_report, system, full_source, configuration
        )
        if field.shape != (system.size,):
            raise ValueError("resume field does not match the canonical grid")
        preparation = dict(prior_report.get("preparation", {}))
        preparation["resume_build_seconds"] = build_seconds
        preparation["resume_peak_rss_bytes_after_build"] = peak_after_build
        preparation["resume_reused_saved_full_linear_field"] = True
        base = _base_report(
            system, full_source, source_metadata, configuration, preparation
        )
        resume_branch = _branch_summary(system, field)
        if not resume_branch["passes"]:
            raise ValueError("resume field is outside the admissible normal branch")
        base["resume"] = {
            "checkpoint": str(checkpoint.resolve()),
            "completed_stage": completed_stage,
            "field_sha256": _sha256_array(field),
            "branch": resume_branch,
        }
        _require_resume_crosscheck_clear(
            prior_report, completed_stage, stop_after_stage
        )
    else:
        linear_started = time.perf_counter()
        full_linear_field = solve_linear_reference(system, full_source)
        linear_seconds = time.perf_counter() - linear_started
        initial_predictor = full_linear_field / CANONICAL_CONTINUATION_STEPS
        predictor_branch = _branch_summary(system, initial_predictor)
        if not predictor_branch["passes"]:
            raise RuntimeError(
                "native fine-grid 1/12 Poisson predictor failed its branch gate"
            )
        preparation = {
            "build_seconds": build_seconds,
            "linear_solve_seconds": linear_seconds,
            "peak_rss_bytes_before": peak_before,
            "peak_rss_bytes_after_build": peak_after_build,
            "peak_rss_bytes_after_linear_solve": peak_rss_bytes(),
            "initial_predictor": {
                "kind": "native (1/12) phi_linear",
                "field_sha256": _sha256_array(initial_predictor),
                "full_linear_field_sha256": _sha256_array(full_linear_field),
                "branch": predictor_branch,
            },
        }
        base = _base_report(
            system, full_source, source_metadata, configuration, preparation
        )
        field = initial_predictor
        completed_stage = 0
        stages: list[dict[str, Any]] = []
        in_progress = None
        preflight_report = _preflight_checkpoint_report(
            base, field, stop_after_stage
        )
        save_campaign_checkpoint(
            checkpoint, field, full_linear_field, preflight_report
        )

    if stop_after_stage < completed_stage:
        raise ValueError("requested stop stage precedes the saved checkpoint")
    if (
        in_progress is not None
        and stop_after_stage < int(in_progress["stage_number"])
    ):
        raise ValueError("requested stop stage precedes in-progress accepted work")
    first_stage = (
        int(in_progress["stage_number"])
        if in_progress is not None
        else completed_stage + 1
    )
    if first_stage > stop_after_stage + 1:
        raise ValueError("requested stop stage conflicts with in-progress state")
    for stage_number in range(first_stage, stop_after_stage + 1):
        amplitude = stage_number / CANONICAL_CONTINUATION_STEPS
        prior_history = (
            list(in_progress["history"])
            if in_progress is not None
            and int(in_progress["stage_number"]) == stage_number
            else None
        )

        def save_accepted_step(
            accepted_field: np.ndarray,
            accepted_history: list[dict[str, Any]],
        ) -> None:
            progress = _in_progress_checkpoint_report(
                base,
                accepted_field,
                stages,
                stage_number,
                accepted_history,
                stop_after_stage,
            )
            progress["campaign"]["target_source_digest"] = e025._source_digest(
                amplitude * full_source
            )
            save_campaign_checkpoint(
                checkpoint,
                accepted_field,
                full_linear_field,
                progress,
            )

        try:
            field, stage = solve_one_stage(
                system,
                full_source,
                field,
                amplitude,
                configuration,
                prior_history=prior_history,
                accepted_step_callback=save_accepted_step,
            )
        except Exception as error:
            saved_field, saved_linear, failure_report = load_campaign_checkpoint(
                checkpoint
            )
            failure_report["campaign"]["last_failure"] = {
                "stage_number": stage_number,
                "amplitude": amplitude,
                "error_type": type(error).__name__,
                "message": str(error),
                "peak_rss_bytes": peak_rss_bytes(),
            }
            save_campaign_checkpoint(
                checkpoint, saved_field, saved_linear, failure_report
            )
            raise
        stages.append(stage)
        in_progress = None
        report = _report_after_stage(
            base,
            system,
            full_source,
            source_metadata,
            full_linear_field,
            field,
            stages,
            stop_after_stage,
        )
        save_campaign_checkpoint(checkpoint, field, full_linear_field, report)
        if (
            report["spatial_principal_crosschecks"]
            ["crosscheck_conflicts_with_wide_gate"]
            and stage_number < stop_after_stage
        ):
            raise RuntimeError(
                "E-028 fixed/centered admissibility conflict is a hard stop "
                "before any later continuation stage"
            )

    if stop_after_stage == completed_stage:
        report = _report_after_stage(
            base,
            system,
            full_source,
            source_metadata,
            full_linear_field,
            field,
            stages,
            stop_after_stage,
        )
    if output_artifact is not None:
        save_campaign_artifact(output_artifact, field, report)
    return field, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stop-after-stage",
        type=int,
        default=1,
        help="absolute continuation stage to reach, from 1 through 12",
    )
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output-artifact", type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--preconditioner", choices=("pgsa", "air"), default="pgsa")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    configuration = AmgConfiguration(kind=args.preconditioner)
    output = args.output_artifact
    if output is None:
        output = _default_output_artifact(
            args.stop_after_stage, args.preconditioner
        )
    _, report = run_canonical_campaign(
        stop_after_stage=args.stop_after_stage,
        checkpoint_path=args.checkpoint,
        output_artifact=output,
        resume=args.resume,
        configuration=configuration,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        campaign = report["campaign"]
        diagnostics = report["current_stage_diagnostics"]
        nonlinear = campaign["stages"][-1]["nonlinear"]
        crosschecks = report["spatial_principal_crosschecks"]
        print(
            f"completed stage {campaign['completed_stage']}/12; "
            f"relative L2={nonlinear['relative_residual_l2']:.6e}; "
            f"wide pair/spatial/time={nonlinear['minimum_pair_sum']:.6e}/"
            f"{nonlinear['minimum_spatial_principal']:.6e}/"
            f"{nonlinear['minimum_time_kinetic']:.6e}"
        )
        print(
            "centered original/White residuals="
            f"{diagnostics['independent_centered_residual']['original_relative_volume_l2']:.6e}/"
            f"{diagnostics['independent_centered_residual']['white_root_relative_volume_l2']:.6e}; "
            "crosscheck conflict="
            f"{crosschecks['crosscheck_conflicts_with_wide_gate']}"
        )


if __name__ == "__main__":
    main()

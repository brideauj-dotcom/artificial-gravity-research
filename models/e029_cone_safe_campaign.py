#!/usr/bin/env python3
"""E-029 diagnostic-cone-safe retry of the blocked E-028 stage-7 interval.

E-028's canonical ``6/12 -> 7/12`` Newton path reached a positive endpoint
but failed its predeclared independent-cone and low-margin-tail gates.  This
module preserves that negative history and defines a new numerical experiment:

* start from the immutable accepted E-028 ``6/12`` checkpoint;
* subdivide the source interval first at ``13/24`` and only then try
  ``14/24``;
* keep every accepted Newton state and nine interior points on each accepted
  correction segment inside active, fixed-coordinate, native-centered, and
  matched-step-centered shifted ``Gamma_2`` diagnostics;
* compare each converged endpoint with the predeclared ``6/12`` matched-step
  ``pair < 0.05`` and ``pair < 0.02`` source-relative tail caps; and
* repeat the interval on a freshly reconstructed coarse control.

The path/tail screen is deliberately not an endpoint generalized-Jacobian
certificate.  If it ever passes, all genuine endpoint active-frame tie
selections and the promised WCDD/M-matrix diagnostics remain a separate
required gate before any accepted-lineage change.

The sampled path is not an interval enclosure, a uniqueness proof, or a
continuum-convergence result.  The underlying cubic-Galileon PDE is
hypothetical, and this calculation is not evidence for artificial gravity,
inertial control, spacetime engineering, FTL travel, or propulsion.
"""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
import math
from pathlib import Path
import time
from typing import Any, Callable

import numpy as np

import models.e025_axisymmetric_wide_2hessian as e025
import models.e026_nonsymmetric_amg as e026
import models.e028_fine_grid_campaign as e028
from models.e025_axisymmetric_wide_2hessian import AxisymmetricGrid
from models.e026_nonsymmetric_amg import AmgConfiguration


ACCEPTED_STAGE6_CHECKPOINT = (
    Path(__file__).resolve().parent
    / "checkpoints"
    / "e028_h0125_m4_campaign_checkpoint_20260725.npz"
)
ACCEPTED_STAGE6_CHECKPOINT_SHA256 = (
    "ff82363833c84e416e020a8df56d6067b6b1f7612c41f30f6499d6b95690babb"
)
ACCEPTED_STAGE6_FIELD_SHA256 = (
    "cd806ff41c0a33d541cc5c1dba44a3c7ad693ddb6b81dda5eae2ac1db8757c3e"
)
ACCEPTED_STAGE6_LINEAR_FIELD_SHA256 = (
    "6fe081d1b9eb5a02e88e6c0e79531f6419aa35053f75c87090cf03be1f5bc606"
)
ACCEPTED_STAGE6_REPORT_SHA256 = (
    "fe2c11e1d2e7806b12836325eaaed565137b5495efbb25417f4c6545fd3a256c"
)
CANONICAL_FAILED_STAGE7_ARTIFACT_SHA256 = (
    "96ce02aca8198d23c1bb5c563bdf18b14c79ef4009dd03fd75fa2e77525c479b"
)

TARGET_AMPLITUDES = (13.0 / 24.0, 14.0 / 24.0)
SEGMENT_INTERIOR_SAMPLES = 9
MATCHED_DIFFERENCE_STEP = 0.25
COMMON_WINDOW_RADIUS = 78.5
TAIL_THRESHOLDS = (0.05, 0.02)
TAIL_RELATIVE_TOLERANCE = 1.0e-10

# These values were declared by E-028 before E-029 was run and are reproduced
# from the immutable fine stage-6 field using the definitions below.
FINE_STAGE6_REFERENCE_CAPS = {
    "0.05": {
        "node_count": 227,
        "positive_weight_node_count": 223,
        "component_count": 1,
        "source_support_weight_fraction": 0.003138623639587411,
        "source_transition_weight_fraction": 0.003190016417728476,
        "largest_component_source_support_weight_fraction": (
            0.003138623639587411
        ),
    },
    "0.02": {
        "node_count": 10,
        "positive_weight_node_count": 10,
        "component_count": 1,
        "source_support_weight_fraction": 0.0002703160150325283,
        "source_transition_weight_fraction": 0.00027474225168394454,
        "largest_component_source_support_weight_fraction": (
            0.0002703160150325283
        ),
    },
}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_array(values: np.ndarray) -> str:
    return e028._sha256_array(values)


def implementation_provenance() -> dict[str, Any]:
    """Fingerprint the new campaign without changing E-028 provenance."""

    paths = {
        "e029_campaign": Path(__file__).resolve(),
        "e028_campaign": Path(e028.__file__).resolve(),
        "e025_operator": Path(e025.__file__).resolve(),
        "e026_amg": Path(e026.__file__).resolve(),
        "research_requirements": Path(__file__).resolve().parents[1]
        / "requirements-research.txt",
    }
    repository_root = Path(__file__).resolve().parents[1]
    return {
        "modules": {
            name: {
                "path": str(path.relative_to(repository_root)),
                "sha256": _sha256_file(path),
            }
            for name, path in paths.items()
        },
        "campaign": "E-029",
        "campaign_checkpoint_schema": 1,
        "strategy": {
            "target_amplitudes": list(TARGET_AMPLITUDES),
            "segment_interior_samples": SEGMENT_INTERIOR_SAMPLES,
            "matched_difference_step": MATCHED_DIFFERENCE_STEP,
            "common_window_radius": COMMON_WINDOW_RADIUS,
            "tail_thresholds": list(TAIL_THRESHOLDS),
            "tail_policy": (
                "Each converged amplitude endpoint must not exceed its grid's "
                "stage-6 node, component, source-support-weight, or largest-"
                "component source-support-weight baseline. Off-root tails are "
                "recorded but are not treated as source-homotopy endpoints."
            ),
        },
    }


def _eigenvalues_from_components(
    radial: np.ndarray,
    mixed: np.ndarray,
    axial: np.ndarray,
    azimuthal: np.ndarray,
    shift: float,
) -> np.ndarray:
    gap = np.sqrt((radial - axial) ** 2 + 4.0 * mixed**2)
    low = 0.5 * (radial + axial - gap)
    high = 0.5 * (radial + axial + gap)
    return (
        np.sort(np.stack((low, high, azimuthal), axis=-1), axis=-1)
        + float(shift)
    )


def _gamma_summary(
    eigenvalues: np.ndarray,
    rho: np.ndarray,
    z: np.ndarray,
) -> dict[str, Any]:
    values = np.asarray(eigenvalues, dtype=float)
    sigma1 = np.sum(values, axis=-1)
    pair = values[:, 0] + values[:, 1]
    sigma2 = (
        values[:, 0] * values[:, 1]
        + values[:, 0] * values[:, 2]
        + values[:, 1] * values[:, 2]
    )

    def minimum_record(quantity: np.ndarray) -> dict[str, Any]:
        index = int(np.argmin(quantity))
        return {
            "value": float(quantity[index]),
            "rho": float(rho[index]),
            "z": float(z[index]),
            "eigenvalues": [float(item) for item in values[index]],
        }

    nonpositive = {
        "sigma1": int(np.count_nonzero(sigma1 <= 0.0)),
        "pair": int(np.count_nonzero(pair <= 0.0)),
        "sigma2": int(np.count_nonzero(sigma2 <= 0.0)),
    }
    return {
        "evaluated_nodes": int(values.shape[0]),
        "minimum_sigma1": minimum_record(sigma1),
        "minimum_pair_sum": minimum_record(pair),
        "minimum_sigma2": minimum_record(sigma2),
        "nonpositive_counts": nonpositive,
        "passes": bool(all(count == 0 for count in nonpositive.values())),
    }


def _centered_eigenvalues(
    system: Any,
    field: np.ndarray,
    *,
    difference_step: float,
    maximum_radius: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    radius = np.hypot(system.rho, system.z)
    mask = radius <= maximum_radius + 1.0e-12
    rho = system.rho[mask]
    z = system.z[mask]
    phi_r, _phi_z, radial, mixed, axial = (
        e025.interpolated_cylindrical_derivatives(
            system,
            field,
            rho,
            z,
            difference_step=difference_step,
        )
    )
    azimuthal = np.divide(
        phi_r,
        rho,
        out=radial.copy(),
        where=rho > 0.5 * difference_step,
    )
    eigenvalues = _eigenvalues_from_components(
        radial,
        mixed,
        axial,
        azimuthal,
        system.shift,
    )
    return eigenvalues, rho, z, np.flatnonzero(mask)


def full_gamma_diagnostics(
    system: Any,
    field: np.ndarray,
) -> dict[str, Any]:
    """Evaluate every E-029 full-cone reconstruction on one field."""

    _operator, active, curvatures = e025.monotone_operator(system, field)
    nodes = np.arange(system.size)
    active_values = np.sort(curvatures[active, nodes], axis=-1)
    active_summary = _gamma_summary(
        active_values,
        system.rho,
        system.z,
    )

    fixed_components = e025.fixed_coordinate_hessian_components(system, field)
    fixed_values = _eigenvalues_from_components(
        fixed_components[0],
        fixed_components[1],
        fixed_components[2],
        fixed_components[3],
        system.shift,
    )
    fixed_summary = _gamma_summary(fixed_values, system.rho, system.z)

    native_step = float(system.grid.spacing)
    native_radius = (
        system.grid.radial_max - 3.0 * math.sqrt(2.0) * native_step
    )
    native_values, native_rho, native_z, _ = _centered_eigenvalues(
        system,
        field,
        difference_step=native_step,
        maximum_radius=native_radius,
    )
    native_summary = _gamma_summary(native_values, native_rho, native_z)
    native_summary["difference_step"] = native_step
    native_summary["maximum_radius"] = native_radius

    matched_radius = min(COMMON_WINDOW_RADIUS, native_radius)
    matched_values, matched_rho, matched_z, _ = _centered_eigenvalues(
        system,
        field,
        difference_step=MATCHED_DIFFERENCE_STEP,
        maximum_radius=matched_radius,
    )
    matched_summary = _gamma_summary(matched_values, matched_rho, matched_z)
    matched_summary["difference_step"] = MATCHED_DIFFERENCE_STEP
    matched_summary["maximum_radius"] = matched_radius

    reconstructions = {
        "active": active_summary,
        "fixed": fixed_summary,
        "centered_native": native_summary,
        "centered_matched": matched_summary,
    }
    return {
        "reconstructions": reconstructions,
        "passes": bool(
            all(summary["passes"] for summary in reconstructions.values())
        ),
    }


def _connected_components(
    system: Any,
    selected_global_nodes: np.ndarray,
    weights: np.ndarray,
    source_support: np.ndarray,
    source_support_weight: float,
) -> list[dict[str, Any]]:
    selected = np.zeros(system.size, dtype=bool)
    selected[np.asarray(selected_global_nodes, dtype=int)] = True
    visited = np.zeros(system.size, dtype=bool)
    spacing = float(system.grid.spacing)
    components: list[dict[str, Any]] = []
    for start in np.flatnonzero(selected):
        if visited[start]:
            continue
        queue: deque[int] = deque([int(start)])
        visited[start] = True
        members: list[int] = []
        while queue:
            node = queue.popleft()
            members.append(node)
            radial_index = int(round(float(system.rho[node]) / spacing))
            axial_index = int(round(float(system.z[node]) / spacing))
            for delta_radial, delta_axial in (
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1),
            ):
                next_radial = radial_index + delta_radial
                next_axial = axial_index + delta_axial
                if (
                    next_radial < 0
                    or next_axial < 0
                    or next_radial >= system.index_map.shape[0]
                    or next_axial >= system.index_map.shape[1]
                ):
                    continue
                neighbor = int(system.index_map[next_radial, next_axial])
                if (
                    neighbor >= 0
                    and selected[neighbor]
                    and not visited[neighbor]
                ):
                    visited[neighbor] = True
                    queue.append(neighbor)
        member_array = np.asarray(members, dtype=int)
        component_support_weight = float(
            np.sum(weights[member_array] * source_support[member_array])
        )
        components.append(
            {
                "node_count": int(member_array.size),
                "positive_weight_node_count": int(
                    np.count_nonzero(weights[member_array] > 0.0)
                ),
                "rho_min": float(np.min(system.rho[member_array])),
                "rho_max": float(np.max(system.rho[member_array])),
                "z_min": float(np.min(system.z[member_array])),
                "z_max": float(np.max(system.z[member_array])),
                "source_support_weight_fraction": (
                    component_support_weight / source_support_weight
                    if source_support_weight > 0.0
                    else 0.0
                ),
            }
        )
    components.sort(
        key=lambda item: (
            item["source_support_weight_fraction"],
            item["node_count"],
        ),
        reverse=True,
    )
    return components


def matched_tail_diagnostics(
    system: Any,
    field: np.ndarray,
    full_source: np.ndarray,
) -> dict[str, Any]:
    """Measure the predeclared matched-step low-pair source-layer tails."""

    maximum_radius = min(
        COMMON_WINDOW_RADIUS,
        system.grid.radial_max
        - 3.0 * math.sqrt(2.0) * MATCHED_DIFFERENCE_STEP,
    )
    eigenvalues, rho, z, global_nodes = _centered_eigenvalues(
        system,
        field,
        difference_step=MATCHED_DIFFERENCE_STEP,
        maximum_radius=maximum_radius,
    )
    pair = eigenvalues[:, 0] + eigenvalues[:, 1]
    all_weights = e025.nodal_volume_weights(system)
    weights = all_weights[global_nodes]
    source = np.asarray(full_source, dtype=float)
    source_support_global = source > 0.0
    source_transition_global = (source > 0.0) & (
        source < float(np.max(source)) * (1.0 - 1.0e-12)
    )
    source_support = source_support_global[global_nodes]
    source_transition = source_transition_global[global_nodes]
    window_weight = float(np.sum(weights))
    support_weight = float(np.sum(weights[source_support]))
    transition_weight = float(np.sum(weights[source_transition]))
    thresholds: dict[str, Any] = {}
    for threshold in TAIL_THRESHOLDS:
        low = pair < threshold
        selected_global = global_nodes[low]
        components = _connected_components(
            system,
            selected_global,
            all_weights,
            source_support_global,
            support_weight,
        )
        thresholds[f"{threshold:.2f}"] = {
            "threshold": threshold,
            "node_count": int(np.count_nonzero(low)),
            "positive_weight_node_count": int(
                np.count_nonzero(weights[low] > 0.0)
            ),
            "full_window_weight_fraction": (
                float(np.sum(weights[low])) / window_weight
                if window_weight > 0.0
                else 0.0
            ),
            "source_support_weight_fraction": (
                float(np.sum(weights[low & source_support])) / support_weight
                if support_weight > 0.0
                else 0.0
            ),
            "source_transition_weight_fraction": (
                float(np.sum(weights[low & source_transition]))
                / transition_weight
                if transition_weight > 0.0
                else 0.0
            ),
            "component_count": len(components),
            "components": components,
        }
    return {
        "difference_step": MATCHED_DIFFERENCE_STEP,
        "maximum_radius": maximum_radius,
        "evaluated_nodes": int(global_nodes.size),
        "minimum_pair_sum": float(np.min(pair)),
        "thresholds": thresholds,
    }


def tail_caps_from_baseline(diagnostics: dict[str, Any]) -> dict[str, Any]:
    """Freeze a grid's stage-6 endpoint as a no-broadening ceiling."""

    caps: dict[str, Any] = {}
    for key, row in diagnostics["thresholds"].items():
        components = row["components"]
        caps[key] = {
            "node_count": int(row["node_count"]),
            "positive_weight_node_count": int(
                row["positive_weight_node_count"]
            ),
            "component_count": int(row["component_count"]),
            "source_support_weight_fraction": float(
                row["source_support_weight_fraction"]
            ),
            "source_transition_weight_fraction": float(
                row["source_transition_weight_fraction"]
            ),
            "largest_component_source_support_weight_fraction": (
                float(components[0]["source_support_weight_fraction"])
                if components
                else 0.0
            ),
        }
    return caps


def evaluate_tail_gate(
    diagnostics: dict[str, Any],
    caps: dict[str, Any],
) -> dict[str, Any]:
    comparisons: dict[str, Any] = {}
    passes = True
    for key, cap in caps.items():
        row = diagnostics["thresholds"][key]
        components = row["components"]
        largest = (
            float(components[0]["source_support_weight_fraction"])
            if components
            else 0.0
        )
        checks = {
            "node_count": bool(row["node_count"] <= cap["node_count"]),
            "positive_weight_node_count": bool(
                row["positive_weight_node_count"]
                <= cap["positive_weight_node_count"]
            ),
            "component_count": bool(
                row["component_count"] <= cap["component_count"]
            ),
            "source_support_weight_fraction": bool(
                row["source_support_weight_fraction"]
                <= cap["source_support_weight_fraction"]
                * (1.0 + TAIL_RELATIVE_TOLERANCE)
                + np.finfo(float).eps
            ),
            "source_transition_weight_fraction": bool(
                row["source_transition_weight_fraction"]
                <= cap["source_transition_weight_fraction"]
                * (1.0 + TAIL_RELATIVE_TOLERANCE)
                + np.finfo(float).eps
            ),
            "largest_component_source_support_weight_fraction": bool(
                largest
                <= cap["largest_component_source_support_weight_fraction"]
                * (1.0 + TAIL_RELATIVE_TOLERANCE)
                + np.finfo(float).eps
            ),
        }
        row_passes = bool(all(checks.values()))
        comparisons[key] = {
            "passes": row_passes,
            "checks": checks,
            "observed": {
                "node_count": int(row["node_count"]),
                "positive_weight_node_count": int(
                    row["positive_weight_node_count"]
                ),
                "component_count": int(row["component_count"]),
                "source_support_weight_fraction": float(
                    row["source_support_weight_fraction"]
                ),
                "source_transition_weight_fraction": float(
                    row["source_transition_weight_fraction"]
                ),
                "largest_component_source_support_weight_fraction": largest,
            },
            "caps": cap,
        }
        passes = passes and row_passes
    return {"passes": bool(passes), "comparisons": comparisons}


def _minimum_cone_margins(
    diagnostics: list[dict[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name in (
        "active",
        "fixed",
        "centered_native",
        "centered_matched",
    ):
        result[name] = {
            "minimum_sigma1": min(
                item["reconstructions"][name]["minimum_sigma1"]["value"]
                for item in diagnostics
            ),
            "minimum_pair_sum": min(
                item["reconstructions"][name]["minimum_pair_sum"]["value"]
                for item in diagnostics
            ),
            "minimum_sigma2": min(
                item["reconstructions"][name]["minimum_sigma2"]["value"]
                for item in diagnostics
            ),
        }
    return result


def _segment_cone_audit(
    system: Any,
    start: np.ndarray,
    end: np.ndarray,
) -> dict[str, Any]:
    samples: list[dict[str, Any]] = []
    for index in range(1, SEGMENT_INTERIOR_SAMPLES + 1):
        fraction = index / (SEGMENT_INTERIOR_SAMPLES + 1)
        diagnostics = full_gamma_diagnostics(
            system,
            start + fraction * (end - start),
        )
        sample_field = start + fraction * (end - start)
        samples.append(
            {
                "fraction": fraction,
                "field_sha256": _sha256_array(sample_field),
                "diagnostics": diagnostics,
            }
        )
    return {
        "sample_count": SEGMENT_INTERIOR_SAMPLES,
        "samples": samples,
        "passes": bool(
            all(item["diagnostics"]["passes"] for item in samples)
        ),
        "minimum_margins": _minimum_cone_margins(
            [item["diagnostics"] for item in samples]
        ),
    }


def solve_cone_safe_stage(
    system: Any,
    full_source: np.ndarray,
    initial_field: np.ndarray,
    amplitude: float,
    configuration: AmgConfiguration,
    *,
    nonlinear_relative_tolerance: float = e028.NONLINEAR_RELATIVE_TOLERANCE,
    newton_max_iterations: int = e028.NEWTON_MAX_ITERATIONS,
    accepted_step_callback: (
        Callable[[np.ndarray, list[dict[str, Any]]], None] | None
    ) = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Close one source value with E-028 gates plus E-029 cone sampling."""

    configuration.validate()
    if not 0.0 < amplitude <= 1.0:
        raise ValueError("stage amplitude must lie in (0, 1]")
    source = amplitude * np.asarray(full_source, dtype=float)
    field = np.asarray(initial_field, dtype=float).copy()
    if source.shape != (system.size,) or field.shape != (system.size,):
        raise ValueError("stage arrays do not match the system")
    if not np.all(np.isfinite(field)):
        raise ValueError("stage field must be finite")
    initial_cones = full_gamma_diagnostics(system, field)
    if not initial_cones["passes"]:
        raise ValueError("E-029 initial field fails a full-Gamma2 reconstruction")

    stage_scale = max(
        float(np.linalg.norm(source)) / (2.0 * system.cubic_coefficient),
        np.finfo(float).tiny,
    )
    history: list[dict[str, Any]] = []
    total_setup_seconds = 0.0
    total_solve_seconds = 0.0
    started = time.perf_counter()
    for newton_iteration in range(1, newton_max_iterations + 1):
        operator, active, curvatures = e025.monotone_operator(system, field)
        pair, spatial, time_coefficient = e025.scheme_diagnostics(
            system, curvatures
        )
        if pair <= 0.0 or spatial <= 0.0 or time_coefficient <= 0.0:
            raise RuntimeError("E-029 accepted field left an E-028 wide gate")
        current_cones = full_gamma_diagnostics(system, field)
        if not current_cones["passes"]:
            raise RuntimeError("E-029 accepted field left a full-Gamma2 cone")
        residual = operator - e025.shifted_rhs(
            source, system.cubic_coefficient
        )
        residual_norm = float(np.linalg.norm(residual))
        relative_before = residual_norm / stage_scale
        if relative_before < nonlinear_relative_tolerance:
            break
        nodes = np.arange(system.size)
        active_gradient = e025.monotone_sigma_gradient(
            curvatures[active, nodes]
        )
        jacobian = e025.active_jacobian_matrix(
            system, active, active_gradient
        )
        correction, linear_report = e028._solve_linear_corrector_strict(
            jacobian, residual, system, configuration
        )
        if not linear_report["passes_strict_krylov_gate"]:
            raise RuntimeError(
                "E-029 strict Krylov failure: "
                f"info={linear_report['gmres_info']}; "
                f"true_ratio={linear_report['true_linear_residual_ratio']:.6e}"
            )

        accepted = False
        step = 1.0
        rejected_trials: list[dict[str, Any]] = []
        for _ in range(24):
            trial = field + step * correction
            trial_operator, _, trial_curvatures = e025.monotone_operator(
                system, trial
            )
            trial_residual = trial_operator - e025.shifted_rhs(
                source, system.cubic_coefficient
            )
            trial_pair, trial_spatial, trial_time = e025.scheme_diagnostics(
                system, trial_curvatures
            )
            sufficient_decrease = float(np.linalg.norm(trial_residual)) < (
                residual_norm * (1.0 - 1.0e-4 * step)
            )
            wide_passes = bool(
                trial_pair > 0.0
                and trial_spatial > 0.0
                and trial_time > 0.0
            )
            trial_cones = (
                full_gamma_diagnostics(system, trial)
                if sufficient_decrease and wide_passes
                else None
            )
            segment = (
                _segment_cone_audit(system, field, trial)
                if trial_cones is not None and trial_cones["passes"]
                else None
            )
            if (
                sufficient_decrease
                and wide_passes
                and trial_cones is not None
                and trial_cones["passes"]
                and segment is not None
                and segment["passes"]
            ):
                previous = field
                field = trial
                accepted = True
                relative_after = float(
                    np.linalg.norm(trial_residual) / stage_scale
                )
                break
            rejected_trials.append(
                {
                    "step": step,
                    "sufficient_decrease": sufficient_decrease,
                    "wide_passes": wide_passes,
                    "cones_pass": (
                        trial_cones["passes"]
                        if trial_cones is not None
                        else None
                    ),
                    "segment_passes": (
                        segment["passes"] if segment is not None else None
                    ),
                }
            )
            step *= 0.5
        if not accepted:
            raise RuntimeError(
                "E-029 cone-safe line search exhausted 24 halvings; "
                f"relative_residual={relative_before:.6e}"
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
            "full_gamma": trial_cones,
            "segment_audit": segment,
            "rejected_trials": rejected_trials,
            "linear": linear_report,
            "accepted_field_sha256": _sha256_array(field),
            "increment_relative_l2": float(
                np.linalg.norm(field - previous)
                / max(np.linalg.norm(field), np.finfo(float).tiny)
            ),
        }
        history.append(row)
        if accepted_step_callback is not None:
            accepted_step_callback(field, history)

    final_operator, _, final_curvatures = e025.monotone_operator(system, field)
    final_residual = final_operator - e025.shifted_rhs(
        source, system.cubic_coefficient
    )
    relative_l2 = float(np.linalg.norm(final_residual) / stage_scale)
    source_linf_scale = max(
        float(np.max(source)) / (2.0 * system.cubic_coefficient),
        np.finfo(float).tiny,
    )
    relative_linf = float(np.max(np.abs(final_residual)) / source_linf_scale)
    pair, spatial, time_coefficient = e025.scheme_diagnostics(
        system, final_curvatures
    )
    final_cones = full_gamma_diagnostics(system, field)
    if relative_l2 >= nonlinear_relative_tolerance:
        raise RuntimeError(
            "E-029 stage exhausted the Newton cap; "
            f"relative_l2={relative_l2:.6e}"
        )
    if (
        pair <= 0.0
        or spatial <= 0.0
        or time_coefficient <= 0.0
        or not final_cones["passes"]
    ):
        raise RuntimeError("E-029 converged endpoint fails a cone gate")
    return field, {
        "amplitude": amplitude,
        "target_source_digest": e025._source_digest(source),
        "configuration": e026.configuration_provenance(configuration),
        "newton_iterations": len(history),
        "summed_gmres_inner_iterations": int(
            sum(row["linear"]["inner_iterations"] for row in history)
        ),
        "summed_setup_seconds": total_setup_seconds,
        "summed_solve_seconds": total_solve_seconds,
        "elapsed_seconds": time.perf_counter() - started,
        "relative_residual_l2": relative_l2,
        "relative_residual_linf": relative_linf,
        "minimum_pair_sum": pair,
        "minimum_spatial_principal": spatial,
        "minimum_time_kinetic": time_coefficient,
        "full_gamma": final_cones,
        "history": history,
        "output_field_sha256": _sha256_array(field),
    }


def _validate_accepted_stage6(
    checkpoint_path: Path,
    system: Any,
    full_source: np.ndarray,
    configuration: AmgConfiguration,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    container_sha = _sha256_file(checkpoint_path)
    if container_sha != ACCEPTED_STAGE6_CHECKPOINT_SHA256:
        raise ValueError(
            "E-029 stage-6 checkpoint container SHA-256 does not match"
        )
    field, linear_field, report = e028.load_campaign_checkpoint(
        checkpoint_path
    )
    if _sha256_array(field) != ACCEPTED_STAGE6_FIELD_SHA256:
        raise ValueError("E-029 stage-6 field SHA-256 does not match")
    if _sha256_array(linear_field) != ACCEPTED_STAGE6_LINEAR_FIELD_SHA256:
        raise ValueError("E-029 stage-6 linear-field SHA-256 does not match")
    report_digest = hashlib.sha256(
        e028._canonical_json(report).encode("utf-8")
    ).hexdigest()
    if report_digest != ACCEPTED_STAGE6_REPORT_SHA256:
        raise ValueError("E-029 immutable E-028 report SHA-256 does not match")
    expected_operator = {
        "system_digest": e025._system_digest(system),
        "full_source_digest": e025._source_digest(full_source),
    }
    actual_operator = report.get("operator_and_source", {})
    for key, value in expected_operator.items():
        if actual_operator.get(key) != value:
            raise ValueError(f"E-029 stage-6 {key} does not match")
    if report.get("runtime_provenance") != e026.runtime_provenance():
        raise ValueError("E-029 stage-6 runtime provenance does not match")
    if report.get("configuration", {}).get(
        "amg"
    ) != e026.configuration_provenance(configuration):
        raise ValueError("E-029 stage-6 AMG provenance does not match")
    historical_implementation = report.get("implementation_provenance", {})
    current_implementation = e028.implementation_provenance()
    if {
        name: values.get("sha256")
        for name, values in historical_implementation.get("modules", {}).items()
    } != {
        name: values.get("sha256")
        for name, values in current_implementation.get("modules", {}).items()
    }:
        raise ValueError(
            "E-029 E-028 content fingerprints do not match after path migration"
        )
    for key in ("artifact_format", "campaign_checkpoint_schema"):
        if historical_implementation.get(key) != current_implementation.get(key):
            raise ValueError(f"E-029 E-028 {key} does not match")
    campaign = report.get("campaign", {})
    completed = int(campaign.get("completed_stage", -1))
    stages = campaign.get("stages")
    if (
        completed != 6
        or not math.isclose(
            float(campaign.get("completed_amplitude", -1.0)),
            0.5,
            rel_tol=0.0,
            abs_tol=0.0,
        )
        or not isinstance(stages, list)
        or len(stages) != 6
        or "in_progress_stage" in campaign
    ):
        raise ValueError("E-029 input is not the immutable completed stage 6")
    return field, linear_field, report


def _verify_fine_reference_caps(
    observed: dict[str, Any],
) -> None:
    for key, expected in FINE_STAGE6_REFERENCE_CAPS.items():
        actual = tail_caps_from_baseline(observed)[key]
        if actual["node_count"] != expected["node_count"]:
            raise ValueError(f"E-029 fine stage-6 {key} node cap drifted")
        if actual["component_count"] != expected["component_count"]:
            raise ValueError(f"E-029 fine stage-6 {key} component cap drifted")
        for metric in (
            "source_support_weight_fraction",
            "source_transition_weight_fraction",
            "largest_component_source_support_weight_fraction",
        ):
            if not math.isclose(
                actual[metric],
                expected[metric],
                rel_tol=1.0e-12,
                abs_tol=1.0e-15,
            ):
                raise ValueError(
                    f"E-029 fine stage-6 {key} {metric} cap drifted"
                )
        if (
            actual["positive_weight_node_count"]
            != expected["positive_weight_node_count"]
        ):
            raise ValueError(
                f"E-029 fine stage-6 {key} positive-weight cap drifted"
            )


def _run_interval(
    system: Any,
    full_source: np.ndarray,
    baseline_field: np.ndarray,
    configuration: AmgConfiguration,
    *,
    baseline_caps: dict[str, Any],
) -> tuple[np.ndarray, dict[str, Any]]:
    field = np.asarray(baseline_field, dtype=float).copy()
    stages: list[dict[str, Any]] = []
    status = "passed"
    for amplitude in TARGET_AMPLITUDES:
        field, stage = solve_cone_safe_stage(
            system,
            full_source,
            field,
            amplitude,
            configuration,
        )
        endpoint_tail = matched_tail_diagnostics(system, field, full_source)
        tail_gate = evaluate_tail_gate(endpoint_tail, baseline_caps)
        stage["endpoint_tail"] = endpoint_tail
        stage["tail_gate"] = tail_gate
        stages.append(stage)
        if not tail_gate["passes"]:
            status = "tail_conflict"
            break
    return field, {
        "status": status,
        "completed_amplitude": float(stages[-1]["amplitude"]) if stages else 0.5,
        "passes": bool(
            status == "passed"
            and len(stages) == len(TARGET_AMPLITUDES)
        ),
        "stages": stages,
        "output_field_sha256": _sha256_array(field),
    }


def _fresh_coarse_stage6(
    configuration: AmgConfiguration,
) -> tuple[Any, np.ndarray, np.ndarray, dict[str, Any]]:
    system = e025.build_system(AxisymmetricGrid(80.0, 0.25, 3))
    full_source, source_metadata = e025.smooth_annulus_source(system)
    full_linear = e025.solve_linear_reference(system, full_source)
    field = full_linear / 12.0
    reconstruction: list[dict[str, Any]] = []
    for stage_number in range(1, 7):
        field, stage = e028.solve_one_stage(
            system,
            full_source,
            field,
            stage_number / 12.0,
            configuration,
        )
        reconstruction.append(
            {
                "amplitude": stage["amplitude"],
                "newton_iterations": stage["nonlinear"]["newton_iterations"],
                "gmres_iterations": stage["nonlinear"][
                    "summed_gmres_inner_iterations"
                ],
                "relative_residual_l2": stage["nonlinear"][
                    "relative_residual_l2"
                ],
                "output_field_sha256": _sha256_array(field),
            }
        )
    return system, full_source, field, {
        "source_metadata": source_metadata,
        "reconstruction": reconstruction,
    }


def run_campaign(
    *,
    accepted_stage6_checkpoint: str | Path = ACCEPTED_STAGE6_CHECKPOINT,
    configuration: AmgConfiguration = AmgConfiguration(),
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Run the fine and fresh-coarse E-029 interval experiment."""

    configuration.validate()
    started = time.perf_counter()
    fine_system = e025.build_system(e028._canonical_grid())
    fine_source, fine_source_metadata = e025.smooth_annulus_source(
        fine_system
    )
    fine_input, _fine_linear, e028_report = _validate_accepted_stage6(
        Path(accepted_stage6_checkpoint),
        fine_system,
        fine_source,
        configuration,
    )
    fine_baseline_gamma = full_gamma_diagnostics(fine_system, fine_input)
    if not fine_baseline_gamma["passes"]:
        raise ValueError("E-029 fine stage-6 baseline fails a cone diagnostic")
    fine_baseline_tail = matched_tail_diagnostics(
        fine_system, fine_input, fine_source
    )
    _verify_fine_reference_caps(fine_baseline_tail)
    fine_caps = FINE_STAGE6_REFERENCE_CAPS
    fine_field, fine_interval = _run_interval(
        fine_system,
        fine_source,
        fine_input,
        configuration,
        baseline_caps=fine_caps,
    )

    coarse_system, coarse_source, coarse_input, coarse_preparation = (
        _fresh_coarse_stage6(configuration)
    )
    coarse_baseline_gamma = full_gamma_diagnostics(
        coarse_system, coarse_input
    )
    if not coarse_baseline_gamma["passes"]:
        raise ValueError("E-029 fresh coarse stage-6 baseline fails a cone gate")
    coarse_baseline_tail = matched_tail_diagnostics(
        coarse_system, coarse_input, coarse_source
    )
    coarse_caps = tail_caps_from_baseline(coarse_baseline_tail)
    coarse_field, coarse_interval = _run_interval(
        coarse_system,
        coarse_source,
        coarse_input,
        configuration,
        baseline_caps=coarse_caps,
    )

    path_and_tail_screen_passes = bool(
        fine_interval["passes"] and coarse_interval["passes"]
    )
    endpoint_tie_audit_complete = False
    overall_passes = bool(
        path_and_tail_screen_passes and endpoint_tie_audit_complete
    )
    report = {
        "epistemic_status": (
            "sampled discrete continuation of a hypothetical PDE; not a "
            "continuum theorem, detected field, useful artificial gravity, "
            "inertial control, spacetime engineering, FTL, or propulsion result"
        ),
        "focus_question": (
            "Can a new fingerprinted diagnostic-cone-safe dyadic source-step "
            "subdivision resolve E-028's blocked 6/12 -> 7/12 path and tail "
            "gates on fine and fresh coarse grids?"
        ),
        "runtime_provenance": e026.runtime_provenance(),
        "implementation_provenance": implementation_provenance(),
        "configuration": {
            "amg": e026.configuration_provenance(configuration),
            "targets": list(TARGET_AMPLITUDES),
            "segment_interior_samples": SEGMENT_INTERIOR_SAMPLES,
            "matched_difference_step": MATCHED_DIFFERENCE_STEP,
            "common_window_radius": COMMON_WINDOW_RADIUS,
        },
        "provenance": {
            "accepted_stage6_checkpoint": str(
                Path("models")
                / "checkpoints"
                / Path(accepted_stage6_checkpoint).name
            ),
            "accepted_stage6_checkpoint_sha256": (
                ACCEPTED_STAGE6_CHECKPOINT_SHA256
            ),
            "accepted_stage6_field_sha256": ACCEPTED_STAGE6_FIELD_SHA256,
            "canonical_failed_stage7_artifact_sha256": (
                CANONICAL_FAILED_STAGE7_ARTIFACT_SHA256
            ),
            "e028_input_implementation_provenance": e028_report[
                "implementation_provenance"
            ],
        },
        "fine": {
            "grid": {
                "radial_max": fine_system.grid.radial_max,
                "spacing": fine_system.grid.spacing,
                "directional_radius": fine_system.grid.directional_radius,
                "unknowns": fine_system.size,
            },
            "full_source_digest": e025._source_digest(fine_source),
            "source_metadata": fine_source_metadata,
            "stage6_baseline_gamma": fine_baseline_gamma,
            "stage6_baseline_tail": fine_baseline_tail,
            "predeclared_tail_caps": fine_caps,
            "interval": fine_interval,
        },
        "coarse": {
            "grid": {
                "radial_max": coarse_system.grid.radial_max,
                "spacing": coarse_system.grid.spacing,
                "directional_radius": coarse_system.grid.directional_radius,
                "unknowns": coarse_system.size,
            },
            "full_source_digest": e025._source_digest(coarse_source),
            "preparation": coarse_preparation,
            "stage6_baseline_gamma": coarse_baseline_gamma,
            "stage6_baseline_tail": coarse_baseline_tail,
            "predeclared_tail_caps": coarse_caps,
            "interval": coarse_interval,
        },
        "decision": {
            "passes": overall_passes,
            "path_and_tail_screen_passes": path_and_tail_screen_passes,
            "endpoint_tie_audit_complete": endpoint_tie_audit_complete,
            "accepted_amplitude": (
                14.0 / 24.0 if overall_passes else 6.0 / 12.0
            ),
            "status": (
                "stage7_reconsideration_gate_passed"
                if overall_passes
                else (
                    "pending_endpoint_tie_audit"
                    if path_and_tail_screen_passes
                    else "accepted_lineage_remains_stage6"
                )
            ),
            "rule": (
                "Both grids must pass every sampled cone path and both "
                "predeclared no-broadening endpoint tail thresholds, after "
                "which all genuine endpoint active-frame tie selections and "
                "the WCDD/M-matrix-pattern audit remain required. A failure or "
                "an incomplete later gate leaves accepted E-028 lineage at 6/12."
            ),
        },
        "resource_accounting": {
            "elapsed_seconds": time.perf_counter() - started,
            "peak_rss_bytes": e028.peak_rss_bytes(),
            "peak_rss_gib": e028.peak_rss_bytes() / 1024.0**3,
        },
        "fine_output_field_sha256": _sha256_array(fine_field),
        "coarse_output_field_sha256": _sha256_array(coarse_field),
        "limitations": [
            "Nine interior samples on each accepted correction segment are not an interval enclosure.",
            "Cone-safe Newton corrections do not prove a unique source-homotopy branch.",
            "The no-broadening tail cap is a predeclared discrete refinement diagnostic, not a physical stability theorem.",
            "Two coupled grids do not establish an asymptotic convergence order or transfer the Cartesian theorem to this cylindrical scheme.",
            "Endpoint active-frame tie enumeration and WCDD diagnostics are not implemented here; they remain mandatory if the earlier path/tail screen ever passes.",
            "No 8/12, outer-box, density, asymmetry, target, EFT, or engineering extension is authorized by this experiment.",
        ],
    }
    return fine_field, coarse_field, report


def artifact_report(
    report: dict[str, Any],
    role: str,
    field: np.ndarray,
) -> dict[str, Any]:
    """Bind one E-029 artifact report to its grid role and exact field."""

    if role not in {"fine", "coarse"}:
        raise ValueError("E-029 artifact role must be fine or coarse")
    field_sha256 = _sha256_array(field)
    expected = report.get(f"{role}_output_field_sha256")
    if expected != field_sha256:
        raise ValueError(
            f"E-029 {role} report and output field digests disagree"
        )
    bound = dict(report)
    bound["artifact_role"] = role
    bound["output_field_sha256"] = field_sha256
    return bound


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--accepted-stage6-checkpoint",
        type=Path,
        default=ACCEPTED_STAGE6_CHECKPOINT,
    )
    parser.add_argument("--fine-output-artifact", type=Path)
    parser.add_argument("--coarse-output-artifact", type=Path)
    parser.add_argument("--report-json", type=Path)
    parser.add_argument(
        "--preconditioner", choices=("pgsa",), default="pgsa"
    )
    args = parser.parse_args()
    configuration = AmgConfiguration(kind=args.preconditioner)
    fine, coarse, report = run_campaign(
        accepted_stage6_checkpoint=args.accepted_stage6_checkpoint,
        configuration=configuration,
    )
    if args.fine_output_artifact is not None:
        e026.save_campaign_artifact(
            args.fine_output_artifact,
            fine,
            artifact_report(report, "fine", fine),
        )
    if args.coarse_output_artifact is not None:
        e026.save_campaign_artifact(
            args.coarse_output_artifact,
            coarse,
            artifact_report(report, "coarse", coarse),
        )
    if args.report_json is not None:
        args.report_json.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(
        "E-029 "
        f"fine={report['fine']['interval']['status']} "
        f"coarse={report['coarse']['interval']['status']} "
        f"decision={report['decision']['status']} "
        f"elapsed={report['resource_accounting']['elapsed_seconds']:.2f}s"
    )


if __name__ == "__main__":
    main()

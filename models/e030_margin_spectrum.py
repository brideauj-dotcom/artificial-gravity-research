#!/usr/bin/env python3
"""E-030 tangent-predicted margin-spectrum diagnostic.

E-029 repaired the sampled Newton-corrector path from the immutable E-028
``6/12`` state to ``13/24``, but both the fine and fresh coarse grids failed
their independently frozen low-pair tail gates.  This module does not retry,
relax, or supersede that failure.  It asks a narrower diagnostic question:

* solve the active stage-6 tangent equation on each grid;
* predict where the matched-step pair-margin field crosses ``0.05`` and
  ``0.02`` along that tangent;
* replace sole reliance on hard cutoffs with source-volume-weighted margin
  and baseline-deficit quantile spectra;
* verify only ``49/96`` and ``25/48`` using E-029's unchanged nonlinear,
  Krylov, wide-stencil, full-cone, sampled-segment, and frozen-tail
  bookkeeping; and
* retain four-neighbour topology while keeping accepted lineage at ``6/12``.

The tangent is a local, active-frame linearization.  The quantile and topology
summaries are discrete diagnostics, not a convergence theorem.  No verified
state from this module is accepted, checkpointed, or promoted as evidence for
a physical field, artificial gravity, inertial control, spacetime
engineering, faster-than-light travel, or propulsion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import time
from typing import Any, Sequence

import numpy as np

import models.e025_axisymmetric_wide_2hessian as e025
import models.e026_nonsymmetric_amg as e026
import models.e028_fine_grid_campaign as e028
import models.e029_cone_safe_campaign as e029
from models.e026_nonsymmetric_amg import AmgConfiguration


BASELINE_AMPLITUDE = 6.0 / 12.0
PREDICTION_MAX_AMPLITUDE = 13.0 / 24.0
VERIFICATION_AMPLITUDES = (49.0 / 96.0, 25.0 / 48.0)
PREDICTION_SCAN_INTERVALS = 16
PREDICTION_BISECTION_ITERATIONS = 32
MONOTONICITY_ABSOLUTE_TOLERANCE = 1.0e-11
SPECTRUM_QUANTILES = (
    0.0,
    1.0e-4,
    1.0e-3,
    1.0e-2,
    0.1,
    0.5,
    0.9,
    0.99,
    1.0,
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def implementation_provenance() -> dict[str, Any]:
    """Fingerprint E-030 and every reused numerical implementation."""

    paths = {
        "e030_campaign": Path(__file__).resolve(),
        "e029_campaign": Path(e029.__file__).resolve(),
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
        "campaign": "E-030",
        "campaign_schema": 1,
        "strategy": {
            "accepted_baseline_amplitude": BASELINE_AMPLITUDE,
            "prediction_max_amplitude": PREDICTION_MAX_AMPLITUDE,
            "verification_amplitudes": list(VERIFICATION_AMPLITUDES),
            "prediction_scan_intervals": PREDICTION_SCAN_INTERVALS,
            "prediction_bisection_iterations": (
                PREDICTION_BISECTION_ITERATIONS
            ),
            "matched_difference_step": e029.MATCHED_DIFFERENCE_STEP,
            "common_window_radius": e029.COMMON_WINDOW_RADIUS,
            "tail_thresholds": list(e029.TAIL_THRESHOLDS),
            "spectrum_quantiles": list(SPECTRUM_QUANTILES),
            "lineage_policy": (
                "Both amplitudes are diagnostics only. No field produced by "
                "E-030 is an accepted checkpoint; accepted lineage remains "
                "the immutable E-028 6/12 state regardless of outcome."
            ),
        },
    }


def _matched_pair_values(
    system: Any,
    field: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    maximum_radius = min(
        e029.COMMON_WINDOW_RADIUS,
        system.grid.radial_max
        - 3.0
        * math.sqrt(2.0)
        * e029.MATCHED_DIFFERENCE_STEP,
    )
    eigenvalues, _rho, _z, global_nodes = e029._centered_eigenvalues(
        system,
        field,
        difference_step=e029.MATCHED_DIFFERENCE_STEP,
        maximum_radius=maximum_radius,
    )
    return eigenvalues[:, 0] + eigenvalues[:, 1], global_nodes


def _matched_affine_components(
    system: Any,
    baseline_field: np.ndarray,
    tangent_field: np.ndarray,
) -> dict[str, np.ndarray]:
    """Return matched centered Hessian components for ``base + da*tangent``."""

    maximum_radius = min(
        e029.COMMON_WINDOW_RADIUS,
        system.grid.radial_max
        - 3.0
        * math.sqrt(2.0)
        * e029.MATCHED_DIFFERENCE_STEP,
    )
    radius = np.hypot(system.rho, system.z)
    mask = radius <= maximum_radius + 1.0e-12
    rho = system.rho[mask]
    z = system.z[mask]

    def components(field: np.ndarray) -> tuple[np.ndarray, ...]:
        phi_r, _phi_z, radial, mixed, axial = (
            e025.interpolated_cylindrical_derivatives(
                system,
                field,
                rho,
                z,
                difference_step=e029.MATCHED_DIFFERENCE_STEP,
            )
        )
        azimuthal = np.divide(
            phi_r,
            rho,
            out=radial.copy(),
            where=rho > 0.5 * e029.MATCHED_DIFFERENCE_STEP,
        )
        return radial, mixed, axial, azimuthal

    base = components(np.asarray(baseline_field, dtype=float))
    tangent = components(np.asarray(tangent_field, dtype=float))
    return {
        "base_radial": base[0],
        "base_mixed": base[1],
        "base_axial": base[2],
        "base_azimuthal": base[3],
        "tangent_radial": tangent[0],
        "tangent_mixed": tangent[1],
        "tangent_axial": tangent[2],
        "tangent_azimuthal": tangent[3],
        "global_nodes": np.flatnonzero(mask),
    }


def _pair_from_affine_components(
    components: dict[str, np.ndarray],
    amplitude_delta: float | np.ndarray,
    shift: float,
    *,
    indices: np.ndarray | None = None,
) -> np.ndarray:
    selected: slice | np.ndarray = slice(None) if indices is None else indices
    delta = np.asarray(amplitude_delta, dtype=float)
    radial = (
        components["base_radial"][selected]
        + delta * components["tangent_radial"][selected]
    )
    mixed = (
        components["base_mixed"][selected]
        + delta * components["tangent_mixed"][selected]
    )
    axial = (
        components["base_axial"][selected]
        + delta * components["tangent_axial"][selected]
    )
    azimuthal = (
        components["base_azimuthal"][selected]
        + delta * components["tangent_azimuthal"][selected]
    )
    eigenvalues = e029._eigenvalues_from_components(
        radial,
        mixed,
        axial,
        azimuthal,
        shift,
    )
    return eigenvalues[:, 0] + eigenvalues[:, 1]


def _weighted_quantiles(
    values: np.ndarray,
    weights: np.ndarray,
    quantiles: Sequence[float] = SPECTRUM_QUANTILES,
) -> dict[str, float]:
    data = np.asarray(values, dtype=float)
    mass = np.asarray(weights, dtype=float)
    if data.shape != mass.shape:
        raise ValueError("weighted-quantile values and weights must match")
    if np.any(~np.isfinite(data)) or np.any(~np.isfinite(mass)):
        raise ValueError("weighted-quantile inputs must be finite")
    if np.any(mass < 0.0):
        raise ValueError("weighted-quantile weights must be nonnegative")
    keep = mass > 0.0
    if not np.any(keep):
        raise ValueError("weighted-quantile inputs need positive weight")
    data = data[keep]
    mass = mass[keep]
    order = np.argsort(data, kind="stable")
    data = data[order]
    mass = mass[order]
    cumulative = np.cumsum(mass)
    total = float(cumulative[-1])
    result: dict[str, float] = {}
    for raw_quantile in quantiles:
        quantile = float(raw_quantile)
        if not 0.0 <= quantile <= 1.0:
            raise ValueError("weighted quantiles must lie in [0, 1]")
        target = quantile * total
        index = int(np.searchsorted(cumulative, target, side="left"))
        index = min(index, data.size - 1)
        result[f"{quantile:.6g}"] = float(data[index])
    return result


def margin_deficit_spectrum(
    system: Any,
    baseline_field: np.ndarray,
    current_field: np.ndarray,
    full_source: np.ndarray,
) -> dict[str, Any]:
    """Summarize the matched margin distribution without a margin cutoff."""

    baseline, baseline_nodes = _matched_pair_values(system, baseline_field)
    current, current_nodes = _matched_pair_values(system, current_field)
    if not np.array_equal(baseline_nodes, current_nodes):
        raise ValueError("matched pair evaluations use different node sets")
    all_weights = e025.nodal_volume_weights(system)
    weights = all_weights[baseline_nodes]
    source = np.asarray(full_source, dtype=float)
    source_values = source[baseline_nodes]
    source_support = source_values > 0.0
    use = source_support & (weights > 0.0)
    if not np.any(use):
        raise ValueError("margin spectrum has no positive source weight")
    baseline_support = baseline[use]
    current_support = current[use]
    signed_change = current_support - baseline_support
    positive_deficit = np.maximum(-signed_change, 0.0)

    def weighted_summary(spectrum_weights: np.ndarray) -> dict[str, Any]:
        total_weight = float(np.sum(spectrum_weights))
        mean_deficit = float(
            np.sum(spectrum_weights * positive_deficit) / total_weight
        )
        rms_deficit = float(
            np.sqrt(
                np.sum(spectrum_weights * positive_deficit**2)
                / total_weight
            )
        )
        mean_baseline = float(
            np.sum(spectrum_weights * baseline_support) / total_weight
        )
        return {
            "total_weight": total_weight,
            "weighted_mean_baseline_margin": mean_baseline,
            "weighted_mean_current_margin": float(
                np.sum(spectrum_weights * current_support) / total_weight
            ),
            "weighted_mean_signed_change": float(
                np.sum(spectrum_weights * signed_change) / total_weight
            ),
            "weighted_mean_positive_deficit": mean_deficit,
            "weighted_rms_positive_deficit": rms_deficit,
            "weighted_relative_mean_positive_deficit": (
                mean_deficit / mean_baseline
                if mean_baseline != 0.0
                else math.inf
            ),
            "weight_fraction_with_decreased_margin": float(
                np.sum(spectrum_weights[signed_change < 0.0])
                / total_weight
            ),
            "baseline_margin_quantiles": _weighted_quantiles(
                baseline_support, spectrum_weights
            ),
            "current_margin_quantiles": _weighted_quantiles(
                current_support, spectrum_weights
            ),
            "positive_deficit_quantiles": _weighted_quantiles(
                positive_deficit, spectrum_weights
            ),
        }

    support_volume_weights = weights[use]
    source_charge_weights = support_volume_weights * source_values[use]
    return {
        "definition": (
            "Empirical quantiles of matched pair margin and of "
            "max(stage6_margin-current_margin,0), reported both with E-029's "
            "source-support cylindrical-volume weights and with true sampled "
            "source-charge weights w*S. Neither spectrum uses the 0.02 or "
            "0.05 cutoff."
        ),
        "evaluated_source_nodes": int(np.count_nonzero(use)),
        "spectra": {
            "source_support_volume": weighted_summary(
                support_volume_weights
            ),
            "source_charge": weighted_summary(source_charge_weights),
        },
    }


def prediction_error_spectrum(
    system: Any,
    predicted_field: np.ndarray,
    actual_field: np.ndarray,
    full_source: np.ndarray,
) -> dict[str, Any]:
    predicted, predicted_nodes = _matched_pair_values(system, predicted_field)
    actual, actual_nodes = _matched_pair_values(system, actual_field)
    if not np.array_equal(predicted_nodes, actual_nodes):
        raise ValueError("prediction comparison uses different node sets")
    weights = e025.nodal_volume_weights(system)[predicted_nodes]
    support = np.asarray(full_source)[predicted_nodes] > 0.0
    use = support & (weights > 0.0)
    error = actual[use] - predicted[use]
    absolute_error = np.abs(error)
    used_weights = weights[use]
    total_weight = float(np.sum(used_weights))
    return {
        "weighted_mean_error": float(
            np.sum(used_weights * error) / total_weight
        ),
        "weighted_mean_absolute_error": float(
            np.sum(used_weights * absolute_error) / total_weight
        ),
        "weighted_rms_error": float(
            np.sqrt(np.sum(used_weights * error**2) / total_weight)
        ),
        "absolute_error_quantiles": _weighted_quantiles(
            absolute_error, used_weights
        ),
        "signed_error_quantiles": _weighted_quantiles(error, used_weights),
    }


def solve_stage6_tangent(
    system: Any,
    full_source: np.ndarray,
    stage6_field: np.ndarray,
    configuration: AmgConfiguration,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Solve ``J dphi/da = full_source/(2*c3)`` at stage 6."""

    configuration.validate()
    source = np.asarray(full_source, dtype=float)
    field = np.asarray(stage6_field, dtype=float)
    if source.shape != (system.size,) or field.shape != (system.size,):
        raise ValueError("stage-6 tangent arrays do not match the system")
    operator, active, curvatures = e025.monotone_operator(system, field)
    stage6_source = BASELINE_AMPLITUDE * source
    nonlinear_residual = operator - e025.shifted_rhs(
        stage6_source, system.cubic_coefficient
    )
    stage_scale = max(
        float(np.linalg.norm(stage6_source))
        / (2.0 * system.cubic_coefficient),
        np.finfo(float).tiny,
    )
    active_gradient = e025.monotone_sigma_gradient(
        curvatures[active, np.arange(system.size)]
    )
    jacobian = e025.active_jacobian_matrix(system, active, active_gradient)
    tangent_rhs = source / (2.0 * system.cubic_coefficient)
    # _solve_linear_corrector_strict solves (-J)x=rhs.  The tangent equation
    # J*dphi/da=tangent_rhs therefore requires rhs=-tangent_rhs.
    tangent, linear = e028._solve_linear_corrector_strict(
        jacobian,
        -tangent_rhs,
        system,
        configuration,
    )
    direct_ratio = float(
        np.linalg.norm(jacobian @ tangent - tangent_rhs)
        / np.linalg.norm(tangent_rhs)
    )
    if (
        not linear["passes_strict_krylov_gate"]
        or direct_ratio >= configuration.gmres_relative_tolerance
    ):
        raise RuntimeError(
            "E-030 stage-6 tangent failed the strict direct residual gate"
        )
    return tangent, {
        "equation": "J*dphi_da = full_source/(2*cubic_coefficient)",
        "active_frame_sha256": e029._sha256_array(
            np.asarray(active, dtype=np.int64)
        ),
        "stage6_nonlinear_relative_l2": float(
            np.linalg.norm(nonlinear_residual) / stage_scale
        ),
        "linear": linear,
        "direct_tangent_residual_ratio": direct_ratio,
        "tangent_field_sha256": e029._sha256_array(tangent),
        "tangent_relative_l2_per_unit_amplitude": float(
            np.linalg.norm(tangent)
            / max(np.linalg.norm(field), np.finfo(float).tiny)
        ),
    }


def _crossing_summary(
    system: Any,
    full_source: np.ndarray,
    global_nodes: np.ndarray,
    crossing_amplitudes: np.ndarray,
    threshold: float,
) -> dict[str, Any]:
    all_weights = e025.nodal_volume_weights(system)
    weights = all_weights[global_nodes]
    source = np.asarray(full_source, dtype=float)
    support = source[global_nodes] > 0.0
    support_weight = float(np.sum(weights[support]))
    preexisting = np.isclose(
        crossing_amplitudes,
        BASELINE_AMPLITUDE,
        rtol=0.0,
        atol=np.finfo(float).eps,
    )
    new = np.isfinite(crossing_amplitudes) & ~preexisting
    new_support = new & support & (weights > 0.0)
    result: dict[str, Any] = {
        "threshold": threshold,
        "preexisting_node_count": int(np.count_nonzero(preexisting)),
        "new_crossing_node_count": int(np.count_nonzero(new)),
        "new_source_support_crossing_node_count": int(
            np.count_nonzero(new_support)
        ),
        "new_source_support_crossing_weight_fraction": (
            float(np.sum(weights[new & support])) / support_weight
            if support_weight > 0.0
            else 0.0
        ),
    }
    if np.any(new):
        earliest_local = int(
            np.nanargmin(np.where(new, crossing_amplitudes, np.nan))
        )
        earliest_global = int(global_nodes[earliest_local])
        result["earliest_new_crossing"] = {
            "amplitude": float(crossing_amplitudes[earliest_local]),
            "rho": float(system.rho[earliest_global]),
            "z": float(system.z[earliest_global]),
        }
    else:
        result["earliest_new_crossing"] = None
    if np.any(new_support):
        result["new_source_support_crossing_amplitude_quantiles"] = (
            _weighted_quantiles(
                crossing_amplitudes[new_support],
                weights[new_support],
            )
        )
    else:
        result["new_source_support_crossing_amplitude_quantiles"] = {}
    cumulative: dict[str, Any] = {}
    for amplitude in (*VERIFICATION_AMPLITUDES, PREDICTION_MAX_AMPLITUDE):
        reached = new & (crossing_amplitudes <= amplitude)
        cumulative[f"{amplitude:.12g}"] = {
            "amplitude": amplitude,
            "node_count": int(np.count_nonzero(reached)),
            "source_support_weight_fraction": (
                float(np.sum(weights[reached & support])) / support_weight
                if support_weight > 0.0
                else 0.0
            ),
        }
    result["cumulative_new_crossings"] = cumulative
    return result


def tangent_crossing_spectrum(
    system: Any,
    full_source: np.ndarray,
    stage6_field: np.ndarray,
    tangent_field: np.ndarray,
) -> dict[str, Any]:
    """Predict first hard-threshold crossings along the stage-6 tangent."""

    components = _matched_affine_components(
        system, stage6_field, tangent_field
    )
    global_nodes = components["global_nodes"]
    probe_amplitudes = np.linspace(
        BASELINE_AMPLITUDE,
        PREDICTION_MAX_AMPLITUDE,
        PREDICTION_SCAN_INTERVALS + 1,
    )
    previous = _pair_from_affine_components(
        components, 0.0, system.shift
    )
    baseline_pair = previous.copy()
    crossings = {
        threshold: np.full(previous.shape, np.nan, dtype=float)
        for threshold in e029.TAIL_THRESHOLDS
    }
    for threshold in e029.TAIL_THRESHOLDS:
        crossings[threshold][baseline_pair < threshold] = BASELINE_AMPLITUDE
    any_increase = np.zeros(previous.shape, dtype=bool)

    for lower_amplitude, upper_amplitude in zip(
        probe_amplitudes[:-1], probe_amplitudes[1:]
    ):
        current = _pair_from_affine_components(
            components,
            upper_amplitude - BASELINE_AMPLITUDE,
            system.shift,
        )
        any_increase |= (
            current - previous > MONOTONICITY_ABSOLUTE_TOLERANCE
        )
        for threshold in e029.TAIL_THRESHOLDS:
            crossing = crossings[threshold]
            candidates = np.flatnonzero(
                ~np.isfinite(crossing)
                & (previous >= threshold)
                & (current < threshold)
            )
            if candidates.size == 0:
                continue
            low = np.full(candidates.size, lower_amplitude, dtype=float)
            high = np.full(candidates.size, upper_amplitude, dtype=float)
            for _ in range(PREDICTION_BISECTION_ITERATIONS):
                middle = 0.5 * (low + high)
                middle_pair = _pair_from_affine_components(
                    components,
                    middle - BASELINE_AMPLITUDE,
                    system.shift,
                    indices=candidates,
                )
                below = middle_pair < threshold
                high[below] = middle[below]
                low[~below] = middle[~below]
            crossing[candidates] = high
        previous = current

    threshold_summaries = {
        f"{threshold:.2f}": _crossing_summary(
            system,
            full_source,
            global_nodes,
            crossings[threshold],
            threshold,
        )
        for threshold in e029.TAIL_THRESHOLDS
    }
    predicted_endpoints: dict[str, Any] = {}
    for amplitude in (*VERIFICATION_AMPLITUDES, PREDICTION_MAX_AMPLITUDE):
        predicted_field = np.asarray(stage6_field) + (
            amplitude - BASELINE_AMPLITUDE
        ) * np.asarray(tangent_field)
        predicted_endpoints[f"{amplitude:.12g}"] = {
            "amplitude": amplitude,
            "field_sha256": e029._sha256_array(predicted_field),
            "tail": e029.matched_tail_diagnostics(
                system, predicted_field, full_source
            ),
            "deficit_spectrum": margin_deficit_spectrum(
                system,
                stage6_field,
                predicted_field,
                full_source,
            ),
        }
    return {
        "model": (
            "phi_predicted(a)=phi_stage6+(a-1/2)*dphi_da, with dphi_da "
            "from the active stage-6 tangent equation"
        ),
        "scan_amplitudes": [float(item) for item in probe_amplitudes],
        "nodes_with_any_sampled_margin_increase": int(
            np.count_nonzero(any_increase)
        ),
        "threshold_crossings": threshold_summaries,
        "predicted_endpoints": predicted_endpoints,
    }


def _run_verifications(
    system: Any,
    full_source: np.ndarray,
    stage6_field: np.ndarray,
    tangent_field: np.ndarray,
    baseline_caps: dict[str, Any],
    configuration: AmgConfiguration,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    field = np.asarray(stage6_field, dtype=float).copy()
    rows: list[dict[str, Any]] = []
    for amplitude in VERIFICATION_AMPLITUDES:
        field, stage = e029.solve_cone_safe_stage(
            system,
            full_source,
            field,
            amplitude,
            configuration,
        )
        tail = e029.matched_tail_diagnostics(system, field, full_source)
        predicted_field = np.asarray(stage6_field) + (
            amplitude - BASELINE_AMPLITUDE
        ) * np.asarray(tangent_field)
        stage["diagnostic_role"] = (
            "verified_unaccepted_e030_endpoint"
        )
        stage["endpoint_tail"] = tail
        stage["frozen_tail_gate"] = e029.evaluate_tail_gate(
            tail, baseline_caps
        )
        stage["deficit_spectrum"] = margin_deficit_spectrum(
            system, stage6_field, field, full_source
        )
        stage["tangent_prediction"] = {
            "predicted_field_sha256": e029._sha256_array(predicted_field),
            "predicted_tail": e029.matched_tail_diagnostics(
                system, predicted_field, full_source
            ),
            "predicted_deficit_spectrum": margin_deficit_spectrum(
                system, stage6_field, predicted_field, full_source
            ),
            "error_spectrum": prediction_error_spectrum(
                system, predicted_field, field, full_source
            ),
        }
        rows.append(stage)
    return field, rows


def _grid_report(
    system: Any,
    full_source: np.ndarray,
    stage6_field: np.ndarray,
    baseline_caps: dict[str, Any],
    configuration: AmgConfiguration,
) -> tuple[np.ndarray, dict[str, Any]]:
    baseline_gamma = e029.full_gamma_diagnostics(system, stage6_field)
    baseline_tail = e029.matched_tail_diagnostics(
        system, stage6_field, full_source
    )
    if not baseline_gamma["passes"]:
        raise ValueError("E-030 stage-6 baseline fails a full-cone diagnostic")
    if not e029.evaluate_tail_gate(baseline_tail, baseline_caps)["passes"]:
        raise ValueError("E-030 stage-6 baseline does not reproduce frozen caps")
    tangent, tangent_report = solve_stage6_tangent(
        system, full_source, stage6_field, configuration
    )
    prediction = tangent_crossing_spectrum(
        system, full_source, stage6_field, tangent
    )
    final_field, verifications = _run_verifications(
        system,
        full_source,
        stage6_field,
        tangent,
        baseline_caps,
        configuration,
    )
    return final_field, {
        "grid": {
            "radial_max": system.grid.radial_max,
            "spacing": system.grid.spacing,
            "directional_radius": system.grid.directional_radius,
            "unknowns": system.size,
        },
        "full_source_digest": e025._source_digest(full_source),
        "stage6_field_sha256": e029._sha256_array(stage6_field),
        "stage6_baseline_gamma": baseline_gamma,
        "stage6_baseline_tail": baseline_tail,
        "frozen_stage6_tail_caps": baseline_caps,
        "stage6_tangent": tangent_report,
        "prediction": prediction,
        "verifications": verifications,
        "final_diagnostic_field_sha256": e029._sha256_array(final_field),
    }


def run_campaign(
    *,
    accepted_stage6_checkpoint: str | Path = (
        e029.ACCEPTED_STAGE6_CHECKPOINT
    ),
    configuration: AmgConfiguration = AmgConfiguration(),
) -> dict[str, Any]:
    """Run the bounded fine/coarse E-030 diagnostic campaign."""

    configuration.validate()
    started = time.perf_counter()
    fine_system = e025.build_system(e028._canonical_grid())
    fine_source, fine_source_metadata = e025.smooth_annulus_source(
        fine_system
    )
    fine_stage6, _fine_linear, e028_report = (
        e029._validate_accepted_stage6(
            Path(accepted_stage6_checkpoint),
            fine_system,
            fine_source,
            configuration,
        )
    )
    fine_baseline_tail = e029.matched_tail_diagnostics(
        fine_system, fine_stage6, fine_source
    )
    e029._verify_fine_reference_caps(fine_baseline_tail)
    _fine_final, fine_report = _grid_report(
        fine_system,
        fine_source,
        fine_stage6,
        e029.FINE_STAGE6_REFERENCE_CAPS,
        configuration,
    )
    fine_report["source_metadata"] = fine_source_metadata

    coarse_system, coarse_source, coarse_stage6, coarse_preparation = (
        e029._fresh_coarse_stage6(configuration)
    )
    coarse_baseline_tail = e029.matched_tail_diagnostics(
        coarse_system, coarse_stage6, coarse_source
    )
    coarse_caps = e029.tail_caps_from_baseline(coarse_baseline_tail)
    _coarse_final, coarse_report = _grid_report(
        coarse_system,
        coarse_source,
        coarse_stage6,
        coarse_caps,
        configuration,
    )
    coarse_report["preparation"] = coarse_preparation

    report = {
        "epistemic_status": (
            "local tangent and two-grid discrete diagnostics for a "
            "hypothetical PDE; not a continuum theorem, detected physical "
            "field, useful artificial gravity, inertial control, spacetime "
            "engineering, FTL, or propulsion result"
        ),
        "focus_question": (
            "Does the E-029 hard-threshold tail jump overlay a smooth "
            "source-weighted margin erosion, and is that erosion consistent "
            "between the fine and fresh coarse grids before 13/24?"
        ),
        "runtime_provenance": e026.runtime_provenance(),
        "implementation_provenance": implementation_provenance(),
        "configuration": {
            "amg": e026.configuration_provenance(configuration),
            "accepted_baseline_amplitude": BASELINE_AMPLITUDE,
            "verification_amplitudes": list(VERIFICATION_AMPLITUDES),
        },
        "provenance": {
            "accepted_stage6_checkpoint": str(
                Path("models")
                / "checkpoints"
                / Path(accepted_stage6_checkpoint).name
            ),
            "accepted_stage6_checkpoint_sha256": (
                e029.ACCEPTED_STAGE6_CHECKPOINT_SHA256
            ),
            "accepted_stage6_field_sha256": (
                e029.ACCEPTED_STAGE6_FIELD_SHA256
            ),
            "e028_input_implementation_provenance": e028_report[
                "implementation_provenance"
            ],
        },
        "fine": fine_report,
        "coarse": coarse_report,
        "decision": {
            "diagnostic_completed": True,
            "accepted_amplitude": BASELINE_AMPLITUDE,
            "accepted_lineage_changed": False,
            "artifacts_written_by_campaign": False,
            "status": "diagnostic_only_accepted_lineage_remains_stage6",
            "rule": (
                "E-030 may verify exactly 49/96 and 25/48, but neither field "
                "can pass or relax E-029's failed gate or alter accepted "
                "lineage. The two thresholded tails, threshold-free spectra, "
                "tangent error, and four-neighbour topology must be "
                "interpreted together."
            ),
        },
        "limitations": [
            "The tangent freezes the stage-6 active generalized Jacobian and is only a local predictor.",
            "Finite sampled Newton segments are not interval continuation or a no-branch-jump certificate.",
            "Weighted quantiles reduce hard-threshold brittleness but do not prove mesh convergence.",
            "Four-neighbour component counts on two different grids lack a common-space sup-norm or persistence-stability certificate.",
            "Two coupled grids do not establish an asymptotic order or transfer a Cartesian convergence theorem to the reflected cylindrical operator.",
            "No diagnostic endpoint is retained as an accepted or work checkpoint.",
            "No 7/12, 8/12, outer-box, density, asymmetry, target, EFT, or engineering extension is authorized.",
        ],
        "resource_accounting": {
            "elapsed_seconds": time.perf_counter() - started,
            "peak_rss_bytes": e028.peak_rss_bytes(),
            "peak_rss_gib": e028.peak_rss_bytes() / 1024.0**3,
        },
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--accepted-stage6-checkpoint",
        type=Path,
        default=e029.ACCEPTED_STAGE6_CHECKPOINT,
    )
    parser.add_argument("--report-json", type=Path)
    parser.add_argument(
        "--preconditioner", choices=("pgsa",), default="pgsa"
    )
    args = parser.parse_args()
    report = run_campaign(
        accepted_stage6_checkpoint=args.accepted_stage6_checkpoint,
        configuration=AmgConfiguration(kind=args.preconditioner),
    )
    if args.report_json is not None:
        args.report_json.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    fine_rows = report["fine"]["verifications"]
    coarse_rows = report["coarse"]["verifications"]
    print(
        "E-030 "
        f"fine={[row['amplitude'] for row in fine_rows]} "
        f"coarse={[row['amplitude'] for row in coarse_rows]} "
        f"decision={report['decision']['status']} "
        f"elapsed={report['resource_accounting']['elapsed_seconds']:.2f}s"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""E-032 matched-Hessian discrepancy decomposition.

E-031 placed the fine and coarse matched pair-margin fields on one exact
common-node graph.  Its sup discrepancy was about ``0.12`` at
``(rho, z) = (8.75, 0.75)``, much larger than the detached coarse
zero-dimensional persistence lifetime.  This module keeps the same transient
``49/96`` and ``25/48`` endpoints and asks which reconstructed Hessian
component and physical difference step create that discrepancy.

At the canonical physical step ``0.25``, the module:

* reproduces the full common-window pair-margin sup discrepancy;
* records radial, mixed, axial, and azimuthal Hessian differences;
* uses ``pair = trace(H) - lambda_max(H) + 2*shift`` to separate a
  direct trace response from the exact spectral-selection response;
* supplies an exact, order-neutral four-component Shapley attribution as an
  attribution-sensitivity cross-check; and
* checks Weyl/Hoffman-Wielandt-style spectral perturbation bounds.

Only the E-031 hotspot and its three-node detached-lobe basin are repeated at
the predeclared mesh-compatible common physical steps ``0.25`` and ``0.5``.
Both steps are integer multiples of the fine and coarse spacings.  The
``0.125`` fine-native step is deliberately excluded because it is sub-cell on
the coarse grid and would measure bilinear-interpolation amplification rather
than a like-for-like Hessian reconstruction.

No endpoint from this module is accepted, checkpointed, or promoted as
evidence for a continuum solution, a physical field, artificial gravity,
inertial control, spacetime engineering, faster-than-light travel, or
propulsion.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import time
from typing import Any

import numpy as np

import models.e025_axisymmetric_wide_2hessian as e025
import models.e026_nonsymmetric_amg as e026
import models.e028_fine_grid_campaign as e028
import models.e029_cone_safe_campaign as e029
import models.e030_margin_spectrum as e030
import models.e031_common_space_persistence as e031
from models.e026_nonsymmetric_amg import AmgConfiguration


BASELINE_AMPLITUDE = e031.BASELINE_AMPLITUDE
VERIFICATION_AMPLITUDES = e031.VERIFICATION_AMPLITUDES
CANONICAL_DIFFERENCE_STEP = e029.MATCHED_DIFFERENCE_STEP
RECONSTRUCTION_STEPS = (0.25, 0.5)
HOTSPOT = (8.75, 0.75)
LOBE_BASIN = ((5.75, 0.5), (6.0, 0.5), (6.25, 0.5))
ROI_POINTS = (HOTSPOT,) + LOBE_BASIN
COMPONENT_NAMES = ("radial", "mixed", "axial", "azimuthal")
DECOMPOSITION_ABSOLUTE_TOLERANCE = 5.0e-13


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def implementation_provenance() -> dict[str, Any]:
    """Fingerprint E-032 and every reused numerical implementation."""

    paths = {
        "e032_campaign": Path(__file__).resolve(),
        "e031_campaign": Path(e031.__file__).resolve(),
        "e030_campaign": Path(e030.__file__).resolve(),
        "e029_campaign": Path(e029.__file__).resolve(),
        "e028_campaign": Path(e028.__file__).resolve(),
        "e025_operator": Path(e025.__file__).resolve(),
        "e026_amg": Path(e026.__file__).resolve(),
        "research_requirements": (
            Path(__file__).resolve().parents[1]
            / "requirements-research.txt"
        ),
    }
    repository_root = Path(__file__).resolve().parents[1]
    return {
        "campaign": "E-032",
        "campaign_schema": 1,
        "modules": {
            name: {
                "path": str(path.relative_to(repository_root)),
                "sha256": _sha256_file(path),
            }
            for name, path in paths.items()
        },
        "strategy": {
            "accepted_baseline_amplitude": BASELINE_AMPLITUDE,
            "verification_amplitudes": list(VERIFICATION_AMPLITUDES),
            "canonical_difference_step": CANONICAL_DIFFERENCE_STEP,
            "reconstruction_steps": list(RECONSTRUCTION_STEPS),
            "hotspot": list(HOTSPOT),
            "lobe_basin": [list(point) for point in LOBE_BASIN],
            "first_order_attribution": (
                "pair=trace-lambda_max+2shift, linearized at the coarse "
                "top eigenvector; the exact closure residual is retained "
                "only as a local linearization diagnostic"
            ),
            "order_neutral_attribution": (
                "exact four-component Shapley average over all 24 replacement "
                "orders from the coarse to the fine Hessian"
            ),
            "lineage_policy": (
                "All E-032 roots are transient diagnostics. Accepted lineage "
                "remains the immutable E-028 6/12 checkpoint."
            ),
        },
    }


def _matrix_from_components(components: np.ndarray) -> np.ndarray:
    """Build the axisymmetric Cartesian-frame Hessian matrices."""

    values = np.asarray(components, dtype=float)
    if values.shape[-1] != len(COMPONENT_NAMES):
        raise ValueError("components must end in radial,mixed,axial,azimuthal")
    matrices = np.zeros(values.shape[:-1] + (3, 3), dtype=float)
    matrices[..., 0, 0] = values[..., 0]
    matrices[..., 0, 1] = values[..., 1]
    matrices[..., 1, 0] = values[..., 1]
    matrices[..., 1, 1] = values[..., 2]
    matrices[..., 2, 2] = values[..., 3]
    return matrices


def _shifted_eigenvalues_and_pair(
    components: np.ndarray,
    shift: float,
) -> tuple[np.ndarray, np.ndarray]:
    matrices = _matrix_from_components(components)
    eigenvalues = np.linalg.eigvalsh(matrices) + float(shift)
    pair = eigenvalues[..., 0] + eigenvalues[..., 1]
    return eigenvalues, pair


def _component_bundle(
    system: Any,
    field: np.ndarray,
    coordinates: np.ndarray,
    *,
    difference_step: float,
) -> dict[str, np.ndarray]:
    """Evaluate one centered cylindrical Hessian reconstruction."""

    points = np.asarray(coordinates, dtype=float)
    if points.ndim != 2 or points.shape[1] != 2:
        raise ValueError("coordinates must have shape (point, 2)")
    rho = points[:, 0]
    z = points[:, 1]
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
        out=np.asarray(radial, dtype=float).copy(),
        where=rho > 0.5 * difference_step,
    )
    components = np.column_stack((radial, mixed, axial, azimuthal))
    eigenvalues, pair = _shifted_eigenvalues_and_pair(
        components,
        system.shift,
    )
    return {
        "components": components,
        "matrices": _matrix_from_components(components),
        "eigenvalues": eigenvalues,
        "pair": pair,
    }


def _pair_for_component_vector(
    components: np.ndarray,
    shift: float,
) -> float:
    _eigenvalues, pair = _shifted_eigenvalues_and_pair(
        np.asarray(components, dtype=float),
        shift,
    )
    return float(pair)


def _shapley_pair_attribution(
    coarse_components: np.ndarray,
    fine_components: np.ndarray,
    shift: float,
) -> dict[str, Any]:
    """Return an exact order-neutral attribution of the pair difference."""

    coarse = np.asarray(coarse_components, dtype=float)
    fine = np.asarray(fine_components, dtype=float)
    if coarse.shape != (4,) or fine.shape != (4,):
        raise ValueError("Shapley attribution requires two four-vectors")
    totals = np.zeros(4, dtype=float)
    marginals: list[list[float]] = [[] for _ in range(4)]
    permutations = tuple(itertools.permutations(range(4)))
    for order in permutations:
        state = coarse.copy()
        previous = _pair_for_component_vector(state, shift)
        for component in order:
            state[component] = fine[component]
            current = _pair_for_component_vector(state, shift)
            marginal = current - previous
            totals[component] += marginal
            marginals[component].append(marginal)
            previous = current
    attribution = totals / len(permutations)
    actual = _pair_for_component_vector(fine, shift) - (
        _pair_for_component_vector(coarse, shift)
    )
    closure_error = float(np.sum(attribution) - actual)
    if not math.isclose(
        closure_error,
        0.0,
        rel_tol=0.0,
        abs_tol=DECOMPOSITION_ABSOLUTE_TOLERANCE,
    ):
        raise RuntimeError("Shapley pair attribution failed exact closure")
    contribution_map = {
        name: float(value)
        for name, value in zip(COMPONENT_NAMES, attribution, strict=True)
    }
    absolute_sum = float(np.sum(np.abs(attribution)))
    return {
        "component_contributions": contribution_map,
        "coalition_marginal_envelopes": {
            name: {
                "minimum": float(np.min(values)),
                "maximum": float(np.max(values)),
                "distinct_coalition_marginal_count": int(
                    np.unique(np.asarray(values)).size
                ),
                "distinct_coalition_marginals": [
                    float(value)
                    for value in np.unique(np.asarray(values))
                ],
            }
            for name, values in zip(
                COMPONENT_NAMES,
                marginals,
                strict=True,
            )
        },
        "sum": float(np.sum(attribution)),
        "actual_pair_difference": actual,
        "sum_absolute_component_contributions": absolute_sum,
        "net_to_absolute_contribution_ratio": (
            abs(actual) / absolute_sum if absolute_sum > 0.0 else 1.0
        ),
        "closure_error": closure_error,
        "replacement_order_count": len(permutations),
        "interpretation": (
            "Exact order-neutral attribution of this finite coarse-to-fine "
            "component replacement; it is not a causal error decomposition."
        ),
    }


def _spectral_pair_decomposition(
    coarse_components: np.ndarray,
    fine_components: np.ndarray,
    shift: float,
) -> dict[str, Any]:
    """Decompose ``fine pair - coarse pair`` with an exact closure term."""

    coarse = np.asarray(coarse_components, dtype=float)
    fine = np.asarray(fine_components, dtype=float)
    coarse_matrix = _matrix_from_components(coarse)
    fine_matrix = _matrix_from_components(fine)
    delta_matrix = fine_matrix - coarse_matrix
    coarse_raw, coarse_vectors = np.linalg.eigh(coarse_matrix)
    fine_raw, fine_vectors = np.linalg.eigh(fine_matrix)
    coarse_eigenvalues = coarse_raw + float(shift)
    fine_eigenvalues = fine_raw + float(shift)
    coarse_pair = float(np.sum(coarse_eigenvalues[:2]))
    fine_pair = float(np.sum(fine_eigenvalues[:2]))
    pair_difference = fine_pair - coarse_pair

    top_vector = coarse_vectors[:, -1]
    component_delta = fine - coarse
    radial, mixed, axial, azimuthal = component_delta
    first_order = np.array(
        (
            radial * (1.0 - top_vector[0] ** 2),
            -2.0 * mixed * top_vector[0] * top_vector[1],
            axial * (1.0 - top_vector[1] ** 2),
            azimuthal * (1.0 - top_vector[2] ** 2),
        ),
        dtype=float,
    )
    first_order_sum = float(np.sum(first_order))
    linearization_remainder = pair_difference - first_order_sum
    closure_error = (
        first_order_sum + linearization_remainder - pair_difference
    )
    if not math.isclose(
        closure_error,
        0.0,
        rel_tol=0.0,
        abs_tol=DECOMPOSITION_ABSOLUTE_TOLERANCE,
    ):
        raise RuntimeError("spectral pair decomposition failed exact closure")

    spectral_norm = float(np.linalg.norm(delta_matrix, ord=2))
    frobenius_norm = float(np.linalg.norm(delta_matrix, ord="fro"))
    eigenvalue_delta = fine_raw - coarse_raw
    eigenvalue_delta_l2 = float(np.linalg.norm(eigenvalue_delta))
    twice_spectral_bound = 2.0 * spectral_norm
    coarse_meridional = np.linalg.eigvalsh(coarse_matrix[:2, :2])
    fine_meridional = np.linalg.eigvalsh(fine_matrix[:2, :2])
    coarse_branch_gap = float(coarse[3] - coarse_meridional[-1])
    fine_branch_gap = float(fine[3] - fine_meridional[-1])

    def pair_branch(branch_gap: float) -> str:
        return (
            "both_meridional_eigenvalues"
            if branch_gap >= 0.0
            else "lower_meridional_plus_azimuthal"
        )

    return {
        "coarse_components": {
            name: float(value)
            for name, value in zip(COMPONENT_NAMES, coarse, strict=True)
        },
        "fine_components": {
            name: float(value)
            for name, value in zip(COMPONENT_NAMES, fine, strict=True)
        },
        "component_differences_fine_minus_coarse": {
            name: float(value)
            for name, value in zip(
                COMPONENT_NAMES,
                component_delta,
                strict=True,
            )
        },
        "coarse_shifted_eigenvalues": [
            float(value) for value in coarse_eigenvalues
        ],
        "fine_shifted_eigenvalues": [
            float(value) for value in fine_eigenvalues
        ],
        "shifted_eigenvalue_differences_fine_minus_coarse": [
            float(value)
            for value in (fine_eigenvalues - coarse_eigenvalues)
        ],
        "coarse_pair": coarse_pair,
        "fine_pair": fine_pair,
        "pair_difference_fine_minus_coarse": pair_difference,
        "axisymmetric_branch_diagnostics": {
            "coarse_meridional_eigenvalues_unshifted": [
                float(value) for value in coarse_meridional
            ],
            "fine_meridional_eigenvalues_unshifted": [
                float(value) for value in fine_meridional
            ],
            "coarse_azimuthal_minus_upper_meridional": coarse_branch_gap,
            "fine_azimuthal_minus_upper_meridional": fine_branch_gap,
            "coarse_pair_branch": pair_branch(coarse_branch_gap),
            "fine_pair_branch": pair_branch(fine_branch_gap),
            "pair_branch_changed": bool(
                pair_branch(coarse_branch_gap)
                != pair_branch(fine_branch_gap)
            ),
        },
        "trace_difference": float(np.trace(delta_matrix)),
        "largest_eigenvalue_difference": float(
            fine_raw[-1] - coarse_raw[-1]
        ),
        "spectral_selection_response": float(
            -(fine_raw[-1] - coarse_raw[-1])
        ),
        "pair_identity_trace_minus_largest_eigenvalue": float(
            np.trace(delta_matrix) - (fine_raw[-1] - coarse_raw[-1])
        ),
        "coarse_top_eigenvector": [
            float(value) for value in top_vector
        ],
        "coarse_top_eigenvalue_gap": float(
            coarse_raw[-1] - coarse_raw[-2]
        ),
        "fine_top_eigenvalue_gap": float(fine_raw[-1] - fine_raw[-2]),
        "top_eigenvector_absolute_overlap": float(
            abs(np.dot(top_vector, fine_vectors[:, -1]))
        ),
        "first_order_component_contributions": {
            name: float(value)
            for name, value in zip(
                COMPONENT_NAMES,
                first_order,
                strict=True,
            )
        },
        "first_order_sum": first_order_sum,
        "coarse_top_eigenvector_linearization_remainder": (
            linearization_remainder
        ),
        "exact_closure_error": float(closure_error),
        "perturbation_bounds": {
            "delta_matrix_spectral_norm": spectral_norm,
            "delta_matrix_frobenius_norm": frobenius_norm,
            "two_times_spectral_norm_pair_bound": twice_spectral_bound,
            "absolute_pair_difference": abs(pair_difference),
            "pair_to_two_spectral_bound_ratio": (
                abs(pair_difference) / twice_spectral_bound
                if twice_spectral_bound > 0.0
                else 0.0
            ),
            "ordered_eigenvalue_delta_l2": eigenvalue_delta_l2,
            "hoffman_wielandt_l2_le_frobenius": bool(
                eigenvalue_delta_l2
                <= frobenius_norm + DECOMPOSITION_ABSOLUTE_TOLERANCE
            ),
        },
        "shapley_attribution": _shapley_pair_attribution(
            coarse,
            fine,
            shift,
        ),
    }


def _point_decompositions(
    fine_system: Any,
    coarse_system: Any,
    fine_field: np.ndarray,
    coarse_field: np.ndarray,
    coordinates: np.ndarray,
    *,
    difference_step: float,
) -> list[dict[str, Any]]:
    points = np.asarray(coordinates, dtype=float)
    fine = _component_bundle(
        fine_system,
        fine_field,
        points,
        difference_step=difference_step,
    )
    coarse = _component_bundle(
        coarse_system,
        coarse_field,
        points,
        difference_step=difference_step,
    )
    rows: list[dict[str, Any]] = []
    for index, point in enumerate(points):
        decomposition = _spectral_pair_decomposition(
            coarse["components"][index],
            fine["components"][index],
            fine_system.shift,
        )
        rows.append(
            {
                "rho": float(point[0]),
                "z": float(point[1]),
                "role": (
                    "e031_sup_discrepancy_hotspot"
                    if tuple(point) == HOTSPOT
                    else "e031_detached_lobe_basin"
                ),
                **decomposition,
            }
        )
    return rows


def _canonical_common_window_summary(
    fine_field: np.ndarray,
    coarse_field: np.ndarray,
    bundle: dict[str, Any],
    label: str,
) -> dict[str, Any]:
    coordinates = np.column_stack((bundle["rho"], bundle["z"]))
    fine_pair = np.asarray(bundle["values"][label]["fine"], dtype=float)
    coarse_pair = np.asarray(bundle["values"][label]["coarse"], dtype=float)
    difference = fine_pair - coarse_pair
    maximum_index = int(np.argmax(np.abs(difference)))
    maximum_coordinate = tuple(coordinates[maximum_index])
    if maximum_coordinate != HOTSPOT:
        raise RuntimeError(
            "E-032 common-window maximum moved from the frozen E-031 hotspot"
        )
    fine_potential = np.asarray(fine_field)[bundle["fine_nodes"]]
    coarse_potential = np.asarray(coarse_field)[bundle["coarse_nodes"]]
    potential_difference = fine_potential - coarse_potential
    potential_index = int(np.argmax(np.abs(potential_difference)))
    eta = float(abs(potential_difference[potential_index]))
    hotspot_rho = HOTSPOT[0]
    step = CANONICAL_DIFFERENCE_STEP
    return {
        "common_node_count": int(coordinates.shape[0]),
        "difference_step": CANONICAL_DIFFERENCE_STEP,
        "epsilon": float(abs(difference[maximum_index])),
        "signed_pair_difference_fine_minus_coarse": float(
            difference[maximum_index]
        ),
        "maximum_discrepancy_coordinate": {
            "rho": float(maximum_coordinate[0]),
            "z": float(maximum_coordinate[1]),
        },
        "fine_pair": float(fine_pair[maximum_index]),
        "coarse_pair": float(coarse_pair[maximum_index]),
        "hotspot_reproduced": True,
        "fine_pair_values_sha256": e029._sha256_array(fine_pair),
        "coarse_pair_values_sha256": e029._sha256_array(coarse_pair),
        "signed_pair_differences_sha256": e029._sha256_array(difference),
        "common_node_potential_discrepancy": {
            "sup_norm_eta": eta,
            "maximum_coordinate": {
                "rho": float(coordinates[potential_index, 0]),
                "z": float(coordinates[potential_index, 1]),
            },
            "potential_differences_sha256": e029._sha256_array(
                potential_difference
            ),
            "centered_stencil_amplification_bounds_at_hotspot": {
                "radial_or_axial_second_derivative": 4.0
                * eta
                / step**2,
                "mixed_second_derivative": eta / step**2,
                "azimuthal_from_radial_first_derivative": (
                    eta / (hotspot_rho * step)
                ),
            },
            "interpretation": (
                "Algebraic sup bounds for centered differences of the "
                "common-node potential discrepancy. They show possible "
                "derivative amplification but are not attained error bars."
            ),
        },
    }


def _step_sensitivity(
    fine_system: Any,
    coarse_system: Any,
    fine_baseline_field: np.ndarray,
    coarse_baseline_field: np.ndarray,
    fine_field: np.ndarray,
    coarse_field: np.ndarray,
    roi_source: np.ndarray,
    roi_weights: np.ndarray,
) -> dict[str, Any]:
    coordinates = np.asarray(ROI_POINTS, dtype=float)
    by_step: list[dict[str, Any]] = []
    for step in RECONSTRUCTION_STEPS:
        baseline_rows = _point_decompositions(
            fine_system,
            coarse_system,
            fine_baseline_field,
            coarse_baseline_field,
            coordinates,
            difference_step=step,
        )
        rows = _point_decompositions(
            fine_system,
            coarse_system,
            fine_field,
            coarse_field,
            coordinates,
            difference_step=step,
        )
        for baseline, endpoint in zip(
            baseline_rows,
            rows,
            strict=True,
        ):
            response = (
                endpoint["pair_difference_fine_minus_coarse"]
                - baseline["pair_difference_fine_minus_coarse"]
            )
            endpoint["stage6_grid_gap_and_continuation_identity"] = {
                "stage6_pair_difference_fine_minus_coarse": (
                    baseline["pair_difference_fine_minus_coarse"]
                ),
                "differential_continuation_response": response,
                "reconstructed_endpoint_grid_gap": (
                    baseline["pair_difference_fine_minus_coarse"]
                    + response
                ),
                "identity_closure_error": (
                    baseline["pair_difference_fine_minus_coarse"]
                    + response
                    - endpoint["pair_difference_fine_minus_coarse"]
                ),
            }
        by_step.append(
            {
                "difference_step": step,
                "stage6_points": baseline_rows,
                "points": rows,
            }
        )

    canonical_index = RECONSTRUCTION_STEPS.index(
        CANONICAL_DIFFERENCE_STEP
    )
    canonical_rows = by_step[canonical_index]["points"]
    for step_row in by_step:
        for point_index, point_row in enumerate(step_row["points"]):
            canonical = canonical_rows[point_index]
            point_row["step_change_from_canonical"] = {
                "fine_pair": (
                    point_row["fine_pair"] - canonical["fine_pair"]
                ),
                "coarse_pair": (
                    point_row["coarse_pair"] - canonical["coarse_pair"]
                ),
                "pair_difference_fine_minus_coarse": (
                    point_row["pair_difference_fine_minus_coarse"]
                    - canonical["pair_difference_fine_minus_coarse"]
                ),
            }

    point_summaries: list[dict[str, Any]] = []
    for point_index, point in enumerate(coordinates):
        differences = np.array(
            [
                row["points"][point_index][
                    "pair_difference_fine_minus_coarse"
                ]
                for row in by_step
            ],
            dtype=float,
        )
        absolute = np.abs(differences)
        point_summaries.append(
            {
                "rho": float(point[0]),
                "z": float(point[1]),
                "pair_differences_by_step": {
                    f"{step:.17g}": float(value)
                    for step, value in zip(
                        RECONSTRUCTION_STEPS,
                        differences,
                        strict=True,
                    )
                },
                "signed_range_over_steps": float(
                    np.max(differences) - np.min(differences)
                ),
                "absolute_range_over_steps": float(
                    np.max(absolute) - np.min(absolute)
                ),
                "minimum_absolute_discrepancy_step": (
                    RECONSTRUCTION_STEPS[int(np.argmin(absolute))]
                ),
                "maximum_absolute_discrepancy_step": (
                    RECONSTRUCTION_STEPS[int(np.argmax(absolute))]
                ),
                "canonical_absolute_discrepancy": float(
                    absolute[canonical_index]
                ),
                "step_effect_0p5_minus_0p25": float(
                    differences[RECONSTRUCTION_STEPS.index(0.5)]
                    - differences[RECONSTRUCTION_STEPS.index(0.25)]
                ),
            }
        )
    lobe_weights = np.asarray(roi_weights, dtype=float)[1:]
    lobe_source = np.asarray(roi_source, dtype=float)[1:]
    lobe_charge_weights = lobe_weights * lobe_source
    lobe_summaries: list[dict[str, Any]] = []
    for step_row in by_step:
        lobe_rows = step_row["points"][1:]
        differences = np.asarray(
            [
                row["pair_difference_fine_minus_coarse"]
                for row in lobe_rows
            ],
            dtype=float,
        )
        fine_pairs = np.asarray(
            [row["fine_pair"] for row in lobe_rows],
            dtype=float,
        )
        coarse_pairs = np.asarray(
            [row["coarse_pair"] for row in lobe_rows],
            dtype=float,
        )
        lobe_summaries.append(
            {
                "difference_step": step_row["difference_step"],
                "unweighted_mean_pair_difference": float(
                    np.mean(differences)
                ),
                "common_volume_weighted_mean_pair_difference": float(
                    np.average(differences, weights=lobe_weights)
                ),
                "source_charge_weighted_mean_pair_difference": float(
                    np.average(
                        differences,
                        weights=lobe_charge_weights,
                    )
                ),
                "minimum_fine_pair": float(np.min(fine_pairs)),
                "minimum_coarse_pair": float(np.min(coarse_pairs)),
                "all_fine_and_coarse_pairs_above_0p02": bool(
                    np.all(fine_pairs > 0.02)
                    and np.all(coarse_pairs > 0.02)
                ),
            }
        )
    canonical_lobe = next(
        row
        for row in by_step
        if row["difference_step"] == CANONICAL_DIFFERENCE_STEP
    )
    half_lobe = next(
        row for row in by_step if row["difference_step"] == 0.5
    )
    lobe_sign_changes = [
        bool(
            np.sign(canonical["pair_difference_fine_minus_coarse"])
            != np.sign(half["pair_difference_fine_minus_coarse"])
        )
        for canonical, half in zip(
            canonical_lobe["points"][1:],
            half_lobe["points"][1:],
            strict=True,
        )
    ]
    return {
        "steps": by_step,
        "point_summaries": point_summaries,
        "lobe_summaries": lobe_summaries,
        "lobe_node_sign_changes_between_0p25_and_0p5": lobe_sign_changes,
        "interpretation": (
            "This is a reconstruction-scale sensitivity on fixed transient "
            "fields and fixed physical coordinates. It is not a grid-"
            "convergence order or continuum-Hessian estimate."
        ),
    }


def _dominance_summary(step_sensitivity: dict[str, Any]) -> dict[str, Any]:
    canonical = next(
        row
        for row in step_sensitivity["steps"]
        if row["difference_step"] == CANONICAL_DIFFERENCE_STEP
    )
    hotspot = canonical["points"][0]
    hotspot_shapley = hotspot["shapley_attribution"][
        "component_contributions"
    ]
    hotspot_dominant = max(
        COMPONENT_NAMES,
        key=lambda name: abs(hotspot_shapley[name]),
    )

    lobe_values = {
        name: np.mean(
            [
                abs(
                    row["shapley_attribution"][
                        "component_contributions"
                    ][name]
                )
                for row in canonical["points"][1:]
            ]
        )
        for name in COMPONENT_NAMES
    }
    lobe_dominant = max(lobe_values, key=lobe_values.get)
    half_step = next(
        row
        for row in step_sensitivity["steps"]
        if row["difference_step"] == 0.5
    )
    half_hotspot = half_step["points"][0]
    half_shapley = half_hotspot["shapley_attribution"][
        "component_contributions"
    ]
    half_dominant = max(
        COMPONENT_NAMES,
        key=lambda name: abs(half_shapley[name]),
    )
    canonical_abs = abs(
        hotspot["pair_difference_fine_minus_coarse"]
    )
    half_abs = abs(half_hotspot["pair_difference_fine_minus_coarse"])

    def order_robust_component(point: dict[str, Any]) -> str | None:
        envelopes = point["shapley_attribution"][
            "coalition_marginal_envelopes"
        ]
        candidates: list[str] = []
        for name in COMPONENT_NAMES:
            lower = envelopes[name]["minimum"]
            upper = envelopes[name]["maximum"]
            same_nonzero_sign = lower > 0.0 or upper < 0.0
            if not same_nonzero_sign:
                continue
            minimum_magnitude = min(abs(lower), abs(upper))
            competitor_maximum = max(
                max(
                    abs(envelopes[other]["minimum"]),
                    abs(envelopes[other]["maximum"]),
                )
                for other in COMPONENT_NAMES
                if other != name
            )
            if minimum_magnitude > competitor_maximum:
                candidates.append(name)
        return candidates[0] if len(candidates) == 1 else None

    relative_step_drift = (
        abs(half_abs - canonical_abs) / canonical_abs
        if canonical_abs > 0.0
        else 0.0
    )
    return {
        "canonical_hotspot_dominant_absolute_shapley_component": (
            hotspot_dominant
        ),
        "canonical_hotspot_shapley_components": hotspot_shapley,
        "canonical_hotspot_trace_response": hotspot["trace_difference"],
        "canonical_hotspot_spectral_selection_response": hotspot[
            "spectral_selection_response"
        ],
        "canonical_hotspot_coarse_eigenvector_linearization_remainder": (
            hotspot["coarse_top_eigenvector_linearization_remainder"]
        ),
        "canonical_hotspot_order_robust_component": (
            order_robust_component(hotspot)
        ),
        "step_0p5_hotspot_dominant_absolute_shapley_component": (
            half_dominant
        ),
        "step_0p5_hotspot_order_robust_component": (
            order_robust_component(half_hotspot)
        ),
        "hotspot_absolute_discrepancy_0p25": canonical_abs,
        "hotspot_absolute_discrepancy_0p5": half_abs,
        "hotspot_relative_step_drift": relative_step_drift,
        "hotspot_discrepancy_reduction_fraction_at_0p5": (
            1.0 - half_abs / canonical_abs
            if canonical_abs > 0.0
            else 0.0
        ),
        "hotspot_dominant_component_cross_step_stable": bool(
            hotspot_dominant == half_dominant
            and relative_step_drift <= 0.25
        ),
        "canonical_lobe_mean_absolute_shapley_components": {
            name: float(value) for name, value in lobe_values.items()
        },
        "canonical_lobe_dominant_mean_absolute_shapley_component": (
            lobe_dominant
        ),
    }


def run_campaign(
    *,
    accepted_stage6_checkpoint: str | Path = (
        e029.ACCEPTED_STAGE6_CHECKPOINT
    ),
    configuration: AmgConfiguration = AmgConfiguration(),
) -> dict[str, Any]:
    """Run the bounded, no-checkpoint E-032 diagnostic campaign."""

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
        fine_system,
        fine_stage6,
        fine_source,
    )
    e029._verify_fine_reference_caps(fine_baseline_tail)
    fine_fields, fine_stages = e031._solve_transient_endpoints(
        fine_system,
        fine_source,
        fine_stage6,
        e029.FINE_STAGE6_REFERENCE_CAPS,
        configuration,
    )
    for stage in fine_stages:
        stage["diagnostic_role"] = "verified_unaccepted_e032_endpoint"

    coarse_system, coarse_source, coarse_stage6, coarse_preparation = (
        e029._fresh_coarse_stage6(configuration)
    )
    coarse_baseline_tail = e029.matched_tail_diagnostics(
        coarse_system,
        coarse_stage6,
        coarse_source,
    )
    coarse_caps = e029.tail_caps_from_baseline(coarse_baseline_tail)
    coarse_fields, coarse_stages = e031._solve_transient_endpoints(
        coarse_system,
        coarse_source,
        coarse_stage6,
        coarse_caps,
        configuration,
    )
    for stage in coarse_stages:
        stage["diagnostic_role"] = "verified_unaccepted_e032_endpoint"

    bundle = e031._common_node_bundle(
        fine_system,
        coarse_system,
        fine_source,
        coarse_source,
        fine_fields,
        coarse_fields,
    )
    comparisons: list[dict[str, Any]] = []
    for amplitude in VERIFICATION_AMPLITUDES:
        label = f"{amplitude:.17g}"
        common_window = _canonical_common_window_summary(
            fine_fields[label],
            coarse_fields[label],
            bundle,
            label,
        )
        coordinates = np.column_stack((bundle["rho"], bundle["z"]))
        roi_indices = []
        for point in ROI_POINTS:
            matches = np.flatnonzero(
                (coordinates[:, 0] == point[0])
                & (coordinates[:, 1] == point[1])
            )
            if matches.size != 1:
                raise RuntimeError("a frozen E-032 ROI point is missing")
            roi_indices.append(int(matches[0]))
        roi_indices_array = np.asarray(roi_indices, dtype=int)
        sensitivity = _step_sensitivity(
            fine_system,
            coarse_system,
            fine_stage6,
            coarse_stage6,
            fine_fields[label],
            coarse_fields[label],
            np.asarray(bundle["source"])[roi_indices_array],
            np.asarray(bundle["weights"])[roi_indices_array],
        )
        comparisons.append(
            {
                "amplitude": amplitude,
                "canonical_common_window": common_window,
                "roi_step_sensitivity": sensitivity,
                "dominance_summary": _dominance_summary(sensitivity),
            }
        )

    reconstruction_step_stable = all(
        row["dominance_summary"][
            "hotspot_dominant_component_cross_step_stable"
        ]
        for row in comparisons
    ) and not any(
        any(
            row["roi_step_sensitivity"][
                "lobe_node_sign_changes_between_0p25_and_0p5"
            ]
        )
        for row in comparisons
    )
    report = {
        "epistemic_status": (
            "component and reconstruction-scale decomposition of a Hessian-"
            "derived numerical discrepancy for a hypothetical PDE; not a "
            "continuum solution, detected physical field, useful artificial "
            "gravity, inertial control, spacetime engineering, FTL, or "
            "propulsion"
        ),
        "focus_question": (
            "Which radial, mixed, axial, azimuthal, eigenvalue, or physical "
            "reconstruction-step contribution dominates E-031's common-node "
            "pair-margin discrepancy at the frozen hotspot and lobe basin?"
        ),
        "runtime_provenance": e026.runtime_provenance(),
        "implementation_provenance": implementation_provenance(),
        "configuration": {
            "amg": e026.configuration_provenance(configuration),
            "accepted_baseline_amplitude": BASELINE_AMPLITUDE,
            "verification_amplitudes": list(VERIFICATION_AMPLITUDES),
            "canonical_difference_step": CANONICAL_DIFFERENCE_STEP,
            "reconstruction_steps": list(RECONSTRUCTION_STEPS),
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
        "fine": {
            "grid": {
                "radial_max": fine_system.grid.radial_max,
                "spacing": fine_system.grid.spacing,
                "directional_radius": (
                    fine_system.grid.directional_radius
                ),
                "unknowns": fine_system.size,
            },
            "source_metadata": fine_source_metadata,
            "stage6_field_sha256": e029._sha256_array(fine_stage6),
            "stage6_baseline_tail": fine_baseline_tail,
            "stages": fine_stages,
        },
        "coarse": {
            "grid": {
                "radial_max": coarse_system.grid.radial_max,
                "spacing": coarse_system.grid.spacing,
                "directional_radius": (
                    coarse_system.grid.directional_radius
                ),
                "unknowns": coarse_system.size,
            },
            "preparation": coarse_preparation,
            "stage6_field_sha256": e029._sha256_array(coarse_stage6),
            "stage6_baseline_tail": coarse_baseline_tail,
            "stages": coarse_stages,
        },
        "common_mapping": {
            "common_node_count": int(bundle["coarse_nodes"].size),
            "coarse_global_nodes_sha256": e029._sha256_array(
                bundle["coarse_nodes"]
            ),
            "fine_global_nodes_sha256": e029._sha256_array(
                bundle["fine_nodes"]
            ),
            "source_values_sha256": e029._sha256_array(bundle["source"]),
            "source_values_bitwise_identical": True,
        },
        "comparisons": comparisons,
        "decision": {
            "diagnostic_completed": True,
            "status": (
                "component_attribution_cross_step_stable"
                if reconstruction_step_stable
                else "reconstruction_scale_sensitive_no_unique_dominant_cause"
            ),
            "accepted_amplitude": BASELINE_AMPLITUDE,
            "accepted_lineage_changed": False,
            "checkpoint_or_field_artifacts_written_by_campaign": False,
            "report_output_policy": (
                "run_campaign returns an in-memory report; the CLI writes "
                "JSON only when the caller supplies --report-json"
            ),
            "all_frozen_hotspots_reproduced": all(
                row["canonical_common_window"]["hotspot_reproduced"]
                for row in comparisons
            ),
            "all_shapley_decompositions_close": True,
            "all_hoffman_wielandt_checks_pass": all(
                point["perturbation_bounds"][
                    "hoffman_wielandt_l2_le_frobenius"
                ]
                for row in comparisons
                for step in row["roi_step_sensitivity"]["steps"]
                for point in step["points"]
            ),
            "component_attribution_cross_step_stable": (
                reconstruction_step_stable
            ),
        },
        "limitations": [
            "The decomposition operates on reconstructed finite-difference Hessians of two transient discrete fields, not on a known continuum Hessian.",
            "A Shapley attribution is exact and order-neutral for the declared four-component replacement game, but it is not a causal error budget.",
            "The coarse-eigenvector first-order ledger is basis-sensitive near a repeated top eigenvalue; reported spectral gaps and the exact remainder expose that limitation.",
            "Changing the physical difference step changes a postprocessor on fixed fields; it is not an independent grid-refinement sequence or convergence order.",
            "The fine-native 0.125 step is excluded because it is sub-cell on the coarse grid and would diagnose interpolation amplification rather than a mesh-compatible common reconstruction.",
            "Only the frozen hotspot and three-node lobe basin are compared at 0.25 and 0.5; the full common-window sup norm remains the canonical 0.25 reconstruction.",
            "No diagnostic endpoint is retained as an accepted or work checkpoint.",
            "No 13/24, 7/12, 8/12, outer-box, density, asymmetry, target, EFT, or engineering extension is authorized.",
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
        "--preconditioner",
        choices=("pgsa",),
        default="pgsa",
    )
    args = parser.parse_args()
    report = run_campaign(
        accepted_stage6_checkpoint=args.accepted_stage6_checkpoint,
        configuration=AmgConfiguration(kind=args.preconditioner),
    )
    if args.report_json is not None:
        args.report_json.write_text(
            json.dumps(
                report,
                allow_nan=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    dominant = report["comparisons"][0]["dominance_summary"][
        "canonical_hotspot_dominant_absolute_shapley_component"
    ]
    print(
        "E-032 "
        f"decision={report['decision']['status']} "
        f"hotspot_dominant={dominant} "
        f"elapsed={report['resource_accounting']['elapsed_seconds']:.2f}s"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""E-033 exact common-node potential-error stencil diagnostic.

E-032 found that the matched fine/coarse Hessian-derived pair discrepancy at
its frozen hotspot changed strongly when the physical reconstruction step was
changed from 0.25 to 0.5.  This module keeps only the same transient 49/96 and
25/48 endpoints and asks a narrower question: does the fine-minus-coarse
potential error on one predeclared 5x5 common-node patch contain derivative
content that explains that reconstruction-scale sensitivity?

The analysis is deliberately error-first:

* all 25 potential differences are exact coincident fine/coarse lattice
  values, never interpolated values;
* the 0.25 and 0.5 centered component differences are written as explicit
  linear stencils of that potential error;
* one unweighted total-degree-two least-squares recovery is applied on the
  frozen 5x5 patch, with its rank, condition number, weights, and residuals
  exposed; and
* manufactured quadratic, smooth, and grid-scale controls delimit what the
  diagnostic can and cannot distinguish.

The pair margin itself is nonlinear in Hessian eigenvalues.  It is therefore
recomputed from the separately recovered fine and coarse component vectors;
it is never represented as a linear stencil of the potential error.

No endpoint from this module is accepted, checkpointed, or promoted as
evidence for a continuum solution, a physical field, artificial gravity,
inertial control, spacetime engineering, faster-than-light travel, or
propulsion.
"""

from __future__ import annotations

import argparse
import hashlib
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
import models.e032_hessian_discrepancy as e032
from models.e026_nonsymmetric_amg import AmgConfiguration


BASELINE_AMPLITUDE = e032.BASELINE_AMPLITUDE
VERIFICATION_AMPLITUDES = e032.VERIFICATION_AMPLITUDES
COMMON_NODE_STEP = 0.25
NESTED_RECONSTRUCTION_STEPS = (0.25, 0.5)
PATCH_OFFSETS = tuple(range(-2, 3))
PATCH_HALF_WIDTH = 0.5
RECOVERY_LENGTH = PATCH_HALF_WIDTH
HOTSPOT = e032.HOTSPOT
LOBE_BASIN = e032.LOBE_BASIN
ROI_POINTS = e032.ROI_POINTS
COMPONENT_NAMES = e032.COMPONENT_NAMES
LINEARITY_ABSOLUTE_TOLERANCE = 2.0e-11


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _quadratic_design() -> np.ndarray:
    """Return the frozen dimensionless 5x5 quadratic design matrix."""

    rows = []
    for radial_offset in PATCH_OFFSETS:
        for axial_offset in PATCH_OFFSETS:
            xi = radial_offset * COMMON_NODE_STEP / RECOVERY_LENGTH
            zeta = axial_offset * COMMON_NODE_STEP / RECOVERY_LENGTH
            rows.append((1.0, xi, zeta, xi**2, xi * zeta, zeta**2))
    return np.asarray(rows, dtype=float)


QUADRATIC_DESIGN = _quadratic_design()
(
    QUADRATIC_PSEUDOINVERSE,
    _QUADRATIC_LSTSQ_RESIDUALS,
    QUADRATIC_RANK,
    QUADRATIC_SINGULAR_VALUES,
) = np.linalg.lstsq(
    QUADRATIC_DESIGN,
    np.eye(QUADRATIC_DESIGN.shape[0]),
    rcond=None,
)


def implementation_provenance() -> dict[str, Any]:
    """Fingerprint E-033 and every reused numerical implementation."""

    paths = {
        "e033_campaign": Path(__file__).resolve(),
        "e032_campaign": Path(e032.__file__).resolve(),
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
        "campaign": "E-033",
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
            "common_node_step": COMMON_NODE_STEP,
            "nested_reconstruction_steps": list(
                NESTED_RECONSTRUCTION_STEPS
            ),
            "patch_offsets": list(PATCH_OFFSETS),
            "patch_shape": [5, 5],
            "patch_half_width": PATCH_HALF_WIDTH,
            "hotspot": list(HOTSPOT),
            "lobe_basin": [list(point) for point in LOBE_BASIN],
            "recovery": {
                "basis": [
                    "1",
                    "xi",
                    "zeta",
                    "xi^2",
                    "xi*zeta",
                    "zeta^2",
                ],
                "xi_definition": "(rho-rho0)/0.5",
                "zeta_definition": "(z-z0)/0.5",
                "solver": (
                    "numpy.linalg.lstsq_svd_pseudoinverse_reused_for_fit_"
                    "and_reported_weights"
                ),
                "weighting": "unweighted_all_25_nodes",
                "rank": int(QUADRATIC_RANK),
                "singular_values": [
                    float(value) for value in QUADRATIC_SINGULAR_VALUES
                ],
                "condition_number_2": float(
                    QUADRATIC_SINGULAR_VALUES[0]
                    / QUADRATIC_SINGULAR_VALUES[-1]
                ),
            },
            "lineage_policy": (
                "All E-033 roots are transient diagnostics. Accepted lineage "
                "remains the immutable E-028 6/12 checkpoint."
            ),
        },
    }


def _patch_nodes(
    fine_system: Any,
    coarse_system: Any,
    center: tuple[float, float],
) -> tuple[np.ndarray, np.ndarray]:
    """Return exact coarse and mapped fine nodes for one frozen patch."""

    if not math.isclose(
        coarse_system.grid.spacing,
        COMMON_NODE_STEP,
        rel_tol=0.0,
        abs_tol=1.0e-14,
    ):
        raise ValueError("E-033 requires a 0.25 coarse common-node spacing")
    for coordinate in center:
        lattice_coordinate = coordinate / COMMON_NODE_STEP
        if not math.isclose(
            lattice_coordinate,
            round(lattice_coordinate),
            rel_tol=0.0,
            abs_tol=1.0e-12,
        ):
            raise ValueError("E-033 patch center must be a common lattice node")
    center_i = int(round(center[0] / COMMON_NODE_STEP))
    center_j = int(round(center[1] / COMMON_NODE_STEP))
    coarse_nodes: list[int] = []
    for radial_offset in PATCH_OFFSETS:
        for axial_offset in PATCH_OFFSETS:
            grid_i = center_i + radial_offset
            grid_j = center_j + axial_offset
            if (
                grid_i < 0
                or grid_j < 0
                or grid_i >= coarse_system.index_map.shape[0]
                or grid_j >= coarse_system.index_map.shape[1]
            ):
                raise ValueError("frozen E-033 patch leaves the coarse grid")
            node = int(coarse_system.index_map[grid_i, grid_j])
            if node < 0:
                raise ValueError("frozen E-033 patch reaches the boundary")
            coarse_nodes.append(node)
    coarse_array = np.asarray(coarse_nodes, dtype=int)
    fine_array = e031._coarse_to_fine_nodes(
        fine_system,
        coarse_system,
        coarse_array,
    )
    expected_rho = np.asarray(
        [
            center[0] + radial_offset * COMMON_NODE_STEP
            for radial_offset in PATCH_OFFSETS
            for _axial_offset in PATCH_OFFSETS
        ],
        dtype=float,
    )
    expected_z = np.asarray(
        [
            center[1] + axial_offset * COMMON_NODE_STEP
            for _radial_offset in PATCH_OFFSETS
            for axial_offset in PATCH_OFFSETS
        ],
        dtype=float,
    )
    np.testing.assert_array_equal(
        coarse_system.rho[coarse_array],
        expected_rho,
    )
    np.testing.assert_array_equal(
        coarse_system.z[coarse_array],
        expected_z,
    )
    np.testing.assert_array_equal(
        fine_system.rho[fine_array],
        expected_rho,
    )
    np.testing.assert_array_equal(
        fine_system.z[fine_array],
        expected_z,
    )
    return fine_array, coarse_array


def _common_error_patch(
    fine_system: Any,
    coarse_system: Any,
    fine_field: np.ndarray,
    coarse_field: np.ndarray,
    center: tuple[float, float],
) -> dict[str, Any]:
    """Sample one exact coincident-node fine/coarse potential patch."""

    fine_nodes, coarse_nodes = _patch_nodes(
        fine_system,
        coarse_system,
        center,
    )
    fine_values = np.asarray(fine_field, dtype=float)[fine_nodes].reshape(5, 5)
    coarse_values = np.asarray(coarse_field, dtype=float)[
        coarse_nodes
    ].reshape(5, 5)
    error = fine_values - coarse_values
    rows = []
    for radial_index, radial_offset in enumerate(PATCH_OFFSETS):
        for axial_index, axial_offset in enumerate(PATCH_OFFSETS):
            rows.append(
                {
                    "radial_offset_cells": radial_offset,
                    "axial_offset_cells": axial_offset,
                    "rho": center[0]
                    + radial_offset * COMMON_NODE_STEP,
                    "z": center[1] + axial_offset * COMMON_NODE_STEP,
                    "fine_node": int(
                        fine_nodes.reshape(5, 5)[
                            radial_index,
                            axial_index,
                        ]
                    ),
                    "coarse_node": int(
                        coarse_nodes.reshape(5, 5)[
                            radial_index,
                            axial_index,
                        ]
                    ),
                    "fine_potential": float(
                        fine_values[radial_index, axial_index]
                    ),
                    "coarse_potential": float(
                        coarse_values[radial_index, axial_index]
                    ),
                    "potential_error_fine_minus_coarse": float(
                        error[radial_index, axial_index]
                    ),
                }
            )
    return {
        "fine_values": fine_values,
        "coarse_values": coarse_values,
        "error": error,
        "fine_nodes": fine_nodes,
        "coarse_nodes": coarse_nodes,
        "rows": rows,
    }


def _linear_ledger(
    patch: np.ndarray,
    terms: tuple[tuple[int, int, float], ...],
) -> dict[str, Any]:
    """Evaluate and expose one exact linear stencil."""

    array = np.asarray(patch, dtype=float)
    if array.shape != (5, 5):
        raise ValueError("E-033 stencils require a 5x5 patch")
    rows = []
    for radial_offset, axial_offset, coefficient in terms:
        value = float(
            array[radial_offset + 2, axial_offset + 2]
        )
        rows.append(
            {
                "radial_offset_cells": radial_offset,
                "axial_offset_cells": axial_offset,
                "coefficient": coefficient,
                "potential_error": value,
                "contribution": coefficient * value,
            }
        )
    return {
        "terms": rows,
        "sum": float(sum(row["contribution"] for row in rows)),
    }


def _centered_component_ledgers(
    patch: np.ndarray,
    rho0: float,
    *,
    stride: int,
) -> dict[str, Any]:
    """Return the four centered cylindrical component stencils."""

    if stride not in (1, 2):
        raise ValueError("E-033 supports only one- and two-cell strides")
    step = stride * COMMON_NODE_STEP
    inverse_second = 1.0 / step**2
    ledgers = {
        "radial": _linear_ledger(
            patch,
            (
                (-stride, 0, inverse_second),
                (0, 0, -2.0 * inverse_second),
                (stride, 0, inverse_second),
            ),
        ),
        "mixed": _linear_ledger(
            patch,
            (
                (-stride, -stride, 0.25 * inverse_second),
                (-stride, stride, -0.25 * inverse_second),
                (stride, -stride, -0.25 * inverse_second),
                (stride, stride, 0.25 * inverse_second),
            ),
        ),
        "axial": _linear_ledger(
            patch,
            (
                (0, -stride, inverse_second),
                (0, 0, -2.0 * inverse_second),
                (0, stride, inverse_second),
            ),
        ),
        "azimuthal": _linear_ledger(
            patch,
            (
                (-stride, 0, -0.5 / (step * rho0)),
                (stride, 0, 0.5 / (step * rho0)),
            ),
        ),
    }
    return {
        "difference_step": step,
        "components": np.asarray(
            [ledgers[name]["sum"] for name in COMPONENT_NAMES],
            dtype=float,
        ),
        "ledgers": ledgers,
    }


def _nested_detail_ledgers(
    patch: np.ndarray,
    rho0: float,
) -> dict[str, Any]:
    """Expose exact 0.25-minus-0.5 component-detail stencils."""

    h = COMMON_NODE_STEP
    terms = {
        "radial": (
            (-2, 0, -1.0 / (4.0 * h**2)),
            (-1, 0, 1.0 / h**2),
            (0, 0, -3.0 / (2.0 * h**2)),
            (1, 0, 1.0 / h**2),
            (2, 0, -1.0 / (4.0 * h**2)),
        ),
        "mixed": (
            (-2, -2, -1.0 / (16.0 * h**2)),
            (-2, 2, 1.0 / (16.0 * h**2)),
            (-1, -1, 1.0 / (4.0 * h**2)),
            (-1, 1, -1.0 / (4.0 * h**2)),
            (1, -1, -1.0 / (4.0 * h**2)),
            (1, 1, 1.0 / (4.0 * h**2)),
            (2, -2, 1.0 / (16.0 * h**2)),
            (2, 2, -1.0 / (16.0 * h**2)),
        ),
        "axial": (
            (0, -2, -1.0 / (4.0 * h**2)),
            (0, -1, 1.0 / h**2),
            (0, 0, -3.0 / (2.0 * h**2)),
            (0, 1, 1.0 / h**2),
            (0, 2, -1.0 / (4.0 * h**2)),
        ),
        "azimuthal": (
            (-2, 0, 1.0 / (4.0 * h * rho0)),
            (-1, 0, -1.0 / (2.0 * h * rho0)),
            (1, 0, 1.0 / (2.0 * h * rho0)),
            (2, 0, -1.0 / (4.0 * h * rho0)),
        ),
    }
    ledgers = {
        name: _linear_ledger(patch, component_terms)
        for name, component_terms in terms.items()
    }
    return {
        "definition": (
            "exact component stencil at step 0.25 minus the nested stencil "
            "at step 0.5; radial and axial rows are negative fourth "
            "differences divided by 4*h^2"
        ),
        "components": np.asarray(
            [ledgers[name]["sum"] for name in COMPONENT_NAMES],
            dtype=float,
        ),
        "ledgers": ledgers,
    }


def _quadratic_recovery(
    patch: np.ndarray,
    rho0: float,
) -> dict[str, Any]:
    """Fit the one predeclared quadratic and recover center components."""

    if rho0 <= RECOVERY_LENGTH:
        raise ValueError("E-033 recovery does not define an axis fallback")
    values = np.asarray(patch, dtype=float)
    if values.shape != (5, 5):
        raise ValueError("E-033 recovery requires a 5x5 patch")
    flat = values.reshape(-1)
    if not np.all(np.isfinite(flat)):
        raise ValueError("E-033 recovery patch must be finite")
    coefficients = QUADRATIC_PSEUDOINVERSE @ flat
    predicted = QUADRATIC_DESIGN @ coefficients
    residual = flat - predicted
    centered = flat - np.mean(flat)
    centered_norm = float(np.linalg.norm(centered))
    patch_range = float(np.ptp(flat))
    components = np.asarray(
        (
            2.0 * coefficients[3] / RECOVERY_LENGTH**2,
            coefficients[4] / RECOVERY_LENGTH**2,
            2.0 * coefficients[5] / RECOVERY_LENGTH**2,
            coefficients[1] / (RECOVERY_LENGTH * rho0),
        ),
        dtype=float,
    )
    component_weights = np.vstack(
        (
            2.0 * QUADRATIC_PSEUDOINVERSE[3] / RECOVERY_LENGTH**2,
            QUADRATIC_PSEUDOINVERSE[4] / RECOVERY_LENGTH**2,
            2.0 * QUADRATIC_PSEUDOINVERSE[5] / RECOVERY_LENGTH**2,
            QUADRATIC_PSEUDOINVERSE[1] / (RECOVERY_LENGTH * rho0),
        )
    )
    return {
        "components": components,
        "coefficients": coefficients,
        "predicted": predicted.reshape(5, 5),
        "residual": residual.reshape(5, 5),
        "rank": int(QUADRATIC_RANK),
        "singular_values": QUADRATIC_SINGULAR_VALUES,
        "condition_number_2": float(
            QUADRATIC_SINGULAR_VALUES[0]
            / QUADRATIC_SINGULAR_VALUES[-1]
        ),
        "residual_l2": float(np.linalg.norm(residual)),
        "residual_rms": float(np.sqrt(np.mean(residual**2))),
        "residual_linf": float(np.max(np.abs(residual))),
        "residual_rms_over_patch_range": (
            float(np.sqrt(np.mean(residual**2))) / patch_range
            if patch_range > 0.0
            else 0.0
        ),
        "residual_l2_over_demeaned_patch_l2": (
            float(np.linalg.norm(residual)) / centered_norm
            if centered_norm > 0.0
            else 0.0
        ),
        "residual_linf_over_patch_range": (
            float(np.max(np.abs(residual))) / patch_range
            if patch_range > 0.0
            else 0.0
        ),
        "component_weights": component_weights,
    }


def _json_recovery(recovery: dict[str, Any]) -> dict[str, Any]:
    return {
        "components": {
            name: float(value)
            for name, value in zip(
                COMPONENT_NAMES,
                recovery["components"],
                strict=True,
            )
        },
        "coefficients": [
            float(value) for value in recovery["coefficients"]
        ],
        "rank": recovery["rank"],
        "singular_values": [
            float(value) for value in recovery["singular_values"]
        ],
        "condition_number_2": recovery["condition_number_2"],
        "residual_l2": recovery["residual_l2"],
        "residual_rms": recovery["residual_rms"],
        "residual_linf": recovery["residual_linf"],
        "residual_rms_over_patch_range": recovery[
            "residual_rms_over_patch_range"
        ],
        "residual_l2_over_demeaned_patch_l2": recovery[
            "residual_l2_over_demeaned_patch_l2"
        ],
        "residual_linf_over_patch_range": recovery[
            "residual_linf_over_patch_range"
        ],
        "component_weights": {
            name: [
                float(value)
                for value in recovery["component_weights"][index]
            ]
            for index, name in enumerate(COMPONENT_NAMES)
        },
    }


def _weighted_component_vector(components: np.ndarray) -> np.ndarray:
    values = np.asarray(components, dtype=float).copy()
    values[1] *= math.sqrt(2.0)
    return values


def _nearest_scale_comparison(
    inner: float | np.ndarray,
    outer: float | np.ndarray,
    recovered: float | np.ndarray,
) -> dict[str, Any]:
    """Return a descriptive nearest-scale comparison with a tie state."""

    inner_values = np.atleast_1d(np.asarray(inner, dtype=float))
    outer_values = np.atleast_1d(np.asarray(outer, dtype=float))
    recovered_values = np.atleast_1d(np.asarray(recovered, dtype=float))
    if not (
        inner_values.shape
        == outer_values.shape
        == recovered_values.shape
    ):
        raise ValueError("nearest-scale inputs must have equal shapes")
    distance_to_inner = float(
        np.linalg.norm(recovered_values - inner_values)
    )
    distance_to_outer = float(
        np.linalg.norm(recovered_values - outer_values)
    )
    numerical_tolerance = (
        128.0
        * np.finfo(float).eps
        * max(1.0, distance_to_inner, distance_to_outer)
    )
    if abs(distance_to_inner - distance_to_outer) <= numerical_tolerance:
        nearest = "equidistant_within_roundoff"
    elif distance_to_outer < distance_to_inner:
        nearest = "0.5_centered"
    else:
        nearest = "0.25_centered"
    denominator = max(
        distance_to_inner,
        distance_to_outer,
        np.finfo(float).tiny,
    )
    return {
        "distance_to_0p25": distance_to_inner,
        "distance_to_0p5": distance_to_outer,
        "relative_distance_margin": (
            abs(distance_to_inner - distance_to_outer) / denominator
        ),
        "nearest": nearest,
        "interpretation": (
            "Descriptive geometry only; no statistical independence, "
            "mechanism classification, or convergence inference."
        ),
    }


def _analyze_patch(
    fine_system: Any,
    coarse_system: Any,
    fine_field: np.ndarray,
    coarse_field: np.ndarray,
    center: tuple[float, float],
) -> dict[str, Any]:
    """Run the exact stencils and one recovery on one ROI patch."""

    patch = _common_error_patch(
        fine_system,
        coarse_system,
        fine_field,
        coarse_field,
        center,
    )
    scale_rows = []
    centered_results: dict[float, dict[str, Any]] = {}
    coordinate = np.asarray([center], dtype=float)
    for stride in (1, 2):
        step = stride * COMMON_NODE_STEP
        fine_stencil = _centered_component_ledgers(
            patch["fine_values"],
            center[0],
            stride=stride,
        )
        coarse_stencil = _centered_component_ledgers(
            patch["coarse_values"],
            center[0],
            stride=stride,
        )
        error_stencil = _centered_component_ledgers(
            patch["error"],
            center[0],
            stride=stride,
        )
        linearity_residual = (
            fine_stencil["components"]
            - coarse_stencil["components"]
            - error_stencil["components"]
        )
        direct_fine = e032._component_bundle(
            fine_system,
            fine_field,
            coordinate,
            difference_step=step,
        )["components"][0]
        direct_coarse = e032._component_bundle(
            coarse_system,
            coarse_field,
            coordinate,
            difference_step=step,
        )["components"][0]
        direct_residual = np.concatenate(
            (
                fine_stencil["components"] - direct_fine,
                coarse_stencil["components"] - direct_coarse,
            )
        )
        if (
            np.max(np.abs(linearity_residual))
            > LINEARITY_ABSOLUTE_TOLERANCE
            or np.max(np.abs(direct_residual))
            > LINEARITY_ABSOLUTE_TOLERANCE
        ):
            raise RuntimeError("E-033 exact common-node stencil closure failed")
        decomposition = e032._spectral_pair_decomposition(
            coarse_stencil["components"],
            fine_stencil["components"],
            fine_system.shift,
        )
        row = {
            "difference_step": step,
            "fine_components": {
                name: float(value)
                for name, value in zip(
                    COMPONENT_NAMES,
                    fine_stencil["components"],
                    strict=True,
                )
            },
            "coarse_components": {
                name: float(value)
                for name, value in zip(
                    COMPONENT_NAMES,
                    coarse_stencil["components"],
                    strict=True,
                )
            },
            "potential_error_component_stencils": {
                "components": {
                    name: float(value)
                    for name, value in zip(
                        COMPONENT_NAMES,
                        error_stencil["components"],
                        strict=True,
                    )
                },
                "ledgers": error_stencil["ledgers"],
            },
            "component_linearity_max_absolute_closure_error": float(
                np.max(np.abs(linearity_residual))
            ),
            "direct_e032_reconstruction_max_absolute_closure_error": float(
                np.max(np.abs(direct_residual))
            ),
            "pair_decomposition": decomposition,
        }
        scale_rows.append(row)
        centered_results[step] = {
            "fine": fine_stencil["components"],
            "coarse": coarse_stencil["components"],
            "error": error_stencil["components"],
            "pair_difference": decomposition[
                "pair_difference_fine_minus_coarse"
            ],
        }

    nested = _nested_detail_ledgers(patch["error"], center[0])
    nested_residual = (
        centered_results[0.25]["error"]
        - centered_results[0.5]["error"]
        - nested["components"]
    )
    if np.max(np.abs(nested_residual)) > LINEARITY_ABSOLUTE_TOLERANCE:
        raise RuntimeError("E-033 nested detail identity failed")

    fine_recovery = _quadratic_recovery(
        patch["fine_values"],
        center[0],
    )
    coarse_recovery = _quadratic_recovery(
        patch["coarse_values"],
        center[0],
    )
    error_recovery = _quadratic_recovery(patch["error"], center[0])
    recovery_linearity_residual = (
        fine_recovery["components"]
        - coarse_recovery["components"]
        - error_recovery["components"]
    )
    if (
        np.max(np.abs(recovery_linearity_residual))
        > LINEARITY_ABSOLUTE_TOLERANCE
    ):
        raise RuntimeError("E-033 quadratic recovery closure failed")
    recovery_decomposition = e032._spectral_pair_decomposition(
        coarse_recovery["components"],
        fine_recovery["components"],
        fine_system.shift,
    )

    pair_025 = float(centered_results[0.25]["pair_difference"])
    pair_05 = float(centered_results[0.5]["pair_difference"])
    pair_quadratic = float(
        recovery_decomposition["pair_difference_fine_minus_coarse"]
    )
    vector_025 = _weighted_component_vector(
        centered_results[0.25]["error"]
    )
    vector_05 = _weighted_component_vector(
        centered_results[0.5]["error"]
    )
    vector_quadratic = _weighted_component_vector(
        error_recovery["components"]
    )
    pair_nearest = _nearest_scale_comparison(
        pair_025,
        pair_05,
        pair_quadratic,
    )
    component_nearest = _nearest_scale_comparison(
        vector_025,
        vector_05,
        vector_quadratic,
    )
    return {
        "rho": center[0],
        "z": center[1],
        "role": (
            "e031_sup_pair_discrepancy_hotspot"
            if center == HOTSPOT
            else "e031_detached_lobe_basin"
        ),
        "patch": {
            "shape": [5, 5],
            "common_node_step": COMMON_NODE_STEP,
            "rows": patch["rows"],
            "potential_error_minimum": float(np.min(patch["error"])),
            "potential_error_maximum": float(np.max(patch["error"])),
            "potential_error_range": float(np.ptp(patch["error"])),
            "potential_error_rms": float(
                np.sqrt(np.mean(patch["error"] ** 2))
            ),
            "fine_values_sha256": e029._sha256_array(
                patch["fine_values"]
            ),
            "coarse_values_sha256": e029._sha256_array(
                patch["coarse_values"]
            ),
            "potential_error_sha256": e029._sha256_array(
                patch["error"]
            ),
        },
        "centered_stencils": scale_rows,
        "nested_0p25_minus_0p5_detail": {
            "components": {
                name: float(value)
                for name, value in zip(
                    COMPONENT_NAMES,
                    nested["components"],
                    strict=True,
                )
            },
            "definition": nested["definition"],
            "ledgers": nested["ledgers"],
            "max_absolute_closure_error": float(
                np.max(np.abs(nested_residual))
            ),
        },
        "quadratic_recovery": {
            "fine": _json_recovery(fine_recovery),
            "coarse": _json_recovery(coarse_recovery),
            "potential_error": _json_recovery(error_recovery),
            "component_linearity_max_absolute_closure_error": float(
                np.max(np.abs(recovery_linearity_residual))
            ),
            "pair_decomposition": recovery_decomposition,
        },
        "descriptive_scale_comparison": {
            "pair_difference_0p25": pair_025,
            "pair_difference_0p5": pair_05,
            "pair_difference_quadratic_recovery": pair_quadratic,
            "quadratic_pair_nearest_scale": pair_nearest,
            "quadratic_component_vector_nearest_scale": (
                component_nearest
            ),
            "interpretation": (
                "The nearest-scale relations are descriptive and "
                "threshold-free. The declared manufactured controls show "
                "that they do not discriminate smooth higher-order, "
                "long-wave, and aliased content."
            ),
        },
    }


def manufactured_validation() -> dict[str, Any]:
    """Return exactness gates and deliberately non-identifying controls."""

    rho0 = 6.0
    h = COMMON_NODE_STEP
    x = np.asarray(PATCH_OFFSETS, dtype=float)[:, None] * h
    y = np.asarray(PATCH_OFFSETS, dtype=float)[None, :] * h

    monomial_max_residual = 0.0
    for column in range(QUADRATIC_DESIGN.shape[1]):
        values = QUADRATIC_DESIGN[:, column].reshape(5, 5)
        recovered = _quadratic_recovery(values, rho0)
        monomial_max_residual = max(
            monomial_max_residual,
            recovered["residual_linf"],
        )

    quadratic = (
        1.0
        + 0.7 * x
        - 0.4 * y
        + 0.6 * x**2
        - 0.3 * x * y
        + 0.2 * y**2
    )
    expected = np.asarray((1.2, -0.3, 0.4, 0.7 / rho0))
    quadratic_components = {
        "0.25_centered": _centered_component_ledgers(
            quadratic,
            rho0,
            stride=1,
        )["components"],
        "0.5_centered": _centered_component_ledgers(
            quadratic,
            rho0,
            stride=2,
        )["components"],
        "quadratic_recovery": _quadratic_recovery(
            quadratic,
            rho0,
        )["components"],
    }
    quadratic_error = max(
        float(np.max(np.abs(values - expected)))
        for values in quadratic_components.values()
    )

    axial_quartic = (y / h) ** 4 + np.zeros_like(x)
    axial_nyquist = np.cos(math.pi * y / h) + np.zeros_like(x)
    wavenumber = 0.25 / h
    long_wave = np.cos(wavenumber * x) * np.cos(wavenumber * y)

    def control(
        patch: np.ndarray,
        true_components: np.ndarray,
        mechanism: str,
    ) -> dict[str, Any]:
        inner = _centered_component_ledgers(
            patch,
            rho0,
            stride=1,
        )["components"]
        outer = _centered_component_ledgers(
            patch,
            rho0,
            stride=2,
        )["components"]
        recovered = _quadratic_recovery(
            patch,
            rho0,
        )["components"]
        return {
            "mechanism": mechanism,
            "analytic_center_components": [
                float(value) for value in true_components
            ],
            "components_0p25": [float(value) for value in inner],
            "components_0p5": [float(value) for value in outer],
            "components_quadratic_recovery": [
                float(value) for value in recovered
            ],
            "quadratic_component_vector_nearest_scale": (
                _nearest_scale_comparison(
                    _weighted_component_vector(inner),
                    _weighted_component_vector(outer),
                    _weighted_component_vector(recovered),
                )
            ),
        }

    return {
        "quadratic_polynomial_gate": {
            "all_six_basis_monomials_max_fit_residual": (
                monomial_max_residual
            ),
            "expected_center_components": [
                float(value) for value in expected
            ],
            "maximum_component_error_across_both_scales_and_recovery": (
                quadratic_error
            ),
            "passed": bool(
                monomial_max_residual <= 2.0e-14
                and quadratic_error <= 2.0e-13
            ),
        },
        "controls_not_acceptance_tests": {
            "smooth_axial_quartic_with_zero_center_continuum_hessian": (
                control(
                    axial_quartic,
                    np.zeros(4, dtype=float),
                    "smooth_resolved_higher_order_polynomial",
                )
            ),
            "axial_nyquist_mode": control(
                axial_nyquist,
                np.asarray((0.0, 0.0, -math.pi**2 / h**2, 0.0)),
                "one_cell_aliasing_control",
            ),
            "long_wave_cosine_kh_0p25": control(
                long_wave,
                np.asarray(
                    (-wavenumber**2, 0.0, -wavenumber**2, 0.0)
                ),
                "smooth_long_wave_control",
            ),
            "interpretation": (
                "The smooth quartic, long-wave, and Nyquist controls all "
                "place the quadratic component vector nearer the 0.5 "
                "centered result despite representing mutually different "
                "mechanisms. The nearest-scale ordering is therefore "
                "non-identifying."
            ),
        },
    }


def _decision(
    comparisons: list[dict[str, Any]],
    validation: dict[str, Any],
) -> dict[str, Any]:
    rows = [
        point
        for comparison in comparisons
        for point in comparison["points"]
    ]
    pair_closer_to_half = sum(
        point["descriptive_scale_comparison"][
            "quadratic_pair_nearest_scale"
        ]["nearest"]
        == "0.5_centered"
        for point in rows
    )
    vector_closer_to_half = sum(
        point["descriptive_scale_comparison"][
            "quadratic_component_vector_nearest_scale"
        ]["nearest"]
        == "0.5_centered"
        for point in rows
    )
    controls = validation["controls_not_acceptance_tests"]
    control_names = (
        "smooth_axial_quartic_with_zero_center_continuum_hessian",
        "axial_nyquist_mode",
        "long_wave_cosine_kh_0p25",
    )
    control_nearest = {
        name: controls[name][
            "quadratic_component_vector_nearest_scale"
        ]["nearest"]
        for name in control_names
    }
    return {
        "diagnostic_completed": True,
        "status": "nonidentifying_mixed_recovery_result",
        "frozen_point_endpoint_count": len(rows),
        "descriptive_quadratic_pair_nearer_0p5_count": pair_closer_to_half,
        "descriptive_quadratic_component_vector_nearer_0p5_count": (
            vector_closer_to_half
        ),
        "manufactured_control_component_nearest_scales": control_nearest,
        "all_three_distinct_controls_are_also_nearer_0p5": bool(
            all(value == "0.5_centered" for value in control_nearest.values())
        ),
        "interpretation": (
            "The fixed quadratic error-component vector is nearer the "
            "0.5-centered vector at every frozen point/endpoint, but the "
            "long-wave, smooth-quartic, and Nyquist controls all produce "
            "the same ordering. The nonlinear recovered pair is nearer 0.5 "
            "only at the hotspot. The exact nested detail is localized, but "
            "these operators do not discriminate one-cell, smooth "
            "higher-order, and aliased content; the result remains "
            "unresolved."
        ),
        "accepted_amplitude": BASELINE_AMPLITUDE,
        "accepted_lineage_changed": False,
        "checkpoint_or_field_artifacts_written_by_campaign": False,
        "report_output_policy": (
            "run_campaign returns an in-memory report; the CLI writes JSON "
            "only when the caller supplies --report-json"
        ),
    }


def run_campaign(
    *,
    accepted_stage6_checkpoint: str | Path = (
        e029.ACCEPTED_STAGE6_CHECKPOINT
    ),
    configuration: AmgConfiguration = AmgConfiguration(),
) -> dict[str, Any]:
    """Run the bounded, no-checkpoint E-033 diagnostic campaign."""

    configuration.validate()
    if tuple(e031.VERIFICATION_AMPLITUDES) != tuple(
        VERIFICATION_AMPLITUDES
    ):
        raise RuntimeError(
            "E-031 endpoint schedule drifted from frozen E-033 scope"
        )
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
        stage["diagnostic_role"] = "verified_unaccepted_e033_endpoint"

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
        stage["diagnostic_role"] = "verified_unaccepted_e033_endpoint"

    comparisons = []
    all_fine_nodes: list[int] = []
    all_coarse_nodes: list[int] = []
    for amplitude in VERIFICATION_AMPLITUDES:
        label = f"{amplitude:.17g}"
        points = [
            _analyze_patch(
                fine_system,
                coarse_system,
                fine_fields[label],
                coarse_fields[label],
                point,
            )
            for point in ROI_POINTS
        ]
        comparisons.append(
            {
                "amplitude": amplitude,
                "points": points,
            }
        )
    for point in ROI_POINTS:
        fine_nodes, coarse_nodes = _patch_nodes(
            fine_system,
            coarse_system,
            point,
        )
        all_fine_nodes.extend(fine_nodes.tolist())
        all_coarse_nodes.extend(coarse_nodes.tolist())

    validation = manufactured_validation()
    if not validation["quadratic_polynomial_gate"]["passed"]:
        raise RuntimeError("E-033 manufactured quadratic gate failed")
    report = {
        "epistemic_status": (
            "exact common-node potential-error stencil and one local "
            "quadratic recovery diagnostic for transient numerical fields "
            "of a hypothetical PDE; not a continuum solution, detected "
            "physical field, useful artificial gravity, inertial control, "
            "spacetime engineering, FTL, or propulsion"
        ),
        "focus_question": (
            "At only the E-032 transient 49/96 and 25/48 endpoints, is the "
            "0.25-versus-0.5 Hessian-reconstruction change more compatible "
            "with one-cell-scale potential-error content or a locally "
            "coherent quadratic error on the frozen hotspot and lobe patches?"
        ),
        "runtime_provenance": e026.runtime_provenance(),
        "implementation_provenance": implementation_provenance(),
        "configuration": {
            "amg": e026.configuration_provenance(configuration),
            "accepted_baseline_amplitude": BASELINE_AMPLITUDE,
            "verification_amplitudes": list(VERIFICATION_AMPLITUDES),
            "common_node_step": COMMON_NODE_STEP,
            "nested_reconstruction_steps": list(
                NESTED_RECONSTRUCTION_STEPS
            ),
            "patch_shape": [5, 5],
            "quadratic_recovery_count": 1,
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
                "directional_radius": fine_system.grid.directional_radius,
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
                "directional_radius": coarse_system.grid.directional_radius,
                "unknowns": coarse_system.size,
            },
            "preparation": coarse_preparation,
            "stage6_field_sha256": e029._sha256_array(coarse_stage6),
            "stage6_baseline_tail": coarse_baseline_tail,
            "stages": coarse_stages,
        },
        "common_mapping": {
            "references_per_endpoint": len(ROI_POINTS) * 25,
            "unique_patch_nodes": len(set(all_coarse_nodes)),
            "fine_global_nodes_sha256": e029._sha256_array(
                np.asarray(sorted(set(all_fine_nodes)), dtype=int)
            ),
            "coarse_global_nodes_sha256": e029._sha256_array(
                np.asarray(sorted(set(all_coarse_nodes)), dtype=int)
            ),
            "coordinates_exactly_identical": True,
            "potential_error_patch_interpolation_used": False,
        },
        "manufactured_validation": validation,
        "comparisons": comparisons,
        "decision": _decision(comparisons, validation),
        "limitations": [
            "The endpoint fields are transient, tail-gate-failed diagnostics; accepted lineage remains the immutable E-028 6/12 checkpoint.",
            "The potential error is a fine-minus-coarse discrete-field difference on exact common nodes, not a bounded continuum potential error.",
            "Centered second differences amplify potential-error content as the inverse square of their step; small potential error does not imply small Hessian error.",
            "The quadratic fit is one fixed local recovery with exact degree-two reproduction, not a general Hessian-recovery convergence theorem.",
            "The quadratic fit uses the same outer plus-or-minus 0.5 support as the larger centered stencil, so closeness to that stencil is not independent convergence evidence.",
            "The recovery residual and nearest-scale comparisons are descriptive. No adaptive window, weights, threshold, or post-outcome recovery was tried.",
            "A smooth quartic can produce reconstruction-scale disagreement, while a Nyquist mode can alias; the two available scales cannot identify the generating mechanism.",
            "Pair margin is nonlinear in Hessian eigenvalues. Only component differences obey the exact potential-error stencil identities.",
            "The four patches overlap and therefore are correlated; the three lobe nodes are not independent samples.",
            "Solver error is checked by the inherited endpoint gates but is not enclosed as a rigorous Hessian-error interval.",
            "No diagnostic endpoint is retained as an accepted or work checkpoint.",
            "No amplitude advance, extra endpoint, refined solve, outer-box, density, asymmetry, target, EFT, or engineering extension is authorized.",
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
    print(
        "E-033 "
        f"decision={report['decision']['status']} "
        "pair_nearer_0p5="
        f"{report['decision']['descriptive_quadratic_pair_nearer_0p5_count']}/"
        f"{report['decision']['frozen_point_endpoint_count']} "
        f"elapsed={report['resource_accounting']['elapsed_seconds']:.2f}s"
    )


if __name__ == "__main__":
    main()

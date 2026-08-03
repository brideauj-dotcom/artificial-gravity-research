"""E-036 no-solve actual-solution derivative-enclosure closure audit.

E-035 left two separate questions open: whether a rigorous two-parameter
``(h, delta_theta)`` Hessian-error enclosure exists for the *actual* annular
solution, and whether the proposed validation protocol could be made fully
executable without looking at another nonlinear outcome.  This module closes
both questions without loading a field, building a PDE, or solving a PDE.

The protocol definitions are completed: every common-node mask is enumerated,
all native recovery supports are checked on all three proposed grids, the
three recovery families are generated and manufactured-validated, and exact
solver, transfer, parity, orientation, eigengap, and dormant row-equivalence
rules are frozen.  These definitions do not create an error theorem.

The enclosure audit is negative.  Existing convergence and consistency
results do not provide verified regularity, uniform ellipticity/stability,
boundary/axis, source-transition, algebraic-root, or between-node constants
for this fixed solution.  Nodal fields alone cannot supply the missing
between-node Hessian control: ``e_h(x)=h^2 sin(2*pi*x/h)`` vanishes on every
grid node while ``||e_h''||_inf=4*pi^2``.  Consequently H-019 and the annular
Galileon numerical line are parked with all prior evidence preserved.

This is numerical-method research about a hypothetical PDE.  It is not a
continuum solution, a detected field, artificial gravity, inertial control,
spacetime engineering, reactionless propulsion, or faster-than-light travel.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct
import time
from typing import Any, Iterable

import numpy as np
from scipy import sparse

import models.e033_potential_error_stencils as e033
import models.e034_postprocessor_transfer as e034
import models.e035_coupled_grid_preregistration as e035


CAMPAIGN = "E-036"
RADIAL_MAX = e035.RADIAL_MAX
BASE_SPACING = e035.BASELINE_SPACING
GRID_SPECIFICATIONS = e035.GRID_SPECIFICATIONS
RECOVERY_NAMES = ("C_h", "C_2h", "Q_2h")
COMPONENT_NAMES = ("radial", "mixed", "axial", "azimuthal")
MASK_NAMES = (
    "full_positive_source_support",
    "radial_transition",
    "angular_transition",
    "inner_feature_rectangle",
    "global_interior",
)
ACCEPTED_AMPLITUDE = 6.0 / 12.0
ACCEPTED_CHECKPOINT_SHA256 = (
    "ff82363833c84e416e020a8df56d6067b6b1f7612c41f30f6499d6b95690babb"
)
ACCEPTED_FIELD_SHA256 = (
    "cd806ff41c0a33d541cc5c1dba44a3c7ad693ddb6b81dda5eae2ac1db8757c3e"
)
ACCEPTED_REPORT_SHA256 = (
    "fe2c11e1d2e7806b12836325eaaed565137b5495efbb25417f4c6545fd3a256c"
)
ACCEPTED_E025_MODULE_SHA256 = (
    "7667750de59824be493981d8e063d5a475377776113b44d235178d81f7e711c3"
)
ACCEPTED_E028_MODULE_SHA256 = (
    "e3e4029e8e83a08ee9d1df8068e325a1b9f954d4fd26232de12f6c46bb8eb95d"
)
TRANSFER_FRACTION_CAP = 0.10
PARITY_FRACTION_CAP = 0.05
ABSOLUTE_TO_FINE_DIFFERENCE_CAP = 0.25
FLOAT_SAFETY_MULTIPLIER = 128.0
PRIMARY_METRIC_NAMES = (
    "matrix_weighted_l2",
    "matrix_linf_spectral",
    *(f"component_{name}_weighted_l2" for name in COMPONENT_NAMES),
    *(f"component_{name}_linf" for name in COMPONENT_NAMES),
)
PRIMARY_ACCEPTANCE_MASK_NAMES = MASK_NAMES[:3]
COUPLED_Q_KEYS = tuple(
    f"{mask}:{recovery}:{metric}"
    for mask in MASK_NAMES
    for recovery in RECOVERY_NAMES
    for metric in PRIMARY_METRIC_NAMES
)
OPERATOR_SPREAD_KEYS = tuple(
    f"{mask}:{metric}"
    for mask in MASK_NAMES
    for metric in PRIMARY_METRIC_NAMES
)
FIXED_ORIENTATION_KEYS = tuple(
    f"rho={rho:g},z={z:g}:{component}"
    for rho, z in e035.FIXED_POINTS
    for component in COMPONENT_NAMES
)
RECOVERY_TO_E034_POSTPROCESSOR = {
    "C_h": "centered_0p25",
    "C_2h": "centered_0p5",
    "Q_2h": "quadratic_5x5",
}
BASELINE_DIRECTIONAL_BASES = tuple(
    e035.e025.primitive_meridional_bases(e035.BASELINE_DIRECTIONAL_RADIUS)
)
BASELINE_ORDERED_MERIDIONAL_STEPS = tuple(
    step
    for first, second in BASELINE_DIRECTIONAL_BASES
    for step in ((first, second), (-second, first))
)
CANONICAL_OPERATOR_NAMES = (
    *(
        f"directional_{index:02d}_{first}_{second}"
        for index, (first, second) in enumerate(BASELINE_ORDERED_MERIDIONAL_STEPS)
    ),
    "azimuthal_24",
)
REQUIRED_ROW_ACTION_NAMES = (
    "zero",
    "one",
    "rho",
    "z",
    "rho2",
    "rho_z",
    "z2",
    "normalized_rho4_plus_z4",
    "normalized_rho2_z2",
    *(
        name
        for index, (first, second) in enumerate(BASELINE_ORDERED_MERIDIONAL_STEPS)
        for name in (
            f"operator_wave_cos_{index:02d}_{first}_{second}",
            f"operator_wave_sin_{index:02d}_{first}_{second}",
        )
    ),
    *(f"rademacher_seed_260719_{index}" for index in range(4)),
    *(f"gaussian_seed_260719_{index}" for index in range(4)),
)
REQUIRED_NONLINEAR_ACTION_NAMES = (
    "curvatures",
    "candidate_values",
    "default_first_index_argmins",
    "exact_tie_masks",
    "exact_tie_index_lists",
    "selected_values",
    "shifted_residual",
    "fixed_components",
    "active_gradients",
    "active_jacobian_actions",
    *(f"tie_selection_{index:02d}_active_jacobian_action" for index in range(16)),
)
EXPECTED_STAGE6_TIE_NODE_COUNT = 4
EXPECTED_STAGE6_TIE_MULTIPLICITIES = (2, 2, 2, 2)
BASELINE_UNKNOWN_COUNT = 322_319
BASELINE_INDEX_MAP_SHAPE = (641, 641)
REQUIRED_EQUIVALENCE_ARTIFACT_FIELDS = (
    "system",
    "field",
    "target_source",
    "checkpoint_payload",
    "report",
    "implementation_payloads",
)
REQUIRED_SYSTEM_ARTIFACT_FIELDS = (
    "radial_max",
    "spacing",
    "directional_radius",
    "cubic_coefficient",
    "bases",
    "rho",
    "z",
    "index_map",
    "operators",
    "boundary_offsets",
)
REQUIRED_DERIVED_LINEAGE_FIELDS = (
    "accepted_checkpoint_sha256",
    "accepted_field_sha256",
    "accepted_report_sha256",
    "system_sha256",
    "target_source_sha256",
    "e025_module_sha256",
    "e028_module_sha256",
)
REQUIRED_MANIFEST_FIELDS = (
    "accepted_checkpoint_sha256",
    "accepted_field_sha256",
    "accepted_report_sha256",
    "system_sha256",
    "target_source_sha256",
    "e025_module_sha256",
    "e028_module_sha256",
    "operator_order",
    "generator",
    "probe_vector_sha256",
    "dtype",
    "endianness",
    "signed_zero_policy",
)
EQUIVALENCE_LINEAGE_MANIFEST = {
    "accepted_checkpoint_sha256": ACCEPTED_CHECKPOINT_SHA256,
    "accepted_field_sha256": ACCEPTED_FIELD_SHA256,
    "accepted_report_sha256": ACCEPTED_REPORT_SHA256,
    "system_sha256": (
        "derive_from_supplied_canonical_E025_system_and_verify_against_report"
    ),
    "target_source_sha256": (
        "derive_from_supplied_stage6_float64_source_and_verify_against_report"
    ),
    "e025_module_sha256": ACCEPTED_E025_MODULE_SHA256,
    "e028_module_sha256": ACCEPTED_E028_MODULE_SHA256,
    "operator_order": list(CANONICAL_OPERATOR_NAMES),
    "generator": (
        "numpy.random.Generator(PCG64(260719)); four Rademacher then four "
        "standard_normal float64 vectors"
    ),
    "probe_vector_sha256": "derived_from_supplied_row_coordinates_at_execution",
    "dtype": "float64-little-endian",
    "endianness": "little",
    "signed_zero_policy": "preserve and compare uint64 bit patterns",
}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def implementation_provenance() -> dict[str, Any]:
    """Fingerprint the closure audit and imported frozen definitions."""

    repository_root = Path(__file__).resolve().parents[1]
    paths = {
        "e036_closure": Path(__file__).resolve(),
        "e035_preregistration": Path(e035.__file__).resolve(),
        "e034_transfer": Path(e034.__file__).resolve(),
        "e033_recovery": Path(e033.__file__).resolve(),
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
            "No checkpoint or field is read or written. Accepted E-028 stage "
            "6/12 remains immutable."
        ),
    }


def _coarse_nodes() -> Iterable[tuple[int, int]]:
    """Yield every strict quarter-disk node on the h=1/8 common lattice."""

    intervals = int(round(RADIAL_MAX / BASE_SPACING))
    radius_squared = intervals * intervals
    for radial_index in range(intervals):
        axial_max = math.isqrt(
            radius_squared - radial_index * radial_index - 1
        )
        for axial_index in range(axial_max + 1):
            yield radial_index, axial_index


def _mask_memberships(radial_index: int, axial_index: int) -> tuple[str, ...]:
    rho = radial_index * BASE_SPACING
    z = axial_index * BASE_SPACING
    radius_squared = rho * rho + z * z
    inside_angular_support = z < rho * math.tan(0.1)
    inside_radial_support = 25.0 < radius_squared < 1089.0
    memberships: list[str] = []
    if inside_radial_support and inside_angular_support:
        memberships.append("full_positive_source_support")
    if (
        inside_angular_support
        and (
            25.0 < radius_squared < 121.0
            or 729.0 < radius_squared < 1089.0
        )
    ):
        memberships.append("radial_transition")
    if inside_radial_support and 0.0 < z < rho * math.tan(0.1):
        memberships.append("angular_transition")
    if 4.0 <= rho <= 12.0 and 0.0 <= z <= 4.0:
        memberships.append("inner_feature_rectangle")
    if rho >= 0.5 and radius_squared <= 78.5**2:
        memberships.append("global_interior")
    return tuple(memberships)


def _support_valid_on_grid(
    radial_index: int,
    axial_index: int,
    spacing: float,
) -> bool:
    """Check the full reflected 5x5 support on one exactly mapped grid."""

    multiplier = int(round(BASE_SPACING / spacing))
    mapped_radial = radial_index * multiplier
    mapped_axial = axial_index * multiplier
    intervals = int(round(RADIAL_MAX / spacing))
    if mapped_radial - 2 < 0:
        return False
    # z<0 is defined by exact even reflection.  Since rho,z are nonnegative,
    # the (+2,+2) corner maximizes radius over the entire reflected 5x5 patch.
    return (
        (mapped_radial + 2) ** 2 + (mapped_axial + 2) ** 2
        < intervals**2
    )


@lru_cache(maxsize=1)
def enumerate_common_masks() -> dict[str, Any]:
    """Enumerate and hash every mask and validate every native support."""

    state = {
        name: {
            "count": 0,
            "digest": hashlib.sha256(),
            "radial_index_min": None,
            "radial_index_max": None,
            "axial_index_min": None,
            "axial_index_max": None,
            "quadrature_weight_sum": 0.0,
            "invalid_supports": {
                f"h={spacing:g},m={directional_radius}": 0
                for spacing, directional_radius in GRID_SPECIFICATIONS
            },
            "minimum_curved_boundary_clearance": {
                f"h={spacing:g},m={directional_radius}": math.inf
                for spacing, directional_radius in GRID_SPECIFICATIONS
            },
        }
        for name in MASK_NAMES
    }
    total_nodes = 0
    for radial_index, axial_index in _coarse_nodes():
        total_nodes += 1
        for name in _mask_memberships(radial_index, axial_index):
            entry = state[name]
            entry["count"] += 1
            entry["digest"].update(
                struct.pack("<II", radial_index, axial_index)
            )
            for key, value in (
                ("radial_index_min", radial_index),
                ("radial_index_max", radial_index),
                ("axial_index_min", axial_index),
                ("axial_index_max", axial_index),
            ):
                if entry[key] is None:
                    entry[key] = value
                elif key.endswith("_min"):
                    entry[key] = min(entry[key], value)
                else:
                    entry[key] = max(entry[key], value)
            rho = radial_index * BASE_SPACING
            reflection_weight = 0.5 if axial_index == 0 else 1.0
            entry["quadrature_weight_sum"] += (
                4.0
                * math.pi
                * BASE_SPACING**2
                * rho
                * reflection_weight
            )
            for spacing, directional_radius in GRID_SPECIFICATIONS:
                multiplier = int(round(BASE_SPACING / spacing))
                mapped_radial = radial_index * multiplier
                mapped_axial = axial_index * multiplier
                clearance = RADIAL_MAX - spacing * math.hypot(
                    mapped_radial + 2,
                    mapped_axial + 2,
                )
                grid_key = f"h={spacing:g},m={directional_radius}"
                entry["minimum_curved_boundary_clearance"][grid_key] = min(
                    entry["minimum_curved_boundary_clearance"][grid_key],
                    clearance,
                )
                if not _support_valid_on_grid(
                    radial_index, axial_index, spacing
                ):
                    entry["invalid_supports"][grid_key] += 1

    masks = {}
    for name, entry in state.items():
        masks[name] = {
            **{
                key: value
                for key, value in entry.items()
                if key != "digest"
            },
            "sha256_le_u32_index_pairs": entry["digest"].hexdigest(),
            "all_native_recovery_supports_valid": all(
                count == 0 for count in entry["invalid_supports"].values()
            ),
        }
    return {
        "design_status": "fully_enumerated_and_executable",
        "base_spacing": BASE_SPACING,
        "strict_quarter_disk_node_count": total_nodes,
        "restriction_multipliers": [
            int(round(BASE_SPACING / spacing))
            for spacing, _directional_radius in GRID_SPECIFICATIONS
        ],
        "negative_z_treatment": "exact_even_reflection_j_to_abs_j",
        "rho_axis_treatment": (
            "no fallback; a row is invalid unless its full radial support has i>=0"
        ),
        "curved_boundary_treatment": (
            "no fallback; every reflected 5x5 support node must satisfy rho^2+z^2<R^2"
        ),
        "quadrature": (
            "4*pi*h0^2*rho with half weight at z=0, evaluated once on the "
            "h0=0.125 restricted node set"
        ),
        "masks": masks,
    }


def _centered_weights(
    spacing: float,
    stride: int,
    rho0: float,
) -> np.ndarray:
    """Return radial/mixed/axial/azimuthal rows on a conceptual 5x5 patch."""

    if stride not in {1, 2}:
        raise ValueError("centered recovery stride must be 1 or 2")
    if spacing <= 0.0 or rho0 <= 2.0 * spacing:
        raise ValueError("invalid centered-recovery geometry")
    rows = np.zeros((4, 5, 5), dtype=float)
    center = 2
    step = stride * spacing
    rows[0, center + stride, center] = 1.0 / step**2
    rows[0, center, center] = -2.0 / step**2
    rows[0, center - stride, center] = 1.0 / step**2
    rows[2, center, center + stride] = 1.0 / step**2
    rows[2, center, center] = -2.0 / step**2
    rows[2, center, center - stride] = 1.0 / step**2
    mixed_scale = 1.0 / (4.0 * step**2)
    rows[1, center + stride, center + stride] = mixed_scale
    rows[1, center + stride, center - stride] = -mixed_scale
    rows[1, center - stride, center + stride] = -mixed_scale
    rows[1, center - stride, center - stride] = mixed_scale
    first_scale = 1.0 / (2.0 * step * rho0)
    rows[3, center + stride, center] = first_scale
    rows[3, center - stride, center] = -first_scale
    return rows.reshape(4, 25)


def _quadratic_weights(spacing: float, rho0: float) -> np.ndarray:
    """Return E-033's dimensionless 5x5 recovery scaled to support 2h."""

    recovery_length = 2.0 * spacing
    if spacing <= 0.0 or rho0 <= recovery_length:
        raise ValueError("invalid quadratic-recovery geometry")
    return np.vstack(
        (
            2.0 * e033.QUADRATIC_PSEUDOINVERSE[3] / recovery_length**2,
            e033.QUADRATIC_PSEUDOINVERSE[4] / recovery_length**2,
            2.0 * e033.QUADRATIC_PSEUDOINVERSE[5] / recovery_length**2,
            e033.QUADRATIC_PSEUDOINVERSE[1]
            / (recovery_length * rho0),
        )
    )


def recovery_weights(
    name: str,
    spacing: float,
    rho0: float,
) -> np.ndarray:
    if name == "C_h":
        return _centered_weights(spacing, 1, rho0)
    if name == "C_2h":
        return _centered_weights(spacing, 2, rho0)
    if name == "Q_2h":
        return _quadratic_weights(spacing, rho0)
    raise ValueError(f"unknown recovery family: {name}")


def reflected_patch_addresses(
    radial_index: int,
    axial_index: int,
) -> np.ndarray:
    """Return the native 5x5 addresses with exact even-z reflection."""

    if radial_index < 2 or axial_index < 0:
        raise ValueError("full radial support and nonnegative axial index required")
    return np.asarray(
        [
            (radial_index + radial_offset, abs(axial_index + axial_offset))
            for radial_offset in range(-2, 3)
            for axial_offset in range(-2, 3)
        ],
        dtype=np.int64,
    )


def coalesced_recovery_row(
    name: str,
    spacing: float,
    radial_index: int,
    axial_index: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Materialize and coalesce one reflected recovery row."""

    rho0 = radial_index * spacing
    addresses = reflected_patch_addresses(radial_index, axial_index)
    weights = recovery_weights(name, spacing, rho0)
    ordered_addresses: list[tuple[int, int]] = []
    columns: dict[tuple[int, int], np.ndarray] = {}
    for address, coefficient in zip(addresses, weights.T, strict=True):
        key = (int(address[0]), int(address[1]))
        if key not in columns:
            ordered_addresses.append(key)
            columns[key] = np.zeros(len(COMPONENT_NAMES), dtype=np.float64)
        columns[key] += coefficient
    retained = [
        key
        for key in ordered_addresses
        if np.any(columns[key].view(np.uint64) != np.float64(0.0).view(np.uint64))
    ]
    return (
        np.asarray(retained, dtype=np.int64),
        np.column_stack([columns[key] for key in retained]),
    )


def apply_coalesced_recovery(
    addresses: np.ndarray,
    coefficients: np.ndarray,
    field: np.ndarray,
) -> np.ndarray:
    """Apply a four-component coalesced row to a native meridional field."""

    if addresses.ndim != 2 or addresses.shape[1] != 2:
        raise ValueError("addresses must have shape (n,2)")
    if coefficients.shape != (len(COMPONENT_NAMES), len(addresses)):
        raise ValueError("coefficient shape does not match addresses")
    if np.any(addresses < 0):
        raise ValueError("reflected addresses must be nonnegative")
    if np.any(addresses[:, 0] >= field.shape[0]) or np.any(
        addresses[:, 1] >= field.shape[1]
    ):
        raise ValueError("recovery address is outside the supplied field")
    samples = field[addresses[:, 0], addresses[:, 1]]
    return coefficients @ samples


def _even_polynomial_field(
    spacing: float,
    radial_count: int,
    axial_count: int,
) -> tuple[
    np.ndarray,
    tuple[float, float, float, float],
    np.ndarray,
]:
    """Return an even-z field including a mixed component away from z=0."""

    constant, radial, radial_squared, axial_squared = (0.7, -0.3, 0.4, 0.6)
    rho = np.arange(radial_count, dtype=float)[:, None] * spacing
    z = np.arange(axial_count, dtype=float)[None, :] * spacing
    field = constant + radial * rho + radial_squared * rho**2 + axial_squared * z**2
    mixed_control = rho * z**2
    return field, (radial, radial_squared, axial_squared, constant), mixed_control


def reflected_axis_recovery_validation() -> dict[str, Any]:
    """Execute support, coalescing, and even-z recovery checks at z=0 and z=h."""

    rows = []
    maximum_error = 0.0
    maximum_mixed_cross_control_error = 0.0
    for spacing, directional_radius in GRID_SPECIFICATIONS:
        radial_index = int(round(8.75 / spacing))
        field, coefficients, mixed_control = _even_polynomial_field(
            spacing,
            radial_index + 4,
            5,
        )
        radial, radial_squared, axial_squared, _constant = coefficients
        rho0 = radial_index * spacing
        for axial_index in (0, 1):
            z0 = axial_index * spacing
            expected = np.asarray(
                (
                    2.0 * radial_squared,
                    0.0,
                    2.0 * axial_squared,
                    (radial + 2.0 * radial_squared * rho0) / rho0,
                )
            )
            for name in RECOVERY_NAMES:
                addresses, row_coefficients = coalesced_recovery_row(
                    name,
                    spacing,
                    radial_index,
                    axial_index,
                )
                recovered = apply_coalesced_recovery(
                    addresses,
                    row_coefficients,
                    field,
                )
                error = float(np.max(np.abs(recovered - expected)))
                maximum_error = max(maximum_error, error)
                mixed_cross_recovered = apply_coalesced_recovery(
                    addresses,
                    row_coefficients,
                    mixed_control,
                )[1]
                mixed_cross_error = float(
                    abs(mixed_cross_recovered - 2.0 * z0)
                )
                maximum_mixed_cross_control_error = max(
                    maximum_mixed_cross_control_error,
                    mixed_cross_error,
                )
                rows.append(
                    {
                        "spacing": spacing,
                        "directional_radius": directional_radius,
                        "axial_index": axial_index,
                        "recovery": name,
                        "coalesced_address_count": len(addresses),
                        "recovered_components": recovered.tolist(),
                        "expected_components": expected.tolist(),
                        "maximum_abs_error": error,
                        "mixed_rho_z2_control_recovered": float(
                            mixed_cross_recovered
                        ),
                        "mixed_rho_z2_control_expected": 2.0 * z0,
                        "mixed_rho_z2_control_abs_error": float(
                            mixed_cross_error
                        ),
                        "address_sha256": hashlib.sha256(
                            np.ascontiguousarray(addresses).view(np.uint8)
                        ).hexdigest(),
                        "coefficient_sha256": hashlib.sha256(
                            np.ascontiguousarray(row_coefficients).view(np.uint8)
                        ).hexdigest(),
                    }
                )
    return {
        "design_status": "executed_at_z0_and_z1_native_nodes",
        "rows": rows,
        "maximum_abs_error": maximum_error,
        "maximum_mixed_rho_z2_control_abs_error": (
            maximum_mixed_cross_control_error
        ),
        "passed": bool(
            maximum_error < 2.0e-11
            and maximum_mixed_cross_control_error < 2.0e-11
        ),
        "scope_limit": (
            "This validates reflected support addressing, duplicate coalescing, "
            "and recovery application on an even manufactured polynomial, "
            "including nonzero mixed recovery at z=h; "
            "it is not a boundary consistency theorem for the actual solution."
        ),
    }


def _quadratic_patch(
    spacing: float,
    rho0: float,
    z0: float,
) -> tuple[np.ndarray, np.ndarray]:
    coefficients = np.asarray((0.7, -0.3, 0.2, 0.4, -0.25, 0.6))
    values = []
    for radial_offset in range(-2, 3):
        for axial_offset in range(-2, 3):
            rho = rho0 + radial_offset * spacing
            z = z0 + axial_offset * spacing
            values.append(
                coefficients[0]
                + coefficients[1] * rho
                + coefficients[2] * z
                + coefficients[3] * rho**2
                + coefficients[4] * rho * z
                + coefficients[5] * z**2
            )
    expected = np.asarray(
        (
            2.0 * coefficients[3],
            coefficients[4],
            2.0 * coefficients[5],
            (
                coefficients[1]
                + 2.0 * coefficients[3] * rho0
                + coefficients[4] * z0
            )
            / rho0,
        )
    )
    return np.asarray(values), expected


def executable_recovery_definitions() -> dict[str, Any]:
    """Generate and validate every fixed native recovery family."""

    rho0 = 8.75
    z0 = 0.75
    rows = []
    normalized_reference: dict[str, np.ndarray] = {}
    for spacing, directional_radius in GRID_SPECIFICATIONS:
        patch, expected = _quadratic_patch(spacing, rho0, z0)
        for name in RECOVERY_NAMES:
            weights = recovery_weights(name, spacing, rho0)
            recovered = weights @ patch
            normalized = weights.copy()
            normalized[:3] *= spacing**2
            normalized[3] *= spacing * rho0
            if name not in normalized_reference:
                normalized_reference[name] = normalized
            scale_covariant = bool(
                np.allclose(
                    normalized,
                    normalized_reference[name],
                    rtol=0.0,
                    atol=(
                        FLOAT_SAFETY_MULTIPLIER
                        * np.finfo(float).eps
                        * max(1.0, float(np.max(np.abs(normalized))))
                    ),
                )
            )
            rows.append(
                {
                    "spacing": spacing,
                    "directional_radius": directional_radius,
                    "recovery": name,
                    "quadratic_reproduction_linf": float(
                        np.max(np.abs(recovered - expected))
                    ),
                    "row_l1_norms": [
                        float(np.sum(np.abs(row))) for row in weights
                    ],
                    "scale_covariant": scale_covariant,
                    "weight_sha256": hashlib.sha256(
                        np.ascontiguousarray(weights).view(np.uint8)
                    ).hexdigest(),
                }
            )
    maximum_error = max(row["quadratic_reproduction_linf"] for row in rows)
    reflected_axis = reflected_axis_recovery_validation()
    return {
        "design_status": "fully_generated_and_executable",
        "families": list(RECOVERY_NAMES),
        "components": list(COMPONENT_NAMES),
        "patch_order": (
            "radial offset outer loop -2..2; axial offset inner loop -2..2"
        ),
        "representative_validation_point": [rho0, z0],
        "quadratic_reproduction_linf_max": maximum_error,
        "quadratic_reproduction_passed": maximum_error < 2.0e-11,
        "scale_covariance_passed": all(row["scale_covariant"] for row in rows),
        "reflected_axis_validation": reflected_axis,
        "reflected_axis_validation_passed": reflected_axis["passed"],
        "rows": rows,
        "scope_limit": (
            "Manufactured reproduction and row scaling validate the recovery "
            "definitions only; they do not enclose the actual solution error."
        ),
    }


def matrix_difference_norms(
    component_differences: np.ndarray,
    quadrature_weights: np.ndarray,
) -> dict[str, Any]:
    """Evaluate the frozen weighted-L2 and Linf matrix/component norms."""

    components = np.asarray(component_differences, dtype=np.float64)
    weights = np.asarray(quadrature_weights, dtype=np.float64)
    if components.ndim != 2 or components.shape[1] != 4:
        raise ValueError("component differences must have shape (n,4)")
    if weights.shape != (len(components),) or np.any(weights <= 0.0):
        raise ValueError("quadrature weights must be positive with shape (n,)")
    if not np.all(np.isfinite(components)) or not np.all(np.isfinite(weights)):
        raise ValueError("norm inputs must be finite")
    matrices = np.zeros((len(components), 3, 3), dtype=np.float64)
    matrices[:, 0, 0] = components[:, 0]
    matrices[:, 0, 1] = components[:, 1]
    matrices[:, 1, 0] = components[:, 1]
    matrices[:, 1, 1] = components[:, 2]
    matrices[:, 2, 2] = components[:, 3]
    weight_sum = float(np.sum(weights))
    frobenius_squared = np.sum(matrices * matrices, axis=(1, 2))
    spectral = np.max(np.abs(np.linalg.eigvalsh(matrices)), axis=1)
    component_weighted_l2 = np.sqrt(
        np.sum(weights[:, None] * components**2, axis=0) / weight_sum
    )
    return {
        "matrix_weighted_l2": float(
            math.sqrt(float(np.sum(weights * frobenius_squared)) / weight_sum)
        ),
        "matrix_linf_spectral": float(np.max(spectral)),
        "component_weighted_l2": component_weighted_l2.tolist(),
        "component_linf": np.max(np.abs(components), axis=0).tolist(),
    }


def _flatten_matrix_norms(norms: dict[str, Any]) -> dict[str, float]:
    """Flatten one matrix/component norm report into the frozen metric keys."""

    flattened = {
        "matrix_weighted_l2": float(norms["matrix_weighted_l2"]),
        "matrix_linf_spectral": float(norms["matrix_linf_spectral"]),
    }
    for index, component in enumerate(COMPONENT_NAMES):
        flattened[f"component_{component}_weighted_l2"] = float(
            norms["component_weighted_l2"][index]
        )
    for index, component in enumerate(COMPONENT_NAMES):
        flattened[f"component_{component}_linf"] = float(
            norms["component_linf"][index]
        )
    if tuple(flattened) != PRIMARY_METRIC_NAMES:
        raise RuntimeError("primary metric construction drifted")
    return flattened


def same_grid_operator_spread(
    recovery_component_fields: np.ndarray,
    quadrature_weights: np.ndarray,
) -> dict[str, Any]:
    """Evaluate E-035's max pairwise C_h/C_2h/Q_2h spread on one mask."""

    fields = np.asarray(recovery_component_fields, dtype=np.float64)
    if fields.ndim != 3 or fields.shape[0] != len(RECOVERY_NAMES) or fields.shape[2] != 4:
        raise ValueError("recovery fields must have shape (3,n,4) in frozen recovery order")
    pair_reports: dict[str, dict[str, float]] = {}
    for first in range(len(RECOVERY_NAMES)):
        for second in range(first + 1, len(RECOVERY_NAMES)):
            name = f"{RECOVERY_NAMES[first]}__{RECOVERY_NAMES[second]}"
            pair_reports[name] = _flatten_matrix_norms(
                matrix_difference_norms(
                    fields[first] - fields[second],
                    quadrature_weights,
                )
            )
    spread = {
        metric: max(report[metric] for report in pair_reports.values())
        for metric in PRIMARY_METRIC_NAMES
    }
    return {
        "recovery_order": list(RECOVERY_NAMES),
        "pair_norms": pair_reports,
        "spread_by_metric": spread,
    }


def coupled_path_metrics(
    recovered_by_grid_and_operator: np.ndarray,
    quadrature_weights: np.ndarray,
) -> dict[str, Any]:
    """Compute every per-recovery D_j,p and same-grid A_j,p on one mask."""

    recovered = np.asarray(recovered_by_grid_and_operator, dtype=np.float64)
    if (
        recovered.ndim != 4
        or recovered.shape[0] != len(GRID_SPECIFICATIONS)
        or recovered.shape[1] != len(RECOVERY_NAMES)
        or recovered.shape[3] != len(COMPONENT_NAMES)
    ):
        raise ValueError("recovered data must have shape (3 grids,3 recoveries,n,4)")
    weights = np.asarray(quadrature_weights, dtype=np.float64)
    if weights.shape != (recovered.shape[2],):
        raise ValueError("quadrature weights must match the common mask")
    differences: dict[str, list[dict[str, float]]] = {}
    for recovery_index, recovery in enumerate(RECOVERY_NAMES):
        differences[recovery] = [
            _flatten_matrix_norms(
                matrix_difference_norms(
                    recovered[grid_index, recovery_index]
                    - recovered[grid_index + 1, recovery_index],
                    weights,
                )
            )
            for grid_index in range(2)
        ]
    spreads = [
        same_grid_operator_spread(recovered[grid_index], weights)[
            "spread_by_metric"
        ]
        for grid_index in range(3)
    ]
    return {
        "grid_order": [list(specification) for specification in GRID_SPECIFICATIONS],
        "recovery_order": list(RECOVERY_NAMES),
        "nested_differences_by_recovery": differences,
        "same_grid_operator_spreads": spreads,
    }


def coupled_path_screen_gate(
    metrics_by_mask: dict[str, dict[str, Any]],
    orientation_pass_by_key: dict[str, bool],
    *,
    solution_schedule: str,
    verified_root_error_enclosure: bool,
) -> dict[str, Any]:
    """Execute all-recovery q_p and operator-spread gates without postselection."""

    if tuple(metrics_by_mask) != MASK_NAMES:
        raise ValueError("metrics must cover all five frozen masks in order")
    if tuple(orientation_pass_by_key) != FIXED_ORIENTATION_KEYS:
        raise ValueError("orientation results must cover every frozen point/component in order")
    q_by_key: dict[str, float] = {}
    difference_checks: dict[str, bool] = {}
    spread_checks: dict[str, bool] = {}
    for mask in MASK_NAMES:
        metrics = metrics_by_mask[mask]
        if metrics.get("grid_order") != [
            list(specification) for specification in GRID_SPECIFICATIONS
        ] or metrics.get("recovery_order") != list(RECOVERY_NAMES):
            raise ValueError("coupled metrics use the wrong grid or recovery order")
        differences = metrics.get("nested_differences_by_recovery", {})
        spreads = metrics.get("same_grid_operator_spreads", [])
        if tuple(differences) != RECOVERY_NAMES or len(spreads) != 3:
            raise ValueError("coupled metrics are incomplete")
        for recovery in RECOVERY_NAMES:
            rows = differences[recovery]
            if len(rows) != 2 or any(tuple(row) != PRIMARY_METRIC_NAMES for row in rows):
                raise ValueError("nested-difference metric keys are incomplete or reordered")
            for metric in PRIMARY_METRIC_NAMES:
                first = float(rows[0][metric])
                second = float(rows[1][metric])
                key = f"{mask}:{recovery}:{metric}"
                valid = (
                    math.isfinite(first)
                    and math.isfinite(second)
                    and first > 0.0
                    and second > 0.0
                    and second < first
                )
                q = math.log2(first / second) if valid else math.nan
                q_by_key[key] = q
                difference_checks[key] = valid and math.isfinite(q) and q > 0.0
        if any(tuple(row) != PRIMARY_METRIC_NAMES for row in spreads):
            raise ValueError("operator-spread metric keys are incomplete or reordered")
        for metric in PRIMARY_METRIC_NAMES:
            values = [float(row[metric]) for row in spreads]
            key = f"{mask}:{metric}"
            spread_checks[key] = (
                all(math.isfinite(value) and value >= 0.0 for value in values)
                and values[2] < values[1] < values[0]
            )
    if tuple(q_by_key) != COUPLED_Q_KEYS or tuple(spread_checks) != OPERATOR_SPREAD_KEYS:
        raise RuntimeError("coupled-path exhaustive key construction drifted")
    orientation_complete = all(
        type(orientation_pass_by_key[key]) is bool
        for key in FIXED_ORIENTATION_KEYS
    )
    orientation_passed = orientation_complete and all(
        orientation_pass_by_key[key] for key in FIXED_ORIENTATION_KEYS
    )
    primary_q_keys = tuple(
        f"{mask}:{recovery}:{metric}"
        for mask in PRIMARY_ACCEPTANCE_MASK_NAMES
        for recovery in RECOVERY_NAMES
        for metric in PRIMARY_METRIC_NAMES
    )
    primary_spread_keys = tuple(
        f"{mask}:{metric}"
        for mask in PRIMARY_ACCEPTANCE_MASK_NAMES
        for metric in PRIMARY_METRIC_NAMES
    )
    primary_differences_passed = all(difference_checks[key] for key in primary_q_keys)
    primary_spreads_passed = all(spread_checks[key] for key in primary_spread_keys)
    schedule_passed = solution_schedule == "tight_2"
    root_passed = verified_root_error_enclosure is True
    return {
        "q_by_mask_recovery_metric": q_by_key,
        "difference_checks": difference_checks,
        "operator_spread_checks": spread_checks,
        "acceptance_masks": list(PRIMARY_ACCEPTANCE_MASK_NAMES),
        "report_only_masks": [
            mask for mask in MASK_NAMES if mask not in PRIMARY_ACCEPTANCE_MASK_NAMES
        ],
        "all_recoveries_difference_contraction_passed": primary_differences_passed,
        "operator_spread_contraction_passed": primary_spreads_passed,
        "orientation_coverage_passed": orientation_complete,
        "orientation_passed": orientation_passed,
        "most_tightly_solved_schedule_used": schedule_passed,
        "verified_root_error_enclosure_present": root_passed,
        "necessary_conditions_passed": (
            primary_differences_passed
            and primary_spreads_passed
            and orientation_passed
            and schedule_passed
        ),
        "screen_authorized": (
            primary_differences_passed
            and primary_spreads_passed
            and orientation_passed
            and schedule_passed
            and root_passed
        ),
        "interpretation": (
            "A necessary-condition pass is not spatial order, Richardson "
            "extrapolation, GCI, an error theorem, or authorization without a "
            "verified root enclosure."
        ),
    }


def solver_separation_gate(
    grid_difference: float,
    standard_to_tight1: tuple[float, float],
    tight1_to_tight2: tuple[float, float],
) -> dict[str, Any]:
    """Evaluate the two-grid, three-schedule output-sensitivity gate."""

    if grid_difference <= 0.0:
        raise ValueError("grid difference must be positive")
    first = np.asarray(standard_to_tight1, dtype=np.float64)
    second = np.asarray(tight1_to_tight2, dtype=np.float64)
    if first.shape != (2,) or second.shape != (2,) or np.any(first < 0.0) or np.any(second < 0.0):
        raise ValueError("replay differences must be two nonnegative values")
    separation = np.maximum(first, second)
    ratio = float(np.sum(separation) / grid_difference)
    decreasing = bool(np.all(second < first))
    return {
        "separation_by_grid": separation.tolist(),
        "separation_to_grid_difference": ratio,
        "replay_differences_strictly_decrease": decreasing,
        "passed": decreasing and ratio <= 0.01,
    }


def orientation_interval_gate(
    nested_differences: tuple[float, float],
    per_grid_verified_error_radii: tuple[float, float, float],
    per_grid_row_l1_norms: tuple[float, float, float],
    per_grid_field_linf_values: tuple[float, float, float],
    *,
    component: str,
    axial_index: int,
) -> dict[str, Any]:
    """Evaluate signed orientation with the declared arithmetic floor."""

    if component not in COMPONENT_NAMES or axial_index < 0:
        raise ValueError("orientation component/axial index is outside the frozen scheme")
    differences = np.asarray(nested_differences, dtype=np.float64)
    radii = np.asarray(per_grid_verified_error_radii, dtype=np.float64)
    row_norms = np.asarray(per_grid_row_l1_norms, dtype=np.float64)
    field_norms = np.asarray(per_grid_field_linf_values, dtype=np.float64)
    if (
        differences.shape != (2,)
        or radii.shape != (3,)
        or row_norms.shape != (3,)
        or field_norms.shape != (3,)
        or np.any(radii < 0.0)
        or np.any(row_norms < 0.0)
        or np.any(field_norms < 0.0)
        or not np.all(np.isfinite(differences))
        or not np.all(np.isfinite(radii))
        or not np.all(np.isfinite(row_norms))
        or not np.all(np.isfinite(field_norms))
    ):
        raise ValueError("orientation inputs must be finite nonnegative two-value bounds")
    floating_floors = (
        FLOAT_SAFETY_MULTIPLIER
        * np.finfo(np.float64).eps
        * np.maximum(1.0, row_norms * field_norms)
    )
    total_radii = np.asarray(
        (
            radii[0] + radii[1] + floating_floors[0] + floating_floors[1],
            radii[1] + radii[2] + floating_floors[1] + floating_floors[2],
        )
    )
    intervals = np.column_stack(
        (differences - total_radii, differences + total_radii)
    )
    excludes_zero = np.logical_or(intervals[:, 1] < 0.0, intervals[:, 0] > 0.0)
    same_sign = bool(np.sign(differences[0]) == np.sign(differences[1]))
    symmetry_zero = component == "mixed" and axial_index == 0
    symmetry_difference_floors = np.asarray(
        (
            floating_floors[0] + floating_floors[1],
            floating_floors[1] + floating_floors[2],
        )
    )
    symmetry_resolved = bool(
        symmetry_zero
        and np.all(np.abs(differences) <= symmetry_difference_floors)
    )
    passed = bool(
        symmetry_resolved
        or (not symmetry_zero and np.all(excludes_zero) and same_sign)
    )
    return {
        "intervals": intervals.tolist(),
        "floating_floors": floating_floors.tolist(),
        "symmetry_difference_floors": symmetry_difference_floors.tolist(),
        "total_error_radii": total_radii.tolist(),
        "zero_excluded": excludes_zero.tolist(),
        "same_sign": same_sign,
        "symmetry_zero_whitelisted": symmetry_zero,
        "symmetry_zero_resolved_within_floating_floor": symmetry_resolved,
        "passed": passed,
    }


def eigengap_gate(
    measured_gaps: np.ndarray,
    verified_matrix_error_radii: np.ndarray,
) -> dict[str, Any]:
    """Evaluate the strict Weyl eigengap-resolution gate pointwise."""

    gaps = np.asarray(measured_gaps, dtype=np.float64)
    radii = np.asarray(verified_matrix_error_radii, dtype=np.float64)
    if gaps.shape != radii.shape or gaps.size == 0 or np.any(radii < 0.0):
        raise ValueError("eigengaps and error radii must share a nonempty shape")
    resolved = gaps > 2.0 * radii
    return {
        "resolved": resolved.tolist(),
        "minimum_gap_to_twice_error_ratio": float(
            np.min(np.divide(gaps, 2.0 * radii, out=np.full_like(gaps, math.inf), where=radii > 0.0))
        ),
        "passed": bool(np.all(resolved)),
    }


@lru_cache(maxsize=1)
def frozen_transfer_cutoffs() -> dict[str, float]:
    """Return E-034's exact 90-percent origin-square cutoffs by recovery/component."""

    rows = e034.resolution_map()["rows"]
    lookup = {
        (row["postprocessor"], row["component"]): float(
            row["ten_percent_relative_amplitude"]["theta_cutoff"]
        )
        for row in rows
    }
    result = {
        f"{recovery}:{component}": lookup[
            (RECOVERY_TO_E034_POSTPROCESSOR[recovery], component)
        ]
        for recovery in RECOVERY_NAMES
        for component in COMPONENT_NAMES
    }
    if len(result) != len(RECOVERY_NAMES) * len(COMPONENT_NAMES):
        raise RuntimeError("frozen transfer cutoff construction is incomplete")
    return result


def transfer_tile(
    component_field: np.ndarray,
    center_ij: tuple[int, int],
    spacing: float,
    component: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Materialize the exact half-open 4x4 tile with component parity at z=0."""

    field = np.asarray(component_field, dtype=np.float64)
    if (
        field.ndim != 2
        or component not in COMPONENT_NAMES
        or not np.all(np.isfinite(field))
    ):
        raise ValueError("component field must be 2D with a frozen component name")
    if spacing not in tuple(value for value, _radius in GRID_SPECIFICATIONS):
        raise ValueError("tile spacing must be one of the frozen candidate grids")
    tile_count_float = 4.0 / spacing
    tile_count = int(round(tile_count_float))
    if not math.isclose(tile_count_float, tile_count, rel_tol=0.0, abs_tol=1.0e-12) or tile_count % 2:
        raise ValueError("the physical tile must have an even integer sample count")
    center_i, center_j = center_ij
    offsets = np.arange(-tile_count // 2, tile_count // 2, dtype=np.int64)
    radial_indices = center_i + offsets
    signed_axial_indices = center_j + offsets
    axial_indices = np.abs(signed_axial_indices)
    if (
        center_i < 0
        or center_j < 0
        or np.any(radial_indices <= 0)
        or np.any(radial_indices >= field.shape[0])
        or np.any(axial_indices >= field.shape[1])
    ):
        raise ValueError("the full half-open tile must exist and exclude rho=0")
    tile = field[np.ix_(radial_indices, axial_indices)].copy()
    if component == "mixed":
        signs = np.sign(signed_axial_indices).astype(np.float64)
        tile *= signs[None, :]
    rho = radial_indices.astype(np.float64) * spacing
    weights = np.broadcast_to(
        (2.0 * math.pi * spacing**2 * rho)[:, None],
        tile.shape,
    ).copy()
    return tile, weights


def frozen_outside_origin_band(
    shape: tuple[int, int],
    *,
    spacing: float,
    recovery: str,
    component: str,
) -> tuple[np.ndarray, float]:
    """Construct the non-adjustable FFT outside-band mask from E-034."""

    expected_count = int(round(4.0 / spacing))
    if (
        spacing not in tuple(value for value, _radius in GRID_SPECIFICATIONS)
        or shape != (expected_count, expected_count)
    ):
        raise ValueError("transfer tile shape must be the frozen half-open 4x4 physical tile")
    key = f"{recovery}:{component}"
    if key not in frozen_transfer_cutoffs():
        raise ValueError("unknown frozen recovery/component transfer band")
    cutoff = frozen_transfer_cutoffs()[key]
    theta_rho = 2.0 * math.pi * np.fft.fftfreq(shape[0])
    theta_z = 2.0 * math.pi * np.fft.fftfreq(shape[1])
    radial, axial = np.meshgrid(theta_rho, theta_z, indexing="ij")
    outside = np.logical_or(np.abs(radial) > cutoff, np.abs(axial) > cutoff)
    return outside, cutoff


def transfer_parity_metrics(
    values: np.ndarray,
    quadrature_weights: np.ndarray,
    *,
    spacing: float,
    recovery: str,
    component: str,
    detrend: str,
) -> dict[str, Any]:
    """Compute the frozen detrended FFT and three parity diagnostics."""

    field = np.asarray(values, dtype=np.float64)
    weights = np.asarray(quadrature_weights, dtype=np.float64)
    if field.ndim != 2 or min(field.shape) < 4:
        raise ValueError("transfer tile must be a two-dimensional array at least 4x4")
    if (
        weights.shape != field.shape
        or np.any(weights <= 0.0)
        or not np.all(np.isfinite(field))
        or not np.all(np.isfinite(weights))
    ):
        raise ValueError("positive weights must match the tile")
    if detrend not in {"affine", "constant"}:
        raise ValueError("detrend must be affine or constant")
    expected_detrend = "constant" if component == "azimuthal" else "affine"
    if detrend != expected_detrend:
        raise ValueError("detrend does not match the frozen component rule")
    outside, cutoff = frozen_outside_origin_band(
        field.shape,
        spacing=spacing,
        recovery=recovery,
        component=component,
    )
    ii, jj = np.indices(field.shape, dtype=np.float64)
    columns = [np.ones(field.size)]
    if detrend == "affine":
        columns.extend((ii.ravel(), jj.ravel()))
    design = np.column_stack(columns)
    root_weights = np.sqrt(weights.ravel())
    coefficients, *_unused = np.linalg.lstsq(
        design * root_weights[:, None],
        field.ravel() * root_weights,
        rcond=None,
    )
    residual = field - (design @ coefficients).reshape(field.shape)
    hann_i = 0.5 - 0.5 * np.cos(2.0 * math.pi * np.arange(field.shape[0]) / field.shape[0])
    hann_j = 0.5 - 0.5 * np.cos(2.0 * math.pi * np.arange(field.shape[1]) / field.shape[1])
    window = np.outer(hann_i, hann_j)
    window /= math.sqrt(float(np.mean(window**2)))
    spectrum = np.fft.fft2(residual * window, norm="ortho")
    total_rms = math.sqrt(float(np.sum(weights * residual**2) / np.sum(weights)))
    spectral_energy = np.abs(spectrum) ** 2
    total_spectral_energy = float(np.sum(spectral_energy))
    outside_spectral_energy = float(np.sum(spectral_energy[outside]))
    outside_rms = math.sqrt(outside_spectral_energy / field.size)
    windowed_total_rms = math.sqrt(total_spectral_energy / field.size)
    outside_energy_fraction = (
        outside_spectral_energy / total_spectral_energy
        if total_spectral_energy > 0.0
        else 0.0
    )
    floating_floor = (
        FLOAT_SAFETY_MULTIPLIER
        * np.finfo(np.float64).eps
        * max(1.0, float(np.max(np.abs(field))))
    )
    parity_amplitudes = {}
    parity_correlations = {}
    parity_below_floor = {}
    for name, basis in (
        ("radial", (-1.0) ** ii),
        ("axial", (-1.0) ** jj),
        ("checkerboard", (-1.0) ** (ii + jj)),
    ):
        numerator = float(abs(np.sum(weights * residual * basis)))
        amplitude = numerator / float(np.sum(weights))
        denominator = math.sqrt(
            float(np.sum(weights * residual**2) * np.sum(weights * basis**2))
        )
        parity_amplitudes[name] = amplitude
        parity_below_floor[name] = amplitude <= floating_floor
        parity_correlations[name] = numerator / denominator if denominator > 0.0 else 0.0
    return {
        "recovery": recovery,
        "component": component,
        "origin_square_theta_cutoff": cutoff,
        "outside_band_mask_sha256": hashlib.sha256(
            np.ascontiguousarray(outside).view(np.uint8)
        ).hexdigest(),
        "total_component_rms": total_rms,
        "windowed_total_rms": windowed_total_rms,
        "outside_band_rms": outside_rms,
        "outside_band_energy_fraction": outside_energy_fraction,
        "parseval_relative_error": abs(
            total_spectral_energy - float(np.sum((residual * window) ** 2))
        )
        / max(total_spectral_energy, np.finfo(np.float64).tiny),
        "floating_floor": floating_floor,
        "parity_amplitudes": parity_amplitudes,
        "parity_normalized_correlations": parity_correlations,
        "parity_below_floating_floor": parity_below_floor,
    }


def transfer_parity_gate(
    metrics_by_grid: list[dict[str, Any]],
    fine_grid_difference_rms: float,
) -> dict[str, Any]:
    """Evaluate strict double contraction and absolute finest-grid caps."""

    if len(metrics_by_grid) != 3 or fine_grid_difference_rms <= 0.0:
        raise ValueError("three grid metrics and a positive fine difference are required")
    identities = [
        (row.get("recovery"), row.get("component"), row.get("origin_square_theta_cutoff"))
        for row in metrics_by_grid
    ]
    if any(identity != identities[0] for identity in identities[1:]):
        raise ValueError("all grid metrics must use one frozen recovery/component band")
    if identities[0][0] not in RECOVERY_NAMES or identities[0][1] not in COMPONENT_NAMES:
        raise ValueError("grid metrics lack a frozen recovery/component identity")
    parseval_passed = all(
        float(row.get("parseval_relative_error", math.inf)) <= 1.0e-12
        for row in metrics_by_grid
    )
    outside = np.asarray([row["outside_band_rms"] for row in metrics_by_grid])
    outside_fractions = np.asarray(
        [row["outside_band_energy_fraction"] for row in metrics_by_grid]
    )
    floors = np.asarray([row["floating_floor"] for row in metrics_by_grid])
    parity_names = ("radial", "axial", "checkerboard")
    parity_amplitudes = {
        name: np.asarray([row["parity_amplitudes"][name] for row in metrics_by_grid])
        for name in parity_names
    }
    parity_correlations = {
        name: np.asarray(
            [row["parity_normalized_correlations"][name] for row in metrics_by_grid]
        )
        for name in parity_names
    }
    outside_contraction = bool(
        outside[2] < outside[1] < outside[0]
        or np.all(outside <= floors)
    )
    fraction_contraction = bool(
        outside_fractions[2] < outside_fractions[1] < outside_fractions[0]
        or np.all(outside <= floors)
    )
    parity_contraction = all(
        (
            values[2] < values[1] < values[0]
            or np.all(parity_amplitudes[name] <= floors)
        )
        for name, values in parity_correlations.items()
    )
    finest_caps = bool(
        outside_fractions[2] <= TRANSFER_FRACTION_CAP
        and outside[2] <= ABSOLUTE_TO_FINE_DIFFERENCE_CAP * fine_grid_difference_rms
        and all(
            parity_correlations[name][2] <= PARITY_FRACTION_CAP
            and parity_amplitudes[name][2]
            <= ABSOLUTE_TO_FINE_DIFFERENCE_CAP * fine_grid_difference_rms
            for name in parity_names
        )
    )
    return {
        "outside_rms_double_contraction": outside_contraction,
        "outside_energy_fraction_double_contraction": fraction_contraction,
        "parity_correlation_double_contraction_or_below_floor": parity_contraction,
        "finest_absolute_caps_passed": finest_caps,
        "parseval_passed": parseval_passed,
        "passed": (
            outside_contraction
            and fraction_contraction
            and parity_contraction
            and finest_caps
            and parseval_passed
        ),
    }


def required_equivalence_vectors(
    radial_indices: np.ndarray,
    axial_indices: np.ndarray,
) -> dict[str, np.ndarray]:
    """Generate every frozen baseline row-action probe in exact order."""

    radial_index = np.asarray(radial_indices, dtype=np.int64)
    axial_index = np.asarray(axial_indices, dtype=np.int64)
    if (
        radial_index.ndim != 1
        or axial_index.shape != radial_index.shape
        or radial_index.size == 0
        or np.any(radial_index < 0)
        or np.any(axial_index < 0)
    ):
        raise ValueError("row probe indices must be equal nonempty nonnegative vectors")
    rho = radial_index.astype(np.float64) * BASE_SPACING
    z = axial_index.astype(np.float64) * BASE_SPACING
    vectors: dict[str, np.ndarray] = {
        "zero": np.zeros_like(rho),
        "one": np.ones_like(rho),
        "rho": rho,
        "z": z,
        "rho2": rho**2,
        "rho_z": rho * z,
        "z2": z**2,
        "normalized_rho4_plus_z4": (rho / RADIAL_MAX) ** 4
        + (z / RADIAL_MAX) ** 4,
        "normalized_rho2_z2": (rho * z / RADIAL_MAX**2) ** 2,
    }
    for index, (first, second) in enumerate(BASELINE_ORDERED_MERIDIONAL_STEPS):
        phase = 2.0 * math.pi * (
            first * radial_index.astype(np.float64)
            + second * axial_index.astype(np.float64)
        ) / 17.0
        vectors[f"operator_wave_cos_{index:02d}_{first}_{second}"] = np.cos(phase)
        vectors[f"operator_wave_sin_{index:02d}_{first}_{second}"] = np.sin(phase)
    generator = np.random.Generator(np.random.PCG64(260719))
    for index in range(4):
        draws = generator.integers(0, 2, size=radial_index.size, dtype=np.int8)
        vectors[f"rademacher_seed_260719_{index}"] = (
            2.0 * draws.astype(np.float64) - 1.0
        )
    for index in range(4):
        vectors[f"gaussian_seed_260719_{index}"] = generator.standard_normal(
            radial_index.size,
            dtype=np.float64,
        )
    if tuple(vectors) != REQUIRED_ROW_ACTION_NAMES:
        raise RuntimeError("equivalence-vector generation order drifted")
    return vectors


def equivalence_vector_hashes(
    vectors: dict[str, np.ndarray],
) -> dict[str, str]:
    """Hash every probe with dtype/shape/content bound in frozen order."""

    if tuple(vectors) != REQUIRED_ROW_ACTION_NAMES:
        raise ValueError("equivalence vectors are incomplete or reordered")
    result = {}
    for name, value in vectors.items():
        digest = hashlib.sha256()
        _update_snapshot_digest(digest, np.asarray(value))
        result[name] = digest.hexdigest()
    return result


def _update_snapshot_digest(digest: Any, value: Any) -> None:
    """Hash nested snapshots with dtype, shape, order, and signed zeros bound."""

    if isinstance(value, np.ndarray):
        array = np.ascontiguousarray(value)
        digest.update(b"array\0")
        digest.update(array.dtype.str.encode("ascii") + b"\0")
        digest.update(json.dumps(array.shape).encode("ascii") + b"\0")
        digest.update(array.tobytes())
    elif isinstance(value, dict):
        digest.update(b"dict\0")
        for key, item in value.items():
            digest.update(str(key).encode("utf-8") + b"\0")
            _update_snapshot_digest(digest, item)
    elif isinstance(value, (list, tuple)):
        digest.update(b"sequence\0")
        for item in value:
            _update_snapshot_digest(digest, item)
    else:
        digest.update(b"scalar\0")
        digest.update(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        digest.update(b"\0")


def snapshot_fingerprint(snapshot: dict[str, Any]) -> str:
    """Recompute a content fingerprint; no supplied digest is trusted."""

    digest = hashlib.sha256()
    _update_snapshot_digest(digest, snapshot)
    return digest.hexdigest()


def _require_exact_array(
    value: Any,
    dtype: str,
    ndim: int,
    label: str,
) -> np.ndarray:
    """Require canonical little-endian, C-contiguous artifact storage."""

    array = np.asarray(value)
    expected_dtype = np.dtype(dtype)
    if array.dtype != expected_dtype or array.ndim != ndim:
        raise ValueError(
            f"{label} must have dtype {expected_dtype.str} and ndim {ndim}"
        )
    if not array.flags.c_contiguous:
        raise ValueError(f"{label} must be C-contiguous")
    return array


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(
        character not in "0123456789abcdef" for character in value
    ):
        raise ValueError(f"{label} must be a lowercase SHA-256")
    return value


def _payload_sha256(value: Any, label: str) -> str:
    if not isinstance(value, (bytes, bytearray, memoryview)):
        raise TypeError(f"{label} must be supplied as bytes")
    return hashlib.sha256(value).hexdigest()


def _float64_array_sha256(value: np.ndarray) -> str:
    array = np.ascontiguousarray(np.asarray(value, dtype=np.float64))
    return hashlib.sha256(array.view(np.uint8)).hexdigest()


def _canonical_report_sha256(report: dict[str, Any]) -> str:
    try:
        payload = json.dumps(
            report,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ValueError("stage-6 report must be finite canonical JSON") from error
    return hashlib.sha256(payload).hexdigest()


def _array_fingerprint_record(value: np.ndarray) -> dict[str, Any]:
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    _update_snapshot_digest(digest, array)
    return {
        "dtype": array.dtype.str,
        "shape": list(array.shape),
        "sha256": digest.hexdigest(),
    }


def _validated_system_artifact(
    system: dict[str, Any],
    *,
    expected_size: int,
    expected_index_map_shape: tuple[int, int],
) -> tuple[dict[str, Any], dict[str, sparse.csr_matrix], int]:
    """Validate exact baseline metadata and every canonical CSR invariant."""

    if not isinstance(system, dict) or set(system) != set(
        REQUIRED_SYSTEM_ARTIFACT_FIELDS
    ):
        raise ValueError("system artifact fields are incomplete")
    radial_max = float(system["radial_max"])
    spacing = float(system["spacing"])
    directional_radius = int(system["directional_radius"])
    cubic_coefficient = float(system["cubic_coefficient"])
    bases = tuple(tuple(int(component) for component in basis) for basis in system["bases"])
    if (
        radial_max != RADIAL_MAX
        or spacing != BASE_SPACING
        or directional_radius != e035.BASELINE_DIRECTIONAL_RADIUS
        or bases != BASELINE_DIRECTIONAL_BASES
        or not math.isfinite(cubic_coefficient)
        or cubic_coefficient <= 0.0
    ):
        raise ValueError("system artifact is not the frozen h=0.125,m=4 discretization")

    rho = _require_exact_array(system["rho"], "<f8", 1, "rho")
    z = _require_exact_array(system["z"], "<f8", 1, "z")
    index_map = _require_exact_array(system["index_map"], "<i8", 2, "index_map")
    if rho.shape != z.shape or rho.size == 0:
        raise ValueError("rho and z must be equal nonempty coordinate vectors")
    if rho.size != expected_size or index_map.shape != expected_index_map_shape:
        raise ValueError("system artifact does not have the required baseline geometry")
    if not np.all(np.isfinite(rho)) or not np.all(np.isfinite(z)):
        raise ValueError("system coordinates must be finite")
    if np.any(index_map < -1):
        raise ValueError("index_map entries below -1 are invalid")
    mapped = index_map[index_map >= 0]
    size = int(rho.size)
    if mapped.size != size or not np.array_equal(
        np.sort(mapped), np.arange(size, dtype=np.int64)
    ):
        raise ValueError("index_map must contain every unknown exactly once")
    locations = np.argwhere(index_map >= 0)
    assigned = index_map[index_map >= 0]
    expected_rho = np.empty(size, dtype=np.float64)
    expected_z = np.empty(size, dtype=np.float64)
    expected_rho[assigned] = locations[:, 0].astype(np.float64) * spacing
    expected_z[assigned] = locations[:, 1].astype(np.float64) * spacing
    if not np.array_equal(rho, expected_rho) or not np.array_equal(z, expected_z):
        raise ValueError("rho/z coordinates do not agree exactly with index_map")

    operators = system["operators"]
    boundary_offsets = system["boundary_offsets"]
    if not isinstance(operators, dict) or tuple(operators) != CANONICAL_OPERATOR_NAMES:
        raise ValueError("operator artifact must use the canonical E-025 order")
    if not isinstance(boundary_offsets, dict) or tuple(
        boundary_offsets
    ) != CANONICAL_OPERATOR_NAMES:
        raise ValueError("boundary offsets must use the canonical E-025 order")
    canonical_operators: dict[str, dict[str, np.ndarray]] = {}
    matrices: dict[str, sparse.csr_matrix] = {}
    canonical_offsets: dict[str, np.ndarray] = {}
    for name in CANONICAL_OPERATOR_NAMES:
        operator = operators[name]
        if not isinstance(operator, dict) or tuple(operator) != (
            "indptr",
            "indices",
            "data",
        ):
            raise ValueError(f"operator {name} lacks ordered canonical CSR arrays")
        indptr = _require_exact_array(
            operator["indptr"], "<i8", 1, f"{name}.indptr"
        )
        indices = _require_exact_array(
            operator["indices"], "<i8", 1, f"{name}.indices"
        )
        data = _require_exact_array(operator["data"], "<f8", 1, f"{name}.data")
        offset = _require_exact_array(
            boundary_offsets[name], "<f8", 1, f"{name}.boundary_offset"
        )
        if indptr.shape != (size + 1,) or indptr[0] != 0:
            raise ValueError(f"operator {name} has an invalid CSR indptr")
        if np.any(np.diff(indptr) < 0) or int(indptr[-1]) != indices.size:
            raise ValueError(f"operator {name} has inconsistent CSR row pointers")
        if data.shape != indices.shape or offset.shape != (size,):
            raise ValueError(f"operator {name} arrays do not match the system size")
        if np.any(indices < 0) or np.any(indices >= size):
            raise ValueError(f"operator {name} contains an out-of-range column")
        if not np.all(np.isfinite(data)) or not np.all(np.isfinite(offset)):
            raise ValueError(f"operator {name} contains non-finite coefficients")
        for start, stop in zip(indptr[:-1], indptr[1:]):
            row_indices = indices[int(start) : int(stop)]
            if row_indices.size > 1 and np.any(np.diff(row_indices) <= 0):
                raise ValueError(
                    f"operator {name} CSR rows must be sorted and coalesced"
                )
        matrix = sparse.csr_matrix(
            (data, indices, indptr),
            shape=(size, size),
            copy=False,
        )
        if not matrix.has_canonical_format:
            raise ValueError(f"operator {name} is not canonical CSR")
        canonical_operators[name] = {
            "indptr": indptr,
            "indices": indices,
            "data": data,
        }
        matrices[name] = matrix
        canonical_offsets[name] = offset
    return (
        {
            "radial_max": radial_max,
            "spacing": spacing,
            "directional_radius": directional_radius,
            "cubic_coefficient": cubic_coefficient,
            "bases": bases,
            "rho": rho,
            "z": z,
            "index_map": index_map,
            "operators": canonical_operators,
            "boundary_offsets": canonical_offsets,
        },
        matrices,
        size,
    )


def _e025_compatible_system_sha256(system: dict[str, Any]) -> str:
    """Reproduce E-025's system digest from already validated arrays."""

    digest = hashlib.sha256()

    def update_array(label: str, values: np.ndarray, dtype: str) -> None:
        array = np.ascontiguousarray(np.asarray(values, dtype=np.dtype(dtype)))
        digest.update(label.encode("utf-8"))
        digest.update(json.dumps(array.shape).encode("ascii"))
        digest.update(array.tobytes())

    digest.update(
        json.dumps(
            {
                "radial_max": system["radial_max"],
                "spacing": system["spacing"],
                "directional_radius": system["directional_radius"],
                "cubic_coefficient": system["cubic_coefficient"],
                "bases": system["bases"],
            },
            sort_keys=True,
        ).encode("ascii")
    )
    update_array("rho", system["rho"], "<f8")
    update_array("z", system["z"], "<f8")
    update_array("index_map", system["index_map"], "<i8")
    for index, name in enumerate(CANONICAL_OPERATOR_NAMES):
        operator = system["operators"][name]
        update_array(f"operator-{index}-indptr", operator["indptr"], "<i8")
        update_array(f"operator-{index}-indices", operator["indices"], "<i8")
        update_array(f"operator-{index}-data", operator["data"], "<f8")
        update_array(
            f"operator-{index}-boundary",
            system["boundary_offsets"][name],
            "<f8",
        )
    return digest.hexdigest()


def _derived_row_action_records(
    matrices: dict[str, sparse.csr_matrix],
    offsets: dict[str, np.ndarray],
    vectors: dict[str, np.ndarray],
    size: int,
) -> dict[str, dict[str, Any]]:
    """Apply every affine E-025 directional row to every frozen probe."""

    records: dict[str, dict[str, Any]] = {}
    for probe_name, vector in vectors.items():
        if vector.shape != (size,):
            raise ValueError(f"probe {probe_name} does not match the system size")
        actions = np.empty((len(CANONICAL_OPERATOR_NAMES), size), dtype=np.float64)
        for operator_index, operator_name in enumerate(CANONICAL_OPERATOR_NAMES):
            actions[operator_index] = (
                matrices[operator_name] @ vector + offsets[operator_name]
            )
        records[probe_name] = _array_fingerprint_record(actions)
    if tuple(records) != REQUIRED_ROW_ACTION_NAMES:
        raise RuntimeError("derived row-action inventory drifted")
    return records


def _active_jacobian_action_record(
    matrices: dict[str, sparse.csr_matrix],
    active: np.ndarray,
    gradient: np.ndarray,
    vectors: dict[str, np.ndarray],
) -> dict[str, Any]:
    size = int(active.size)
    jacobian = matrices[CANONICAL_OPERATOR_NAMES[-1]].multiply(
        gradient[:, 2, None]
    )
    for basis_index in range(len(BASELINE_DIRECTIONAL_BASES)):
        mask = active == basis_index
        if not np.any(mask):
            continue
        primary_name = CANONICAL_OPERATOR_NAMES[2 * basis_index]
        perpendicular_name = CANONICAL_OPERATOR_NAMES[2 * basis_index + 1]
        jacobian = jacobian + matrices[primary_name].multiply(
            np.where(mask, gradient[:, 0], 0.0)[:, None]
        )
        jacobian = jacobian + matrices[perpendicular_name].multiply(
            np.where(mask, gradient[:, 1], 0.0)[:, None]
        )
    jacobian.eliminate_zeros()
    jacobian = jacobian.tocsr()
    actions = np.empty((len(REQUIRED_ROW_ACTION_NAMES), size), dtype=np.float64)
    for probe_index, vector in enumerate(vectors.values()):
        actions[probe_index] = jacobian @ vector
    return _array_fingerprint_record(actions)


def stage6_nonlinear_snapshot(
    system: dict[str, Any],
    matrices: dict[str, sparse.csr_matrix],
    field: np.ndarray,
    target_source: np.ndarray,
    vectors: dict[str, np.ndarray],
) -> dict[str, dict[str, Any]]:
    """Derive the stage-6 residual, exact ties, and Jacobian actions."""

    size = int(field.size)
    shift = 1.0 / (4.0 * system["cubic_coefficient"])
    offsets = system["boundary_offsets"]
    azimuthal = (
        matrices[CANONICAL_OPERATOR_NAMES[-1]] @ field
        + offsets[CANONICAL_OPERATOR_NAMES[-1]]
        + shift
    )
    curvatures = np.empty(
        (len(BASELINE_DIRECTIONAL_BASES), size, 3), dtype=np.float64
    )
    for basis_index in range(len(BASELINE_DIRECTIONAL_BASES)):
        for component in (0, 1):
            name = CANONICAL_OPERATOR_NAMES[2 * basis_index + component]
            curvatures[basis_index, :, component] = (
                matrices[name] @ field + offsets[name] + shift
            )
        curvatures[basis_index, :, 2] = azimuthal
    candidates = e035.e025.monotone_sigma_extension(curvatures)
    active = np.argmin(candidates, axis=0).astype(np.int64)
    nodes = np.arange(size, dtype=np.int64)
    selected = candidates[active, nodes]
    tie_masks = candidates == selected[None, :]
    tie_counts = np.count_nonzero(tie_masks, axis=0)
    tie_nodes = np.flatnonzero(tie_counts > 1)
    tie_multiplicities = tuple(int(tie_counts[node]) for node in tie_nodes)
    if (
        tie_nodes.size != EXPECTED_STAGE6_TIE_NODE_COUNT
        or tie_multiplicities != EXPECTED_STAGE6_TIE_MULTIPLICITIES
    ):
        raise ValueError(
            "stage-6 exact ties must be four ordered binary nodes before "
            "the frozen 16 selections are evaluated"
        )
    tie_index_lists = np.full(
        (size, len(BASELINE_DIRECTIONAL_BASES)), -1, dtype=np.int64
    )
    tie_options: list[np.ndarray] = []
    for node in range(size):
        indices = np.flatnonzero(tie_masks[:, node]).astype(np.int64)
        tie_index_lists[node, : indices.size] = indices
        if indices.size > 1:
            tie_options.append(indices)

    active_curvatures = curvatures[active, nodes]
    active_gradients = e035.e025.monotone_sigma_gradient(active_curvatures)
    fixed_radial_index = BASELINE_DIRECTIONAL_BASES.index((1, 0))
    fixed_diagonal_index = BASELINE_DIRECTIONAL_BASES.index((1, 1))
    radial_name = CANONICAL_OPERATOR_NAMES[2 * fixed_radial_index]
    axial_name = CANONICAL_OPERATOR_NAMES[2 * fixed_radial_index + 1]
    positive_diagonal_name = CANONICAL_OPERATOR_NAMES[2 * fixed_diagonal_index]
    negative_diagonal_name = CANONICAL_OPERATOR_NAMES[
        2 * fixed_diagonal_index + 1
    ]
    radial = matrices[radial_name] @ field + offsets[radial_name]
    axial = matrices[axial_name] @ field + offsets[axial_name]
    diagonal_plus = (
        matrices[positive_diagonal_name] @ field
        + offsets[positive_diagonal_name]
    )
    diagonal_minus = (
        matrices[negative_diagonal_name] @ field
        + offsets[negative_diagonal_name]
    )
    fixed_components = np.stack(
        (
            radial,
            0.5 * (diagonal_plus - diagonal_minus),
            axial,
            matrices[CANONICAL_OPERATOR_NAMES[-1]] @ field
            + offsets[CANONICAL_OPERATOR_NAMES[-1]],
        )
    )
    rhs = 3.0 / (16.0 * system["cubic_coefficient"] ** 2) + target_source / (
        2.0 * system["cubic_coefficient"]
    )
    result: dict[str, dict[str, Any]] = {
        "curvatures": _array_fingerprint_record(curvatures),
        "candidate_values": _array_fingerprint_record(candidates),
        "default_first_index_argmins": _array_fingerprint_record(active),
        "exact_tie_masks": _array_fingerprint_record(tie_masks),
        "exact_tie_index_lists": _array_fingerprint_record(tie_index_lists),
        "selected_values": _array_fingerprint_record(selected),
        "shifted_residual": _array_fingerprint_record(selected - rhs),
        "fixed_components": _array_fingerprint_record(fixed_components),
        "active_gradients": _array_fingerprint_record(active_gradients),
        "active_jacobian_actions": _active_jacobian_action_record(
            matrices,
            active,
            active_gradients,
            vectors,
        ),
    }
    selections = list(itertools.product(*tie_options))
    if len(selections) != 16:
        raise RuntimeError("stage-6 tie-selection enumeration drifted")
    for selection_index, selection in enumerate(selections):
        selected_active = active.copy()
        selected_active[tie_nodes] = np.asarray(selection, dtype=np.int64)
        selected_curvatures = curvatures[selected_active, nodes]
        selected_gradient = e035.e025.monotone_sigma_gradient(selected_curvatures)
        result[
            f"tie_selection_{selection_index:02d}_active_jacobian_action"
        ] = _active_jacobian_action_record(
            matrices,
            selected_active,
            selected_gradient,
            vectors,
        )
    if tuple(result) != REQUIRED_NONLINEAR_ACTION_NAMES:
        raise RuntimeError("derived nonlinear/tie-action inventory drifted")
    return result


def _validate_stage6_report_bindings(
    report: dict[str, Any],
    field_sha256: str,
    system_sha256: str,
    target_source_sha256: str,
) -> None:
    if not isinstance(report, dict):
        raise TypeError("stage-6 report must be supplied as a mapping")
    if report.get("output_field_sha256") != field_sha256:
        raise ValueError("stage-6 report is not bound to the supplied field")
    operator_and_source = report.get("operator_and_source")
    if not isinstance(operator_and_source, dict) or operator_and_source.get(
        "system_digest"
    ) != system_sha256:
        raise ValueError("stage-6 report is not bound to the supplied system")
    campaign = report.get("campaign")
    if not isinstance(campaign, dict):
        raise ValueError("stage-6 report has no campaign ledger")
    stages = campaign.get("stages")
    if (
        campaign.get("completed_stage") != 6
        or campaign.get("completed_amplitude") != ACCEPTED_AMPLITUDE
        or not isinstance(stages, list)
        or len(stages) != 6
        or not isinstance(stages[-1], dict)
        or stages[-1].get("amplitude") != ACCEPTED_AMPLITUDE
        or stages[-1].get("target_source_digest") != target_source_sha256
    ):
        raise ValueError("stage-6 report is not bound to the supplied target source")


def _derive_stage6_equivalence_snapshot(
    artifacts: dict[str, Any],
    *,
    expected_lineage: dict[str, str],
    expected_size: int,
    expected_index_map_shape: tuple[int, int],
) -> dict[str, Any]:
    """Generic derivation core; the public path supplies immutable lineage."""

    if not isinstance(artifacts, dict) or set(artifacts) != set(
        REQUIRED_EQUIVALENCE_ARTIFACT_FIELDS
    ):
        raise ValueError("equivalence artifacts are incomplete")
    system, matrices, size = _validated_system_artifact(
        artifacts["system"],
        expected_size=expected_size,
        expected_index_map_shape=expected_index_map_shape,
    )
    field = _require_exact_array(artifacts["field"], "<f8", 1, "stage-6 field")
    target_source = _require_exact_array(
        artifacts["target_source"], "<f8", 1, "stage-6 target source"
    )
    if field.shape != (size,) or target_source.shape != (size,):
        raise ValueError("stage-6 field/source arrays do not match the system")
    if not np.all(np.isfinite(field)) or not np.all(np.isfinite(target_source)):
        raise ValueError("stage-6 field/source arrays must be finite")
    implementation_payloads = artifacts["implementation_payloads"]
    if not isinstance(implementation_payloads, dict) or tuple(
        implementation_payloads
    ) != ("e025_module", "e028_module"):
        raise ValueError("implementation payloads must be ordered E-025 then E-028")
    if not isinstance(expected_lineage, dict) or tuple(
        expected_lineage
    ) != REQUIRED_DERIVED_LINEAGE_FIELDS:
        raise ValueError("expected lineage fields are incomplete or reordered")
    for name, value in expected_lineage.items():
        _require_sha256(value, name)

    radial_indices = np.rint(system["rho"] / system["spacing"]).astype(np.int64)
    axial_indices = np.rint(system["z"] / system["spacing"]).astype(np.int64)
    if not np.array_equal(
        system["rho"], radial_indices.astype(np.float64) * system["spacing"]
    ) or not np.array_equal(
        system["z"], axial_indices.astype(np.float64) * system["spacing"]
    ):
        raise ValueError("system coordinates are not exact baseline grid nodes")
    vectors = required_equivalence_vectors(radial_indices, axial_indices)
    system_sha256 = _e025_compatible_system_sha256(system)
    field_sha256 = _float64_array_sha256(field)
    target_source_sha256 = _float64_array_sha256(target_source)
    report = artifacts["report"]
    _validate_stage6_report_bindings(
        report,
        field_sha256,
        system_sha256,
        target_source_sha256,
    )
    derived_lineage = {
        "accepted_checkpoint_sha256": _payload_sha256(
            artifacts["checkpoint_payload"], "checkpoint payload"
        ),
        "accepted_field_sha256": field_sha256,
        "accepted_report_sha256": _canonical_report_sha256(report),
        "system_sha256": system_sha256,
        "target_source_sha256": target_source_sha256,
        "e025_module_sha256": _payload_sha256(
            implementation_payloads["e025_module"], "E-025 module payload"
        ),
        "e028_module_sha256": _payload_sha256(
            implementation_payloads["e028_module"], "E-028 module payload"
        ),
    }
    if derived_lineage != expected_lineage:
        differences = [
            name
            for name in REQUIRED_DERIVED_LINEAGE_FIELDS
            if derived_lineage[name] != expected_lineage[name]
        ]
        raise ValueError(
            "supplied stage-6 artifacts fail expected lineage at "
            + ", ".join(differences)
        )
    manifest = {
        **derived_lineage,
        "operator_order": list(CANONICAL_OPERATOR_NAMES),
        "generator": EQUIVALENCE_LINEAGE_MANIFEST["generator"],
        "probe_vector_sha256": snapshot_fingerprint(vectors),
        "dtype": EQUIVALENCE_LINEAGE_MANIFEST["dtype"],
        "endianness": EQUIVALENCE_LINEAGE_MANIFEST["endianness"],
        "signed_zero_policy": EQUIVALENCE_LINEAGE_MANIFEST[
            "signed_zero_policy"
        ],
    }
    if tuple(manifest) != REQUIRED_MANIFEST_FIELDS:
        raise RuntimeError("derived equivalence manifest order drifted")
    operator_records = {
        name: {
            key: _array_fingerprint_record(system["operators"][name][key])
            for key in ("indptr", "indices", "data")
        }
        for name in CANONICAL_OPERATOR_NAMES
    }
    boundary_records = {
        name: _array_fingerprint_record(system["boundary_offsets"][name])
        for name in CANONICAL_OPERATOR_NAMES
    }
    return {
        "operator_snapshot": {
            "manifest": manifest,
            "operators": operator_records,
            "boundary_offsets": boundary_records,
            "row_actions": _derived_row_action_records(
                matrices,
                system["boundary_offsets"],
                vectors,
                size,
            ),
        },
        "nonlinear_snapshot": stage6_nonlinear_snapshot(
            system,
            matrices,
            field,
            target_source,
            vectors,
        ),
    }


def _retained_lineage_from_report(report: dict[str, Any]) -> dict[str, str]:
    """Bind dynamic system/source hashes through the immutable report hash."""

    if not isinstance(report, dict):
        raise TypeError("stage-6 report must be supplied as a mapping")
    if _canonical_report_sha256(report) != ACCEPTED_REPORT_SHA256:
        raise ValueError("supplied report is not the immutable accepted stage-6 report")
    operator_and_source = report.get("operator_and_source")
    campaign = report.get("campaign")
    stages = campaign.get("stages") if isinstance(campaign, dict) else None
    if (
        not isinstance(operator_and_source, dict)
        or not isinstance(stages, list)
        or len(stages) != 6
        or not isinstance(stages[-1], dict)
    ):
        raise ValueError("accepted stage-6 report lineage fields are missing")
    system_sha256 = _require_sha256(
        operator_and_source.get("system_digest"), "report system_digest"
    )
    target_source_sha256 = _require_sha256(
        stages[-1].get("target_source_digest"),
        "report stage-6 target_source_digest",
    )
    return {
        "accepted_checkpoint_sha256": ACCEPTED_CHECKPOINT_SHA256,
        "accepted_field_sha256": ACCEPTED_FIELD_SHA256,
        "accepted_report_sha256": ACCEPTED_REPORT_SHA256,
        "system_sha256": system_sha256,
        "target_source_sha256": target_source_sha256,
        "e025_module_sha256": ACCEPTED_E025_MODULE_SHA256,
        "e028_module_sha256": ACCEPTED_E028_MODULE_SHA256,
    }


def derive_stage6_equivalence_snapshot(
    artifacts: dict[str, Any],
) -> dict[str, Any]:
    """Derive the accepted baseline snapshot with hard-bound lineage and geometry."""

    if not isinstance(artifacts, dict) or set(artifacts) != set(
        REQUIRED_EQUIVALENCE_ARTIFACT_FIELDS
    ):
        raise ValueError("equivalence artifacts are incomplete")
    return _derive_stage6_equivalence_snapshot(
        artifacts,
        expected_lineage=_retained_lineage_from_report(artifacts["report"]),
        expected_size=BASELINE_UNKNOWN_COUNT,
        expected_index_map_shape=BASELINE_INDEX_MAP_SHAPE,
    )


def _compare_equivalence_snapshots(
    reference: dict[str, Any] | None,
    candidate: dict[str, Any] | None,
) -> dict[str, Any]:
    """Compare only snapshots produced by a derivation pathway."""

    reference_valid = reference is not None
    candidate_valid = candidate is not None
    checks = {
        "reference_artifacts_derived": reference_valid,
        "candidate_artifacts_derived": candidate_valid,
        "operator_snapshot": reference_valid
        and candidate_valid
        and snapshot_fingerprint(reference["operator_snapshot"])
        == snapshot_fingerprint(candidate["operator_snapshot"]),
        "nonlinear_snapshot": reference_valid
        and candidate_valid
        and snapshot_fingerprint(reference["nonlinear_snapshot"])
        == snapshot_fingerprint(candidate["nonlinear_snapshot"]),
    }
    checks["complete_snapshot"] = (
        reference_valid
        and candidate_valid
        and snapshot_fingerprint(reference) == snapshot_fingerprint(candidate)
    )
    return {
        "checks": checks,
        "reference_fingerprint_recomputed": (
            snapshot_fingerprint(reference) if reference_valid else None
        ),
        "candidate_fingerprint_recomputed": (
            snapshot_fingerprint(candidate) if candidate_valid else None
        ),
        "passed": all(checks.values()),
    }


def exact_row_action_equivalence(
    reference_artifacts: dict[str, Any],
    candidate_artifacts: dict[str, Any],
) -> dict[str, Any]:
    """Derive, fingerprint, and compare two supplied stage-6 artifact sets."""

    reference: dict[str, Any] | None = None
    candidate: dict[str, Any] | None = None
    try:
        reference = derive_stage6_equivalence_snapshot(reference_artifacts)
    except (KeyError, TypeError, ValueError):
        pass
    try:
        candidate = derive_stage6_equivalence_snapshot(candidate_artifacts)
    except (KeyError, TypeError, ValueError):
        pass
    return _compare_equivalence_snapshots(reference, candidate)


def _equivalence_self_test_fixture() -> dict[str, Any]:
    """Build tiny explicit stage-6 artifacts; this is not baseline execution."""

    size = 4
    indptr = np.arange(size + 1, dtype=np.int64)
    indices = np.arange(size, dtype=np.int64)
    operators = {
        name: {
            "indptr": indptr.copy(),
            "indices": indices.copy(),
            "data": np.full(size, float(operator_index + 1), dtype=np.float64),
        }
        for operator_index, name in enumerate(CANONICAL_OPERATOR_NAMES)
    }
    boundary_offsets: dict[str, np.ndarray] = {}
    for operator_index, name in enumerate(CANONICAL_OPERATOR_NAMES):
        basis_index = operator_index // 2
        curvature = 1.0 if basis_index in (0, 1) else 2.0
        if name == CANONICAL_OPERATOR_NAMES[-1]:
            curvature = 1.0
        boundary_offsets[name] = np.full(
            size,
            curvature - 0.25,
            dtype=np.float64,
        )
    system_artifact = {
        "radial_max": RADIAL_MAX,
        "spacing": BASE_SPACING,
        "directional_radius": e035.BASELINE_DIRECTIONAL_RADIUS,
        "cubic_coefficient": 1.0,
        "bases": BASELINE_DIRECTIONAL_BASES,
        "rho": np.asarray((0.0, 0.0, 0.125, 0.125), dtype=np.float64),
        "z": np.asarray((0.0, 0.125, 0.0, 0.125), dtype=np.float64),
        "index_map": np.asarray(((0, 1), (2, 3)), dtype=np.int64),
        "operators": operators,
        "boundary_offsets": boundary_offsets,
    }
    canonical_system, _matrices, _size = _validated_system_artifact(
        system_artifact,
        expected_size=size,
        expected_index_map_shape=(2, 2),
    )
    field = np.zeros(size, dtype=np.float64)
    target_source = np.asarray((0.1, 0.2, 0.3, -0.0), dtype=np.float64)
    system_sha256 = _e025_compatible_system_sha256(canonical_system)
    field_sha256 = _float64_array_sha256(field)
    target_source_sha256 = _float64_array_sha256(target_source)
    stages = [
        {
            "amplitude": stage / 12.0,
            "target_source_digest": (
                target_source_sha256 if stage == 6 else f"{stage:064x}"
            ),
        }
        for stage in range(1, 7)
    ]
    report = {
        "output_field_sha256": field_sha256,
        "operator_and_source": {"system_digest": system_sha256},
        "campaign": {
            "completed_stage": 6,
            "completed_amplitude": ACCEPTED_AMPLITUDE,
            "stages": stages,
        },
    }
    checkpoint_payload = b"deterministic-tiny-stage6-checkpoint"
    implementation_payloads = {
        "e025_module": b"deterministic-tiny-e025-module",
        "e028_module": b"deterministic-tiny-e028-module",
    }
    return {
        "system": system_artifact,
        "field": field,
        "target_source": target_source,
        "checkpoint_payload": checkpoint_payload,
        "report": report,
        "implementation_payloads": implementation_payloads,
    }


def _tiny_equivalence_expected_lineage(
    artifacts: dict[str, Any],
) -> dict[str, str]:
    """Derive expectations only for the deterministic four-row self-test."""

    system, _matrices, _size = _validated_system_artifact(
        artifacts["system"],
        expected_size=4,
        expected_index_map_shape=(2, 2),
    )
    return {
        "accepted_checkpoint_sha256": _payload_sha256(
            artifacts["checkpoint_payload"], "checkpoint payload"
        ),
        "accepted_field_sha256": _float64_array_sha256(artifacts["field"]),
        "accepted_report_sha256": _canonical_report_sha256(artifacts["report"]),
        "system_sha256": _e025_compatible_system_sha256(system),
        "target_source_sha256": _float64_array_sha256(
            artifacts["target_source"]
        ),
        "e025_module_sha256": _payload_sha256(
            artifacts["implementation_payloads"]["e025_module"],
            "E-025 module payload",
        ),
        "e028_module_sha256": _payload_sha256(
            artifacts["implementation_payloads"]["e028_module"],
            "E-028 module payload",
        ),
    }


def _derive_tiny_equivalence_snapshot(
    artifacts: dict[str, Any],
    *,
    expected_lineage: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Run the generic executor under the explicit tiny-test geometry."""

    return _derive_stage6_equivalence_snapshot(
        artifacts,
        expected_lineage=(
            _tiny_equivalence_expected_lineage(artifacts)
            if expected_lineage is None
            else expected_lineage
        ),
        expected_size=4,
        expected_index_map_shape=(2, 2),
    )


def _tiny_row_action_equivalence(
    reference_artifacts: dict[str, Any],
    candidate_artifacts: dict[str, Any],
) -> dict[str, Any]:
    reference: dict[str, Any] | None = None
    candidate: dict[str, Any] | None = None
    try:
        reference = _derive_tiny_equivalence_snapshot(reference_artifacts)
    except (KeyError, TypeError, ValueError):
        pass
    try:
        candidate = _derive_tiny_equivalence_snapshot(candidate_artifacts)
    except (KeyError, TypeError, ValueError):
        pass
    return _compare_equivalence_snapshots(reference, candidate)


def executable_gate_self_tests() -> dict[str, Any]:
    """Exercise every frozen evaluator on passing and rejecting controls."""

    norms = matrix_difference_norms(
        np.asarray(((1.0, 0.0, -1.0, 0.5), (0.0, 0.5, 0.0, -0.5))),
        np.asarray((1.0, 2.0)),
    )
    spread = same_grid_operator_spread(
        np.asarray(
            (
                ((1.0, 0.0, -1.0, 0.5), (0.0, 0.5, 0.0, -0.5)),
                ((0.5, 0.0, -0.5, 0.25), (0.0, 0.25, 0.0, -0.25)),
                ((0.25, 0.0, -0.25, 0.125), (0.0, 0.125, 0.0, -0.125)),
            )
        ),
        np.asarray((1.0, 2.0)),
    )
    base_components = np.asarray(
        ((1.0, 0.5, -1.0, 0.25), (0.5, -0.25, 0.75, -0.5))
    )
    recovered = np.asarray(
        [
            [grid_scale * recovery_scale * base_components for recovery_scale in (1.0, 0.8, 0.6)]
            for grid_scale in (4.0, 2.0, 1.0)
        ]
    )
    one_mask_metrics = coupled_path_metrics(recovered, np.asarray((1.0, 2.0)))
    screen_metrics = {mask: one_mask_metrics for mask in MASK_NAMES}
    screen_orientations = {key: True for key in FIXED_ORIENTATION_KEYS}
    coupled_pass = coupled_path_screen_gate(
        screen_metrics,
        screen_orientations,
        solution_schedule="tight_2",
        verified_root_error_enclosure=True,
    )["screen_authorized"]
    coupled_reject = not coupled_path_screen_gate(
        screen_metrics,
        screen_orientations,
        solution_schedule="tight_2",
        verified_root_error_enclosure=False,
    )["screen_authorized"]
    separation_pass = solver_separation_gate(10.0, (0.02, 0.02), (0.01, 0.01))["passed"]
    separation_reject = not solver_separation_gate(1.0, (0.02, 0.02), (0.01, 0.01))["passed"]
    orientation_pass = orientation_interval_gate(
        (1.0, 0.5),
        (0.05, 0.05, 0.05),
        (10.0, 20.0, 40.0),
        (2.0, 2.0, 2.0),
        component="radial",
        axial_index=6,
    )["passed"]
    orientation_reject = not orientation_interval_gate(
        (1.0, -0.5),
        (0.05, 0.05, 0.05),
        (10.0, 20.0, 40.0),
        (2.0, 2.0, 2.0),
        component="radial",
        axial_index=6,
    )["passed"]
    symmetry_zero_pass = orientation_interval_gate(
        (0.0, 0.0),
        (0.0, 0.0, 0.0),
        (10.0, 20.0, 40.0),
        (2.0, 2.0, 2.0),
        component="mixed",
        axial_index=0,
    )["passed"]
    symmetry_zero_reject = not orientation_interval_gate(
        (1.0e-6, 0.0),
        (0.0, 0.0, 0.0),
        (10.0, 20.0, 40.0),
        (2.0, 2.0, 2.0),
        component="mixed",
        axial_index=0,
    )["passed"]
    eigengap_pass = eigengap_gate(np.asarray((1.0, 2.0)), np.asarray((0.1, 0.2)))["passed"]
    eigengap_reject = not eigengap_gate(np.asarray((0.2,)), np.asarray((0.1,)))["passed"]
    tile = np.sin(2.0 * math.pi * np.indices((32, 32))[0] / 32.0)
    transfer_metrics_executed = transfer_parity_metrics(
        tile,
        np.ones_like(tile),
        spacing=0.125,
        recovery="C_h",
        component="radial",
        detrend="affine",
    )["total_component_rms"] > 0.0
    synthetic_metrics = [
        {
            "recovery": "C_h",
            "component": "radial",
            "origin_square_theta_cutoff": frozen_transfer_cutoffs()["C_h:radial"],
            "total_component_rms": 1.0,
            "windowed_total_rms": 1.0,
            "outside_band_rms": value,
            "outside_band_energy_fraction": value,
            "parseval_relative_error": 0.0,
            "floating_floor": 1.0e-15,
            "parity_amplitudes": {
                name: value / 10.0
                for name in ("radial", "axial", "checkerboard")
            },
            "parity_normalized_correlations": {
                name: value
                for name in ("radial", "axial", "checkerboard")
            },
        }
        for value in (0.06, 0.03, 0.01)
    ]
    transfer_pass = transfer_parity_gate(synthetic_metrics, 0.1)["passed"]
    transfer_reject = not transfer_parity_gate(list(reversed(synthetic_metrics)), 0.1)["passed"]
    fixture = _equivalence_self_test_fixture()
    equivalence_pass = _tiny_row_action_equivalence(fixture, fixture)["passed"]
    first_operator = CANONICAL_OPERATOR_NAMES[0]
    signed_zero_source = fixture["target_source"].copy()
    signed_zero_source[-1] = 0.0
    signed_zero = {**fixture, "target_source": signed_zero_source}
    equivalence_reject = not _tiny_row_action_equivalence(fixture, signed_zero)["passed"]
    invalid_operator = dict(fixture["system"]["operators"][first_operator])
    invalid_indptr = invalid_operator["indptr"].copy()
    invalid_indptr[-1] -= 1
    invalid_operator["indptr"] = invalid_indptr
    invalid_operators = dict(fixture["system"]["operators"])
    invalid_operators[first_operator] = invalid_operator
    invalid_csr = {
        **fixture,
        "system": {**fixture["system"], "operators": invalid_operators},
    }
    equivalence_noncanonical_csr_reject = not _tiny_row_action_equivalence(
        fixture,
        invalid_csr,
    )["passed"]
    checks = {
        "matrix_norms": norms["matrix_linf_spectral"] > 0.0,
        "same_grid_operator_spread": (
            tuple(spread["spread_by_metric"]) == PRIMARY_METRIC_NAMES
        ),
        "coupled_path_pass_control": coupled_pass,
        "coupled_path_missing_root_enclosure_reject_control": coupled_reject,
        "solver_separation_pass_control": separation_pass,
        "solver_separation_reject_control": separation_reject,
        "orientation_pass_control": orientation_pass,
        "orientation_reject_control": orientation_reject,
        "symmetry_zero_pass_control": symmetry_zero_pass,
        "symmetry_zero_nonzero_reject_control": symmetry_zero_reject,
        "eigengap_pass_control": eigengap_pass,
        "eigengap_reject_control": eigengap_reject,
        "transfer_metrics_executed": transfer_metrics_executed,
        "transfer_gate_pass_control": transfer_pass,
        "transfer_gate_reject_control": transfer_reject,
        "row_equivalence_pass_control": equivalence_pass,
        "row_equivalence_signed_zero_reject_control": equivalence_reject,
        "row_equivalence_noncanonical_csr_reject_control": (
            equivalence_noncanonical_csr_reject
        ),
    }
    return {"checks": checks, "all_passed": all(checks.values())}


def frozen_validation_protocol() -> dict[str, Any]:
    """Return exact dormant rules and execute their evaluator self-tests."""

    solver_schedule = {
        "standard": {
            "nonlinear_relative_l2": 1.0e-7,
            "gmres_true_relative_residual": 1.0e-8,
        },
        "tight_1": {
            "nonlinear_relative_l2": 1.0e-8,
            "gmres_true_relative_residual": 1.0e-9,
        },
        "tight_2": {
            "nonlinear_relative_l2": 1.0e-9,
            "gmres_true_relative_residual": 1.0e-10,
        },
        "shared": {
            "target_amplitude": ACCEPTED_AMPLITUDE,
            "continuation_targets": [step / 12.0 for step in range(1, 7)],
            "newton_max_iterations_per_target": 20,
            "gmres_restart": 50,
            "gmres_max_restart_cycles": 40,
            "gmres_total_inner_cap": 2000,
            "line_search_sufficient_decrease": 1.0e-4,
            "line_search_max_dyadic_halvings": 24,
            "initialization": (
                "each tolerance schedule independently runs all six targets "
                "from its own native Poisson predictor at 1/12 and exact "
                "accepted previous target thereafter; no root is reused across "
                "schedules"
            ),
            "strict_rules": (
                "require info=0, direct true residual strictly below request, "
                "nonlinear residual strictly below request, and every inherited "
                "provenance/source/domain/cone/path/tail/flux/force gate"
            ),
        },
    }
    resource_rows = e035.resource_feasibility()["candidate_grids"]
    projected_seconds_lower = 3.0 * sum(
        row["projected_one_standard_campaign_core_seconds_lower"]
        for row in resource_rows
    )
    projected_seconds_upper = 3.0 * sum(
        row["projected_one_standard_campaign_core_seconds_upper"]
        for row in resource_rows
    )
    self_tests = executable_gate_self_tests()
    transfer_cutoffs = frozen_transfer_cutoffs()
    definition_schema = {
        "masks": list(MASK_NAMES),
        "recoveries": list(RECOVERY_NAMES),
        "components": list(COMPONENT_NAMES),
        "primary_metrics": list(PRIMARY_METRIC_NAMES),
        "primary_acceptance_masks": list(PRIMARY_ACCEPTANCE_MASK_NAMES),
        "coupled_q_keys": list(COUPLED_Q_KEYS),
        "operator_spread_keys": list(OPERATOR_SPREAD_KEYS),
        "fixed_orientation_keys": list(FIXED_ORIENTATION_KEYS),
        "transfer_cutoffs": transfer_cutoffs,
        "required_row_actions": list(REQUIRED_ROW_ACTION_NAMES),
        "required_nonlinear_actions": list(REQUIRED_NONLINEAR_ACTION_NAMES),
        "required_manifest_fields": list(REQUIRED_MANIFEST_FIELDS),
        "canonical_operator_names": list(CANONICAL_OPERATOR_NAMES),
        "equivalence_artifact_fields": list(
            REQUIRED_EQUIVALENCE_ARTIFACT_FIELDS
        ),
        "baseline_unknown_count": BASELINE_UNKNOWN_COUNT,
        "baseline_index_map_shape": list(BASELINE_INDEX_MAP_SHAPE),
        "stage6_tie_multiplicities": list(
            EXPECTED_STAGE6_TIE_MULTIPLICITIES
        ),
        "lineage_manifest_template": EQUIVALENCE_LINEAGE_MANIFEST,
    }
    definition_fingerprint = hashlib.sha256(
        json.dumps(
            definition_schema,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    definition_audit = {
        "schema_sha256": definition_fingerprint,
        "coupled_q_key_count": len(COUPLED_Q_KEYS),
        "operator_spread_key_count": len(OPERATOR_SPREAD_KEYS),
        "fixed_orientation_key_count": len(FIXED_ORIENTATION_KEYS),
        "transfer_cutoff_count": len(transfer_cutoffs),
        "required_row_action_count": len(REQUIRED_ROW_ACTION_NAMES),
        "required_nonlinear_action_count": len(REQUIRED_NONLINEAR_ACTION_NAMES),
        "required_manifest_field_count": len(REQUIRED_MANIFEST_FIELDS),
        "canonical_operator_count": len(CANONICAL_OPERATOR_NAMES),
        "full_baseline_equivalence_executed": False,
        "evaluator_self_tests_all_passed": self_tests["all_passed"],
        "all_frozen": (
            len(COUPLED_Q_KEYS)
            == len(MASK_NAMES) * len(RECOVERY_NAMES) * len(PRIMARY_METRIC_NAMES)
            and len(OPERATOR_SPREAD_KEYS)
            == len(MASK_NAMES) * len(PRIMARY_METRIC_NAMES)
            and len(FIXED_ORIENTATION_KEYS)
            == len(e035.FIXED_POINTS) * len(COMPONENT_NAMES)
            and len(transfer_cutoffs)
            == len(RECOVERY_NAMES) * len(COMPONENT_NAMES)
            and len(CANONICAL_OPERATOR_NAMES) == 25
            and self_tests["all_passed"]
        ),
    }
    return {
        "design_status": "fully_frozen_with_executable_gates_not_authorized",
        "executors": {
            "matrix_norms": "matrix_difference_norms",
            "same_grid_operator_spread": "same_grid_operator_spread",
            "coupled_path_metrics": "coupled_path_metrics",
            "coupled_path_screen": "coupled_path_screen_gate",
            "solver_separation": "solver_separation_gate",
            "transfer_tile": "transfer_tile",
            "transfer_band_constructor": "frozen_outside_origin_band",
            "transfer_parity_metrics": "transfer_parity_metrics",
            "transfer_parity_gate": "transfer_parity_gate",
            "orientation": "orientation_interval_gate",
            "eigengap": "eigengap_gate",
            "equivalence_vectors": "required_equivalence_vectors",
            "artifact_snapshot": "derive_stage6_equivalence_snapshot",
            "nonlinear_snapshot": "stage6_nonlinear_snapshot",
            "snapshot_fingerprint": "snapshot_fingerprint",
            "row_action_equivalence": "exact_row_action_equivalence",
        },
        "definition_schema": definition_schema,
        "definition_audit": definition_audit,
        "evaluator_self_tests": self_tests,
        "solver_schedule": solver_schedule,
        "native_then_restrict": (
            "Evaluate C_h, C_2h, and Q_2h on each native grid, then restrict "
            "their values by exact multipliers [1,2,4] to the enumerated "
            "h0=0.125 masks. No interpolation, moving extremum, or fallback."
        ),
        "matrix_norms": {
            "weighted_l2": (
                "sqrt(sum_x w_x ||M_j(x)-M_(j+1)(x)||_F^2/sum_x w_x)"
            ),
            "linf": "max_x ||M_j(x)-M_(j+1)(x)||_2",
            "components": (
                "the same weighted L2 and Linf on rr,rz,zz,aa separately"
            ),
        },
        "coupled_path_and_operator_spread": {
            "operator_spread": (
                "For every one of the five masks and ten frozen metrics, "
                "A_j,p is the maximum of all three pairwise C_h/C_2h/Q_2h "
                "same-grid differences."
            ),
            "contraction_index": "q_p=log2(D_0,p/D_1,p)",
            "difference_definition": (
                "D_j,r,p is computed separately for every recovery r; no "
                "post-outcome recovery selection or aggregation is allowed"
            ),
            "q_key_count": len(COUPLED_Q_KEYS),
            "operator_spread_key_count": len(OPERATOR_SPREAD_KEYS),
            "gate": (
                "Using only tight_2 outputs and only after a verified root-error "
                "enclosure exists, require finite positive q_p, D_1,p<D_0,p, "
                "A_2,p<A_1,p<A_0,p for each of the three source/transition "
                "acceptance masks; inner-feature/global masks are report-only. "
                "Every frozen fixed-point component orientation must also pass."
            ),
            "prohibited": "pure-spatial order, Richardson extrapolation, GCI, or continuum certificate",
        },
        "solver_separation": {
            "definition": (
                "S_j,p=max(||M_std-M_tight1||_p,"
                "||M_tight1-M_tight2||_p)"
            ),
            "gate": (
                "(S_j,p+S_(j+1),p)/D_j,p<=0.01 and the second replay "
                "difference is strictly smaller than the first"
            ),
            "limit": (
                "This remains an output-sensitivity screen and cannot replace "
                "a Krawczyk/interval-Newton or other verified root enclosure."
            ),
        },
        "transfer_and_parity": {
            "tile": (
                "half-open [rho0-2,rho0+2) x [z0-2,z0+2) with N=4/h; "
                "rr/zz/aa reflect evenly, rz reflects oddly and is zero at z=0; "
                "rho=0 is excluded"
            ),
            "preprocessing": (
                "cylindrical-quadrature weighted least-squares affine detrend "
                "for rr/rz/zz, constant detrend for aa; symmetric periodic Hann "
                "w[n]=0.5-0.5*cos(2*pi*n/N), unit-RMS normalized; unitary norm='ortho' FFT"
            ),
            "outside_band": (
                "derivative-weighted RMS outside each E-034 90-percent "
                "operator-amplitude origin square"
            ),
            "cutoff_source": (
                "models.e034_postprocessor_transfer.resolution_map; exact mapping "
                "C_h=centered_0p25, C_2h=centered_0p5, Q_2h=quadratic_5x5"
            ),
            "cutoffs_theta": transfer_cutoffs,
            "parity": (
                "absolute cylindrical-weighted amplitudes and normalized "
                "correlations on (-1)^i, (-1)^j, and (-1)^(i+j), with a "
                "128*eps*max(1,||field||inf) below-floor policy"
            ),
            "gate": (
                "outside-band RMS, windowed spectral energy fraction, and parity "
                "correlation must strictly contract twice or be below their frozen "
                "arithmetic floor; on the finest grid outside energy fraction <= "
                f"{TRANSFER_FRACTION_CAP:g} and parity correlation <= "
                f"{PARITY_FRACTION_CAP:g}; absolute RMS/amplitude must also be <= "
                f"{ABSOLUTE_TO_FINE_DIFFERENCE_CAP:g} times the absolute fine-grid "
                "difference RMS in the same component/mask"
            ),
            "classification": (
                "project diagnostics with predeclared thresholds, not an error theorem"
            ),
        },
        "orientation": {
            "gate": (
                "For each signed fixed-point component difference d_01/d_12, "
                "form radii E0+E1+f0+f1 and E1+E2+f1+f2. "
                "Orientation passes only when zero is excluded and both nested "
                "differences have the same sign; otherwise mark unresolved."
            ),
            "floating_floor": (
                f"{FLOAT_SAFETY_MULTIPLIER:g}*eps*max(1,row_L1*||u||inf); this "
                "guards arithmetic only and is not a discretization bound"
            ),
            "symmetry_zero_policy": (
                "only mixed recovery at z=0 is whitelisted; both observed nested "
                "differences must lie within their summed arithmetic floors"
            ),
        },
        "eigengap": {
            "gate": (
                "At each point require the measured leading-eigenvalue gap to "
                "exceed twice the verified spectral-norm matrix-error radius; "
                "otherwise eigenbranch-dependent output is unresolved by Weyl."
            ),
            "pair_margin": (
                "report only after the component enclosure and eigengap gate; "
                "never apply Richardson/GCI to this derived nonsmooth output"
            ),
        },
        "runtime_budget": {
            "designed_campaigns_per_grid": 3,
            "designed_grids": 3,
            "projected_campaign_cores": 9,
            "projected_core_seconds_low_estimate": projected_seconds_lower,
            "projected_core_seconds_high_estimate": projected_seconds_upper,
            "projected_core_hours_low_estimate": projected_seconds_lower / 3600.0,
            "projected_core_hours_high_estimate": projected_seconds_upper / 3600.0,
            "included_work": (
                "three independent complete copies of E-035's projected "
                "one-standard-campaign core on each of the three grids"
            ),
            "excluded_work": (
                "native linear solves, preflight/report/checkpoint work, root "
                "verification, recovery/mask/FFT diagnostics, teardown, "
                "iteration growth, and handoff reserve; 4.06-5.90 hours is an "
                "indicative fixed-iteration projection, not a demonstrated lower "
                "bound or a complete feasible budget for the tighter schedules"
            ),
            "authorization": (
                "none: E-035 already shows the frozen sequence exceeds nightly "
                "and retained-memory caps, and E-036 parks the line"
            ),
        },
    }


def nodal_between_node_counterexample() -> dict[str, Any]:
    """Record an exact nodal-invisibility example for Hessian error."""

    rows = []
    for spacing, directional_radius in GRID_SPECIFICATIONS:
        rows.append(
            {
                "spacing": spacing,
                "directional_radius": directional_radius,
                "potential_linf": spacing**2,
                "nodal_values": "exactly zero at x=k*h for every integer k",
                "second_derivative_linf": 4.0 * math.pi**2,
            }
        )
    return {
        "error_identity": (
            "R_hm(u_tilde_hm)-D2u = R_hm(u_tilde_hm-u_hm) + "
            "R_hm(u_hm-I_hu) + (R_hm(I_hu)-D2u)"
        ),
        "family": "e_h(x)=h^2*sin(2*pi*x/h)",
        "rows": rows,
        "limit": (
            "This is an information/regularity counterexample, not a claim "
            "that e_h satisfies the nonlinear PDE. It shows that nodal values, "
            "nodal recoveries, and potential convergence cannot control the "
            "between-node Hessian without a verified PDE stability and "
            "regularity estimate."
        ),
    }


def actual_solution_enclosure_audit() -> dict[str, Any]:
    """Attempt the required enclosure and record why it cannot be certified."""

    obligations = [
        {
            "term": "actual_solution_existence_uniqueness_and_regular_branch",
            "needed": (
                "a theorem for the exact axisymmetric quarter-disk problem, "
                "source, symmetry axis, curved boundary, and admitted cone"
            ),
            "status": "not_verified_for_this_problem",
        },
        {
            "term": "uniform_ellipticity_and_inverse_stability",
            "needed": (
                "a positive certified actual-solution ellipticity margin and a "
                "computable inverse/comparison constant on the fixed ROI"
            ),
            "status": "missing",
        },
        {
            "term": "spatial_consistency",
            "needed": (
                "explicit C_h*h^p with verified actual-solution derivative "
                "bounds, including cylindrical coefficients"
            ),
            "status": "formal_order_only_constants_missing",
        },
        {
            "term": "directional_consistency",
            "needed": (
                "explicit C_theta*delta_theta^q and mixed term for the actual "
                "Hessian/eigenvector field on the nongeometric m=4,5,6 path"
            ),
            "status": "formal_order_only_constants_missing",
        },
        {
            "term": "source_transition_regularity_and_consistency",
            "needed": (
                "a reliability bound for the C2 source transition, including "
                "its four-cell coarsest positive-support infimum"
            ),
            "status": "missing_and_source_resolution_gate_failed",
        },
        {
            "term": "axis_and_curved_boundary_consistency",
            "needed": (
                "proved stability/consistency constants for reflected-axis and "
                "exact-line-intersection boundary rows"
            ),
            "status": "implementation_defined_theorem_missing",
        },
        {
            "term": "algebraic_root_error",
            "needed": (
                "interval Newton/Krawczyk inclusion or another verified "
                "residual-to-root theorem for each discrete root"
            ),
            "status": "not_available_residual_and_replays_are_proxies",
        },
        {
            "term": "recovery_operator",
            "needed": (
                "enumerated supports, fixed rows, scale covariance, and "
                "manufactured reproduction"
            ),
            "status": "completed_but_implementation_only",
        },
        {
            "term": "between_node_hessian",
            "needed": (
                "a verified modulus/regularity estimate controlling D2u "
                "between nodes from the PDE and data"
            ),
            "status": "missing_nodal_counterexample_remains",
        },
        {
            "term": "independent_validation",
            "needed": (
                "a published or separately proved reliability theorem whose "
                "hypotheses are checked for this operator and actual solution"
            ),
            "status": "missing",
        },
    ]
    return {
        "error_identity": (
            "R_hm(u_tilde_hm)-D2u = R_hm(u_tilde_hm-u_hm) + "
            "R_hm(u_hm-I_hu) + (R_hm(I_hu)-D2u)"
        ),
        "attempted_form": (
            "||D2u-R_(h,m)u_(h,m)|| <= E_h + E_theta + E_mixed + "
            "E_source + E_axis_boundary + E_root + E_recovery + E_between"
        ),
        "obligations": obligations,
        "all_required_terms_certified": all(
            item["status"].startswith("completed") for item in obligations
        ),
        "theorem_scope": {
            "barles_souganidis": (
                "monotone, stable, consistent schemes converge to the viscosity "
                "solution under comparison; it does not furnish this Hessian "
                "rate/enclosure"
            ),
            "froese_oberman_salvador": (
                "one 2-Hessian scheme is proved convergent to the viscosity "
                "solution in its stated Cartesian setting; the accurate method "
                "is reported as lacking a proof, and neither result validates "
                "this cylindrical adaptation's actual-solution Hessian error"
            ),
            "finlay_oberman": (
                "formal consistency separates spatial reach and directional "
                "resolution, but constants depend on smooth exact-solution data "
                "not bounded here"
            ),
            "monge_ampere_pointwise_rates": (
                "available rates use scheme-specific comparison/barrier and "
                "regularity hypotheses and control potential error, not this "
                "postprocessed Hessian without an additional derivative theorem"
            ),
        },
        "primary_sources": [
            {
                "citation": (
                    "Barles and Souganidis, Asymptotic Analysis 4 (1991) 271-283"
                ),
                "doi": "10.3233/ASY-1991-4305",
            },
            {
                "citation": (
                    "Froese, Oberman, and Salvador, IMA J. Numer. Anal. 37 "
                    "(2017) 209-236"
                ),
                "doi": "10.1093/imanum/drw007",
            },
            {
                "citation": (
                    "Finlay and Oberman, SIAM J. Sci. Comput. 41 (2019) A1952-A1975"
                ),
                "doi": "10.1137/18M1200269",
            },
            {
                "citation": (
                    "Nochetto, Ntogkas, and Zhang, two-scale Monge-Ampere "
                    "pointwise error estimates"
                ),
                "arxiv": "1706.09113",
            },
        ],
        "decision": "no_rigorous_actual_solution_derivative_enclosure_available",
        "interpretation": (
            "This rejects the proposed replacement gate on current evidence; "
            "it is not a theorem that no future enclosure can ever be derived."
        ),
    }


def dormant_row_action_equivalence_protocol() -> dict[str, Any]:
    """Freeze exact gates for a future representation, without authorizing it."""

    return {
        "status": "defined_but_dormant_not_a_reopening_authorization",
        "executable_evaluator": "exact_row_action_equivalence",
        "required_row_action_names": list(REQUIRED_ROW_ACTION_NAMES),
        "required_nonlinear_action_names": list(REQUIRED_NONLINEAR_ACTION_NAMES),
        "required_manifest_fields": list(REQUIRED_MANIFEST_FIELDS),
        "topology": (
            "For every row and directional operator, sorted/coalesced column "
            "indices must be exactly identical to the retained CSR reference."
        ),
        "coefficients": (
            "After materializing one row in float64, coefficient uint64 bit "
            "patterns must be exactly identical; no norm-tolerance substitute."
        ),
        "boundary_offsets": (
            "Offset indices and float64 bit patterns must be exactly identical "
            "for every reflected-axis and curved-boundary row."
        ),
        "row_actions": (
            "Bitwise-equal actions are required on zero, one, rho, z, all six "
            "quadratic monomials, two quartics, every basis-aligned plane wave, "
            "and deterministic seed-260719 Rademacher/Gaussian probes."
        ),
        "baseline_scope": (
            "exhaust all 25 retained E-025 operators (24 ordered meridional "
            "operators plus the azimuthal operator) and all 322319 rows at "
            "h=0.125,m=4 "
            "before any finer representation is built"
        ),
        "nonlinear_actions": (
            "At immutable stage 6, require bitwise-equal shifted residual, "
            "active candidate values and argmins including tie selections, "
            "fixed components, and active-Jacobian actions."
        ),
        "fingerprints": (
            "Derive content hashes from supplied checkpoint/module/report/field/"
            "source payloads and canonical CSR arrays, then derive all actions; "
            "expected hashes are comparisons, never substitutes for payloads."
        ),
        "failure_rule": (
            "Any unequal row, offset, action, or fingerprint fails equivalence; "
            "a numerically close implementation is a new discretization."
        ),
        "scope_limit": (
            "Passing changes storage only. It supplies neither an actual-solution "
            "enclosure nor a reason to reopen the parked Galileon line."
        ),
    }


def run_analysis() -> dict[str, Any]:
    """Run the deterministic checkpoint-free, PDE-free closure audit."""

    started = time.perf_counter()
    masks = enumerate_common_masks()
    recoveries = executable_recovery_definitions()
    protocol = frozen_validation_protocol()
    enclosure = actual_solution_enclosure_audit()
    counterexample = nodal_between_node_counterexample()
    equivalence = dormant_row_action_equivalence_protocol()
    definitions_complete = (
        masks["design_status"] == "fully_enumerated_and_executable"
        and all(
            mask["all_native_recovery_supports_valid"]
            for mask in masks["masks"].values()
        )
        and recoveries["quadratic_reproduction_passed"]
        and recoveries["scale_covariance_passed"]
        and recoveries["reflected_axis_validation_passed"]
        and protocol["design_status"]
        == "fully_frozen_with_executable_gates_not_authorized"
        and protocol["definition_audit"]["all_frozen"]
        and protocol["evaluator_self_tests"]["all_passed"]
        and equivalence["required_row_action_names"]
        == list(REQUIRED_ROW_ACTION_NAMES)
        and equivalence["required_nonlinear_action_names"]
        == list(REQUIRED_NONLINEAR_ACTION_NAMES)
        and equivalence["required_manifest_fields"]
        == list(REQUIRED_MANIFEST_FIELDS)
    )
    if enclosure["all_required_terms_certified"]:
        raise RuntimeError("E-036 unexpectedly reports a complete enclosure")
    return {
        "epistemic_status": (
            "no-solve numerical-method closure for a hypothetical PDE; not a "
            "continuum solution, detected field, artificial gravity, inertial "
            "control, spacetime engineering, reactionless propulsion, or FTL result"
        ),
        "focus_question": (
            "Can an independently validated two-parameter actual-solution "
            "derivative-error enclosure replace E-035's infeasible fourth grid?"
        ),
        "implementation_provenance": implementation_provenance(),
        "accepted_lineage": {
            "amplitude": ACCEPTED_AMPLITUDE,
            "checkpoint_sha256": ACCEPTED_CHECKPOINT_SHA256,
            "changed": False,
        },
        "common_masks": masks,
        "recovery_definitions": recoveries,
        "validation_protocol": protocol,
        "between_node_counterexample": counterexample,
        "actual_solution_enclosure": enclosure,
        "dormant_row_action_equivalence": equivalence,
        "decision": {
            "analysis_completed": True,
            "mathematical_gate_definitions_complete": definitions_complete,
            "full_baseline_equivalence_executed": False,
            "screen_authorized": False,
            "enclosure_available": False,
            "status": "parked_no_validated_actual_solution_enclosure",
            "h019_status": (
                "parked; discrete partial-source evidence preserved, continuum "
                "persistence unresolved"
            ),
            "annular_galileon_line": (
                "parked; do not reopen without materially new theory/data or "
                "explicit user direction"
            ),
            "main_result": (
                "The protocol can be specified exactly, but the current theory "
                "and saved discrete evidence do not certify the actual-solution "
                "Hessian error. Residual tightening, manufactured recovery, and "
                "three coupled grids cannot replace the missing reliability and "
                "between-node regularity bounds."
            ),
            "next_action": (
                "Move to the diversified rapid-falsification portfolio; retain "
                "the row-action protocol only as dormant documentation."
            ),
        },
        "resource_accounting": {
            "elapsed_seconds": time.perf_counter() - started,
            "checkpoint_reads": 0,
            "field_reads": 0,
            "pde_builds": 0,
            "pde_solves": 0,
            "new_grids_built": 0,
        },
    }


def _write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
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
        f"definitions_complete={decision['mathematical_gate_definitions_complete']}; "
        f"pde_solves={report['resource_accounting']['pde_solves']}; "
        f"elapsed={report['resource_accounting']['elapsed_seconds']:.3f}s"
    )
    return 0 if decision["analysis_completed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

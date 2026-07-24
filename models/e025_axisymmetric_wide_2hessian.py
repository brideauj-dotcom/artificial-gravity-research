#!/usr/bin/env python3
"""Axisymmetric wide-directional 2-Hessian validation core for E-025.

This module is deliberately standalone.  It does not import the E-023 or E-024
mapped-spherical grids, Hessians, residuals, gradients, fluxes, or solvers.
Instead it represents an axisymmetric field on the meridional ``(rho, z)``
quarter-disk and applies the shifted 2-Hessian through directional second
differences.

For ``c3 > 0`` the dimensionless cubic-Galileon equation

    Delta(phi) + c3 * (Delta(phi)**2 - Hess(phi):Hess(phi)) = source

is equivalent to

    sigma_2(D2 u) = 3 / (16 c3**2) + source / (2 c3),
    u = phi + |x|**2 / (8 c3).

For an axisymmetric Hessian, an eigenbasis contains the azimuthal direction.
The remaining eigenvectors lie in the meridional plane.  We therefore search
over wide, orthogonal meridional direction pairs and approximate the
azimuthal curvature with an outward circular chord.  The discrete operator is
monotone in its field differences, but the published Cartesian convergence
proof for wide-stencil 2-Hessian schemes does not automatically cover this
axisymmetric reduction or its shortened curved-boundary stencils.  The
manufactured-solution checks in this module are consequently required parts of
the validation, not optional examples.

This is a numerical artifact for a hypothetical field equation.  It is not
evidence for a new field, useful artificial gravity, FTL travel, inertial
control, or reactionless propulsion.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import time
from typing import Any, Callable

import numpy as np
from scipy import sparse
from scipy.sparse import linalg as sparse_linalg


ScalarField = Callable[[float, float], float]


@dataclass(frozen=True)
class AxisymmetricGrid:
    """Uniform nodal grid on ``rho >= 0, z >= 0, rho**2 + z**2 < R**2``."""

    radial_max: float
    spacing: float
    directional_radius: int = 1

    def validate(self) -> None:
        if self.radial_max <= 0.0:
            raise ValueError("radial_max must be positive")
        if self.spacing <= 0.0:
            raise ValueError("spacing must be positive")
        ratio = self.radial_max / self.spacing
        if not math.isclose(ratio, round(ratio), rel_tol=0.0, abs_tol=1.0e-10):
            raise ValueError("radial_max must be an integer multiple of spacing")
        if self.directional_radius < 1:
            raise ValueError("directional_radius must be at least one")

    @property
    def intervals(self) -> int:
        self.validate()
        return int(round(self.radial_max / self.spacing))


@dataclass(frozen=True)
class SmoothAnnulusSpec:
    """Continuous broad-source parameters fixed by the E-024 campaign."""

    inner_radius: float = 8.0
    outer_radius: float = 30.0
    half_opening_angle: float = 0.05
    mu: float = 36.8
    radial_smoothing_width: float = 6.0
    angular_smoothing_width: float = 0.10

    def validate(self, radial_max: float) -> None:
        if not 0.0 <= self.inner_radius < self.outer_radius < radial_max:
            raise ValueError("require 0 <= inner_radius < outer_radius < radial_max")
        if self.mu < 0.0:
            raise ValueError("mu must be non-negative")
        if self.radial_smoothing_width <= 0.0:
            raise ValueError("radial smoothing width must be positive")
        if self.angular_smoothing_width <= 0.0:
            raise ValueError("angular smoothing width must be positive")
        if self.inner_radius - self.radial_smoothing_width / 2.0 < 0.0:
            raise ValueError("inner smoothing layer crosses the origin")
        if self.outer_radius + self.radial_smoothing_width / 2.0 >= radial_max:
            raise ValueError("outer smoothing layer reaches the boundary")
        if self.angular_smoothing_width > 2.0 * self.half_opening_angle:
            raise ValueError("angular smoothing width exceeds twice theta0")


@dataclass(frozen=True)
class DirectionalOperator:
    """Linear field contribution plus known Dirichlet-boundary contribution."""

    matrix: sparse.csr_matrix
    boundary_offset: np.ndarray


@dataclass
class WideStencilSystem:
    grid: AxisymmetricGrid
    cubic_coefficient: float
    rho: np.ndarray
    z: np.ndarray
    index_map: np.ndarray
    bases: tuple[tuple[int, int], ...]
    meridional_operators: tuple[
        tuple[DirectionalOperator, DirectionalOperator], ...
    ]
    azimuthal_operator: DirectionalOperator

    @property
    def size(self) -> int:
        return int(self.rho.size)

    @property
    def shift(self) -> float:
        return 1.0 / (4.0 * self.cubic_coefficient)


@dataclass(frozen=True)
class ContinuationStage:
    amplitude: float
    newton_iterations: int
    gmres_iterations: int
    relative_residual_l2: float
    minimum_pair_sum: float
    minimum_spatial_principal: float
    minimum_time_kinetic: float
    preconditioner_kind: str = "linearized"
    preconditioner_setups: int = 0
    preconditioner_setup_seconds: float = 0.0
    preconditioner_factor_nnz_max: int = 0


@dataclass(frozen=True)
class ContinuationCheckpoint:
    """Restart state for one fixed grid, source, and continuation schedule."""

    field: np.ndarray
    completed_amplitude: float
    target_amplitude: float
    stage_complete: bool
    stages: tuple[ContinuationStage, ...]
    current_newton_iterations: int
    current_gmres_iterations: int
    current_preconditioner_setups: int
    current_preconditioner_setup_seconds: float
    current_preconditioner_factor_nnz_max: int
    preconditioner_kind: str
    ilu_drop_tolerance: float
    ilu_fill_factor: float


@dataclass
class WideSolution:
    system: WideStencilSystem
    source: np.ndarray
    field: np.ndarray
    linear_field: np.ndarray
    stages: list[ContinuationStage]
    relative_residual_l2: float
    relative_residual_linf: float
    minimum_pair_sum: float
    minimum_spatial_principal: float
    minimum_time_kinetic: float


def primitive_meridional_bases(radius: int) -> tuple[tuple[int, int], ...]:
    """Return unique unoriented integer bases up to quarter-turn symmetry."""

    if radius < 1:
        raise ValueError("directional radius must be at least one")
    bases: list[tuple[int, int]] = []
    for first in range(1, radius + 1):
        # ``-first`` is the same unoriented basis as ``+first`` after swapping
        # the perpendicular vectors, so retain only one diagonal endpoint.
        for second in range(-first + 1, first + 1):
            if math.gcd(first, abs(second)) == 1:
                bases.append((first, second))
    return tuple(bases)


def directional_resolution(radius: int) -> float:
    """Return the worst angular distance to the nearest available basis."""

    angles = sorted(
        {
            math.atan2(second, first) % (math.pi / 2.0)
            for first, second in primitive_meridional_bases(radius)
        }
    )
    gaps = [angles[index + 1] - angles[index] for index in range(len(angles) - 1)]
    gaps.append(angles[0] + math.pi / 2.0 - angles[-1])
    return 0.5 * max(gaps)


def monotone_sigma_extension(values: np.ndarray) -> np.ndarray:
    """Froese-style coordinatewise non-decreasing extension of ``sigma_2``.

    The three directional curvatures occupy the final array axis.
    """

    array = np.asarray(values, dtype=float)
    if array.shape[-1] != 3:
        raise ValueError("the final values axis must have length three")
    ordered = np.sort(array, axis=-1)
    first = ordered[..., 0]
    second = np.maximum(ordered[..., 1], np.abs(first))
    third = np.maximum(ordered[..., 2], np.abs(first))
    return first * second + first * third + second * third


def monotone_sigma_gradient(values: np.ndarray) -> np.ndarray:
    """Return one semismooth derivative of the monotone sigma extension."""

    array = np.asarray(values, dtype=float)
    if array.shape[-1] != 3:
        raise ValueError("the final values axis must have length three")
    order = np.argsort(array, axis=-1, kind="stable")
    ordered = np.take_along_axis(array, order, axis=-1)
    first, second, third = (ordered[..., index] for index in range(3))
    ordered_gradient = np.zeros_like(ordered)
    admissible = first + second >= 0.0
    ordered_gradient[..., 0] = np.where(admissible, second + third, -2.0 * first)
    ordered_gradient[..., 1] = np.where(admissible, first + third, 0.0)
    ordered_gradient[..., 2] = np.where(admissible, first + second, 0.0)
    gradient = np.empty_like(ordered_gradient)
    np.put_along_axis(gradient, order, ordered_gradient, axis=-1)
    return gradient


def _grid_nodes(
    grid: AxisymmetricGrid,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    grid.validate()
    coordinates = np.arange(grid.intervals + 1, dtype=float) * grid.spacing
    rho_mesh, z_mesh = np.meshgrid(coordinates, coordinates, indexing="ij")
    tolerance = 64.0 * np.finfo(float).eps * grid.radial_max**2
    interior = rho_mesh**2 + z_mesh**2 < grid.radial_max**2 - tolerance
    index_map = np.full(interior.shape, -1, dtype=int)
    index_map[interior] = np.arange(int(np.count_nonzero(interior)))
    return rho_mesh[interior], z_mesh[interior], index_map, interior


def _boundary_distance(
    rho: float,
    z: float,
    direction_rho: float,
    direction_z: float,
    radial_max: float,
) -> float:
    projection = rho * direction_rho + z * direction_z
    discriminant = projection**2 + radial_max**2 - rho**2 - z**2
    if discriminant <= 0.0:
        raise RuntimeError("failed to intersect a wide direction with the boundary")
    distance = -projection + math.sqrt(discriminant)
    if distance <= 0.0:
        raise RuntimeError("non-positive wide-stencil boundary distance")
    return distance


def _directional_operator(
    grid: AxisymmetricGrid,
    index_map: np.ndarray,
    direction: tuple[int, int],
    boundary_phi: ScalarField,
) -> DirectionalOperator:
    """Build a reflected/shortened second directional difference."""

    norm = math.hypot(*direction)
    unit = (direction[0] / norm, direction[1] / norm)
    full_distance = grid.spacing * norm
    node_indices = np.argwhere(index_map >= 0)
    size = node_indices.shape[0]
    rows: list[int] = []
    columns: list[int] = []
    data: list[float] = []
    boundary_offset = np.zeros(size, dtype=float)

    for grid_i, grid_j in node_indices:
        row = int(index_map[grid_i, grid_j])
        rho = float(grid_i) * grid.spacing
        z = float(grid_j) * grid.spacing
        endpoints: list[tuple[float, int | None, float]] = []
        for sign in (1, -1):
            raw_i = int(grid_i) + sign * direction[0]
            raw_j = int(grid_j) + sign * direction[1]
            endpoint_rho = rho + sign * direction[0] * grid.spacing
            endpoint_z = z + sign * direction[1] * grid.spacing
            if endpoint_rho**2 + endpoint_z**2 < grid.radial_max**2 - 1.0e-13:
                reflected_i = abs(raw_i)
                reflected_j = abs(raw_j)
                column = int(index_map[reflected_i, reflected_j])
                if column < 0:
                    raise RuntimeError("an interior reflected endpoint is not an unknown")
                endpoints.append((full_distance, column, 0.0))
            else:
                signed_unit = (sign * unit[0], sign * unit[1])
                distance = _boundary_distance(
                    rho, z, signed_unit[0], signed_unit[1], grid.radial_max
                )
                boundary_rho = abs(rho + distance * signed_unit[0])
                boundary_z = abs(z + distance * signed_unit[1])
                endpoints.append(
                    (
                        distance,
                        None,
                        float(boundary_phi(boundary_rho, boundary_z)),
                    )
                )

        plus_distance, plus_column, plus_value = endpoints[0]
        minus_distance, minus_column, minus_value = endpoints[1]
        common = 2.0 / (plus_distance + minus_distance)
        plus_coefficient = common / plus_distance
        minus_coefficient = common / minus_distance
        centre_coefficient = -2.0 / (plus_distance * minus_distance)
        rows.append(row)
        columns.append(row)
        data.append(centre_coefficient)
        if plus_column is None:
            boundary_offset[row] += plus_coefficient * plus_value
        else:
            rows.append(row)
            columns.append(plus_column)
            data.append(plus_coefficient)
        if minus_column is None:
            boundary_offset[row] += minus_coefficient * minus_value
        else:
            rows.append(row)
            columns.append(minus_column)
            data.append(minus_coefficient)

    matrix = sparse.csr_matrix((data, (rows, columns)), shape=(size, size))
    return DirectionalOperator(matrix=matrix, boundary_offset=boundary_offset)


def _azimuthal_operator(
    grid: AxisymmetricGrid,
    index_map: np.ndarray,
    boundary_phi: ScalarField,
) -> DirectionalOperator:
    """Approximate ``u_rho/rho`` by a monotone outward circular chord."""

    node_indices = np.argwhere(index_map >= 0)
    size = node_indices.shape[0]
    rows: list[int] = []
    columns: list[int] = []
    data: list[float] = []
    boundary_offset = np.zeros(size, dtype=float)

    for grid_i, grid_j in node_indices:
        row = int(index_map[grid_i, grid_j])
        rho = float(grid_i) * grid.spacing
        z = float(grid_j) * grid.spacing
        candidate_rho = rho + grid.spacing
        if candidate_rho**2 + z**2 < grid.radial_max**2 - 1.0e-13:
            column = int(index_map[int(grid_i) + 1, grid_j])
            if column < 0:
                raise RuntimeError("an interior azimuthal endpoint is not an unknown")
            target_rho = candidate_rho
            boundary_value = 0.0
        else:
            target_rho = math.sqrt(max(grid.radial_max**2 - z**2, 0.0))
            column = None
            boundary_value = float(boundary_phi(target_rho, z))
        chord_squared = target_rho**2 - rho**2
        if chord_squared <= 0.0:
            raise RuntimeError("non-positive azimuthal chord length")
        coefficient = 2.0 / chord_squared
        rows.append(row)
        columns.append(row)
        data.append(-coefficient)
        if column is None:
            boundary_offset[row] += coefficient * boundary_value
        else:
            rows.append(row)
            columns.append(column)
            data.append(coefficient)

    matrix = sparse.csr_matrix((data, (rows, columns)), shape=(size, size))
    return DirectionalOperator(matrix=matrix, boundary_offset=boundary_offset)


def build_system(
    grid: AxisymmetricGrid,
    cubic_coefficient: float = 1.0,
    boundary_phi: ScalarField | None = None,
) -> WideStencilSystem:
    """Construct all independent wide-directional operators for a grid."""

    grid.validate()
    if cubic_coefficient <= 0.0:
        raise ValueError("the shifted formulation requires c3 > 0")
    if boundary_phi is None:
        boundary_phi = lambda _rho, _z: 0.0
    rho, z, index_map, _ = _grid_nodes(grid)
    bases = primitive_meridional_bases(grid.directional_radius)
    meridional: list[tuple[DirectionalOperator, DirectionalOperator]] = []
    for first, second in bases:
        primary = _directional_operator(
            grid, index_map, (first, second), boundary_phi
        )
        perpendicular = _directional_operator(
            grid, index_map, (-second, first), boundary_phi
        )
        meridional.append((primary, perpendicular))
    return WideStencilSystem(
        grid=grid,
        cubic_coefficient=cubic_coefficient,
        rho=rho,
        z=z,
        index_map=index_map,
        bases=bases,
        meridional_operators=tuple(meridional),
        azimuthal_operator=_azimuthal_operator(grid, index_map, boundary_phi),
    )


def field_from_callable(system: WideStencilSystem, field: ScalarField) -> np.ndarray:
    return np.array(
        [field(float(rho), float(z)) for rho, z in zip(system.rho, system.z)],
        dtype=float,
    )


def directional_curvatures(
    system: WideStencilSystem,
    field: np.ndarray,
) -> np.ndarray:
    """Return shifted curvatures with shape ``(basis, node, component)``."""

    values = np.asarray(field, dtype=float)
    if values.shape != (system.size,):
        raise ValueError("field shape does not match the wide-stencil system")
    azimuthal = (
        system.azimuthal_operator.matrix @ values
        + system.azimuthal_operator.boundary_offset
        + system.shift
    )
    result = np.empty((len(system.bases), system.size, 3), dtype=float)
    for basis_index, (primary, perpendicular) in enumerate(
        system.meridional_operators
    ):
        result[basis_index, :, 0] = (
            primary.matrix @ values + primary.boundary_offset + system.shift
        )
        result[basis_index, :, 1] = (
            perpendicular.matrix @ values
            + perpendicular.boundary_offset
            + system.shift
        )
        result[basis_index, :, 2] = azimuthal
    return result


def monotone_operator(
    system: WideStencilSystem,
    field: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    curvatures = directional_curvatures(system, field)
    candidates = monotone_sigma_extension(curvatures)
    active = np.argmin(candidates, axis=0)
    nodes = np.arange(system.size)
    return candidates[active, nodes], active, curvatures


def shifted_rhs(source: np.ndarray, cubic_coefficient: float) -> np.ndarray:
    if cubic_coefficient <= 0.0:
        raise ValueError("the shifted formulation requires c3 > 0")
    return 3.0 / (16.0 * cubic_coefficient**2) + np.asarray(source) / (
        2.0 * cubic_coefficient
    )


def shifted_residual(
    system: WideStencilSystem,
    field: np.ndarray,
    source: np.ndarray,
) -> np.ndarray:
    if np.asarray(source).shape != (system.size,):
        raise ValueError("source shape does not match the wide-stencil system")
    operator, _, _ = monotone_operator(system, field)
    return operator - shifted_rhs(source, system.cubic_coefficient)


def scheme_diagnostics(
    system: WideStencilSystem,
    curvatures: np.ndarray,
) -> tuple[float, float, float]:
    """Return minimum pair sum, spatial principal value, and time coefficient."""

    ordered = np.sort(curvatures, axis=-1)
    minimum_pair = float(np.min(ordered[..., 0] + ordered[..., 1]))
    minimum_spatial = 2.0 * system.cubic_coefficient * minimum_pair
    trace_phi = np.sum(curvatures, axis=-1) - 3.0 * system.shift
    minimum_time = float(
        np.min(1.0 + 2.0 * system.cubic_coefficient * trace_phi)
    )
    return minimum_pair, minimum_spatial, minimum_time


def _basis_index(system: WideStencilSystem, basis: tuple[int, int]) -> int:
    try:
        return system.bases.index(basis)
    except ValueError as error:
        raise ValueError(f"required meridional basis {basis} is unavailable") from error


def fixed_coordinate_hessian_components(
    system: WideStencilSystem,
    field: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return an unshifted cylindrical Hessian from fixed coordinate frames.

    This diagnostic deliberately does not minimize over the wide frames. The
    ``(1, 0)`` frame supplies ``phi_rhorho`` and ``phi_zz``; the difference of
    the ``(1, 1)`` and ``(-1, 1)`` directional curvatures supplies
    ``phi_rhoz``. It is a fixed-stencil check on the wide solution, not a
    second independent discretization.
    """

    values = np.asarray(field, dtype=float)
    if values.shape != (system.size,):
        raise ValueError("field shape does not match the wide-stencil system")
    axial_index = _basis_index(system, (1, 0))
    diagonal_index = _basis_index(system, (1, 1))
    radial_operator, axial_operator = system.meridional_operators[axial_index]
    positive_diagonal, negative_diagonal = system.meridional_operators[
        diagonal_index
    ]
    radial = radial_operator.matrix @ values + radial_operator.boundary_offset
    axial = axial_operator.matrix @ values + axial_operator.boundary_offset
    diagonal_plus = (
        positive_diagonal.matrix @ values + positive_diagonal.boundary_offset
    )
    diagonal_minus = (
        negative_diagonal.matrix @ values + negative_diagonal.boundary_offset
    )
    mixed = 0.5 * (diagonal_plus - diagonal_minus)
    azimuthal = (
        system.azimuthal_operator.matrix @ values
        + system.azimuthal_operator.boundary_offset
    )
    return radial, mixed, axial, azimuthal


def coordinate_laplacian(
    system: WideStencilSystem,
) -> tuple[sparse.csc_matrix, np.ndarray]:
    """Return the fixed cylindrical Laplacian and its boundary offset."""

    basis_index = _basis_index(system, (1, 0))
    radial, axial = system.meridional_operators[basis_index]
    matrix = (
        radial.matrix + axial.matrix + system.azimuthal_operator.matrix
    ).tocsc()
    offset = (
        radial.boundary_offset
        + axial.boundary_offset
        + system.azimuthal_operator.boundary_offset
    )
    return matrix, offset


def solve_linear_reference(
    system: WideStencilSystem,
    source: np.ndarray,
    factor: Any | None = None,
) -> np.ndarray:
    """Solve ``Delta(phi_linear)=source`` on the cylindrical grid."""

    values = np.asarray(source, dtype=float)
    if values.shape != (system.size,):
        raise ValueError("source shape does not match the wide-stencil system")
    matrix, offset = coordinate_laplacian(system)
    if factor is None:
        factor = sparse_linalg.splu(matrix)
    return np.asarray(factor.solve(values - offset), dtype=float)


def nodal_volume_weights(system: WideStencilSystem) -> np.ndarray:
    """Return full-volume cylindrical weights for the quarter-disk nodes."""

    reflection_weight = np.where(
        np.isclose(system.z, 0.0, rtol=0.0, atol=1.0e-13), 0.5, 1.0
    )
    return (
        4.0
        * math.pi
        * system.grid.spacing**2
        * system.rho
        * reflection_weight
    )


def fixed_coordinate_diagnostics(
    system: WideStencilSystem,
    field: np.ndarray,
    source: np.ndarray,
) -> dict[str, float]:
    """Evaluate original-equation, White-root, and fixed-frame branch checks.

    White et al.'s normal-root form is algebraically equivalent to the cubic
    equation only on the selected attractive branch. Reporting it alongside
    the unsquared residual helps expose a wrong root or a fixed-coordinate
    inconsistency that a small monotone residual alone could hide.
    """

    values = np.asarray(source, dtype=float)
    if values.shape != (system.size,):
        raise ValueError("source shape does not match the wide-stencil system")
    c3 = system.cubic_coefficient
    h_rr, h_rz, h_zz, h_pp = fixed_coordinate_hessian_components(system, field)
    trace = h_rr + h_zz + h_pp
    norm_squared = h_rr**2 + h_zz**2 + h_pp**2 + 2.0 * h_rz**2
    original = trace + c3 * (trace**2 - norm_squared) - values
    radicand = norm_squared + values / c3 + 1.0 / (4.0 * c3**2)
    white = (
        np.sqrt(np.maximum(radicand, 0.0))
        - trace
        - 1.0 / (2.0 * c3)
    )
    meridional_gap = np.sqrt((h_rr - h_zz) ** 2 + 4.0 * h_rz**2)
    eigen_low = 0.5 * (h_rr + h_zz - meridional_gap)
    eigen_high = 0.5 * (h_rr + h_zz + meridional_gap)
    eigenvalues = np.sort(
        np.stack((eigen_low, eigen_high, h_pp), axis=-1), axis=-1
    )
    pair_sum = eigenvalues[:, 0] + eigenvalues[:, 1]
    spatial = 1.0 + 2.0 * c3 * pair_sum
    time = 1.0 + 2.0 * c3 * trace
    spatial_index = int(np.argmin(spatial))
    time_index = int(np.argmin(time))
    weights = nodal_volume_weights(system)
    original_scale = max(
        float(np.sqrt(np.sum(weights * values**2))), np.finfo(float).tiny
    )
    white_scale = max(
        float(np.sqrt(np.sum(weights * (values / c3) ** 2))),
        np.finfo(float).tiny,
    )
    return {
        "original_relative_volume_l2": float(
            np.sqrt(np.sum(weights * original**2)) / original_scale
        ),
        "original_relative_linf": float(
            np.max(np.abs(original))
            / max(float(np.max(np.abs(values))), np.finfo(float).tiny)
        ),
        "white_root_relative_volume_l2": float(
            np.sqrt(np.sum(weights * white**2)) / white_scale
        ),
        "minimum_white_radicand": float(np.min(radicand)),
        "negative_white_radicand_nodes": float(np.count_nonzero(radicand < 0.0)),
        "minimum_spatial_principal": float(spatial[spatial_index]),
        "minimum_spatial_rho": float(system.rho[spatial_index]),
        "minimum_spatial_z": float(system.z[spatial_index]),
        "minimum_time_kinetic": float(time[time_index]),
        "minimum_time_rho": float(system.rho[time_index]),
        "minimum_time_z": float(system.z[time_index]),
    }


def scheme_diagnostic_details(
    system: WideStencilSystem,
    field: np.ndarray,
) -> dict[str, float | int]:
    """Locate conservative all-frame and active-frame branch minima."""

    _, active, curvatures = monotone_operator(system, field)
    ordered = np.sort(curvatures, axis=-1)
    all_pair = ordered[..., 0] + ordered[..., 1]
    all_index = np.unravel_index(int(np.argmin(all_pair)), all_pair.shape)
    nodes = np.arange(system.size)
    active_curvatures = curvatures[active, nodes]
    active_ordered = np.sort(active_curvatures, axis=-1)
    active_pair = active_ordered[:, 0] + active_ordered[:, 1]
    active_index = int(np.argmin(active_pair))
    active_trace_phi = np.sum(active_curvatures, axis=-1) - 3.0 * system.shift
    active_time = 1.0 + 2.0 * system.cubic_coefficient * active_trace_phi
    time_index = int(np.argmin(active_time))
    return {
        "all_frame_minimum_pair_sum": float(all_pair[all_index]),
        "all_frame_minimum_basis_index": int(all_index[0]),
        "all_frame_minimum_rho": float(system.rho[all_index[1]]),
        "all_frame_minimum_z": float(system.z[all_index[1]]),
        "active_minimum_pair_sum": float(active_pair[active_index]),
        "active_minimum_basis_index": int(active[active_index]),
        "active_minimum_rho": float(system.rho[active_index]),
        "active_minimum_z": float(system.z[active_index]),
        "active_minimum_time_kinetic": float(active_time[time_index]),
        "active_minimum_time_rho": float(system.rho[time_index]),
        "active_minimum_time_z": float(system.z[time_index]),
    }


def _jacobian_action(
    system: WideStencilSystem,
    active: np.ndarray,
    active_gradient: np.ndarray,
    vector: np.ndarray,
) -> np.ndarray:
    azimuthal = system.azimuthal_operator.matrix @ vector
    result = np.empty(system.size, dtype=float)
    for basis_index, (primary, perpendicular) in enumerate(
        system.meridional_operators
    ):
        mask = active == basis_index
        if not np.any(mask):
            continue
        primary_value = primary.matrix @ vector
        perpendicular_value = perpendicular.matrix @ vector
        result[mask] = (
            active_gradient[mask, 0] * primary_value[mask]
            + active_gradient[mask, 1] * perpendicular_value[mask]
            + active_gradient[mask, 2] * azimuthal[mask]
        )
    return result


def active_jacobian_matrix(
    system: WideStencilSystem,
    active: np.ndarray,
    active_gradient: np.ndarray,
) -> sparse.csr_matrix:
    """Assemble the active semismooth Jacobian once per Newton step.

    The earlier matrix-free action evaluated every directional sparse matrix
    on every GMRES iteration and discarded inactive rows afterward. Row-scaled
    assembly preserves the exact action while making fine-grid Krylov solves
    proportional to one active stencil rather than every candidate frame.
    """

    active_values = np.asarray(active, dtype=int)
    gradient = np.asarray(active_gradient, dtype=float)
    if active_values.shape != (system.size,) or gradient.shape != (
        system.size,
        3,
    ):
        raise ValueError("active Jacobian arrays do not match the system")
    result = system.azimuthal_operator.matrix.multiply(gradient[:, 2, None])
    for basis_index, (primary, perpendicular) in enumerate(
        system.meridional_operators
    ):
        mask = active_values == basis_index
        if not np.any(mask):
            continue
        primary_weight = np.where(mask, gradient[:, 0], 0.0)
        perpendicular_weight = np.where(mask, gradient[:, 1], 0.0)
        result = result + primary.matrix.multiply(primary_weight[:, None])
        result = result + perpendicular.matrix.multiply(
            perpendicular_weight[:, None]
        )
    result.eliminate_zeros()
    return result.tocsr()


def _linearized_zero_matrix(system: WideStencilSystem) -> sparse.csc_matrix:
    primary, perpendicular = system.meridional_operators[0]
    coefficient = 1.0 / (2.0 * system.cubic_coefficient)
    return (
        coefficient
        * (
            primary.matrix
            + perpendicular.matrix
            + system.azimuthal_operator.matrix
        )
    ).tocsc()


def _source_digest(source: np.ndarray) -> str:
    values = np.ascontiguousarray(np.asarray(source, dtype=np.float64))
    return hashlib.sha256(values.view(np.uint8)).hexdigest()


def _system_digest(system: WideStencilSystem) -> str:
    """Fingerprint the discrete operator, including all boundary offsets."""

    cached = getattr(system, "_checkpoint_system_digest", None)
    if cached is not None:
        return str(cached)
    digest = hashlib.sha256()

    def update_array(label: str, values: np.ndarray, dtype: str) -> None:
        array = np.ascontiguousarray(np.asarray(values, dtype=np.dtype(dtype)))
        digest.update(label.encode("utf-8"))
        digest.update(json.dumps(array.shape).encode("ascii"))
        digest.update(array.tobytes())

    digest.update(
        json.dumps(
            {
                "radial_max": system.grid.radial_max,
                "spacing": system.grid.spacing,
                "directional_radius": system.grid.directional_radius,
                "cubic_coefficient": system.cubic_coefficient,
                "bases": system.bases,
            },
            sort_keys=True,
        ).encode("ascii")
    )
    update_array("rho", system.rho, "<f8")
    update_array("z", system.z, "<f8")
    update_array("index_map", system.index_map, "<i8")
    operators = [
        operator
        for pair in system.meridional_operators
        for operator in pair
    ] + [system.azimuthal_operator]
    for index, operator in enumerate(operators):
        matrix = operator.matrix.tocsr()
        update_array(f"operator-{index}-indptr", matrix.indptr, "<i8")
        update_array(f"operator-{index}-indices", matrix.indices, "<i8")
        update_array(f"operator-{index}-data", matrix.data, "<f8")
        update_array(
            f"operator-{index}-boundary", operator.boundary_offset, "<f8"
        )
    result = digest.hexdigest()
    setattr(system, "_checkpoint_system_digest", result)
    return result


def _stage_from_mapping(values: dict[str, Any]) -> ContinuationStage:
    """Load current or older stage metadata without enabling pickle."""

    return ContinuationStage(
        amplitude=float(values["amplitude"]),
        newton_iterations=int(values["newton_iterations"]),
        gmres_iterations=int(values["gmres_iterations"]),
        relative_residual_l2=float(values["relative_residual_l2"]),
        minimum_pair_sum=float(values["minimum_pair_sum"]),
        minimum_spatial_principal=float(values["minimum_spatial_principal"]),
        minimum_time_kinetic=float(values["minimum_time_kinetic"]),
        preconditioner_kind=str(values.get("preconditioner_kind", "linearized")),
        preconditioner_setups=int(values.get("preconditioner_setups", 0)),
        preconditioner_setup_seconds=float(
            values.get("preconditioner_setup_seconds", 0.0)
        ),
        preconditioner_factor_nnz_max=int(
            values.get("preconditioner_factor_nnz_max", 0)
        ),
    )


def save_continuation_checkpoint(
    path: str | Path,
    system: WideStencilSystem,
    source: np.ndarray,
    field: np.ndarray,
    *,
    continuation_steps: int,
    relative_tolerance: float,
    newton_max_iterations: int,
    gmres_relative_tolerance: float,
    gmres_max_iterations: int,
    preconditioner_kind: str,
    ilu_drop_tolerance: float,
    ilu_fill_factor: float,
    completed_amplitude: float,
    target_amplitude: float,
    stage_complete: bool,
    stages: list[ContinuationStage],
    current_newton_iterations: int = 0,
    current_gmres_iterations: int = 0,
    current_preconditioner_setups: int = 0,
    current_preconditioner_setup_seconds: float = 0.0,
    current_preconditioner_factor_nnz_max: int = 0,
) -> None:
    """Atomically save a branch-checked continuation state without pickle."""

    checkpoint_path = Path(path)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = checkpoint_path.with_name(f".{checkpoint_path.name}.tmp")
    metadata = {
        "format_version": 2,
        "radial_max": system.grid.radial_max,
        "spacing": system.grid.spacing,
        "directional_radius": system.grid.directional_radius,
        "cubic_coefficient": system.cubic_coefficient,
        "system_size": system.size,
        "system_digest": _system_digest(system),
        "source_digest": _source_digest(source),
        "continuation_steps": continuation_steps,
        "relative_tolerance": relative_tolerance,
        "newton_max_iterations": newton_max_iterations,
        "gmres_relative_tolerance": gmres_relative_tolerance,
        "gmres_max_iterations": gmres_max_iterations,
        "preconditioner_kind": preconditioner_kind,
        "ilu_drop_tolerance": ilu_drop_tolerance,
        "ilu_fill_factor": ilu_fill_factor,
        "completed_amplitude": completed_amplitude,
        "target_amplitude": target_amplitude,
        "stage_complete": bool(stage_complete),
        "stages": [stage.__dict__ for stage in stages],
        "current_newton_iterations": current_newton_iterations,
        "current_gmres_iterations": current_gmres_iterations,
        "current_preconditioner_setups": current_preconditioner_setups,
        "current_preconditioner_setup_seconds": (
            current_preconditioner_setup_seconds
        ),
        "current_preconditioner_factor_nnz_max": (
            current_preconditioner_factor_nnz_max
        ),
    }
    with temporary_path.open("wb") as handle:
        np.savez_compressed(
            handle,
            field=np.asarray(field, dtype=float),
            metadata_json=np.asarray(json.dumps(metadata, sort_keys=True)),
        )
    temporary_path.replace(checkpoint_path)


def load_continuation_checkpoint(
    path: str | Path,
    system: WideStencilSystem,
    source: np.ndarray,
    *,
    continuation_steps: int,
    relative_tolerance: float,
    newton_max_iterations: int,
    gmres_relative_tolerance: float,
    gmres_max_iterations: int,
) -> ContinuationCheckpoint:
    """Load and validate restart state against the exact grid and source."""

    checkpoint_path = Path(path)
    with np.load(checkpoint_path, allow_pickle=False) as payload:
        field = np.asarray(payload["field"], dtype=float)
        metadata = json.loads(str(payload["metadata_json"].item()))
    expected = {
        "format_version": 2,
        "radial_max": system.grid.radial_max,
        "spacing": system.grid.spacing,
        "directional_radius": system.grid.directional_radius,
        "cubic_coefficient": system.cubic_coefficient,
        "system_size": system.size,
        "system_digest": _system_digest(system),
        "source_digest": _source_digest(source),
        "continuation_steps": continuation_steps,
        "relative_tolerance": relative_tolerance,
        "newton_max_iterations": newton_max_iterations,
        "gmres_relative_tolerance": gmres_relative_tolerance,
        "gmres_max_iterations": gmres_max_iterations,
    }
    for key, expected_value in expected.items():
        actual_value = metadata.get(key)
        if isinstance(expected_value, float):
            matches = actual_value is not None and math.isclose(
                float(actual_value), expected_value, rel_tol=0.0, abs_tol=1.0e-14
            )
        else:
            matches = actual_value == expected_value
        if not matches:
            raise ValueError(
                f"checkpoint {key} does not match the requested solve: "
                f"{actual_value!r} != {expected_value!r}"
            )
    if field.shape != (system.size,) or not np.all(np.isfinite(field)):
        raise ValueError("checkpoint field does not match the requested system")
    completed_amplitude = float(metadata["completed_amplitude"])
    target_amplitude = float(metadata["target_amplitude"])
    if not 0.0 <= completed_amplitude <= target_amplitude <= 1.0:
        raise ValueError("checkpoint amplitudes are invalid")
    return ContinuationCheckpoint(
        field=field,
        completed_amplitude=completed_amplitude,
        target_amplitude=target_amplitude,
        stage_complete=bool(metadata["stage_complete"]),
        stages=tuple(_stage_from_mapping(row) for row in metadata["stages"]),
        current_newton_iterations=int(
            metadata.get("current_newton_iterations", 0)
        ),
        current_gmres_iterations=int(metadata.get("current_gmres_iterations", 0)),
        current_preconditioner_setups=int(
            metadata.get("current_preconditioner_setups", 0)
        ),
        current_preconditioner_setup_seconds=float(
            metadata.get("current_preconditioner_setup_seconds", 0.0)
        ),
        current_preconditioner_factor_nnz_max=int(
            metadata.get("current_preconditioner_factor_nnz_max", 0)
        ),
        preconditioner_kind=str(metadata["preconditioner_kind"]),
        ilu_drop_tolerance=float(metadata["ilu_drop_tolerance"]),
        ilu_fill_factor=float(metadata["ilu_fill_factor"]),
    )


def _active_preconditioner(
    jacobian: sparse.csr_matrix,
    zero_factor: Any,
    kind: str,
    *,
    drop_tolerance: float,
    fill_factor: float,
) -> tuple[sparse_linalg.LinearOperator, float, int]:
    """Build the requested inverse action and report setup cost/fill."""

    if kind == "linearized":
        return (
            sparse_linalg.LinearOperator(jacobian.shape, matvec=zero_factor.solve),
            0.0,
            0,
        )
    if kind != "active_ilu":
        raise ValueError("preconditioner_kind must be 'linearized' or 'active_ilu'")
    started = time.perf_counter()
    factor = sparse_linalg.spilu(
        jacobian.tocsc(),
        drop_tol=drop_tolerance,
        fill_factor=fill_factor,
        permc_spec="COLAMD",
    )
    elapsed = time.perf_counter() - started
    factor_nnz = int(factor.L.nnz + factor.U.nnz)
    return (
        sparse_linalg.LinearOperator(jacobian.shape, matvec=factor.solve),
        elapsed,
        factor_nnz,
    )


def solve_continuation(
    system: WideStencilSystem,
    source: np.ndarray,
    continuation_steps: int = 4,
    relative_tolerance: float = 1.0e-8,
    newton_max_iterations: int = 15,
    gmres_relative_tolerance: float = 1.0e-9,
    gmres_max_iterations: int = 30,
    initial_field: np.ndarray | None = None,
    preconditioner_kind: str = "linearized",
    ilu_drop_tolerance: float = 1.0e-3,
    ilu_fill_factor: float = 10.0,
    checkpoint_path: str | Path | None = None,
    resume_checkpoint: bool = False,
) -> WideSolution:
    """Follow the admissible normal branch with damped semismooth Newton steps.

    A supplied ``initial_field`` is intended for a nested-grid full-source
    start and should normally be paired with ``continuation_steps=1``.
    Checkpoints contain only accepted fields and reconstructible metadata;
    active frames, Jacobians, ILU factors, and Krylov bases are rebuilt.
    """

    source_values = np.asarray(source, dtype=float)
    if source_values.shape != (system.size,):
        raise ValueError("source shape does not match the wide-stencil system")
    if np.min(source_values) < 0.0:
        raise ValueError("this validation solver requires a non-negative source")
    if continuation_steps < 1 or newton_max_iterations < 1:
        raise ValueError("iteration counts must be positive")
    if relative_tolerance <= 0.0 or gmres_relative_tolerance <= 0.0:
        raise ValueError("solver tolerances must be positive")
    if preconditioner_kind not in {"linearized", "active_ilu"}:
        raise ValueError("preconditioner_kind must be 'linearized' or 'active_ilu'")
    if not 0.0 <= ilu_drop_tolerance <= 1.0:
        raise ValueError("ilu_drop_tolerance must lie between zero and one")
    if ilu_fill_factor < 1.0:
        raise ValueError("ilu_fill_factor must be at least one")
    if resume_checkpoint and checkpoint_path is None:
        raise ValueError("resume_checkpoint requires checkpoint_path")
    if resume_checkpoint and initial_field is not None:
        raise ValueError("resume_checkpoint and initial_field are mutually exclusive")

    amplitudes = np.linspace(1.0 / continuation_steps, 1.0, continuation_steps)
    field = np.zeros(system.size, dtype=float)
    stages: list[ContinuationStage] = []
    start_index = 0
    resumed_incomplete_stage = False
    resumed_newton_iterations = 0
    resumed_gmres_iterations = 0
    resumed_preconditioner_setups = 0
    resumed_preconditioner_setup_seconds = 0.0
    resumed_preconditioner_factor_nnz_max = 0
    if initial_field is not None:
        field = np.asarray(initial_field, dtype=float).copy()
        if field.shape != (system.size,):
            raise ValueError("initial field shape does not match the system")
        if not np.all(np.isfinite(field)):
            raise ValueError("initial field must be finite")
    elif resume_checkpoint:
        checkpoint = load_continuation_checkpoint(
            checkpoint_path,
            system,
            source_values,
            continuation_steps=continuation_steps,
            relative_tolerance=relative_tolerance,
            newton_max_iterations=newton_max_iterations,
            gmres_relative_tolerance=gmres_relative_tolerance,
            gmres_max_iterations=gmres_max_iterations,
        )
        has_incomplete_stage_work = not checkpoint.stage_complete and any(
            (
                checkpoint.current_newton_iterations,
                checkpoint.current_gmres_iterations,
                checkpoint.current_preconditioner_setups,
            )
        )
        same_preconditioner = (
            preconditioner_kind == checkpoint.preconditioner_kind
            and (
                preconditioner_kind != "active_ilu"
                or (
                    math.isclose(
                        ilu_drop_tolerance,
                        checkpoint.ilu_drop_tolerance,
                        rel_tol=0.0,
                        abs_tol=1.0e-15,
                    )
                    and math.isclose(
                        ilu_fill_factor,
                        checkpoint.ilu_fill_factor,
                        rel_tol=0.0,
                        abs_tol=1.0e-14,
                    )
                )
            )
        )
        if has_incomplete_stage_work and not same_preconditioner:
            raise ValueError(
                "cannot change preconditioner after accepted work in an "
                "incomplete continuation stage"
            )
        field = checkpoint.field.copy()
        stages = list(checkpoint.stages)
        matches = np.flatnonzero(
            np.isclose(amplitudes, checkpoint.target_amplitude, rtol=0.0, atol=1.0e-14)
        )
        if matches.size != 1:
            raise ValueError("checkpoint target amplitude is outside the schedule")
        target_index = int(matches[0])
        if checkpoint.stage_complete:
            start_index = target_index + 1
        else:
            start_index = target_index
            resumed_incomplete_stage = True
            resumed_newton_iterations = checkpoint.current_newton_iterations
            resumed_gmres_iterations = checkpoint.current_gmres_iterations
            resumed_preconditioner_setups = (
                checkpoint.current_preconditioner_setups
            )
            resumed_preconditioner_setup_seconds = (
                checkpoint.current_preconditioner_setup_seconds
            )
            resumed_preconditioner_factor_nnz_max = (
                checkpoint.current_preconditioner_factor_nnz_max
            )
        if len(stages) != target_index + int(checkpoint.stage_complete):
            raise ValueError("checkpoint stage history does not match its amplitude")

    # A restart or externally supplied field must not bypass the branch gate
    # merely because its nonlinear residual is already small.
    _, _, initial_curvatures = monotone_operator(system, field)
    initial_pair, _, initial_time = scheme_diagnostics(system, initial_curvatures)
    if initial_pair <= 0.0 or initial_time <= 0.0:
        raise ValueError(
            "initial or checkpoint field is outside the admissible normal branch"
        )

    source_norm = float(np.linalg.norm(source_values))
    if source_norm == 0.0:
        field = np.zeros(system.size, dtype=float)
        _, _, curvatures = monotone_operator(system, field)
        pair, spatial, time = scheme_diagnostics(system, curvatures)
        return WideSolution(
            system=system,
            source=source_values,
            field=field,
            linear_field=field.copy(),
            stages=[],
            relative_residual_l2=0.0,
            relative_residual_linf=0.0,
            minimum_pair_sum=pair,
            minimum_spatial_principal=spatial,
            minimum_time_kinetic=time,
        )

    laplacian, laplacian_offset = coordinate_laplacian(system)
    coefficient = 1.0 / (2.0 * system.cubic_coefficient)
    zero_factor = sparse_linalg.splu((coefficient * laplacian).tocsc())
    linear_field = np.asarray(
        zero_factor.solve(
            source_values / (2.0 * system.cubic_coefficient)
            - coefficient * laplacian_offset
        ),
        dtype=float,
    )

    for stage_index in range(start_index, continuation_steps):
        amplitude = float(amplitudes[stage_index])
        stage_source = amplitude * source_values
        stage_scale = max(
            float(np.linalg.norm(stage_source))
            / (2.0 * system.cubic_coefficient),
            np.finfo(float).tiny,
        )
        continuing = resumed_incomplete_stage and stage_index == start_index
        newton_offset = resumed_newton_iterations if continuing else 0
        total_gmres = resumed_gmres_iterations if continuing else 0
        preconditioner_setups = (
            resumed_preconditioner_setups if continuing else 0
        )
        preconditioner_setup_seconds = (
            resumed_preconditioner_setup_seconds if continuing else 0.0
        )
        preconditioner_factor_nnz_max = (
            resumed_preconditioner_factor_nnz_max if continuing else 0
        )
        converged = False
        stage_newton_iterations = newton_offset
        remaining_newton_iterations = newton_max_iterations - newton_offset
        if remaining_newton_iterations <= 0:
            raise RuntimeError(
                "checkpoint has already exhausted the Newton iteration cap at "
                f"amplitude {amplitude:.6g}"
            )
        for local_newton_iteration in range(1, remaining_newton_iterations + 1):
            stage_newton_iterations = newton_offset + local_newton_iteration
            operator, active, curvatures = monotone_operator(system, field)
            residual = operator - shifted_rhs(
                stage_source, system.cubic_coefficient
            )
            residual_norm = float(np.linalg.norm(residual))
            if residual_norm / stage_scale < relative_tolerance:
                converged = True
                break
            if checkpoint_path is not None:
                save_continuation_checkpoint(
                    checkpoint_path,
                    system,
                    source_values,
                    field,
                    continuation_steps=continuation_steps,
                    relative_tolerance=relative_tolerance,
                    newton_max_iterations=newton_max_iterations,
                    gmres_relative_tolerance=gmres_relative_tolerance,
                    gmres_max_iterations=gmres_max_iterations,
                    preconditioner_kind=preconditioner_kind,
                    ilu_drop_tolerance=ilu_drop_tolerance,
                    ilu_fill_factor=ilu_fill_factor,
                    completed_amplitude=stages[-1].amplitude if stages else 0.0,
                    target_amplitude=amplitude,
                    stage_complete=False,
                    stages=stages,
                    current_newton_iterations=stage_newton_iterations - 1,
                    current_gmres_iterations=total_gmres,
                    current_preconditioner_setups=preconditioner_setups,
                    current_preconditioner_setup_seconds=(
                        preconditioner_setup_seconds
                    ),
                    current_preconditioner_factor_nnz_max=(
                        preconditioner_factor_nnz_max
                    ),
                )
            nodes = np.arange(system.size)
            active_curvatures = curvatures[active, nodes]
            active_gradient = monotone_sigma_gradient(active_curvatures)
            jacobian = active_jacobian_matrix(system, active, active_gradient)
            try:
                preconditioner, setup_seconds, factor_nnz = _active_preconditioner(
                    jacobian,
                    zero_factor,
                    preconditioner_kind,
                    drop_tolerance=ilu_drop_tolerance,
                    fill_factor=ilu_fill_factor,
                )
            except (MemoryError, RuntimeError) as error:
                pair, spatial, time_coefficient = scheme_diagnostics(
                    system, curvatures
                )
                raise RuntimeError(
                    f"{preconditioner_kind} setup failed at amplitude "
                    f"{amplitude:.6g}; newton_iteration={stage_newton_iterations}; "
                    f"relative_residual={residual_norm / stage_scale:.6e}; "
                    f"minimum_pair_sum={pair:.6e}; "
                    f"minimum_spatial_principal={spatial:.6e}; "
                    f"minimum_time_kinetic={time_coefficient:.6e}"
                ) from error
            if preconditioner_kind == "active_ilu":
                preconditioner_setups += 1
                preconditioner_setup_seconds += setup_seconds
                preconditioner_factor_nnz_max = max(
                    preconditioner_factor_nnz_max, factor_nnz
                )
            counter = [0]

            def count_iteration(_: np.ndarray) -> None:
                counter[0] += 1

            correction, info = sparse_linalg.gmres(
                jacobian,
                -residual,
                M=preconditioner,
                rtol=gmres_relative_tolerance,
                atol=0.0,
                restart=min(50, system.size),
                maxiter=gmres_max_iterations,
                callback=count_iteration,
                callback_type="pr_norm",
            )
            total_gmres += counter[0]
            if info != 0 or not np.all(np.isfinite(correction)):
                pair, spatial, time = scheme_diagnostics(system, curvatures)
                raise RuntimeError(
                    "wide-stencil GMRES failed at amplitude "
                    f"{amplitude:.6g}; info={info}; "
                    f"newton_iteration={stage_newton_iterations}; "
                    f"stage_gmres_iterations={total_gmres}; "
                    f"relative_residual={residual_norm / stage_scale:.6e}; "
                    f"minimum_pair_sum={pair:.6e}; "
                    f"minimum_spatial_principal={spatial:.6e}; "
                    f"minimum_time_kinetic={time:.6e}"
                )

            accepted = False
            step = 1.0
            for _ in range(24):
                trial = field + step * correction
                trial_operator, _, trial_curvatures = monotone_operator(
                    system, trial
                )
                trial_residual = trial_operator - shifted_rhs(
                    stage_source, system.cubic_coefficient
                )
                pair, _, time = scheme_diagnostics(system, trial_curvatures)
                sufficient_decrease = float(np.linalg.norm(trial_residual)) < (
                    residual_norm * (1.0 - 1.0e-4 * step)
                )
                if sufficient_decrease and pair > 0.0 and time > 0.0:
                    field = trial
                    accepted = True
                    if checkpoint_path is not None:
                        save_continuation_checkpoint(
                            checkpoint_path,
                            system,
                            source_values,
                            field,
                            continuation_steps=continuation_steps,
                            relative_tolerance=relative_tolerance,
                            newton_max_iterations=newton_max_iterations,
                            gmres_relative_tolerance=gmres_relative_tolerance,
                            gmres_max_iterations=gmres_max_iterations,
                            preconditioner_kind=preconditioner_kind,
                            ilu_drop_tolerance=ilu_drop_tolerance,
                            ilu_fill_factor=ilu_fill_factor,
                            completed_amplitude=(
                                stages[-1].amplitude if stages else 0.0
                            ),
                            target_amplitude=amplitude,
                            stage_complete=False,
                            stages=stages,
                            current_newton_iterations=stage_newton_iterations,
                            current_gmres_iterations=total_gmres,
                            current_preconditioner_setups=preconditioner_setups,
                            current_preconditioner_setup_seconds=(
                                preconditioner_setup_seconds
                            ),
                            current_preconditioner_factor_nnz_max=(
                                preconditioner_factor_nnz_max
                            ),
                        )
                    break
                step *= 0.5
            if not accepted:
                if residual_norm / stage_scale < 2.0 * relative_tolerance:
                    converged = True
                    break
                raise RuntimeError(
                    "wide-stencil Newton line search failed at amplitude "
                    f"{amplitude:.6g}; residual={residual_norm / stage_scale:.3e}"
                )

        final_operator, _, final_curvatures = monotone_operator(system, field)
        final_residual = final_operator - shifted_rhs(
            stage_source, system.cubic_coefficient
        )
        relative = float(np.linalg.norm(final_residual) / stage_scale)
        if not converged and relative >= relative_tolerance:
            raise RuntimeError(
                "wide-stencil Newton solve did not converge at amplitude "
                f"{amplitude:.6g}; residual={relative:.3e}"
            )
        pair, spatial, time = scheme_diagnostics(system, final_curvatures)
        if pair <= 0.0 or time <= 0.0:
            raise RuntimeError(
                "wide-stencil stage reached its residual gate outside the "
                f"admissible branch at amplitude {amplitude:.6g}"
            )
        stages.append(
            ContinuationStage(
                amplitude=amplitude,
                newton_iterations=stage_newton_iterations,
                gmres_iterations=total_gmres,
                relative_residual_l2=relative,
                minimum_pair_sum=pair,
                minimum_spatial_principal=spatial,
                minimum_time_kinetic=time,
                preconditioner_kind=preconditioner_kind,
                preconditioner_setups=preconditioner_setups,
                preconditioner_setup_seconds=preconditioner_setup_seconds,
                preconditioner_factor_nnz_max=preconditioner_factor_nnz_max,
            )
        )
        if checkpoint_path is not None:
            save_continuation_checkpoint(
                checkpoint_path,
                system,
                source_values,
                field,
                continuation_steps=continuation_steps,
                relative_tolerance=relative_tolerance,
                newton_max_iterations=newton_max_iterations,
                gmres_relative_tolerance=gmres_relative_tolerance,
                gmres_max_iterations=gmres_max_iterations,
                preconditioner_kind=preconditioner_kind,
                ilu_drop_tolerance=ilu_drop_tolerance,
                ilu_fill_factor=ilu_fill_factor,
                completed_amplitude=amplitude,
                target_amplitude=amplitude,
                stage_complete=True,
                stages=stages,
            )

    final_residual = shifted_residual(system, field, source_values)
    _, _, final_curvatures = monotone_operator(system, field)
    pair, spatial, time = scheme_diagnostics(system, final_curvatures)
    source_scale_l2 = source_norm / (2.0 * system.cubic_coefficient)
    source_scale_linf = max(
        float(np.max(source_values)) / (2.0 * system.cubic_coefficient),
        np.finfo(float).tiny,
    )
    return WideSolution(
        system=system,
        source=source_values,
        field=field,
        linear_field=linear_field,
        stages=stages,
        relative_residual_l2=float(np.linalg.norm(final_residual) / source_scale_l2),
        relative_residual_linf=float(np.max(np.abs(final_residual)) / source_scale_linf),
        minimum_pair_sum=pair,
        minimum_spatial_principal=spatial,
        minimum_time_kinetic=time,
    )


def quintic_smoothstep(value: np.ndarray) -> np.ndarray:
    clipped = np.clip(value, 0.0, 1.0)
    return clipped**3 * (10.0 - 15.0 * clipped + 6.0 * clipped**2)


def continuous_smooth_normalization(spec: SmoothAnnulusSpec, order: int = 48) -> float:
    """Normalize the continuous smooth shape to the sharp wedge's charge."""

    if order < 8:
        raise ValueError("normalization quadrature order must be at least eight")
    nodes, weights = np.polynomial.legendre.leggauss(order)

    def integrate_piecewise(
        function: Callable[[np.ndarray], np.ndarray],
        breakpoints: list[float],
    ) -> float:
        total = 0.0
        for lower, upper in zip(breakpoints[:-1], breakpoints[1:]):
            if upper <= lower:
                continue
            samples = 0.5 * (upper + lower) + 0.5 * (upper - lower) * nodes
            total += 0.5 * (upper - lower) * float(
                np.sum(weights * function(samples))
            )
        return total

    radial_low = spec.inner_radius - spec.radial_smoothing_width / 2.0
    radial_high = spec.outer_radius + spec.radial_smoothing_width / 2.0

    def radial_integrand(radial: np.ndarray) -> np.ndarray:
        radial_rise = quintic_smoothstep(
            (radial - radial_low) / spec.radial_smoothing_width
        )
        radial_fall = quintic_smoothstep(
            (radial_high - radial) / spec.radial_smoothing_width
        )
        return radial**2 * radial_rise * radial_fall

    radial_breakpoints = sorted(
        {
            radial_low,
            spec.inner_radius + spec.radial_smoothing_width / 2.0,
            spec.outer_radius - spec.radial_smoothing_width / 2.0,
            radial_high,
        }
    )
    radial_integral = integrate_piecewise(radial_integrand, radial_breakpoints)

    angular_low = max(
        spec.half_opening_angle - spec.angular_smoothing_width / 2.0, 0.0
    )
    angular_high = spec.half_opening_angle + spec.angular_smoothing_width / 2.0

    def angular_integrand(latitude: np.ndarray) -> np.ndarray:
        window = quintic_smoothstep(
            (angular_high - latitude) / spec.angular_smoothing_width
        )
        return np.cos(latitude) * window

    angular_integral = integrate_piecewise(
        angular_integrand, sorted({0.0, angular_low, angular_high})
    )
    smooth_volume = 4.0 * math.pi * radial_integral * angular_integral
    nominal_volume = (
        4.0
        * math.pi
        / 3.0
        * math.sin(spec.half_opening_angle)
        * (spec.outer_radius**3 - spec.inner_radius**3)
    )
    return nominal_volume / smooth_volume


def sampled_axisymmetric_charge(
    system: WideStencilSystem,
    source: np.ndarray,
) -> float:
    """Integrate an even axisymmetric nodal source with cylindrical weights.

    The quarter-disk represents both signs of ``z`` and the full azimuth.  The
    ``z=0`` reflection plane receives half weight; the ``rho=0`` axis vanishes
    through the cylindrical Jacobian.  This is an independent nodal quadrature
    diagnostic, not a grid-fitted renormalization of the continuous source.
    """

    values = np.asarray(source, dtype=float)
    if values.shape != (system.size,):
        raise ValueError("source shape does not match the wide-stencil system")
    reflection_weight = np.where(
        np.isclose(system.z, 0.0, rtol=0.0, atol=1.0e-13), 0.5, 1.0
    )
    return float(
        4.0
        * math.pi
        * system.grid.spacing**2
        * np.sum(system.rho * reflection_weight * values)
    )


def smooth_annulus_source(
    system: WideStencilSystem,
    spec: SmoothAnnulusSpec = SmoothAnnulusSpec(),
) -> tuple[np.ndarray, dict[str, float]]:
    """Evaluate the fixed continuous broad source on the independent grid."""

    spec.validate(system.grid.radial_max)
    radius = np.hypot(system.rho, system.z)
    latitude = np.arctan2(system.z, system.rho)
    radial_low = spec.inner_radius - spec.radial_smoothing_width / 2.0
    radial_high = spec.outer_radius + spec.radial_smoothing_width / 2.0
    radial_window = quintic_smoothstep(
        (radius - radial_low) / spec.radial_smoothing_width
    ) * quintic_smoothstep(
        (radial_high - radius) / spec.radial_smoothing_width
    )
    angular_high = spec.half_opening_angle + spec.angular_smoothing_width / 2.0
    angular_window = quintic_smoothstep(
        (angular_high - latitude) / spec.angular_smoothing_width
    )
    normalization = continuous_smooth_normalization(spec)
    source = spec.mu * normalization * radial_window * angular_window
    nominal_volume = (
        4.0
        * math.pi
        / 3.0
        * math.sin(spec.half_opening_angle)
        * (spec.outer_radius**3 - spec.inner_radius**3)
    )
    sampled_charge = sampled_axisymmetric_charge(system, source)
    nominal_charge = spec.mu * nominal_volume
    return source, {
        "continuous_normalization": normalization,
        "nominal_volume": nominal_volume,
        "nominal_charge": nominal_charge,
        "sampled_charge": sampled_charge,
        "sampled_charge_relative_error": sampled_charge / nominal_charge - 1.0,
        "minimum_source": float(np.min(source)),
        "maximum_source": float(np.max(source)),
    }


def interpolate_field(
    system: WideStencilSystem,
    field: np.ndarray,
    rho: np.ndarray | float,
    z: np.ndarray | float,
) -> np.ndarray:
    """Bilinearly interpolate an even field without reusing wide operators."""

    values = np.asarray(field, dtype=float)
    if values.shape != (system.size,):
        raise ValueError("field shape does not match the wide-stencil system")
    rho_values, z_values = np.broadcast_arrays(
        np.abs(np.asarray(rho, dtype=float)), np.abs(np.asarray(z, dtype=float))
    )
    spacing = system.grid.spacing
    safe_radius = system.grid.radial_max - math.sqrt(2.0) * spacing
    if np.any(np.hypot(rho_values, z_values) > safe_radius + 1.0e-12):
        raise ValueError("interpolation point is too close to the circle")

    scaled_rho = rho_values / spacing
    scaled_z = z_values / spacing
    lower_rho = np.floor(scaled_rho).astype(int)
    lower_z = np.floor(scaled_z).astype(int)
    fraction_rho = scaled_rho - lower_rho
    fraction_z = scaled_z - lower_z
    result = np.zeros_like(rho_values, dtype=float)
    for delta_rho, weight_rho in (
        (0, 1.0 - fraction_rho),
        (1, fraction_rho),
    ):
        for delta_z, weight_z in ((0, 1.0 - fraction_z), (1, fraction_z)):
            node = system.index_map[lower_rho + delta_rho, lower_z + delta_z]
            if np.any(node < 0):
                raise RuntimeError("a supposedly safe interpolation corner is outside")
            result += weight_rho * weight_z * values[node]
    return result


def interpolated_cylindrical_derivatives(
    system: WideStencilSystem,
    field: np.ndarray,
    rho: np.ndarray | float,
    z: np.ndarray | float,
    difference_step: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return centered ``phi_r, phi_z, phi_rr, phi_rz, phi_zz`` diagnostics."""

    rho_values, z_values = np.broadcast_arrays(
        np.abs(np.asarray(rho, dtype=float)), np.abs(np.asarray(z, dtype=float))
    )
    step = system.grid.spacing if difference_step is None else difference_step
    if step <= 0.0:
        raise ValueError("difference_step must be positive")
    centre = interpolate_field(system, field, rho_values, z_values)
    radial_plus = interpolate_field(system, field, rho_values + step, z_values)
    radial_minus = interpolate_field(system, field, rho_values - step, z_values)
    axial_plus = interpolate_field(system, field, rho_values, z_values + step)
    axial_minus = interpolate_field(system, field, rho_values, z_values - step)
    phi_r = (radial_plus - radial_minus) / (2.0 * step)
    phi_z = (axial_plus - axial_minus) / (2.0 * step)
    phi_rr = (radial_plus - 2.0 * centre + radial_minus) / step**2
    phi_zz = (axial_plus - 2.0 * centre + axial_minus) / step**2
    mixed = (
        interpolate_field(system, field, rho_values + step, z_values + step)
        - interpolate_field(system, field, rho_values + step, z_values - step)
        - interpolate_field(system, field, rho_values - step, z_values + step)
        + interpolate_field(system, field, rho_values - step, z_values - step)
    ) / (4.0 * step**2)
    mixed = np.where(
        np.isclose(rho_values, 0.0, atol=1.0e-13)
        | np.isclose(z_values, 0.0, atol=1.0e-13),
        0.0,
        mixed,
    )
    return phi_r, phi_z, phi_rr, mixed, phi_zz


def independent_residual_diagnostics(
    system: WideStencilSystem,
    field: np.ndarray,
    source: np.ndarray,
) -> dict[str, float | int]:
    """Evaluate the original PDE and White root on a centered nodal path."""

    source_values = np.asarray(source, dtype=float)
    if source_values.shape != (system.size,):
        raise ValueError("source shape does not match the wide-stencil system")
    h = system.grid.spacing
    mask = np.hypot(system.rho, system.z) <= (
        system.grid.radial_max - 3.0 * math.sqrt(2.0) * h
    )
    rho = system.rho[mask]
    z = system.z[mask]
    selected_source = source_values[mask]
    phi_r, _phi_z, h_rr, h_rz, h_zz = interpolated_cylindrical_derivatives(
        system, field, rho, z
    )
    h_pp = np.divide(phi_r, rho, out=h_rr.copy(), where=rho > 0.5 * h)
    trace = h_rr + h_zz + h_pp
    norm_squared = h_rr**2 + h_zz**2 + h_pp**2 + 2.0 * h_rz**2
    c3 = system.cubic_coefficient
    original = trace + c3 * (trace**2 - norm_squared) - selected_source
    radicand = norm_squared + selected_source / c3 + 1.0 / (4.0 * c3**2)
    white = np.sqrt(np.maximum(radicand, 0.0)) - trace - 1.0 / (2.0 * c3)
    normal_factor = trace + 1.0 / (2.0 * c3)
    weights = nodal_volume_weights(system)[mask]
    original_scale = max(
        float(np.sqrt(np.sum(weights * selected_source**2))),
        np.finfo(float).tiny,
    )
    white_scale = max(
        float(np.sqrt(np.sum(weights * (selected_source / c3) ** 2))),
        np.finfo(float).tiny,
    )
    return {
        "evaluated_nodes": int(np.count_nonzero(mask)),
        "excluded_outer_nodes": int(system.size - np.count_nonzero(mask)),
        "original_relative_volume_l2": float(
            np.sqrt(np.sum(weights * original**2)) / original_scale
        ),
        "original_relative_linf": float(
            np.max(np.abs(original))
            / max(float(np.max(np.abs(selected_source))), np.finfo(float).tiny)
        ),
        "white_root_relative_volume_l2": float(
            np.sqrt(np.sum(weights * white**2)) / white_scale
        ),
        "minimum_white_radicand": float(np.min(radicand)),
        "negative_white_radicand_nodes": int(np.count_nonzero(radicand < 0.0)),
        "minimum_normal_branch_factor": float(np.min(normal_factor)),
    }


def prolongate_field(
    coarse_solution: WideSolution,
    fine_system: WideStencilSystem,
) -> np.ndarray:
    """Interpolate a coarse solution to a fine grid for a scaled warm start."""

    if not math.isclose(
        coarse_solution.system.grid.radial_max,
        fine_system.grid.radial_max,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    ):
        raise ValueError("coarse and fine systems must share radial_max")
    safe = np.hypot(fine_system.rho, fine_system.z) <= (
        coarse_solution.system.grid.radial_max
        - math.sqrt(2.0) * coarse_solution.system.grid.spacing
    )
    result = np.zeros(fine_system.size, dtype=float)
    result[safe] = interpolate_field(
        coarse_solution.system,
        coarse_solution.field,
        fine_system.rho[safe],
        fine_system.z[safe],
    )
    return result


def force_ray_diagnostics(
    solution: WideSolution,
    latitude: float = math.pi / 10.0,
    maximum_radius: float = 12.0,
) -> dict[str, float | None]:
    """Compare nonlinear and linear force along a fixed-latitude ray."""

    system = solution.system
    if maximum_radius + 2.0 * system.grid.spacing >= system.grid.radial_max:
        raise ValueError("force ray is too close to the circular boundary")
    samples = max(
        101, int(math.ceil(8.0 * maximum_radius / system.grid.spacing)) + 1
    )
    radii = np.linspace(0.0, maximum_radius, samples)
    rho = radii * math.cos(latitude)
    z = radii * math.sin(latitude)
    nonlinear_r, nonlinear_z, *_ = interpolated_cylindrical_derivatives(
        system, solution.field, rho, z
    )
    linear_r, linear_z, *_ = interpolated_cylindrical_derivatives(
        system, solution.linear_field, rho, z
    )
    nonlinear = np.hypot(nonlinear_r, nonlinear_z)
    linear = np.hypot(linear_r, linear_z)
    nonlinear[0] = 0.0
    linear[0] = 0.0
    floor = max(1.0e-7 * float(np.max(linear)), np.finfo(float).tiny)
    ratio = np.divide(
        nonlinear,
        linear,
        out=np.full_like(nonlinear, np.nan),
        where=linear > floor,
    )
    at_one = int(np.argmin(np.abs(radii - 1.0)))
    peak = int(np.argmax(nonlinear))
    anti = np.flatnonzero((nonlinear > linear) & (linear > floor))
    return {
        "latitude_rad": latitude,
        "samples": float(samples),
        "ratio_at_center": None,
        "linear_gradient_at_r1": float(linear[at_one]),
        "nonlinear_gradient_at_r1": float(nonlinear[at_one]),
        "ratio_at_r1": float(ratio[at_one]),
        "maximum_nonlinear_gradient": float(nonlinear[peak]),
        "maximum_nonlinear_gradient_radius": float(radii[peak]),
        "maximum_finite_ratio": float(np.nanmax(ratio)),
        "anti_screened_radius_start": (
            float(radii[anti[0]]) if anti.size else None
        ),
        "anti_screened_radius_end": (
            float(radii[anti[-1]]) if anti.size else None
        ),
        "ratio_denominator_floor": floor,
    }


def spherical_flux_diagnostic(
    system: WideStencilSystem,
    field: np.ndarray,
    radius: float,
    quadrature_order: int = 64,
) -> float:
    """Integrate the exact divergence current on an interpolated sphere."""

    if quadrature_order < 8:
        raise ValueError("quadrature_order must be at least eight")
    if radius + 2.0 * system.grid.spacing >= system.grid.radial_max:
        raise ValueError("flux sphere is too close to the circular boundary")
    nodes, weights = np.polynomial.legendre.leggauss(quadrature_order)
    latitude = 0.25 * math.pi * (nodes + 1.0)
    latitude_weights = 0.25 * math.pi * weights
    rho = radius * np.cos(latitude)
    z = radius * np.sin(latitude)
    phi_r, phi_z, h_rr, h_rz, h_zz = interpolated_cylindrical_derivatives(
        system, field, rho, z
    )
    h_pp = np.divide(phi_r, rho, out=h_rr.copy(), where=rho > 0.0)
    c3 = system.cubic_coefficient
    current_r = phi_r + c3 * ((h_zz + h_pp) * phi_r - h_rz * phi_z)
    current_z = phi_z + c3 * ((h_rr + h_pp) * phi_z - h_rz * phi_r)
    normal_current = current_r * np.cos(latitude) + current_z * np.sin(latitude)
    return float(
        4.0
        * math.pi
        * radius**2
        * np.sum(latitude_weights * np.cos(latitude) * normal_current)
    )


def annulus_diagnostics(
    solution: WideSolution,
    source_metadata: dict[str, float],
    spec: SmoothAnnulusSpec = SmoothAnnulusSpec(),
) -> dict[str, object]:
    """Build the E-024-comparable E-025 force, residual, and flux report."""

    system = solution.system
    shell_gap = system.grid.radial_max - (
        spec.outer_radius + spec.radial_smoothing_width / 2.0
    )
    shell_radii = [
        spec.outer_radius + spec.radial_smoothing_width / 2.0 + fraction * shell_gap
        for fraction in (0.2, 0.4, 0.6)
    ]
    sampled_charge = float(source_metadata["sampled_charge"])
    nominal_charge = float(source_metadata["nominal_charge"])
    flux_rows: list[dict[str, float]] = []
    for radius in shell_radii:
        flux = spherical_flux_diagnostic(system, solution.field, radius)
        flux_rows.append(
            {
                "radius": radius,
                "flux": flux,
                "relative_to_sampled_charge": flux / sampled_charge - 1.0,
                "relative_to_nominal_charge": flux / nominal_charge - 1.0,
            }
        )
    return {
        "epistemic_status": (
            "numerical validation of a hypothetical PDE; not evidence for a "
            "new field, artificial gravity, inertial control, FTL, or propulsion"
        ),
        "grid": {
            "radial_max": system.grid.radial_max,
            "spacing": system.grid.spacing,
            "directional_radius": system.grid.directional_radius,
            "unknowns": system.size,
            "bases": len(system.bases),
            "directional_resolution_rad": directional_resolution(
                system.grid.directional_radius
            ),
        },
        "source": source_metadata,
        "solver": {
            "relative_residual_l2": solution.relative_residual_l2,
            "relative_residual_linf": solution.relative_residual_linf,
            "summed_newton_iterations": sum(
                stage.newton_iterations for stage in solution.stages
            ),
            "summed_gmres_iterations": sum(
                stage.gmres_iterations for stage in solution.stages
            ),
            "preconditioner_kinds": sorted(
                {stage.preconditioner_kind for stage in solution.stages}
            ),
            "summed_preconditioner_setups": sum(
                stage.preconditioner_setups for stage in solution.stages
            ),
            "summed_preconditioner_setup_seconds": sum(
                stage.preconditioner_setup_seconds for stage in solution.stages
            ),
            "maximum_preconditioner_factor_nnz": max(
                (
                    stage.preconditioner_factor_nnz_max
                    for stage in solution.stages
                ),
                default=0,
            ),
            "stages": [stage.__dict__ for stage in solution.stages],
        },
        "wide_branch": scheme_diagnostic_details(system, solution.field),
        "fixed_frame_crosscheck": fixed_coordinate_diagnostics(
            system, solution.field, solution.source
        ),
        "independent_centered_residual": independent_residual_diagnostics(
            system, solution.field, solution.source
        ),
        "force_ray": force_ray_diagnostics(solution),
        "flux_spheres": flux_rows,
        "limitations": [
            "The centered residual and interpolated flux omit the outer derivative band.",
            "The linear reference shares the same domain and fixed-frame Laplacian.",
            "The published Cartesian wide-stencil proof does not cover this axisymmetric curved-boundary scheme.",
        ],
    }


def run_annulus_validation(
    radial_max: float = 80.0,
    spacing: float = 0.5,
    directional_radius: int = 2,
    continuation_steps: int = 12,
    preconditioner_kind: str = "active_ilu",
    ilu_drop_tolerance: float = 1.0e-3,
    ilu_fill_factor: float = 10.0,
    checkpoint_path: str | Path | None = None,
    resume_checkpoint: bool = False,
) -> dict[str, object]:
    """Solve and diagnose one broad-annulus E-025 refinement level."""

    system = build_system(
        AxisymmetricGrid(radial_max, spacing, directional_radius)
    )
    source, metadata = smooth_annulus_source(system)
    solution = solve_continuation(
        system,
        source,
        continuation_steps=continuation_steps,
        relative_tolerance=1.0e-7,
        newton_max_iterations=20,
        gmres_relative_tolerance=1.0e-8,
        gmres_max_iterations=40,
        preconditioner_kind=preconditioner_kind,
        ilu_drop_tolerance=ilu_drop_tolerance,
        ilu_fill_factor=ilu_fill_factor,
        checkpoint_path=checkpoint_path,
        resume_checkpoint=resume_checkpoint,
    )
    return annulus_diagnostics(solution, metadata)


def _smoke_source(system: WideStencilSystem, amplitude: float) -> np.ndarray:
    radial_scale = system.grid.radial_max
    ring = np.exp(-((system.rho - 0.45 * radial_scale) / (0.18 * radial_scale)) ** 4)
    layer = np.exp(-(system.z / (0.16 * radial_scale)) ** 4)
    return amplitude * ring * layer


def run_smoke(
    radial_max: float = 4.0,
    spacing: float = 0.5,
    directional_radius: int = 2,
    source_amplitude: float = 0.02,
    continuation_steps: int = 4,
) -> dict[str, object]:
    grid = AxisymmetricGrid(radial_max, spacing, directional_radius)
    system = build_system(grid)
    source = _smoke_source(system, source_amplitude)
    solution = solve_continuation(
        system,
        source,
        continuation_steps=continuation_steps,
    )
    return {
        "epistemic_status": (
            "hypothetical PDE smoke validation; not a detected field, useful "
            "artificial gravity, FTL result, or reactionless propulsion"
        ),
        "configuration": {
            "radial_max": radial_max,
            "spacing": spacing,
            "directional_radius": directional_radius,
            "directional_resolution_rad": directional_resolution(
                directional_radius
            ),
            "unknowns": system.size,
            "bases": len(system.bases),
            "source_amplitude": source_amplitude,
            "continuation_steps": continuation_steps,
        },
        "solver": {
            "relative_residual_l2": solution.relative_residual_l2,
            "relative_residual_linf": solution.relative_residual_linf,
            "minimum_pair_sum": solution.minimum_pair_sum,
            "minimum_spatial_principal": solution.minimum_spatial_principal,
            "minimum_time_kinetic": solution.minimum_time_kinetic,
            "maximum_absolute_field": float(np.max(np.abs(solution.field))),
            "stages": [stage.__dict__ for stage in solution.stages],
        },
        "limitations": [
            "The full mu=36.8 annulus campaign is intentionally not run by this smoke CLI.",
            "Joint spatial and directional refinement remains a manual E-025 gate.",
            "The axisymmetric curved-boundary reduction requires manufactured convergence checks.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radial-max", type=float, default=4.0)
    parser.add_argument("--spacing", type=float, default=0.5)
    parser.add_argument("--directional-radius", type=int, default=2)
    parser.add_argument("--source-amplitude", type=float, default=0.02)
    parser.add_argument("--continuation-steps", type=int, default=4)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run_smoke(
        radial_max=args.radial_max,
        spacing=args.spacing,
        directional_radius=args.directional_radius,
        source_amplitude=args.source_amplitude,
        continuation_steps=args.continuation_steps,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        configuration = report["configuration"]
        solver = report["solver"]
        print(report["epistemic_status"])
        print(
            "grid: "
            f"unknowns={configuration['unknowns']}, "
            f"bases={configuration['bases']}, "
            f"dtheta={configuration['directional_resolution_rad']:.6g} rad"
        )
        print(
            "residual L2/Linf: "
            f"{solver['relative_residual_l2']:.3e} / "
            f"{solver['relative_residual_linf']:.3e}"
        )
        print(
            "minimum pair/spatial/time: "
            f"{solver['minimum_pair_sum']:.6g} / "
            f"{solver['minimum_spatial_principal']:.6g} / "
            f"{solver['minimum_time_kinetic']:.6g}"
        )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Independent shifted-2-Hessian solver for E-024.

This module intentionally does not import the E-023 Galileon replication.
It independently constructs the mapped spherical grid, Hessian, Laplacian,
shifted residual, branch diagnostics, Newton--Krylov continuation, and surface
flux.  The unknown stored by the solver is ``phi``; the quadratic shift is
added analytically to its orthonormal Hessian, avoiding cancellation from
solving directly for ``u = phi + |x|^2/(8 c3)``.

For ``c3 > 0`` the dimensionless cubic-Galileon equation

    Delta(phi) + c3 [Delta(phi)^2 - Hess(phi):Hess(phi)] = S

is exactly equivalent to

    sigma_2(D2 u) = 3/(16 c3^2) + S/(2 c3),
    u = phi + |x|^2/(8 c3).

This is a numerical validation artifact for a hypothetical field equation,
not evidence that a Galileon field exists or an artificial-gravity design.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy import sparse
from scipy.sparse import linalg as sparse_linalg


@dataclass(frozen=True)
class ShiftedGrid:
    radial_cells: int
    angular_cells: int
    radial_max: float
    radial_mapping_alpha: float = 0.2

    def validate(self) -> None:
        if self.radial_cells < 12 or self.angular_cells < 8:
            raise ValueError("grid is too coarse")
        if self.radial_max <= 0.0:
            raise ValueError("radial_max must be positive")
        if self.radial_mapping_alpha < 0.0:
            raise ValueError("radial mapping alpha must be non-negative")


@dataclass(frozen=True)
class ContinuationStage:
    amplitude: float
    newton_iterations: int
    gmres_iterations: int
    relative_shifted_residual_l2: float
    minimum_spatial_principal: float
    minimum_time_kinetic: float
    minimum_sigma2: float


@dataclass
class ShiftedSolution:
    grid: ShiftedGrid
    source: np.ndarray
    field: np.ndarray
    stages: list[ContinuationStage]
    relative_shifted_residual_l2: float
    relative_original_residual_l2: float
    relative_original_residual_linf: float
    minimum_spatial_principal: float
    minimum_pair_sum: float
    minimum_time_kinetic: float
    minimum_sigma2: float


def _chi_max(grid: ShiftedGrid) -> float:
    grid.validate()
    if grid.radial_mapping_alpha == 0.0:
        return grid.radial_max
    low = 0.0
    high = grid.radial_max
    alpha = grid.radial_mapping_alpha
    for _ in range(100):
        middle = 0.5 * (low + high)
        mapped = middle + alpha * middle**3 / 3.0
        if mapped < grid.radial_max:
            low = middle
        else:
            high = middle
    return 0.5 * (low + high)


def grid_coordinates(
    grid: ShiftedGrid,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, float]:
    """Return chi/r centres, r faces, theta centres, dchi, and dtheta."""

    grid.validate()
    chi_max = _chi_max(grid)
    dchi = chi_max / grid.radial_cells
    chi_faces = np.arange(grid.radial_cells + 1, dtype=float) * dchi
    chi = (np.arange(grid.radial_cells, dtype=float) + 0.5) * dchi
    alpha = grid.radial_mapping_alpha
    radial_faces = chi_faces + alpha * chi_faces**3 / 3.0
    radial = chi + alpha * chi**3 / 3.0
    dtheta = (math.pi / 2.0) / grid.angular_cells
    angular = (np.arange(grid.angular_cells, dtype=float) + 0.5) * dtheta
    return chi, radial, radial_faces, angular, dchi, dtheta


def cell_volume_weights(grid: ShiftedGrid) -> np.ndarray:
    """Return full reflection-restored physical cell-volume weights."""

    _, _, radial_faces, _, _, _ = grid_coordinates(grid)
    angular_faces = np.linspace(0.0, math.pi / 2.0, grid.angular_cells + 1)
    radial_weight = (radial_faces[1:] ** 3 - radial_faces[:-1] ** 3) / 3.0
    angular_weight = np.sin(angular_faces[1:]) - np.sin(angular_faces[:-1])
    return 4.0 * math.pi * radial_weight[:, None] * angular_weight[None, :]


def _ghost_pad(field: np.ndarray, grid: ShiftedGrid) -> np.ndarray:
    if field.shape != (grid.radial_cells, grid.angular_cells):
        raise ValueError("field shape does not match shifted grid")
    padded = np.empty(
        (grid.radial_cells + 2, grid.angular_cells + 2), dtype=float
    )
    padded[1:-1, 1:-1] = field
    padded[0, 1:-1] = field[0, :]
    padded[-1, 1:-1] = -field[-1, :]
    padded[1:-1, 0] = field[:, 0]
    padded[1:-1, -1] = field[:, -1]
    padded[0, 0] = field[0, 0]
    padded[0, -1] = field[0, -1]
    padded[-1, 0] = -field[-1, 0]
    padded[-1, -1] = -field[-1, -1]
    return padded


def hessian_components(
    field: np.ndarray,
    grid: ShiftedGrid,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return independent orthonormal ``rr, rtheta, theta, phi`` Hessian."""

    padded = _ghost_pad(field, grid)
    chi, radial, _, angular, dchi, dtheta = grid_coordinates(grid)
    phi_chi = (padded[2:, 1:-1] - padded[:-2, 1:-1]) / (2.0 * dchi)
    phi_chichi = (
        padded[2:, 1:-1]
        - 2.0 * padded[1:-1, 1:-1]
        + padded[:-2, 1:-1]
    ) / dchi**2
    phi_theta = (padded[1:-1, 2:] - padded[1:-1, :-2]) / (
        2.0 * dtheta
    )
    phi_thetatheta = (
        padded[1:-1, 2:]
        - 2.0 * padded[1:-1, 1:-1]
        + padded[1:-1, :-2]
    ) / dtheta**2
    phi_chitheta = (
        padded[2:, 2:]
        - padded[2:, :-2]
        - padded[:-2, 2:]
        + padded[:-2, :-2]
    ) / (4.0 * dchi * dtheta)

    alpha = grid.radial_mapping_alpha
    mapping_derivative = 1.0 + alpha * chi[:, None] ** 2
    radius = radial[:, None]
    theta = angular[None, :]
    phi_r = phi_chi / mapping_derivative
    phi_rr = (
        phi_chichi / mapping_derivative**2
        - 2.0
        * alpha
        * chi[:, None]
        * phi_chi
        / mapping_derivative**3
    )
    phi_rtheta = phi_chitheta / mapping_derivative
    h_rr = phi_rr
    h_rtheta = phi_rtheta / radius - phi_theta / radius**2
    h_thetatheta = phi_r / radius + phi_thetatheta / radius**2
    h_phiphi = phi_r / radius - np.tan(theta) * phi_theta / radius**2
    return h_rr, h_rtheta, h_thetatheta, h_phiphi


def gradient_components(
    field: np.ndarray,
    grid: ShiftedGrid,
) -> tuple[np.ndarray, np.ndarray]:
    """Return independent orthonormal radial and angular gradient components."""

    padded = _ghost_pad(field, grid)
    chi, radial, _, _, dchi, dtheta = grid_coordinates(grid)
    phi_chi = (padded[2:, 1:-1] - padded[:-2, 1:-1]) / (2.0 * dchi)
    radial_gradient = phi_chi / (
        1.0 + grid.radial_mapping_alpha * chi[:, None] ** 2
    )
    angular_gradient = (padded[1:-1, 2:] - padded[1:-1, :-2]) / (
        2.0 * dtheta * radial[:, None]
    )
    return radial_gradient, angular_gradient


def build_laplacian(grid: ShiftedGrid) -> sparse.csc_matrix:
    """Build an independently assembled mapped spherical Laplacian."""

    chi, radial, _, angular, dchi, dtheta = grid_coordinates(grid)
    nr = grid.radial_cells
    nt = grid.angular_cells
    rows: list[int] = []
    columns: list[int] = []
    values: list[float] = []

    def add(row: int, column: int, value: float) -> None:
        rows.append(row)
        columns.append(column)
        values.append(value)

    for i, radius in enumerate(radial):
        derivative = 1.0 + grid.radial_mapping_alpha * chi[i] ** 2
        second = 1.0 / derivative**2
        first = (
            -2.0 * grid.radial_mapping_alpha * chi[i] / derivative**3
            + 2.0 / (radius * derivative)
        )
        radial_minus = second / dchi**2 - first / (2.0 * dchi)
        radial_plus = second / dchi**2 + first / (2.0 * dchi)
        for j, theta in enumerate(angular):
            row = i * nt + j
            diagonal = -2.0 * second / dchi**2
            if i > 0:
                add(row, (i - 1) * nt + j, radial_minus)
            else:
                diagonal += radial_minus
            if i < nr - 1:
                add(row, (i + 1) * nt + j, radial_plus)
            else:
                diagonal -= radial_plus

            angular_minus = (
                1.0 / dtheta**2 + math.tan(theta) / (2.0 * dtheta)
            ) / radius**2
            angular_plus = (
                1.0 / dtheta**2 - math.tan(theta) / (2.0 * dtheta)
            ) / radius**2
            diagonal -= 2.0 / (radius**2 * dtheta**2)
            if j > 0:
                add(row, i * nt + j - 1, angular_minus)
            else:
                diagonal += angular_minus
            if j < nt - 1:
                add(row, i * nt + j + 1, angular_plus)
            else:
                diagonal += angular_plus
            add(row, row, diagonal)

    return sparse.csc_matrix(
        (values, (rows, columns)), shape=(nr * nt, nr * nt)
    )


def shifted_components(
    field: np.ndarray,
    grid: ShiftedGrid,
    cubic_coefficient: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if cubic_coefficient <= 0.0:
        raise ValueError("shifted formulation requires c3 > 0")
    h_rr, h_rtheta, h_thetatheta, h_phiphi = hessian_components(field, grid)
    shift = 1.0 / (4.0 * cubic_coefficient)
    return (
        h_rr + shift,
        h_rtheta,
        h_thetatheta + shift,
        h_phiphi + shift,
    )


def shifted_residual(
    field: np.ndarray,
    source: np.ndarray,
    grid: ShiftedGrid,
    cubic_coefficient: float,
) -> np.ndarray:
    """Return direct pair-product 2-Hessian residual."""

    if source.shape != field.shape:
        raise ValueError("source and field shapes differ")
    w_rr, w_rtheta, w_thetatheta, w_phiphi = shifted_components(
        field, grid, cubic_coefficient
    )
    sigma2 = (
        w_rr * w_thetatheta
        + w_rr * w_phiphi
        + w_thetatheta * w_phiphi
        - w_rtheta**2
    )
    rhs = (
        3.0 / (16.0 * cubic_coefficient**2)
        + source / (2.0 * cubic_coefficient)
    )
    return sigma2 - rhs


def original_residual(
    field: np.ndarray,
    source: np.ndarray,
    grid: ShiftedGrid,
    cubic_coefficient: float,
) -> np.ndarray:
    """Independently evaluate the unshifted Galileon residual."""

    h_rr, h_rtheta, h_thetatheta, h_phiphi = hessian_components(field, grid)
    trace = h_rr + h_thetatheta + h_phiphi
    norm_squared = (
        h_rr**2
        + h_thetatheta**2
        + h_phiphi**2
        + 2.0 * h_rtheta**2
    )
    return trace + cubic_coefficient * (trace**2 - norm_squared) - source


def branch_diagnostics(
    field: np.ndarray,
    grid: ShiftedGrid,
    cubic_coefficient: float,
) -> tuple[float, float, float, float]:
    """Return min Galileon spatial, shifted pair, time, and sigma2 values."""

    w_rr, w_rtheta, w_thetatheta, w_phiphi = shifted_components(
        field, grid, cubic_coefficient
    )
    discriminant = np.sqrt(
        (w_rr - w_thetatheta) ** 2 + 4.0 * w_rtheta**2
    )
    meridional_low = 0.5 * (w_rr + w_thetatheta - discriminant)
    meridional_high = 0.5 * (w_rr + w_thetatheta + discriminant)
    pair_sums = np.stack(
        [
            meridional_low + meridional_high,
            meridional_low + w_phiphi,
            meridional_high + w_phiphi,
        ],
        axis=0,
    )
    minimum_pair_sum = float(np.min(pair_sums))
    minimum_spatial = 2.0 * cubic_coefficient * minimum_pair_sum
    hessian = hessian_components(field, grid)
    trace_h = hessian[0] + hessian[2] + hessian[3]
    minimum_time = float(np.min(1.0 + 2.0 * cubic_coefficient * trace_h))
    sigma2 = (
        w_rr * w_thetatheta
        + w_rr * w_phiphi
        + w_thetatheta * w_phiphi
        - w_rtheta**2
    )
    return minimum_spatial, minimum_pair_sum, minimum_time, float(np.min(sigma2))


def branch_diagnostic_details(
    field: np.ndarray,
    grid: ShiftedGrid,
    cubic_coefficient: float,
) -> dict[str, float | int]:
    """Locate the smallest principal value and report a boundary-excluded check.

    The global minimum can occur in the first mapped radial or angular cell,
    where the origin/equatorial ghost convention is most sensitive.  Reporting
    its coordinates prevents that discrete warning from being mistaken for a
    demonstrated physical loss of ellipticity.
    """

    w_rr, w_rtheta, w_thetatheta, w_phiphi = shifted_components(
        field, grid, cubic_coefficient
    )
    discriminant = np.sqrt(
        (w_rr - w_thetatheta) ** 2 + 4.0 * w_rtheta**2
    )
    meridional_low = 0.5 * (w_rr + w_thetatheta - discriminant)
    meridional_high = 0.5 * (w_rr + w_thetatheta + discriminant)
    principal = 2.0 * cubic_coefficient * np.stack(
        [
            meridional_low + meridional_high,
            meridional_low + w_phiphi,
            meridional_high + w_phiphi,
        ],
        axis=0,
    )
    component, radial_index, angular_index = np.unravel_index(
        int(np.argmin(principal)), principal.shape
    )
    _, radial, _, angular, _, _ = grid_coordinates(grid)
    if grid.radial_cells > 2 and grid.angular_cells > 2:
        boundary_excluded_minimum = float(np.min(principal[:, 1:-1, 1:-1]))
    else:  # Guarded by ``ShiftedGrid.validate``; retained for completeness.
        boundary_excluded_minimum = float(np.min(principal))
    return {
        "minimum_spatial_principal": float(
            principal[component, radial_index, angular_index]
        ),
        "principal_component_index": int(component),
        "radial_index": int(radial_index),
        "angular_index": int(angular_index),
        "radius": float(radial[radial_index]),
        "theta": float(angular[angular_index]),
        "one_cell_boundary_excluded_minimum": boundary_excluded_minimum,
    }


def shifted_jacobian_vector(
    field: np.ndarray,
    vector: np.ndarray,
    grid: ShiftedGrid,
    cubic_coefficient: float,
) -> np.ndarray:
    """Apply the analytic first-Newton-tensor Jacobian to ``vector``."""

    if field.shape != vector.shape:
        raise ValueError("field and Jacobian vector shapes differ")
    w_rr, w_rtheta, w_thetatheta, w_phiphi = shifted_components(
        field, grid, cubic_coefficient
    )
    trace_w = w_rr + w_thetatheta + w_phiphi
    v_rr, v_rtheta, v_thetatheta, v_phiphi = hessian_components(vector, grid)
    return (
        (trace_w - w_rr) * v_rr
        + (trace_w - w_thetatheta) * v_thetatheta
        + (trace_w - w_phiphi) * v_phiphi
        - 2.0 * w_rtheta * v_rtheta
    )


def solve_shifted_continuation(
    grid: ShiftedGrid,
    source: np.ndarray,
    cubic_coefficient: float = 1.0,
    continuation_steps: int = 10,
    relative_tolerance: float = 1.0e-8,
    newton_max_iterations: int = 15,
    gmres_relative_tolerance: float = 1.0e-8,
    gmres_max_iterations: int = 20,
) -> ShiftedSolution:
    """Follow the admissible normal branch with damped Newton--Krylov steps."""

    grid.validate()
    if source.shape != (grid.radial_cells, grid.angular_cells):
        raise ValueError("source shape does not match shifted grid")
    if cubic_coefficient <= 0.0:
        raise ValueError("shifted continuation requires c3 > 0")
    if continuation_steps < 1 or newton_max_iterations < 1:
        raise ValueError("continuation and Newton counts must be positive")
    if relative_tolerance <= 0.0 or gmres_relative_tolerance <= 0.0:
        raise ValueError("solver tolerances must be positive")

    field = np.zeros_like(source, dtype=float)
    source_norm = float(np.linalg.norm(source.ravel()))
    if source_norm == 0.0:
        spatial, pair, time, sigma2 = branch_diagnostics(
            field, grid, cubic_coefficient
        )
        return ShiftedSolution(
            grid=grid,
            source=source,
            field=field,
            stages=[],
            relative_shifted_residual_l2=0.0,
            relative_original_residual_l2=0.0,
            relative_original_residual_linf=0.0,
            minimum_spatial_principal=spatial,
            minimum_pair_sum=pair,
            minimum_time_kinetic=time,
            minimum_sigma2=sigma2,
        )

    laplacian = build_laplacian(grid)
    laplacian_factor = sparse_linalg.splu(laplacian)
    size = source.size
    preconditioner = sparse_linalg.LinearOperator(
        (size, size),
        matvec=lambda vector: 2.0
        * cubic_coefficient
        * laplacian_factor.solve(vector),
    )
    stages: list[ContinuationStage] = []

    for amplitude in np.linspace(
        1.0 / continuation_steps, 1.0, continuation_steps
    ):
        stage_source = amplitude * source
        stage_scale = max(
            float(np.linalg.norm(stage_source.ravel()))
            / (2.0 * cubic_coefficient),
            np.finfo(float).tiny,
        )
        total_gmres_iterations = 0
        converged = False
        for newton_iteration in range(1, newton_max_iterations + 1):
            residual = shifted_residual(
                field, stage_source, grid, cubic_coefficient
            )
            residual_norm = float(np.linalg.norm(residual.ravel()))
            if residual_norm / stage_scale < relative_tolerance:
                converged = True
                break

            def jacobian_vector(vector: np.ndarray) -> np.ndarray:
                return shifted_jacobian_vector(
                    field,
                    vector.reshape(source.shape),
                    grid,
                    cubic_coefficient,
                ).ravel()

            jacobian = sparse_linalg.LinearOperator(
                (size, size), matvec=jacobian_vector
            )
            gmres_counter = [0]

            def count_gmres(_: np.ndarray) -> None:
                gmres_counter[0] += 1

            correction, gmres_info = sparse_linalg.gmres(
                jacobian,
                -residual.ravel(),
                M=preconditioner,
                rtol=gmres_relative_tolerance,
                atol=0.0,
                restart=min(60, size),
                maxiter=gmres_max_iterations,
                callback=count_gmres,
                callback_type="pr_norm",
            )
            total_gmres_iterations += gmres_counter[0]

            if gmres_info < 0:
                raise RuntimeError(
                    "shifted GMRES failed before producing a usable correction "
                    f"at amplitude {amplitude:.6g}; info={gmres_info}"
                )
            if not np.all(np.isfinite(correction)):
                raise RuntimeError(
                    "shifted GMRES produced a non-finite correction at amplitude "
                    f"{amplitude:.6g}; info={gmres_info}"
                )

            accepted = False
            step = 1.0
            spatial = float("nan")
            time = float("nan")
            sigma2 = float("nan")
            for _ in range(24):
                trial = field + step * correction.reshape(source.shape)
                if not np.all(np.isfinite(trial)):
                    step *= 0.5
                    continue
                trial_residual = shifted_residual(
                    trial, stage_source, grid, cubic_coefficient
                )
                spatial, _, time, sigma2 = branch_diagnostics(
                    trial, grid, cubic_coefficient
                )
                sufficient_decrease = float(
                    np.linalg.norm(trial_residual.ravel())
                ) < residual_norm * (1.0 - 1.0e-4 * step)
                if (
                    sufficient_decrease
                    and spatial > 0.0
                    and time > 0.0
                    and sigma2 > 0.0
                ):
                    field = trial
                    accepted = True
                    break
                step *= 0.5
            if not accepted:
                # Near the requested finite-difference/linear-solve floor, an
                # otherwise admissible Newton step can fail the Armijo test
                # by roundoff.  Preserve and report the attained residual
                # rather than taking a numerically meaningless micro-step.
                if residual_norm / stage_scale < 2.0 * relative_tolerance:
                    converged = True
                    break
                raise RuntimeError(
                    "shifted Newton line search failed at amplitude "
                    f"{amplitude:.6g}; GMRES info={gmres_info}, "
                    f"residual={residual_norm / stage_scale:.3e}, "
                    f"trial spatial/time/sigma2={spatial:.3e}/{time:.3e}/{sigma2:.3e}"
                )

        if not converged:
            residual = shifted_residual(
                field, stage_source, grid, cubic_coefficient
            )
            if float(np.linalg.norm(residual.ravel())) / stage_scale < relative_tolerance:
                converged = True
            else:
                raise RuntimeError(
                    f"shifted Newton solve did not converge at amplitude {amplitude:.6g}"
                )
        spatial, _, time, sigma2 = branch_diagnostics(
            field, grid, cubic_coefficient
        )
        final_stage_residual = shifted_residual(
            field, stage_source, grid, cubic_coefficient
        )
        stages.append(
            ContinuationStage(
                amplitude=float(amplitude),
                newton_iterations=newton_iteration,
                gmres_iterations=total_gmres_iterations,
                relative_shifted_residual_l2=float(
                    np.linalg.norm(final_stage_residual.ravel()) / stage_scale
                ),
                minimum_spatial_principal=spatial,
                minimum_time_kinetic=time,
                minimum_sigma2=sigma2,
            )
        )

    shifted = shifted_residual(field, source, grid, cubic_coefficient)
    original = original_residual(field, source, grid, cubic_coefficient)
    spatial, pair, time, sigma2 = branch_diagnostics(
        field, grid, cubic_coefficient
    )
    shifted_scale = source_norm / (2.0 * cubic_coefficient)
    source_linf = max(float(np.max(np.abs(source))), np.finfo(float).tiny)
    return ShiftedSolution(
        grid=grid,
        source=source,
        field=field,
        stages=stages,
        relative_shifted_residual_l2=float(
            np.linalg.norm(shifted.ravel()) / shifted_scale
        ),
        relative_original_residual_l2=float(
            np.linalg.norm(original.ravel()) / source_norm
        ),
        relative_original_residual_linf=float(
            np.max(np.abs(original)) / source_linf
        ),
        minimum_spatial_principal=spatial,
        minimum_pair_sum=pair,
        minimum_time_kinetic=time,
        minimum_sigma2=sigma2,
    )


def surface_flux(
    field: np.ndarray,
    grid: ShiftedGrid,
    cubic_coefficient: float,
    radius: float,
    formulation: str = "shifted",
) -> float:
    """Integrate the original or shifted divergence current on a sphere."""

    _, radial, _, _, _, _ = grid_coordinates(grid)
    if not radial[0] < radius < radial[-1]:
        raise ValueError("flux radius must lie inside the cell-centre range")
    h_rr, h_rtheta, h_thetatheta, h_phiphi = hessian_components(field, grid)
    grad_r, grad_theta = gradient_components(field, grid)
    if formulation == "original":
        trace = h_rr + h_thetatheta + h_phiphi
        current = grad_r + cubic_coefficient * (
            (trace - h_rr) * grad_r - h_rtheta * grad_theta
        )
    elif formulation == "shifted":
        shift = 1.0 / (4.0 * cubic_coefficient)
        u_radial = grad_r + radial[:, None] * shift
        current = cubic_coefficient * (
            (h_thetatheta + h_phiphi + 2.0 * shift) * u_radial
            - h_rtheta * grad_theta
        ) - radial[:, None] / (8.0 * cubic_coefficient)
    else:
        raise ValueError("formulation must be original or shifted")

    radial_current = np.array(
        [
            np.interp(radius, radial, current[:, column])
            for column in range(grid.angular_cells)
        ]
    )
    angular_faces = np.linspace(0.0, math.pi / 2.0, grid.angular_cells + 1)
    angular_weights = np.sin(angular_faces[1:]) - np.sin(angular_faces[:-1])
    return float(
        4.0 * math.pi * radius**2 * np.sum(angular_weights * radial_current)
    )

#!/usr/bin/env python3
"""E-023 cubic-Galileon annular-wedge replication.

This module independently discretizes the dimensionless static equation used
by Ogawa, Hiramatsu, and Kobayashi (arXiv:1802.04969),

    laplacian(phi) + c3 * [laplacian(phi)^2 - Hess(phi):Hess(phi)] = mu f,

on the reflection-symmetric half-domain ``0 <= theta <= pi/2``.  The source is
their spherical wedge, ``r1 <= r <= r2`` and ``theta <= theta0``.  ``theta``
is latitude measured from the equatorial plane.  The code uses a cell-centred
centred-difference Poisson operator and the paper's Picard/source iteration with
under-relaxation.  It also reports diagnostics that the original ratio plots
do not provide: an independently recomputed PDE residual, absolute force,
the exact symmetry-centre zero, and the principal-matrix/kinetic signs.

This is a reproduction and numerical-boundary artifact, not evidence that a
Galileon field exists, not an artificial-gravity device, and not a propulsion
model.  The symmetric internal source receives the equal-and-opposite
reaction to any target force.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from typing import Any

try:
    import numpy as np
    from scipy import sparse
    from scipy.sparse import linalg as sparse_linalg
except ImportError as exc:  # pragma: no cover - exercised only without extras
    raise SystemExit(
        "E-023 requires NumPy and SciPy. Create .venv and run "
        "`.venv/bin/python -m pip install -r requirements-research.txt`."
    ) from exc


C = 299_792_458.0
G = 6.67430e-11
EV_J = 1.602_176_634e-19
HBAR_C_EV_M = 1.973_269_804e-7
HBAR_EV_S = 6.582_119_569e-16
REDUCED_PLANCK_MASS_EV = 2.435e27
MPC_M = 3.085_677_581_491_367e22


@dataclass(frozen=True)
class AnnulusConfig:
    """Dimensionless annular-wedge PDE configuration."""

    radial_cells: int = 200
    angular_cells: int = 100
    radial_max: float = 80.0
    radial_mapping_alpha: float = 0.2
    inner_radius: float = 8.0
    outer_radius: float = 30.0
    half_opening_angle: float = 0.05
    mu: float = 36.8
    cubic_coefficient: float = 1.0
    mixing: float = 0.01
    update_tolerance: float = 1.0e-8
    residual_tolerance: float = 2.0e-4
    max_iterations: int = 20_000
    source_discretization: str = "volume_fraction"

    def validate(self) -> None:
        if self.radial_cells < 12 or self.angular_cells < 8:
            raise ValueError("grid is too coarse")
        if self.radial_max <= 0.0:
            raise ValueError("radial_max must be positive")
        if self.radial_mapping_alpha < 0.0:
            raise ValueError("radial mapping alpha must be non-negative")
        if not 0.0 <= self.inner_radius < self.outer_radius < self.radial_max:
            raise ValueError("require 0 <= r1 < r2 < rmax")
        if not 0.0 < self.half_opening_angle <= math.pi / 2.0:
            raise ValueError("opening angle must lie in (0, pi/2]")
        if self.mu < 0.0:
            raise ValueError("mu must be non-negative")
        if self.cubic_coefficient < 0.0:
            raise ValueError("this artifact follows the c3 >= 0 normal branch")
        if not 0.0 < self.mixing <= 1.0:
            raise ValueError("mixing must lie in (0, 1]")
        if self.update_tolerance <= 0.0 or self.residual_tolerance <= 0.0:
            raise ValueError("tolerances must be positive")
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be positive")
        if self.source_discretization not in {"volume_fraction", "cell_center"}:
            raise ValueError(
                "source_discretization must be volume_fraction or cell_center"
            )


@dataclass
class AnnulusSolution:
    """Numerical fields plus convergence diagnostics."""

    config: AnnulusConfig
    radial_centres: np.ndarray
    angular_centres: np.ndarray
    source: np.ndarray
    linear_field: np.ndarray
    nonlinear_field: np.ndarray
    iterations: int
    converged: bool
    relative_update: float
    relative_residual_l2: float
    relative_residual_volume_l2: float
    relative_residual_linf: float
    minimum_spatial_principal_eigenvalue: float
    minimum_spatial_principal_radius: float
    minimum_spatial_principal_theta: float
    minimum_time_kinetic_coefficient: float


def cosmological_galileon_scale_ev(hubble_km_s_mpc: float = 70.0) -> float:
    """Return ``Lambda=(M_Pl (hbar H0)^2)^(1/3)`` in eV."""

    if hubble_km_s_mpc <= 0.0:
        raise ValueError("Hubble benchmark must be positive")
    hubble_s_inverse = hubble_km_s_mpc * 1000.0 / MPC_M
    return (
        REDUCED_PLANCK_MASS_EV * (HBAR_EV_S * hubble_s_inverse) ** 2
    ) ** (1.0 / 3.0)


def _chi_max(config: AnnulusConfig) -> float:
    """Invert ``r=chi+alpha chi^3/3`` at the outer boundary."""

    if config.radial_mapping_alpha == 0.0:
        return config.radial_max
    low = 0.0
    high = config.radial_max
    alpha = config.radial_mapping_alpha
    for _ in range(100):
        middle = 0.5 * (low + high)
        mapped = middle + alpha * middle**3 / 3.0
        if mapped < config.radial_max:
            low = middle
        else:
            high = middle
    return 0.5 * (low + high)


def radial_grid(
    config: AnnulusConfig,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Return chi centres, physical-r centres/faces, and uniform dchi.

    Ogawa's later thesis documents the otherwise omitted mapping

    ``r=chi+alpha chi^3/3``, with ``alpha=0.2``.

    Setting ``alpha=0`` supplies an independent uniform-r check.
    """

    config.validate()
    chi_max = _chi_max(config)
    dchi = chi_max / config.radial_cells
    chi_faces = np.arange(config.radial_cells + 1, dtype=float) * dchi
    chi_centres = (np.arange(config.radial_cells, dtype=float) + 0.5) * dchi
    alpha = config.radial_mapping_alpha
    radial_faces = chi_faces + alpha * chi_faces**3 / 3.0
    radial_centres = chi_centres + alpha * chi_centres**3 / 3.0
    return chi_centres, radial_centres, radial_faces, dchi


def cell_centres(config: AnnulusConfig) -> tuple[np.ndarray, np.ndarray]:
    config.validate()
    dtheta = (math.pi / 2.0) / config.angular_cells
    _, radial, _, _ = radial_grid(config)
    angular = (np.arange(config.angular_cells, dtype=float) + 0.5) * dtheta
    return radial, angular


def spherical_wedge_source(
    config: AnnulusConfig,
    radial: np.ndarray,
    angular: np.ndarray,
) -> np.ndarray:
    """Return cell-average ``mu f`` for the annular spherical wedge.

    The default integrates overlaps exactly in the natural volume coordinates
    ``r^3`` and ``sin(theta)``.  ``cell_center`` preserves the likely
    Heaviside-at-grid-point convention of the published replication.
    """

    if config.source_discretization == "cell_center":
        radial_mask = (radial >= config.inner_radius) & (
            radial <= config.outer_radius
        )
        angular_mask = angular <= config.half_opening_angle
        return config.mu * radial_mask[:, None] * angular_mask[None, :]

    _, _, radial_faces, _ = radial_grid(config)
    angular_faces = np.linspace(
        0.0, math.pi / 2.0, config.angular_cells + 1
    )
    radial_low = np.maximum(radial_faces[:-1], config.inner_radius)
    radial_high = np.minimum(radial_faces[1:], config.outer_radius)
    radial_overlap = np.maximum(radial_high**3 - radial_low**3, 0.0)
    radial_total = radial_faces[1:] ** 3 - radial_faces[:-1] ** 3
    radial_fraction = radial_overlap / radial_total

    angular_low = angular_faces[:-1]
    angular_high = np.minimum(angular_faces[1:], config.half_opening_angle)
    angular_overlap = np.maximum(
        np.sin(angular_high) - np.sin(angular_low), 0.0
    )
    angular_total = np.sin(angular_faces[1:]) - np.sin(angular_faces[:-1])
    angular_fraction = angular_overlap / angular_total
    return config.mu * radial_fraction[:, None] * angular_fraction[None, :]


def cell_volume_weights_dimensionless(config: AnnulusConfig) -> np.ndarray:
    """Return full, reflection-restored cell volumes in units of ``r0^3``."""

    _, _, radial_faces, _ = radial_grid(config)
    angular_faces = np.linspace(
        0.0, math.pi / 2.0, config.angular_cells + 1
    )
    radial_volume = (radial_faces[1:] ** 3 - radial_faces[:-1] ** 3) / 3.0
    angular_volume = np.sin(angular_faces[1:]) - np.sin(angular_faces[:-1])
    return 4.0 * math.pi * radial_volume[:, None] * angular_volume[None, :]


def build_spherical_laplacian(config: AnnulusConfig) -> sparse.csc_matrix:
    """Build the mapped, cell-centred spherical Laplacian.

    This uses the same centred derivatives as
    :func:`orthonormal_hessian_components`, so the discrete Laplacian equals
    the trace of the discrete Hessian.  Regular/reflection ghost cells copy
    the adjacent value.  The outer Dirichlet ghost is its negative, placing
    ``phi=0`` at the boundary face.
    """

    config.validate()
    nr = config.radial_cells
    nt = config.angular_cells
    dt = (math.pi / 2.0) / nt
    radial, angular = cell_centres(config)
    chi, _, _, dchi = radial_grid(config)
    alpha = config.radial_mapping_alpha

    rows: list[int] = []
    columns: list[int] = []
    values: list[float] = []

    def add(row: int, column: int, value: float) -> None:
        rows.append(row)
        columns.append(column)
        values.append(value)

    for i, radius in enumerate(radial):
        mapping_derivative = 1.0 + alpha * chi[i] ** 2
        second_coefficient = 1.0 / mapping_derivative**2
        first_coefficient = (
            -2.0 * alpha * chi[i] / mapping_derivative**3
            + 2.0 / (radius * mapping_derivative)
        )
        radial_minus = (
            second_coefficient / dchi**2
            - first_coefficient / (2.0 * dchi)
        )
        radial_plus = (
            second_coefficient / dchi**2
            + first_coefficient / (2.0 * dchi)
        )
        for j, theta in enumerate(angular):
            row = i * nt + j
            diagonal = -2.0 * second_coefficient / dchi**2

            if i > 0:
                add(row, (i - 1) * nt + j, radial_minus)
            else:
                diagonal += radial_minus
            if i < nr - 1:
                add(row, (i + 1) * nt + j, radial_plus)
            else:
                diagonal -= radial_plus

            angular_minus = (
                1.0 / dt**2 + math.tan(theta) / (2.0 * dt)
            ) / radius**2
            angular_plus = (
                1.0 / dt**2 - math.tan(theta) / (2.0 * dt)
            ) / radius**2
            diagonal -= 2.0 / (radius**2 * dt**2)
            if j > 0:
                add(row, i * nt + (j - 1), angular_minus)
            else:
                diagonal += angular_minus
            if j < nt - 1:
                add(row, i * nt + (j + 1), angular_plus)
            else:
                diagonal += angular_plus

            add(row, row, diagonal)

    return sparse.csc_matrix(
        (values, (rows, columns)), shape=(nr * nt, nr * nt)
    )


def _ghost_padded(field: np.ndarray) -> np.ndarray:
    """Pad cell-centred field for regular/reflecting/Dirichlet boundaries."""

    nr, nt = field.shape
    padded = np.empty((nr + 2, nt + 2), dtype=float)
    padded[1:-1, 1:-1] = field
    padded[0, 1:-1] = field[0, :]  # regular radial centre
    padded[-1, 1:-1] = -field[-1, :]  # phi=0 at outer face
    padded[1:-1, 0] = field[:, 0]  # equatorial reflection
    padded[1:-1, -1] = field[:, -1]  # axial reflection
    padded[0, 0] = field[0, 0]
    padded[0, -1] = field[0, -1]
    padded[-1, 0] = -field[-1, 0]
    padded[-1, -1] = -field[-1, -1]
    return padded


def orthonormal_hessian_components(
    field: np.ndarray,
    config: AnnulusConfig,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return ``Hrr, Hrtheta, Hthetatheta, Hphiphi``.

    Components are in the local orthonormal basis for latitude ``theta``.
    Central differences use symmetry/Dirichlet ghost cells.  The formulas are

    ``Hrr=phi_rr``;
    ``Hrtheta=phi_rtheta/r-phi_theta/r^2``;
    ``Hthetatheta=phi_r/r+phi_thetatheta/r^2``;
    ``Hphiphi=phi_r/r-tan(theta)phi_theta/r^2``.
    """

    if field.shape != (config.radial_cells, config.angular_cells):
        raise ValueError("field shape does not match configuration")
    padded = _ghost_padded(field)
    dt = (math.pi / 2.0) / config.angular_cells
    chi, radial, _, dchi = radial_grid(config)
    _, angular = cell_centres(config)

    phi_chi = (
        padded[2:, 1:-1] - padded[:-2, 1:-1]
    ) / (2.0 * dchi)
    phi_chichi = (
        padded[2:, 1:-1]
        - 2.0 * padded[1:-1, 1:-1]
        + padded[:-2, 1:-1]
    ) / dchi**2
    phi_t = (padded[1:-1, 2:] - padded[1:-1, :-2]) / (2.0 * dt)
    phi_tt = (
        padded[1:-1, 2:]
        - 2.0 * padded[1:-1, 1:-1]
        + padded[1:-1, :-2]
    ) / dt**2
    phi_chit = (
        padded[2:, 2:]
        - padded[2:, :-2]
        - padded[:-2, 2:]
        + padded[:-2, :-2]
    ) / (4.0 * dchi * dt)

    r = radial[:, None]
    chi_column = chi[:, None]
    theta = angular[None, :]
    alpha = config.radial_mapping_alpha
    mapping_derivative = 1.0 + alpha * chi_column**2
    phi_r = phi_chi / mapping_derivative
    phi_rr = (
        phi_chichi / mapping_derivative**2
        - 2.0
        * alpha
        * chi_column
        * phi_chi
        / mapping_derivative**3
    )
    phi_rt_coordinate = phi_chit / mapping_derivative
    h_rr = phi_rr
    h_rt = phi_rt_coordinate / r - phi_t / r**2
    h_tt = phi_r / r + phi_tt / r**2
    h_pp = phi_r / r - np.tan(theta) * phi_t / r**2
    return h_rr, h_rt, h_tt, h_pp


def nonlinear_invariant(field: np.ndarray, config: AnnulusConfig) -> np.ndarray:
    """Return ``laplacian(phi)^2-Hess(phi):Hess(phi)``."""

    h_rr, h_rt, h_tt, h_pp = orthonormal_hessian_components(field, config)
    laplacian = h_rr + h_tt + h_pp
    hessian_squared = h_rr**2 + h_tt**2 + h_pp**2 + 2.0 * h_rt**2
    return laplacian**2 - hessian_squared


def principal_coefficients_from_hessian(
    h_rr: np.ndarray,
    h_rt: np.ndarray,
    h_tt: np.ndarray,
    h_pp: np.ndarray,
    cubic_coefficient: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return minimum spatial eigenvalue and time kinetic coefficient.

    Linearizing the static operator gives

    ``A_ij = delta_ij + 2 c3 [(laplacian phi) delta_ij - H_ij]``.

    In the same flat-space convention, the coefficient of the perturbation's
    second time derivative is ``K_t=1+2 c3 laplacian(phi)``.  Positivity is a
    necessary branch-health check, not a sufficient UV-stability theorem.
    """

    if cubic_coefficient < 0.0:
        raise ValueError("cubic coefficient must be non-negative")
    trace = h_rr + h_tt + h_pp
    discriminant = np.sqrt((h_rr - h_tt) ** 2 + 4.0 * h_rt**2)
    h_meridional_low = 0.5 * (h_rr + h_tt - discriminant)
    h_meridional_high = 0.5 * (h_rr + h_tt + discriminant)
    spatial = np.stack(
        [
            1.0 + 2.0 * cubic_coefficient * (trace - h_meridional_low),
            1.0 + 2.0 * cubic_coefficient * (trace - h_meridional_high),
            1.0 + 2.0 * cubic_coefficient * (trace - h_pp),
        ],
        axis=0,
    )
    return np.min(spatial, axis=0), 1.0 + 2.0 * cubic_coefficient * trace


def solve_annular_wedge(config: AnnulusConfig) -> AnnulusSolution:
    """Solve the linear reference and paper-style nonlinear Picard problem."""

    config.validate()
    radial, angular = cell_centres(config)
    source = spherical_wedge_source(config, radial, angular)
    laplacian = build_spherical_laplacian(config)
    factor = sparse_linalg.splu(laplacian)
    linear = factor.solve(source.ravel()).reshape(source.shape)

    field = linear.copy()
    relative_update = 0.0
    converged = config.cubic_coefficient == 0.0 or config.mu == 0.0
    iterations = 0

    if not converged:
        for iteration in range(1, config.max_iterations + 1):
            nonlinear_source = nonlinear_invariant(field, config)
            star = factor.solve(
                (source - config.cubic_coefficient * nonlinear_source).ravel()
            ).reshape(source.shape)
            new_field = (
                (1.0 - config.mixing) * field + config.mixing * star
            )
            denominator = float(np.linalg.norm(new_field.ravel()))
            relative_update = float(
                np.linalg.norm((new_field - field).ravel())
                / max(denominator, np.finfo(float).tiny)
            )
            if not np.isfinite(relative_update) or not np.all(np.isfinite(new_field)):
                raise RuntimeError("nonlinear iteration left the finite branch")
            field = new_field
            iterations = iteration
            if relative_update < config.update_tolerance:
                converged = True
                break

    residual = (
        laplacian @ field.ravel()
        + config.cubic_coefficient * nonlinear_invariant(field, config).ravel()
        - source.ravel()
    ).reshape(source.shape)
    source_l2 = float(np.linalg.norm(source.ravel()))
    source_linf = float(np.max(np.abs(source)))
    relative_residual_l2 = float(
        np.linalg.norm(residual.ravel()) / max(source_l2, np.finfo(float).tiny)
    )
    volume_weights = cell_volume_weights_dimensionless(config)
    relative_residual_volume_l2 = float(
        np.sqrt(np.sum(volume_weights * residual**2))
        / max(
            float(np.sqrt(np.sum(volume_weights * source**2))),
            np.finfo(float).tiny,
        )
    )
    relative_residual_linf = float(
        np.max(np.abs(residual)) / max(source_linf, np.finfo(float).tiny)
    )

    hessian = orthonormal_hessian_components(field, config)
    spatial_min, time_kinetic = principal_coefficients_from_hessian(
        *hessian, config.cubic_coefficient
    )
    minimum_index = np.unravel_index(int(np.argmin(spatial_min)), spatial_min.shape)
    residual_pass = relative_residual_l2 < config.residual_tolerance
    converged = converged and residual_pass

    return AnnulusSolution(
        config=config,
        radial_centres=radial,
        angular_centres=angular,
        source=source,
        linear_field=linear,
        nonlinear_field=field,
        iterations=iterations,
        converged=converged,
        relative_update=relative_update,
        relative_residual_l2=relative_residual_l2,
        relative_residual_volume_l2=relative_residual_volume_l2,
        relative_residual_linf=relative_residual_linf,
        minimum_spatial_principal_eigenvalue=float(np.min(spatial_min)),
        minimum_spatial_principal_radius=float(radial[minimum_index[0]]),
        minimum_spatial_principal_theta=float(angular[minimum_index[1]]),
        minimum_time_kinetic_coefficient=float(np.min(time_kinetic)),
    )


def gradient_components(
    field: np.ndarray,
    config: AnnulusConfig,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return orthonormal ``(dphi/dr, dphi/(r dtheta), magnitude)``."""

    padded = _ghost_padded(field)
    dt = (math.pi / 2.0) / config.angular_cells
    chi, radial, _, dchi = radial_grid(config)
    alpha = config.radial_mapping_alpha
    phi_chi = (
        padded[2:, 1:-1] - padded[:-2, 1:-1]
    ) / (2.0 * dchi)
    radial_component = phi_chi / (
        1.0 + alpha * chi[:, None] ** 2
    )
    angular_component = (
        padded[1:-1, 2:] - padded[1:-1, :-2]
    ) / (2.0 * dt * radial[:, None])
    magnitude = np.hypot(radial_component, angular_component)
    return radial_component, angular_component, magnitude


def _interpolate_radial(
    values: np.ndarray,
    radial_centres: np.ndarray,
    radius: float,
) -> float:
    if radius <= 0.0:
        return 0.0
    if radius < radial_centres[0]:
        # A regular vector gradient vanishes linearly at the symmetry centre.
        # Holding the first-cell magnitude constant down to arbitrarily small
        # positive radius would manufacture a finite force next to r=0.
        return float(values[0] * radius / radial_centres[0])
    if radius >= radial_centres[-1]:
        return float(values[-1])
    return float(np.interp(radius, radial_centres, values, left=values[0]))


def sample_ray(
    solution: AnnulusSolution,
    theta: float = math.pi / 10.0,
    maximum_radius: float = 12.0,
    samples: int = 601,
    ratio_floor_fraction: float = 1.0e-8,
) -> dict[str, Any]:
    """Sample absolute and ratio observables along the paper's comparison ray."""

    if not 0.0 <= theta <= math.pi / 2.0:
        raise ValueError("ray angle must lie in [0, pi/2]")
    if not 0.0 < maximum_radius < solution.config.radial_max:
        raise ValueError("maximum ray radius must lie inside the box")
    if samples < 3:
        raise ValueError("at least three ray samples are required")
    if ratio_floor_fraction <= 0.0:
        raise ValueError("ratio floor must be positive")

    linear_radial_component, linear_angular_component, _ = gradient_components(
        solution.linear_field, solution.config
    )
    nonlinear_radial_component, nonlinear_angular_component, _ = gradient_components(
        solution.nonlinear_field, solution.config
    )
    angular = solution.angular_centres
    # Interpolate in theta first, then in radius.  The exact centre is inserted
    # analytically as zero; 0/0 is reported as null rather than infinity.
    upper = int(np.searchsorted(angular, theta))
    upper = min(max(upper, 1), len(angular) - 1)
    lower = upper - 1
    weight = (theta - angular[lower]) / (angular[upper] - angular[lower])
    weight = min(max(float(weight), 0.0), 1.0)
    def angular_interpolate(component: np.ndarray) -> np.ndarray:
        return (
            (1.0 - weight) * component[:, lower]
            + weight * component[:, upper]
        )

    linear_radial = angular_interpolate(linear_radial_component)
    linear_angular = angular_interpolate(linear_angular_component)
    nonlinear_radial = angular_interpolate(nonlinear_radial_component)
    nonlinear_angular = angular_interpolate(nonlinear_angular_component)

    # Include native radial centres as well as the uniform plotting samples.
    # Otherwise the reported ratio maximum depends on whether an arbitrary
    # plotting grid happens to hit the innermost resolved shell.
    radii = np.unique(
        np.concatenate(
            [
                np.linspace(0.0, maximum_radius, samples),
                solution.radial_centres[
                    solution.radial_centres <= maximum_radius
                ],
            ]
        )
    )
    linear_radial_samples = np.array(
        [
            _interpolate_radial(linear_radial, solution.radial_centres, radius)
            for radius in radii
        ]
    )
    linear_angular_samples = np.array(
        [
            _interpolate_radial(linear_angular, solution.radial_centres, radius)
            for radius in radii
        ]
    )
    nonlinear_radial_samples = np.array(
        [
            _interpolate_radial(
                nonlinear_radial, solution.radial_centres, radius
            )
            for radius in radii
        ]
    )
    nonlinear_angular_samples = np.array(
        [
            _interpolate_radial(
                nonlinear_angular, solution.radial_centres, radius
            )
            for radius in radii
        ]
    )
    linear_samples = np.hypot(linear_radial_samples, linear_angular_samples)
    nonlinear_samples = np.hypot(
        nonlinear_radial_samples, nonlinear_angular_samples
    )
    floor = ratio_floor_fraction * max(
        float(np.max(linear_samples)), np.finfo(float).tiny
    )
    valid = linear_samples > floor
    ratio = np.full_like(linear_samples, np.nan)
    ratio[valid] = nonlinear_samples[valid] / linear_samples[valid]

    valid_indices = np.flatnonzero(np.isfinite(ratio))
    peak_absolute_index = int(np.argmax(nonlinear_samples))
    anti = np.flatnonzero(np.isfinite(ratio) & (ratio > 1.0))
    anti_interval = None
    peak_absolute_anti_screened_gradient = None
    peak_absolute_anti_screened_gradient_radius = None
    if anti.size:
        anti_interval = [float(radii[anti[0]]), float(radii[anti[-1]])]
        anti_peak_index = int(anti[np.argmax(nonlinear_samples[anti])])
        peak_absolute_anti_screened_gradient = float(
            nonlinear_samples[anti_peak_index]
        )
        peak_absolute_anti_screened_gradient_radius = float(
            radii[anti_peak_index]
        )
    peak_ratio = None
    peak_ratio_radius = None
    nonlinear_at_ratio_peak = None
    linear_at_ratio_peak = None
    if valid_indices.size:
        peak_ratio_index = int(
            valid_indices[np.argmax(ratio[valid_indices])]
        )
        peak_ratio = float(ratio[peak_ratio_index])
        peak_ratio_radius = float(radii[peak_ratio_index])
        nonlinear_at_ratio_peak = float(nonlinear_samples[peak_ratio_index])
        linear_at_ratio_peak = float(linear_samples[peak_ratio_index])

    reference_linear = None
    reference_nonlinear = None
    reference_ratio = None
    if maximum_radius >= 1.0:
        reference_linear = float(np.interp(1.0, radii, linear_samples))
        if reference_linear > floor:
            reference_nonlinear = float(
                np.interp(1.0, radii, nonlinear_samples)
            )
            reference_ratio = reference_nonlinear / reference_linear

    return {
        "theta_rad": theta,
        "centre_linear_gradient": 0.0,
        "centre_nonlinear_gradient": 0.0,
        "centre_ratio": None,
        "ratio_floor": floor,
        "peak_ratio": peak_ratio,
        "peak_ratio_radius": peak_ratio_radius,
        "nonlinear_gradient_at_ratio_peak": nonlinear_at_ratio_peak,
        "linear_gradient_at_ratio_peak": linear_at_ratio_peak,
        "peak_absolute_nonlinear_gradient": float(
            nonlinear_samples[peak_absolute_index]
        ),
        "peak_absolute_nonlinear_gradient_radius": float(
            radii[peak_absolute_index]
        ),
        "peak_absolute_anti_screened_gradient": (
            peak_absolute_anti_screened_gradient
        ),
        "peak_absolute_anti_screened_gradient_radius": (
            peak_absolute_anti_screened_gradient_radius
        ),
        "ratio_at_r_equals_1": reference_ratio,
        "linear_gradient_at_r_equals_1": reference_linear,
        "nonlinear_gradient_at_r_equals_1": reference_nonlinear,
        "anti_screened_radial_interval": anti_interval,
    }


def wedge_volume_dimensionless(config: AnnulusConfig) -> float:
    """Return the full reflection-symmetric wedge volume in units of r0^3."""

    return (
        4.0
        * math.pi
        / 3.0
        * math.sin(config.half_opening_angle)
        * (config.outer_radius**3 - config.inner_radius**3)
    )


def represented_source_volume_dimensionless(
    config: AnnulusConfig, source: np.ndarray
) -> float:
    """Return the volume represented by a nonzero-``mu`` discrete source."""

    if config.mu <= 0.0:
        return 0.0
    return float(
        np.sum(cell_volume_weights_dimensionless(config) * source / config.mu)
    )


def physical_density_kg_m3(mu: float, lambda_ev: float, beta: float) -> float:
    """Translate paper ``mu`` to mass density for ``M=Lambda``."""

    if mu < 0.0 or lambda_ev <= 0.0 or beta <= 0.0:
        raise ValueError("mu must be non-negative; Lambda and beta positive")
    energy_density_ev4 = mu * lambda_ev**3 * REDUCED_PLANCK_MASS_EV / beta
    return energy_density_ev4 * EV_J / (C**2 * HBAR_C_EV_M**3)


def dimensionless_gradient_to_acceleration_m_s2(
    gradient: float,
    r0_m: float,
    lambda_ev: float,
    beta: float,
) -> float:
    """Convert ``|grad_bar phi|`` to scalar acceleration."""

    if gradient < 0.0 or r0_m <= 0.0 or lambda_ev <= 0.0 or beta <= 0.0:
        raise ValueError("gradient non-negative; r0, Lambda, beta positive")
    return (
        beta
        * lambda_ev**3
        * r0_m
        * C**2
        / (REDUCED_PLANCK_MASS_EV * HBAR_C_EV_M**2)
        * gradient
    )


def summarize_solution(
    solution: AnnulusSolution,
    r0_m: float = 1.0,
    lambda_ev: float | None = None,
    beta: float = 1.0,
    target_mass_kg: float = 70.0,
) -> dict[str, Any]:
    """Return a JSON-safe replication and physical-scale report."""

    if r0_m <= 0.0 or beta <= 0.0 or target_mass_kg <= 0.0:
        raise ValueError("physical scales must be positive")
    if lambda_ev is None:
        lambda_ev = cosmological_galileon_scale_ev()
    ray_maximum = min(
        solution.config.outer_radius,
        0.95 * solution.config.radial_max,
    )
    corrected_ray = sample_ray(
        solution, theta=math.pi / 10.0, maximum_radius=ray_maximum
    )
    arxiv_caption_ray = sample_ray(
        solution, theta=2.0 * math.pi / 5.0, maximum_radius=ray_maximum
    )
    density = physical_density_kg_m3(solution.config.mu, lambda_ev, beta)
    nominal_volume = wedge_volume_dimensionless(solution.config)
    represented_volume = represented_source_volume_dimensionless(
        solution.config, solution.source
    )
    source_mass = density * nominal_volume * r0_m**3
    represented_source_mass = density * represented_volume * r0_m**3
    nonlinear_acceleration = dimensionless_gradient_to_acceleration_m_s2(
        corrected_ray["peak_absolute_nonlinear_gradient"], r0_m, lambda_ev, beta
    )
    resolved_acceleration = dimensionless_gradient_to_acceleration_m_s2(
        corrected_ray["nonlinear_gradient_at_r_equals_1"],
        r0_m,
        lambda_ev,
        beta,
    )
    acceleration_at_ratio_peak = dimensionless_gradient_to_acceleration_m_s2(
        corrected_ray["nonlinear_gradient_at_ratio_peak"], r0_m, lambda_ev, beta
    )
    linear_acceleration_at_ratio_peak = dimensionless_gradient_to_acceleration_m_s2(
        corrected_ray["linear_gradient_at_ratio_peak"], r0_m, lambda_ev, beta
    )
    newtonian_at_ratio_peak = linear_acceleration_at_ratio_peak / (2.0 * beta**2)
    target_force = target_mass_kg * acceleration_at_ratio_peak
    target_force_resolved = target_mass_kg * resolved_acceleration
    target_force_peak = target_mass_kg * nonlinear_acceleration

    return {
        "epistemic_status": (
            "hypothetical cubic-Galileon PDE reproduction; not a detected field "
            "or artificial-gravity device"
        ),
        "configuration": {
            "radial_cells": solution.config.radial_cells,
            "angular_cells": solution.config.angular_cells,
            "radial_max": solution.config.radial_max,
            "radial_mapping_alpha": solution.config.radial_mapping_alpha,
            "inner_radius": solution.config.inner_radius,
            "outer_radius": solution.config.outer_radius,
            "half_opening_angle": solution.config.half_opening_angle,
            "mu": solution.config.mu,
            "cubic_coefficient": solution.config.cubic_coefficient,
            "mixing": solution.config.mixing,
            "source_discretization": solution.config.source_discretization,
        },
        "numerics": {
            "iterations": solution.iterations,
            "converged_update_and_residual": solution.converged,
            "relative_update": solution.relative_update,
            "relative_residual_l2": solution.relative_residual_l2,
            "relative_residual_algebraic_l2": solution.relative_residual_l2,
            "relative_residual_volume_l2": (
                solution.relative_residual_volume_l2
            ),
            "relative_residual_linf": solution.relative_residual_linf,
            "minimum_spatial_principal_eigenvalue": (
                solution.minimum_spatial_principal_eigenvalue
            ),
            "minimum_spatial_principal_location": {
                "radius": solution.minimum_spatial_principal_radius,
                "theta": solution.minimum_spatial_principal_theta,
            },
            "minimum_time_kinetic_coefficient": (
                solution.minimum_time_kinetic_coefficient
            ),
            "healthy_signs": (
                solution.minimum_spatial_principal_eigenvalue > 0.0
                and solution.minimum_time_kinetic_coefficient > 0.0
            ),
        },
        "dimensionless_ray": corrected_ray,
        "arxiv_caption_ray": arxiv_caption_ray,
        "ray_discrepancy_note": (
            "arXiv labels the slice theta=2pi/5; Ogawa's later thesis "
            "uses theta=pi/10, the complementary latitude, so both are reported"
        ),
        "physical_translation": {
            "conditional_on_M_equals_Lambda": True,
            "r0_m": r0_m,
            "lambda_ev": lambda_ev,
            "beta": beta,
            "density_kg_m3": density,
            "source_mass_kg": source_mass,
            "represented_source_mass_kg": represented_source_mass,
            "represented_to_nominal_source_volume": (
                represented_volume / nominal_volume
            ),
            "peak_absolute_scalar_acceleration_m_s2": nonlinear_acceleration,
            "scalar_acceleration_at_r_equals_1_m_s2": resolved_acceleration,
            "scalar_acceleration_at_ratio_peak_m_s2": acceleration_at_ratio_peak,
            "linear_scalar_acceleration_at_ratio_peak_m_s2": (
                linear_acceleration_at_ratio_peak
            ),
            "ordinary_newtonian_acceleration_at_ratio_peak_m_s2": (
                newtonian_at_ratio_peak
            ),
            "target_mass_kg": target_mass_kg,
            "target_scalar_force_at_ratio_peak_n": target_force,
            "target_scalar_force_at_r_equals_1_n": target_force_resolved,
            "target_scalar_force_at_peak_absolute_n": target_force_peak,
            "equal_opposite_source_reaction_n": target_force_peak,
        },
    }


def _format_report(report: dict[str, Any]) -> str:
    numerics = report["numerics"]
    ray = report["dimensionless_ray"]
    physical = report["physical_translation"]
    return "\n".join(
        [
            "E-023 annular cubic-Galileon replication",
            f"converged: {numerics['converged_update_and_residual']}",
            f"iterations: {numerics['iterations']}",
            f"relative update: {numerics['relative_update']:.3e}",
            (
                "relative residual algebraic L2: "
                f"{numerics['relative_residual_algebraic_l2']:.3e}"
            ),
            (
                "relative residual volume L2: "
                f"{numerics['relative_residual_volume_l2']:.3e}"
            ),
            f"relative residual Linf: {numerics['relative_residual_linf']:.3e}",
            (
                "minimum spatial/time coefficients: "
                f"{numerics['minimum_spatial_principal_eigenvalue']:.6g}, "
                f"{numerics['minimum_time_kinetic_coefficient']:.6g}"
            ),
            (
                "ray peak ratio: "
                f"{ray['peak_ratio']:.6g} at r/r0={ray['peak_ratio_radius']:.4g}"
            ),
            (
                "absolute dimensionless gradient at ratio peak: "
                f"{ray['nonlinear_gradient_at_ratio_peak']:.6g}"
            ),
            (
                "conditional source density/mass: "
                f"{physical['density_kg_m3']:.3e} kg/m^3, "
                f"{physical['source_mass_kg']:.3e} kg"
            ),
            (
                "conditional scalar acceleration at ratio peak: "
                f"{physical['scalar_acceleration_at_ratio_peak_m_s2']:.3e} m/s^2"
            ),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radial-cells", type=int, default=200)
    parser.add_argument("--angular-cells", type=int, default=100)
    parser.add_argument("--radial-max", type=float, default=80.0)
    parser.add_argument("--radial-mapping-alpha", type=float, default=0.2)
    parser.add_argument("--inner-radius", type=float, default=8.0)
    parser.add_argument("--outer-radius", type=float, default=30.0)
    parser.add_argument("--half-opening-angle", type=float, default=0.05)
    parser.add_argument("--mu", type=float, default=36.8)
    parser.add_argument("--c3", type=float, default=1.0)
    parser.add_argument("--mixing", type=float, default=0.01)
    parser.add_argument("--update-tolerance", type=float, default=1.0e-8)
    parser.add_argument("--residual-tolerance", type=float, default=2.0e-4)
    parser.add_argument("--max-iterations", type=int, default=20_000)
    parser.add_argument(
        "--source-discretization",
        choices=("volume_fraction", "cell_center"),
        default="volume_fraction",
    )
    parser.add_argument("--r0-m", type=float, default=1.0)
    parser.add_argument("--lambda-ev", type=float)
    parser.add_argument("--beta", type=float, default=1.0)
    parser.add_argument("--target-mass-kg", type=float, default=70.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    config = AnnulusConfig(
        radial_cells=args.radial_cells,
        angular_cells=args.angular_cells,
        radial_max=args.radial_max,
        radial_mapping_alpha=args.radial_mapping_alpha,
        inner_radius=args.inner_radius,
        outer_radius=args.outer_radius,
        half_opening_angle=args.half_opening_angle,
        mu=args.mu,
        cubic_coefficient=args.c3,
        mixing=args.mixing,
        update_tolerance=args.update_tolerance,
        residual_tolerance=args.residual_tolerance,
        max_iterations=args.max_iterations,
        source_discretization=args.source_discretization,
    )
    solution = solve_annular_wedge(config)
    report = summarize_solution(
        solution,
        r0_m=args.r0_m,
        lambda_ev=args.lambda_ev,
        beta=args.beta,
        target_mass_kg=args.target_mass_kg,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_format_report(report))


if __name__ == "__main__":
    main()

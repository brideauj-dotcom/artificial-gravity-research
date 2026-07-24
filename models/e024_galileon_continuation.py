#!/usr/bin/env python3
"""E-024 smooth-source and shifted-2-Hessian validation campaign.

The artifact asks a deliberately narrow question: does the dilute annular
cubic-Galileon enhancement from E-023 survive a mass-preserving smooth source,
source-amplitude continuation on the normal branch, an independently coded
shifted-2-Hessian Newton solve, and a divergence-flux check?

The two nonlinear paths are intentionally different.  The reference path uses
the E-023 mapped-grid Picard/Poisson formulation.  The shifted path imports no
E-023 derivatives or residuals; it follows the admissible branch from zero
source with damped Newton--Krylov steps.  Both paths still use the same grid
family, so this is stronger than an algebraic re-evaluation but is not the
wide-stencil monotone 2-Hessian proof required for a final continuum claim.

Nothing here establishes that a Galileon field exists, creates useful gravity,
enables FTL travel, or supplies reactionless propulsion.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from typing import Any

import numpy as np
from scipy.sparse import linalg as sparse_linalg

try:
    from models.e023_galileon_annulus import (
        AnnulusConfig,
        AnnulusSolution,
        build_spherical_laplacian,
        cell_centres,
        cell_volume_weights_dimensionless,
        gradient_components as e023_gradient_components,
        nonlinear_invariant,
        orthonormal_hessian_components,
        principal_coefficients_from_hessian,
        sample_ray,
        wedge_volume_dimensionless,
    )
    from models.e024_shifted_2hessian import (
        ShiftedGrid,
        branch_diagnostic_details as shifted_branch_diagnostic_details,
        branch_diagnostics as shifted_branch_diagnostics,
        cell_volume_weights as shifted_cell_volume_weights,
        gradient_components as shifted_gradient_components,
        grid_coordinates as shifted_grid_coordinates,
        original_residual as shifted_original_residual,
        shifted_residual,
        solve_shifted_continuation,
        surface_flux,
    )
except ModuleNotFoundError:  # Direct ``python models/...`` execution.
    from e023_galileon_annulus import (  # type: ignore[no-redef]
        AnnulusConfig,
        AnnulusSolution,
        build_spherical_laplacian,
        cell_centres,
        cell_volume_weights_dimensionless,
        gradient_components as e023_gradient_components,
        nonlinear_invariant,
        orthonormal_hessian_components,
        principal_coefficients_from_hessian,
        sample_ray,
        wedge_volume_dimensionless,
    )
    from e024_shifted_2hessian import (  # type: ignore[no-redef]
        ShiftedGrid,
        branch_diagnostic_details as shifted_branch_diagnostic_details,
        branch_diagnostics as shifted_branch_diagnostics,
        cell_volume_weights as shifted_cell_volume_weights,
        gradient_components as shifted_gradient_components,
        grid_coordinates as shifted_grid_coordinates,
        original_residual as shifted_original_residual,
        shifted_residual,
        solve_shifted_continuation,
        surface_flux,
    )


@dataclass(frozen=True)
class ValidationConfig:
    annulus: AnnulusConfig
    radial_smoothing_width: float = 2.0
    angular_smoothing_width: float = 0.08
    quadrature_order: int = 4
    picard_mixing: float = 0.01
    picard_update_tolerance: float = 1.0e-11
    picard_residual_tolerance: float = 2.0e-4
    picard_max_iterations: int = 30_000
    continuation_steps: int = 10
    shifted_relative_tolerance: float = 1.0e-7
    shifted_newton_max_iterations: int = 25
    shifted_gmres_relative_tolerance: float = 1.0e-8
    shifted_gmres_max_iterations: int = 20

    def validate(self) -> None:
        self.annulus.validate()
        if self.annulus.cubic_coefficient <= 0.0:
            raise ValueError("E-024 shifted validation requires c3 > 0")
        if self.radial_smoothing_width <= 0.0:
            raise ValueError("radial smoothing width must be positive")
        if self.angular_smoothing_width <= 0.0:
            raise ValueError("angular smoothing width must be positive")
        if (
            self.annulus.inner_radius - self.radial_smoothing_width / 2.0
            < 0.0
        ):
            raise ValueError("inner radial smoothing layer crosses the origin")
        if (
            self.annulus.outer_radius + self.radial_smoothing_width / 2.0
            >= self.annulus.radial_max
        ):
            raise ValueError("outer radial smoothing layer reaches the box")
        if self.angular_smoothing_width > 2.0 * self.annulus.half_opening_angle:
            raise ValueError(
                "angular smoothing width may not exceed twice theta0"
            )
        if self.quadrature_order < 2:
            raise ValueError("source quadrature order must be at least two")
        if not 0.0 < self.picard_mixing <= 1.0:
            raise ValueError("Picard mixing must lie in (0, 1]")
        if (
            self.picard_update_tolerance <= 0.0
            or self.picard_residual_tolerance <= 0.0
        ):
            raise ValueError("Picard tolerances must be positive")
        if self.picard_max_iterations < 1 or self.continuation_steps < 1:
            raise ValueError("iteration counts must be positive")


@dataclass(frozen=True)
class SmoothSource:
    values: np.ndarray
    unnormalized_volume: float
    nominal_volume: float
    normalization: float
    maximum_normalized_shape: float
    radial_inner_transition_cells: int
    radial_outer_transition_cells: int
    angular_transition_cells: int
    radial_inner_cells_per_width: float
    radial_outer_cells_per_width: float
    angular_cells_per_width: float


@dataclass
class PicardResult:
    field: np.ndarray
    linear_field: np.ndarray
    iterations: int
    converged: bool
    relative_update: float
    relative_residual_l2: float
    relative_residual_volume_l2: float
    relative_residual_linf: float
    minimum_spatial_principal: float
    minimum_time_kinetic: float


def quintic_smoothstep(value: np.ndarray) -> np.ndarray:
    """Compact C2 transition from zero to one on ``0 <= value <= 1``."""

    clipped = np.clip(value, 0.0, 1.0)
    return clipped**3 * (10.0 - 15.0 * clipped + 6.0 * clipped**2)


def _radial_window(
    radius: np.ndarray,
    inner_radius: float,
    outer_radius: float,
    width: float,
) -> np.ndarray:
    rising = quintic_smoothstep(
        (radius - (inner_radius - width / 2.0)) / width
    )
    falling = quintic_smoothstep(
        ((outer_radius + width / 2.0) - radius) / width
    )
    return rising * falling


def _angular_window(
    latitude: np.ndarray,
    half_opening_angle: float,
    width: float,
) -> np.ndarray:
    return quintic_smoothstep(
        ((half_opening_angle + width / 2.0) - latitude) / width
    )


def _cell_average_in_natural_coordinate(
    lower: np.ndarray,
    upper: np.ndarray,
    transform: Any,
    window: Any,
    order: int,
) -> np.ndarray:
    nodes, weights = np.polynomial.legendre.leggauss(order)
    midpoint = 0.5 * (lower + upper)
    half_width = 0.5 * (upper - lower)
    natural_samples = midpoint[:, None] + half_width[:, None] * nodes[None, :]
    physical_samples = transform(natural_samples)
    return 0.5 * np.sum(weights[None, :] * window(physical_samples), axis=1)


def smooth_mass_preserving_source(config: ValidationConfig) -> SmoothSource:
    """Return a positive C2 source with the sharp wedge's total scalar charge."""

    config.validate()
    annulus = config.annulus
    _, radial_faces = _e023_radial_centres_and_faces(annulus)
    angular_faces = np.linspace(
        0.0, math.pi / 2.0, annulus.angular_cells + 1
    )

    radial_average = _cell_average_in_natural_coordinate(
        radial_faces[:-1] ** 3,
        radial_faces[1:] ** 3,
        lambda value: np.cbrt(value),
        lambda radius: _radial_window(
            radius,
            annulus.inner_radius,
            annulus.outer_radius,
            config.radial_smoothing_width,
        ),
        config.quadrature_order,
    )
    angular_average = _cell_average_in_natural_coordinate(
        np.sin(angular_faces[:-1]),
        np.sin(angular_faces[1:]),
        lambda value: np.arcsin(np.clip(value, 0.0, 1.0)),
        lambda latitude: _angular_window(
            latitude,
            annulus.half_opening_angle,
            config.angular_smoothing_width,
        ),
        config.quadrature_order,
    )
    unnormalized_shape = radial_average[:, None] * angular_average[None, :]
    volume_weights = cell_volume_weights_dimensionless(annulus)
    unnormalized_volume = float(np.sum(volume_weights * unnormalized_shape))
    nominal_volume = wedge_volume_dimensionless(annulus)
    normalization = nominal_volume / unnormalized_volume
    normalized_shape = normalization * unnormalized_shape

    radial_inner_cells = int(
        np.count_nonzero(
            (radial_faces[1:] > annulus.inner_radius - config.radial_smoothing_width / 2.0)
            & (radial_faces[:-1] < annulus.inner_radius + config.radial_smoothing_width / 2.0)
        )
    )
    radial_outer_cells = int(
        np.count_nonzero(
            (radial_faces[1:] > annulus.outer_radius - config.radial_smoothing_width / 2.0)
            & (radial_faces[:-1] < annulus.outer_radius + config.radial_smoothing_width / 2.0)
        )
    )
    angular_cells = int(
        np.count_nonzero(
            (angular_faces[1:] > annulus.half_opening_angle - config.angular_smoothing_width / 2.0)
            & (angular_faces[:-1] < annulus.half_opening_angle + config.angular_smoothing_width / 2.0)
        )
    )
    radial_widths = np.diff(radial_faces)
    inner_mask = (
        (radial_faces[1:] > annulus.inner_radius - config.radial_smoothing_width / 2.0)
        & (radial_faces[:-1] < annulus.inner_radius + config.radial_smoothing_width / 2.0)
    )
    outer_mask = (
        (radial_faces[1:] > annulus.outer_radius - config.radial_smoothing_width / 2.0)
        & (radial_faces[:-1] < annulus.outer_radius + config.radial_smoothing_width / 2.0)
    )
    radial_inner_cells_per_width = config.radial_smoothing_width / float(
        np.max(radial_widths[inner_mask])
    )
    radial_outer_cells_per_width = config.radial_smoothing_width / float(
        np.max(radial_widths[outer_mask])
    )
    angular_cells_per_width = config.angular_smoothing_width / float(
        angular_faces[1] - angular_faces[0]
    )
    return SmoothSource(
        values=annulus.mu * normalized_shape,
        unnormalized_volume=unnormalized_volume,
        nominal_volume=nominal_volume,
        normalization=normalization,
        maximum_normalized_shape=float(np.max(normalized_shape)),
        radial_inner_transition_cells=radial_inner_cells,
        radial_outer_transition_cells=radial_outer_cells,
        angular_transition_cells=angular_cells,
        radial_inner_cells_per_width=radial_inner_cells_per_width,
        radial_outer_cells_per_width=radial_outer_cells_per_width,
        angular_cells_per_width=angular_cells_per_width,
    )


def _e023_radial_centres_and_faces(
    annulus: AnnulusConfig,
) -> tuple[np.ndarray, np.ndarray]:
    """Use public grid values while avoiding dependence on private helpers."""

    radial, _ = cell_centres(annulus)
    shifted_grid = ShiftedGrid(
        radial_cells=annulus.radial_cells,
        angular_cells=annulus.angular_cells,
        radial_max=annulus.radial_max,
        radial_mapping_alpha=annulus.radial_mapping_alpha,
    )
    _, shifted_radial, radial_faces, _, _, _ = shifted_grid_coordinates(
        shifted_grid
    )
    if not np.allclose(radial, shifted_radial, rtol=0.0, atol=2.0e-13):
        raise RuntimeError("independent grids disagree")
    return radial, radial_faces


def _e023_residual(
    field: np.ndarray,
    source: np.ndarray,
    annulus: AnnulusConfig,
    laplacian: Any,
) -> np.ndarray:
    return (
        laplacian @ field.ravel()
        + annulus.cubic_coefficient
        * nonlinear_invariant(field, annulus).ravel()
        - source.ravel()
    ).reshape(source.shape)


def solve_picard_reference(
    config: ValidationConfig,
    source: np.ndarray,
) -> PicardResult:
    """Solve the smooth source with the original E-023 Picard formulation."""

    config.validate()
    annulus = config.annulus
    if source.shape != (annulus.radial_cells, annulus.angular_cells):
        raise ValueError("source shape does not match annulus grid")
    laplacian = build_spherical_laplacian(annulus)
    factor = sparse_linalg.splu(laplacian)
    linear = factor.solve(source.ravel()).reshape(source.shape)
    field = linear.copy()
    relative_update = 0.0
    iterations = 0

    for iteration in range(1, config.picard_max_iterations + 1):
        star = factor.solve(
            (
                source
                - annulus.cubic_coefficient
                * nonlinear_invariant(field, annulus)
            ).ravel()
        ).reshape(source.shape)
        new_field = (
            (1.0 - config.picard_mixing) * field
            + config.picard_mixing * star
        )
        relative_update = float(
            np.linalg.norm((new_field - field).ravel())
            / max(
                float(np.linalg.norm(new_field.ravel())),
                np.finfo(float).tiny,
            )
        )
        if not np.all(np.isfinite(new_field)):
            raise RuntimeError("Picard reference left the finite branch")
        field = new_field
        iterations = iteration
        if relative_update < config.picard_update_tolerance:
            break

    residual = _e023_residual(field, source, annulus, laplacian)
    source_l2 = max(float(np.linalg.norm(source.ravel())), np.finfo(float).tiny)
    source_linf = max(float(np.max(np.abs(source))), np.finfo(float).tiny)
    volume = cell_volume_weights_dimensionless(annulus)
    volume_source = max(
        float(np.sqrt(np.sum(volume * source**2))), np.finfo(float).tiny
    )
    hessian = orthonormal_hessian_components(field, annulus)
    spatial, time = principal_coefficients_from_hessian(
        *hessian, annulus.cubic_coefficient
    )
    relative_residual = float(np.linalg.norm(residual.ravel()) / source_l2)
    converged = (
        relative_update < config.picard_update_tolerance
        and relative_residual < config.picard_residual_tolerance
        and float(np.min(spatial)) > 0.0
        and float(np.min(time)) > 0.0
    )
    return PicardResult(
        field=field,
        linear_field=linear,
        iterations=iterations,
        converged=converged,
        relative_update=relative_update,
        relative_residual_l2=relative_residual,
        relative_residual_volume_l2=float(
            np.sqrt(np.sum(volume * residual**2)) / volume_source
        ),
        relative_residual_linf=float(np.max(np.abs(residual)) / source_linf),
        minimum_spatial_principal=float(np.min(spatial)),
        minimum_time_kinetic=float(np.min(time)),
    )


def white_normal_root_residual(
    field: np.ndarray,
    source: np.ndarray,
    annulus: AnnulusConfig,
) -> np.ndarray:
    """Evaluate White et al.'s attractive algebraic-root residual."""

    c3 = annulus.cubic_coefficient
    if c3 <= 0.0:
        raise ValueError("White normal-root residual requires c3 > 0")
    h_rr, h_rtheta, h_thetatheta, h_phiphi = orthonormal_hessian_components(
        field, annulus
    )
    trace = h_rr + h_thetatheta + h_phiphi
    norm_squared = (
        h_rr**2
        + h_thetatheta**2
        + h_phiphi**2
        + 2.0 * h_rtheta**2
    )
    return (
        np.sqrt(np.maximum(norm_squared + source / c3 + 1.0 / (4.0 * c3**2), 0.0))
        - trace
        - 1.0 / (2.0 * c3)
    )


def _solution_for_ray(
    config: AnnulusConfig,
    source: np.ndarray,
    linear: np.ndarray,
    field: np.ndarray,
) -> AnnulusSolution:
    radial, angular = cell_centres(config)
    hessian = orthonormal_hessian_components(field, config)
    spatial, time = principal_coefficients_from_hessian(
        *hessian, config.cubic_coefficient
    )
    minimum_index = np.unravel_index(int(np.argmin(spatial)), spatial.shape)
    return AnnulusSolution(
        config=config,
        radial_centres=radial,
        angular_centres=angular,
        source=source,
        linear_field=linear,
        nonlinear_field=field,
        iterations=0,
        converged=True,
        relative_update=0.0,
        relative_residual_l2=0.0,
        relative_residual_volume_l2=0.0,
        relative_residual_linf=0.0,
        minimum_spatial_principal_eigenvalue=float(np.min(spatial)),
        minimum_spatial_principal_radius=float(radial[minimum_index[0]]),
        minimum_spatial_principal_theta=float(angular[minimum_index[1]]),
        minimum_time_kinetic_coefficient=float(np.min(time)),
    )


def run_validation(config: ValidationConfig) -> dict[str, Any]:
    """Run both formulations and return a JSON-safe validation certificate."""

    config.validate()
    annulus = config.annulus
    source_info = smooth_mass_preserving_source(config)
    source = source_info.values
    picard = solve_picard_reference(config, source)

    shifted_grid = ShiftedGrid(
        radial_cells=annulus.radial_cells,
        angular_cells=annulus.angular_cells,
        radial_max=annulus.radial_max,
        radial_mapping_alpha=annulus.radial_mapping_alpha,
    )
    shifted = solve_shifted_continuation(
        shifted_grid,
        source,
        cubic_coefficient=annulus.cubic_coefficient,
        continuation_steps=config.continuation_steps,
        relative_tolerance=config.shifted_relative_tolerance,
        newton_max_iterations=config.shifted_newton_max_iterations,
        gmres_relative_tolerance=config.shifted_gmres_relative_tolerance,
        gmres_max_iterations=config.shifted_gmres_max_iterations,
    )

    radial, _ = cell_centres(annulus)
    _, shifted_radial, _, _, _, _ = shifted_grid_coordinates(shifted_grid)
    grid_disagreement = float(np.max(np.abs(radial - shifted_radial)))
    volume = cell_volume_weights_dimensionless(annulus)
    shifted_volume = shifted_cell_volume_weights(shifted_grid)
    volume_disagreement = float(np.max(np.abs(volume - shifted_volume)))
    field_difference = picard.field - shifted.field
    field_relative_difference = float(
        np.sqrt(np.sum(volume * field_difference**2))
        / max(
            float(np.sqrt(np.sum(volume * shifted.field**2))),
            np.finfo(float).tiny,
        )
    )

    picard_grad_r, picard_grad_theta, _ = e023_gradient_components(
        picard.field, annulus
    )
    shifted_grad_r, shifted_grad_theta = shifted_gradient_components(
        shifted.field, shifted_grid
    )
    gradient_difference = np.hypot(
        picard_grad_r - shifted_grad_r,
        picard_grad_theta - shifted_grad_theta,
    )
    shifted_gradient = np.hypot(shifted_grad_r, shifted_grad_theta)
    gradient_relative_difference = float(
        np.sqrt(np.sum(volume * gradient_difference**2))
        / max(
            float(np.sqrt(np.sum(volume * shifted_gradient**2))),
            np.finfo(float).tiny,
        )
    )

    laplacian = build_spherical_laplacian(annulus)
    original_on_shifted = _e023_residual(
        shifted.field, source, annulus, laplacian
    )
    independent_shifted = shifted_residual(
        shifted.field, source, shifted_grid, annulus.cubic_coefficient
    )
    residual_identity_error = float(
        np.max(
            np.abs(
                original_on_shifted
                - 2.0 * annulus.cubic_coefficient * independent_shifted
            )
        )
        / max(float(np.max(np.abs(source))), np.finfo(float).tiny)
    )
    shifted_native_original = shifted_original_residual(
        shifted.field, source, shifted_grid, annulus.cubic_coefficient
    )
    cross_original_error = float(
        np.linalg.norm((original_on_shifted - shifted_native_original).ravel())
        / max(float(np.linalg.norm(source.ravel())), np.finfo(float).tiny)
    )

    white_residual = white_normal_root_residual(picard.field, source, annulus)
    white_scale = max(
        float(np.sqrt(np.sum(volume * (source / annulus.cubic_coefficient) ** 2))),
        np.finfo(float).tiny,
    )
    white_relative_volume = float(
        np.sqrt(np.sum(volume * white_residual**2)) / white_scale
    )

    source_integral = float(np.sum(shifted_volume * source))
    outer_smoothed_edge = (
        annulus.outer_radius + config.radial_smoothing_width / 2.0
    )
    gap = annulus.radial_max - outer_smoothed_edge
    flux_radii = [
        outer_smoothed_edge + fraction * gap for fraction in (0.2, 0.4, 0.6)
    ]
    flux_rows: list[dict[str, float]] = []
    for radius in flux_radii:
        original_flux = surface_flux(
            shifted.field,
            shifted_grid,
            annulus.cubic_coefficient,
            radius,
            formulation="original",
        )
        shifted_flux = surface_flux(
            shifted.field,
            shifted_grid,
            annulus.cubic_coefficient,
            radius,
            formulation="shifted",
        )
        flux_rows.append(
            {
                "radius": float(radius),
                "original_flux": original_flux,
                "shifted_flux": shifted_flux,
                "original_relative_error": original_flux / source_integral - 1.0,
                "shifted_relative_error": shifted_flux / source_integral - 1.0,
                "formulation_relative_difference": (
                    shifted_flux - original_flux
                )
                / source_integral,
            }
        )
    maximum_flux_error = max(
        max(
            abs(row["original_relative_error"]),
            abs(row["shifted_relative_error"]),
        )
        for row in flux_rows
    )

    ray_maximum = min(annulus.outer_radius, 0.95 * annulus.radial_max)
    picard_ray = sample_ray(
        _solution_for_ray(
            annulus, source, picard.linear_field, picard.field
        ),
        maximum_radius=ray_maximum,
    )
    shifted_ray = sample_ray(
        _solution_for_ray(
            annulus, source, picard.linear_field, shifted.field
        ),
        maximum_radius=ray_maximum,
    )
    shifted_spatial, shifted_pair, shifted_time, shifted_sigma2 = (
        shifted_branch_diagnostics(
            shifted.field, shifted_grid, annulus.cubic_coefficient
        )
    )
    shifted_principal_details = shifted_branch_diagnostic_details(
        shifted.field, shifted_grid, annulus.cubic_coefficient
    )

    cells_per_width = min(
        source_info.radial_inner_cells_per_width,
        source_info.radial_outer_cells_per_width,
        source_info.angular_cells_per_width,
    )
    resolution_gate = cells_per_width >= 6.0
    solver_gate = (
        picard.converged
        and shifted.relative_original_residual_l2
        < config.picard_residual_tolerance
        and shifted_spatial > 0.0
        and shifted_time > 0.0
        and shifted_sigma2 > 0.0
    )
    comparison_gate = (
        field_relative_difference < 2.0e-3
        and gradient_relative_difference < 2.0e-3
        and residual_identity_error < 5.0e-8
        and cross_original_error < 5.0e-8
    )
    flux_gate = maximum_flux_error < 0.02

    return {
        "epistemic_status": (
            "hypothetical cubic-Galileon numerical validation; not a detected "
            "field, artificial-gravity device, FTL result, or reactionless drive"
        ),
        "focus_question": (
            "Does dilute annular anti-screening survive mass-preserving smoothing, "
            "normal-branch continuation, a separately coded shifted-2-Hessian "
            "solve, and divergence-flux checks?"
        ),
        "configuration": {
            "radial_cells": annulus.radial_cells,
            "angular_cells": annulus.angular_cells,
            "radial_max": annulus.radial_max,
            "radial_mapping_alpha": annulus.radial_mapping_alpha,
            "inner_radius": annulus.inner_radius,
            "outer_radius": annulus.outer_radius,
            "half_opening_angle": annulus.half_opening_angle,
            "mu": annulus.mu,
            "cubic_coefficient": annulus.cubic_coefficient,
            "radial_smoothing_width": config.radial_smoothing_width,
            "angular_smoothing_width": config.angular_smoothing_width,
            "continuation_steps": config.continuation_steps,
        },
        "smooth_source": {
            "mass_preserving": True,
            "nominal_volume": source_info.nominal_volume,
            "unnormalized_smoothed_volume": source_info.unnormalized_volume,
            "normalization": source_info.normalization,
            "maximum_normalized_shape": source_info.maximum_normalized_shape,
            "integrated_source": source_integral,
            "radial_inner_transition_cells": (
                source_info.radial_inner_transition_cells
            ),
            "radial_outer_transition_cells": (
                source_info.radial_outer_transition_cells
            ),
            "angular_transition_cells": source_info.angular_transition_cells,
            "radial_inner_cells_per_width": (
                source_info.radial_inner_cells_per_width
            ),
            "radial_outer_cells_per_width": (
                source_info.radial_outer_cells_per_width
            ),
            "angular_cells_per_width": source_info.angular_cells_per_width,
            "minimum_cells_per_width": cells_per_width,
            "six_cell_resolution_gate": resolution_gate,
        },
        "picard_reference": {
            "converged": picard.converged,
            "iterations": picard.iterations,
            "relative_update": picard.relative_update,
            "relative_residual_l2": picard.relative_residual_l2,
            "relative_residual_volume_l2": picard.relative_residual_volume_l2,
            "relative_residual_linf": picard.relative_residual_linf,
            "white_root_relative_volume_l2": white_relative_volume,
            "minimum_spatial_principal": picard.minimum_spatial_principal,
            "minimum_time_kinetic": picard.minimum_time_kinetic,
        },
        "shifted_continuation": {
            "stages": [stage.__dict__ for stage in shifted.stages],
            "relative_shifted_residual_l2": (
                shifted.relative_shifted_residual_l2
            ),
            "relative_original_residual_l2": (
                shifted.relative_original_residual_l2
            ),
            "relative_original_residual_linf": (
                shifted.relative_original_residual_linf
            ),
            "minimum_spatial_principal": shifted_spatial,
            "minimum_shifted_pair_sum": shifted_pair,
            "minimum_time_kinetic": shifted_time,
            "minimum_sigma2": shifted_sigma2,
            "principal_minimum_location": shifted_principal_details,
        },
        "formulation_comparison": {
            "independently_coded_derivatives": True,
            "same_grid_family": True,
            "wide_stencil_monotone_crosscheck_completed": False,
            "grid_coordinate_max_abs_disagreement": grid_disagreement,
            "cell_volume_max_abs_disagreement": volume_disagreement,
            "volume_weighted_field_relative_difference": field_relative_difference,
            "volume_weighted_gradient_relative_difference": (
                gradient_relative_difference
            ),
            "scaled_residual_identity_relative_linf": residual_identity_error,
            "cross_original_residual_relative_l2": cross_original_error,
        },
        "flux_closure": {
            "source_integral": source_integral,
            "shells": flux_rows,
            "maximum_absolute_relative_error": maximum_flux_error,
        },
        "dimensionless_ray": {
            "theta_rad": picard_ray["theta_rad"],
            "centre_ratio": None,
            "picard_ratio_at_r_equals_1": picard_ray["ratio_at_r_equals_1"],
            "shifted_ratio_at_r_equals_1": shifted_ray["ratio_at_r_equals_1"],
            "picard_peak_absolute_gradient": (
                picard_ray["peak_absolute_nonlinear_gradient"]
            ),
            "shifted_peak_absolute_gradient": (
                shifted_ray["peak_absolute_nonlinear_gradient"]
            ),
            "picard_anti_screened_interval": (
                picard_ray["anti_screened_radial_interval"]
            ),
            "shifted_anti_screened_interval": (
                shifted_ray["anti_screened_radial_interval"]
            ),
        },
        "gates": {
            "solver_and_admissibility": solver_gate,
            "formulation_agreement": comparison_gate,
            "flux_within_two_percent": flux_gate,
            "source_transition_resolved_by_six_cells": resolution_gate,
            "provisional_same_grid_validation": (
                solver_gate and comparison_gate and flux_gate and resolution_gate
            ),
            "final_independent_discretization_validation": False,
        },
        "limitations": [
            "The field equation and coupling are hypothetical and undetected.",
            "The two solvers are independently coded but use the same mapped-grid family.",
            "A provably convergent wide-stencil 2-Hessian discretization is not yet implemented.",
            "No material-density, asymmetric, target-backreaction, EFT, or UV-completion claim is made.",
            "The exact symmetric centre force remains zero; internal target force has source/support reaction.",
        ],
    }


def _format_report(report: dict[str, Any]) -> str:
    source = report["smooth_source"]
    picard = report["picard_reference"]
    shifted = report["shifted_continuation"]
    compare = report["formulation_comparison"]
    flux = report["flux_closure"]
    ray = report["dimensionless_ray"]
    gates = report["gates"]
    return "\n".join(
        [
            "E-024 smooth annulus / shifted-2-Hessian validation",
            (
                "transition cells (inner, outer, angular): "
                f"{source['radial_inner_transition_cells']}, "
                f"{source['radial_outer_transition_cells']}, "
                f"{source['angular_transition_cells']}"
            ),
            (
                "minimum local cells per transition width: "
                f"{source['minimum_cells_per_width']:.3f}"
            ),
            (
                "Picard residual/min spatial: "
                f"{picard['relative_residual_l2']:.3e}, "
                f"{picard['minimum_spatial_principal']:.6g}"
            ),
            (
                "shifted residual/min spatial: "
                f"{shifted['relative_original_residual_l2']:.3e}, "
                f"{shifted['minimum_spatial_principal']:.6g}"
            ),
            (
                "principal minimum (r, theta) / boundary-excluded: "
                f"({shifted['principal_minimum_location']['radius']:.6g}, "
                f"{shifted['principal_minimum_location']['theta']:.6g}) / "
                f"{shifted['principal_minimum_location']['one_cell_boundary_excluded_minimum']:.6g}"
            ),
            (
                "field/gradient formulation differences: "
                f"{compare['volume_weighted_field_relative_difference']:.3e}, "
                f"{compare['volume_weighted_gradient_relative_difference']:.3e}"
            ),
            f"maximum shell-flux error: {flux['maximum_absolute_relative_error']:.3e}",
            (
                "ratio at r=1 (Picard / shifted): "
                f"{ray['picard_ratio_at_r_equals_1']:.6g} / "
                f"{ray['shifted_ratio_at_r_equals_1']:.6g}"
            ),
            (
                "provisional same-grid validation: "
                f"{gates['provisional_same_grid_validation']}"
            ),
            "final independent-discretization validation: False",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radial-cells", type=int, default=80)
    parser.add_argument("--angular-cells", type=int, default=40)
    parser.add_argument("--radial-max", type=float, default=80.0)
    parser.add_argument("--radial-mapping-alpha", type=float, default=0.2)
    parser.add_argument("--inner-radius", type=float, default=8.0)
    parser.add_argument("--outer-radius", type=float, default=30.0)
    parser.add_argument("--half-opening-angle", type=float, default=0.05)
    parser.add_argument("--mu", type=float, default=36.8)
    parser.add_argument("--c3", type=float, default=1.0)
    parser.add_argument("--radial-smoothing-width", type=float, default=2.0)
    parser.add_argument("--angular-smoothing-width", type=float, default=0.08)
    parser.add_argument("--continuation-steps", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    annulus = AnnulusConfig(
        radial_cells=args.radial_cells,
        angular_cells=args.angular_cells,
        radial_max=args.radial_max,
        radial_mapping_alpha=args.radial_mapping_alpha,
        inner_radius=args.inner_radius,
        outer_radius=args.outer_radius,
        half_opening_angle=args.half_opening_angle,
        mu=args.mu,
        cubic_coefficient=args.c3,
    )
    config = ValidationConfig(
        annulus=annulus,
        radial_smoothing_width=args.radial_smoothing_width,
        angular_smoothing_width=args.angular_smoothing_width,
        continuation_steps=args.continuation_steps,
    )
    report = run_validation(config)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_format_report(report))


if __name__ == "__main__":
    main()

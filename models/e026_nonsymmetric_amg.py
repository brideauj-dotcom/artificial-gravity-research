#!/usr/bin/env python3
"""E-026 nonsymmetric AMG benchmark for the saved E-025 corrector.

This module reconstructs the exact accepted ``11/12`` E-025 state, assembles
the active semismooth Jacobian, sign-normalizes it to ``A=-J``, and applies a
fixed algebraic-multigrid V-cycle inside ordinary GMRES.  The hierarchy is
rebuilt between Newton steps but remains fixed during each Krylov solve.

The calculation validates one numerical solution of a hypothetical cubic-
Galileon PDE.  It is not evidence for a new field, useful artificial gravity,
inertial control, FTL travel, or reactionless propulsion.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import asdict, dataclass
import hashlib
import json
import math
import platform
from pathlib import Path
import time
from typing import Any, Iterator, Literal

import numpy as np
import pyamg
import scipy
from scipy import sparse
from scipy.sparse import linalg as sparse_linalg

from models.e025_axisymmetric_wide_2hessian import (
    AxisymmetricGrid,
    ContinuationStage,
    WideSolution,
    active_jacobian_matrix,
    annulus_diagnostics,
    build_system,
    fixed_coordinate_hessian_components,
    interpolated_cylindrical_derivatives,
    load_continuation_checkpoint,
    monotone_operator,
    monotone_sigma_gradient,
    scheme_diagnostics,
    shifted_rhs,
    smooth_annulus_source,
    solve_linear_reference,
)


PreconditionerKind = Literal["air", "pgsa"]
NearNullCandidate = Literal[
    "boundary_vanishing_quadratic",
    "constant",
    "rho_weighted_boundary_vanishing_quadratic",
]
DEFAULT_CHECKPOINT = (
    Path(__file__).resolve().parent
    / "checkpoints"
    / "e025_h025_m3_11of12.npz"
)
DEFAULT_OUTPUT_ARTIFACT = (
    Path(__file__).resolve().parent
    / "checkpoints"
    / "e026_h025_m3_full_source_pgsa.npz"
)
EXPECTED_INPUT_SHA256 = (
    "63306017e50599aa6f04c8f32edbe102c640b0f991ce4be937da54112346ac94"
)


@dataclass(frozen=True)
class AmgConfiguration:
    """One fixed hierarchy and Krylov configuration."""

    kind: PreconditionerKind = "pgsa"
    cycle: str = "V"
    gmres_relative_tolerance: float = 1.0e-8
    gmres_restart: int = 50
    gmres_max_restart_cycles: int = 40
    max_levels: int = 20
    max_coarse: int = 50
    random_seed: int = 260719
    right_near_null_candidate: NearNullCandidate = "boundary_vanishing_quadratic"
    left_near_null_candidate: NearNullCandidate = "boundary_vanishing_quadratic"

    def validate(self) -> None:
        if self.kind not in {"air", "pgsa"}:
            raise ValueError("AMG kind must be 'air' or 'pgsa'")
        if self.cycle not in {"V", "W", "F"}:
            raise ValueError("unsupported AMG cycle")
        if self.gmres_relative_tolerance <= 0.0:
            raise ValueError("GMRES tolerance must be positive")
        if self.gmres_restart < 1 or self.gmres_max_restart_cycles < 1:
            raise ValueError("GMRES iteration limits must be positive")
        if self.max_levels < 2 or self.max_coarse < 1:
            raise ValueError("AMG hierarchy limits are invalid")
        if not 0 <= self.random_seed <= np.iinfo(np.uint32).max:
            raise ValueError("random_seed must fit an unsigned 32-bit integer")
        allowed_candidates = {
            "boundary_vanishing_quadratic",
            "constant",
            "rho_weighted_boundary_vanishing_quadratic",
        }
        if self.right_near_null_candidate not in allowed_candidates:
            raise ValueError("unsupported right near-null candidate")
        if self.left_near_null_candidate not in allowed_candidates:
            raise ValueError("unsupported left near-null candidate")


@dataclass(frozen=True)
class ExactCorrectorState:
    """Reconstructed saved field and exact full-source linearization."""

    system: Any
    source: np.ndarray
    source_metadata: dict[str, float]
    field: np.ndarray
    residual: np.ndarray
    jacobian: sparse.csr_matrix
    checkpoint_sha256: str
    completed_amplitude: float
    target_amplitude: float


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_array(values: np.ndarray) -> str:
    array = np.ascontiguousarray(np.asarray(values, dtype=np.float64))
    return hashlib.sha256(array.view(np.uint8)).hexdigest()


def _canonical_json(values: Any) -> str:
    return json.dumps(
        values,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _sha256_json(values: Any) -> str:
    return hashlib.sha256(_canonical_json(values).encode("utf-8")).hexdigest()


@contextmanager
def _isolated_numpy_random_seed(seed: int) -> Iterator[None]:
    """Make PyAMG setup deterministic without changing the caller's RNG state."""

    state = np.random.get_state()
    np.random.seed(seed)
    try:
        yield
    finally:
        np.random.set_state(state)


def runtime_provenance() -> dict[str, str]:
    """Return the numerical runtime versions needed to interpret an artifact."""

    return {
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "pyamg": pyamg.__version__,
    }


def implementation_provenance() -> dict[str, Any]:
    """Fingerprint the implementation that generated a campaign report."""

    return {
        "module": str(Path(__file__).resolve()),
        "module_sha256": _sha256_file(Path(__file__).resolve()),
        "input_checkpoint_format": 2,
        "campaign_artifact_format": 2,
    }


def effective_hierarchy_configuration(
    configuration: AmgConfiguration,
) -> dict[str, Any]:
    """Expand every hierarchy option that affects a recorded solve."""

    configuration.validate()
    common = {
        "kind": configuration.kind,
        "cycle": configuration.cycle,
        "max_levels": configuration.max_levels,
        "random_seed": configuration.random_seed,
        "matrix_sign_normalization": "A=-J",
    }
    if configuration.kind == "air":
        return {
            **common,
            "strength": ["classical", {"theta": 0.3, "norm": "min"}],
            "cf_splitting": ["RS", {"second_pass": True}],
            "interpolation": "one_point",
            "restriction": ["air", {"degree": 2, "theta": 0.05}],
            "presmoother": None,
            "postsmoother": [
                "fc_jacobi",
                {
                    "omega": 1.0,
                    "iterations": 1,
                    "withrho": False,
                    "f_iterations": 2,
                    "c_iterations": 1,
                },
            ],
            "max_coarse": min(configuration.max_coarse, 20),
        }
    return {
        **common,
        "symmetry": "nonsymmetric",
        "right_near_null_candidate": configuration.right_near_null_candidate,
        "left_near_null_candidate": configuration.left_near_null_candidate,
        "candidate_normalization": "none",
        "strength": ["symmetric", {"theta": 0.0}],
        "aggregate": "standard",
        "prolongation_smoother": ["jacobi", {"omega": 4.0 / 3.0}],
        "presmoother": ["block_gauss_seidel", {"sweep": "symmetric"}],
        "postsmoother": ["block_gauss_seidel", {"sweep": "symmetric"}],
        "improve_candidates": [
            [
                "block_gauss_seidel",
                {"iterations": 4, "sweep": "symmetric"},
            ],
            None,
        ],
        "max_coarse": configuration.max_coarse,
    }


def configuration_provenance(configuration: AmgConfiguration) -> dict[str, Any]:
    return {
        "requested": asdict(configuration),
        "effective_hierarchy": effective_hierarchy_configuration(configuration),
    }


def _near_null_candidate(system: Any, name: NearNullCandidate) -> np.ndarray:
    radius = np.hypot(system.rho, system.z)
    quadratic = 1.0 - (radius / system.grid.radial_max) ** 2
    if name == "constant":
        values = np.ones_like(radius)
    elif name == "boundary_vanishing_quadratic":
        values = quadratic
    elif name == "rho_weighted_boundary_vanishing_quadratic":
        values = system.rho * quadratic
    else:  # Defensive guard for callers that bypass configuration validation.
        raise ValueError(f"unsupported near-null candidate {name!r}")
    return values[:, None]


def reconstruct_exact_corrector(
    checkpoint_path: str | Path = DEFAULT_CHECKPOINT,
) -> ExactCorrectorState:
    """Load and independently reconstruct the exact E-026 linear corrector."""

    path = Path(checkpoint_path)
    checkpoint_sha256 = _sha256_file(path)
    if path.resolve() == DEFAULT_CHECKPOINT.resolve():
        if checkpoint_sha256 != EXPECTED_INPUT_SHA256:
            raise ValueError("canonical E-025 checkpoint SHA-256 does not match")

    # Keep 80.0 as a float: the v2 checkpoint fingerprints serialized grid
    # metadata as well as the discrete matrices and boundary offsets.
    system = build_system(AxisymmetricGrid(80.0, 0.25, 3))
    source, source_metadata = smooth_annulus_source(system)
    checkpoint = load_continuation_checkpoint(
        path,
        system,
        source,
        continuation_steps=12,
        relative_tolerance=1.0e-7,
        newton_max_iterations=20,
        gmres_relative_tolerance=1.0e-8,
        gmres_max_iterations=40,
    )
    if not math.isclose(
        checkpoint.completed_amplitude, 11.0 / 12.0, rel_tol=0.0, abs_tol=1.0e-14
    ):
        raise ValueError("checkpoint is not the accepted 11/12 state")
    if checkpoint.stage_complete or not math.isclose(
        checkpoint.target_amplitude, 1.0, rel_tol=0.0, abs_tol=1.0e-14
    ):
        raise ValueError("checkpoint is not pending the full-source target")
    if any(
        (
            checkpoint.current_newton_iterations,
            checkpoint.current_gmres_iterations,
            checkpoint.current_preconditioner_setups,
        )
    ):
        raise ValueError("checkpoint contains pending accepted-stage work")

    operator, active, curvatures = monotone_operator(system, checkpoint.field)
    nodes = np.arange(system.size)
    active_gradient = monotone_sigma_gradient(curvatures[active, nodes])
    jacobian = active_jacobian_matrix(system, active, active_gradient)
    residual = operator - shifted_rhs(source, system.cubic_coefficient)
    return ExactCorrectorState(
        system=system,
        source=source,
        source_metadata=source_metadata,
        field=checkpoint.field.copy(),
        residual=residual,
        jacobian=jacobian,
        checkpoint_sha256=checkpoint_sha256,
        completed_amplitude=checkpoint.completed_amplitude,
        target_amplitude=checkpoint.target_amplitude,
    )


def matrix_diagnostics(
    matrix: sparse.spmatrix,
    *,
    rho: np.ndarray | None = None,
    z: np.ndarray | None = None,
    radial_max: float | None = None,
) -> dict[str, Any]:
    """Report sign, asymmetry, dominance, row-sum, and smooth-mode checks."""

    jacobian = sparse.csr_matrix(matrix)
    diagonal = jacobian.diagonal()
    off_diagonal = jacobian.copy()
    off_diagonal.setdiag(0.0)
    off_diagonal.eliminate_zeros()
    frobenius = float(np.linalg.norm(jacobian.data))
    difference = jacobian - jacobian.T
    asymmetry = float(np.linalg.norm(difference.data) / frobenius)

    normalized = -jacobian
    normalized_diagonal = normalized.diagonal()
    normalized_off = normalized.copy()
    normalized_off.setdiag(0.0)
    normalized_off.eliminate_zeros()
    row_sums = np.asarray(normalized.sum(axis=1)).ravel()
    absolute_row_sums = np.asarray(abs(normalized).sum(axis=1)).ravel()
    off_absolute = absolute_row_sums - np.abs(normalized_diagonal)
    dominance_margin = np.abs(normalized_diagonal) - off_absolute
    tolerance = 1.0e-12 * max(float(np.max(np.abs(normalized_diagonal))), 1.0)

    mode_rows: dict[str, float] = {}
    if rho is not None and z is not None and radial_max is not None:
        if rho.shape != (jacobian.shape[0],) or z.shape != rho.shape:
            raise ValueError("coordinate arrays do not match the matrix")
        radius = np.hypot(rho, z)
        modes = {
            "constant": np.ones_like(radius),
            "boundary_vanishing_quadratic": 1.0 - (radius / radial_max) ** 2,
        }
        for name, mode in modes.items():
            norm = float(np.linalg.norm(mode))
            mode_rows[name] = float(np.linalg.norm(jacobian @ mode) / norm)

    return {
        "shape": list(jacobian.shape),
        "nonzeros": int(jacobian.nnz),
        "frobenius_asymmetry_ratio": asymmetry,
        "jacobian_negative_diagonal_count": int(np.count_nonzero(diagonal < 0.0)),
        "jacobian_positive_off_diagonal_count": int(
            np.count_nonzero(off_diagonal.data > 0.0)
        ),
        "sign_normalized_positive_diagonal_count": int(
            np.count_nonzero(normalized_diagonal > 0.0)
        ),
        "sign_normalized_negative_off_diagonal_count": int(
            np.count_nonzero(normalized_off.data < 0.0)
        ),
        "weakly_diagonally_dominant_rows": int(
            np.count_nonzero(dominance_margin >= -tolerance)
        ),
        "strictly_diagonally_dominant_rows": int(
            np.count_nonzero(dominance_margin > tolerance)
        ),
        "near_zero_row_sum_rows": int(np.count_nonzero(np.abs(row_sums) <= tolerance)),
        "row_sum_minimum": float(np.min(row_sums)),
        "row_sum_maximum": float(np.max(row_sums)),
        "smooth_mode_action_norms": mode_rows,
    }


def _require_m_matrix_sign_pattern(matrix: sparse.csr_matrix) -> None:
    diagonal = matrix.diagonal()
    off_diagonal = matrix.copy()
    off_diagonal.setdiag(0.0)
    off_diagonal.eliminate_zeros()
    scale = max(float(np.max(np.abs(matrix.data))), 1.0)
    tolerance = 1.0e-13 * scale
    if np.any(diagonal <= 0.0) or np.any(off_diagonal.data > tolerance):
        raise ValueError("sign-normalized active Jacobian is not M-matrix-like")


def build_fixed_hierarchy(
    positive_matrix: sparse.csr_matrix,
    system: Any,
    configuration: AmgConfiguration,
) -> Any:
    """Build one hierarchy that remains fixed throughout a GMRES call."""

    configuration.validate()
    matrix = sparse.csr_matrix(positive_matrix)
    _require_m_matrix_sign_pattern(matrix)
    with _isolated_numpy_random_seed(configuration.random_seed):
        if configuration.kind == "air":
            return pyamg.air_solver(
                matrix,
                strength=("classical", {"theta": 0.3, "norm": "min"}),
                CF=("RS", {"second_pass": True}),
                interpolation="one_point",
                restrict=("air", {"degree": 2, "theta": 0.05}),
                presmoother=None,
                postsmoother=(
                    "fc_jacobi",
                    {
                        "omega": 1.0,
                        "iterations": 1,
                        "withrho": False,
                        "f_iterations": 2,
                        "c_iterations": 1,
                    },
                ),
                max_levels=configuration.max_levels,
                max_coarse=min(configuration.max_coarse, 20),
                keep=True,
            )

        right_candidate = _near_null_candidate(
            system, configuration.right_near_null_candidate
        )
        left_candidate = _near_null_candidate(
            system, configuration.left_near_null_candidate
        )
        return pyamg.smoothed_aggregation_solver(
            matrix,
            B=right_candidate,
            BH=left_candidate,
            symmetry="nonsymmetric",
            strength=("symmetric", {"theta": 0.0}),
            aggregate="standard",
            smooth=("jacobi", {"omega": 4.0 / 3.0}),
            presmoother=("block_gauss_seidel", {"sweep": "symmetric"}),
            postsmoother=("block_gauss_seidel", {"sweep": "symmetric"}),
            improve_candidates=(
                (
                    "block_gauss_seidel",
                    {"iterations": 4, "sweep": "symmetric"},
                ),
                None,
            ),
            max_levels=configuration.max_levels,
            max_coarse=configuration.max_coarse,
            keep=True,
        )


def hierarchy_diagnostics(hierarchy: Any) -> dict[str, Any]:
    level_operator_nonzeros = [int(level.A.nnz) for level in hierarchy.levels]
    level_sizes = [int(level.A.shape[0]) for level in hierarchy.levels]
    prolongation_nonzeros = [
        int(getattr(level, "P").nnz) if hasattr(level, "P") else 0
        for level in hierarchy.levels
    ]
    restriction_nonzeros = [
        int(getattr(level, "R").nnz) if hasattr(level, "R") else 0
        for level in hierarchy.levels
    ]
    operator_nonzeros = int(sum(level_operator_nonzeros))
    transfer_nonzeros = int(sum(prolongation_nonzeros) + sum(restriction_nonzeros))
    return {
        "levels": len(hierarchy.levels),
        "level_sizes": level_sizes,
        "level_operator_nonzeros": level_operator_nonzeros,
        "operator_nonzeros": operator_nonzeros,
        "level_prolongation_nonzeros": prolongation_nonzeros,
        "level_restriction_nonzeros": restriction_nonzeros,
        "transfer_nonzeros": transfer_nonzeros,
        "stored_sparse_nonzeros": operator_nonzeros + transfer_nonzeros,
        "operator_complexity": float(hierarchy.operator_complexity()),
        "grid_complexity": float(hierarchy.grid_complexity()),
    }


def solve_linear_corrector(
    jacobian: sparse.csr_matrix,
    residual: np.ndarray,
    system: Any,
    configuration: AmgConfiguration,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Solve ``J s=-F`` through ``(-J)s=F`` and audit the true residual."""

    positive_matrix = (-jacobian).tocsr()
    setup_started = time.perf_counter()
    hierarchy = build_fixed_hierarchy(positive_matrix, system, configuration)
    setup_seconds = time.perf_counter() - setup_started
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
    report = {
        "gmres_info": int(info),
        "inner_iterations": len(history),
        "true_linear_residual_ratio": true_ratio,
        "passes_inexact_newton_gate": bool(true_ratio < 1.0),
        "passes_strict_krylov_gate": bool(info == 0),
        "setup_seconds": setup_seconds,
        "solve_seconds": solve_seconds,
        "preconditioned_residual_first": history[0] if history else None,
        "preconditioned_residual_last": history[-1] if history else None,
        "hierarchy": hierarchy_diagnostics(hierarchy),
    }
    return np.asarray(correction, dtype=float), report


def benchmark_saved_corrector(
    state: ExactCorrectorState,
    configuration: AmgConfiguration,
) -> dict[str, Any]:
    """Benchmark exactly one saved full-target linear correction."""

    _, report = solve_linear_corrector(
        state.jacobian, state.residual, state.system, configuration
    )
    stage_scale = max(
        float(np.linalg.norm(state.source))
        / (2.0 * state.system.cubic_coefficient),
        np.finfo(float).tiny,
    )
    return {
        "configuration": configuration_provenance(configuration),
        "full_target_relative_nonlinear_residual": float(
            np.linalg.norm(state.residual) / stage_scale
        ),
        "linear_corrector": report,
    }


def close_full_source(
    state: ExactCorrectorState,
    configuration: AmgConfiguration,
    *,
    nonlinear_relative_tolerance: float = 1.0e-7,
    newton_max_iterations: int = 20,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Attempt the full target while preserving every E-025 acceptance gate."""

    field = state.field.copy()
    stage_scale = max(
        float(np.linalg.norm(state.source))
        / (2.0 * state.system.cubic_coefficient),
        np.finfo(float).tiny,
    )
    history: list[dict[str, Any]] = []
    total_setup_seconds = 0.0
    total_solve_seconds = 0.0
    for newton_iteration in range(1, newton_max_iterations + 1):
        operator, active, curvatures = monotone_operator(state.system, field)
        residual = operator - shifted_rhs(
            state.source, state.system.cubic_coefficient
        )
        relative_before = float(np.linalg.norm(residual) / stage_scale)
        if relative_before < nonlinear_relative_tolerance:
            break
        nodes = np.arange(state.system.size)
        active_gradient = monotone_sigma_gradient(curvatures[active, nodes])
        jacobian = active_jacobian_matrix(
            state.system, active, active_gradient
        )
        correction, linear_report = solve_linear_corrector(
            jacobian, residual, state.system, configuration
        )
        if not linear_report["passes_inexact_newton_gate"]:
            raise RuntimeError("AMG correction failed the true inexact-Newton gate")
        if not linear_report["passes_strict_krylov_gate"]:
            raise RuntimeError("positive GMRES info remains a hard rejection")

        accepted = False
        step = 1.0
        for _ in range(24):
            trial = field + step * correction
            trial_operator, _, trial_curvatures = monotone_operator(
                state.system, trial
            )
            trial_residual = trial_operator - shifted_rhs(
                state.source, state.system.cubic_coefficient
            )
            pair, spatial, time_coefficient = scheme_diagnostics(
                state.system, trial_curvatures
            )
            sufficient_decrease = float(np.linalg.norm(trial_residual)) < (
                np.linalg.norm(residual) * (1.0 - 1.0e-4 * step)
            )
            if (
                sufficient_decrease
                and pair > 0.0
                and spatial > 0.0
                and time_coefficient > 0.0
            ):
                field = trial
                accepted = True
                relative_after = float(np.linalg.norm(trial_residual) / stage_scale)
                break
            step *= 0.5
        if not accepted:
            raise RuntimeError("AMG Newton correction failed the branch-safe line search")

        total_setup_seconds += float(linear_report["setup_seconds"])
        total_solve_seconds += float(linear_report["solve_seconds"])
        history.append(
            {
                "newton_iteration": newton_iteration,
                "relative_residual_before": relative_before,
                "relative_residual_after": relative_after,
                "accepted_step": step,
                "minimum_pair_sum": pair,
                "minimum_spatial_principal": spatial,
                "minimum_time_kinetic": time_coefficient,
                "linear": linear_report,
            }
        )
    final_residual = (
        monotone_operator(state.system, field)[0]
        - shifted_rhs(state.source, state.system.cubic_coefficient)
    )
    relative_l2 = float(np.linalg.norm(final_residual) / stage_scale)
    source_linf_scale = max(
        float(np.max(state.source)) / (2.0 * state.system.cubic_coefficient),
        np.finfo(float).tiny,
    )
    relative_linf = float(np.max(np.abs(final_residual)) / source_linf_scale)
    _, _, final_curvatures = monotone_operator(state.system, field)
    pair, spatial, time_coefficient = scheme_diagnostics(
        state.system, final_curvatures
    )
    if relative_l2 >= nonlinear_relative_tolerance:
        raise RuntimeError(
            "AMG full-source solve exhausted the Newton cap without reaching "
            f"the nonlinear gate; residual={relative_l2:.6e}"
        )
    if pair <= 0.0 or spatial <= 0.0 or time_coefficient <= 0.0:
        raise RuntimeError("AMG full-source solve left the admissible branch")
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


def _spatial_principal_summary(
    system: Any,
    rho: np.ndarray,
    z: np.ndarray,
    radial: np.ndarray,
    mixed: np.ndarray,
    axial: np.ndarray,
    azimuthal: np.ndarray,
) -> dict[str, Any]:
    meridional_gap = np.sqrt((radial - axial) ** 2 + 4.0 * mixed**2)
    eigen_low = 0.5 * (radial + axial - meridional_gap)
    eigen_high = 0.5 * (radial + axial + meridional_gap)
    eigenvalues = np.sort(
        np.stack((eigen_low, eigen_high, azimuthal), axis=-1), axis=-1
    )
    spatial = 1.0 + 2.0 * system.cubic_coefficient * (
        eigenvalues[:, 0] + eigenvalues[:, 1]
    )
    index = int(np.argmin(spatial))
    return {
        "minimum_spatial_principal": float(spatial[index]),
        "nonpositive_node_count": int(np.count_nonzero(spatial <= 0.0)),
        "minimum_rho": float(rho[index]),
        "minimum_z": float(z[index]),
        "minimum_node_eigenvalues": [
            float(value) for value in eigenvalues[index]
        ],
    }


def spatial_principal_crosschecks(
    system: Any,
    field: np.ndarray,
    wide_minimum_spatial_principal: float,
) -> dict[str, Any]:
    """Retain conflicts between the accepted wide gate and separate Hessians."""

    fixed_components = fixed_coordinate_hessian_components(system, field)
    fixed = _spatial_principal_summary(
        system,
        system.rho,
        system.z,
        fixed_components[0],
        fixed_components[1],
        fixed_components[2],
        fixed_components[3],
    )

    spacing = system.grid.spacing
    mask = np.hypot(system.rho, system.z) <= (
        system.grid.radial_max - 3.0 * math.sqrt(2.0) * spacing
    )
    rho = system.rho[mask]
    z = system.z[mask]
    phi_r, _phi_z, radial, mixed, axial = interpolated_cylindrical_derivatives(
        system, field, rho, z
    )
    azimuthal = np.divide(
        phi_r,
        rho,
        out=radial.copy(),
        where=rho > 0.5 * spacing,
    )
    centered = _spatial_principal_summary(
        system, rho, z, radial, mixed, axial, azimuthal
    )
    conflict = (
        fixed["nonpositive_node_count"] > 0
        or centered["nonpositive_node_count"] > 0
    )
    return {
        "wide_stencil_acceptance_gate": {
            "minimum_spatial_principal": float(wide_minimum_spatial_principal),
            "passes": bool(wide_minimum_spatial_principal > 0.0),
        },
        "fixed_coordinate_crosscheck": fixed,
        "independent_centered_crosscheck": {
            **centered,
            "evaluated_nodes": int(np.count_nonzero(mask)),
            "excluded_outer_nodes": int(system.size - np.count_nonzero(mask)),
        },
        "crosscheck_conflicts_with_wide_gate": bool(conflict),
        "interpretation": (
            "The accepted finite-direction wide-stencil gate is positive, but "
            "a nonpositive fixed or centered spatial-principal cross-check is "
            "a retained angular/discretization warning that must be resolved "
            "by joint refinement; it is not silently promoted to branch health."
            if conflict
            else "Wide, fixed-coordinate, and centered spatial-principal checks agree."
        ),
    }


def run_exact_campaign(
    checkpoint_path: str | Path = DEFAULT_CHECKPOINT,
    configuration: AmgConfiguration = AmgConfiguration(),
    *,
    include_annulus_diagnostics: bool = True,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Reconstruct, benchmark, close, and diagnose the exact E-026 target."""

    state = reconstruct_exact_corrector(checkpoint_path)
    matrix_report = matrix_diagnostics(
        state.jacobian,
        rho=state.system.rho,
        z=state.system.z,
        radial_max=state.system.grid.radial_max,
    )
    benchmark = benchmark_saved_corrector(state, configuration)
    field, nonlinear = close_full_source(state, configuration)
    crosschecks = spatial_principal_crosschecks(
        state.system,
        field,
        float(nonlinear["minimum_spatial_principal"]),
    )
    limitations = [
        "This closes one grid and directional level, not a continuum sequence.",
        "The active hierarchy is rebuilt at each Newton step and is not yet shown mesh-independent.",
        "The cylindrical curved-boundary scheme remains outside the cited Cartesian convergence theorem.",
    ]
    if crosschecks["crosscheck_conflicts_with_wide_gate"]:
        limitations.append(
            "The positive finite-direction wide gate conflicts with a nonpositive "
            "fixed/centered spatial-principal value at one node; joint refinement "
            "must resolve this retained admissibility warning."
        )
    report: dict[str, Any] = {
        "epistemic_status": (
            "independent numerical validation of a hypothetical PDE; not a "
            "detected field, useful artificial gravity, inertial control, "
            "FTL result, or propulsion result"
        ),
        "runtime_provenance": runtime_provenance(),
        "implementation_provenance": implementation_provenance(),
        "input_checkpoint": {
            "path": str(Path(checkpoint_path).resolve()),
            "sha256": state.checkpoint_sha256,
            "completed_amplitude": state.completed_amplitude,
            "target_amplitude": state.target_amplitude,
        },
        "matrix": matrix_report,
        "saved_corrector_benchmark": benchmark,
        "full_source": nonlinear,
        "spatial_principal_crosschecks": crosschecks,
        "output_field_sha256": _sha256_array(field),
        "limitations": limitations,
    }
    if include_annulus_diagnostics:
        maximum_operator_nonzeros = max(
            (
                row["linear"]["hierarchy"]["operator_nonzeros"]
                for row in nonlinear["history"]
            ),
            default=0,
        )
        maximum_stored_sparse_nonzeros = max(
            (
                row["linear"]["hierarchy"]["stored_sparse_nonzeros"]
                for row in nonlinear["history"]
            ),
            default=0,
        )
        stage = ContinuationStage(
            amplitude=1.0,
            newton_iterations=int(nonlinear["newton_iterations"]),
            gmres_iterations=int(nonlinear["summed_gmres_inner_iterations"]),
            relative_residual_l2=float(nonlinear["relative_residual_l2"]),
            minimum_pair_sum=float(nonlinear["minimum_pair_sum"]),
            minimum_spatial_principal=float(
                nonlinear["minimum_spatial_principal"]
            ),
            minimum_time_kinetic=float(nonlinear["minimum_time_kinetic"]),
            preconditioner_kind=f"active_{configuration.kind}",
            preconditioner_setups=int(nonlinear["newton_iterations"]),
            preconditioner_setup_seconds=float(nonlinear["summed_setup_seconds"]),
            # PG-SA/AIR have no ILU-style factor. E-026 adds explicit operator
            # and transfer metrics to the packaged diagnostic below.
            preconditioner_factor_nnz_max=0,
        )
        solution = WideSolution(
            system=state.system,
            source=state.source,
            field=field,
            linear_field=solve_linear_reference(state.system, state.source),
            stages=[stage],
            relative_residual_l2=float(nonlinear["relative_residual_l2"]),
            relative_residual_linf=float(nonlinear["relative_residual_linf"]),
            minimum_pair_sum=float(nonlinear["minimum_pair_sum"]),
            minimum_spatial_principal=float(
                nonlinear["minimum_spatial_principal"]
            ),
            minimum_time_kinetic=float(nonlinear["minimum_time_kinetic"]),
        )
        packaged_diagnostics = annulus_diagnostics(
            solution, state.source_metadata
        )
        packaged_solver = packaged_diagnostics["solver"]
        packaged_solver.pop("maximum_preconditioner_factor_nnz", None)
        packaged_solver["maximum_preconditioner_operator_nonzeros"] = int(
            maximum_operator_nonzeros
        )
        packaged_solver["maximum_preconditioner_stored_sparse_nonzeros"] = int(
            maximum_stored_sparse_nonzeros
        )
        for stage_row in packaged_solver["stages"]:
            stage_row.pop("preconditioner_factor_nnz_max", None)
            stage_row["preconditioner_operator_nonzeros_max"] = int(
                maximum_operator_nonzeros
            )
            stage_row["preconditioner_stored_sparse_nonzeros_max"] = int(
                maximum_stored_sparse_nonzeros
            )
        report["annulus_diagnostics"] = packaged_diagnostics
    return field, report


def save_campaign_artifact(
    path: str | Path,
    field: np.ndarray,
    report: dict[str, Any],
) -> None:
    """Save a pickle-free full-source field with complete JSON provenance."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.tmp")
    field_sha256 = _sha256_array(field)
    metadata = {
        "format_version": 2,
        "report": report,
        "report_sha256": _sha256_json(report),
        "field_sha256": field_sha256,
    }
    with temporary.open("wb") as handle:
        np.savez_compressed(
            handle,
            field=np.asarray(field, dtype=np.float64),
            metadata=np.array(_canonical_json(metadata)),
        )
    temporary.replace(destination)


def load_campaign_artifact(path: str | Path) -> tuple[np.ndarray, dict[str, Any]]:
    """Load and verify a pickle-free E-026 campaign artifact."""

    with np.load(Path(path), allow_pickle=False) as payload:
        field = np.asarray(payload["field"], dtype=float)
        metadata = json.loads(str(payload["metadata"].item()))
    if metadata.get("format_version") != 2:
        raise ValueError("unsupported E-026 artifact format")
    if field.ndim != 1 or not np.all(np.isfinite(field)):
        raise ValueError("E-026 artifact field must be a finite vector")
    field_sha256 = _sha256_array(field)
    if field_sha256 != metadata.get("field_sha256"):
        raise ValueError("E-026 artifact field digest does not match")
    report = metadata.get("report")
    if not isinstance(report, dict):
        raise ValueError("E-026 artifact report is missing or invalid")
    if _sha256_json(report) != metadata.get("report_sha256"):
        raise ValueError("E-026 artifact report digest does not match")
    reported_field_sha256 = report.get("output_field_sha256")
    if (
        reported_field_sha256 is not None
        and reported_field_sha256 != field_sha256
    ):
        raise ValueError("E-026 artifact report and field digests disagree")
    return field, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--preconditioner", choices=("air", "pgsa"), default="pgsa")
    parser.add_argument("--linear-only", action="store_true")
    parser.add_argument("--no-annulus-diagnostics", action="store_true")
    parser.add_argument("--output-artifact", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    configuration = AmgConfiguration(kind=args.preconditioner)
    if args.linear_only:
        state = reconstruct_exact_corrector(args.checkpoint)
        report = {
            "epistemic_status": "linear-only E-026 benchmark; not a full-source result",
            "runtime_provenance": runtime_provenance(),
            "implementation_provenance": implementation_provenance(),
            "input_checkpoint": {
                "path": str(Path(args.checkpoint).resolve()),
                "sha256": state.checkpoint_sha256,
                "completed_amplitude": state.completed_amplitude,
                "target_amplitude": state.target_amplitude,
            },
            "matrix": matrix_diagnostics(
                state.jacobian,
                rho=state.system.rho,
                z=state.system.z,
                radial_max=state.system.grid.radial_max,
            ),
            "saved_corrector_benchmark": benchmark_saved_corrector(
                state, configuration
            ),
        }
        field = state.field
        report["output_field_sha256"] = _sha256_array(field)
    else:
        field, report = run_exact_campaign(
            args.checkpoint,
            configuration,
            include_annulus_diagnostics=not args.no_annulus_diagnostics,
        )
    if args.output_artifact is not None:
        save_campaign_artifact(args.output_artifact, field, report)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        benchmark = report["saved_corrector_benchmark"]["linear_corrector"]
        print(
            f"saved corrector: {benchmark['inner_iterations']} GMRES iterations; "
            f"true ratio={benchmark['true_linear_residual_ratio']:.6e}"
        )
        if "full_source" in report:
            full = report["full_source"]
            print(
                f"full source: {full['newton_iterations']} Newton iterations; "
                f"relative L2={full['relative_residual_l2']:.6e}; "
                f"pair/spatial/time={full['minimum_pair_sum']:.6e}/"
                f"{full['minimum_spatial_principal']:.6e}/"
                f"{full['minimum_time_kinetic']:.6e}"
            )


if __name__ == "__main__":
    main()

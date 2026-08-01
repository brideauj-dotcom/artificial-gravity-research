#!/usr/bin/env python3
"""E-034 exact transfer functions for the frozen E-033 postprocessors.

E-033 compared three component postprocessors on one 5 x 5 common-node
patch: centered differences at physical steps 0.25 and 0.5, and one
unweighted total-degree-two least-squares recovery over all 25 nodes.  This
module qualifies those linear operators without loading a checkpoint or
solving a PDE.

For a lattice Fourier mode

    u[i, j] = exp(1j * (i * theta_rho + j * theta_z)),

the code derives and independently evaluates the exact radial, mixed, axial,
and frozen-local azimuthal symbols.  It records analytic null and sign-change
bands, maps predeclared 10-percent and half-amplitude resolution squares, and
constructs distinct lower-band and grid-scale manufactured mode mixtures
that reproduce all twelve rounded E-033 hotspot component measurements.

The ``phi_r / rho`` component has only a frozen-coefficient local symbol at a
declared ``rho0``.  None of this analysis establishes a continuum Hessian, a
Galileon field, artificial gravity, inertial control, spacetime engineering,
faster-than-light travel, or propulsion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from pathlib import Path
import sys
import time
from typing import Any, Callable

import numpy as np

import models.e025_axisymmetric_wide_2hessian as e025
import models.e033_potential_error_stencils as e033


CAMPAIGN = "E-034"
GRID_SPACING = e033.COMMON_NODE_STEP
REFERENCE_RHO = e033.HOTSPOT[0]
COMPONENT_NAMES = e033.COMPONENT_NAMES
POSTPROCESSOR_NAMES = ("centered_0p25", "centered_0p5", "quadratic_5x5")
RESOLUTION_THRESHOLDS = {
    "ten_percent_relative_amplitude": 0.9,
    "half_amplitude": 0.5,
}
ANGLE_ABSOLUTE_TOLERANCE = 2.0e-12
SYMBOL_ABSOLUTE_TOLERANCE = 2.0e-12
MIXTURE_ABSOLUTE_TOLERANCE = 2.0e-12
LOW_WAVE_RELATIVE_TOLERANCE = 2.0e-8

# These are the rounded values published in the 2026-07-31 Daily_Log table.
# They are diagnostic targets, not retained endpoint data or acceptance gates.
E033_ROUNDED_HOTSPOT_TARGETS = {
    "49/96": np.asarray(
        (
            0.028904,
            -0.017571,
            0.440309,
            0.001612,
            0.022047,
            0.002340,
            0.251346,
            0.001510,
            0.007631,
            -0.001174,
            0.215699,
            0.001884,
        ),
        dtype=float,
    ),
    "25/48": np.asarray(
        (
            0.029280,
            -0.017399,
            0.449122,
            0.001592,
            0.022607,
            0.002568,
            0.255821,
            0.001486,
            0.007857,
            -0.000942,
            0.219232,
            0.001869,
        ),
        dtype=float,
    ),
}

# Each tuple is (theta_rho / pi, theta_z / pi, phase / pi).  The banks are
# frozen manufactured dictionaries.  They are intentionally overcomplete:
# each maps with rank 12 to the twelve postprocessor/component measurements.
LOWER_BAND_MODE_BANK = (
    (0.08, 0.12, 0.0),
    (0.12, 0.24, 0.0),
    (0.20, 0.10, 0.0),
    (0.18, 0.30, 0.0),
    (0.28, 0.18, 0.0),
    (0.25, 0.36, 0.0),
    (0.35, 0.12, 0.0),
    (0.38, 0.28, 0.0),
    (0.45, 0.42, 0.0),
    (0.50, 0.20, 0.0),
    (0.42, 0.08, 0.0),
    (0.10, 0.45, 0.0),
    (0.10, 0.08, -0.5),
    (0.20, 0.18, -0.5),
    (0.35, 0.32, -0.5),
    (0.45, 0.12, -0.5),
    (0.28, 0.44, -0.5),
)
GRID_SCALE_MODE_BANK = (
    (0.55, 0.62, 0.0),
    (0.62, 0.78, 0.0),
    (0.70, 0.58, 0.0),
    (0.75, 0.88, 0.0),
    (0.82, 0.66, 0.0),
    (0.90, 0.75, 0.0),
    (0.58, 0.93, 0.0),
    (0.68, 0.84, 0.0),
    (0.95, 0.56, 0.0),
    (0.86, 0.92, 0.0),
    (0.73, 0.69, 0.0),
    (0.60, 0.81, 0.0),
    (0.55, 0.65, -0.5),
    (0.68, 0.82, -0.5),
    (0.78, 0.58, -0.5),
    (0.88, 0.91, -0.5),
    (0.95, 0.72, -0.5),
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def implementation_provenance() -> dict[str, Any]:
    """Fingerprint the analytic campaign and the reused frozen weights."""

    repository_root = Path(__file__).resolve().parents[1]
    paths = {
        "e034_analysis": Path(__file__).resolve(),
        "e033_frozen_postprocessors": Path(e033.__file__).resolve(),
        "e025_directional_basis": Path(e025.__file__).resolve(),
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
        "strategy": {
            "grid_spacing": GRID_SPACING,
            "reference_rho": REFERENCE_RHO,
            "postprocessors": list(POSTPROCESSOR_NAMES),
            "components": list(COMPONENT_NAMES),
            "resolution_thresholds": RESOLUTION_THRESHOLDS,
            "mode_bank_sizes": {
                "lower_band": len(LOWER_BAND_MODE_BANK),
                "grid_scale": len(GRID_SCALE_MODE_BANK),
            },
            "lineage_policy": (
                "No checkpoint is read or written. Accepted lineage remains "
                "the immutable E-028 stage 6/12 checkpoint."
            ),
        },
    }


def runtime_provenance() -> dict[str, Any]:
    """Record the numerical runtime used for SVD and least-squares results."""

    build_dependencies = np.__config__.CONFIG.get("Build Dependencies", {})
    return {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "blas": build_dependencies.get("blas", {}),
        "lapack": build_dependencies.get("lapack", {}),
    }


def _sinc(value: float | np.ndarray) -> float | np.ndarray:
    """Return sin(value) / value with the continuous value at zero."""

    array = np.asarray(value, dtype=float)
    result = np.sinc(array / math.pi)
    if np.ndim(array) == 0:
        return float(result)
    return result


def dirichlet_five(theta: float | np.ndarray) -> float | np.ndarray:
    """Return the five-sample symmetric box symbol D(theta)."""

    values = np.asarray(theta, dtype=float)
    result = 1.0 + 2.0 * np.cos(values) + 2.0 * np.cos(2.0 * values)
    if np.ndim(values) == 0:
        return float(result)
    return result


def curvature_factor(theta: float | np.ndarray) -> float | np.ndarray:
    """Return the quadratic-recovery pure-curvature factor A(theta)."""

    values = np.asarray(theta, dtype=float)
    result = 4.0 * np.cos(2.0 * values) - 2.0 * np.cos(values) - 2.0
    if np.ndim(values) == 0:
        return float(result)
    return result


def first_factor(theta: float | np.ndarray) -> float | np.ndarray:
    """Return the quadratic-recovery first-derivative factor P(theta)."""

    values = np.asarray(theta, dtype=float)
    result = np.sin(values) + 2.0 * np.sin(2.0 * values)
    if np.ndim(values) == 0:
        return float(result)
    return result


def continuum_symbols(
    theta_rho: float,
    theta_z: float,
    *,
    rho0: float = REFERENCE_RHO,
) -> np.ndarray:
    """Return local continuum component symbols for one lattice mode."""

    if rho0 <= 0.0:
        raise ValueError("rho0 must be positive")
    h = GRID_SPACING
    return np.asarray(
        (
            -(theta_rho / h) ** 2,
            -(theta_rho * theta_z) / h**2,
            -(theta_z / h) ** 2,
            1j * theta_rho / (h * rho0),
        ),
        dtype=complex,
    )


def centered_symbols(
    theta_rho: float,
    theta_z: float,
    *,
    stride: int,
    rho0: float = REFERENCE_RHO,
) -> np.ndarray:
    """Return exact symbols of one frozen centered postprocessor."""

    if stride not in (1, 2):
        raise ValueError("E-034 supports only E-033 strides 1 and 2")
    if rho0 <= 0.0:
        raise ValueError("rho0 must be positive")
    h = GRID_SPACING
    scaled_rho = stride * theta_rho
    scaled_z = stride * theta_z
    return np.asarray(
        (
            -4.0 * math.sin(scaled_rho / 2.0) ** 2 / (stride * h) ** 2,
            -math.sin(scaled_rho)
            * math.sin(scaled_z)
            / (stride * h) ** 2,
            -4.0 * math.sin(scaled_z / 2.0) ** 2 / (stride * h) ** 2,
            1j * math.sin(scaled_rho) / (stride * h * rho0),
        ),
        dtype=complex,
    )


def quadratic_symbols(
    theta_rho: float,
    theta_z: float,
    *,
    rho0: float = REFERENCE_RHO,
) -> np.ndarray:
    """Return exact symbols of E-033's fixed 25-node quadratic recovery."""

    if rho0 <= 0.0:
        raise ValueError("rho0 must be positive")
    h = GRID_SPACING
    radial_box = dirichlet_five(theta_rho)
    axial_box = dirichlet_five(theta_z)
    radial_first = first_factor(theta_rho)
    axial_first = first_factor(theta_z)
    return np.asarray(
        (
            curvature_factor(theta_rho) * axial_box / (35.0 * h**2),
            -radial_first * axial_first / (25.0 * h**2),
            radial_box * curvature_factor(theta_z) / (35.0 * h**2),
            1j * radial_first * axial_box / (25.0 * h * rho0),
        ),
        dtype=complex,
    )


def normalized_transfer(
    postprocessor: str,
    component: str,
    theta_rho: float | np.ndarray,
    theta_z: float | np.ndarray,
) -> float | np.ndarray:
    """Return the real discrete/continuum transfer ratio with zero limits."""

    radial = np.asarray(theta_rho, dtype=float)
    axial = np.asarray(theta_z, dtype=float)
    if component not in COMPONENT_NAMES:
        raise ValueError(f"unknown component: {component}")
    if postprocessor == "centered_0p25":
        stride = 1
    elif postprocessor == "centered_0p5":
        stride = 2
    elif postprocessor == "quadratic_5x5":
        stride = 0
    else:
        raise ValueError(f"unknown postprocessor: {postprocessor}")

    if stride:
        if component == "radial":
            result = _sinc(stride * radial / 2.0) ** 2
        elif component == "mixed":
            result = _sinc(stride * radial) * _sinc(stride * axial)
        elif component == "axial":
            result = _sinc(stride * axial / 2.0) ** 2
        else:
            result = _sinc(stride * radial)
    elif component == "radial":
        result = (
            _sinc(radial / 2.0) ** 2
            * (4.0 * np.cos(radial) + 3.0)
            * dirichlet_five(axial)
            / 35.0
        )
    elif component == "mixed":
        result = (
            _sinc(radial)
            * (1.0 + 4.0 * np.cos(radial))
            / 5.0
            * _sinc(axial)
            * (1.0 + 4.0 * np.cos(axial))
            / 5.0
        )
    elif component == "axial":
        result = (
            dirichlet_five(radial)
            * _sinc(axial / 2.0) ** 2
            * (4.0 * np.cos(axial) + 3.0)
            / 35.0
        )
    else:
        result = (
            _sinc(radial)
            * (1.0 + 4.0 * np.cos(radial))
            * dirichlet_five(axial)
            / 25.0
        )
    if np.ndim(result) == 0:
        return float(result)
    return np.asarray(result, dtype=float)


def _component_weights(rho0: float) -> dict[str, np.ndarray]:
    """Recover all twelve exact 5 x 5 weight rows from E-033."""

    impulses = np.eye(25, dtype=float).reshape(25, 5, 5)
    result: dict[str, np.ndarray] = {}
    for name, stride in (("centered_0p25", 1), ("centered_0p5", 2)):
        result[name] = np.stack(
            [
                e033._centered_component_ledgers(
                    impulse,
                    rho0,
                    stride=stride,
                )["components"]
                for impulse in impulses
            ],
            axis=1,
        ).reshape(4, 5, 5)
    result["quadratic_5x5"] = np.stack(
        [
            e033._quadratic_recovery(impulse, rho0)["components"]
            for impulse in impulses
        ],
        axis=1,
    ).reshape(4, 5, 5)
    return result


def _symbols_from_weights(
    weights: np.ndarray,
    theta_rho: float,
    theta_z: float,
) -> np.ndarray:
    offsets = np.arange(-2, 3, dtype=float)
    radial, axial = np.meshgrid(offsets, offsets, indexing="ij")
    mode = np.exp(1j * (radial * theta_rho + axial * theta_z))
    return np.asarray(
        [np.sum(component * mode) for component in weights],
        dtype=complex,
    )


def _closed_symbols(
    postprocessor: str,
    theta_rho: float,
    theta_z: float,
    rho0: float,
) -> np.ndarray:
    if postprocessor == "centered_0p25":
        return centered_symbols(theta_rho, theta_z, stride=1, rho0=rho0)
    if postprocessor == "centered_0p5":
        return centered_symbols(theta_rho, theta_z, stride=2, rho0=rho0)
    if postprocessor == "quadratic_5x5":
        return quadratic_symbols(theta_rho, theta_z, rho0=rho0)
    raise ValueError(f"unknown postprocessor: {postprocessor}")


def exact_symbol_validation() -> dict[str, Any]:
    """Cross-check closed symbols against weights and sampled plane waves."""

    rho0 = REFERENCE_RHO
    weights = _component_weights(rho0)
    angles = (
        (0.0, 0.0),
        (0.07 * math.pi, -0.11 * math.pi),
        (0.31 * math.pi, 0.23 * math.pi),
        (-0.44 * math.pi, 0.37 * math.pi),
        (0.61 * math.pi, -0.72 * math.pi),
        (0.93 * math.pi, 0.87 * math.pi),
        (math.pi, -math.pi),
    )
    maximum_weight_error = 0.0
    maximum_sample_error = 0.0
    offsets = np.arange(-2, 3, dtype=float)
    radial, axial = np.meshgrid(offsets, offsets, indexing="ij")
    for theta_rho, theta_z in angles:
        complex_patch = np.exp(
            1j * (radial * theta_rho + axial * theta_z)
        )
        for name in POSTPROCESSOR_NAMES:
            closed = _closed_symbols(name, theta_rho, theta_z, rho0)
            transformed = _symbols_from_weights(
                weights[name],
                theta_rho,
                theta_z,
            )
            maximum_weight_error = max(
                maximum_weight_error,
                float(np.max(np.abs(closed - transformed))),
            )
            real_response = weights[name].reshape(4, 25) @ np.real(
                complex_patch.reshape(-1)
            )
            imag_response = weights[name].reshape(4, 25) @ np.imag(
                complex_patch.reshape(-1)
            )
            sampled = real_response + 1j * imag_response
            maximum_sample_error = max(
                maximum_sample_error,
                float(np.max(np.abs(closed - sampled))),
            )

    x = radial * GRID_SPACING
    z = axial * GRID_SPACING
    coefficients = np.asarray((0.7, -0.4, 0.3, 0.8, -0.6, 1.1))
    polynomial = (
        coefficients[0]
        + coefficients[1] * x
        + coefficients[2] * z
        + coefficients[3] * x**2
        + coefficients[4] * x * z
        + coefficients[5] * z**2
    )
    expected_polynomial_components = np.asarray(
        (
            2.0 * coefficients[3],
            coefficients[4],
            2.0 * coefficients[5],
            coefficients[1] / rho0,
        )
    )
    polynomial_errors = {
        name: float(
            np.max(
                np.abs(
                    weights[name].reshape(4, 25) @ polynomial.reshape(-1)
                    - expected_polynomial_components
                )
            )
        )
        for name in POSTPROCESSOR_NAMES
    }

    epsilon = 1.0e-4
    continuum = continuum_symbols(epsilon, -0.7 * epsilon, rho0=rho0)
    low_wave_errors = {}
    for name in POSTPROCESSOR_NAMES:
        discrete = _closed_symbols(name, epsilon, -0.7 * epsilon, rho0)
        nonzero = np.abs(continuum) > 0.0
        low_wave_errors[name] = float(
            np.max(np.abs(discrete[nonzero] / continuum[nonzero] - 1.0))
        )

    base_rho = 0.37 * math.pi
    base_z = -0.29 * math.pi
    alias_patch = np.exp(1j * (radial * base_rho + axial * base_z))
    translated_patch = np.exp(
        1j * (radial * (base_rho + 2.0 * math.pi) + axial * base_z)
    )
    alias_sample_error = float(np.max(np.abs(alias_patch - translated_patch)))
    alias_continuum_difference = float(
        np.max(
            np.abs(
                continuum_symbols(base_rho, base_z, rho0=rho0)
                - continuum_symbols(
                    base_rho + 2.0 * math.pi,
                    base_z,
                    rho0=rho0,
                )
            )
        )
    )
    passed = (
        maximum_weight_error <= SYMBOL_ABSOLUTE_TOLERANCE
        and maximum_sample_error <= SYMBOL_ABSOLUTE_TOLERANCE
        and max(polynomial_errors.values()) <= 2.0e-13
        and max(low_wave_errors.values()) <= LOW_WAVE_RELATIVE_TOLERANCE
        and alias_sample_error <= SYMBOL_ABSOLUTE_TOLERANCE
        and alias_continuum_difference > 1.0
    )
    return {
        "passed": passed,
        "angle_pairs_checked": len(angles),
        "maximum_closed_form_vs_weight_transform_error": maximum_weight_error,
        "maximum_closed_form_vs_sampled_plane_wave_error": maximum_sample_error,
        "general_degree_two_polynomial_maximum_component_errors": (
            polynomial_errors
        ),
        "low_wave_relative_errors_at_theta_rho_1e_4_theta_z_minus_7e_5": (
            low_wave_errors
        ),
        "reciprocal_lattice_alias": {
            "base_theta_over_pi": [base_rho / math.pi, base_z / math.pi],
            "translated_theta_over_pi": [
                (base_rho + 2.0 * math.pi) / math.pi,
                base_z / math.pi,
            ],
            "maximum_patch_sample_error": alias_sample_error,
            "maximum_continuum_symbol_difference": alias_continuum_difference,
            "interpretation": (
                "Integer-lattice samples are identical under a 2*pi "
                "reciprocal-lattice shift even though the originating "
                "continuum derivatives are different."
            ),
        },
    }


def analytic_bands() -> dict[str, Any]:
    """Return exact null loci and sign-reversal partitions."""

    alpha = math.acos(-3.0 / 4.0)
    beta = math.acos(-1.0 / 4.0)
    box_first = 2.0 * math.pi / 5.0
    box_second = 4.0 * math.pi / 5.0
    return {
        "domain": "theta_rho,theta_z in [-pi,pi]",
        "physical_wavenumber_definition": "k = theta / h with h=0.25",
        "sign_reversal_definition": (
            "negative discrete-to-continuum transfer ratio; for mixed "
            "derivatives this is distinct from the quadrant-dependent sign "
            "of the raw symbol"
        ),
        "centered_0p25": {
            "null_loci": {
                "radial": "theta_rho=0",
                "mixed": "theta_rho or theta_z in {0,+/-pi}",
                "axial": "theta_z=0",
                "azimuthal": "theta_rho in {0,+/-pi}",
            },
            "sign_reversal": "none in the open principal zone",
        },
        "centered_0p5": {
            "null_loci": {
                "radial": "theta_rho in {0,+/-pi}",
                "mixed": (
                    "theta_rho or theta_z in "
                    "{0,+/-pi/2,+/-pi}"
                ),
                "axial": "theta_z in {0,+/-pi}",
                "azimuthal": (
                    "theta_rho in {0,+/-pi/2,+/-pi}"
                ),
            },
            "sign_reversal": {
                "radial_axial": "none; the transfer ratios are squares",
                "mixed": (
                    "exactly one of |theta_rho|,|theta_z| lies in "
                    "(pi/2,pi) and the other in (0,pi/2)"
                ),
                "azimuthal": "pi/2 < |theta_rho| < pi",
            },
        },
        "quadratic_5x5": {
            "factor_definitions": {
                "D(t)": "1+2*cos(t)+2*cos(2*t)",
                "A(t)": "4*cos(2*t)-2*cos(t)-2",
                "P(t)": "sin(t)+2*sin(2*t)",
            },
            "special_angles": {
                "alpha_acos_minus_3_over_4": alpha,
                "alpha_over_pi": alpha / math.pi,
                "beta_acos_minus_1_over_4": beta,
                "beta_over_pi": beta / math.pi,
                "box_first_2pi_over_5": box_first,
                "box_second_4pi_over_5": box_second,
                "physical_wavenumbers": {
                    "alpha_over_h": alpha / GRID_SPACING,
                    "beta_over_h": beta / GRID_SPACING,
                    "2pi_over_5h": box_first / GRID_SPACING,
                    "4pi_over_5h": box_second / GRID_SPACING,
                    "nyquist_pi_over_h": math.pi / GRID_SPACING,
                },
            },
            "null_loci": {
                "radial": (
                    "theta_rho in {0,+/-alpha} or "
                    "theta_z in {+/-2pi/5,+/-4pi/5}"
                ),
                "mixed": (
                    "theta_rho or theta_z in "
                    "{0,+/-beta,+/-pi}"
                ),
                "axial": (
                    "theta_z in {0,+/-alpha} or "
                    "theta_rho in {+/-2pi/5,+/-4pi/5}"
                ),
                "azimuthal": (
                    "theta_rho in {0,+/-beta,+/-pi} or "
                    "theta_z in {+/-2pi/5,+/-4pi/5}"
                ),
            },
            "sign_partitions": {
                "A_low": "0<|t|<alpha",
                "A_high": "alpha<|t|<=pi",
                "P_low": "0<|t|<beta",
                "P_high": "beta<|t|<pi",
                "D_plus": "|t|<2pi/5 or 4pi/5<|t|<=pi",
                "D_minus": "2pi/5<|t|<4pi/5",
            },
            "sign_reversal": {
                "radial": (
                    "A_low(theta_rho) with D_minus(theta_z), or "
                    "A_high(theta_rho) with D_plus(theta_z)"
                ),
                "mixed": (
                    "exactly one axis is in P_high and the other in P_low"
                ),
                "axial": (
                    "A_low(theta_z) with D_minus(theta_rho), or "
                    "A_high(theta_z) with D_plus(theta_rho)"
                ),
                "azimuthal": (
                    "P_low(theta_rho) with D_minus(theta_z), or "
                    "P_high(theta_rho) with D_plus(theta_z)"
                ),
            },
        },
    }


def _first_origin_cutoff(
    gain: Callable[[float], float],
    threshold: float,
    upper: float,
) -> float:
    """Bisect the first origin-connected gain crossing."""

    if not 0.0 < threshold < 1.0:
        raise ValueError("resolution threshold must lie between zero and one")
    samples = np.linspace(0.0, upper, 4001)
    values = np.asarray([gain(float(value)) for value in samples])
    below = np.flatnonzero(values < threshold)
    if below.size == 0:
        return upper
    index = int(below[0])
    lower_angle = float(samples[index - 1])
    upper_angle = float(samples[index])
    for _ in range(80):
        midpoint = 0.5 * (lower_angle + upper_angle)
        if gain(midpoint) >= threshold:
            lower_angle = midpoint
        else:
            upper_angle = midpoint
    return 0.5 * (lower_angle + upper_angle)


def resolution_map() -> dict[str, Any]:
    """Map guaranteed origin-centered square resolution efficiencies."""

    first_positive_bound = {
        "centered_0p25": math.pi,
        "centered_0p5": math.pi / 2.0,
        "quadratic_5x5": 2.0 * math.pi / 5.0,
    }
    rows = []
    for postprocessor in POSTPROCESSOR_NAMES:
        for component in COMPONENT_NAMES:
            gain_on_square_corner = lambda angle, p=postprocessor, c=component: (  # noqa: E731
                normalized_transfer(p, c, angle, angle)
            )
            row: dict[str, Any] = {
                "postprocessor": postprocessor,
                "component": component,
                "definition": (
                    "largest Theta for which the sign-preserving normalized "
                    "amplitude is at least the threshold for every "
                    "|theta_rho|,|theta_z|<=Theta. The transfer factors are "
                    "separable and decrease on the reported positive origin "
                    "lobe, making the square corner the minimum; the radial "
                    "factors are checked on 4001 samples and the full square "
                    "on a 201x201 mesh"
                ),
            }
            previous_cutoff = 0.0
            for label, threshold in RESOLUTION_THRESHOLDS.items():
                cutoff = _first_origin_cutoff(
                    gain_on_square_corner,
                    threshold,
                    first_positive_bound[postprocessor],
                )
                sample_angles = np.linspace(0.0, cutoff, 4001)
                sample_gains = np.asarray(
                    [gain_on_square_corner(float(value)) for value in sample_angles]
                )
                monotonic_violation = float(
                    np.max(np.maximum(np.diff(sample_gains), 0.0))
                )
                gain_at_cutoff = float(gain_on_square_corner(cutoff))
                square_axis = np.linspace(0.0, cutoff, 201)
                square_rho, square_z = np.meshgrid(
                    square_axis,
                    square_axis,
                    indexing="ij",
                )
                square_gains = normalized_transfer(
                    postprocessor,
                    component,
                    square_rho,
                    square_z,
                )
                minimum_square_gain = float(np.min(square_gains))
                square_corner_error = abs(minimum_square_gain - gain_at_cutoff)
                if (
                    minimum_square_gain < threshold - 2.0e-12
                    or square_corner_error > 2.0e-12
                ):
                    raise RuntimeError("origin-square resolution check failed")
                row[label] = {
                    "minimum_required_gain": threshold,
                    "theta_cutoff": cutoff,
                    "theta_cutoff_over_pi": cutoff / math.pi,
                    "physical_wavenumber_cutoff": cutoff / GRID_SPACING,
                    "gain_at_cutoff": gain_at_cutoff,
                    "sampled_monotonicity_violation": monotonic_violation,
                    "minimum_gain_on_201x201_square": minimum_square_gain,
                    "minimum_vs_corner_absolute_error": square_corner_error,
                }
                if cutoff + ANGLE_ABSOLUTE_TOLERANCE < previous_cutoff:
                    raise RuntimeError("resolution thresholds are not nested")
                previous_cutoff = cutoff
            rows.append(row)
    return {
        "metric": "origin-centered square resolving efficiency",
        "tolerance_source": (
            "Project-defined operator-amplitude thresholds: 90 percent "
            "transmission (10 percent amplitude loss) and a descriptive "
            "50 percent transmission boundary. Lele motivates declaring a "
            "frequency-response tolerance but these are not his modified-"
            "wavenumber error thresholds."
        ),
        "rows": rows,
    }


def _mode_patch(specification: tuple[float, float, float]) -> np.ndarray:
    theta_rho_fraction, theta_z_fraction, phase_fraction = specification
    offsets = np.arange(-2, 3, dtype=float)
    radial, axial = np.meshgrid(offsets, offsets, indexing="ij")
    return np.cos(
        math.pi
        * (
            theta_rho_fraction * radial
            + theta_z_fraction * axial
            + phase_fraction
        )
    )


def _measurement_vector(patch: np.ndarray, rho0: float) -> np.ndarray:
    return np.concatenate(
        (
            e033._centered_component_ledgers(
                patch,
                rho0,
                stride=1,
            )["components"],
            e033._centered_component_ledgers(
                patch,
                rho0,
                stride=2,
            )["components"],
            e033._quadratic_recovery(patch, rho0)["components"],
        )
    )


def _fit_mode_bank(
    target: np.ndarray,
    bank: tuple[tuple[float, float, float], ...],
    *,
    rho0: float,
) -> dict[str, Any]:
    patches = [_mode_patch(specification) for specification in bank]
    response = np.column_stack(
        [_measurement_vector(patch, rho0) for patch in patches]
    )
    row_norms = np.linalg.norm(response, axis=1)
    if np.any(row_norms <= 0.0):
        raise RuntimeError("mode bank leaves a zero measurement row")
    rank = int(np.linalg.matrix_rank(response))
    coefficients, _residuals, _reported_rank, singular_values = np.linalg.lstsq(
        response,
        np.asarray(target, dtype=float),
        rcond=None,
    )
    patch = sum(
        coefficient * mode_patch
        for coefficient, mode_patch in zip(coefficients, patches, strict=True)
    )
    reconstructed = _measurement_vector(patch, rho0)
    residual = reconstructed - target
    normalized_response = response / row_norms[:, np.newaxis]
    normalized_singular_values = np.linalg.svd(
        normalized_response,
        compute_uv=False,
    )
    return {
        "rank": rank,
        "nullity": len(bank) - rank,
        "coefficients": [float(value) for value in coefficients],
        "mode_bank": [
            {
                "theta_rho_over_pi": values[0],
                "theta_z_over_pi": values[1],
                "phase_over_pi": values[2],
            }
            for values in bank
        ],
        "raw_response_singular_values": [
            float(value) for value in singular_values
        ],
        "row_normalized_condition_number": float(
            normalized_singular_values[0] / normalized_singular_values[-1]
        ),
        "coefficient_l2": float(np.linalg.norm(coefficients)),
        "coefficient_linf": float(np.max(np.abs(coefficients))),
        "patch_l2": float(np.linalg.norm(patch)),
        "patch_linf": float(np.max(np.abs(patch))),
        "patch_sha256": hashlib.sha256(
            np.ascontiguousarray(patch).view(np.uint8)
        ).hexdigest(),
        "reconstructed_measurements": [
            float(value) for value in reconstructed
        ],
        "maximum_absolute_measurement_residual": float(
            np.max(np.abs(residual))
        ),
        "patch": patch,
    }


def mode_mixture_nonuniqueness() -> dict[str, Any]:
    """Fit two disjoint spectral dictionaries to each rounded E-033 target."""

    comparisons = []
    maximum_residual = 0.0
    minimum_patch_separation = math.inf
    for amplitude, target in E033_ROUNDED_HOTSPOT_TARGETS.items():
        lower = _fit_mode_bank(
            target,
            LOWER_BAND_MODE_BANK,
            rho0=REFERENCE_RHO,
        )
        grid = _fit_mode_bank(
            target,
            GRID_SCALE_MODE_BANK,
            rho0=REFERENCE_RHO,
        )
        patch_separation = float(np.linalg.norm(lower["patch"] - grid["patch"]))
        maximum_residual = max(
            maximum_residual,
            lower["maximum_absolute_measurement_residual"],
            grid["maximum_absolute_measurement_residual"],
        )
        minimum_patch_separation = min(minimum_patch_separation, patch_separation)
        for result in (lower, grid):
            result.pop("patch")
        comparisons.append(
            {
                "amplitude": amplitude,
                "target_source": (
                    "rounded six-decimal E-033 hotspot table; reproduction "
                    "is compatibility with those rounded values only"
                ),
                "target_order": [
                    f"{postprocessor}:{component}"
                    for postprocessor in POSTPROCESSOR_NAMES
                    for component in COMPONENT_NAMES
                ],
                "target_measurements": [float(value) for value in target],
                "lower_band_fit": lower,
                "grid_scale_fit": grid,
                "lower_vs_grid_patch_l2_separation": patch_separation,
            }
        )
    passed = (
        maximum_residual <= MIXTURE_ABSOLUTE_TOLERANCE
        and minimum_patch_separation > 1.0e-3
        and all(
            row[f"{label}_fit"]["rank"] == 12
            for row in comparisons
            for label in ("lower_band", "grid_scale")
        )
    )
    return {
        "passed": passed,
        "lower_band_definition": (
            "all |theta| components are <=0.50*pi; this is a lower-band "
            "manufactured dictionary, not a claim that every mode is within "
            "every postprocessor's 10-percent resolution square"
        ),
        "grid_scale_definition": (
            "all |theta| components lie between 0.55*pi and 0.95*pi"
        ),
        "maximum_absolute_measurement_residual": maximum_residual,
        "minimum_lower_vs_grid_patch_l2_separation": minimum_patch_separation,
        "comparisons": comparisons,
        "interpretation": (
            "Two disjoint, full-rank manufactured spectral dictionaries "
            "reproduce all twelve rounded component measurements while "
            "producing different 5x5 patches. The examples prove "
            "nonuniqueness for these finite measurements; they do not infer "
            "which dictionary resembles the unretained endpoint spectrum."
        ),
    }


def preregistered_three_grid_gate() -> dict[str, Any]:
    """Return the coupled-grid screen required before another replay."""

    radial_max = 80.0
    source = e025.SmoothAnnulusSpec()
    minimum_transition_width = (
        source.inner_radius * source.angular_smoothing_width
    )
    specifications = ((0.125, 4), (0.0625, 5), (0.03125, 6))
    grids = []
    for spacing, directional_radius in specifications:
        delta_theta = e025.directional_resolution(directional_radius)
        bases = e025.primitive_meridional_bases(directional_radius)
        maximum_reach = spacing * max(
            math.hypot(first, second) for first, second in bases
        )
        grids.append(
            {
                "spacing": spacing,
                "directional_radius": directional_radius,
                "directional_resolution_radians": delta_theta,
                "h_over_directional_resolution": spacing / delta_theta,
                "maximum_wide_stencil_physical_reach": maximum_reach,
                "minimum_source_transition_cells": (
                    minimum_transition_width / spacing
                ),
                "estimated_quarter_disk_unknowns": int(
                    round(math.pi * radial_max**2 / (4.0 * spacing**2))
                ),
            }
        )
    geometry_passed = (
        all(row["minimum_source_transition_cells"] >= 6.0 for row in grids)
        and all(
            grids[index + 1]["h_over_directional_resolution"]
            < grids[index]["h_over_directional_resolution"]
            for index in range(len(grids) - 1)
        )
        and all(
            grids[index + 1]["maximum_wide_stencil_physical_reach"]
            < grids[index]["maximum_wide_stencil_physical_reach"]
            for index in range(len(grids) - 1)
        )
    )
    return {
        "status": "predeclared_screen_pending_e035_resource_feasibility",
        "minimum_grid_count": 3,
        "refinement_ratio": 2.0,
        "radial_max": radial_max,
        "source": {
            "mu": source.mu,
            "inner_radius": source.inner_radius,
            "outer_radius": source.outer_radius,
            "radial_smoothing_width": source.radial_smoothing_width,
            "angular_smoothing_width": source.angular_smoothing_width,
            "minimum_physical_transition_width": minimum_transition_width,
        },
        "candidate_grids": grids,
        "coupled_geometry_preflight_passed": geometry_passed,
        "fourth_grid_rate_check": {
            "spacing": 0.015625,
            "directional_radius": 7,
            "role": (
                "required to confirm an apparent-order plateau unless an "
                "independent validated derivative-error enclosure is used"
            ),
            "status": "not_authorized_until_e035_resource_preflight",
        },
        "fixed_before_solve": [
            "R=80 physical domain and boundary condition",
            "the stated positive mass-preserving smooth source and transition widths",
            "accepted amplitude 6/12 and canonical continuation path",
            "common physical ROI and exact common-node mapping without interpolation",
            "5x5 degree-two recovery family with support shrinking as 2*h",
            "centered stride-1 and stride-2 families with support shrinking with h",
            "solver, cone, tail, flux, force, source, and provenance gates",
        ],
        "fixed_rois": {
            "points": [
                [8.75, 0.75],
                [5.75, 0.5],
                [6.0, 0.5],
                [6.25, 0.5],
            ],
            "masks": [
                "positive source support",
                "source transition support",
                "interior common nodes with rho>=0.5 and radius<=78.5",
            ],
            "quadrature": "same coarsest-grid cylindrical weights on every restricted field",
        },
        "derivative_norms": {
            "matrix_definition": (
                "M(H)=[[phi_rr,phi_rz,0],[phi_rz,phi_zz,0],"
                "[0,0,phi_r/rho]]"
            ),
            "weighted_l2": (
                "D_j,2=sqrt(sum_x w_x ||M(H_j)-M(H_j+1)||_F^2 / "
                "sum_x w_x)"
            ),
            "linf": "D_j,inf=max_x ||M(H_j)-M(H_j+1)||_2",
            "componentwise": (
                "also report weighted L2 and Linf for all four raw components"
            ),
            "same_grid_operator_spread": (
                "A_j,p=max_q,qprime ||M(H_j^q)-M(H_j^qprime)||_p"
            ),
        },
        "recovery_stability_gates": {
            "design_rank": 6,
            "design_condition_number": e033.implementation_provenance()[
                "strategy"
            ]["recovery"]["condition_number_2"],
            "maximum_basis_fit_residual": 2.0e-14,
            "maximum_quadratic_component_error": 2.0e-13,
            "maximum_linearity_closure_error": 2.0e-11,
            "scaled_weight_rule": (
                "h^2*||w|| for second derivatives and h*rho*||w|| for "
                "azimuthal recovery must remain grid-independent within "
                "128 machine eps; no adaptive weights, patch, or axis fallback"
            ),
        },
        "required_measurements": [
            "raw radial, mixed, axial, and azimuthal component fields",
            "Frobenius Hessian difference before the nonlinear eigenvalue map",
            "pair margin with eigengap and eigenbranch-stability ledger",
            "solver/algebraic error separately bounded below grid differences",
            "native-grid high-band occupancy and odd/even parity diagnostics",
        ],
        "apparent_order_screen": {
            "norm_formula_for_ratio_2": "p=log2(D_0,p/D_1,p)",
            "necessary_not_sufficient": (
                "finite positive p and D_1,p<D_0,p in every signal-resolved "
                "primary mask/norm, plus A_2,p<A_1,p<A_0,p"
            ),
            "orientation_rule": (
                "Because norms erase sign, separately require componentwise "
                "signed differences at every fixed point to retain orientation; "
                "an oscillatory pattern is inconclusive"
            ),
            "fourth_grid_rule": (
                "apparent p values must agree within 0.5 between the two "
                "finest triplets; this cannot be tested with three grids"
            ),
            "policy_status": "project-specific screen, not a theorem or Celik acceptance rule",
        },
        "solver_separation_policy": (
            "A 10x-tighter replay on the same branch/path must change every "
            "primary derivative norm by <=10 percent of the smaller adjacent-"
            "grid difference. This one-decade threshold is project policy."
        ),
        "transfer_requirement": (
            "Content contributing to a claimed Hessian feature must move "
            "inside the project-defined 90-percent operator-amplitude square "
            "as h decreases, or its outside-square contribution must converge "
            "to zero in a declared derivative-controlling norm."
        ),
        "stop_rules": [
            "stop on any inherited checkpoint/provenance, source, domain, or cone-gate failure",
            "stop if any grid has fewer than six cells across the minimum source transition",
            "stop if h/delta_theta or maximum physical stencil reach fails to decrease",
            "stop if the canonical continuation path leaves a required cone",
            "stop if inter-grid differences are oscillatory or near zero enough to make apparent order unstable",
            "stop if recovery stability, ROI, source, or thresholds would need post-outcome adjustment",
            "stop as blocked if E-035 finds the fixed grids exceed the resource cap; do not shrink R or change the source",
            "do not infer continuum Hessian convergence from one added grid, three grids, or GCI alone",
        ],
    }


def run_analysis() -> dict[str, Any]:
    """Run the bounded analytic/manufactured E-034 campaign."""

    started = time.perf_counter()
    validation = exact_symbol_validation()
    mixtures = mode_mixture_nonuniqueness()
    failed_gates = []
    if not validation["passed"]:
        failed_gates.append("exact_symbol_validation")
    if not mixtures["passed"]:
        failed_gates.append("manufactured_nonuniqueness")
    if failed_gates:
        decision_status = "failed_" + "_and_".join(failed_gates)
        main_result = (
            "The E-034 analytic campaign failed one or more declared gates. "
            "The diagnostic payload is retained; no transfer conclusion or "
            "lineage change is permitted."
        )
    else:
        decision_status = "qualified_nonidentifying_transfer_functions"
        main_result = (
            "All twelve symbols are exact and validated. The quadratic "
            "recovery has transverse Dirichlet null lines and high-band "
            "sign reversals. The stride-2 mixed and azimuthal operators "
            "have sign-reversing bands above half Nyquist (for mixed, only "
            "when exactly one axis is in the high band). Distinct lower-band "
            "and grid-scale mixtures reproduce all rounded E-033 hotspot "
            "component measurements, so those measurements do not identify "
            "their generating spectrum."
        )
    report = {
        "epistemic_status": (
            "exact Fourier symbols and manufactured finite-patch examples "
            "for three declared linear postprocessors; not a continuum PDE "
            "solution, physical field, artificial gravity, inertial control, "
            "spacetime engineering, FTL, or propulsion"
        ),
        "focus_question": (
            "What scales do E-033's centered 0.25, centered 0.5, and fixed "
            "25-node quadratic component postprocessors transmit, suppress, "
            "alias, or reverse, and can their recorded component measurements "
            "identify a unique lower-band or grid-scale cause?"
        ),
        "runtime_provenance": runtime_provenance(),
        "implementation_provenance": implementation_provenance(),
        "configuration": {
            "grid_spacing": GRID_SPACING,
            "reference_rho": REFERENCE_RHO,
            "fourier_mode": "exp(i*(i*theta_rho+j*theta_z))",
            "principal_zone": "[-pi,pi]^2",
            "resolution_thresholds": RESOLUTION_THRESHOLDS,
        },
        "exact_symbols": {
            "centered_stride_s": {
                "radial": "-4*sin(s*theta_rho/2)^2/(s*h)^2",
                "mixed": "-sin(s*theta_rho)*sin(s*theta_z)/(s*h)^2",
                "axial": "-4*sin(s*theta_z/2)^2/(s*h)^2",
                "azimuthal": "i*sin(s*theta_rho)/(s*h*rho0)",
            },
            "quadratic_5x5": {
                "radial": "A(theta_rho)*D(theta_z)/(35*h^2)",
                "mixed": "-P(theta_rho)*P(theta_z)/(25*h^2)",
                "axial": "D(theta_rho)*A(theta_z)/(35*h^2)",
                "azimuthal": "i*P(theta_rho)*D(theta_z)/(25*h*rho0)",
                "D": "1+2*cos(t)+2*cos(2*t)",
                "A": "4*cos(2*t)-2*cos(t)-2",
                "P": "sin(t)+2*sin(2*t)",
            },
            "frozen_coefficient_warning": (
                "rho0 is fixed locally. The cylindrical 1/rho coefficient "
                "prevents one global translation-invariant azimuthal symbol."
            ),
        },
        "analytic_bands": analytic_bands(),
        "resolution_map": resolution_map(),
        "exact_symbol_validation": validation,
        "mode_mixture_nonuniqueness": mixtures,
        "three_grid_gate": preregistered_three_grid_gate(),
        "decision": {
            "status": decision_status,
            "passed": not failed_gates,
            "failed_gates": failed_gates,
            "main_result": main_result,
        },
        "limitations": [
            "Fourier symbols qualify linear postprocessors on an infinite lattice; the E-033 patch is finite and windowed.",
            "The azimuthal symbol freezes 1/rho at rho0 and does not represent coefficient variation, the axis, or boundaries.",
            "Resolution bands are operator-response definitions with explicit tolerances, not estimates of the endpoint field spectrum.",
            "The manufactured mixtures fit rounded six-decimal ledger values and are existence examples, not reconstructions of unretained endpoint fields.",
            "Mode coefficients use cancellation and do not impose a smoothness, positivity, energy, PDE, or probabilistic prior.",
            "Twelve linear component measurements cannot identify a unique 25-node patch or originating continuous spectrum.",
            "Pair margin is nonlinear in Hessian eigenvalues and is deliberately excluded from the linear mixture fit.",
            "No checkpoint or retained field array/file is read or written; the embedded E-033 targets are rounded field-derived ledger measurements.",
            "No retained work snapshot or checkpoint-manifest entry is read, written, accepted, or changed.",
            "Accepted lineage remains E-028 stage 6/12; every tail, path, refinement, and physical-scale boundary remains in force.",
        ],
        "resource_accounting": {
            "elapsed_seconds": time.perf_counter() - started,
        },
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-json", type=Path)
    args = parser.parse_args()
    report = run_analysis()
    if args.report_json is not None:
        args.report_json.write_text(
            json.dumps(report, allow_nan=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(
        "E-034 "
        f"decision={report['decision']['status']} "
        "symbol_error="
        f"{report['exact_symbol_validation']['maximum_closed_form_vs_weight_transform_error']:.3e} "
        "mixture_error="
        f"{report['mode_mixture_nonuniqueness']['maximum_absolute_measurement_residual']:.3e} "
        f"elapsed={report['resource_accounting']['elapsed_seconds']:.2f}s"
    )
    if not report["decision"]["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

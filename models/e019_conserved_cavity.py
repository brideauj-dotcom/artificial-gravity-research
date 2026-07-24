#!/usr/bin/env python3
"""E-019 conservation and multipole screen for a one-dimensional cavity.

This is a weak-field, scalar T00 model.  It tests what energy and
center-of-energy conservation do to the exterior field before a full
tensor Einstein-Langevin calculation is attempted.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from typing import Protocol, Sequence


G = 6.67430e-11
C = 299_792_458.0


class SourceComponent(Protocol):
    """A linearized perturbation to a one-dimensional source."""

    label: str

    def moment(self, order: int) -> float:
        """Return integral(delta energy * x**order), in J m**order."""

    def acceleration(self, probe_x_m: float) -> float:
        """Return the on-axis weak-field acceleration perturbation."""

    def extent(self) -> float:
        """Return the largest absolute source coordinate represented."""


@dataclass(frozen=True)
class PointEnergy:
    """A signed energy perturbation localized at one coordinate."""

    label: str
    energy_j: float
    x_m: float

    def moment(self, order: int) -> float:
        if order < 0:
            raise ValueError("moment order must be non-negative")
        return self.energy_j * self.x_m**order

    def acceleration(self, probe_x_m: float) -> float:
        separation = probe_x_m - self.x_m
        if separation == 0:
            raise ValueError(f"probe coincides with point source {self.label!r}")
        return -G * self.energy_j / C**2 * separation / abs(separation) ** 3

    def extent(self) -> float:
        return abs(self.x_m)


@dataclass(frozen=True)
class LinearizedMassDisplacement:
    """First-order T00 perturbation from displacing an ordinary mass.

    The derivative form avoids subtracting two nearly identical, enormous
    rest energies when the recoil displacement is much smaller than machine
    precision at the source coordinate.
    """

    label: str
    mass_kg: float
    x0_m: float
    delta_x_m: float

    def moment(self, order: int) -> float:
        if order < 0:
            raise ValueError("moment order must be non-negative")
        if order == 0:
            return 0.0
        return (
            self.mass_kg
            * C**2
            * order
            * self.x0_m ** (order - 1)
            * self.delta_x_m
        )

    def acceleration(self, probe_x_m: float) -> float:
        separation = probe_x_m - self.x0_m
        if separation == 0:
            raise ValueError(f"probe coincides with displaced mass {self.label!r}")
        return -2.0 * G * self.mass_kg * self.delta_x_m / abs(separation) ** 3

    def extent(self) -> float:
        return abs(self.x0_m)


@dataclass(frozen=True)
class SourceDistribution:
    """A collection of linearized source perturbations."""

    name: str
    components: tuple[SourceComponent, ...]
    note: str

    def moment(self, order: int) -> float:
        return math.fsum(component.moment(order) for component in self.components)

    def exact_acceleration(self, probe_x_m: float) -> float:
        return math.fsum(
            component.acceleration(probe_x_m) for component in self.components
        )

    def multipole_acceleration(self, probe_x_m: float, max_order: int = 6) -> float:
        """Return the positive-axis exterior multipole expansion.

        For probe x greater than every represented source coordinate,

          delta a_x = -(G/c^2) sum_n (n+1) I_n / x^(n+2),

        where I_n = integral(delta E x^n).
        """

        if probe_x_m <= max(component.extent() for component in self.components):
            raise ValueError("multipole probe must lie beyond the source extent")
        if max_order < 0:
            raise ValueError("max_order must be non-negative")
        terms = (
            (order + 1) * self.moment(order) / probe_x_m ** (order + 2)
            for order in range(max_order + 1)
        )
        return -G / C**2 * math.fsum(terms)

    def first_nonzero_moment(self, through_order: int = 6) -> int | None:
        scale = max(
            1.0,
            *(abs(component.moment(0)) for component in self.components),
        )
        for order in range(through_order + 1):
            if not math.isclose(self.moment(order), 0.0, abs_tol=1e-14 * scale):
                return order
        return None

    def summary(self, probe_x_m: float) -> dict[str, object]:
        exact = self.exact_acceleration(probe_x_m)
        multipole = self.multipole_acceleration(probe_x_m)
        return {
            "name": self.name,
            "note": self.note,
            "monopole_J": self.moment(0),
            "dipole_J_m": self.moment(1),
            "quadrupole_raw_J_m2": self.moment(2),
            "octupole_raw_J_m3": self.moment(3),
            "leading_moment_order": self.first_nonzero_moment(),
            "exact_acceleration_m_s2": exact,
            "multipole_acceleration_m_s2": multipole,
            "multipole_relative_error": (
                abs(multipole - exact) / abs(exact) if exact != 0.0 else None
            ),
        }


def field_only_source(energy_j: float, field_x_m: float = 0.0) -> SourceDistribution:
    return SourceDistribution(
        name="field_only",
        components=(PointEnergy("cavity field", energy_j, field_x_m),),
        note="Incomplete comparison source: ignores where the field energy came from.",
    )


def closed_cavity_source(
    energy_j: float, cavity_length_m: float, field_x_m: float = 0.0
) -> SourceDistribution:
    """Move energy from two wall-localized reservoirs into the cavity field.

    Wall perturbations are solved so both total perturbation energy and the
    first energy moment remain zero.  They are bookkeeping reservoirs, not a
    microscopic model of mirror stress.
    """

    if cavity_length_m <= 0:
        raise ValueError("cavity length must be positive")
    x_left = -cavity_length_m / 2.0
    x_right = cavity_length_m / 2.0
    if not x_left <= field_x_m <= x_right:
        raise ValueError("field position must lie inside the cavity")

    left_energy = -energy_j * (x_right - field_x_m) / cavity_length_m
    right_energy = -energy_j * (field_x_m - x_left) / cavity_length_m
    return SourceDistribution(
        name="closed_cavity",
        components=(
            PointEnergy("cavity field", energy_j, field_x_m),
            PointEnergy("left wall reservoir", left_energy, x_left),
            PointEnergy("right wall reservoir", right_energy, x_right),
        ),
        note=(
            "Conserves perturbation energy and center of energy; the leading "
            "exterior term is therefore quadrupolar in this scalar model."
        ),
    )


def emitted_pulse_source(
    energy_j: float,
    elapsed_s: float,
    support_mass_kg: float,
    emission_x_m: float = 0.0,
) -> SourceDistribution:
    """Model a right-moving pulse before absorption, including source recoil.

    The pulse carries momentum E/c.  To first order, a support of mass M
    recoils with velocity -E/(Mc), giving displacement -Et/(Mc).  Including
    that displacement makes the total energy monopole and center-of-energy
    dipole constant through first order.
    """

    if elapsed_s < 0:
        raise ValueError("elapsed time must be non-negative")
    if support_mass_kg <= 0:
        raise ValueError("support mass must be positive")

    pulse_x = emission_x_m + C * elapsed_s
    recoil_dx = -energy_j * elapsed_s / (support_mass_kg * C)
    return SourceDistribution(
        name="emitted_pulse_with_recoil",
        components=(
            PointEnergy("depleted source", -energy_j, emission_x_m),
            PointEnergy("outgoing pulse", energy_j, pulse_x),
            LinearizedMassDisplacement(
                "source support recoil", support_mass_kg, emission_x_m, recoil_dx
            ),
        ),
        note=(
            "Valid before absorption and to first order in recoil; emission and "
            "recoil cancel monopole and dipole changes, leaving higher moments."
        ),
    )


def radial_sweep(
    source: SourceDistribution, first_probe_m: float
) -> list[dict[str, float | None]]:
    rows: list[dict[str, float | None]] = []
    prior_r: float | None = None
    prior_a: float | None = None
    for factor in (1.0, 2.0, 4.0, 8.0):
        radius = first_probe_m * factor
        acceleration = source.exact_acceleration(radius)
        slope = None
        if prior_r is not None and prior_a is not None and acceleration != 0.0:
            slope = math.log(abs(prior_a / acceleration)) / math.log(radius / prior_r)
        rows.append(
            {
                "probe_m": radius,
                "acceleration_m_s2": acceleration,
                "effective_power_law": slope,
            }
        )
        prior_r = radius
        prior_a = acceleration
    return rows


def build_report(args: argparse.Namespace) -> dict[str, object]:
    if args.probe_m <= max(args.length_m / 2.0, args.loss_distance_m):
        raise ValueError("probe must lie beyond the cavity and in-flight pulse")
    if not 0.0 <= args.pulse_fraction <= 1.0:
        raise ValueError("pulse fraction must be between zero and one")

    field_only = field_only_source(args.energy_j, args.field_offset_m)
    closed = closed_cavity_source(
        args.energy_j, args.length_m, args.field_offset_m
    )
    pulse_time = args.pulse_fraction * args.loss_distance_m / C
    pulse = emitted_pulse_source(args.energy_j, pulse_time, args.support_mass_kg)

    scenarios = [field_only, closed, pulse]
    summaries = [scenario.summary(args.probe_m) for scenario in scenarios]
    naive_acceleration = abs(field_only.exact_acceleration(args.probe_m))
    for summary in summaries:
        exact = abs(float(summary["exact_acceleration_m_s2"]))
        summary["absolute_ratio_to_field_only"] = exact / naive_acceleration

    return {
        "model": "E-019 conserved cavity scalar multipole screen",
        "parameters": {
            "energy_J": args.energy_j,
            "cavity_length_m": args.length_m,
            "field_offset_m": args.field_offset_m,
            "probe_m": args.probe_m,
            "loss_distance_m": args.loss_distance_m,
            "pulse_fraction": args.pulse_fraction,
            "support_mass_kg": args.support_mass_kg,
        },
        "scenarios": summaries,
        "closed_cavity_radial_sweep": radial_sweep(closed, args.probe_m),
        "interpretation": (
            "Within this T00-only weak-field model, closing the energy and "
            "center-of-energy ledger removes exterior monopole and dipole "
            "changes. The surviving near-zone signal begins at quadrupole "
            "order. A full conserved T_mu_nu calculation is still required "
            "to include mirror/support stress and retarded tensor effects."
        ),
    }


def render_text(report: dict[str, object]) -> str:
    parameters = report["parameters"]
    assert isinstance(parameters, dict)
    lines = [
        str(report["model"]),
        (
            f"E={parameters['energy_J']:.6g} J, L={parameters['cavity_length_m']:.6g} m, "
            f"probe={parameters['probe_m']:.6g} m"
        ),
        "",
        "scenario                         M0 (J)       D1 (J m)       I2 (J m^2)      a_x (m/s^2)       |a|/naive",
    ]
    scenarios = report["scenarios"]
    assert isinstance(scenarios, list)
    for item in scenarios:
        assert isinstance(item, dict)
        lines.append(
            f"{item['name']:<31} "
            f"{item['monopole_J']:>11.3e}  "
            f"{item['dipole_J_m']:>13.3e}  "
            f"{item['quadrupole_raw_J_m2']:>14.3e}  "
            f"{item['exact_acceleration_m_s2']:>14.3e}  "
            f"{item['absolute_ratio_to_field_only']:>12.3e}"
        )
    lines.extend(["", "Closed-cavity radial sweep:"])
    sweep = report["closed_cavity_radial_sweep"]
    assert isinstance(sweep, list)
    for row in sweep:
        assert isinstance(row, dict)
        slope = row["effective_power_law"]
        slope_text = "n/a" if slope is None else f"r^-{slope:.5f}"
        lines.append(
            f"  r={row['probe_m']:.6g} m  a={row['acceleration_m_s2']:.6e} m/s^2  {slope_text}"
        )
    lines.extend(["", str(report["interpretation"])])
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--energy-j", type=float, default=1.0)
    parser.add_argument("--length-m", type=float, default=0.01)
    parser.add_argument("--field-offset-m", type=float, default=0.0)
    parser.add_argument("--probe-m", type=float, default=1.0)
    parser.add_argument("--loss-distance-m", type=float, default=0.01)
    parser.add_argument("--pulse-fraction", type=float, default=0.5)
    parser.add_argument("--support-mass-kg", type=float, default=1.0)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

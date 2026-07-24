#!/usr/bin/env python3
"""E-020 body-screening bound for a canonical inverse-power chameleon.

The model asks whether a chameleon scalar can provide a body-scale,
approximately universal acceleration inside a vacuum chamber.  It is a
transparent scaling screen, not a finite-element chamber solution.

Natural-unit formulas are translated to SI only at the final acceleration
step.  The chamber field is estimated by setting its Compton wavelength equal
to the chamber size.  The test body's scalar charge is then reduced by the
standard thin-shell factor.  This deliberately neglects the much smaller
field value inside dense matter, making the result an optimistic upper bound.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass


C = 299_792_458.0
G = 6.67430e-11
HBAR_C_EV_M = 1.973_269_804e-7
REDUCED_PLANCK_MASS_EV = 2.435e27
STANDARD_GRAVITY_M_S2 = 9.80665
EV_J = 1.602_176_634e-19


@dataclass(frozen=True)
class Body:
    """Homogeneous-sphere proxy used only for thin-shell compactness."""

    label: str
    mass_kg: float
    radius_m: float

    def compactness(self) -> float:
        """Return the dimensionless surface potential GM/(Rc^2)."""

        if self.mass_kg <= 0.0:
            raise ValueError("body mass must be positive")
        if self.radius_m <= 0.0:
            raise ValueError("body radius must be positive")
        return G * self.mass_kg / (self.radius_m * C**2)


def chamber_field_ev(
    chamber_scale_m: float,
    lambda_ev: float = 2.4e-3,
    power_n: float = 1.0,
    geometry_factor: float = 1.0,
) -> float:
    """Estimate an optimistic passive chamber field scale in electronvolts.

    For V(phi)=Lambda^(4+n)/phi^n, the fluctuation mass is

      m_eff^2 = n(n+1) Lambda^(4+n) / phi^(n+2).

    Setting m_eff L = 1 gives the chamber-limited field.  Published chamber
    solutions attach an order-one geometry coefficient; ``geometry_factor=1``
    is retained as an optimistic benchmark, not asserted as a universal upper
    bound on arbitrary chamber geometry or active boundary conditions.
    """

    if chamber_scale_m <= 0.0:
        raise ValueError("chamber scale must be positive")
    if lambda_ev <= 0.0:
        raise ValueError("Lambda must be positive")
    if power_n <= 0.0:
        raise ValueError("inverse-power index n must be positive")
    if geometry_factor <= 0.0:
        raise ValueError("geometry factor must be positive")

    length_ev_inverse = chamber_scale_m / HBAR_C_EV_M
    field_power = (
        power_n
        * (power_n + 1.0)
        * lambda_ev ** (4.0 + power_n)
        * length_ev_inverse**2
    )
    return geometry_factor * field_power ** (1.0 / (power_n + 2.0))


def thin_shell_charge(
    beta: float,
    body: Body,
    ambient_field_ev: float,
    reduced_planck_mass_ev: float = REDUCED_PLANCK_MASS_EV,
) -> float:
    """Return the body's scalar charge relative to an unscreened test mass.

    In the high-density-body limit, the standard spherical thin-shell result
    can be written

      q = min[1, phi_bg / (2 beta M_Pl Phi_body)],

    where Phi_body=GM/(Rc^2).  Order-one convention changes do not matter for
    the many-order engineering comparison made here.
    """

    if beta <= 0.0:
        raise ValueError("matter coupling beta must be positive")
    if ambient_field_ev <= 0.0:
        raise ValueError("ambient field must be positive")
    if reduced_planck_mass_ev <= 0.0:
        raise ValueError("reduced Planck mass must be positive")

    charge = ambient_field_ev / (
        2.0 * beta * reduced_planck_mass_ev * body.compactness()
    )
    return min(1.0, charge)


def chamber_scale_to_unscreen_body_m(
    beta: float,
    body: Body,
    lambda_ev: float = 2.4e-3,
    power_n: float = 1.0,
    geometry_factor: float = 1.0,
) -> float:
    """Invert the chamber estimate for the scale at which ``q`` reaches one.

    This is not a design prescription.  It exposes how far a finite screened
    cabin is from the field amplitude needed to keep a macroscopic body
    unscreened at a selected microscopic coupling.
    """

    if beta <= 0.0:
        raise ValueError("matter coupling beta must be positive")
    if lambda_ev <= 0.0:
        raise ValueError("Lambda must be positive")
    if power_n <= 0.0:
        raise ValueError("inverse-power index n must be positive")
    if geometry_factor <= 0.0:
        raise ValueError("geometry factor must be positive")

    required_field_ev = (
        2.0 * beta * REDUCED_PLANCK_MASS_EV * body.compactness()
    )
    field_without_geometry = required_field_ev / geometry_factor
    length_ev_inverse_squared = field_without_geometry ** (power_n + 2.0) / (
        power_n
        * (power_n + 1.0)
        * lambda_ev ** (4.0 + power_n)
    )
    return math.sqrt(length_ev_inverse_squared) * HBAR_C_EV_M


def scalar_acceleration_m_s2(
    beta: float,
    scalar_charge: float,
    field_excursion_ev: float,
    gradient_scale_m: float,
    reduced_planck_mass_ev: float = REDUCED_PLANCK_MASS_EV,
) -> float:
    """Return ``beta*q*c^2*Delta(phi)/(M_Pl*ell)`` in SI units."""

    if beta <= 0.0:
        raise ValueError("matter coupling beta must be positive")
    if not 0.0 <= scalar_charge <= 1.0:
        raise ValueError("scalar charge must lie between zero and one")
    if field_excursion_ev < 0.0:
        raise ValueError("field excursion must be non-negative")
    if gradient_scale_m <= 0.0:
        raise ValueError("gradient scale must be positive")
    if reduced_planck_mass_ev <= 0.0:
        raise ValueError("reduced Planck mass must be positive")

    return (
        beta
        * scalar_charge
        * C**2
        * field_excursion_ev
        / (reduced_planck_mass_ev * gradient_scale_m)
    )


def externally_driven_unscreened_requirement(
    beta: float,
    body: Body,
    target_acceleration_m_s2: float,
    field_span_m: float,
) -> dict[str, float]:
    """Quantify a formal externally driven escape from passive screening.

    This calculation *assumes* a separate actuator can keep the whole body
    unscreened while imposing a scalar gradient.  It does not provide such an
    actuator or include its reaction, penetration, backreaction, potential,
    or EFT budget.  The returned kinetic energy density is therefore only the
    canonical gradient term, not a complete system energy.
    """

    if beta <= 0.0:
        raise ValueError("matter coupling beta must be positive")
    if target_acceleration_m_s2 <= 0.0:
        raise ValueError("target acceleration must be positive")
    if field_span_m <= 0.0:
        raise ValueError("field span must be positive")

    # A real body also has a positive interior field. Omitting it makes this
    # only an optimistic lower floor, consistent with the rest of E-020.
    optimistic_field_floor_ev = (
        2.0 * beta * REDUCED_PLANCK_MASS_EV * body.compactness()
    )
    field_excursion_ev = (
        REDUCED_PLANCK_MASS_EV
        * target_acceleration_m_s2
        * field_span_m
        / (beta * C**2)
    )
    gradient_ev2 = field_excursion_ev * HBAR_C_EV_M / field_span_m
    gradient_energy_density_j_m3 = (
        0.5 * gradient_ev2**2 * EV_J / HBAR_C_EV_M**3
    )
    return {
        "optimistic_field_floor_to_unscreen_ev": optimistic_field_floor_ev,
        "required_field_excursion_ev": field_excursion_ev,
        "canonical_gradient_energy_density_j_m3": gradient_energy_density_j_m3,
    }


def two_body_scalar_acceleration_m_s2(
    beta: float,
    source: Body,
    target: Body,
    ambient_field_ev: float,
    separation_m: float,
) -> float:
    """Return the long-range spherical two-body chameleon acceleration.

    The standard thin-shell result is

      a_phi = 2 beta^2 q_source q_target G M_source / r^2.

    The Yukawa range factor is omitted, so this is optimistic whenever the
    source-target distance is not short compared with the field range.
    """

    if separation_m < source.radius_m + target.radius_m:
        raise ValueError("source and target spheres must not overlap")
    source_charge = thin_shell_charge(beta, source, ambient_field_ev)
    target_charge = thin_shell_charge(beta, target, ambient_field_ev)
    return (
        2.0
        * beta**2
        * source_charge
        * target_charge
        * G
        * source.mass_kg
        / separation_m**2
    )


def two_body_acceleration_ceiling_m_s2(
    target: Body,
    ambient_field_ev: float,
    source_radius_m: float,
    separation_m: float,
) -> float:
    """Return the fixed-background spherical thin-shell ceiling.

    Writing ``G M_source = Phi_source R_source c^2`` and applying the
    thin-shell charge to both bodies gives

      beta*q_source*Phi_source <= phi_bg/(2 M_Pl)
      beta*q_target            <= phi_bg/(2 M_Pl Phi_target).

    Their product bounds the pair acceleration for every positive ``beta``
    within this shared-background, passive, long-range benchmark.
    """

    if ambient_field_ev <= 0.0:
        raise ValueError("ambient field must be positive")
    if source_radius_m <= 0.0:
        raise ValueError("source radius must be positive")
    if separation_m < source_radius_m + target.radius_m:
        raise ValueError("source and target spheres must not overlap")

    return (
        C**2
        * ambient_field_ev**2
        * source_radius_m
        / (
            2.0
            * REDUCED_PLANCK_MASS_EV**2
            * target.compactness()
            * separation_m**2
        )
    )


def body_screening_case(
    body: Body,
    chamber_scale_m: float,
    beta: float = 1.0,
    lambda_ev: float = 2.4e-3,
    power_n: float = 1.0,
    geometry_factor: float = 1.0,
    excursion_fraction: float = 1.0,
    gradient_scale_m: float | None = None,
    target_g: float = 0.01,
) -> dict[str, float | str]:
    """Build one optimistic body-loading case and its saturation bound."""

    if not 0.0 < excursion_fraction <= 1.0:
        raise ValueError("excursion fraction must be in (0, 1]")
    if target_g <= 0.0:
        raise ValueError("target g fraction must be positive")
    if chamber_scale_m < body.radius_m:
        raise ValueError("the body proxy must fit inside the chamber scale")

    gradient_scale = chamber_scale_m if gradient_scale_m is None else gradient_scale_m
    field_ev = chamber_field_ev(
        chamber_scale_m,
        lambda_ev=lambda_ev,
        power_n=power_n,
        geometry_factor=geometry_factor,
    )
    compactness = body.compactness()
    beta_at_screening = field_ev / (
        2.0 * REDUCED_PLANCK_MASS_EV * compactness
    )
    charge = thin_shell_charge(beta, body, field_ev)
    acceleration = scalar_acceleration_m_s2(
        beta,
        charge,
        excursion_fraction * field_ev,
        gradient_scale,
    )

    # Above beta_at_screening, q is proportional to 1/beta, so beta*q and the
    # body acceleration saturate while the chamber background and excursion
    # are held fixed. Evaluating at the transition gives the passive-model
    # ceiling.
    saturated_acceleration = scalar_acceleration_m_s2(
        beta_at_screening,
        1.0,
        excursion_fraction * field_ev,
        gradient_scale,
    )
    target_acceleration = target_g * STANDARD_GRAVITY_M_S2
    max_unscreened_pair_force_ratio = 2.0 * beta_at_screening**2
    source_mass_equivalent_separation_m = 1.0
    no_source_screening_mass_equivalent = (
        target_acceleration * source_mass_equivalent_separation_m**2
        / (max_unscreened_pair_force_ratio * G)
    )
    # Use a body-fitting adjacent source for the reported finite geometry: a
    # half-scale source plus the target fit within a two-L cabin diameter in
    # the default human benchmark.
    adjacent_source_radius = 0.5 * gradient_scale
    adjacent_source_separation = adjacent_source_radius + body.radius_m
    adjacent_source_max_unscreened_mass = (
        compactness * adjacent_source_radius * C**2 / G
    )
    adjacent_source_pair_ceiling = two_body_acceleration_ceiling_m_s2(
        body,
        field_ev,
        source_radius_m=adjacent_source_radius,
        separation_m=adjacent_source_separation,
    )
    driven_requirement = externally_driven_unscreened_requirement(
        beta,
        body,
        target_acceleration,
        gradient_scale,
    )

    return {
        "body": body.label,
        "body_mass_kg": body.mass_kg,
        "body_radius_m": body.radius_m,
        "body_compactness": compactness,
        "chamber_scale_m": chamber_scale_m,
        "gradient_scale_m": gradient_scale,
        "lambda_ev": lambda_ev,
        "power_n": power_n,
        "geometry_factor": geometry_factor,
        "ambient_field_ev": field_ev,
        "beta": beta,
        "beta_at_screening_transition": beta_at_screening,
        "chamber_scale_to_unscreen_at_selected_beta_m": (
            chamber_scale_to_unscreen_body_m(
                beta,
                body,
                lambda_ev=lambda_ev,
                power_n=power_n,
                geometry_factor=geometry_factor,
            )
        ),
        "scalar_charge": charge,
        "acceleration_m_s2": acceleration,
        "saturated_acceleration_m_s2": saturated_acceleration,
        "target_acceleration_m_s2": target_acceleration,
        "target_to_saturated_ratio": target_acceleration / saturated_acceleration,
        "max_unscreened_pair_force_ratio_at_body_transition": (
            max_unscreened_pair_force_ratio
        ),
        "no_source_screening_mass_equivalent_at_1m_kg": (
            no_source_screening_mass_equivalent
        ),
        "adjacent_source_radius_m": adjacent_source_radius,
        "adjacent_source_center_separation_m": adjacent_source_separation,
        "adjacent_source_max_unscreened_mass_at_body_transition_kg": (
            adjacent_source_max_unscreened_mass
        ),
        "adjacent_source_two_body_acceleration_ceiling_m_s2": (
            adjacent_source_pair_ceiling
        ),
        **driven_requirement,
    }


def default_sweep(
    body: Body,
    beta: float,
    lambda_ev: float,
    power_n: float,
    geometry_factor: float,
    excursion_fraction: float,
    target_g: float,
) -> list[dict[str, float | str]]:
    base_scale = max(1.0, body.radius_m)
    return [
        body_screening_case(
            body,
            chamber_scale_m=scale,
            beta=beta,
            lambda_ev=lambda_ev,
            power_n=power_n,
            geometry_factor=geometry_factor,
            excursion_fraction=excursion_fraction,
            target_g=target_g,
        )
        for scale in (base_scale, 10.0 * base_scale, 100.0 * base_scale)
    ]


def _format_table(rows: list[dict[str, float | str]]) -> str:
    lines = [
        "L (m)   phi_bg (eV)   beta_screen   a_body,max (m/s^2)   target/max",
        "-----   -----------   -----------   ------------------   ----------",
    ]
    for row in rows:
        lines.append(
            f"{float(row['chamber_scale_m']):5.1f}   "
            f"{float(row['ambient_field_ev']):11.3e}   "
            f"{float(row['beta_at_screening_transition']):11.3e}   "
            f"{float(row['saturated_acceleration_m_s2']):18.3e}   "
            f"{float(row['target_to_saturated_ratio']):10.3e}"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--body-mass-kg", type=float, default=70.0)
    parser.add_argument("--body-radius-m", type=float, default=0.3)
    parser.add_argument("--body-label", default="70 kg human-scale sphere")
    parser.add_argument("--beta", type=float, default=1.0)
    parser.add_argument("--lambda-ev", type=float, default=2.4e-3)
    parser.add_argument("--power-n", type=float, default=1.0)
    parser.add_argument("--geometry-factor", type=float, default=1.0)
    parser.add_argument("--excursion-fraction", type=float, default=1.0)
    parser.add_argument("--target-g", type=float, default=0.01)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    body = Body(args.body_label, args.body_mass_kg, args.body_radius_m)
    rows = default_sweep(
        body,
        beta=args.beta,
        lambda_ev=args.lambda_ev,
        power_n=args.power_n,
        geometry_factor=args.geometry_factor,
        excursion_fraction=args.excursion_fraction,
        target_g=args.target_g,
    )

    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return

    print("E-020 canonical chameleon body-screening bound")
    print(f"Body proxy: {body.label}; compactness={body.compactness():.3e}")
    print(
        "Assumption: the full chamber field excursion occurs over the chamber "
        "scale; geometry factor is deliberately optimistic."
    )
    print(_format_table(rows))
    reference_case = rows[0]
    print(
        f"At beta={args.beta:g}, this chamber model would need L~"
        f"{float(reference_case['chamber_scale_to_unscreen_at_selected_beta_m']):.3e} m "
        "to keep the selected body unscreened."
    )
    print(
        f"For the {float(reference_case['chamber_scale_m']):g} m reference case, "
        "requiring the body to remain unscreened limits a "
        "fully unscreened source-target fifth force to "
        f"{float(reference_case['max_unscreened_pair_force_ratio_at_body_transition']):.3e} "
        "times Newtonian gravity. Ignoring the fact that a source of the needed "
        "mass would screen itself, the corresponding 1 m source-mass equivalent "
        f"is {float(reference_case['no_source_screening_mass_equivalent_at_1m_kg']):.3e} kg."
    )
    print(
        "An independent non-overlapping two-body thin-shell benchmark, with "
        f"source radius {float(reference_case['adjacent_source_radius_m']):.3g} m "
        "and center separation "
        f"{float(reference_case['adjacent_source_center_separation_m']):.3g} m, "
        "is bounded by "
        f"{float(reference_case['adjacent_source_two_body_acceleration_ceiling_m_s2']):.3e} m/s^2. "
        "At the body's screening transition, that source can remain unscreened "
        "only up to "
        f"{float(reference_case['adjacent_source_max_unscreened_mass_at_body_transition_kg']):.3e} kg."
    )
    print(
        "A formal externally driven, fully unscreened alternative at the selected "
        f"beta would require an optimistic field floor phi~{float(reference_case['optimistic_field_floor_to_unscreen_ev']):.3e} eV "
        "throughout the body plus a field excursion "
        f"Delta(phi)~{float(reference_case['required_field_excursion_ev']):.3e} eV "
        "before restoring the body's interior field. No scalar actuator or "
        "complete reaction/EFT budget is supplied by this model."
    )
    print(
        "Interpretation: above beta_screen the body's thin-shell charge falls "
        "as 1/beta, so stronger coupling does not raise the body acceleration "
        "within the fixed-background passive-cavity approximation."
    )


if __name__ == "__main__":
    main()

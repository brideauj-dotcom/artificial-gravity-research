# E-019 Conserved Cavity Model

This model asks a narrow question: after the field, cavity walls, energy
reservoirs, and recoil are included, can an internal electromagnetic energy
fluctuation remain visible outside the apparatus as a changing gravitational
monopole?

The first version is a weak-field, one-dimensional `T00` screen. It is not a
full general-relativistic cavity solution and does not claim a detectable
effect. Its purpose is to expose the conservation bookkeeping before adding
the full stress tensor.

## Scenarios

1. **Field only:** puts `delta E` in the cavity and intentionally omits its
   source. This reproduces the optimistic compact-energy estimate
   `delta a = -G delta E/(c^2 r^2)`.
2. **Closed cavity:** moves energy from wall-localized reservoirs into the
   field while enforcing `sum(delta E)=0` and `sum(x delta E)=0`. The exterior
   monopole and dipole disappear, so the first surviving scalar term is the
   quadrupole, proportional to `r^-4` in acceleration.
3. **Emitted pulse with recoil:** follows an outgoing pulse before absorption.
   The pulse momentum `E/c` displaces the source support by
   `delta x=-Et/(Mc)`. That recoil restores center-of-energy conservation and
   again removes the dipole to first order.

Run the default comparison:

```bash
python3 models/e019_conserved_cavity.py
```

Change the source and geometry or emit machine-readable output:

```bash
python3 models/e019_conserved_cavity.py \
  --energy-j 1000 \
  --length-m 0.1 \
  --probe-m 2 \
  --loss-distance-m 0.1 \
  --json
```

Run the verification suite:

```bash
python3 -m unittest discover -s tests -v
```

## Divergence-Free Tensor Extension

`e019_conserved_tensor.py` advances the scalar screen to a compact harmonic
line source with

`tau00=P''`, `tau0x=i(omega/c)P'`, and `tauxx=-(omega/c)^2 P`.

This construction satisfies both nontrivial components of
`partial_mu T^{mu nu}=0`. The solver propagates all three components with the
retarded 3+1 dimensional Green function, checks `partial_mu bar(h)^{mu nu}=0`,
and evaluates the gauge-invariant `R_0x0x` tidal component. It also projects the
E-018 coherent/squeezed photon-number noise model through the resulting tidal
transfer function.

```bash
python3 models/e019_conserved_tensor.py
```

The default `1 J`, `1 cm`, `100 MHz`, `1 m` case gives a tidal-gradient
amplitude near `2.04e-31 s^-2`. The corresponding `1550 nm`, `N=4.5`,
`kappa/2pi=100 MHz` squeezed-vacuum relative-acceleration noise is about
`1.04e-53 m/s^2/sqrt(Hz)` over a `1 m` baseline. A close exterior probe at
`x=6 mm` with a `0.1 mm` baseline remains only about
`2.57e-46 m/s^2/sqrt(Hz)`.

## Equations represented

For signed point-energy perturbations on the positive exterior axis,

`delta a_x(r) = -(G/c^2) sum_i delta E_i/(r-x_i)^2`.

Expanding outside the source gives

`delta a_x(r) = -(G/c^2) sum_n (n+1) I_n/r^(n+2)`,

where `I_n=sum_i delta E_i x_i^n`. Closing the energy ledger sets `I_0=0`.
Keeping the center of energy fixed sets `I_1=0`. The scalar exterior response
therefore starts with `I_2/r^4` unless symmetry removes that term too.

## Important Limits

- The original scalar model remains a useful conservation/multipole screen,
  but it does not include tensor stress or retarded propagation.
- The tensor model is an effective total-apparatus perturbation. It contains
  energy density, longitudinal energy flow, and longitudinal stress, but does
  not yet decompose them into a microscopic optical field, mirrors, springs,
  pump, loss port, and absorber.
- The source is a one-dimensional line distribution embedded in 3+1
  dimensions, not a finite-radius three-dimensional cavity.
- High-frequency enhancement is not free: the required integrated stress grows
  as `(omega L/c)^2`. Frequency cases with stress budgets larger than the
  energy scale are not evidence for a gravity loophole.
- Signed wall energies are perturbations relative to a baseline, not negative
  material mass.
- The recoil calculation is first order in `E/(Mc^2)`.
- A microscopic apparatus decomposition is justified only if it can change the
  conserved tidal transfer by orders of magnitude; the present source scale is
  otherwise already decisive for detectability.

## Primary-source anchors

- D. Ratzel, M. Wilkens, and R. Menzel, “Gravitational properties of light -
  The gravitational field of a laser pulse,” arXiv:1511.01023. Its explicit
  emitter/pulse/absorber treatment motivates keeping the whole source history.
- N. G. Phillips and B. L. Hu, “Noise Kernel in Stochastic Gravity and Stress
  Energy Bi-Tensor of Quantum Fields in Curved Spacetimes,”
  arXiv:gr-qc/0010019. This anchors the connected stress-tensor correlation as
  the stochastic source object.
- J. Gratus, P. Pinto, and S. Talaganis, “The Distributional Stress-Energy
  Quadrupole,” arXiv:2005.02688. This is a warning that a real stress-energy
  quadrupole contains structure that a scalar point model cannot determine.

# E-020 Chameleon Body-Screening Bound

`e020_chameleon_body_screening.py` tests a different route: a hypothetical
matter-coupled scalar that changes the force law rather than sourcing ordinary
Einstein gravity. It specializes to the canonical inverse-power chameleon

`V(phi)=Lambda^(4+n)/phi^n`,

with universal conformal coupling `beta/M_Pl`. The chamber-limited field is
estimated by setting its effective Compton wavelength equal to the chamber
scale `L`,

`phi_bg ~= [n(n+1) Lambda^(4+n) L^2]^(1/(n+2))`,

and a homogeneous spherical body receives the standard thin-shell charge

`q = min[1, phi_bg/(2 beta M_Pl Phi_body)]`,

where `Phi_body=GM/(Rc^2)`. The resulting acceleration is

`a_phi ~= beta q c^2 Delta(phi)/(M_Pl ell)`.

The script also evaluates the independent two-body form

`a_phi = 2 beta^2 q_source q_target G M_source/r^2`.

Applying the thin-shell inequality to both bodies gives a fixed-background,
spherical benchmark ceiling that is independent of `beta` within those
assumptions:

`a_phi <= c^2 phi_bg^2 R_source/(2 M_Pl^2 Phi_target r^2)`.

Algebraically, the point-target choice `R_source=r=ell` is identical to the
chamber-gradient ceiling. Finite non-overlapping bodies require
`r >= R_source + R_target` and therefore sit below that identity. Source
screening still reproduces the same order of scale without assuming a
specific smooth field profile.

Once the body is screened, `q` falls as `1/beta`; stronger coupling therefore
does not increase its acceleration. With the deliberately optimistic choices
`Lambda=2.4 meV`, `n=1`, `Delta(phi)=phi_bg`, and `ell=L`, a `70 kg`, `0.3 m`
homogeneous body in a `1 m` chamber saturates near `1.12e-13 m/s^2`, about
`8.8e11` below `0.01g`. Inverting the same deliberately optimistic chamber
estimate shows that keeping that body unscreened at `beta=1` would require a
chamber scale of roughly `1.2e4 m`; published geometry coefficients below one
push the scale into the tens-of-kilometres range. Conversely, requiring the
body to remain unscreened in the `1 m` case limits the coupling to
`beta~1.9e-3`; even if both source and body were unscreened, their scalar force
would then be at most `~7.2e-6` of the source's Newtonian attraction. Ignoring
source screening converts `0.01g` at `1 m` to a `~2.0e14 kg` mass-equivalent;
this is explicitly counterfactual, because a source that massive is deeply
screened. The fixed-radius two-body ceiling, not that mass-equivalent, is the
self-consistent benchmark. For example, at the human proxy's screening
transition, a `0.5 m`-radius source just touching the proxy at `0.8 m` center
separation can remain unscreened only up to `~117 kg`; its scalar acceleration
is then `~8.74e-14 m/s^2`, exactly the non-overlapping pair ceiling.

The script also quantifies an algebraic escape from the passive-cavity bound:
assume a separate actuator keeps the body unscreened and imposes the needed
gradient. At `beta=1`, a `0.01g` field across `1 m` needs a scalar excursion of
`~2.66 GeV` while maintaining an optimistic field floor of `~844 eV`; the
latter neglects the positive field inside the human proxy and is therefore
only a lower bound on full unscreening. The canonical gradient term alone is
`~2.9e6 J/m^3`, but
that is not a system budget: no known scalar actuator, hull-penetration model,
reaction ledger, backreaction solution, or experimentally allowed EFT is
provided. This is a new-source assumption, not an engineering proposal.

Run the default body-fitting `1-100 m` chamber sweep for the human proxy:

```bash
python3 models/e020_chameleon_body_screening.py
```

Emit machine-readable output or change the body/model proxy:

```bash
python3 models/e020_chameleon_body_screening.py \
  --body-mass-kg 1 \
  --body-radius-m 0.1 \
  --body-label "1 kg payload" \
  --json
```

## E-020 limits

- This is an optimistic scaling bound, not a finite-element chamber solution.
- The dense-body field is neglected relative to `phi_bg`; including it lowers
  the available field excursion.
- A human is represented as a homogeneous sphere. Anatomical porosity can
  change its detailed scalar charge, but then different components no longer
  receive a universal gravity-like acceleration.
- Gradients sharper than the chosen scale can increase a local surface force,
  but not a uniform body-scale field; they reintroduce severe spatial
  variation and tidal/loading problems.
- The field, potential, and coupling are hypothetical. The calculation does
  not assert that a chameleon exists, and the canonical dark-energy model is
  already excluded by laboratory null tests.
- The pair ceiling assumes passive approximately spherical bodies sharing a
  fixed chamber-limited background, canonical positive-field thin-shell
  behavior, and a long-range interaction. It is not a model-independent bound
  on actively driven or arbitrary scalar fields.

## E-020 primary-source anchors

- J. Khoury and A. Weltman, “Chameleon Fields: Awaiting Surprises for Tests of
  Gravity in Space,” arXiv:astro-ph/0309300, for the effective potential and
  thin-shell result.
- C. Burrage et al., “The shape dependence of chameleon screening,”
  arXiv:1711.02065, for chamber saturation and the modest source-shape gain.
- P. Yin et al., “Experiments with levitated force sensor challenge theories
  of dark energy,” arXiv:2405.09791 / Nature Physics 18, 1181 (2022), for the
  canonical-model null result.
- C. D. Panda et al., “Measuring gravitational attraction with a lattice atom
  interferometer,” arXiv:2310.01344 / Nature 631, 515 (2024), for the
  `13 nm/s^2` anomalous-acceleration upper limit on an atomic probe.

# E-021 Finite Planar Cubic-Galileon Screen

`e021_galileon_planar_screen.py` asks whether the exactly de-screened infinite
plane remains useful when the source is made finite. It uses the canonical
quasistatic cubic equation

`laplacian(phi) + c3/Lambda^3 [(laplacian(phi))^2 - (d_i d_j phi)^2] = beta rho/M_Pl`.

For an exact plane the nonlinear invariant vanishes and

`a_phi = 4 pi G beta^2 Sigma/Z`.

The linear finite-disk field carries the usual axial shape factor

`f(z)=1-z/sqrt(z^2+R^2)`.

The model also directly integrates the off-axis thin-disk field and samples a
`3 x 3 x 3` cube, so the cabin-quality statement is not limited to the axis.

The model uses that field only as a reference and checks its consistency with

`epsilon_edge = c3 beta Sigma/(2 Lambda^3 M_Pl R) = (r_V/R)^3/4`.

An `epsilon_edge` much larger than one means that finite-edge curvature has
entered the nonlinear regime and the free disk result cannot be used as a
device prediction. It does not calculate the nonlinear force and is not a
strict upper bound: numerical annular-disk work has found local
anti-screening near a center hole.

It also implements the annular-disk paper's density parameter

`mu = beta rho_0/(Lambda^3 M_Pl)`.

For a uniform disk of thickness `h`, this and the edge diagnostic are linked
exactly by

`epsilon_edge = c3 mu h/(2R)`.

For the paper's thin spherical wedge, `h/(2R) ~= theta_0`, so the analogous
continuation coordinate is `chi=c3 mu theta_0`.

For an illustrative `0.10 m` thickness, the default target disk has
`mu=4.58e35`. The published annular enhancement became difficult to see above
roughly `mu=1e3` in that source family, so E-023 must reproduce the dilute
case and then density-continue it rather than assuming the enhancement reaches
material sources. The paper's favorable ratio peaks are only about `4-5`, and
the exact hole-center vector field is zero by symmetry; absolute force and
usable-volume gradients, not the nonlinear/linear ratio alone, are decisive.

The default case puts a `2 m`-deep target volume `2 m` from the source and
requires `+/-10%` axial uniformity. It finds `R=11.723 m`. The free `beta=1`
reference for scalar `0.01g` needs `Sigma=1.406e8 kg/m^2` and
`M=6.069e10 kg`, while the same matter supplies `0.005g` of Newtonian
acceleration. The cube-sampled field magnitude spans `0.9036-1.1012` times the
center value and its maximum lateral component is `0.0722` times the center
field. A radius near `11.85 m` brings all `27` sampled cabin points within
`+/-10%`, only a `~2%` mass correction; this is not a continuous-volume
extremum proof. For `Lambda=1.758e-13 eV`, the disk has
`epsilon_edge=1.955e33`. The Earth-background factor is
`Z_Earth=2.19e15`. Literal fixed-target scaling would require `1.33e26 kg`
and therefore invalidate the small laboratory-perturbation premise; this is a
reductio, not a device prediction. The isolated-Sun check still gives
`Z=3.51e11` at `1 AU` and `3.51e8` at `100 AU`; nonlinear multi-source
backgrounds cannot be obtained by simply adding these factors. A conservative
published dressed plate limit
`beta/sqrt(Z)<0.05` raises the reference disk mass to `2.43e13 kg`, at which
point ordinary gravity is `200` times the scalar contribution.

The free surface density is also `6.22 km` of osmium-density material. Keeping
such material to `h/R=0.01` requires `R=622 km` and `1.71e20 kg`; keeping the
source `0.10 m` thick instead requires `rho=1.406e9 kg/m^3`.

The scalar-only target is intentional: it tests whether the new channel can
dominate the ordinary plate. If scalar and Newtonian fields are summed to total
`0.01g`, the masses are `1.214e11 kg` for Newtonian gravity alone,
`4.046e10 kg` for free `beta=1`, `1.046e11 kg` at the mapped galaxy limit, and
`1.208e11 kg` at the dressed plate limit. The constrained cases therefore
reproduce the positive-mass boundary.

As an independent conditional benchmark, mapping the galaxy/black-hole offset
limit `Delta G/G_N<0.16` through `Delta G/G_N=2 beta^2` gives `beta<0.283`.
That linear disk is `7.59e11 kg`, with ordinary gravity `6.25` times the scalar
target and `epsilon_edge=6.91e33`. The mapping is model-specific.

Run the report or emit JSON:

```bash
python3 models/e021_galileon_planar_screen.py
python3 models/e021_galileon_planar_screen.py --json
```

## E-021 limits

- The full nonlinear finite-disk PDE is not solved.
- A future nonlinear solve must monitor the principal matrix
  `A_ij=delta_ij+2(c3/Lambda^3)[(laplacian phi)delta_ij-d_i d_j phi]`;
  residual convergence after loss of ellipticity is not a physical branch.
- The published `mu~1e3` anti-screening turnover is geometry-specific, not a
  universal theorem; the model uses it only as a mandatory replication gate.
- The radius is chosen from the axial uniformity condition. The model then
  directly samples a `3 x 3 x 3` cabin grid, including lateral components, as
  a diagnostic rather than re-optimizing the source against the full volume.
- A spherical `r_V` is used only as a global diagnostic; the local edge index
  supplies the independent finite-geometry consistency check.
- The Earth factor assumes a locally radial plate perturbation in a pure cubic
  spherical background. Other orientations change order-one coefficients.
- In the minimal cubic estimate, the bare `H0^-1` cutoff wavelength is
  `1.12e6 m`, so the free `Z=1` meter-scale reference is not a controlled
  minimal-EFT cabin prediction. A demonstrated Earth kinetic background lowers
  the estimate to `2.40 cm` (`1.37 cm` at the `150 Mpc` benchmark),
  conditionally restoring control for smooth meter-scale profiles. Physical
  source edges below the applicable local cutoff are not resolved predictions
  of the EFT.
- The `150 Mpc` LLR number is a published benchmark with nonlinear
  Sun-Earth-Moon/model caveats, not an exact universal bound.
- The field is hypothetical, and no ultraviolet completion or scalar actuator
  is supplied.
- Internal forces conserve total momentum and cannot propel a closed craft.

## E-021 primary-source anchors

- J. K. Bloomfield, C. Burrage, and A.-C. Davis,
  “The Shape Dependence of Vainshtein Screening,” arXiv:1408.4759.
- P. Brax, C. Burrage, and A.-C. Davis, “Laboratory Tests of the Galileon,”
  arXiv:1106.1573.
- H. Ogawa, T. Hiramatsu, and T. Kobayashi, “Anti-screening of the Galileon
  force around a disk center hole,” arXiv:1802.04969.
- L. Hui and A. Nicolis, “An Equivalence Principle for Scalar Forces,”
  arXiv:1009.2520.
- T. Hiramatsu et al., “Equivalence Principle Violation in Vainshtein Screened
  Two-Body Systems,” arXiv:1209.3364.

# E-023 Annular Cubic-Galileon Replication

`e023_galileon_annulus.py` independently solves the dimensionless static
cubic-Galileon equation used by Ogawa, Hiramatsu, and Kobayashi for a thin
spherical annular wedge. It implements the mapped, cell-centred spherical grid
documented in Ogawa's later thesis,

`r = chi + 0.2 chi^3/3`,

the paper's lagged-nonlinearity Poisson iteration, and its `omega=0.01`
under-relaxation. The default source uses exact cell-volume overlap fractions;
`--source-discretization cell_center` preserves the likely published
Heaviside-at-grid-point convention for replication comparisons.

The artifact deliberately reports more than the published force ratio:

- the exact centre force is zero and its nonlinear/linear ratio is `null`;
- the nonlinear residual is reported in conservative algebraic, maximum, and
  physical cell-volume-weighted norms;
- the minimum spatial principal coefficient, its location, and the time
  kinetic coefficient test the candidate branch;
- absolute dimensionless gradients are translated conditionally to density,
  source mass, acceleration, target force, and equal-opposite source reaction;
- both the arXiv caption ray `theta=2pi/5` and the thesis-corrected ray
  `theta=pi/10` are retained.

At the published `200 x 100` resolution, the likely cell-centre source
represents only `0.9372` of the nominal wedge volume. Exact overlap fractions
remove that mass drift. The resolved ratio at `r/r0=1` clusters near `3.3` but
spans roughly `3.15-3.38` over the widest stopping/angular checks. Exact-volume
absolute-gradient peaks are `11.774`, `11.786`, and `11.788` on `200 x 100`,
strict `400 x 200`, and `400 x 400`, only `0.12%` total drift. The nominal
near-origin ratio maximum remains grid- and stopping-tolerance-sensitive.
Strict `400 x 200` cell-centre/exact-volume runs reach algebraic residuals
`1.47e-4`/`1.06e-4` with positive spatial/time principal signs. This reproduces
the local anti-screening effect without certifying a precision ratio peak or
engineering usefulness.

For the conditional cosmological choice `M=Lambda=1.758e-13 eV`, `beta=1`, and
`r0=1 m`, the nominal source density is only `1.13e-25 kg/m^3`, its mass is
`6.26e-22 kg`, and the full sampled-ray acceleration peak is only about
`6e-35 m/s^2`. Naively scaling `r0` at fixed dimensionless/cosmological
parameters to `0.01g` gives `r0~1.62e33 m` and source mass `~2.64e78 kg`; that
extrapolation invalidates the flat/static model and is only a reductio. These
are scale translations of a hypothetical field equation, not a detected field
or an artificial-gravity design.

Install the research-only numerical dependencies and run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-research.txt
.venv/bin/python models/e023_galileon_annulus.py
.venv/bin/python models/e023_galileon_annulus.py --json
.venv/bin/python models/e023_galileon_annulus.py --source-discretization cell_center
```

## E-023 limits

- The original source, outer ghost convention, mixed derivative, and linear
  solver are incompletely documented; this is an independent replication, not
  the authors' code.
- The paper's relative-update threshold can be met while the conservative
  algebraic PDE residual and innermost-cell principal sign still fail. A small
  update under strong under-relaxation is not by itself a residual certificate.
- The discontinuous thin wedge is under-resolved at the published angular
  grid. Exact overlap fractions fix integrated source mass, not interface
  convergence. E-024 supplies the smooth-source check; E-025 still requires a
  genuinely independent wide-stencil or different-coordinate 2-Hessian solve.
- The exact centre is `0/0` in a force ratio, and the raw first-shell maximum is
  sensitive to resolution. Resolved ratios and absolute force profiles are the
  defensible observables.
- This stage does not continue to material density, add asymmetry, include a
  nonlinear target, or establish EFT control. Internal forces cannot propel a
  closed system reactionlessly.

# E-024 Smooth Annulus And Shifted-2-Hessian Validation

`e024_galileon_continuation.py` replaces the discontinuous E-023 wedge with a
positive, compact `C2` quintic source. It integrates the source in the natural
volume coordinates `r^3` and `sin(theta)` and renormalizes the profile so its
total scalar charge exactly equals the sharp wedge's value. It then compares:

1. the original mapped-grid Picard/Poisson formulation; and
2. an independently coded source-amplitude continuation of the exact shifted
   2-Hessian equation in `e024_shifted_2hessian.py`.

For

`Delta(phi) + c3 [Delta(phi)^2 - Hess(phi):Hess(phi)] = S`,

the shift

`u = phi + |x|^2/(8 c3)`

gives

`sigma2(D2 u) = 3/(16 c3^2) + S/(2 c3)`.

The shifted solver stores `phi` and adds `I/(4 c3)` to its Hessian
analytically. This avoids subtracting a large quadratic field when recovering
the physical gradient. Damped Newton--Krylov steps follow the source amplitude
from zero to one and reject trial steps unless the residual decreases and the
spatial principal, time kinetic, and local `sigma2` signs stay positive.

The Galileon spatial principal matrix is exactly twice `c3` times the first
Newton tensor of the shifted Hessian. Its three eigenvalues are

`2 c3 (kappa_j + kappa_k)`,

where the `kappa` values are shifted-Hessian eigenvalues. Thus positive
principal signs are the 2-Hessian admissibility condition on an exact
positive-source solution. The code also checks the divergence current

`J_i = phi_i + c3 [(Delta phi) phi_i - phi_ij phi_j]`,

so shell flux must approach the volume-integrated source under refinement.
The shifted formulation supplies an algebraically different current and both
surface integrals are reported.

## 2026-07-15 validation campaign

For the fiducial `mu=36.8` annulus and a fixed broad smooth layer
`(w_r,w_theta)=(6,0.10)`, the shifted normal-branch results were:

| Grid | Transition cells inner/outer/angular | Ratio at `r/r0=1` | Absolute gradient peak | Max shell-flux error | Minimum spatial principal |
| --- | ---: | ---: | ---: | ---: | ---: |
| `80 x 40` | `13 / 6 / 3` | `3.43284` | `11.7121` | `1.078%` | `0.00298` |
| `120 x 60` | `19 / 8 / 4` | `3.40718` | `11.7372` | `0.490%` | `0.00398` |
| `200 x 100` | `31 / 12 / 7` | `3.40669` | `11.7523` | `0.188%` | `0.00616` |

Only the `200 x 100` broad case spans at least six local cell widths across
every transition: its minimum is `6.37` in the angular layer. Narrowing to the
`(4,0.08)` layer gives only `5.09` angular cells per width, so it is a stress
test rather than a passing resolution case. It gives ratio `3.37962`, absolute
peak `11.7683`, flux error `0.229%`, and global minimum spatial-principal value
`0.00643`. Relative to the broad case, the stress-test drift is about `0.8%`
in ratio and `0.14%` in absolute peak.

A near-fixed-central-resolution box screen gives:

| `rmax` | Radial cells | Ratio at `r/r0=1` | Absolute peak |
| ---: | ---: | ---: | ---: |
| `40` | `62` | `3.04574` | `10.9345` |
| `80` | `80` | `3.43284` | `11.7121` |
| `160` | `103` | `3.45812` | `11.7541` |

The `rmax=40` box is too close, while `80` and `160` agree to about `0.74%` in
the resolved ratio and `0.36%` in the absolute peak at this coarse angular
resolution.

The fine broad-source shifted solve reaches original-equation relative
residual `1.21e-7`, keeps the time coefficient above one, and closes shell
flux to `0.19%`. The Picard field agrees with it at about `2e-9` in
volume-weighted field norm and `3e-7` in gradient norm, but the Picard update
stop still leaves an unweighted algebraic residual `1.09e-3`. Its
volume-weighted residual is only `9.3e-7`, showing that small-volume near-origin
cells can fail the conservative algebraic gate while barely moving the global
field. The global spatial-principal minimum `0.00616` occurs in the first
radial/equatorial cell at `(r,theta)=(0.0254,0.00785)`; excluding one boundary
layer raises it to `0.01282`. The report records both. This is a
coordinate-boundary/stencil warning, not by itself a condition estimate or
physical near-degeneracy claim.

Run a quick paired smoke validation with:

```bash
.venv/bin/python models/e024_galileon_continuation.py
.venv/bin/python models/e024_galileon_continuation.py --json
```

The quick default intentionally does not satisfy the six-cell source gate. The
final broad passing case and narrower five-cell stress test are reproducible
with:

```bash
.venv/bin/python models/e024_galileon_continuation.py --radial-cells 200 --angular-cells 100 --radial-smoothing-width 6 --angular-smoothing-width 0.10 --json
.venv/bin/python models/e024_galileon_continuation.py --radial-cells 200 --angular-cells 100 --radial-smoothing-width 4 --angular-smoothing-width 0.08 --json
```

The `rmax` screen used `(--radial-max, --radial-cells)=(40,62),(80,80),
(160,103)` with `40` angular cells and the broad `(6,0.10)` source. Those
coarse angular runs are box diagnostics only; they do not satisfy the final
source-resolution gate.

## E-024 limits

- The smooth annular enhancement survives the present grid, width, box, flux,
  and two-solver checks. This supports a conditional dimensionless PDE result,
  not a useful absolute field; the E-023 cosmological translation remains only
  about `6e-35 m/s^2` for `r0=1 m`.
- The shifted and original equations are exactly related. Re-evaluating both
  with one discrete Hessian is a scaled algebraic identity, not an independent
  continuum proof. E-024 uses separately coded derivatives and nonlinear
  solvers, but both still use the same mapped-grid family.
- A monotone wide-stencil 2-Hessian solve with independent boundary treatment
  is still required. The accurate centered scheme is non-monotone, and the
  boundary-sensitive global principal minimum makes location-aware diagnostics
  important.
- The Picard relative-update criterion remains insufficient even after source
  smoothing. Residual, flux, and admissibility gates must be retained.
- Material-density continuation, controlled asymmetry, target backreaction,
  EFT/UV validity, and source/support reaction remain gated. Natural or
  pseudo-arclength continuation may not be used to legitimize a branch after
  loss of ellipticity.

# E-025 Independent Axisymmetric Wide-Directional 2-Hessian Gate

`e025_axisymmetric_wide_2hessian.py` begins the genuinely independent
discretization required by E-024. It represents the axisymmetric Hessian by
wide primitive directions in the `(rho,z)` meridional plane plus a separately
constructed azimuthal curvature. It evaluates the globally monotone extension
of `sigma2` and does not import E-023/E-024's mapped-spherical grid, centered
Hessian, source array, residual, gradient, flux, or solver.

The domain is a nodal meridional quarter-disk with reflection at both symmetry
axes and Dirichlet data injected at exact line-circle intersections. Unequal
forward/backward distances retain nonnegative neighbor weights and are exact
for quadratics. The azimuthal curvature uses an outward circular chord that
reduces to the even-axis radial second difference at `rho=0`. The fixed broad
source is rebuilt continuously in cylindrical coordinates, normalized to
charge `204067.868812537`, and checked with an independent
`4 pi rho d rho d z` nodal quadrature rather than grid-fitted renormalization.

For ordered directional curvatures `x<=y<=z`, the monotone extension uses

`xy+xz+yz` when `x+y>=0`, and `-x^2` otherwise.

Thus the inadmissible triple `(-5,-5,1)` is not allowed to pass merely because
its raw `sigma2` equals `15`; the extension returns `-25`. The solver follows
the source amplitude with damped semismooth Newton-GMRES and accepts steps only
when residual, pair-sum, and time-kinetic checks remain healthy.

Run the focused checks and provisional smoke solve with:

```bash
.venv/bin/python -m unittest tests.test_e025_axisymmetric_wide_2hessian -v
.venv/bin/python models/e025_axisymmetric_wide_2hessian.py
.venv/bin/python models/e025_axisymmetric_wide_2hessian.py --json
```

The smoke CLI uses only `56` unknowns and is deliberately not the annulus. It
reaches relative `L2/Linf` residuals `5.15e-9/6.84e-9`, minimum pair sum
`0.4940`, spatial principal `0.9880`, and time coefficient `1.00000017`.
Twenty-one focused tests cover exact shortened-boundary quadratics, a rotated
nonconvex admissible Hessian, nonlinear manufactured convergence, the invalid
branch trap, zero and small sources, source normalization/charge, directional
refinement, the fixed-direction plateau, active-ILU closure, completed and
interrupted mid-stage checkpoint/resume, source-fingerprint validation, and
inadmissible restart rejection.

## 2026-07-16 provisional actual-source checks

Two `rmax=80`, `mu=36.8` source-amplitude stress solves converged:

| `h,m` | Unknowns / bases | Nearest-frame error | Source cells | Charge error | Residual `L2 / Linf` | Minimum spatial / time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `1,1` | `5097 / 2` | `22.50 deg` | `0.8` | `-1.018%` | `6.44e-11 / 3.25e-10` | `0.02376 / 1.00033` |
| `0.5,2` | `20252 / 4` | `13.28 deg` | `1.6` | `-0.1024%` | `7.68e-10 / 5.59e-9` | `0.01804 / 1.00003` |

Both are under-resolved and neither reports an accepted force ratio or flux.
The minimum pair sum occurs at `(rho,z)=(5,0)` in the coarse checks. At fixed
`m=2`, a manufactured interior RMS error plateaus at approximately `1.41e-3`
under the last spatial refinement, while the coupled sequence
`(h,m)=(0.125,2),(0.0625,3),(0.03125,4)` continues from `3.03e-3` to
`1.38e-3` to `6.80e-4`. Boundary-inclusive coupled errors are not monotone yet.

Independent source-charge errors for `h=1,0.5,0.25,0.125` are `-1.018%`,
`-0.1024%`, `-0.006813%`, and `-0.0004316%`. The first six-cell level is
approximately `h=0.125`, with `322319` quarter-disk unknowns at `rmax=80`.
At the radial window's half-height (`r=8`), its `m=4` physical stencil still
reaches `0.625`, about `78%` of the full `0.8` angular transition, so six source
cells alone do not establish an
asymptotic result.

## 2026-07-17 diagnostic and refinement campaign

E-025 now evaluates the observables that the provisional roots lacked:

- a fixed-frame linear Poisson solution, explicitly labeled a cross-check;
- a separately evaluated bilinear/centered cylindrical Hessian and original/
  White normal-root residual with axis limits and an excluded outer band;
- a `theta=pi/10` nonlinear/linear force ray with a null center ratio;
- the exact divergence current integrated over three spherical shells;
- all-frame and active-frame pair-minimum locations; and
- an assembled active semismooth Jacobian plus a broad-annulus report driver.

The spherical flux is

`4 pi r^2 integral_0^(pi/2) cos(theta) (J dot n) dtheta`,

where `theta` is latitude from the equator. The `4 pi` factor restores both
signs of `z` and the full azimuth. Analytic quadratic tests verify the centered
Hessian, linear solve, White residual, and flux normalization. An exact action
test verifies that active Jacobian assembly preserves the previous matrix-free
operator. All `78` workspace tests pass.

At `R=80`, the unchanged `(h,m)=(0.5,2)` solve now takes `40.0 s`, down from
`78.1 s`, and gives:

| Quantity | Result |
| --- | ---: |
| sampled-charge error | `-0.102401%` |
| monotone residual `L2 / Linf` | `7.685e-10 / 5.590e-9` |
| pair / spatial / time minima | `0.0090199 / 0.0180397 / 1.000026` |
| force ratio at `r=1` | `2.60205` |
| maximum nonlinear gradient | `10.9761` |
| centered original / White residual | `2.9599% / 0.6131%` |
| shell-flux errors | `-4.008% / -4.354% / -4.500%` |

This point is still only `1.6` cells across the narrow source scale and is
materially away from E-024's `3.40669` ratio, `11.75234` peak, and `0.188%`
maximum shell-flux error. It is a convergence datum, not confirmation.

The exact `(0.25,3)` refinement has `80731` unknowns, eight bases, and source
charge error `-0.006813%`, but does not reach full source. At amplitude `5/12`,
Newton iteration `4`, GMRES exhausts the fixed cap with relative residual
`5.493e-6` after `4707` stage Krylov iterations. Pair, spatial, and time
margins remain positive at `0.02465`, `0.04931`, and `1.000004`; this is a
conditioning stop, not demonstrated branch loss. No fine force or flux is
reported. Raw full-source prolongation is also rejected because it can make a
fine-grid predictor inadmissible.

## 2026-07-18 active-ILUT and checkpoint campaign

The continuation solver can now write an atomic accepted-state checkpoint and
resume it after validating the grid, full discrete-operator and boundary-offset
digest, source digest, amplitude schedule, tolerances, and iteration caps. It
never serializes rejected trials, an ILU factor, or a Krylov basis. A loaded
field is checked against the all-frame pair and time-kinetic gates before the
residual convergence shortcut is allowed.

The Python API exposes the solver controls explicitly:

```python
solution = solve_continuation(
    system,
    source,
    continuation_steps=12,
    relative_tolerance=1.0e-7,
    newton_max_iterations=20,
    gmres_relative_tolerance=1.0e-8,
    gmres_max_iterations=40,
    preconditioner_kind="active_ilu",
    ilu_drop_tolerance=1.0e-3,
    ilu_fill_factor=10.0,
    checkpoint_path="e025-h025-m3.npz",
    resume_checkpoint=False,
)
```

Set `resume_checkpoint=True` with the same numerical problem to continue from
the last accepted field. Preconditioner kind and ILU options are stored as
provenance. They may change after a completed stage, or before any accepted
work in a newly entered stage, but not after an accepted correction in an
incomplete stage; this prevents mixed counters from being attributed to one
preconditioner. The physical source, discretization including boundary data,
continuation schedule, tolerances, and caps may not change.

At the former `5/12` failure state, the exact active Jacobian has approximately
`4.59e5` nonzeros for `80731` unknowns. The old zero-state Poisson
preconditioner exhausted all `2000` allowed inner iterations. Active ILUT gives:

| drop tolerance / fill factor | GMRES inner iterations | setup time | `L+U` nonzeros |
| --- | ---: | ---: | ---: |
| `1e-2 / 5` | `861` | `0.425 s` | `1.36e6` |
| `1e-3 / 10` | `478` | `0.675 s` | `3.07e6` |
| `1e-4 / 20` | `316` | `1.184 s` | `6.90e6` |

All three corrections take the full line-search step, reduce the nonlinear
residual from `5.493e-6` to about `4.59e-8`, and retain positive branch
margins. The middle setting is the current cost/fill compromise. It removes
the old wall but does not finish the campaign.

With the original `12` amplitudes and unchanged residual, branch, and Krylov
caps, active ILUT accepts stages through `11/12`. That checkpoint has pair /
spatial / time minima `0.0095666 / 0.0191332 / 0.9999972`. Its bounded
partial-source diagnostics are:

| Quantity | `11/12` result |
| --- | ---: |
| solver residual `L2 / Linf` | `7.93e-9 / 7.21e-8` |
| force ratio at `r=1` | `3.24984` |
| maximum nonlinear gradient | `10.4286` |
| centered original / White residual | `1.933% / 0.337%` |
| shell-flux errors | `-1.818% / -1.910% / -1.938%` |

These are not full-source E-025 observables. The first full-source corrector
still exhausts the `2000`-iteration cap, as do stronger ILUT and intermediate
targets `23/24` and `15/16`. Finite capped directions are not admitted: their
true linear residual ratios are `1.3565-1.5409`, so they fail the basic
inexact-Newton requirement `||F+Js||/||F||<1` even when heavy damping makes the
nonlinear residual decrease slightly.

The accepted state is preserved as
`checkpoints/e025_h025_m3_11of12.npz`; `checkpoints/README.md` records its
SHA-256, exact solver provenance, and the restrictions on interpreting it.

## 2026-07-19 E-026 nonsymmetric AMG closure

`e026_nonsymmetric_amg.py` reconstructs the saved `11/12` state without
rewriting it, assembles the exact active Jacobian, and benchmarks fixed
nonsymmetric AMG V-cycles under the original GMRES and nonlinear gates. It
requires `A=-J` to retain positive diagonals and nonpositive off-diagonals,
freezes each hierarchy during one GMRES call, computes the true unpreconditioned
linear residual, rejects positive `info`, and retains the all-frame
pair/spatial/time line-search conditions.

The saved matrix has `80731` rows and `458371` nonzeros. Its Frobenius
asymmetry ratio is `0.139018`. For `A=-J`, every diagonal is positive, every
off-diagonal is negative, `79522` rows have near-zero sums, and `1209`
boundary-influenced rows are strictly diagonally dominant. This supports an
M-matrix-like diffusion preconditioner but not CG or an SPD interpretation.

Two independent fixed hierarchies clear the exact saved corrector:

| Hierarchy | GMRES iterations | True residual ratio | Operator complexity |
| --- | ---: | ---: | ---: |
| default lAIR | `20` | `2.609e-9` | `14.983` |
| PyAMG nonsymmetric SA (PG-type transfers) | `45` | `9.182e-9` | `1.606` |

PyAMG nonsymmetric SA with Petrov-Galerkin-type transfers is retained as the
lower-complexity campaign configuration under the historical/internal `pgsa`
token. It is not literally Sala-Tuminaro's local-damping PG-SA algorithm. Rebuilding
one hierarchy per Newton step closes full source in `45+44+46=135` inner
iterations. All three steps are undamped; nonlinear relative `L2` falls from
`8.333e-2` to `7.189e-8`; final **wide-stencil all-frame** pair/spatial/time minima are
`0.0088301 / 0.0176603 / 1.0000128`. Default lAIR also closes in `60` total
inner iterations. A fresh deterministic comparison gives relative
`L2=1.67e-15`, even
though lAIR's hierarchy is about `9.3` times more complex.

This positive-gate statement is deliberately limited to the solved monotone
wide-stencil operator. The artifact's separate fixed-frame cross-check has
minimum spatial-principal value `-0.0243895`; an independent centered Hessian
reconstruction finds one negative node, `-0.0250979`, at
`(rho,z)=(6.25,0.75)`. The input `11/12` field was already negative there, so
the warning is not an AMG regression. It is a hard E-028 resolution and
continuum-admissibility gate.

The first completed fine full-source observables are ratio `3.28303` at
`r/r0=1`, peak gradient `11.0713`, centered original/White residuals
`1.963% / 0.328%`, and shell-flux deficits `1.857-1.986%`. These trend from
the coarse E-025 point toward E-024 but do not match it yet. The source has
only about `3.2` cells across the narrow scale, so the result is a completed
refinement datum rather than a continuum confirmation.

Run the full reproducible campaign with:

```bash
.venv/bin/python -m models.e026_nonsymmetric_amg \
  --preconditioner pgsa \
  --output-artifact models/checkpoints/e026_h025_m3_full_source_pgsa.npz
```

The E-026 tests cover matrix-sign diagnostics, fixed AIR action, the explicit
true-residual gate, caller-RNG isolation, field/report integrity-checked pickle-free
artifact round trips, and an exact deterministic rerun of the canonical
campaign and diagnostic boundary. The artifact records seed `260719`, effective
hierarchy/candidate choices, runtime versions, and the implementation digest.

## E-025/E-026 current limits

- The independent operator core and first full-source refinement point pass;
  the independent annulus continuum gate does not. E-026's `3.2830` ratio,
  `11.0713` peak, and `1.86-1.99%` shell-flux deficits move toward E-024 but
  remain materially different.
- A fixed direction set is not a convergence study. The campaign must refine
  `h`, directional coverage, and physical stencil reach together, with
  `h/dtheta -> 0`.
- The axisymmetric continuum reduction is exact, but the composite discrete
  azimuthal chord, axis reflection, and shortened circular boundary are an
  internal adaptation of published Cartesian schemes. Manufactured tests are
  evidence, not a transferred convergence theorem.
- The force, centered/White residual, shell-current flux, and minimum-location
  diagnostics now exist at full source. The remaining gate needs an outer-box
  comparison with the same observables and at least one six-cell
  joint-refinement level. It must also resolve the one negative centered/fixed-
  frame spatial-principal node; positive wide-stencil gates alone are not a
  continuum certificate.
- Stage checkpoint/restart, active-Jacobian incomplete factorization, and two
  fixed nonsymmetric AMG families now exist. PyAMG nonsymmetric SA is
  low-complexity at this
  grid, but mesh-independent setup and iteration behavior is untested.
  Higher-accuracy
  monotone directional interpolation or a positive-weight locally refined
  point cloud may later reduce uniform-grid cost, but each must pass the same
  source, boundary, residual, force, flux, and pair-sum gates.
- The six-cell preflight reaches `322319` unknowns and about `1.46 GiB` peak
  RSS through the direct native fine linear solve. Raw E-026-field prolongation
  becomes admissible only below `alpha~=0.003419` and is rejected as a warm
  start. The native `(1/12) phi_linear` predictor passes with pair/spatial/time
  `0.06323 / 0.12647 / 0.98999` and should seed E-028's matching first source
  stage; use `1/24` only as a conservative fallback.
- Density, material, asymmetry, target backreaction, EFT validity, and reaction
  accounting remain blocked. No artificial-gravity, inertial-control, FTL, or
  reactionless-propulsion claim follows.

## 2026-07-20 to 2026-07-24 E-028 native fine-grid continuation

`e028_fine_grid_campaign.py` turns the E-026 preflight into a digest-checked,
accepted-step continuation driver for the canonical `R=80`, `h=0.125`, `m=4`
broad annulus. It stores the full native linear field in the checkpoint, so a
resume rebuilds and fingerprints the operator/source but does not repeat the
large direct Poisson solve. The driver branch-checks before any residual
shortcut, freezes each PyAMG nonsymmetric-SA hierarchy inside GMRES, rebuilds it between
Newton corrections, and requires `info=0`, direct true residual ratio below
`1e-8`, at most `2000` inner iterations, nonlinear decrease, and positive
all-frame gates. It also records fixed-frame and independently centered
spatial-principal checks, A/P/R storage, peak RSS, runtime/code provenance, and
accepted-step failure state.

The canonical first stage starts from `(1/12) phi_linear` and targets the
matching `1/12` source. It closes in ten undamped Newton corrections and `370`
GMRES inner iterations, reaching nonlinear relative `L2=9.455e-12`. Final
wide pair/spatial/time minima are
`0.214399 / 0.428798 / 1.00000003`; fixed and centered spatial minima are
`0.428798` and `0.429923`, with no nonpositive nodes. Maximum operator
complexity is `1.7524`, maximum explicitly counted A/P/R sparse storage is
about `72.6 MB`, and peak process RSS is about `1.84 GiB`. A clean-process
replay is bitwise identical, and three nonsymmetric-SA candidate choices agree to
relative `L2` of order `1e-15`.

Run the retained first stage from scratch with a new checkpoint path:

```bash
.venv/bin/python -m models.e028_fine_grid_campaign \
  --stop-after-stage 1 \
  --checkpoint /tmp/e028_h0125_m4_campaign_checkpoint.npz \
  --output-artifact /tmp/e028_h0125_m4_1of12_pgsa.npz \
  --json
```

The original `2/12` checkpoint fingerprints macOS `26.5.1`; macOS `26.5.2`
correctly fails its exact runtime-provenance comparison before solving. Do not
bypass that guard. A fresh current-runtime replay reproduced the old `2/12`
field bit for bit and was continued in the separately named
`e028_h0125_m4_campaign_checkpoint_20260722.npz` lineage. Subject to an exact
runtime/code match, resume that accepted state to the next amplitude with:

```bash
cp -f \
  models/checkpoints/e028_h0125_m4_campaign_checkpoint_20260722.npz \
  models/checkpoints/e028_h0125_m4_campaign_stage4_work_20260723.npz
.venv/bin/python -m models.e028_fine_grid_campaign \
  --resume \
  --stop-after-stage 4 \
  --checkpoint models/checkpoints/e028_h0125_m4_campaign_stage4_work_20260723.npz \
  --output-artifact models/checkpoints/e028_h0125_m4_4of12_pgsa_20260723.npz \
  --json
```

Verify the source checkpoint SHA before copying and the working-copy SHA
before running. Keep the accepted stage-3 checkpoint immutable. If stage 4 is
interrupted, retain the work file only as an incomplete forensic record and
restart from a fresh stage-3 copy rather than promoting or blindly resuming it.

The retained `1/12`, `2/12`, and `3/12` artifacts are deliberately partial-source
bootstrap/branch-reach results. Stage 2 closes in nine Newton corrections and
`327` GMRES inner iterations, with one accepted `0.25` line-search step and
final nonlinear relative `L2=1.98284e-12`. Wide pair/spatial/time are
`0.103271 / 0.206542 / 1.00000037`; fixed/centered are
`0.206542 / 0.207483`, with no conflict. Its force ratio `1.165716`, peak
`2.791581`, centered original/White residuals `0.8553% / 0.2965%`, and worst
partial-charge flux deficit `-0.5962%` are not refinements of E-026's
full-source values. Physical stencil reach remains `0.625 r0`, or `78.1%` of
the source-transition scale.

The completed stage passes a stronger post-hoc shifted-`Gamma_2` check:
active/fixed/centered `sigma_2` minima are
`0.187500 / 0.154191 / 0.154469`. Pair-sum positivity is the linearized
ellipticity gate but does not, by itself, imply positive `sigma_2` away from an
exact pointwise root. Do not patch that extra gate into the driver mid-campaign:
the implementation hash is part of checkpoint resume. Apply it manually as a
hard stop until a deliberate checkpoint migration or replay can extend the
schema.

A same-amplitude coarse `2/12` control shows `44.5% / 46.7%` lower centered
original/White residuals and `38.4%` lower worst flux-deficit magnitude on the
fine grid, but the tracked `(6.25,0.75)` centered value is `3.25%` less
positive. Two coupled grids do not establish an asymptotic order. A full
secant predictor `2 phi_2-phi_1` to `3/12` is inadmissible. Scratch tests find
a conservative damped predictor near `lambda=0.8` and a wider-margin `5/24`
midpoint fallback, but neither belongs to the current fingerprinted campaign.
The canonical stage-3 run retained the plain accepted `2/12` seed and closed
without damping. The failed full secant remains useful predictor-boundary
evidence, not a required fallback.

Stage 3 closes in seven full Newton corrections and `280` GMRES inner
iterations. Every GMRES call has `info=0`; the largest direct true-residual
ratio is `9.1512e-9`, the largest inner count is `56`, and final nonlinear
relative `L2/Linf` are `7.01069e-12 / 1.81747e-10`. Wide pair/spatial/time are
`0.056542 / 0.113084 / 1.00000033`; fixed/centered spatial minima are
`0.112777 / 0.113256`, with no nonpositive nodes or conflict. Manual
active/fixed/centered shifted-`sigma_2` minima are
`0.187500 / 0.116118 / 0.116137`, all positive. The old warning location
`(6.25,0.75)` remains positive but its shifted-`sigma_2` falls about `8%`
from the coarse `3/12` control, so both moving-global and fixed-location
ledgers remain required.

At `3/12`, the force ratio at `r/r0=1` is `1.422741`; the maximum sampled
gradient is `3.919218` at the fixed-ray endpoint `r=12`; centered
original/White residuals are `0.96917% / 0.27903%`; and sampled-charge flux
deficits are `-0.74787% / -0.74159% / -0.72356%`. Fine versus a fresh coarse
`3/12` control lowers common-window original/White residuals
`40.99% / 45.91%` and worst flux-deficit magnitude `38.33%`, while ratio and
endpoint gradient change only `+0.447% / +0.382%`. These are same-amplitude
one-quarter-source comparisons, not full-source refinement or continuum
error bars.

A scratch-only stage-4 path reveals why the immutable-copy protocol matters.
The exact first full Newton correction passes `info=0`, direct true residual
`5.595e-10`, Armijo decrease, and all core wide gates, but its independent
fixed/centered spatial minima are `-0.032523 / -0.032099` and shifted
`sigma_2` minima are `-0.044816 / -0.044262` near `(6.25,0.375)`. A second
full correction returns them positive. Along the first direction the earliest
independent zero occurs at damping about `0.81237`; `0.8` barely passes, while
the dyadic `0.5` step has robust positive margins. Froese-Oberman-Salvador's
monotone extension is defined outside `Gamma_2`, so this off-root excursion
does not by itself reject a final passing root or prove the continuation branch
crossed the cone. It does mean an in-progress checkpoint is only a search
state: quote no observables and accept stage 4 only after final wide,
fixed/centered, and manual active/fixed/centered shifted-`sigma_2` checks pass.

The stage-3 invocation reports about `1.604 GiB` peak RSS, while the fresh
current-runtime replay high-water is about `1.832 GiB` from stage 1 (the old
runtime lineage reached `1.836 GiB`); explicit retained
A/P/R arrays remain about `72.6 MB`. If full source eventually passes, the
outer-box test must use fixed physical flux spheres and a common interior
window; the existing box-relative flux radii are not a same-observable
comparison. No physical artificial-gravity or propulsion claim follows.

Stage 4 was run only from the verified byte-identical working copy documented
above. It closes `4/12=1/3` source amplitude in six full Newton corrections
and `237` GMRES inner iterations. The largest direct true-residual ratio is
`8.447e-9`, the largest correction uses `56` inner iterations, and final
nonlinear relative `L2/Linf` are `6.808e-9 / 1.634e-7`. Wide
pair/spatial/time are `0.0355105 / 0.0710210 / 1.00000176`;
fixed/centered spatial minima are `0.0702601 / 0.0704617`, with no
nonpositive nodes or conflict.

The required manual endpoint audit passes active/fixed/centered shifted
`sigma_2=0.187499 / 0.085476 / 0.085357`; all corresponding `sigma_1`,
pair-sum, and `sigma_2` nonpositive counts are zero. Centered `sigma_2`
remains positive at difference steps `h`, `2h`, and `4h`. The old
`(6.25,0.75)` warning and the stage-4 transient `(6.25,0.375)` location are
both positive at the endpoint. The accepted checkpoint and artifact fields
and reports are exactly equal.

A fresh coarse `(h,m)=(0.25,3)` `4/12` control gives almost the same force
profile but materially worse integrated diagnostics. Fine versus coarse
changes are `+0.0756%` in the `r=1` force ratio, `+0.3673%` in the sampled
endpoint gradient, `-30.61% / -47.84%` in matched-step common-window
original/White residuals, `-37.97%` in worst fixed-sphere flux-deficit
magnitude, and `-93.66%` in source-charge-error magnitude. Fine stage GMRES
work rises `74.26%`; this is improving same-amplitude evidence, not an
asymptotic order.

The canonical first full correction still leaves the independent
fixed/centered `Gamma_2` reconstructions. A scratch-only sensitivity replaced
it with `alpha=0.5`, manually required active/fixed/centered `sigma_1`, pair,
and `sigma_2` positivity after every later accepted correction, and reached
the canonical endpoint to relative field `L2=4.89e-12` and maximum absolute
difference `4.56e-8`. This supports a common fixed-grid root and identifies
the excursion as solver-path dependent. It does not prove a unique
continuum-admissible branch, and the cone-preserving path did not replace the
canonical artifact.

The immutable accepted stage-4 checkpoint is
`models/checkpoints/e028_h0125_m4_campaign_checkpoint_20260723.npz`, SHA-256
`8cd1abd9f43b9076d6fb884933d055c4746fb0c37e8fd6d596840b7353c13ec4`.
The stage-4 artifact is
`models/checkpoints/e028_h0125_m4_4of12_pgsa_20260723.npz`, SHA-256
`4ddd280ba9b4ada9ebdb1963d92904813047577e48c750134df36ff9c06f58c1`.
Its field/report SHA-256 values are
`ec8fdb4f4050b11affb0194b4bb2eff68ab7e9ae3cf8371d54e3bf442bb7ae53`
and
`8b2c9ee855b2216862012434a16d87777d053bbd8cd0e11e8779d39ed3e4a4db`.

Stage 5 was run only from a collision-checked byte-identical copy of the
immutable stage-4 checkpoint. It closes `5/12` in five full Newton
corrections and `217` GMRES inner iterations. Maximum direct true-residual
ratio is `9.473e-9`, maximum one-correction inner work is `50`, and final
nonlinear relative `L2/Linf` are `4.822e-8 / 1.459e-6`. Wide
pair/spatial/time are `0.0250567 / 0.0501135 / 1.00000038`;
fixed/centered spatial minima are `0.0501135 / 0.0502433`, with no
nonpositive nodes or conflict.

Manual endpoint active/fixed/centered shifted `sigma_2` minima are
`0.187489 / 0.062050 / 0.061808`; all corresponding `sigma_1`, pair, and
`sigma_2` minima are positive and their nonpositive counts are zero. Centered
`sigma_2` remains positive at physical steps `h`, `2h`, and `4h`. A fresh
deterministic canonical replay ends at the saved field bit for bit; its
accepted states and tested piecewise-affine segments pass the three
active/fixed/centered `Gamma_2` reconstructions. The smallest accepted-state
or sampled-segment fixed pair/`sigma_2` are
`0.012607 / 0.029889`; centered values are `0.019123 / 0.052069`.
The fixed check shares wide-operator ingredients; the centered postprocessor
is separate. This stage has no analog of the canonical stage-4 path
excursion.

At matched centered step `0.25`, the global pair minimum falls from
`0.05711` to `0.03590` to `0.02525` over stages 3--5, but the `0.01%`
weighted quantile falls more slowly from `0.11887` to `0.09529` to
`0.08334`; only `5.26e-5` of common-window axisymmetric nodal-quadrature
weight is below pair margin `0.05` at stage 5, but `182/310365` masked nodes
are below it. The denominator includes the large outer vacuum region and
does not rule out a thin connected strip or a larger source-layer-relative
tail. Record weighted and unweighted tails as well as the moving minimum. A
fresh coarse stage-5
control shows fine reductions of `29.79% / 47.50%` in matched-step
common-window original/White residual, `37.94%` in worst fixed-sphere flux
deficit, and `93.66%` in source-charge error. The fine `r=1` ratio changes
`+0.619%`, while stage GMRES work rises `76.42%`. This is improving
same-amplitude evidence, not an asymptotic order.

The immutable accepted stage-5 checkpoint is
`models/checkpoints/e028_h0125_m4_campaign_checkpoint_20260724.npz`, SHA-256
`4c2c10a53156c59b53abbc5963d9089f460c75e65b6cdc4fa1cb64d4f548977f`.
The stage-5 artifact is
`models/checkpoints/e028_h0125_m4_5of12_pgsa_20260724.npz`, SHA-256
`a72166c722c947dad9da93b505fa1335633adf23bd61c33a7dfa9968b6215c84`.
Its field/report SHA-256 values are
`ab5b23f15f729cb0f72589c2287e1013f8f6b05a7dbe91ad6b1debffe272f5c7`
and
`7207528839fcdd909ed19467e6de349374c09ff2fcbd7a97e9780e568f2174c0`.
The checkpoint and artifact loaders return exactly equal fields and reports.

The first strict attempt to resume stage 5 correctly stopped before solving:
the checkpoint embedded requirements-file SHA
`cd1df48db71c...`, while the committed file is
`b44e38d9b107...`. The numerical dependencies and runtime were unchanged, but
the exact provenance guard includes the whole file. It was not bypassed. A
fresh campaign under the committed fingerprint replayed through `5/12` in
`164.6 s` and reproduced the accepted stage-5 field bit for bit. Only that
current-provenance replay advanced to stage 6.

Stage 6 closes `6/12=0.5` in five full Newton corrections and `254` GMRES
inner iterations. Every GMRES `info=0`; maximum direct true-residual ratio is
`9.154e-9`, maximum one-correction work is `59`, and final nonlinear relative
`L2/Linf` are `5.459e-8 / 1.784e-6`. Wide pair/spatial/time are
`0.0192176 / 0.0384351 / 1.00000237`; fixed/centered spatial minima are
`0.0330635 / 0.0327836`, with no nonpositive nodes or conflict.

Manual endpoint active/fixed/centered shifted `sigma_2` minima are
`0.187484 / 0.042521 / 0.042158`; all corresponding `sigma_1`, pair, and
`sigma_2` counts remain positive. Centered `sigma_2` at physical difference
steps `0.125/0.25/0.5` is
`0.042158 / 0.066460 / 0.127299`. The tracked `(6.25,0.75)` and
`(6.25,0.375)` locations remain positive.

A deterministic stage-6 replay returns the retained field bit for bit and
reproduces five Newton/`254` GMRES. All five accepted states and nine tested
points on every piecewise-affine segment remain inside active, fixed, and
centered shifted `Gamma_2`, but the first accepted full correction comes
close: fixed pair/`sigma_2` are `0.002255 / 0.004942`, and centered values are
`0.002233 / 0.004885`. Later accepted states recover the endpoint margin.
This is a positive sampled search path, not an interval enclosure.

The endpoint has four exact active-frame ties at the axis. Enumerating all
`2^4=16` active selections produces one bitwise-identical Jacobian matrix.
Its sign-normalized form has positive diagonal, nonpositive off-diagonal, one
strongly connected component, all `322319` rows weakly diagonally dominant
to numerical tolerance, and `3047` strict rows. Thus the observed tie
selection does not generate alternate endpoint matrices. This still does not
bound the inverse, roundoff, nearby source states, or continuum conditioning,
and it does not replace a validated continuation enclosure.

At matched centered step `0.25`, stages `3/12` through `6/12` have pair minima
`0.05711 / 0.03590 / 0.02525 / 0.01937` and pair `0.01%` weighted quantiles
`0.11887 / 0.09529 / 0.08334 / 0.07520`. At stage 6,
`227/310365` common-window nodes lie below pair `0.05`. They form one
connected near-midplane component spanning `rho=0-6.25`, `z=0-0.75` and
touching the inner source smoothing layer. Its full-window axisymmetric
weight fraction is `6.535e-5`, but its source-support-relative fraction is
`0.003139`. Even the stricter pair `<0.02` set contains ten nodes in one
component. The tail is localized but genuine; the large outer vacuum
denominator understates its source-relative prominence.

A fresh same-amplitude coarse `(h,m)=(0.25,3)` control closes in five
Newton/`174` GMRES. Fine versus coarse changes are `+1.728%` in `r=1` force
ratio, `+0.321%` in sampled endpoint gradient, `-29.19% / -47.15%` in
matched common-window original/White residuals, `-37.87%` in worst
flux-deficit magnitude, and `-93.66%` in source-charge-error magnitude.
Native fixed/centered margins decline, while the matched-`0.25` centered
margin improves. This mixed two-grid evidence is not an asymptotic order.

The immutable accepted stage-6 checkpoint is
`models/checkpoints/e028_h0125_m4_campaign_checkpoint_20260725.npz`, SHA-256
`ff82363833c84e416e020a8df56d6067b6b1f7612c41f30f6499d6b95690babb`.
The stage-6 artifact is
`models/checkpoints/e028_h0125_m4_6of12_pgsa_20260725.npz`, SHA-256
`64a0fca132dd6b068c543f102c74c3ffa09a545509d9f822857cc13e179c5476`.
Its field/report SHA-256 values are
`cd806ff41c0a33d541cc5c1dba44a3c7ad693ddb6b81dda5eae2ac1db8757c3e`
and
`fe2c11e1d2e7806b12836325eaaed565137b5495efbb25417f4c6545fd3a256c`.
The checkpoint and artifact loaders return exactly equal fields and reports.

Subject to exact checkpoint, runtime, and code matches, stage 7 should run
only from a new collision-checked byte-identical stage-6 working copy.
Choose unused date-stamped names and stop rather than bypassing any mismatch.
If interrupted, restart from another accepted stage-6 copy. Require the
existing strict solver and endpoint gates, deterministic accepted-path replay,
the source-relative connected-tail ledger, all active-frame tie selections,
and a fresh coarse `7/12` control. The first accepted correction now deserves
special scrutiny because its independent margin is much smaller than the
endpoint's. Do not begin outer-box, density, asymmetry, target, or propulsion
extensions before full source passes.

Stage 6 remains a half-source numerical result for a hypothetical scalar PDE.
No detected field, physical artificial gravity, inertial control, spacetime
engineering, FTL, or propulsion claim follows.

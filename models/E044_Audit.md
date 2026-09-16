# E-044: Earth-sourced ALP helicity phase qualification

Audit date: 2026-09-16. **Decision: park P-028/H-028 pending measured helicity,
rotation, and optical-response qualification.** This is a hypothetical
new-interaction precision test, not an observed field or an acceleration device.
Only P-028 was deepened. E-036 remains closed; the annular Galileon line and its
immutable checkpoints remain parked.

## Frozen model and scope

Use a free canonical scalar with `-g_B phi NbarN - g_gamma phi F Ftilde/4`,
`g_L=g_(B-L)=0`, baryon charge `Q=M/u`, and no dark-matter abundance assumption.
An ordinary Earth source would generate a static scalar profile **if these
couplings exist**. Rotating the detector modulates its response; it does not
actuate the source. Equal-and-opposite scalar reaction belongs to source,
field, and probe. Optical angular momentum and mechanical rotation react
through mirrors/retarders, motors, bearings, supports, and Earth.

For a homogeneous sphere, write `y=m R/(hbar c)` and
`A(y)=exp(-y)*3*(y cosh(y)-sinh(y))/y^3`. With physical lengths in metres,

```
|Delta phi| = g_B Q (hbar c)/(4 pi) A(y) exp[-m d/(hbar c)]
              * [ell/(R+d) + 1-exp(-m ell/(hbar c))]/(R+d+ell)
S = (4 F/pi) * g_gamma[GeV^-1] * 1e-9 * |Delta phi[eV]|.
```

The executable uses `expm1` and a small-argument series to preserve the
massless limit and avoid overflow. It reports **magnitudes**; signs reverse
with coupling product, helicity, and orientation. The signal is the reflected
opposite-helicity phase, not PVLAS transmitted ellipticity. Parameters are
`M=5.9722e24 kg`, `R=6371 km`, `d=0.1 m`, `ell=1 m`, `F=1e4`, `1064 nm`.
The homogeneous Earth is a source model, not a certified density enclosure.
Fayet's five-sphere alternative changes the endpoint transfer by about
`-0.1794%` at `m=1e-14 eV`; that comparison is not a rigorous uncertainty bound.
The report's `earth_source_model_sensitivity` freezes Table 3's radii
`(6371, 6341, 5701, 3480, 1221) km` and weights
`(0.5, 0.1333, 0.1715, 0.1929, 0.0023)` at the same total Earth mass and detector
endpoints; these weights describe superposed full spheres, not disjoint shell
masses.

## Conditional constraint comparison

The dated primary-source audit recovers a conservative baryon-only spin-zero
MICROSCOPE envelope `|g_B|<=6.6e-25` for `m<=1e-14 eV`; the massless Table 6
value is `6.4e-25`. Different charges, several simultaneous couplings,
screening, or another scalar potential require another analysis.
The following three factorized comparisons intentionally omit the direct
pulsar constraint discussed below; none is the largest currently allowed
signal when that pulsar model is also adopted.

| Photon scenario | Photon bound, GeV^-1 | Arithmetic product, GeV^-1 | Massless phase ceiling, rad |
| --- | ---: | ---: | ---: |
| H1821+643 cluster-field model | `6.3e-13` | `4.158e-37` | `7.3662e-12` |
| CAST solar Primakoff model | `5.8e-11` | `3.828e-35` | `6.7815e-10` |
| ALPS II laboratory-only photon bound | `1.5e-9` | `9.9e-34` | `1.7538e-8` |

These are conditional **ceilings from separate limits**, not predictions,
joint 95% regions, or a globally allowed envelope. H1821 uses 99.7% Bayesian
credibility and a `beta=100` magnetic-pressure model, including its author's
light-mass limiting extension. MICROSCOPE, CAST and ALPS use their different
stated 95% constructions. The solar and laboratory-only rows deliberately
omit stronger cluster assumptions; they are not simultaneously allowed under
all three scenarios. Dark-matter bounds are inapplicable without abundance.

**Additional current conditional constraint:** the September 8 revision of
[Witte et al., arXiv:2512.11023v2](https://arxiv.org/html/2512.11023v2),
Appendix B Eqs. (19)-(20), gives an approximate present interpulse exclusion
`|g_B*g_gamma| >= 8e-39 GeV^-1` for `m <= about 1e-12 eV`. Its generic linear
nucleon interaction and photon operator match this audit without a QCD
mass-coupling relation or dark-matter abundance. We use only `m<=1e-14 eV`.
This is conditional on the neutron-star source and pulsar discharge model:
an APR equation of state and one-solar-mass scalar source, dipolar field and
return-current geometry, and near-surface radio pair cascades. The
[September 8 companion methods paper](https://arxiv.org/html/2609.08840v1)
addresses discharge modeling and consistency requirements.

The geometry is an inference, not measured current tomography. The underlying
[radio-polarization study](https://arxiv.org/html/2008.13750v2) also discusses
non-dipolar surface fields and emission near ten stellar radii. That emission
altitude is distinct from the lower pair-production region suppressed in the
constraint argument. Conversely, the new methods paper reports a global PIC
check of current closure when only one pole loses pair production; global
closure is not wholly untested. These facts retain an approximate exclusion
conditional on the dipolar return-current interpretation, without supplying
a quantified alternative topology that removes it.

The interpulse estimate does not state a confidence level. The author's
death-line curve is somewhat stronger and labeled 95%, but its exact numerical
curve was not recovered; it is not replaced by an invented stronger value.
Appendix B Eq. (22)'s `2e-39` sensitivity is **prospective**, requiring additional
sign/geometry information, and is not used as a current limit.

Using `8e-39` as an approximate conditional product ceiling gives a massless
Earth phase `1.41725e-13 rad`, **51.975 times smaller** than the factorized
cluster/MICROSCOPE comparison. It is a model-conditioned scale bound, not a
precise confidence contour, a signal prediction, or a globally certified
allowed envelope. All existing larger comparison rows remain explicitly
scoped rather than being silently rewritten.

The report preserves sparse MICROSCOPE Table 6 values through `1e-11 eV`,
but marks every resulting diagnostic as **not the combined allowed region**.
Surface sources and orbital measurements have different range suppression.
No extrapolation of the low-mass ceiling or inference of an allowed large
signal from weakened satellite limits is permitted. Primary short-range
curves exist; an author-supplied numerical combined envelope was not recovered
in this bounded audit. Fixed-coupling mass sweeps are transfer diagnostics.

At the scalar envelope, the massless surface-gradient scale is `0.1812 eV^2`.
A `B/m=1/u` test body has conditional fifth-force acceleration
`5.848e-11 m/s^2`, or `4.093e-9 N` on 70 kg. This is neither universal free fall
nor a controllable local source. Local scalar-gradient energy is
`0.3424 J/m^3`; `8 pi G u/c^4=7.109e-44 m^-2` is only a dimensional curvature
source scale, not a solved metric or the entire source/apparatus energy.
The effective theory also breaks CP and shift symmetry. The proposal's
illustrative `10 TeV` cutoff gives a mass correction of order `7.4e-13 eV`
at this `g_B`; light masses can require tuning. This cutoff-dependent
naturalness observation is not an experimental exclusion or universal no-go.
The pulsar product ceiling alone does not determine `g_B`; these force and
gradient-energy numbers retain their separately declared scalar-envelope
assumption and do not become measured or uniquely pulsar-conditioned scales.

## What the detector would actually have to reject

First preserve the explicitly factorized cluster/MICROSCOPE comparison,
which omits the newer pulsar model; smaller couplings demand proportionally
tighter residuals. Its equivalent
cavity differential length is `9.797e-23 m`. Every dominant coherent false
signal must be below `7.366e-13 rad` (`9.797e-24 m` in the simple length
channel). A one-sided white length ASD of `4.988e-19 m/sqrt(Hz)` would give
SNR one for a known sinusoidal peak over 300 days. White integration over
that time has not been demonstrated here.

Adopting the present conditional interpulse product ceiling instead requires:

| Quantity | Pulsar-conditioned massless budget |
| --- | ---: |
| Unit-peak vertical-source phase | `1.41725e-13 rad` |
| Equivalent differential length | `1.88494e-24 m` |
| Each dominant coherent phase residual, `<0.1 S` | `1.41725e-14 rad` |
| Corresponding simple length-channel residual | `1.88494e-25 m` |
| One-sided white length ASD for sinusoidal SNR one over 300 days | `9.59656e-21 m/sqrt(Hz)` |

These budgets share the same unverified response and white-integration
assumptions. They are 51.975 times tighter than the factorized comparison.

Published benchmarks do not establish the same helicity observable:

- PVLAS measured single-pass optical-path-difference noise around
  `3-6e-19 m/sqrt(Hz)` at 10-20 Hz, principally **linear** birefringence;
  ellipticity/rotation mixing and cavity transfer matter. This adjacent
  benchmark is numerically near the older factorized-scenario ASD target,
  but above the pulsar-conditioned target. Neither comparison establishes a
  MAGPI noise floor, achievable rejection, or a general optical no-go.
- A June 2026 three-frequency, 19-m **linear-polarization** cavity measured
  `4e-14 m/sqrt(Hz)` at 3 mHz over a 20-hour record; rotating a half-wave plate
  gave `1.3e-13 m/sqrt(Hz)` in a 15-hour record. It did not rotate a complete
  MAGPI cavity or qualify 300-day residuals. Its `1e-17` target is projected.
- No matched Jones/polarization transfer, gain covariance, multi-color
  cross-PSD, or coherent rotation/thermal/magnetic/stress budget was recovered.
  Numerical qualification defaults to false and requires independent
  provenance attestations; quantities in different observables cannot pass it.

## New analytic falsification: co-metrology has a noise cost and a null space

After calibrated finesse normalization, let `y_i=A+k_i L+b_i`. With one common
length nuisance, the two-color estimator has weights
`w=(k2,-k1)/(k2-k1)`. At fixed **total** circulating power across colors,
independent photon counting minimizes its variance at
`P_i/P_total=|w_i|sqrt(E_i)/sum_j |w_j|sqrt(E_j)`.

The declared count convention is `P0=pi P_cav/(2F)` and
`sigma=1/sqrt(N_gamma)`. At 1 MW and 300 days, `P0=157.08 W` and
`sigma_DC=6.772e-15 rad`. The proposal's approximate Eq. (10) is smaller by a
factor of two; it is preserved separately, not silently mixed. Incident
optical energy is `4.072e9 J` (`1.131 MWh`), excluding electrical conversion,
cryogenics, rotation and losses. This aggregate count allocation is an
explicit audit convention, not proof of the paper's complete apparatus power.

| Ideal two-color case | Optimal DC sigma, rad | Full-rotation peak sigma, rad | Peak SNR, cluster/MICROSCOPE only | Peak SNR, conditional interpulse ceiling |
| --- | ---: | ---: | ---: | ---: |
| Adjacent longitudinal modes, 149.896 MHz apart | `2.546e-8` | `3.600e-8` | `2.046e-4` | `3.93662e-6` |
| Octave, 1064 / 532 nm | `2.312e-14` | `3.270e-14` | `225.29` | `4.33462` |

The peak calculation uses `T_eff=integral cos^2(Omega t)dt=T/2`. Equal
independent per-color phase noise is amplified `2.658e6` for adjacent modes,
versus `sqrt(5)` for octave spacing. The first case fails even this ideal
source-scale test; the second survives only ideal photon statistics. No
coating, efficiency, mode, or noise-correlation performance is inferred.
The table assumes an ideal full rotation with unit peak projection onto the
vertical source gradient. The Earth-axis null geometry below retains only
`cos(latitude)` of that signal: at 45 degrees the pulsar-conditioned octave
SNR is `3.06504`, before any technical noise or losses. This smaller ideal
margin strengthens the reason to demand measured qualification; it does not
prove all such searches impossible.

More wavelengths cannot separate `A_axion+A_rotation`: their design-matrix
columns are identical. Nor does the word “chromatic” specify a coating model:
an unrestricted coating function can take any values at finitely many
wavelengths. A restricted, calibrated dispersion basis with bounded residuals
is necessary even before rotation discrimination.

## Achromatic rotation and the correct modulation harmonic

Ordinary spin-rotation response has scale
`S_rot=kappa*(4F/pi)*(ell/c)*(Omega dot n)`. The 2025 gyroscope proposal uses
an order-one expression (`kappa=1`); inserting its dispersion relation into
MAGPI's single-ended reflection convention gives `kappa=2`. These are
convention sensitivity examples, **not a proven interval** for an unbuilt
instrument. Both require complete optical boundary and angular calibration.

At an illustrative 45-degree latitude, the Earth term is
`2.19e-9` or `4.38e-9 rad`, respectively **297 or 595 times** the cluster
ceiling. Helicity reversal and color subtraction preserve this nuisance.
The same-channel coherent axial-rate residual must be below
`1.734e-8` or `8.672e-9 rad/s`. At a declared 3-mHz full rotation, the associated
small axial-wobble scales are `0.920` or `0.460 microrad`. These are target
budgets, not measured wobble or a general mechanical tolerance.

For the conditional interpulse ceiling, the unchanged Earth terms are instead
`15452` or `30904` times the phase target. The coherent axial-rate residual
budgets tighten to `3.33701e-10` or `1.66850e-10 rad/s`, with corresponding
3-mHz small axial-wobble scales `17.7034` or `8.85169 nrad`. These numbers use
the same unit-peak reference and convention examples; choosing the 45-degree
null geometry tightens its residual budgets by another `cos(45 degrees)`.

There is an algebraic escape worth recording: rotate the cavity direction in
a plane perpendicular to Earth's rotation vector, with the rotor axis
parallel to that vector. Then ideal `Omega dot n=0` for both Earth and rotor,
while radial-source phase retains `cos(latitude)*cos(Omega_mod t)`. This is
not validated rejection: finite beam aperture, flexure, pointing, coating and
retarder phases remain. Its reduced signal also tightens the budget by the
`cos(latitude)` factor. At the poles this geometry has no radial signal.

An independent control is a pair of **settled** up/north orientations:
`y_U=A+R*sin(lambda)` and `y_N=R*cos(lambda)`, with design matrix
`X=[[1,sin(lambda)],[0,cos(lambda)]]` and
`A_hat=y_U-tan(lambda)*y_N`. Its condition number is
`sqrt((1+|sin(lambda)|)/(1-|sin(lambda)|))`, equal to `1+sqrt(2)` at 45 degrees
and singular at the poles. If each orientation has variance `C/t`, fixed total
settled exposure `T` is optimally split as
`t_U/T=1/(1+|tan(lambda)|)` and `t_N/T=|tan(lambda)|/(1+|tan(lambda)|)`, giving
`sigma_A=(1+|tan(lambda)|)*sqrt(C/T)`. At 45 degrees this has the same ideal
factor-two penalty as continuous Earth-axis-null modulation, with no
sensitivity windfall. Signed up/down and north/south differences remove only
a stable common offset: an unknown `b(n)=beta*n_Up` remains exactly degenerate
with the source signal. This is a geometry/transfer control, not demonstrated
rejection; arbitrary orientation backgrounds still prevent identification.
Relative gains, handedness and alignment must remain calibrated, while
motion transients, settling losses and the actual duty cycle require separate
budgets. At the equator, estimating the rotation coefficient independently
requires nonzero north exposure even though the optimum for `A` alone does not.

Symmetric small rocking **about vertical** supplies no first harmonic:
`cos(theta0 cos(Omega t))=1-theta0^2/4-(theta0^2/4)cos(2Omega t)+...`.
At one degree the second-harmonic signal is only `7.615e-5` of the vertical
phase. Full rotation supplies the unit-peak first-harmonic budget above.
Biased rocking `theta=theta_b+theta0*cos(Omega t)` instead has first-harmonic
fraction `-2*sin(theta_b)*J1(theta0)`, approximately `-theta0*sin(theta_b)`;
its attenuation and effective exposure must be included separately.

## Reopening rule and next step

P-028 passes source/reaction only at model level; constraints, achievable
precision scale, and executed falsification remain partial. Park it as
`parked_no_measured_helicity_noise_and_rotation_budget`. This is a negative
qualification result, not a disproof of ALPs or all future photon searches.

Reopen only for a measured same-helicity transfer and resource tuple, a
current constraint envelope for the tested masses, bounded dispersion and
spin-rotation response, and all dominant coherent residuals below `0.1 S`.
These per-background thresholds do not bound the aggregate coherent residual
to `0.1 S` and do not establish detection significance: seven such residuals
can sum coherently toward `0.7 S`. Any limit or discovery analysis requires a
joint systematic and covariance model.
Publish phase/length/thermal/field/pointing injections, helicity swaps,
rotation reversals, angular metrology, both quadratures, channel cross-PSDs,
and independent null data. A geometry or simulation alone does not pass.

E-045 moves to P-034's distinct trapped-ion proper-time witness and joint-
resource audit; the portfolio also retains gravity-tractor acceleration and
MHD gas separation and parks X17 for remote-force range. No hardware or
numerical campaign is authorized by this result.

## Reproduction and primary sources

```
python -m models.e044_axion_helicity_audit --output /tmp/e044.json
python -m unittest discover -s tests -v
```

- [MAGPI source and reflected-phase convention, PRD 109, 015025](https://arxiv.org/html/2304.11261v2).
- [Fayet spin-zero scalar recast, PRD 112, 095018](https://arxiv.org/html/2507.02723v2).
- [H1821+643 conditional photon constraint, MNRAS 510, 1264](https://arxiv.org/html/2109.03261v2).
- [CAST final 2024 result](https://arxiv.org/abs/2406.16840v3).
- [ALPS II measured bound, May 2026 revision](https://arxiv.org/abs/2512.14110v3).
- [Present conditional pulsar interpulse product constraint, September 8 revision, Appendix B Eqs. (19)-(20)](https://arxiv.org/html/2512.11023v2).
- [Pulsar discharge modeling and particle-in-cell methods, September 8 preprint](https://arxiv.org/html/2609.08840v1).
- [Helicity gyroscope, PRA 111, 043502](https://arxiv.org/html/2406.16178v2).
- [PVLAS measured birefringence noise, EPJC 78, 585](https://arxiv.org/html/1805.03198).
- [Three-frequency cavity demonstration, PRA 113, 063518](https://journals.aps.org/pra/abstract/10.1103/r33m-v1kn).

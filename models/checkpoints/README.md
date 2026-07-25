# E-025 and E-028 Research Checkpoints

These files preserve accepted numerical states for the independent
wide-directional 2-Hessian validation. They are solver artifacts for a
hypothetical PDE, not observations or full-source physics results.

The `.npz` files are stored through Git LFS. Their independent container
hashes are listed in [`SHA256SUMS`](SHA256SUMS); from this directory, verify
them with `shasum -a 256 -c SHA256SUMS`. Three retained work snapshots are
tracked deliberately for continuity:

- `e028_h0125_m4_campaign_stage4_work_20260723.npz` is byte-identical to the
  accepted `e028_h0125_m4_campaign_checkpoint_20260723.npz` state.
- `e028_h0125_m4_campaign_stage5_work_20260724.npz` is byte-identical to the
  accepted `e028_h0125_m4_campaign_checkpoint_20260724.npz` state.
- `e028_h0125_m4_campaign_stage6_work_20260725.npz` is byte-identical to the
  accepted `e028_h0125_m4_campaign_checkpoint_20260725.npz` state.

The work suffix preserves solver lineage and is not an acceptance or physics
claim. Before replacing a tracked work snapshot, commit the prior version and
document the transition. Disposable `*.partial.npz` and `*.tmp.npz` files
remain excluded. If a failed state has enduring boundary value, retain it as a
dated, documented artifact and add its digest before committing.

## `e025_h025_m3_11of12.npz`

- Date: 2026-07-18
- Grid: `R=80`, `h=0.25`, directional radius `m=3`, `80731` unknowns
- Source: fixed broad smooth `mu=36.8` annulus
- Accepted amplitude: `11/12`
- Pending target: `1`
- Nonlinear / GMRES tolerances: `1e-7 / 1e-8`
- Newton / GMRES restart-cycle caps: `20 / 40`, with GMRES restart `50`
- Completed-stage preconditioner: active ILUT, drop/fill `1e-3 / 10`
- Pending-stage provenance: active ILUT, drop/fill `1e-4 / 20`; no pending-stage
  Newton correction was accepted, so E-026 may select a new preconditioner
  before resuming
- Pair / spatial / time minima: `0.0095666 / 0.0191332 / 0.9999972`
- SHA-256:
  `63306017e50599aa6f04c8f32edbe102c640b0f991ce4be937da54112346ac94`

The loader validates the full discrete-operator and boundary digest, source
digest, continuation schedule, tolerances, and iteration caps. Do not bypass a
fingerprint failure. Recompute active frames, Jacobians, factors, and Krylov
state after loading.

## `e026_h025_m3_full_source_pgsa.npz`

- Date: 2026-07-19
- Input checkpoint SHA-256:
  `63306017e50599aa6f04c8f32edbe102c640b0f991ce4be937da54112346ac94`
- Grid/source: unchanged `R=80`, `h=0.25`, `m=3`, broad smooth `mu=36.8`
- Full-source solver: fixed PyAMG nonsymmetric-SA V-cycle with
  Petrov-Galerkin-type transfers, rebuilt once per Newton
  step, ordinary left-preconditioned GMRES, `rtol=1e-8`, `restart=50`,
  `maxiter=40`
- Closure: three undamped Newton corrections, `135` total GMRES inner
  iterations, final nonlinear relative `L2=7.18854e-8`
- Wide-stencil all-frame pair / spatial / time minima:
  `0.00883013 / 0.01766026 / 1.00001278`
- Independent cross-check warning: fixed-frame minimum spatial principal
  `-0.0243895`; centered minimum `-0.02509785` at the single nonpositive node
  `(rho,z)=(6.25,0.75)`. This was already negative in the `11/12` input and is
  a hard E-028 joint-refinement gate, not an AMG regression.
- Field SHA-256:
  `b5f0a48c9b5e84e7a6abc89239c797f0e082d0fbb6bc023913e3cf41d98042ed`
- Report SHA-256:
  `44c6913e509454c3ba2c19702137ee8b71f04ce7b6fb377638a690cab37a9acc`
- Model-module SHA-256:
  `a02567a970af5f9326a61bb26b5a78f80a13f3555011a70c8bc6218290b5cf1c`
- Artifact SHA-256:
  `0af7fa9b280b7803394aabb55939a17a6355105bdfead643a0e78d954cfcd6a2`

This is a pickle-free E-026 format-v2 artifact containing the full-source field
plus its JSON provenance and complete diagnostic report. Load it with
`load_campaign_artifact`; the loader verifies both field and report digests and
their mutual consistency. Seed `260719`, effective hierarchy choices, runtime
versions, and implementation provenance make the checked-in result exactly
rerunnable in the recorded environment. It is the first
completed independent full-source refinement point, not a six-cell or
continuum result and not evidence for a physical Galileon field.

## `e028_h0125_m4_campaign_checkpoint.npz`

- Date: 2026-07-21
- Grid: `R=80`, `h=0.125`, directional radius `m=4`, `322319` unknowns
- Source: fixed broad smooth `mu=36.8` annulus
- Accepted amplitude: `2/12`
- Pending target: `3/12`
- Solver: fixed PyAMG nonsymmetric-SA V-cycle with Petrov-Galerkin-type
  transfers (historical/internal token `pgsa`), rebuilt once per Newton step;
  left-preconditioned GMRES with `rtol=1e-8`, `restart=50`, `maxiter=40`
- Latest-stage closure: nine Newton corrections, `327` GMRES inner iterations,
  eight full steps and one `0.25` step, final nonlinear relative
  `L2=1.98284e-12`
- Campaign totals through two stages: `19` Newton corrections and `697` GMRES
  inner iterations
- Wide pair / spatial / time minima:
  `0.10327087 / 0.20654173 / 1.00000037`
- Independent checks: fixed-frame minimum `0.20654173`, centered minimum
  `0.20748251`, no nonpositive nodes at this partial amplitude; post-hoc
  active/fixed/centered shifted-`sigma_2` minima
  `0.187500 / 0.154191 / 0.154469`
- Field SHA-256:
  `3219171452d92fa1e6f027623a318e6aed11bfe9e463a7a6e55c262251270290`
- Model-module SHA-256:
  `e3e4029e8e83a08ee9d1df8068e325a1b9f954d4fd26232de12f6c46bb8eb95d`
- Checkpoint SHA-256:
  `8dd454c10583f0cfe4287d7938228b5e41023e4121320c2f2b6ab35aa55b9db3`

This pickle-free accepted-state checkpoint contains both the nonlinear field
and the full native fine-grid linear reference, each protected by embedded
integrity digests. Resume
validates the operator, source, schedule, configuration, runtime/code
fingerprints, field, linear field, and report before rebuilding active
Jacobians and hierarchies. It avoids repeating the direct Poisson solve. Never
reinterpret the `12`-stage schedule as a `24`-stage checkpoint.

On 2026-07-22 this checkpoint's saved platform
`macOS-26.5.1-arm64-arm-64bit-Mach-O` did not match the current
`macOS-26.5.2-arm64-arm-64bit-Mach-O`. Exact resume stopped before solving or
writing, and the checkpoint retained the SHA-256 above. Do not bypass that
guard. The current-runtime replay and its continuation are documented below
under separate filenames.

## `e028_h0125_m4_1of12_pgsa.npz`

- Date: 2026-07-20
- Input accepted-state checkpoint SHA-256:
  `49de2d6b3dafb536ef60a9863d9fad7cf4d0a4df6d27a77166839f857fd4cdfa`
- Grid/source and accepted state: canonical E-028 values above, amplitude
  `1/12`
- Source charge error: `-4.31633e-6` (`-0.000431633%`)
- Maximum PyAMG nonsymmetric-SA operator complexity / levels: `1.75236 / 5`
- Maximum explicit A/P/R sparse storage: about `72.6 MB`
- Peak process RSS: about `1.84 GiB`
- Field SHA-256:
  `65764586bd75368121cc616d28b5fdb0a6da4d05294da78b605bf44bba7ccce0`
- Model-module SHA-256:
  `e3e4029e8e83a08ee9d1df8068e325a1b9f954d4fd26232de12f6c46bb8eb95d`
- Artifact SHA-256:
  `960076106dbf157fb80c696561cf5165c4c5c127b416f903c1ef2cdd1ebd649e`

This completed-stage artifact is a digest-checked discrete solver/bootstrap
result, not a full-source refinement. Its force, peak, residual, and flux
diagnostics are normalized to the `1/12` source. The absence of a negative
centered node at weak source does not resolve E-026's full-source warning.
Continue only through integrity-checked accepted stages and stop on any
wide/fixed/centered conflict. No artificial-gravity, inertial-control, FTL, or
propulsion claim follows.

## `e028_h0125_m4_2of12_pgsa.npz`

- Date: 2026-07-21
- Resume input checkpoint SHA-256:
  `49de2d6b3dafb536ef60a9863d9fad7cf4d0a4df6d27a77166839f857fd4cdfa`
- Output accepted-state checkpoint SHA-256:
  `8dd454c10583f0cfe4287d7938228b5e41023e4121320c2f2b6ab35aa55b9db3`
- Grid/source and accepted state: canonical E-028 values above, amplitude
  `2/12`
- Latest-stage closure: nine Newton corrections, `327` GMRES iterations,
  final relative nonlinear `L2=1.98284e-12`
- Wide pair/spatial/time: `0.10327087 / 0.20654173 / 1.00000037`
- Fixed/centered spatial: `0.20654173 / 0.20748251`, no nonpositive nodes
- Partial-source observables: ratio `1.165716`, peak `2.791581`, centered
  original/White residuals `0.8553% / 0.2965%`, worst flux deficit `-0.5962%`
- Source charge error: `-4.31633e-6` (`-0.000431633%`)
- Maximum explicit A/P/R sparse storage: about `72.6 MB`
- Current-invocation peak RSS: about `1.616 GiB`; campaign high-water remains
  about `1.84 GiB` from stage 1
- Field SHA-256:
  `3219171452d92fa1e6f027623a318e6aed11bfe9e463a7a6e55c262251270290`
- Report SHA-256:
  `fe387583e8349617aaa8a860994e1a2e4244284a6e524cdfa5744ae85d425db0`
- Model-module SHA-256:
  `e3e4029e8e83a08ee9d1df8068e325a1b9f954d4fd26232de12f6c46bb8eb95d`
- Artifact SHA-256:
  `2f6beaa5cfec35870816df07faa6ce1520b77e8b3ad17cd6b50e8b9a3bcb98f3`

This artifact is a partial-source branch-reach result, not a full-source
refinement. A full secant predictor to `3/12` fails the wide, fixed, centered,
and shifted-`sigma_2` checks; the canonical next run must retain the accepted
plain `2/12` field and advance exactly one stage. Damped-secant and `5/24`
midpoint predictors are scratch-only fallback designs and require separate
schedule/configuration provenance. No density, asymmetry, outer-box, physical
field, artificial-gravity, inertial-control, FTL, or propulsion conclusion
follows.

## `e028_h0125_m4_2of12_pgsa_replay_20260722.npz`

- Date: 2026-07-22
- Purpose: fresh replay through `2/12` under the current runtime after the
  original checkpoint's exact platform-provenance mismatch
- Runtime: macOS `26.5.2`, Python `3.14.6`, NumPy `2.5.1`, SciPy `1.18.0`,
  PyAMG `5.3.0`
- Grid/source/configuration: unchanged canonical E-028 values and 12-stage
  schedule
- Replay versus original `2/12` field: bitwise equal; maximum absolute
  difference `0`
- Field SHA-256:
  `3219171452d92fa1e6f027623a318e6aed11bfe9e463a7a6e55c262251270290`
- Model-module SHA-256:
  `e3e4029e8e83a08ee9d1df8068e325a1b9f954d4fd26232de12f6c46bb8eb95d`
- Replay artifact SHA-256:
  `1cd31cc2c634c7f75bd56330c8c4f2da076fd3204bba5fd1831bb0d99c1abaa5`

This artifact isolates the macOS patch as recorded runtime drift rather than
an observed numerical-field drift at `2/12`. Timing, RSS, and runtime metadata
are expected to differ from the original report. Bitwise equality of one
accepted discrete field is a reproducibility result, not continuum or physics
evidence.

## `e028_h0125_m4_campaign_checkpoint_20260722.npz`

- Date: 2026-07-22
- Lineage: fresh macOS `26.5.2` replay through `2/12`, then exact plain-seed
  continuation through `3/12`
- Accepted amplitude: `3/12=0.25`
- Pending target: `4/12`
- Latest-stage closure: seven full Newton corrections, `280` GMRES inner
  iterations, final relative nonlinear `L2=7.01069e-12`
- Campaign totals through three stages: `26` Newton corrections and `977`
  GMRES inner iterations
- Maximum direct true-residual ratio in stage 3: `9.1512e-9`; maximum inner
  iterations in one correction: `56`
- Wide pair/spatial/time:
  `0.05654223 / 0.11308446 / 1.00000033`
- Fixed/centered spatial: `0.11277736 / 0.11325609`, no nonpositive nodes
- Post-hoc active/fixed/centered shifted-`sigma_2`:
  `0.18750000 / 0.11611764 / 0.11613725`, no nonpositive nodes
- Field SHA-256:
  `b2fcb751e8fb039d5031ddc9a5b6bd7245d13eae446d50663b652a5ba172d8ba`
- Report SHA-256:
  `4d5d14daea28a0b07ab2ba72b5556ef293f2258822136c8ce2d5ed1d1774ae9f`
- Model-module SHA-256:
  `e3e4029e8e83a08ee9d1df8068e325a1b9f954d4fd26232de12f6c46bb8eb95d`
- Checkpoint SHA-256:
  `368f569bd18cbcb0fdc443ce49703078b52953dd59155869334c10a2f3b8013c`

This checkpoint is the only accepted current-runtime resume lineage. Verify
its container hash and preserve it immutably before the next accepted-state
update. Copy it byte for byte to a separately named stage-4 working checkpoint
and resume only the copy. The report
records the resumed input field hash and path but not the pre-mutation input
container hash, so that external check is part of the audit.

## `e028_h0125_m4_3of12_pgsa_20260722.npz`

- Date: 2026-07-22
- Grid/source and accepted state: canonical E-028 values above, amplitude
  `3/12=0.25`
- Latest-stage closure and branch values: identical to the current-runtime
  checkpoint section above
- Partial-source observables: ratio at `r/r0=1` `1.422741`; maximum sampled
  gradient `3.919218` at the fixed-ray endpoint `r=12`; centered
  original/White residuals `0.96917% / 0.27903%`; sampled-charge flux deficits
  `-0.74787% / -0.74159% / -0.72356%`
- Source charge error: `-4.31633e-6` (`-0.000431633%`)
- Maximum explicit A/P/R sparse storage: about `72.6 MB` decimal
- Current-invocation peak RSS: about `1.604 GiB`; current replay campaign
  high-water is about `1.832 GiB`
- Field SHA-256:
  `b2fcb751e8fb039d5031ddc9a5b6bd7245d13eae446d50663b652a5ba172d8ba`
- Report SHA-256:
  `4d5d14daea28a0b07ab2ba72b5556ef293f2258822136c8ce2d5ed1d1774ae9f`
- Artifact SHA-256:
  `d44f43e9aa6f3e3542df570cd9999da7c6294858922dbad18af7df1798f64fef`

The loader verifies this artifact and it matches the current checkpoint field
and report exactly. Artifact existence is not itself scientific acceptance:
the driver does not enforce shifted-`sigma_2`, and a requested-final-stage
artifact can exist before a later resume would hard-stop a fixed/centered
conflict. The manual checks above are therefore part of acceptance. This is a
one-quarter-source branch-reach result, not a full-source, continuum,
artificial-gravity, inertial-control, FTL, or propulsion result.

### Pre-run stage-4 working-checkpoint warning (recorded 2026-07-22)

A scratch-only first correction from this stage-3 field toward `4/12` passes
strict GMRES, Armijo decrease, and all core wide gates, so the current driver
would save it as accepted **Newton work**. It is not an accepted amplitude
state: fixed/centered spatial minima are `-0.032523 / -0.032099` and shifted
`sigma_2` minima are `-0.044816 / -0.044262` near `(6.25,0.375)`. A second
scratch correction returns those independent checks positive. No stage-4
checkpoint or artifact was written during that pre-run audit; the accepted
2026-07-23 result is documented below.

The in-progress schema correctly labels such a field incomplete and quotes no
force, flux, or completed-target observables, but it does not store or block
fixed/centered or shifted-`sigma_2` conflicts. Therefore never mutate the only
accepted stage-3 checkpoint. Run stage 4 from a verified working copy; if
interrupted, preserve that file for forensics but restart from another clean
stage-3 copy. Accept `4/12` only after nonlinear closure, loader equality,
positive final wide/fixed/centered checks, and positive manual
active/fixed/centered shifted-`sigma_2`.

## `e028_h0125_m4_campaign_checkpoint_20260723.npz`

- Date: 2026-07-23
- Lineage: byte-identical copy of the accepted current-runtime stage-3
  checkpoint, then exact plain-seed continuation through `4/12`
- Accepted amplitude: `4/12=1/3`
- Pending target: `5/12`
- Latest-stage closure: six full Newton corrections, `237` GMRES inner
  iterations, final relative nonlinear `L2=6.80850e-9`
- Campaign totals through four stages: `32` Newton corrections and `1214`
  GMRES inner iterations
- Maximum direct true-residual ratio in stage 4: `8.44663e-9`; maximum inner
  iterations in one correction: `56`
- Wide pair/spatial/time:
  `0.03551049 / 0.07102099 / 1.00000176`
- Fixed/centered spatial: `0.07026008 / 0.07046168`, no nonpositive nodes
- Post-hoc active/fixed/centered shifted-`sigma_2`:
  `0.18749900 / 0.08547619 / 0.08535728`, no nonpositive nodes
- Centered shifted-`sigma_2` at physical steps `0.125/0.25/0.5`:
  `0.085357 / 0.096137 / 0.143379`
- Field SHA-256:
  `ec8fdb4f4050b11affb0194b4bb2eff68ab7e9ae3cf8371d54e3bf442bb7ae53`
- Report SHA-256:
  `8b2c9ee855b2216862012434a16d87777d053bbd8cd0e11e8779d39ed3e4a4db`
- Model-module SHA-256:
  `e3e4029e8e83a08ee9d1df8068e325a1b9f954d4fd26232de12f6c46bb8eb95d`
- Checkpoint SHA-256:
  `8cd1abd9f43b9076d6fb884933d055c4746fb0c37e8fd6d596840b7353c13ec4`

This accepted checkpoint is byte-identical to the completed run's
`e028_h0125_m4_campaign_stage4_work_20260723.npz`; the separately named copy
is the immutable source for the next stage. The embedded report retains the
actual working-checkpoint path used during stage 4. Preserve this file and run
stage 5 only from a new byte-identical work copy. If interrupted, restart from
another accepted stage-4 copy rather than resuming an in-progress field.

## `e028_h0125_m4_4of12_pgsa_20260723.npz`

- Date: 2026-07-23
- Grid/source and accepted state: canonical E-028 values above, amplitude
  `4/12=1/3`
- Latest-stage closure and branch values: identical to the accepted
  stage-4 checkpoint section above
- Partial-source observables: ratio at `r/r0=1` `1.809541`; maximum finite
  sampled ratio `1.894623`; maximum sampled gradient `4.940985` at the fixed
  ray endpoint `r=12`; centered original/White residuals
  `1.03375% / 0.25724%`; sampled-charge flux deficits
  `-0.84453% / -0.85054% / -0.83862%`
- Source charge error: `-4.31633e-6` (`-0.000431633%`)
- Maximum explicit A/P/R sparse storage: `72,586,832` bytes
- Current-invocation peak RSS: about `1.621 GiB`; current replay campaign
  high-water remains about `1.832 GiB`
- Field SHA-256:
  `ec8fdb4f4050b11affb0194b4bb2eff68ab7e9ae3cf8371d54e3bf442bb7ae53`
- Report SHA-256:
  `8b2c9ee855b2216862012434a16d87777d053bbd8cd0e11e8779d39ed3e4a4db`
- Artifact SHA-256:
  `4ddd280ba9b4ada9ebdb1963d92904813047577e48c750134df36ff9c06f58c1`

The loader verifies this artifact and it matches the accepted checkpoint field
and report exactly. The canonical first full correction toward this endpoint
temporarily leaves the independent fixed/centered `Gamma_2` reconstructions,
although it remains inside the solved wide gate. A separately labeled
`alpha=0.5` first-step replay keeps every accepted active/fixed/centered
`Gamma_2` audit positive and reaches the canonical endpoint to relative field
`L2=4.89e-12`; it does not replace this artifact or prove a unique continuum
branch.

Artifact existence alone remains insufficient acceptance because the driver
does not enforce shifted-`sigma_2` and can emit a requested-final artifact
before a later invocation would block a fixed/centered conflict. The manual
checks above are part of acceptance. This is a one-third-source branch-reach
result, not a full-source, continuum, artificial-gravity, inertial-control,
FTL, or propulsion result.

## `e028_h0125_m4_campaign_checkpoint_20260724.npz`

- Date: 2026-07-24
- Lineage: collision-checked byte-identical copy of the accepted
  current-runtime stage-4 checkpoint, then exact plain-seed continuation
  through `5/12`
- Accepted amplitude: `5/12=0.4166667`
- Pending target: `6/12`
- Latest-stage closure: five full Newton corrections, `217` GMRES inner
  iterations, final relative nonlinear `L2=4.82226e-8`
- Campaign totals through five stages: `37` Newton corrections and `1431`
  GMRES inner iterations
- Maximum direct true-residual ratio in stage 5: `9.47315e-9`; maximum inner
  iterations in one correction: `50`
- Wide pair/spatial/time:
  `0.02505673 / 0.05011347 / 1.00000038`
- Fixed/centered spatial: `0.05011347 / 0.05024332`, no nonpositive nodes
- Post-hoc active/fixed/centered shifted-`sigma_2`:
  `0.18748885 / 0.06204966 / 0.06180786`, no nonpositive nodes
- Centered shifted-`sigma_2` at physical steps `0.125/0.25/0.5`:
  `0.06180786 / 0.07887984 / 0.13411076`
- Field SHA-256:
  `ab5b23f15f729cb0f72589c2287e1013f8f6b05a7dbe91ad6b1debffe272f5c7`
- Report SHA-256:
  `7207528839fcdd909ed19467e6de349374c09ff2fcbd7a97e9780e568f2174c0`
- Model-module SHA-256:
  `e3e4029e8e83a08ee9d1df8068e325a1b9f954d4fd26232de12f6c46bb8eb95d`
- Checkpoint SHA-256:
  `4c2c10a53156c59b53abbc5963d9089f460c75e65b6cdc4fa1cb64d4f548977f`

This accepted checkpoint is byte-identical to the completed run's
`e028_h0125_m4_campaign_stage5_work_20260724.npz`; the separately named copy
is the immutable source for the next stage. The embedded report retains the
actual working-checkpoint path used during stage 5. Preserve this file and
run stage 6 only from a new collision-checked byte-identical work copy. If
interrupted, restart from another accepted stage-5 copy rather than resuming
an in-progress field.

A fresh deterministic stage-5 replay ends at the retained field bit for bit
and reproduces the Newton count, GMRES count, and residual. Every accepted
state and tested piecewise-affine segment passes the three
active/fixed/centered `Gamma_2` reconstructions; the smallest accepted-state
or sampled-segment fixed pair/`sigma_2` are
`0.01260698 / 0.02988896`, and centered values are
`0.01912254 / 0.05206855`. This is deterministic path evidence, not an
interval uniqueness or continuum-branch certificate.

The retained checkpoint/artifact embed only the completed field and report,
not the replay's intermediate fields, coarse-control arrays, tail ledger, or
tangent/secant calculations. Those are dated manual evidence recorded in the
living research ledger and must be recomputed for an independent audit.

## `e028_h0125_m4_5of12_pgsa_20260724.npz`

- Date: 2026-07-24
- Grid/source and accepted state: canonical E-028 values above, amplitude
  `5/12=0.4166667`
- Latest-stage closure and branch values: identical to the accepted stage-5
  checkpoint section above
- Partial-source observables: ratio at `r/r0=1` `2.233660`; maximum finite
  sampled ratio `2.466898`; maximum sampled gradient `5.881391` at the fixed
  ray endpoint `r=12`; centered original/White residuals
  `1.07590% / 0.24137%`; sampled-charge flux deficits
  `-0.91107% / -0.92872% / -0.92223%`
- Source charge error: `-4.31633e-6` (`-0.000431633%`)
- Maximum explicit A/P/R sparse storage: `72,586,832` bytes
- Current-invocation peak RSS: about `1.135 GiB`; current replay campaign
  high-water remains about `1.832 GiB`
- Field SHA-256:
  `ab5b23f15f729cb0f72589c2287e1013f8f6b05a7dbe91ad6b1debffe272f5c7`
- Report SHA-256:
  `7207528839fcdd909ed19467e6de349374c09ff2fcbd7a97e9780e568f2174c0`
- Artifact SHA-256:
  `a72166c722c947dad9da93b505fa1335633adf23bd61c33a7dfa9968b6215c84`

The loader verifies this artifact and it matches the accepted checkpoint field
and report exactly. A fresh coarse same-amplitude control supports the fine
result: matched-step common-window original/White residuals fall
`29.79% / 47.50%`, worst fixed-sphere flux-deficit magnitude falls `37.94%`,
and source-charge-error magnitude falls `93.66%`, while the `r=1` ratio
changes `+0.619%` and fine stage GMRES work rises `76.42%`.

At matched centered step `0.25`, pair minima over stages 3--5 are
`0.05711 / 0.03590 / 0.02525`, pair `0.01%` weighted quantiles are
`0.11887 / 0.09529 / 0.08334`, and the stage-5 common-window axisymmetric
nodal-quadrature weight fraction below pair margin `0.05` is `5.26e-5`.
However, `182/310365` masked nodes are below the threshold. The denominator
includes the large outer vacuum region and does not exclude a thin connected
strip or larger source-layer-relative tail. Future stages must report the
global minimum plus weighted and unweighted tails.

Artifact existence alone remains insufficient acceptance because the driver
does not enforce shifted-`sigma_2`, accepted-iterate reconstructed cones, or
tail diagnostics. The manual/replay checks above are part of acceptance.
This is a five-twelfths-source branch-reach result, not a full-source,
continuum, artificial-gravity, inertial-control, FTL, or propulsion result.

## `e028_h0125_m4_5of12_pgsa_replay_20260725.npz`

- Date: 2026-07-25
- Purpose: fresh replay through `5/12` under the exact committed
  `requirements-research.txt` fingerprint after strict resume of the 2026-07-24
  checkpoint correctly stopped on a requirements-file hash mismatch
- Runtime: macOS `26.5.2`, Python `3.14.6`, NumPy `2.5.1`, SciPy `1.18.0`,
  PyAMG `5.3.0`
- Replay versus accepted 2026-07-24 stage-5 field: bitwise equal; maximum
  absolute difference `0`
- Field SHA-256:
  `ab5b23f15f729cb0f72589c2287e1013f8f6b05a7dbe91ad6b1debffe272f5c7`
- Artifact SHA-256:
  `b3adf0714c96815ece3782232dafa5b623e6fc7dcdfeaae4239e1f52267f2ab4`

The old checkpoint embedded requirements hash
`cd1df48db71f3a60d6d85fc10d1636b64db217e1228ed733c9dc968af43dc7aa`;
the committed file has hash
`b44e38d9b1076b4de3497d8d81a2dbfb2bf0405494ea129bfe3d3d6af0e46349`.
The numerical dependencies and runtime were unchanged, but exact provenance
means even nonnumerical file drift is a hard stop. The guard was not bypassed:
the full current-provenance campaign was replayed, reproduced stage 5 bit for
bit, and only that replay was advanced. This is a reproducibility/provenance
result, not new physics evidence.

## `e028_h0125_m4_campaign_checkpoint_20260725.npz`

- Date: 2026-07-25
- Lineage: fresh current-committed-provenance replay through `5/12`, then
  exact plain-seed continuation through `6/12`
- Accepted amplitude: `6/12=0.5`
- Pending target: `7/12`
- Latest-stage closure: five full Newton corrections, `254` GMRES inner
  iterations, final relative nonlinear `L2=5.45884e-8`
- Campaign totals through six stages: `42` Newton corrections and `1685`
  GMRES inner iterations
- Maximum direct true-residual ratio in stage 6: `9.15407e-9`; maximum inner
  iterations in one correction: `59`
- Wide pair/spatial/time:
  `0.01921756 / 0.03843512 / 1.00000237`
- Fixed/centered spatial:
  `0.03306351 / 0.03278356`, no nonpositive nodes
- Post-hoc active/fixed/centered shifted-`sigma_2`:
  `0.18748363 / 0.04252053 / 0.04215838`, no nonpositive nodes
- Centered shifted-`sigma_2` at physical steps `0.125/0.25/0.5`:
  `0.04215838 / 0.06645977 / 0.12729943`
- Field SHA-256:
  `cd806ff41c0a33d541cc5c1dba44a3c7ad693ddb6b81dda5eae2ac1db8757c3e`
- Report SHA-256:
  `fe2c11e1d2e7806b12836325eaaed565137b5495efbb25417f4c6545fd3a256c`
- Full linear-field SHA-256:
  `6fe081d1b9eb5a02e88e6c0e79531f6419aa35053f75c87090cf03be1f5bc606`
- Model-module SHA-256:
  `e3e4029e8e83a08ee9d1df8068e325a1b9f954d4fd26232de12f6c46bb8eb95d`
- Checkpoint SHA-256:
  `ff82363833c84e416e020a8df56d6067b6b1f7612c41f30f6499d6b95690babb`

This accepted checkpoint is byte-identical to
`e028_h0125_m4_campaign_stage6_work_20260725.npz`. Preserve both and run
stage 7 only from a new collision-checked byte-identical copy. If interrupted,
restart from another accepted stage-6 copy rather than treating an in-progress
field as an endpoint.

The deterministic stage-6 replay ends bit for bit at the retained field and
reproduces five Newton/`254` GMRES. Every accepted state and nine tested points
on every piecewise-affine connecting segment remain in active, fixed, and
centered shifted `Gamma_2`. The smallest state/segment fixed pair/`sigma_2`
are `0.00225488 / 0.00494198`; centered values are
`0.00223272 / 0.00488521`, all on the first accepted correction. This is a
close positive path margin, not an interval or no-jump certificate.

At the endpoint's four exact active-frame ties, all `2^4=16` frame-selection
vertices assemble to one bitwise-identical Jacobian matrix. That matrix has
positive sign-normalized diagonal, nonpositive off-diagonal, one strongly
connected component, all `322319` rows weakly diagonally dominant to the
stated numerical tolerance, and `3047` strict rows. This removes the observed
tie-selection ambiguity at this endpoint, but supplies no inverse-norm,
rounding, nearby-state, or continuum bound.

## `e028_h0125_m4_6of12_pgsa_20260725.npz`

- Date: 2026-07-25
- Grid/source and accepted state: canonical E-028 values above, amplitude
  `6/12=0.5`
- Latest-stage closure and branch values: identical to the accepted stage-6
  checkpoint section above
- Partial-source observables: ratio at `r/r0=1` `2.604856`; maximum finite
  ratio `3.022631`; maximum sampled gradient `6.756110` at the fixed-ray
  endpoint `r=12`; centered original/White residuals
  `1.10908% / 0.228795%`; sampled-charge flux deficits
  `-0.962787% / -0.990948% / -0.988775%`
- Source charge error: `-4.31633e-6` (`-0.000431633%`)
- Maximum explicit A/P/R sparse storage: `72,586,832` bytes
- Current-invocation peak RSS: about `1.614 GiB`; replay-campaign high-water
  remains about `1.832 GiB`
- Field SHA-256:
  `cd806ff41c0a33d541cc5c1dba44a3c7ad693ddb6b81dda5eae2ac1db8757c3e`
- Report SHA-256:
  `fe2c11e1d2e7806b12836325eaaed565137b5495efbb25417f4c6545fd3a256c`
- Artifact SHA-256:
  `64a0fca132dd6b068c543f102c74c3ffa09a545509d9f822857cc13e179c5476`

A fresh same-amplitude coarse `(h,m)=(0.25,3)` control closes in five
Newton/`174` GMRES. Fine versus coarse changes are `+1.728%` in the `r=1`
ratio, `+0.321%` in the sampled endpoint gradient, `-29.19% / -47.15%` in
matched-step common-window original/White residuals, `-37.87%` in worst
flux-deficit magnitude, and `-93.66%` in source-charge-error magnitude.
Fine stage GMRES rises `45.98%`. Native fixed/centered margins decline with
refinement, while the matched-`0.25` centered margin improves; this is a mixed
two-grid comparison, not an asymptotic order.

At matched centered step `0.25`, the pair minimum is `0.0193653`, and
`227/310365` common-window nodes lie below pair `0.05`. They form one connected
near-midplane component over `rho=0-6.25`, `z=0-0.75`, reaching the inner
source smoothing layer. Its full-window axisymmetric weight fraction is only
`6.535e-5`, but its source-support-relative weight fraction is `0.003139`.
Threshold sensitivity confirms a real localized tail: even pair `<0.02`
contains ten nodes in one component. No sampled node has `sigma_2<0.05`.

This is a half-source discrete branch-reach result, not a full-source or
continuum refinement and not evidence of artificial gravity, inertial
control, spacetime engineering, FTL, or propulsion.

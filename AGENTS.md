# Repository Instructions

## Purpose

This is a living theoretical and numerical research workspace. Preserve the
distinction between established physics, strongly modeled results,
speculation, weak signals, and rejected paths.

## Scientific integrity

- Never describe a numerical solution as experimental evidence for a physical
  field or device.
- Never claim that known physics currently enables artificial gravity,
  inertial control, reactionless propulsion, spacetime engineering, or
  faster-than-light travel.
- State model assumptions, validity regimes, scales, provenance, and failure
  modes next to conclusions.
- Preserve negative results and hard boundaries. Do not delete an inconvenient
  failure merely because a later route looks more promising.
- Prefer primary sources and high-quality technical reviews. Record enough
  bibliographic detail for another researcher to recover the source.
- Do not silently rewrite historical log entries. Correct them explicitly and
  explain what changed.

## Research runs

Follow `Nightly_Runbook.md`. Begin by reading the canonical research files,
choose one narrow focus, and update the living ledger before closing the run.
Leave a concrete next best step.

## Models and checkpoints

- Run `python -m unittest discover -s tests -v` after model or checkpoint
  changes.
- Do not bypass checkpoint provenance, fingerprint, digest, loader-identity,
  admissibility, or convergence gates.
- Accepted checkpoints are immutable and use Git LFS. Mutable restart files
  must use a `*_work_*.npz`, `*.partial.npz`, or `*.tmp.npz` name and remain
  untracked.
- When adding or removing an accepted checkpoint, update
  `models/checkpoints/SHA256SUMS`, its checkpoint note, and the relevant
  research ledger entries in the same change.
- Preserve meaningful failed states only as dated, documented, immutable
  failure artifacts.
- Do not run full numerical campaigns in CI; CI is limited to deterministic
  unit, integrity, and compilation checks.

## Git workflow

Use a fresh `codex/*` or `claude/*` branch in an isolated worktree. Open PRs
ready for review, use squash merging, and leave `main` clean. Do not commit
secrets, local environments, mutable work checkpoints, or generated caches.

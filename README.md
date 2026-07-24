# Artificial Gravity Research Workspace

This folder is a living research workspace for persistent investigation into artificial gravity, inertial control, spacetime engineering, and adjacent physics that could eventually inform technologies often imagined in science fiction.

> [!IMPORTANT]
> This repository contains theoretical analysis and numerical experiments, not
> an experimental demonstration of artificial gravity, inertial control,
> reactionless propulsion, spacetime engineering, or faster-than-light travel.
> A solver artifact is evidence about the stated mathematical model only.

The standing premise is ambitious but disciplined:

- Artificial gravity may be a key enabling capability for deep-space habitation, high-acceleration travel, and more speculative propulsion concepts.
- Faster-than-light travel remains unsupported by known experimentally validated physics, so every idea must be tracked with its assumptions, evidence, failure modes, and testability.
- Failure is expected. Useful negative results should be preserved because they map the boundary of the possible.
- The work should combine orthodox physics, fringe-adjacent hypotheses only when clearly labeled, engineering constraints, historical dead ends, and new opportunities from modern theory and experiment.

## Core Files

- [Research_Charter.md](Research_Charter.md): mission, standards, scope, and rules of evidence.
- [Nightly_Runbook.md](Nightly_Runbook.md): exact workflow for each midnight automation run.
- [Daily_Log.md](Daily_Log.md): chronological record of nightly work.
- [Hypotheses_Register.md](Hypotheses_Register.md): ranked ideas, conjectures, and falsification status.
- [Sources_and_Notes.md](Sources_and_Notes.md): citations, summaries, and source quality notes.
- [Experiment_Backlog.md](Experiment_Backlog.md): calculations, simulations, reading tasks, and possible experiments.
- [Boundary_Map.md](Boundary_Map.md): known limits, no-go results, and places where assumptions may be revisited.
- [Open_Questions.md](Open_Questions.md): unresolved questions for future runs.

## Numerical Models

The [`models/`](models/) directory contains reproducible bounding calculations
and numerical experiments. The maintained verification target is Python 3.14.

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-research.txt
python -m unittest discover -s tests -v
```

Accepted `.npz` checkpoints and deliberately retained work snapshots are
integrity-checked research artifacts tracked with Git LFS. After cloning, run
`git lfs install` and `git lfs pull`. Their independent full-file digests are
recorded in [`models/checkpoints/SHA256SUMS`](models/checkpoints/SHA256SUMS).
Work snapshots preserve exact prior solver states so later agents can inspect
or resume the recorded path; a work suffix is not an acceptance or physics
claim. Disposable `.partial.npz` and `.tmp.npz` files remain ignored.

## Nightly Automation Purpose

Each night at midnight, Codex should spend at least 20 minutes and no more than one hour doing research and thinking, then update this folder with:

1. What was studied.
2. What was learned.
3. Which ideas became more or less plausible.
4. What failed or reached a boundary.
5. The next best question to pursue.

The 20-minute floor is a real work requirement, not just a scheduling label, and the intended use of the nightly window is deeper than a single quick calculation. If the first calculation or source pass resolves quickly, continue within the same narrow focus by adding sensitivity checks, alternate models, primary-source review, failure-mode analysis, comparison against existing boundaries, and a sharper next experiment or hypothesis. Do not stop after a short result simply because the result is decisive. A normal unblocked run should usually keep working toward the 45-55 minute range before switching fully to documentation.

The goal is not to prove a desired conclusion. The goal is to keep pushing intelligently at the boundary between known physics, engineering possibility, and speculative opportunity.

## Reuse

No open-source license has been granted for this repository. Public visibility
does not by itself grant permission to copy, modify, or redistribute its
contents.

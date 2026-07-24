# Nightly Runbook

This is the standing workflow for the midnight automation. Each run should take at least 20 minutes and no more than 60 minutes.

## Start Of Run

1. Read `README.md`, `Research_Charter.md`, `Daily_Log.md`, `Hypotheses_Register.md`, `Boundary_Map.md`, `Open_Questions.md`, and the latest entries in `Sources_and_Notes.md`.
2. Pick one narrow focus question for the night.
3. State the focus question in the new `Daily_Log.md` entry before researching.

## Research Loop

Within the time limit:

1. Search for primary or high-quality secondary sources.
2. Extract the relevant physics, assumptions, equations, constraints, and experimental status.
3. Compare the findings against the current hypothesis register and boundary map.
4. Look for one of:
   - a new possible mechanism,
   - a hidden assumption,
   - a better falsification route,
   - an analogy from another domain,
   - an engineering scaling issue,
   - a source that changes confidence in an existing idea.
5. Convert the source review into original research work for this workspace:
   - name at least one blank space between known results and the desired capability,
   - state whether that blank space is blocked by known physics, merely unengineered, or still unclear,
   - propose a new hypothesis, calculation, simulation, or experiment that could reduce the uncertainty.

## Minimum Depth Standard

The timebox exists to force deeper thinking. A run must not close just because the first calculation is decisive. Treat an early result as the start of the real work, then keep pushing inside the same narrow focus.

Before finalizing a normal scheduled run, complete at least four of the following deepening actions:

- Review at least three primary or high-quality sources, including at least one source that could weaken or complicate the emerging conclusion.
- Run a sensitivity check over the key parameter range, not just one benchmark point.
- Build an independent bounding model using different assumptions from the first calculation.
- Compare the result against at least two existing boundaries or hypotheses in this workspace.
- Audit the hidden assumptions, failure modes, and regimes where the conclusion might not apply.
- Turn the failure or boundary into a new blank-space idea, experiment, simulation, or falsification route.
- Design the next experiment/backlog item precisely enough that the following run can start without rediscovering the setup.

If the initial calculation or source review resolves before 20 minutes have elapsed, continue until the 20-minute floor is actually met. If it resolves before 45 minutes have elapsed and there is no blocker, deepen the same focus with more of the actions above rather than stopping. Preserve the narrow focus; deepen it rather than broadening into unrelated speculation.

## Update Requirements

At the end of every run, update these files as appropriate:

- `Daily_Log.md`: add a dated entry with focus, sources, reasoning, result, failures, and next step.
- `Sources_and_Notes.md`: add citations and source-quality notes.
- `Hypotheses_Register.md`: add or adjust hypotheses, confidence, and falsification state.
- `Boundary_Map.md`: add constraints or no-go results.
- `Experiment_Backlog.md`: add calculations, simulations, or reading tasks.
- `Open_Questions.md`: add or retire questions.

## Required Log Format

Use this structure in `Daily_Log.md`:

```markdown
## YYYY-MM-DD - Short Focus Title

**Focus question:** ...

**Sources reviewed:** ...

**Deepening work completed:** ...

**What changed:** ...

**Reasoning:** ...

**Failure or boundary found:** ...

**Blank space or new idea:** ...

**Hypothesis updates:** ...

**Next best step:** ...
```

## Time Limit

Work for at least 20 minutes unless blocked by missing files, tool failure, or an explicit user stop. Do not exceed 60 minutes.

Before finalizing a scheduled run, check elapsed time. If less than 20 minutes have elapsed and there is no real blocker or explicit stop, continue research and analysis under the same focus question until the 20-minute minimum is satisfied. If less than 45 minutes have elapsed, the run should usually continue with deeper source review, sensitivity analysis, alternative bounding models, or next-experiment design unless the user has explicitly asked for a shorter pass or the work is genuinely blocked.

Stop active research by 55 minutes. Use the final 5 minutes to write the log and update the registers. If the work is incomplete, preserve the thread of reasoning and schedule the next best step.

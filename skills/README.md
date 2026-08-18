# Skills

Recipes an agent follows when working with this library. Three of them, and
they divide by what you are doing:

| skill | when |
|---|---|
| [`draw-a-figure`](draw-a-figure/SKILL.md) | building a figure out of shapes that already exist |
| [`review-a-drawing`](review-a-drawing/SKILL.md) | **before reporting any drawing as finished** |
| [`trace-a-shape`](trace-a-shape/SKILL.md) | turning a photograph or sketch into a shape the library does not have |

## Why these exist, and what they are really for

`biodraw` assumes most figures will be *described*, not typed. The agent doing
the describing **cannot see the result**, which is the central problem the
whole library is arranged around: `bd.check`, `bd.explain`, the geometry pins
and the construction figures all exist to substitute for eyes.

Skills are the other half of that. They are where the accumulated judgement
lives — the things that have actually gone wrong on real drawings here, and
the numbers that catch each one.

## The fine-tuning loop

This is the process, and it is the reason `review-a-drawing` is not a static
checklist. Anyone can run it; a second developer joining should read this
first.

The maintainer of this repo speaks in two registers, and they are used
differently (see [CLAUDE.md](../CLAUDE.md)):

- **Developer hat** — "split this module", "the pins should be JSON not PNG".
  A decision about the codebase. Apply it and move on.
- **User hat** — "these two branches look mirror-like", "there's a little
  twiddle in the neck", "the image quality is too low to debug". This is
  **not** a bug report. It is a *sample of how a real user will behave*, and
  it is worth far more than its literal content, because nobody else will file
  an issue saying "your bifurcations look manufactured" — they will simply not
  use the library and say nothing.

When a user-hat comment arrives, four steps, in order:

1. **Fix the specific thing.**
2. **Name the general rule it is an instance of**, and write it down —
   `docs/PLAN.md` if it governs the repo, a skill if it governs how a figure
   gets made.
3. **Add a check to `review-a-drawing`** so the next agent catches it without
   being told. *This is the step that makes the loop actually converge.* A
   rule recorded only as prose gets read once; a rule recorded as a numeric
   check gets run every time.
4. **Go back and apply it everywhere it already applies**, not just where it
   was raised.

A skill that had to be told the same class of thing twice was not updated
properly the first time.

## What makes a skill acceptable here

Copied from `docs/PLAN.md`, because it is the contract:

1. **Name its trigger precisely** — when it applies and, as importantly, when
   it does not.
2. **Be derived from a worked example, not imagined.** Do the task once by
   hand, keep what was actually needed, cut what turned out not to be.
   Anything asserted in a skill that was never exercised is a guess.
3. **State the checks.** What the agent runs to know it succeeded, and what
   the failure looks like. A skill with no verification step is a wish.
4. **Fail loudly on ambiguity.** Where a choice is a scientific claim — which
   compartment a contact lands on, whether two cells are level — the skill
   must say *ask*, not *pick*.
5. **Ship with its example.** The folder under `examples/` it was derived
   from, so it can be re-derived and tested against a known output.

## Provenance

Every check in `review-a-drawing` names the comment that produced it. That is
deliberate: it keeps the checks honest — anything that cannot name a real
failure it caught is a guess, and should be cut.

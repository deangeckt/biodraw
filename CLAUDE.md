# Working on biodraw

How this repository is built, as distinct from what it contains. For what it
contains, see [docs/PLAN.md](docs/PLAN.md); for how to *drive* the library,
see [AGENTS.md](AGENTS.md).

## The conversation is the training signal

This library is being developed in conversation, and the maintainer speaks in
two hats. Both are data, and they are used differently.

**With the developer's hat on** — "split this module", "the pins should be
JSON not PNG", "fix the sign on that normal" — the comment is a decision about
the codebase. Apply it and move on.

**With the user's hat on** — "I want to draw something like my sketch", "these
images are too heavy", "the README should be images not text", "that code
snippet isn't clear" — the comment is something else entirely. It is a
*sample of how real users will behave*. Nobody else will file an issue saying
"your positional arguments are unreadable"; they will simply fail to use the
library and say nothing. So a user-hat comment is worth far more than its
literal content:

1. **Fix the specific thing.**
2. **Ask what general rule it is an instance of**, and write that rule down —
   in `docs/PLAN.md` if it governs the repo, in a skill if it governs how a
   figure gets made.
3. **Add a check to [`skills/review-a-drawing`](skills/review-a-drawing/SKILL.md)**,
   so the next agent catches it without being told. **This is the step that
   makes the loop converge**, and the one most easily skipped: a rule written
   as prose gets read once, a rule written as a numeric check gets run every
   time.
4. **Go back and apply the rule everywhere it already applies**, not just
   where it was raised.

Treat the accumulating set of these as fine-tuning: each round should leave
the skills measurably better at anticipating the next comment. A skill that
had to be told the same class of thing twice was not updated properly the
first time.

The evidence that step 3 is worth the trouble: of the ten bugs in
[docs/STATE.md](docs/STATE.md), **three were found by writing a new check and
running it once** — the stale axon documentation, the `.gitignore` that hid
the gallery's source, and the unlinted directory behind it. That is the
cheapest of the five ways a defect has been found here, and the only one that
keeps working after the session that discovered it ends.

The skills are the durable form of all this, and they are where a second
developer should look first — see [skills/README.md](skills/README.md). Every
check in `review-a-drawing` names the comment that produced it, so the
provenance stays visible and a check that never caught anything can be cut.

Rules that arrived this way so far, with the comment that produced them:

| The comment | The rule it became |
|---|---|
| "the code snippet should come after the blueprint images" | Image first, code second — everywhere |
| "lines like `render_hollow(ax, [part], "#FFD9D9", ...)` are not clear" | Every documented call uses named arguments with trailing comments |
| "why do tests need to hold png?" | Geometry pinned numerically; image baselines capped at two |
| "these files are too heavy to carry on GitHub alone" | Contact sheets, compact rasters, and a per-example weight budget |
| "the readme should be filled with many more examples per example" | Variants are the unit of documentation, shown as icon grids |
| "the image quality is too low to debug and fix" | The weight budget is a *publication* constraint, not a development one — quality profiles, flipped in one line |
| "the two top branches are very similar, mirror like, it shouldn't be like that" | A repeated part must not repeat exactly — pairs and runs differ by default, seeded |
| "there is a little twiddle there in the neck" | A cosmetic term that does not scale with length ends up driving something structural |
| "why so many tests are needed right now? its more a qualitative library" | Test what must be true; pin what merely is |
| "we dont need synapses which are simply dots user can add themselves" | The library draws; the figure's claims are the author's. No placement engine, no claim colours |
| "the top apical dendrite is too crowded" | A count spread over a length is a density |
| "the axon is very wierd, just keep arrows / line like connections" | Prefer the schematic where the realistic one competes for attention |
| "i want to prioritize the website over the github" | The gallery is the documentation; `README.md` is a front door that links to it, never a second copy |
| "why do we need Rebuilding these drawings subsections?" | A public page shows only what `pip install` can do; the reader's next step is an agent and the skills |
| "i prefer without the hover animation, its confusing" | Hover may affirm, never replace — if a picture is worth showing, show it |
| "delete those axon images" | Deleting code means deleting its documentation too — images, prose and links |

## Fight complexity

Your job is to keep the system small, clear, focused, and useful — whether it
is an application, library, tool, or notebook. **Not** to maximise capability.

This repo has already paid for the rule three times over: the placement
engine, the claim colours and `neuro.Axon` were all built, all worked, and
were all removed, and each removal made the library clearer. See *Things built
and then deliberately removed* in [docs/STATE.md](docs/STATE.md) — that list
is the evidence, and it should keep growing.

Before adding anything, ask:

- What specific problem does this solve?
- Is it important enough to justify permanent complexity?
- Can we improve or simplify something that already exists instead?

Default to:

- **Delete before adding.**
- **Improve before creating.**
- **One obvious way** before multiple ways or settings.

### Keep changes focused

- Do not perform unrelated refactors or expand the scope of the task.
- Do not create trivial tests to increase coverage. (The standing rule here is
  already *test what must be true, pin what merely is*.)
- Do not run unrelated tests.

### Push back

- Do not blindly implement requests if alternatives exist.
- If something is unnecessary, say so, or recommend the smaller alternative.
- You have permission to say no, or to ask for evidence.

## Ask, don't assume

The maintainer prefers being asked. When a decision has more than one
defensible answer — an API shape, a scope boundary, what a default should
be — use the question tool with concrete options rather than picking silently
and explaining afterwards. Questions are cheap; a wrong assumption compounds
through every example built on it.

Exception: routine judgement calls with an obvious default. Do not ask which
variable name to use.

## Report honestly

- Say what was verified and what was not. "Tests pass" and "it looks right"
  are different claims.
- When a bug is found in ported code, say so plainly and say how it was found.
  Two have been found this way already, both invisible in the configuration
  the original ever drew.
- Never regenerate a pin or a baseline without describing what moved.

## Never

- Commit without being asked.
- Strip the tuning comments. They record why a number is what it is, usually
  after something looked wrong, and they are the most expensive thing here to
  rediscover.
- Add a runtime dependency beyond `numpy` and `matplotlib`.
- Let a shape ship without anchors, a pin, and an entry in an example.

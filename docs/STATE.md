# Where things stand

A running handoff. Read this, then [CLAUDE.md](../CLAUDE.md) for how the repo
is developed and [PLAN.md](PLAN.md) for where it is going.

Last updated: session 2 (2026-08-18). Nothing has been committed yet.

## Built and verified

**200 tests pass, `ruff check .` clean, all 38 example files across seven
folders regenerate byte-identically.**

| | |
|---|---|
| `biodraw/core/` | `geom`, `paths`, `profile` (+ the traced spine), `branch`, `render`, `anchor`, `shape` (+ `Layer`), `scatter`, `connectors` |
| `biodraw/neuro/` | `Pyramidal` (soma, forked apical, basals, spines) · `Basket` (round soma, aspiny dendrites, forks) |
| `skills/` | `draw-a-figure`, `review-a-drawing`, `trace-a-shape` |
| `biodraw/cells/` | `Blob` — wall, nucleus, nucleolus, scattered organelles, protrusions · `Sheet` — epithelial row, brush border, basement membrane, curvature to a closed ring |
| `biodraw/layout/` | `contact_sheet` |
| `biodraw/style/` | three palettes |
| `biodraw/io.py` | `canvas`, `fit`, `save` (vector, SVG hygiene, byte-reproducible), `save_compact` (rasters) + three quality profiles |
| `examples/` | `dendritic_spine`, `pyramidal_cell`, `generic_cell`, `epithelial_sheet`, `basket_cell`, `wiring`, `circuit_motifs` — ~1.6 MB at `review` quality |
| `tests/` | 50 numeric shape pins + 2 image baselines |

## Decisions taken

MIT · objects + anchors for people, introspection + checks for agents · core
is domain-neutral, `neuro` and `cells` are the domains · matplotlib with SVG
hygiene · primitives pinned numerically, images capped at two · tracing is a
**skill**, not a parser · the image weight budget is a *publication*
constraint, relaxed to the `review` profile until this repo goes public ·
**test what must be true, pin what merely is** · the library draws, the
figure's claims are the author's.

## Things built and then deliberately removed

Worth recording, because each was a real answer to "where does this library
stop":

- **The contact-placement engine** (`core/placement.py`) — allocated a total
  across compartments and chose the anchors. That is the figure's scientific
  logic, not drawing. Once a cell is drawn, marking it is a line of matplotlib
  against public anchors.
- **The palette's "claim" colours** (`spine`, `shaft`) — they existed only to
  serve that engine, and they were one paper's argument living inside a
  general library. The palette is identity-only now.
- **`neuro.Axon`** — a tapered tube with Gaussian bouton swellings and Rall
  collaterals. It worked, and at the size an axon appears in a circuit panel
  it read as a fat beaded worm competing with the cells it connected. A
  projection is now a line with a mark on the end.

All three were removed on the maintainer's user-hat feedback, and all three
made the library smaller and clearer. The pattern is worth keeping in mind:
the failure mode of a drawing library is doing the author's thinking for them.

## Bugs found, and how

Seven now, and the pattern is worth noting: **none were found by the test
suite as it stood.** Three were found by computing a number on suspicion, two
by Dean looking at a drawing, one by a test written while adding a new shape,
one by a guard raising during an example build.

From the ported seed code:

1. **Soma anchor normals pointed inward.** Every connector landing on a soma
   would have reached through the cell. Replaced the sign arithmetic with a
   test against the body's own centre.
2. **`neck_polygon` filleted the right base corner with the wrong sign**,
   pushing the control point outside the body — a spike, not a round. Caught
   by the geometry pins. Only visible at `basal=0`, which figure 7 never drew.

From session 1's own code:

3. **`Branch.child` keyed off the local tangent**, which on a short branch is
   dominated by the waver's derivative (measured 39.5° off vertical). Forks
   came out lopsided. Now measures from the branch's nominal axis.

From session 2:

4. **The waver's cycle count did not scale with branch length.** `wave_n` is a
   count, not a frequency, so a forked apical drove its short trunk at up to
   **four times** the rate the drawing was tuned at — 3.56 cycles/unit against
   a reference of 0.89 — and swung it 44° off axis against 22°. That is the
   "twiddle" Dean saw above the soma once the images were rendered big enough
   to see it. Fixed by giving `Branch` a `wave_per` (wavelength) and setting
   the cell from `Pyramidal.WAVE_PER`; the unforked cell at the default
   `trunk_len` is unchanged by construction, and six pins moved.
5. **`Sheet`'s lateral bow ate the gap between neighbours** — caught by a test
   asserting that two cells do not touch, written while building the shape.
6. **`bd.save` was not byte-reproducible.** matplotlib stamps `<dc:date>` into
   every SVG and salts clip-path ids from a per-process `uuid4`. Determinism
   is a stated non-negotiable and CI would have failed on the one committed
   SVG. Pinned via `io.SVG_HASHSALT` and `metadata={'Date': None}`.
7. **The fork crotch showed a spur** (Dean, from the higher-res images). Three
   compounding causes, all measured:
   - each daughter took the trunk's *full* width, so `paths.buried_base` had
     no depth at which its flat base chord was both clear of the trunk's tip
     and inside its wall — the joint was literally unbuildable. Daughters are
     now sized by `paths.rall_widths` (cross-sections sum to the parent's), so
     both come out thinner than the trunk; even at `fork_ratio=1.0` they are
     0.63 of it.
   - `base_ext` was a fixed 2 x the daughter's own width, which knows nothing
     about the angle and swung the chord out through the far wall. Now
     searched numerically against the trunk tube *as drawn*, so taper and lean
     are accounted for.
   - the real fix: a forked trunk was drawn **open-ended**, which means "this
     process runs off the page" and leaves the daughters nothing to bury into.
     A fork tip is a junction, not an end. Capping it gives the crotch a
     rounded bottom, which is what a real bifurcation has.

   Measured across the nine variants of `forks.png`: 12 of 18 base chords
   exposed before, 6 after the Rall and burial fixes, **0** after capping.
   An interim attempt measured the joint angle from the trunk's *local
   tangent* rather than its axis, which on a short trunk sits ~20° off and
   turned a 57° daughter into a 78° one — the same "structure must not inherit
   cosmetic noise" trap `Branch.child` already documents.

## Open, in priority order

1. **`bend` has the same length-scaling problem the waver had, and is not
   fixed.** It is an absolute across-offset at the tip, so a short branch
   leans at a steeper angle for the same number: the forked trunk still peaks
   at 31° off axis against the unforked apical's 22°, and the lean term is
   what dominates that. The waver fix took the trunk from 44° to 31° and
   removed all four sign reversals, so the S-kink is gone — but the remaining
   9° is this. It is **not obviously a bug**: an absolute offset means a
   longer branch is gently bowed and a short one visibly bent, which may be
   what a drawing wants. Making it a fraction of length would change how wide
   every fork splays, so it wants a decision rather than a patch.
2. **Milestone 4 — layout, style presets, export.** The multi-panel assembler,
   `style.use('paper'|'poster'|'slides')` to own the point-valued knobs, panel
   letters. `examples/circuit_motifs/` currently does its panels by hand with
   `plt.subplots`, which is exactly the thing milestone 4 should absorb.
3. `tools/build_gallery.py --check` cannot distinguish "untracked" from
   "modified", so it exits 1 in this never-committed repo whatever the state.
   It will start working the moment `examples/` is committed; until then,
   verify determinism by building twice and diffing hashes.
4. `neck_polygon` is still specialised to an upright triangle meeting a
   vertical tube; the general version would subsume it.
5. GitHub URLs guess `deangeckt/biodraw` in `pyproject.toml` and
   `CITATION.cff`.
6. The main `README.md` has gained a positioning section and the variant
   grids, but its example list and status section still predate `cells`,
   `Basket`, `Axon` and the wiring. Worth a pass now there are seven folders
   to build it from.

## Before publishing

One line: `biodraw/io.py`, `DEFAULT_QUALITY = "review"` → `"compact"`. Then
rebuild the gallery and commit the smaller images. Current cost of the higher
quality is about 2.3x the bytes; the seven folders total ~1.9 MB at `review`
and would be roughly 800 kB at `compact`.

## The skills, and the loop they encode

`skills/` now exists: `draw-a-figure`, `review-a-drawing`, `trace-a-shape`,
with [`skills/README.md`](../skills/README.md) carrying the contract.

`review-a-drawing` is the one that matters, and it is **not** a static
checklist — it is where a user-hat comment gets converted into a numeric
check. That is step 3 of the loop in `CLAUDE.md`, and the step most easily
skipped: a rule written as prose gets read once, a rule written as a check
gets run every time. Every check in it names the comment that produced it, so
a check that never caught anything can be identified and cut.

## The sketch exercise, for the skill

Dean supplied a whiteboard photograph and the naive prompt *"let's draw a
python-based image like my drawing showing dendritic spines"*. What it
actually took, in order:

1. **Turn the picture into a parts list** — counts, angles, fractions — before
   any code. One triangular soma; a bare apical trunk; the apical **forks at
   ~40%** into daughters splaying ~35°; two basals at ~55°; large spines
   clustered near tips.
2. **Check the inventory against the library and name the gap out loud.** The
   apical fork did not exist.
3. **Fix the gap in the core, not the domain** — `Branch.child()`, which also
   serves axon arbors and astrocytes.
4. **First render was wrong** — lopsided fork.
5. **Diagnose by computing, not by looking.** One number (39.5°) found it.
6. **Second render: symmetric but a tulip** — daughters curving inward, which
   reads as two branches about to rejoin. Flipped the bend sign.
7. **Third pass, session 2: symmetric was itself the bug.** A bifurcation
   drawn as a mirror reads as a symbol for branching rather than as something
   that branched. Daughters now differ in length, calibre and angle from one
   `fork_ratio`, and the basal legs likewise.
8. **Lock it** — but lock the *invariants*, not the appearance. An earlier
   test asserted the daughters were mirror images, which made the defect the
   specification and had to be deleted before the bug could be fixed.

The transferable lessons, which are the skill's real payload: inventory before
code; name gaps rather than routing around them; fix gaps in the core;
diagnose numerically because the agent cannot see; **document the surprising
defaults**, since a naive agent picks `relative_to="tangent"` every time and
then chases the error with `angle_deg`, which never converges; and render big
enough to see, because two defects sat in the committed images for a whole
session at 100 dpi.

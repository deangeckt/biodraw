# Where things stand

A running handoff. Read this, then [CLAUDE.md](../CLAUDE.md) for how the repo
is developed and [PLAN.md](PLAN.md) for where it is going.

Last updated: session 7 (2026-08-19). Pushed to
[github.com/deangeckt/biodraw](https://github.com/deangeckt/biodraw) and
**live at [deangeckt.github.io/biodraw](https://deangeckt.github.io/biodraw/)**.

## Built and verified

**356 tests pass, `ruff check .` clean, all 79 example images across
seventeen folders regenerate byte-identically, and the sixteen-page gallery
rebuilds from its content modules.** Run them with `py -3.12` on this
machine — `python` is a Windows Store stub here.

| | |
|---|---|
| `biodraw/core/` | `geom`, `paths`, `profile` (+ the traced spine), `branch`, `render`, `anchor`, `shape` (+ `Layer`), `scatter`, `connectors` |
| `biodraw/neuro/` | `Pyramidal` (soma, forked apical, basals, spines) · `Basket` (round soma, aspiny dendrites, forks) |
| `skills/` | `draw-a-figure`, `review-a-drawing`, `trace-a-shape` |
| `biodraw/cells/` | `Blob` — wall, nucleus, nucleolus, scattered organelles, protrusions · `Sheet` — epithelial row, brush border, basement membrane, curvature to a closed ring |
| `biodraw/animals/` | `Mouse`, `Fly`, `Zebrafish`, `Worm` — silhouettes on a shared `Animal` base that carries `size` and `facing` |
| `biodraw/genetics/` | `Repeat`, `Promoter`, `CDS`, `Terminator` — SBOL construct glyphs on a `core.Track` — plus `Protein`, a lobed body with domain tags and a `cleft` anchor |
| `biodraw/micro/` | `Bacterium` — a capsule body whose named forms are *settings* (length, `curve_deg`, `twists`), plus capsule, nucleoid, granules, flagella and pili |
| `biodraw/layout/` | `contact_sheet` |
| `biodraw/style/` | three palettes |
| `biodraw/io.py` | `canvas`, `fit`, `save` (vector, SVG hygiene, byte-reproducible), `save_compact` (rasters) + three quality profiles |
| `examples/` | `dendritic_spine`, `pyramidal_cell`, `basket_cell`, `bipolar`, `granule`, `purkinje`, `astrocyte`, `radial_cell`, `styles`, `wiring`, `circuit_motifs`, `generic_cell`, `cell_atlas`, `epithelial_sheet`, `bacteria` — `build.py` + images, ~2.8 MB at `review` quality |
| `site/` | the gallery: index with category filter and search, **13 cards across three categories plus one standalone page** (drawing styles, in the masthead and a band beside the grid), built from `site/content/*.py` by `tools/build_site.py`. Root `index.html` + `.nojekyll` so GitHub Pages serves it from the repository root — **live**, and held to the catalog budget by `check_catalog` |
| `tests/` | 94 numeric shape pins + 2 image baselines |

## Decisions taken

**Session 7, last.** `biodraw.animals` — mouse, fly, zebrafish, worm — with
`examples/animals/` and a fifth gallery category. The direction that shaped
it: *"use very simple drawings, not complex realistic images, sometimes an
outline is even enough"*, and *"grab text book images, take the basic ones"*
— which is now a rule in PLAN: **a reference is a parts list and a set of
proportions**, read and then written as numbers, never traced and never
committed. A traced picture has no knobs, which is the entire argument for
this library over a stock one.

`facing` is the knob the category exists for, and it lives on the base class.
Two smaller things came out of the build, both worth keeping:

- `Layer` gained **`wall_lw`** (a number, or `'0.8x'` as a multiple). A
  zebrafish stripe stroked at the body's wall weight reads as a pipe laid on
  the fish rather than as a marking in it;
- an animal's `wall` anchors are taken over **what is drawn**, layers
  included. Computed from `_forms()` alone they sat under the fly's own
  wing — the one place a label must not go. The test found that, not the eye.

**Session 7, before that.** Milestone 10's genetics half shipped: `core.Track`
and `biodraw.genetics`, with `examples/inducible_construct/` and a fourth
gallery category. The design decision worth keeping is where the line fell —
**the track is in `core`**, because "lay parts along an axis, each consuming
its own width" is a domain map, an ideogram, a gene model and a timeline as
much as it is a construct, and `Sheet` cannot do it (there the pitch is the
input and the cells are interchangeable). `genetics` supplies only glyphs.

**No text is drawn by the library**, which is the same call as the synapse
dot and the claim colours: every glyph carries a `label`, the track exposes
`label` anchors that hug each glyph and `tick` anchors on a shared baseline,
and the figure writes its own text. The asymmetry is not cosmetic — the first
draft put the promoter's name inside the coding sequence beside it, because a
promoter's underside *is* the backbone.

Also decided this session, and recorded in PLAN: **microscopy means the field
of view**, not the equipment — a section outline, a field at a stated
magnification and density, a scale bar that knows its units, an inset box —
and it stays queued behind `annotate.scalebar` and the panel machinery.
**Animals are unblocked**, with the direction being simple silhouettes built
from the core rather than traced or downloaded art.

**Session 7, earlier.** Six user-hat comments, and the four that changed the
shape of the catalog rather than one page of it:

- **each named cell type is its own card** — `bipolar`, `granule`,
  `purkinje` and `astrocyte` are example folders and gallery pages now.
  Nobody looking for a Purkinje cell searches for "neuron types". The family
  argument stayed behind on a *Radial body plan* card, which is also the
  entry point for a cell the library does not name;
- **wiring and circuit motifs are one card**, over two example folders. That
  needed the site builder to stop assuming a page *is* a folder: an image may
  now be written `wiring/bus.png`, and a page may list the `examples` it
  draws from;
- **the styles page left the grid.** A card is a drawing; a property of every
  drawing belongs in the chrome. `PAGE["standalone"] = True` builds the page,
  puts it in the masthead of every page and renders a full-width band beside
  the grid — all three from the one dict;
- **the spine grew the knobs it was missing.** `Profile.place(head=, neck=)`
  scales the head and the neck widths of any traced profile, blended across
  the shape and leaving every length alone, so `head_offset` — what a
  connector aims at — is untouched. Thin, stubby, mushroom and long-necked
  spines are that pair plus `size` and `extend`, not four traced outlines.

`Purkinje`'s default moved from two primaries over 34 degrees to three over
55, and its two pins with it: at portrait size the old one read as a
two-pronged fork whose trunks crossed their own daughters into a lattice.
Nothing else in the suite moved.

Also, from the same session and worth keeping: `save_compact` pads 0.02 inch
instead of matplotlib's fixed 0.1, and `build_gallery` reports loose frames
on every run. See the image weight budget in PLAN.md.

**Session 6, last.** `render_skeleton` and `Shape.draw(style='skeleton')`
— a second drawing *language*, not a re-ink. The first styles page
offered six "styles" that were one style at different linewidths and colours,
and Dean said so. A hollow cell claims a process has a width and a wall; a
skeleton claims it exists and connects two places, which is what a circuit or
connectome figure asserts and the only one of the two that survives at small
sizes, where two walls a fraction of a point apart merge into a smudge.
`Shape._skeleton()` returns `None` by default and `draw` refuses rather than
guesses — a blob is an area, not a set of processes.

**Session 6, later still.** `neuro` gained four cell types — `Bipolar`,
`Granule`, `Purkinje`, `Astrocyte` — and none of them is a new module. The
implementation behind `Basket` moved to `RadialCell` (a soma with processes
leaving it, generalised with recursive `depth`), and all five are that shape
at different settings, the same call `micro.Bacterium` makes for its named
forms. `Basket`'s 60 existing pins were **unchanged by the refactor**, which is
what made it safe to do. Direction from the maintainer: **breadth over depth** —
circuits are done, and a new shape is worth more to a catalog than a better
arrangement of the shapes already in it.

Worth recording as a limit rather than a bug: **the branch recursion does not
avoid itself.** Branch count is `dendrites * (2^(depth+1) - 1)`, so density
climbs much faster than it reads — three processes at depth 4 is **93**
branches sweeping one arc, and they cross until the union fuses the fan into a
lattice. Past about depth 3 the extra generation adds crossings, not detail.
(This paragraph said "forty-five" until session 7, when someone multiplied it
out. 45 is the same cell one generation *down*.)
The named forms are tuned under that ceiling and `examples/radial_cell/`
shows it happening.

**Session 6, later.** The default palette is **red / green / blue** —
excitatory red and inhibitory green, the convention most neuroscience readers
already carry, so a figure spends none of their attention teaching it. That
pair is the classic colour-blind hazard and the palette docstring says so:
structure carries the distinction first (a triangle is not a round soma), and
`palettes['colorblind']` is one argument away.

`examples/summary_figure/` was **built and then removed the same session**. It
reproduced a journal figure closely, and the ask had been to expand the
catalog with new *styles* of neuron — a reference figure is a source of
capabilities, not a thing to clone. What survived is the capability:
`connect_bus` moved to the `wiring` page where connectors belong, and
`examples/styles/` took its place — the same two cells under six house
styles and four detail levels, which is a catalog entry rather than one
figure. **Circuits are done for now**; the maintainer's direction is breadth,
so new shapes come before better arrangements of existing ones.

**Session 6.** The palette's default is no longer the seed paper's red/blue —
Dean's point that *"these specific blue and red are from my paper, you dont
have to commit to those"* is the general case of a default inherited from one
figure being a placeholder. It is now blue / lavender / sage, chosen off a
rendered comparison of five candidates rather than argued in hex. Its slots
are renamed `primary` / `secondary` / `tertiary`: the old
`excitatory` / `inhibitory` read well in `biodraw.neuro` and nowhere else, and
`examples/epithelial_sheet` was already colouring a **nucleus** with
`palette["inhibitory"]` for want of a third slot. Gallery categories are now
**three, mirroring the domain packages** — Neuroscience, Cells & tissues,
Microbes — where five had put nine pages behind five filters, three of which
were the same package.


MIT · objects + anchors for people, introspection + checks for agents · core
is domain-neutral, `neuro`, `cells` and `micro` are the domains · matplotlib with SVG
hygiene · primitives pinned numerically, images capped at two · tracing is a
**skill**, not a parser · the image weight budget is a *publication*
constraint, relaxed to the `review` profile until this repo goes public ·
**test what must be true, pin what merely is** · the library draws, the
figure's claims are the author's · **no CI** — verification is local, because
the only check that mattered could not pass on a hosted runner · **the gallery
is the documentation**, `README.md` is a front door that links to it, and the
reader's next step is `pip install biodraw` and an agent pointed at the skills,
never a clone.

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

Twenty-one now, and the pattern is worth noting: **none were found by the
test suite as it stood.** Session 7 added five. Three were prose and pictures
that had quietly stopped matching the code; the other two were in a module a
day old, and both were found by *writing its tests*, which is the cheapest
this list has ever recorded:

19. **A promoter drew 0.0175 outside its own span.** The stem is a walled
    centreline and the centreline ran up `x0` itself, so the wall landed left
    of the glyph's own span — and a track lays the next glyph by width alone.
    Invisible at the default gap of 0.09; an overlap at a smaller one. Found
    by `test_every_glyph_stays_inside_its_own_span`.
20. **The protein's cleft search stopped inside the body.** The ray walked
    `2.2 x reach`, which is shorter than a lobe, so it never left the body
    and every opening reported the same depth — the one number the open/closed
    pair of drawings is *about*. Found by
    `test_opening_the_body_moves_the_cleft_in_toward_the_hinge`.

And the three from earlier in the session:

16. **The motifs key said "blue, bar — inhibition".** The drawing had used
    `palette['secondary']` since the palette went red/green two sessions
    earlier, so the key on the live site named a colour that was not in the
    figure. Found while merging the wiring and motifs pages, by reading the
    build script the page was describing.
17. **The branch-count arithmetic was wrong in two docstrings and one
    handoff note** — "three primaries at depth 4 is forty-five branches" is
    the same cell one generation down, and "two at depth 3 is fourteen" is
    30. Found by multiplying it out. The example sheets now print
    `len(cell._branches())`, so the number on the page comes from the cell.
18. **Loose frames.** `examples/dendritic_spine/branch.png` filled 62% of its
    own width, and the three emptiest images in the catalog were all on the
    page a reader had just complained about. Found by writing check 13 and
    running it once — which also caught a *new* one (`bipolar.png`, 61%) an
    hour later, in a folder created that same session. Three were found by computing a number on suspicion, two
by Dean looking at a drawing, one by a test written while adding a new shape,
two by a guard raising during an example build, and the other six by writing a
*new* check and running it once — which is the cheapest of the five and the
argument for step 3 of the loop in `CLAUDE.md`.

Session 4 sharpens that argument. Its four defects were all found by running
`review-a-drawing` against a **new example built on old code**, which is the
cheapest bug-finding move this repo has: a new drawing exercises the existing
shapes in configurations nothing had asked for before — flattened, bent,
twisted, jittered — and those are exactly the configurations where the
symmetric default hides everything.

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
   is a stated non-negotiable and the rebuild check would have failed on the
   one committed SVG. Pinned via `io.SVG_HASHSALT` and `metadata={'Date': None}`.
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

8. **`examples/wiring/README.md` had gone stale without anyone noticing.**
   It still documented `neuro.Axon` — removed in session 2 — and referenced
   five images of it (`axon.png`, `boutons.png`, `bouton_shape.png`,
   `arbors.png`, `ends.png`) that were not on disk. Its title was still "Axon
   and wiring", and two other READMEs linked to `../axon_and_wiring/`, a
   folder that never existed under that name. Found by writing the gallery's
   image-existence check, which is now the standing guard against it. The
   pattern holds: **deleting code leaves its documentation behind**, and
   nothing was watching the prose.

9. **`.gitignore` was hiding the entire gallery, source included.** Line 168
   of the Python template `.gitignore` is `/site`, meant for mkdocs output.
   `site/` here is *authored* — the seven content modules hold every word of
   prose migrated out of the READMEs — and all sixteen files were invisible to
   `git status`. The READMEs were already deleted, so a clean checkout would
   have lost the lot. Caught by listing what a commit would actually contain
   rather than trusting a clean-looking status. The rule: **a template
   `.gitignore` encodes someone else's directory names**, and `/site`,
   `/docs`, `/build` and `/dist` are all plausible source directories in a
   project that is not theirs.

10. **`ruff` had never linted `site/`, because ruff respects `.gitignore`.**
    Un-ignoring `/site` surfaced 18 pre-existing E501s in one step. Worth
    knowing in both directions: a gitignored directory is *unlinted*, and
    un-ignoring one will look like it introduced errors it merely revealed.
    Resolved with a scoped `per-file-ignores` for `site/content/*.py` covering
    **E501 only** — those strings are snippets a reader copies, and wrapping
    them at 79 would reflow the code the page is teaching.

From session 4, all four found by pointing `review-a-drawing` at a new
example rather than at new code:

11. **`Blob` gave its protrusions a cycle *count* while jittering their
    lengths**, so the short ones wiggled faster than the long ones — measured
    at **1.88x** across the six pseudopodia of the cell atlas's macrophage,
    against the 1.2x the checklist allows. The third appearance of the same
    defect (`Branch`, then `Pyramidal`, now `Blob`), and the reason the
    bacterium's flagella were written with a wavelength from the start. Fixed
    by deriving `wave_per` from the nominal protrusion length; `wave_n` keeps
    its meaning as a count *at that length*, so `geom_kw` still reads
    naturally. Two pins moved.

12. **Every `Blob` wall anchor and protrusion root sat off the drawn wall on
    any non-round cell.** `superellipse` applies its wobble at the *parameter*
    angle; `Blob.wall_radius` re-applied it at the *polar* angle. Those are
    the same number only when `a == b`, so the error was exactly **0** on
    every round body and grew with flattening — 0.011 local units at
    `aspect=0.72`, on a body of radius 0.55.

    The instructive part is that **a test for this already existed and
    passed.** It ran only at the near-round default, and it measured to the
    nearest *vertex* at a tolerance of 0.02 while the wall carries 240 of them
    — so the sampling alone was 0.012. Fixed with `paths.superellipse_param`,
    the exact inverse of the forward map; the test now runs at three aspects
    and measures to the nearest edge.

13. **`Bacterium`'s nucleoid escaped through the wall on any curved body.** It
    was built by scaling the centreline toward its own centroid, which walks
    off the arc the body was drawn on: 26 points outside the wall on a cell
    bent 30° with a twist in it, and 0 on a rod. Now trimmed *along* the axis,
    so it follows whatever curve the body has.

14. **The staphylococcus cluster drew seven cells through each other** —
    eleven overlapping pairs out of twenty-one — because its slots were
    written as if they were in diameters when they are in radii. And the
    palisade was offset along the rods' own long axis rather than across it,
    putting four cells end to end and straight through one another. Both are
    example-side, both were invisible until check 7 was run on them, and the
    lesson is the ordinary one: **spacing is a clearance, and a clearance is a
    number you check, not a number you eyeball.**

15. **Every example's output depended on which folders sorted before it.**
    `build_gallery.py` runs all of them through `runpy` in **one
    interpreter**, and every `build.py` sets `plt.rcParams` at import time —
    so they leaked forward. `examples/bacteria/` turns the top and right
    spines off; `examples/basket_cell/` only sets the font size and had always
    been first alphabetically. Adding `bacteria` put it ahead of `basket_cell`
    and silently changed that example's committed blueprint, 170 bytes'
    worth, with its geometry provably unchanged (same sha before and after).

    Caught by not believing a `git status` line: `basket_cell/blueprint.png`
    was modified and nothing in the diff explained why, and rebuilding that
    example **on its own** reproduced the committed file exactly — which is
    the tell, because it means the full run and the single run disagree, and
    `--check` assumes they do not. Fixed by wrapping each script in
    `matplotlib.rc_context()`.

    Worth holding on to: this had been latent since the first example, and it
    could only ever be triggered by **adding** one. A determinism check that
    only ever runs the same set in the same order cannot see it.

## Open, in priority order

0. **Three categories Dean has asked for: animals, microscopy and genetics.**
   Written up as milestone 10 in [PLAN.md](PLAN.md). **Genetics is now
   unblocked** — see 0b. Animals wants a decision between traced silhouettes
   (free today, vary only in scale) and a jointed body plan (varies in pose,
   needs a core addition) — the recommendation is silhouettes first.
   **Microscopy is blocked on what it means**: equipment (a microscope, a
   slide) is the case this library's own scope section says to download from
   BioArt rather than draw, while a field of view — section outlines,
   magnification, density, scale bars, inset boxes — varies and is exactly
   what no stock library can offer. Ask before building.

0b. **Both reference figures have arrived — the block is lifted.** Dean
   supplied screenshots in session 6, after two sessions of failed fetches
   (Nature's `idp.nature.com` gate and Elsevier's `linkinghub` interstitial).
   **Do not attempt to fetch either again.** The screenshots were pasted into
   the conversation and are not in the repository — they are figures from
   published papers and should not be committed — so **the inventories in
   [PLAN.md](PLAN.md) milestone 10 are the record**. Work from those. If
   something is genuinely missing from them, ask Dean to re-send the image
   rather than guessing or re-fetching:

   - **Genetics** — figure 1, `doi.org/10.1016/j.tibtech.2023.03.007`,
     chemically and light inducible expression systems. Parts list is a
     **construct track** (repeat box with *n* bars, promoter pentagon, CDS
     box, terminator, transcription bent-arrow that can be struck out) plus a
     **protein layer** (lobed body, crescent, lumpy body, domain tags,
     ligand dot, RNA hairpin). One real core addition: **a track** — lay parts
     along an axis, each consuming its own width — which is not a genetics
     primitive at all and would also draw a domain map, an ideogram or a
     timeline. Suggested first example: `examples/inducible_construct/`.

     Note for the record: this page previously argued genetics on **double
     helices, plasmid maps and exon/intron structure**, and the figure
     contains none of them. The reasoning was right and the parts list was
     wrong, which is the sharpest evidence yet for taking the inventory off
     the figure rather than off the field.

   - **The neuron summary figure** — figure 7,
     `nature.com/articles/s41593-025-02004-2`. This is a **style, not a
     domain**, and it needs almost no new shapes. Three gaps, in order of
     size: **orthogonal connector routing** (its arrows are a shared bus that
     drops, runs along one horizontal and turns up into targets at right
     angles — `core.connectors` draws curved cubics only, and a bus is what
     most summary figures actually use); a **crossbar tuft** (each forked
     apical ends in short transverse dashes instead of spines, i.e. a bar
     profile through `Branch.decorate`); and **flat solid cells**
     (`fill=edge`), which the library does today and no example demonstrates.
     Suggested example: `examples/summary_figure/` — the first catalog entry
     that is a whole figure rather than a shape or a motif.

1. **Milestone 4 — layout, style presets, export.** Not built, but **the two
   design decisions it was stuck on are taken** (session 5, with Dean), so it
   is ready to start:

   - **`style.use` writes matplotlib rcParams and nothing else.** biodraw's
     point-valued knobs take their defaults from the rc key that already means
     that thing: `wall_lw` ← `patch.linewidth` (walls are `PathPatch`es),
     connector `lw` ← `lines.linewidth`, `cap_size` ← `lines.markersize ** 2`
     (the endcap dot is a marker). The reason is **bug 15**: `build_gallery.py`
     wraps each script in `matplotlib.rc_context()`, which protects rcParams
     and would *not* protect biodraw-owned module state — so a global
     `style.use` over its own registry reopens that bug in a form the existing
     fix cannot catch. As a bonus this subsumes the 7 hand-styled
     `ax.legend(fontsize=7.5, frameon=False)` calls and the 12 hand-styled
     `ax.set_title(fontsize=10, loc="left")` calls, which are rcParams already.
   - **`bd.panels` does setup only** — `panels(rows, cols, size=, titles=,
     letters=)` returns axes already frameless, aspect-locked, titled and
     lettered, and `tight_layout`s on the way out. **`bd.fit` stays the
     caller's**, because it genuinely varies: several sites fit to a custom
     bounding box rather than to `shape.points`.

   Scope is **15 sites across 9 `build.py` files** repeating
   `plt.subplots(dpi=150)` → `bd.canvas(ax=ax)` → draw → `bd.fit` →
   `ax.set_title(...)` → `fig.tight_layout()`.

   One measurement worth having before starting: **every image-producing call
   in `examples/` passes `wall_lw`, `lw` and `cap_size` explicitly** — only
   the reader-facing snippets in `site/content/` use the defaults. So the
   signature defaults can move to rcParams **without moving a single committed
   image**, and `paper` should be defined as exactly today's numbers
   (`patch.linewidth` 1.0, `lines.linewidth` 1.2, `lines.markersize`
   `sqrt(26)`). That makes byte-identity the acceptance test for the whole
   refactor. `figure.dpi` deliberately stays **out** of the presets:
   `io.QUALITY` already owns pixels, and two owners of dpi is a conflict.
2. `neck_polygon` is still specialised to an upright triangle meeting a
   vertical tube; the general version would subsume it.
3. **The variant pop-out is designed but not built.** Hovering one cell of an
   18-cell contact sheet and having that variant open full-size would make
   *variants are the unit of documentation* interactive at zero extra image
   weight. CSS-cropping the sheet **will not work**: `layout/sheet.py` ends in
   `fig.tight_layout(pad=0.2)`, whose spacing depends on the per-cell captions
   and row labels, so the grid is nearly regular and not regular — cropping
   would drift worst on exactly the labelled sheets. It becomes exact if
   `contact_sheet` emits a sidecar JSON of each cell's rectangle from
   `ax.get_position()`, a few hundred bytes per sheet. Cost is a change to
   `contact_sheet` plus a rebuild of every sheet.

## Closed in session 5

- **GitHub Pages is live** at
  [deangeckt.github.io/biodraw](https://deangeckt.github.io/biodraw/),
  serving from `main` / `/ (root)` as required — enabled over the API rather
  than the UI (`gh api repos/deangeckt/biodraw/pages -X POST -f
  "source[branch]=main" -f "source[path]=/"`). Verified after the first build
  by fetching **every relative reference on all ten pages: 115 of them, all
  200.** Worth keeping: a headless check that only looks at `document.images`
  reports all nine index cards broken, because they are `loading="lazy"` and
  an undisplayed pane never scrolls them into view. They decode fine. Check
  the response code, not the DOM.
- **GitHub URLs are confirmed, not guessed.** `pyproject.toml` and
  `CITATION.cff` already said `deangeckt/biodraw`, which now matches the
  actual remote.
- **The gallery was cut from an article to a catalog** — Dean, on the live
  site: *"its still too much text, its should be more catalog then
  code-snippet."* 6,662 words → 3,227, 43 code blocks → 10 (one per page),
  and all 66 drawings kept. See documentation rule 7 in
  [PLAN.md](PLAN.md), `check_catalog` in `tools/build_site.py`, and check 11
  of `review-a-drawing`.

  The part worth remembering is *why* it drifted: documentation rule 2, **more
  images than prose**, had been in `PLAN.md` since session 1, was never
  disputed, and was never measured. Three sessions of prose accreted under a
  rule everyone agreed with. Nothing here has ever been fixed by writing the
  rule down more firmly — only by turning it into a number that fails a build.
- **`bend` stays an absolute offset** (was open item 1). Not a bug, and
  decided rather than patched: a long branch gently bowed and a short one
  visibly bent is what a drawing usually wants, and making it a fraction of
  length would change how wide every fork splays and move a great many pins
  for no gain anyone had asked for.

## The gallery

`site/` is the project's front door, built by `tools/build_site.py` from one
content module per example. Session 3, on the model of
[bioicons](https://bioicons.com/) — a filterable index of cards, each opening
a detail page.

What is deliberately *not* borrowed from it: download buttons, licence and
author filters, and dense categorisation. Their unit is a file you take away;
ours is a parameter you change, so the page's job is to make variation legible
and code copyable. A card shows the portrait and cross-fades to that example's
variant sheet on hover, which states the proposition without a line of copy.

Three decisions worth keeping:

- **Content is a schema, not markdown.** A section renders `images`, then
  `body`, then `code`, and there is no field that puts code above a picture.
  `PLAN.md` documentation rule 1 stopped being prose someone reads once and
  became the data structure. A markdown parser would also have been a
  dependency for no gain, since the schema carries the block structure anyway.
- **Images are referenced, not copied** — `../examples/<slug>/<file>`. The
  seven folders are ~1.6 MB and the weight budget is explicit, and a rebuilt
  gallery is picked up with no second step. The cost: **GitHub Pages must
  publish from the repository root**, so the site is served at `/site/`.
- **The per-folder `README.md` files are deleted, and stay deleted.** They
  were the reading surface before the gallery; keeping both would be one body
  of prose in two places. Generated one-line stubs pointing at each gallery
  page were offered and declined — *"i want to prioritize the website over the
  github"*. `examples/<slug>/` is a bare file listing on GitHub and that is
  accepted: those folders are build inputs, not a place to read.
- **`README.md` is a front door, not a second copy.** Cut from 10.3 kB to
  3.1 kB: what it is, three drawings, `pip install`, the snippet, the skills,
  the one paragraph on how the hollow render works, and a table of links.
  Everything it used to argue — the stock-illustration comparison, the two
  faces, the example list — is said better on the site. It is worth keeping
  *some* substance because `pyproject.toml` sets `readme = "README.md"`, so
  this file is also the PyPI project page, and a PyPI visitor may never click
  through.

  One line did *not* deserve cutting, and was read wrong on the way past:
  *"We already spent the tokens generating these images. Let's not spend them
  again."* It looked like a note-to-self left in the file. It is the argument
  the whole library rests on — deriving a good drawing costs real effort, that
  effort has been spent once, and nothing should require spending it again.
  It now closes *Why not a stock illustration?* on the gallery index as a pull
  quote, with **drawings** for *images*. The lesson is narrower than bug 8 and
  worth having anyway: **a line that reads as an aside may be the thesis**, and
  the cost of asking is lower than the cost of deleting it.

`build_site.py` runs two checks, and both exist because something real got
through:

- **every referenced image exists** — see bug 8;
- **no snippet needs a clone.** Every detail page carried a *Rebuilding these
  drawings* section ending in `python tools/build_gallery.py <name>`: a
  maintainer's command on a reader's page. The build now refuses a snippet
  naming `tools/`, `build_gallery` or `git`. What replaced it is the thing the
  gallery was actually missing — `pip install biodraw` and the three skills,
  said once on the index rather than seven times in a footer.

## CI, and why there isn't any

**Deleted in session 3** (`.github/workflows/ci.yml`), on the maintainer's
call. What it was doing, and why none of it was worth keeping while this is a
WIP:

- The three `test` jobs (3.10 / 3.12 / 3.13) were green. Nothing here is
  version-sensitive, so that was three runs of the same signal.
- The `gallery` job — `build_gallery.py --check` — was red on every push, and
  **could never have been green**. It failed on all 38 example files, the SVG
  included. That is not a determinism bug: the same rebuild on this machine is
  byte-identical. matplotlib's rasters move with the libpng/AGG build and its
  SVG text advances move with the freetype version, so *any* hosted runner
  produces different bytes for every file.

The lesson worth keeping, since it will come back the moment anyone re-adds
CI: **byte-identity is a same-machine property.** `--check` is a real and
useful test — run it locally before committing images — but it tests the
machine as much as the code, and wiring it to a different OS tests only the
OS. If determinism ever needs enforcing across machines it has to be against
*geometry* (the numeric pins already do this) or against a pinned container,
never against rendered bytes.

Verification is now whatever gets run locally:

```bash
py -3.12 -m pytest -q                      # 200 tests, ~2 s
py -3.12 -m ruff check .
py -3.12 tools/build_gallery.py --check    # before committing any image
```

## Before publishing

One line: `biodraw/io.py`, `DEFAULT_QUALITY = "review"` → `"compact"`. Then
rebuild the gallery and commit the smaller images. Current cost of the higher
quality is about 2.3x the bytes; the seven folders total ~1.9 MB at `review`
and would be roughly 800 kB at `compact`.

Then enable GitHub Pages **from the repository root** and check the gallery at
`/site/`. Rebuilding the images changes what the site shows without the site
being rebuilt, which is the intended coupling — but do run both, in order:

```bash
py -3.12 tools/build_gallery.py --check
py -3.12 tools/build_site.py
```

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

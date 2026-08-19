# Roadmap

Where `biodraw` is going, and why it is shaped the way it is.

## Where it came from

The seed is a 4800-line module that drew one figure in one paper — cartoon
pyramidal and inhibitory cells, spiny dendrites, projecting axons, synapses,
and wired circuit panels — driven entirely by deep keyword dicts tuned by hand
for that figure.

Underneath that figure-specific surface it already had four clean layers, and
the first three are **not neuron-specific**: a tapered open-ended tube is a
hypha or a vessel, a superellipse is any cell body, and the spine placement is
really *stamp a traced unit profile along a path*. `biodraw` is built on that
seam: a domain-neutral core, with `neuro` as the first domain built on it.

## What this is for, and what it is not

Free libraries of scientific art already exist and are good — NIAID's
[BioArt Source](https://bioart.niaid.nih.gov/) carries 2,000+ vectors and
icons across sixteen categories (viruses, anatomy, cells and organelles,
bacteria, proteins, lab equipment, plants). **This library does not compete
with those and should never try.** If a figure needs a virion or a centrifuge,
the right move is to download one.

The gap it fills is that a static asset cannot become the next one. Figures
need *variation* — the same cell at three spine densities to make the point,
the epithelium curved into a duct, one more basal on the cell in panel B — and
with a fixed asset that means editing points by hand, which ends
reproducibility and costs the same again at every revision. Here a variant is
a parameter, a rebuild is one command, and the drawing lands on a matplotlib
axes so it sits beside real data.

Two consequences for how this is built, both already load-bearing:

- **Variants are the unit of documentation** (see the documentation rules
  below). The README shows grids because the grid *is* the argument.
- **Tracing has to be public API**, not a story about how the shapes were
  made. A researcher's own drawing joining the library on equal terms with the
  bundled ones is the thing a stock library structurally cannot offer.

BioArt's category list also doubles as the roster checklist — it is a survey
of what people actually reach for, compiled by people who had to answer that
question professionally. Anything on it that wants *varying* is a candidate
here; anything that only wants downloading is not.

## Decisions

| | |
|---|---|
| License | MIT |
| API | Objects + **anchors** for people; introspection + checks for agents |
| Scope | Domain-neutral core, `neuro` as the first complete domain |
| Rendering | matplotlib only, plus SVG hygiene (named layers, text as text) |
| Fidelity | Primitives pinned by image tests; the seed figure ships as the flagship example |
| Shapes | Traced from drawings, not synthesised — and tracing is public API |

## Documentation rules

These apply to every page of the gallery, every example folder, and the
main README. Rule 1 is now **enforced structurally**: a gallery section
is `images` then `body` then `code`, and `tools/build_site.py` has no
field that puts a code block above a picture.

1. **Image first, code second — always.** A reader should see what a thing
   looks like before being shown how to make it. Never open a section with a
   code block; open it with the picture the code produces. If a section has no
   image worth showing, ask whether it needs the code either.
2. **More images than prose.** The product is drawings. A wall of text about a
   drawing library is a failure of the library.
3. **Snippets use keyword arguments with meaningful names.**
   `render_hollow(ax, [part], "#FFD9D9", "#FF0000", 2.0)` tells a reader
   nothing. Every argument in documentation is named, and anything non-obvious
   carries a trailing comment:

   ```python
   render.render_hollow(
       ax=ax,
       parts=[outline],
       fill="#FFD9D9",      # the interior wash
       edge="#FF0000",      # the wall
       wall_lw=2.0,         # wall thickness, in points
   )
   ```

   This doubles as an API test: if a call cannot be written readably with
   named arguments, the signature is wrong.
4. **Every example folder carries a blueprint** — the construction figure, so
   the maths is visible and not just asserted.
5. **Variants are the unit of documentation.** A reader learns more from
   eighteen small cells differing in one knob each than from one large cell
   and a paragraph about what the knob does. Fill a page with icon grids, not
   with a handful of portraits.
6. **A public page shows only what `pip install` can do.** Every detail
   page carried a *Rebuilding these drawings* section ending in
   `python tools/build_gallery.py pyramidal` — a command that presumes a
   clone of this repository, on a page written for someone who has installed
   the library. Maintainer instructions belong in `CONTRIBUTING.md`.
   `tools/build_site.py` now refuses to build a snippet naming `tools/`,
   `build_gallery` or `git`. The positive form matters more than the
   prohibition: the reader's next step is `pip install biodraw` and pointing
   an agent at the skills, so that is what the page should say.
7. **Hover may affirm, never replace.** The gallery's cards first cross-faded
   each portrait into that example's variant sheet on hover. It read as the
   card changing identity: two cards could not be compared, and what you
   clicked was not what you had been looking at. Hover is allowed to say
   *this one* — a border, a colour, a lift. The moment it substitutes
   different content, the reader has lost the thing they were looking at in
   order to see something the page could simply have shown. If a picture is
   worth putting on the index, put it on the index.

## Drawing rules

What separates a drawing from a diagram of a drawing. Each of these arrived as
a specific complaint about one figure and turned out to govern everything.

1. **A repeated part must not repeat exactly.** Two fork daughters reflected
   about their trunk, two basal legs of equal length, eight microvilli on
   exactly even slots, a row of cells with a perfectly level apical surface —
   each reads as a symbol *for* the thing rather than as the thing. Anything
   the library produces in pairs or in runs must differ in the ways real ones
   differ, **by default and not on request**, and the variation must be seeded
   so the figure still regenerates byte-identically.

   The distinction that matters is texture versus structure. Mirroring a
   traced profile across a branch is right — it stops N decorations sharing
   one asymmetry (`Profile.place(mirror=...)`). Mirroring a *bifurcation* is
   wrong, because symmetry there is a claim, and a false one: real daughters
   differ in calibre, length and angle, and the three move together — the
   thicker daughter runs further and turns less off the parent's axis while
   the thin one branches off wide. One ratio should drive all of them, or the
   fork reads as three knobs that happen to be set.

2. **A cosmetic term that does not scale with length will end up driving
   something structural.** The waver that makes a branch look drawn is a sine
   with a fixed *cycle count*, so halving a branch's length doubles its
   frequency. An apical forked at 0.25 drove its trunk at four times the rate
   the drawing was tuned at and swung it 44° off axis against a reference of
   22° — which is the "twiddle" visible above the soma. Cycle counts, fixed
   offsets and fixed angles are all suspect the moment they are shared between
   branches of different lengths; prefer a wavelength (`Branch(wave_per=...)`)
   or a fraction. This is the same failure as keying a fork off the local
   tangent, and it is now the second time it has been found.

3. **A count spread over a length is a density.** The same failure as rule 2,
   one level up: `spines=9` on an apical means nine *at the reference length*,
   and forking the apical halves the trunk. Sharing the count crams nine
   spines into half the dendrite and the tuft becomes a mass of touching
   heads. Anything counted along a branch — spines, boutons, microvilli,
   protrusions — has to be derived from a per-unit rate, not carried across
   branches of different lengths.

4. **Prefer the schematic where the realistic one competes for attention.** A
   "realistic" axon was built — a tapered tube with swellings — and removed.
   At the size an axon appears in a circuit panel it reads as a fat beaded
   worm and pulls the eye away from the cells it exists to connect. A line
   with a mark on the end says the same thing and is parsed instantly. The
   test is not "is this anatomically fuller" but "does the reader get the
   claim faster".

5. **When something looks wrong, measure it before changing it.** Neither of
   the two above was found by looking. Both were found by computing one number
   — cycles per unit length, degrees off axis — and comparing it against the
   configuration the drawing was tuned in. An agent cannot see the figure, and
   a human describing what is wrong with one is describing a symptom.

## The image weight budget

**The budget is a publication constraint, not a development one.** It was
imposed before anything needed debugging, and the cost showed up immediately:
at 100 dpi a sheet of eighteen cells gives each cell about 55 pixels, which is
enough to see that a cell was drawn and not enough to see whether it was drawn
*right*. Two real defects sat in the committed images for a whole session
because nobody could see them. So `biodraw.io.QUALITY` holds three profiles —
`compact` (what a published repo carries), `review` (the default while this one
is not published) and `debug` (uncapped, for looking at one shape hard) — and
`DEFAULT_QUALITY` is the single line to flip back before going public.

Worth recording, since the original numbers implied otherwise: **`dpi` is the
binding constraint, not `max_width`.** A three-column sheet at `cell_in=1.5`
comes out 450 px wide, so the 1000 px cap never engages and only the dpi
matters. Going from compact to review roughly doubles the linear resolution
and costs about 2.3x the bytes.

This library is heading for hundreds of examples with thousands of variants
between them. Documentation images are the only thing here that does not
scale for free, so the rules are measured, not guessed:

| for 36 cells | size | per cell |
|---|---|---|
| SVG contact sheet | 2,970 kB | 83 kB |
| PNG, 150 dpi | 157 kB | 4.4 kB |
| PNG, 100 dpi | 87 kB | 2.4 kB |
| **PNG, 100 dpi, quantized** | **29 kB** | **0.81 kB** |

**SVG is the wrong format for documentation.** The hollow renderer strokes
*and* fills every part, so a page of cells carries two paths per part and runs
to megabytes. Vector is for the deliverable — the figure that goes in a paper
— and rasters are for the README.

So:

- **Use `bd.contact_sheet` + `bd.save_compact` for anything in a README.**
  Compact caps the pixel width at 1000 (a README displays at less than that,
  and rendering at three times it is three times the bytes for nothing) and
  quantizes to a 32-colour palette, which is visually lossless on flat line
  art and about a third the size. Pillow does the work and ships with
  matplotlib, so this costs no new dependency.
- **A variant inside a shared sheet costs ~0.8 kB; the same variant as its own
  image costs ~50 kB.** Sixty times cheaper. Show more, in fewer files.
- **Do not commit SVGs of assembled shapes.** A single pyramidal cell is 98 kB
  as SVG — more than all five of that example's rasters put together. The
  vector file is one `bd.save(fig, "cell.svg")` away, and `build.py` is
  committed, so the repository does not need to carry output that regenerates
  in a fraction of a second. One small SVG is kept in
  `examples/dendritic_spine/` as the standing demonstration that vector export
  works; re-proving it per folder costs ~100 kB each for nothing.
- **Budget: about 100 kB per example folder.** At that rate a hundred examples
  is 10 MB, which is a repository people can clone.
- Past two varying knobs, use `row_labels` / `col_labels` rather than a
  caption under every cell — repeating three keys eighteen times is the same
  text written eighteen times, and it crowds out the drawings.

## Non-negotiables

- **Keep the tuning comments.** They record why a number is what it is,
  usually discovered after something looked wrong. They are the most expensive
  thing here to rediscover.
- Vector only. No rasterized fallback anywhere.
- Runtime dependencies: `numpy` and `matplotlib`. Nothing else.
- Pin a drawing before refactoring it.

## Milestones

### 0 — Repo skeleton ✅

`pyproject.toml`, MIT `LICENSE`, `README`, `CITATION.cff`, `CONTRIBUTING.md`,
`AGENTS.md`. Lint, image tests and the gallery rebuild run locally — see
*Verification* below. There is no CI: the rebuild check is same-machine by
nature and could never pass on a hosted runner.

### 1 — Core geometry and rendering ✅

Ported with comments intact, then pinned by baseline images before anything
else is built on it.

- `core/geom.py` — vectors, polylines, arclength resampling
- `core/paths.py` — `tube`, `superellipse`, `bowed_ring`, `rounded_polygon`,
  `neck_polygon`, `elbow`, `cubic_connector`, `fork_tree`
- `core/profile.py` + `core/profiles/spine.py` — traced profiles, the
  canonical frame, and the neck stretch
- `core/branch.py` — the curved process and its decorations
- `core/render.py` — `render_hollow`, the two-pass union
- `io.py`, `style/palette.py`, 89 tests, 6 pinned baselines

### 2 — Anchors, synapses, connectors ✅

`Anchor(point, outward normal, kind)` — the abstraction that makes contributed
shapes interoperate. Connectors, synapse dots, leader labels and scale bars all
consume anchors, so a new cell type gets all of them the moment it exposes
some. Plus `connect()` / `connect_tree()` with dot / bar / arrow endcaps.

**The dot-placement engine was built and then removed.** It allocated a total
across compartments — "eight contacts, five on spines, two on shaft, one on
soma" — and chose the particular anchors. That is a *logic* layer, not a
drawing one: which compartment a synapse lands on is the author's scientific
claim, and once the cell is drawn, marking it is two lines of matplotlib
against anchors that are already public. Carrying it here meant carrying one
paper's argument inside a general drawing library, and it dragged the
figure-specific "claim colours" into the palette with it. Both are gone.

What survives is the part that is genuinely about *drawing*: a connector has
to end in something, and whether that mark is an arrowhead or a bar is how the
figure says excitation or inhibition. That lives in `connectors.endcap`.

### 3 — `neuro`: Pyramidal, Basket, Axon, Synapse ✅ (Synapse recast)

The seed's cells as objects on the core, with every current keyword surviving.
Baselines from milestone 1 must still pass.

`Pyramidal`, `Basket` and `Axon` shipped. **`Synapse` deliberately did not
become a class**, and the placement engine that would have fed it was removed
(see milestone 2). A synapse drawn as a dot is not a shape — it is a mark at
an anchor, and `Anchor.offset` already gives the stand-off. Anyone who wants
one writes it themselves in a line, which is the right amount of library for
something that is really the figure's own logic.

If a figure ever needs a synapse with real internal structure — a cleft,
vesicles, a post-synaptic density — that *is* a shape, and gets a class then.

### 4 — Layout, style presets, export

The multi-panel assembler (nested ratios, per-cell title bands, aspect-locked
panels, linked limits, floating legend), the points-based legend, panel
letters, separators. `style.use('paper' | 'poster' | 'slides')` to own the
point-valued knobs that do not scale with panel size.

### 5 — `explain()`

Every shape renders its own construction figure, from the same object it draws:
a `Profile` shows raw points → canonical frame → stretch span → placed result;
a `Branch` decomposes `along(t)` and `across(t)` into the lean and the waver;
`render_hollow` shows pass 1 / pass 2 / result side by side. Every example's
`construction.png` is generated this way, so it cannot go stale.

### 6 — Sketch to shape, as a skill rather than a parser ✅

**Dropped: an image-tracing toolkit.** Building `from_image` / `from_svg`
parsers would be solving a problem that no longer exists. Someone with a
drawing photographs it, drops it into their agent's chat, and talks about it —
the agent already has eyes, and a dedicated UI would be a worse version of the
conversation they were going to have anyway.

What is genuinely needed is *the recipe the agent follows*, and that is a
**skill**, not a module. The library side is already done: `Profile(...,
normalize=True, tip=...)` puts a traced outline into the canonical frame, and
`profile.register()` makes it available by name.

So this milestone ships `skills/trace-a-shape/`: how to read proportions off a
photograph, what to measure, how to choose the stretch span, how to check the
result against the drawing, and what provenance to record.

### 7 — The agent-facing layer

`biodraw` assumes most figures will be *described*, not typed.

- **`bd.catalog()`** — every shape, knob, default, range and *effect* as data,
  so an agent reads the API in one call instead of grepping the source.
- **`bd.check(fig)`** — programmatic diagnostics standing in for eyes:
  overlapping decoration heads, connectors crossing bodies they should pass
  behind, dots inside walls, ink outside the axes, labels colliding. These are
  exactly the failures the seed's comments record fixing by hand; automating
  them is what lets an agent converge without a human squinting at every pass.

#### Skills — shipped ✅

`skills/` now exists, with three, and [`skills/README.md`](../skills/README.md)
carries the contract and the fine-tuning loop so a second developer can pick
it up:

| skill | when |
|---|---|
| `draw-a-figure` | building a figure from shapes that exist |
| `review-a-drawing` | **before reporting any drawing as finished** |
| `trace-a-shape` | turning a photograph into a shape the library lacks |

`review-a-drawing` is the important one, and it is not a static checklist. It
is where user-hat feedback gets **converted into a numeric check** — step 3 of
the loop in `CLAUDE.md`. Every check in it names the comment that produced it,
which keeps it honest: a check that cannot point at a real failure it caught
is a guess and should be cut. It currently carries eleven, derived from the
waver-frequency bug, the mirror-image fork, the crotch spur, two
inward-pointing-anchor bugs, the layer/occlusion rule, the epithelial gap, and
the SVG determinism bug — plus two added in session 4: the *measure to an
edge, and on a flattened shape* half of check 5, and check 5b, that an inner
part is actually inside the part containing it. Both of those came from
defects that a passing test had been walking past — and one more on the back
of the `rcParams` leak, that **a single-example rebuild and a full rebuild
must agree**, without which `--check` is testing the order the folders happen
to sort in.

The intended effect is that the same class of comment never has to be made
twice — a rule written as prose gets read once, a rule written as a check gets
run every time.

#### What makes a skill good

Skills are the main way this library gets used and extended: some shipped
here, some written by others for their own figure styles. That needs a
contract, or the repo fills up with prompts that work once.

A skill in `skills/` must:

1. **Name its trigger precisely.** When it applies, and — as importantly —
   when it does not.
2. **Be derived from a worked example, not imagined.** Do the task once by
   hand, keep what was actually needed, and cut what turned out not to be.
   Anything asserted in a skill that was never exercised is a guess.
3. **State the checks.** What the agent runs to know it succeeded, and what
   the failure looks like. A skill with no verification step is a wish.
4. **Fail loudly on ambiguity.** Where a choice is a scientific claim — which
   compartment a contact lands on, whether two cells are level — the skill
   must say *ask*, not *pick*.
5. **Ship with its example.** The folder under `examples/` that the skill was
   derived from, so the skill can be re-derived and tested against a known
   output.

`trace-a-shape` was derived exactly this way — from
`examples/dendritic_spine/`, by starting from the original photograph and
rebuilding the blueprint from it. That exercise is the method: whatever it
takes to get there *is* the skill.

### 7.5 — `cells`: the non-neuron example, brought forward ✅

Deliberately ordered **before** the rest of `neuro`. Both examples so far were
neurons, so the claim that the core is domain-neutral was untested — and the
cheapest moment to find a neuron-shaped assumption is before Basket cells and
connectors are built on top of it.

`cells.Blob` (a body with nucleus, nucleolus, organelles and protrusions) and
`cells.Sheet` (an epithelial row, curvable into a villus or a closed duct)
exercise the **body** primitives where everything before leaned on the branch
engine. Shipped as `examples/generic_cell/` and `examples/epithelial_sheet/`.

**What the core turned out to be missing** — the real output of the milestone:

1. **`core.shape.Layer`.** Every shape until now was one unbroken contour, so
   `_parts()` returning a single fused group was enough. A nucleus is the
   opposite requirement: union it with the body and it disappears into the
   body's own fill. Same for two cells of an epithelium meeting at a shared
   wall. `Shape._layers()` now returns an ordered list of render groups —
   parts fuse *within* a layer and occlude *across* layers — and the default
   wraps `_parts()` as one layer, so nothing that existed changed by a byte.
   Layers also carry their own `fill_alpha`, which is how a nucleus reads as
   denser than its cytoplasm without introducing a second hue.
2. **`core.scatter`.** `Branch.decorate` covers everything that grows along a
   line. Nothing covered "n of these, loose in there" — organelles, vesicles,
   granules. Seeded rejection sampling with a wall margin, exclusion regions
   and a minimum separation, which **raises** rather than placing fewer than
   asked.

**And two bugs, both found by the drawings rather than by the tests:**

- The lateral bow on a `Sheet` cell ate the gap between neighbours — 0.018 a
  side against a gap of 0.0276 — so cells overlapped by 0.008 and `gap` did
  not mean what it says.
- `bd.save` was not byte-reproducible: matplotlib stamps a `<dc:date>` into
  every SVG and salts its clip-path ids from a per-process `uuid4`. The
  determinism required of `examples/` would have failed on the one committed
  SVG the moment it was rebuilt. Pinned via `io.SVG_HASHSALT`.

### 7.6 — `micro`, and examples that are only examples ✅

Two additions, deliberately of different kinds, because the question this
milestone answers is *what does expanding the library actually cost*.

**`examples/cell_atlas/` cost nothing.** Twelve nameable cells — erythrocyte,
platelet, lymphocyte, macrophage, fibroblast, smooth muscle, adipocyte,
oocyte, spermatozoon, amoeba, ciliated cell, plant cell — every one of them
`cells.Blob` with different keywords and **no new library code at all**. It is
the strongest available statement of *variants are the unit of documentation*,
and it is the cheapest example in the repo. The page also names what the shape
**cannot** say — a lobed nucleus, a cell wall as a second contour, a bud,
contents confined to part of the cytoplasm — because a page that only shows
successes is advertising rather than documentation.

**`biodraw/micro/Bacterium` cost one semicircle.** `paths.tube(cap_base=True)`
was the whole of what the third domain needed from the core, which is the
return on the first two having paid for it. The shape's own design decision
worth keeping: **the named forms are settings, not classes.** Coccus, bacillus,
vibrio and spirillum each describe one axis — length, `curve_deg`, `twists` —
so given those as numbers every named form is a value and the space between
them is drawable. An enum would have made the four names the only reachable
shapes. Flagellar arrangement is the same trick with `Blob`'s protrusion
vocabulary reused verbatim, so the four textbook arrangements are two numbers.

And arrangement is **composition**: a diplococcus is two cocci and `moved()`.
There is no `arrangement=` keyword, for the same reason there is no placement
engine.

The real yield, though, was diagnostic. Four defects (11-14 in
[STATE.md](STATE.md)) came out of running `review-a-drawing` against these two
examples, and **three of them were in code that had already shipped and been
reviewed**. The lesson is now a rule:

> **A new example is a test of the old code.** It exercises existing shapes in
> configurations nothing had asked for before — flattened, bent, twisted,
> jittered — and those are precisely where a defect that is invisible on the
> symmetric default lives. Two of the four were exactly 0 on a round or
> straight shape.

### 8 — Roster

`neuro.Bipolar`, `neuro.Astrocyte`, `cells.Blob` (the proof the core is not
neuron-shaped), and `annotate.scalebar` / `annotate.label`.

### 9 — Examples and gallery

An example is a folder of **output plus the script that made it**, and a
content module that says how to read it:

```
examples/dendritic_spine/
  build.py           the drawing, ~20 readable lines
  spine.svg          the deliverable
  spine.png          gallery preview
  blueprint.png      the construction figure
site/content/dendritic_spine.py
                     title, category, prose, snippets — the page
```

`tools/build_gallery.py` runs every `build.py` and regenerates all images;
`--check` fails on a non-empty `git diff examples/`, which doubles as the
determinism test. `tools/build_site.py` turns the content modules into
`site/`. The two are deliberately separate: images are expensive and rebuilt
rarely, pages are cheap and rebuilt every time prose changes.

**The per-folder `README.md` is gone.** Seven of them were the reading surface
until the gallery existed, and keeping both would have meant one body of prose
in two places, drifting. The folders keep `build.py` and the images, which is
what the determinism check needs and what a contributor edits.

### 10 — Animals, microscopy and genetics

Three categories Dean has asked for, recorded here before any is built. They
are listed together and they are **not** the same kind of ask, which is the
thing to settle before writing any code.

**Dean is supplying reference figures for animals and microscopy**, and has
already named one for genetics. Wait for them. The seed exercise in
[STATE.md](STATE.md) is unambiguous that the first step is turning a picture
into a parts list, and every attempt here to skip that step and route around
a gap has cost more than it saved.

#### Animals

Model organisms as shapes: mouse, fly, zebrafish, worm, frog, macaque. High
demand — nearly every methods figure in biology opens with one — and a good
fit for the roster test in *What this is for*, because the thing people
actually need to vary is **pose and orientation**, not identity. A mouse seen
from above, from the side, and head-on is three drawings of one animal, and a
stock library makes you download three files that will not match.

The open design question, and it is the whole milestone:

- **A body plan built from the core** (a tapered tube for a torso, `Branch`
  limbs, a traced head profile) would vary properly, and would almost
  certainly need something the core does not have — a jointed chain, which
  `Branch.child` nearly is.
- **A traced silhouette per animal per view** is what `skills/trace-a-shape`
  already supports today, at zero library cost, and is honestly what most
  figures want. It varies in scale and colour and nothing else.

Recommendation: **start with traced silhouettes**, because they are free and
they will show within a week whether anyone wants a pose knob. Building the
jointed body plan first risks a general animal rig that draws worse mice than
one traced outline would.

#### Microscopy

This one needs a decision on scope, and the library's own test is the one to
apply: *anything that wants varying is a candidate here; anything that only
wants downloading is not.* Two readings, and they fall on opposite sides of
that line:

- **Microscopy as equipment** — a microscope, a slide, a coverslip, a
  centrifuge. This is what NIAID's BioArt already carries by the thousand, and
  `docs/PLAN.md` opens by saying this library should never compete with it. A
  microscope drawn here would be a worse version of a file you can download,
  and it does not vary: nobody needs the same microscope at three objective
  counts.
- **Microscopy as what a field of view looks like** — a section outline, a
  well or a coverslip boundary, a field at a stated magnification with cells
  at a stated density, a scale bar that knows its own units, an inset box
  cross-referenced to a zoomed panel. **All of this varies**, all of it is
  arithmetic a person currently does by hand, and none of it exists in any
  stock library because a stock asset cannot know your density or your
  magnification.

Recommendation: **the second reading**, and it is the strongest of the three
categories on this page. It also absorbs two things already queued —
`annotate.scalebar` from milestone 8, and the panel/inset machinery from
milestone 4 — so it should be sequenced after those rather than beside them.

**Ask Dean which reading he meant before building either.** If he meant the
equipment, the right answer may be to say so and point at BioArt, which is
what this library's own scope section already commits to.

#### Genetics

Asked for **in place of** a proteins category, on the strength of figure 1 of
[doi.org/10.1016/j.tibtech.2023.03.007](https://doi.org/10.1016/j.tibtech.2023.03.007)
— *"many examples that this repo/catalog can reproduce and expand"*. The
figure is behind Elsevier's gate and has not been read, so what follows is
the argument for the swap and not a parts list.

The swap is right, and for the reason the scope section already gives.
**A protein is a shape you download**: a ribbon diagram comes out of PDB and
a cartoon receptor comes out of BioArt, and neither wants varying — nobody
needs the same kinase at three domain counts. **Genetics is almost entirely
things that vary**, and they vary along axes this library's core already
speaks:

- a **double helix** is a wave with a wavelength and a phase — the same
  `Branch` term that draws a flagellum, doubled and cross-linked, and it wants
  a length and a turn count rather than a fixed picture;
- a **construct or plasmid map** is a run of boxes along a line or round a
  ring, which is `Sheet`'s arc arithmetic with different contents, and it
  varies in the one way a stock asset cannot: *your* insert, *your* order;
- **exon/intron structure**, guide RNAs, primers, cut sites and repeats are
  all counts and positions along a length — the density rule in *Drawing
  rules* 3 applies to them unchanged.

So genetics passes the roster test where proteins fails it, and the pieces
are mostly already in the core. It is the one of the three that could
plausibly start today — **but wait for the figure**, because what it actually
shows should decide which of those three is built first.

## Verification

```bash
pip install -e ".[dev]"
pytest --mpl                                  # geometry + pinned images
pytest --mpl-generate-path=tests/baseline     # regenerate, if intended
ruff check .
python tools/build_gallery.py --check         # examples rebuild identically
```

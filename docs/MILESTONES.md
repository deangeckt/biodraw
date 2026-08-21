# Milestones

What was built, in the order it was built, and what each one turned out to
cost. Most of this is history and is kept for one reason: **several entries
record something being built, shipped, and then deliberately removed**, and
the reasoning behind a removal is the most expensive thing here to
rediscover. See also *Things built and then deliberately removed* in
[STATE.md](STATE.md).

This file is the archive. For what is coming next, read
[ROADMAP.md](ROADMAP.md) — it is short on purpose.

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

### 3 — `neuro`: Pyramidal, Basket, Synapse ✅ (Synapse recast, Axon removed)

The seed's cells as objects on the core, with every current keyword surviving.
Baselines from milestone 1 must still pass.

`Pyramidal` and `Basket` shipped. **`Axon` shipped and was then deleted** —
at the size an axon appears in a circuit panel a realistic one read as a fat
beaded worm competing with the cells it connected, and a projection is a line
with a mark on the end (`core.connectors`, and *Drawing rules* 4). See
[STATE.md](STATE.md), *Things built and then deliberately removed*.

**`Synapse` deliberately did not
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
is a guess and should be cut.

    grep -c '^### ' skills/review-a-drawing/SKILL.md

That is the count, and it is a command rather than a number in prose because
this sentence said *eleven* for four sessions after it stopped being true.
The skill itself is the list; each check opens with the defect or the comment
that produced it, which is the only provenance worth keeping.

The intended effect is that the same class of comment never has to be made
twice — a rule written as prose gets read once, a rule written as a check gets
run every time.
#### What makes a skill good

The five-point contract a skill in `skills/` must meet has moved to
[RULES.md](RULES.md#what-makes-a-skill-good), with the rest of the rules that
are still live. It was derived from `trace-a-shape` and
`examples/dendritic_spine/`.

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

### 8 — Roster ✅

`cells.Blob` — the proof the core is not neuron-shaped — shipped in 7.5, and
session 6 took the neuron roster past this list: `RadialCell` is the body plan
behind `Basket`, `Bipolar`, `Granule`, `Purkinje` and `Astrocyte`, which are
settings of it rather than five modules. Session 7 gave each named cell its
own gallery card (documentation rule 10).

**`annotate` closed it in session 8** — `core.annotate`, exposed as
`bd.label` and `bd.scalebar`. It is the other half of the anchor contract:
`connectors` consumes anchors to draw strokes *between* shapes, this
consumes the same anchors to put words *beside* one.

It shipped with `examples/annotation/` and a standalone *Labels & scale*
page, and **both came straight back off**: *"i see the page: 'Labels & scale'
its not needed."* A utility is not a catalog entry — see documentation rule 9
in [RULES.md](RULES.md), which gained its third answer here. What documents
`annotate` now is the four catalog figures that quietly use it, which is
better evidence than a page built to show it off.

The case for it was a count, taken before a line was written: **61
hand-written label sites** across `examples/`, **20 of them pinned to a
typed-in `x, y`** — which a wider neck or an animal at `facing=-1` leaves
behind — and **30 more each reimplementing the same three lines**. One
example folder had already grown a private `_label` helper whose docstring
called itself "the one-line stand-in for `annotate.label` (milestone 8)".

Three things the build settled, none of them guessed:

- **Alignment comes from the normal, not just the offset.** A label standing
  off to the left must be right-aligned or it grows back over the shape it
  names. Counted on a ring of twelve: centred, **7 of 12 crossed the
  outline**; derived, none did.
- **`leader` defaults off.** 11 of the 61 sites used one. The rule is about
  where the anchor is rather than taste: a part on the wall is already at the
  edge, a part buried in the cytoplasm cannot be named without a line.
- **`bd.fit` was cropping labels, and always had been.** Text is not ink, so
  `points` cannot see it — three leader labels at `pad=0.12` were all three
  outside the axes. The repository had been paying for this unnamed: **26
  hand-written `set_xlim` / `set_ylim` calls against 24 `fit` calls.** `fit`
  took a `marks=` argument, and every committed image stayed byte-identical
  because the no-marks path is untouched.

The `marks` loop is worth reading before changing: it measures, grows, and
measures **again**. One pass looks sufficient — growing the limits should
only make fixed-point text smaller in data units — and is not, because
`canvas` locks the aspect and matplotlib satisfies that by shrinking the axes
*box*, which can leave text covering *more* data units than when measured.
Tried as one pass: two of eight artists still clipped.

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

#### Animals — **shipped** (session 7)

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

Recommendation: **start with silhouettes**, because they are nearly free and
they will show within a week whether anyone wants a pose knob. Building the
jointed body plan first risks a general animal rig that draws worse mice than
one outline would.

**Built (session 7):** `biodraw.animals` — `Mouse`, `Fly`, `Zebrafish`,
`Worm` — with `examples/animals/` and an Animals category. Silhouettes, as
recommended: no jointed rig, no pose knob, nothing traced. Each animal is a
few superellipse bodies, `Branch` tubes for tails and legs and one union,
and each carries the one knob it is actually about — the mouse's tail
against its body, the fly's wings, the fish's body depth, the worm's curl.

`facing` is on the shared base, and it is the answer to the paragraph above:
a mouse facing left and a mouse facing right are one object at `facing=±1`,
and they match each other exactly, which two downloaded files never do. It
is a **mirror**, not a rotation — a rotated animal is an animal on its back.

Two things fell out of building it that were not obvious in advance:

- **`Layer` gained `wall_lw`.** A *marking* stroked at the body's own wall
  weight stops being a marking and becomes a pipe laid across the animal. A
  layer can now say `wall_lw=0` (no wall) or `'0.8x'` (a multiple of what
  `draw` was asked for). It was built for the zebrafish's stripes, which
  were later removed; the fly's wing kept it earning its place;
- **anchors have to be taken over what is drawn, not over the geometry.**
  The fly's wings are a layer rather than part of `_forms()`, so wall
  anchors computed from the geometry sat *under the wing* — where a label
  must never go. Caught by the test, not by looking.

Still open, and cheap when wanted: more organisms (frog, macaque, chick,
*Arabidopsis*), and the pose question, which nobody has needed yet.

#### Microscopy — **shipped** (session 8)

This one needs a decision on scope, and the library's own test is the one to
apply: *anything that wants varying is a candidate here; anything that only
wants downloading is not.* Two readings, and they fall on opposite sides of
that line:

- **Microscopy as equipment** — a microscope, a slide, a coverslip, a
  centrifuge. This is what NIAID's BioArt already carries by the thousand, and
  [SCOPE.md](SCOPE.md) is explicit that this library should never compete with it. A
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

**Decided (session 7): the first reading — the instrument.** Asked, and the
answer was *"microscopy i meant drawing of a microscope illustration"*. So
this page's recommendation was wrong about what was wanted, and the scope
argument above stands as an argument rather than as a veto: a methods figure
that opens with a microscope is a real and common thing, and BioArt carrying
one does not put it on the axes beside your data.

What makes it pass this library's own test is that a *drawn* microscope has
counts in it, and that is where the parameters are:

| part | varies by |
|---|---|
| objectives on the nosepiece | **n** — this is the one everybody redraws |
| eyepiece | monocular or binocular |
| body | upright or **inverted**, which is a different instrument entirely |
| stage, condenser, illuminator | present or not |
| camera / display arm | present or not |

Built as an outline, in the schematic house style above, that is one shape
with five knobs rather than a downloaded picture of somebody else's
microscope.

**Built in session 8** as `biodraw.lab.Microscope`, with
`examples/microscope/` and a sixth gallery category — the first that draws
no living thing. Four of the five knobs above survived; **`binocular` did
not**, and its removal is the most useful thing the build produced. Two
eyepiece tubes are separated *into the page*, so a strict side elevation puts
one exactly behind the other: measured, the flag changed the inverted body by
**0.0%** and widened the upright's single tube by 11.6% with the barrels
still fused. That is the zebrafish's stripes and the side-on fly in one knob.

Three defects, all found by reading numbers rather than by looking:

- the objectives were drawn **through the stage** — a working distance of
  -0.044, on an outline that looked entirely convincing;
- the objective *anchors* pointed **up** out of an upright, because `_named`
  re-derived the turret that `_forms` already owned and got the sign
  backwards. Fixed by giving both one `_layout` dict to read;
- the fan was held as a fixed **total** spread, so the step between barrels
  shrank as barrels were added and at `objectives=5` the tips fused into a
  lump. That is drawing rule 3 (*a count over a length is a density*) on an
  angle, and it is now half of check 4 in `review-a-drawing`. **The field-of-view reading is not dropped** — a section outline,
a field at a stated density, an inset box — but it is a *second* thing and it
still waits on `annotate.scalebar` and the panel machinery.
#### How the reference figures are used — for all three

The two rules that came out of *"grab text book images ... sometimes an
outline is even enough"* — **a reference is a parts list**, and **draw the
schematic, not the portrait** — apply to every category here and to every one
added later, so they live with the other drawing rules: [RULES.md](RULES.md),
drawing rules 6 and 7.

#### Genetics — **shipped** (session 7)

`biodraw.genetics` and `core.Track`, with `examples/inducible_construct/` and
a Genetics category on the gallery. What went in, against the inventory
below: the construct track (`Repeat`, `Promoter`, `CDS`, `Terminator`) and the
protein layer's lobed body with domain tags. What did not, deliberately: the
crescent, the lumpy body, the RNA hairpin, the light cone, the transcript
arrow and its strike-through — none of them was needed to draw the first
panel, and a vocabulary built ahead of a drawing is a guess.

Two things the build proved, both worth keeping:

- **the track is not a genetics primitive.** It lays parts along an axis,
  each consuming its own width, and knows nothing about biology — a domain
  map, an ideogram and a timeline are the same object with other glyphs. It
  lives in `core`;
- **no text is drawn by the library.** Every glyph carries a `label` and the
  track exposes `label` (hugging each glyph) and `tick` (on a shared
  baseline) anchors; the figure writes its own text. `annotate.label`
  (milestone 8) will render against those anchors.

The inventory it was built from:

Asked for **in place of** a proteins category, on the strength of figure 1 of
[doi.org/10.1016/j.tibtech.2023.03.007](https://doi.org/10.1016/j.tibtech.2023.03.007)
(Trends in Biotechnology, chemically and light inducible expression systems).
The figure was behind Elsevier's gate through two sessions; Dean supplied a
screenshot and its caption in session 6, so the parts list below comes off
**that figure** rather than off a guess.

Worth recording that the guess was partly wrong. This page previously argued
genetics on double helices, plasmid maps and exon/intron structure. The figure
contains none of those. It is **linear constructs and protein complexes**,
which is a different parts list reached by the same reasoning — more evidence
for the rule that the inventory comes off the figure, not off the field.

**What is in it, as parts:**

*A construct track — glyphs laid left to right along a backbone line.* This is
the SBOL Visual vocabulary, and it is the half of the figure this library
should own:

| glyph | in the figure | varies by |
|---|---|---|
| repeat box | `CBS operator` (4 bars), `4xUAS`, `(etr)8`, `(C120)5`, gRNA binding site | **n repeats** |
| promoter | `Minimal promoter`, `P35Smin`, `35S`, `U6` — an arrow-pentagon | label, fill |
| CDS | `GOI`, `dCas9-VP64`, `Guide RNA` — a rounded rectangle | label, width, fill |
| terminator | the ⊥ closing each track | — |
| transcription arrow | the black bent arrow; struck through with a red ✗ for OFF | on/off |
| backbone | the line the whole run sits on | length |

*A protein layer — bodies with tags stuck to them:*

| glyph | in the figure | varies by |
|---|---|---|
| lobed body | `CUP2`, drawn open then closed around the ion | **n lobes** |
| crescent | `pVHL`, a C with a notch a partner sits in | notch width |
| oval / cloud | `HIF1α`, `dCas9` | — |
| lumpy body | `PhyB`, `PIF6`, `E` — irregular organic outline | **seed**, lumpiness |
| domain tag | `Gal4-TAD`, `Gal4-DBD`, `VP16`, `SRDX`, `LOV`, `HTH` | label, **n tags** |
| ligand | `Cu2+`, `O2` — a small filled circle | — |
| RNA | the gRNA hairpin squiggle | **n hairpins** |

*Scene furniture:* a labelled reaction arrow (`connect` already does this), a
light source emitting a coloured cone, bold `ON` / `OFF`, and grey bubble
headers over each half.

**The one real core addition: a track.** "Lay parts along an axis, each
consuming its own width, in the order given" is not something the core can do
— `Sheet` distributes identical cells, which is not the same thing. A track is
worth building properly because it is not a genetics primitive at all: a
protein domain map, a chromosome ideogram, a timeline and a gene model are the
same object with different glyphs.

**Why this passes the roster test**, where a proteins category failed it: every
row marked *varies by* above is a count or a length that a person currently
draws by hand and a stock asset cannot know — **your** repeat number, **your**
insert order, **your** domain list. The light source is the one item on the
list that arguably wants downloading rather than drawing; if it is built, it
is because the cone's colour and angle vary, not because the torch does.

**Suggested first example** — built, and it is the page's hero: one panel of
the chemical-inducible system, a repeat box, a promoter, a CDS, a terminator,
and a two-lobed body carrying one domain tag. It exercised the track, the
lobed body and the tag in one drawing, and writing its tests found two
defects in a day-old module: a promoter drawing 0.0175 outside its own span
(so the track would lay a neighbour into it) and a cleft search whose ray
stopped inside the body, reporting the same depth at every opening.

#### The neuron summary figure — a style, not a domain

Figure 7 of [nature.com/articles/s41593-025-02004-2](https://www.nature.com/articles/s41593-025-02004-2),
also supplied as a screenshot in session 6, after two failed fetches. Dean's
ask was *"very very simple neuronal-like summary figures"*, to be **similar to
rather than a copy of**.

It needs almost no new shapes. It named three gaps, and **two of them are
closed** — which is the point of writing the inventory down rather than
building the figure:

1. **Flat solid cells** ✅ — `fill=edge` was always possible and nothing
   demonstrated it. It is the `solid` entry on the standalone *Drawing
   styles* page now, beside `outline`, `ghost` and the two skeletons.
2. **A crossbar tuft** — still open, and the only one of the three that is a
   drawing gap rather than a documentation one. Each apical forks and each
   daughter ends in short transverse dashes rather than spines: a stylised
   tuft that says "this arborises" without drawing an arbor. A new decoration
   kind (`Branch.decorate` with a bar profile), and the same move as *Drawing
   rules*: prefer the schematic where the realistic one competes for
   attention.
3. **Orthogonal connector routing** ✅ — `connect_bus` drops to a shared rail
   and turns up into each target at right angles, on the *Circuits & wiring*
   page. A square corner reads as routing, which is exactly what a shared
   source is claiming.

Two smaller observations from it, both already supported: **line weight
carries meaning** (thick for the strong projection, hairline for the weak one,
same colour), and **colour is identity only** (cell class), which is what the
palette already commits to.

**`examples/summary_figure/` was built and removed in the same session**, and
should not be rebuilt: it reproduced the reference figure closely, when the
ask had been to expand the catalog with new *styles*. A reference figure is a
source of capabilities, not a thing to clone — the capabilities above went
into the catalog and the figure did not.


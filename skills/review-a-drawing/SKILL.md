---
name: review-a-drawing
description: Check a biodraw drawing for the defects that have actually shipped here, by measuring rather than looking. Run before reporting any drawing as finished, after changing any shape's geometry, and after adding a new shape. Not for pure refactors where the geometry pins are unchanged.
---

# Reviewing a drawing you cannot see

**You cannot see the figure. Do not report a drawing as good because the code
ran.** Every check below exists because something got past that assumption and
shipped looking wrong.

Each one names the comment that produced it. If you add a check, name yours
too — a check that cannot point at a real failure it caught is a guess, and
guesses are what make a checklist too long to run.

## When to run this

- Before reporting any drawing as finished.
- After changing the geometry of any shape, even if the pins were regenerated
  on purpose.
- After adding a new shape, before writing its example.

**Not** for a pure refactor where `pytest tests/test_pins.py` passes
untouched: nothing moved, so nothing can look different.

## First: render it big enough to see

> *"the image quality is too low to debug and fix"*

The committed images are sized for a README, not for inspection. At 100 dpi a
sheet of eighteen cells gives each cell ~55 px, which is enough to see that a
cell was drawn and not enough to see whether it was drawn right. Two real
defects sat in committed images for a whole session because of this.

```bash
python tools/build_gallery.py <example> --quality debug
```

Then **send the image to the user**. You cannot see it; they can. The checks
below catch what is measurable, and the maintainer's eye catches the rest —
that division of labour is the point, not a fallback.

---

## The checks

Run them all. They are cheap, and the expensive part is discovering a defect
after it is in a paper.

### 1 · Waver frequency, across every branch

> *"there is a little twiddle there in the neck"*

`wave_n` is a cycle **count**, not a frequency, so halving a branch's length
doubles how fast it wiggles. A value tuned on a long dendrite corkscrews on a
short one. Measured on this library's own cell: an apical forked at 0.25 drove
its trunk at **3.56 cycles/unit against a reference of 0.89** — four times —
and swung it 44° off axis against 22°.

```python
for name, br in branches:                       # however the shape exposes them
    print(f"{name}: {br.wave_n / br.length:.2f} cycles/unit, "
          f"len {br.length:.3f}")
```

**Fails if** the ratio varies by more than ~1.2x across branches of one shape.
**Fix** by giving `Branch(wave_per=...)` — a wavelength — rather than
`wave_n`, and letting the count follow from each branch's own length.

The general form of this bug is worth holding in mind, because it recurs:
**any cosmetic term that does not scale with length will end up driving
something structural.** Fixed offsets and fixed angles shared between branches
of different lengths are all suspect. (`bend` still has this problem and is
knowingly unfixed — see `docs/STATE.md`.)

### 2 · Repeated parts must not repeat exactly

> *"the two top branches are very similar, mirror like, it shouldn't be like
> that"*

Two fork daughters reflected about their trunk, two basal legs of equal
length, eight microvilli on exactly even slots, a row of cells with a
perfectly level apical surface — each reads as a *symbol for* the thing rather
than the thing.

```python
a, b = the_pair
assert not np.isclose(a.length, b.length)
assert not np.isclose(abs(a.direction[0]), abs(b.direction[0]))
assert not np.isclose(a.wave_phase, b.wave_phase)
# and for runs: the gaps between them must not all be equal
assert np.std(np.diff(positions)) > 1e-6
```

**Fix** by driving the difference from one ratio, so the variation reads as
one event rather than as several knobs that happen to be set. At a
bifurcation the physical rule is Rall's: the thicker daughter also runs
further and turns *less* off the parent's axis, while the thin one branches
off wide. And **seed it** — variation must still regenerate byte-identically.

The distinction that matters is texture versus structure. Mirroring a traced
profile across a branch is *right* (`Profile.place(mirror=...)`), because it
stops N decorations sharing one asymmetry. Mirroring a bifurcation is wrong,
because symmetry there is a claim, and a false one.

### 3 · Every joint is buried

> *"some glitch in the line where the bifurcation starts"*

A tube's near end is a flat chord. Where a child leaves a parent at an angle
that chord is tilted, and if any of it falls outside the parent it is drawn —
a spur across the crotch.

```python
from matplotlib.path import Path
parent = Path(np.asarray(parent_tube), closed=True)
v = np.asarray(child_tube)
m = len(v) // 2                       # tube(open_end=True) runs tip→base→base→tip
chord = v[m - 1] + np.linspace(0, 1, 40)[:, None] * (v[m] - v[m - 1])
assert parent.contains_points(chord).all()
```

**Fails if** any sampled point is outside. Three causes, in the order to check
them:

1. **The child is too wide.** A child as wide as its parent cannot have its
   base hidden at *any* depth — the window `c·tan(a) ≤ b ≤ (p − c·cos a)/sin a`
   is empty. Use `paths.rall_widths` so the daughters' cross-sections sum to
   the parent's; even at ratio 1.0 they come out at 0.63 of it.
2. **The burial depth is a fixed multiple of width.** It has to depend on the
   angle. Use `paths.buried_base`, which searches the parent outline *as
   drawn* so taper and lean are accounted for.
3. **The parent is drawn open-ended at a junction.** An open end means "this
   process runs off the page". A fork tip is not that — cap it, and the
   daughters have solid parent to root into. This was the fix that took the
   pyramidal fork from 6 exposed chords to 0.

Measure the angle from the parent's **nominal axis**, never its local tangent:
on a short branch the tangent sits tens of degrees off, and keying anything
structural to it is a documented trap (`Branch.child`).

### 4 · Decoration heads do not touch

> *"the top apical dendrite is too crowded"*

The same failure as check 1 one level up: a *count* shared between branches of
different lengths. `spines=9` on an apical forked at 0.5 put nine spines on
half a trunk, and the tuft came out a mass of overlapping heads.

```python
for name, br in branches:
    heads = np.array([d["head"] for d in br.decorations])
    if len(heads) < 2:
        continue
    gaps = np.linalg.norm(np.diff(heads, axis=0), axis=1)
    r = br.head_r
    print(f"{name}: closest heads {gaps.min():.3f} vs 2r = {2 * r:.3f}")
```

**Fails if** the closest gap is under `2 * head_r`. **Fix** by deriving the
count from a per-unit rate rather than carrying it across branches — see
`Pyramidal._n_spines` — not by shrinking the spines, which changes what the
drawing says about them.

### 5 · Anchor normals point outward

Two separate bugs here have had connectors reaching *through* a cell.

```python
for a in shape.anchors():
    assert np.dot(a.normal, a.xy - shape.at) > 0     # for a convex body
    assert np.isclose(np.linalg.norm(a.normal), 1.0)
```

Settle "outward" against the body's own centre. Deriving it from a winding
order or a perpendicular's sign is what got it backwards both times.

On a wobbled outline, also check the anchors sit **on** the wall:
`superellipse_radius` returns the *un*-wobbled radius, so an anchor placed
with it alone floats off the drawn wall.

**Measure to the nearest edge, not the nearest vertex, and run it on a
flattened shape.** This check already existed when `Blob` was found placing
every wall anchor off its own wall, and it passed throughout, for two reasons
worth copying into any check you write:

- it measured `min(norm(ring - xy))` — the distance to the closest *vertex*.
  A body carries 240 of them, so the sampling alone is ~0.012, and a
  tolerance of 0.02 could not see an error of 0.011. Use the library's own
  `core.scatter._distance_to`, which projects onto the segments;
- it ran only at the default `aspect=0.88`. The error was exactly **0** on
  every round body and grew with flattening, because `superellipse` applies
  its wobble at the *parameter* angle while the anchor code re-applied it at
  the *polar* angle — two numbers that agree only when `a == b`.

```python
from biodraw.core.scatter import _distance_to
for aspect in (1.0, 0.72, 0.30):                 # round is the blind case
    cell = Blob(aspect=aspect, wobble=0.06, organelles=0, nucleus=None)
    gaps = _distance_to(cell.anchors("wall").points(), cell.geometry["wall"])
    assert gaps.max() < 1e-3
```

The general rule, which is the transferable part: **a parameterisation is not
an angle.** Anything re-evaluating a `t`-indexed term at a known direction has
to invert the forward map first (`paths.superellipse_param`), and a check that
only ever runs on the symmetric case cannot tell you that it did not.

### 5b · An inner part is inside the part that contains it

> Found twice in one session, on two different shapes.

Nothing raises when a nucleus stands through a cell wall. `scatter_in` guards
the things it places and nothing guards the rest, so a nucleus, a nucleoid or
a capsule is checked here or not at all.

```python
from matplotlib.path import Path
body = Path(np.asarray(outer), closed=True)
assert body.contains_points(np.asarray(inner)).all()
```

**Fails if** any point escapes. The two that shipped:

1. `Blob(aspect=0.30)` — the body is 0.165 local units half-tall and the
   default nucleus is 0.187 in radius. A flatter cell holds less, and its
   contents have to come down with it.
2. `Bacterium(nucleoid=...)` on a **curved** body — the nucleoid was built by
   scaling the centreline toward its own centroid, which walks off the arc the
   body was drawn on. 26 points outside the wall on a cell bent 30°, and 0 on
   a rod. Trim along the axis instead of scaling about a point.

Both were invisible on the symmetric default, which is the same lesson as
check 5: **run the containment test on the bent, flattened and twisted cases,
because the straight one is where this class of bug hides.**

### 6 · Parts that must occlude are in separate layers

`render_hollow` unions everything in one call. A nucleus unioned with its cell
body vanishes into it; two neighbouring cells fuse into one long cell.

```python
assert [lay.name for lay in shape.layers] == [...]   # what should occlude what
```

If two parts must not fuse, they need separate `Layer`s. If they *must* fuse —
a spine and its dendrite, a microvillus and its own cell — they belong in one.

### 7 · Neighbouring shapes do not overlap

```python
assert left_outline[:, 0].max() < right_outline[:, 0].min()
```

Watch for bows and wobbles eating the gap: on the epithelial sheet each
lateral wall bulged 0.018 into a gap of 0.0276, so neighbours overlapped and
`gap` did not mean what it said.

### 8 · Determinism

```bash
python tools/build_gallery.py > /dev/null
find examples \( -name "*.png" -o -name "*.svg" \) | sort | xargs sha256sum > /tmp/a
python tools/build_gallery.py > /dev/null
find examples \( -name "*.png" -o -name "*.svg" \) | sort | xargs sha256sum > /tmp/b
diff /tmp/a /tmp/b && echo DETERMINISTIC
```

Any jitter takes a `seed`; never call `np.random` without a seeded generator.
`bd.save` already pins the two things matplotlib randomises in SVG (a
`<dc:date>` and a per-process clip-path salt).

`build_gallery.py --check` reports anything uncommitted under `examples/`,
which includes changes you meant to make. Read the list before believing it.

**And account for every line of it.** If a file you did not touch is listed,
that is a finding, not noise. `examples/basket_cell/blueprint.png` came up
modified after a session that never went near `neuro.Basket`, and the cause
was real: `build_gallery.py` runs every example through `runpy` in one
interpreter, so the `plt.rcParams` each `build.py` sets at import time leaked
into the next one, and adding an example whose folder sorted **earlier**
changed the output of a later one.

The test that isolates it, when a file you did not touch has moved:

```bash
git checkout -- examples/<that one>/ && python tools/build_gallery.py <that one>
git status --porcelain -- examples/<that one>/      # clean?
```

**A single-example rebuild and a full rebuild must agree.** If building one
example alone reproduces the committed image and building everything does
not, the examples are not independent and `--check` is testing the order they
happen to sit in. (Fixed here with `matplotlib.rc_context()` per script — but
the class of bug is *shared process state*, so a new example importing
anything with global settings deserves the same suspicion.)

It is also a **same-machine** test: matplotlib's rasters move with the
libpng/AGG build and its SVG text advances with the freetype version, so the
identical code on another OS produces different bytes for every file. Never
wire it to a runner that is not the machine the images were built on.

### 9 · The counts in the prose are the counts in the drawing

Anything the gallery page asserts — how many anchors, what fits, what raises —
run it. The prose lives in `site/content/<slug>.py`.

```python
print({k: len(cell.anchors(k)) for k in ("spine", "shaft", "soma", "axon")})
```

### 10 · Nothing still refers to what you removed

From Dean, twice in one session: *"delete those axon images"* — about images
that were already gone, because the prose referring to them was not.

`neuro.Axon` was removed in session 2. Its class went, its tests went, its
images went. What stayed was `examples/wiring/README.md`, still titled "Axon
and wiring", still walking through `bouton_len`, still linking five images
that no longer existed — plus two other READMEs pointing at
`../axon_and_wiring/`, a folder that never existed under that name. Nothing
was watching the prose, and it sat there for a whole session.

**Removing a shape is not done until nothing refers to it.** After deleting or
renaming anything, grep for it by name:

```bash
git grep -n -i "axon"                    # the thing you removed
python tools/build_site.py               # fails on any image that is not on disk
```

The site builder's image-existence check is the standing guard for the image
half. The name half is still grep, so run it.

### 11 · The page is a catalog, not an article about one

From Dean, on the live site: *"its still too much text, its should be more
catalog then code-snippet."* At the time the gallery held 6,662 words and 352
lines of code across 66 drawings — about a hundred words per picture — and ten
of its sections carried **no image at all**.

The reason it got there is instructive: documentation rule 2, *more images
than prose*, had been in `docs/PLAN.md` since session 1 and everyone agreed
with it. Nothing measured it, so it drifted for three sessions. It is a number
now.

```bash
python tools/build_site.py     # check_catalog fails the build on any of these
```

`check_catalog` enforces ≤150 words of prose per page, ≤1 code block, ≤20
words per caption, and **no section without a drawing**. When you add or edit
a page, the two judgement calls it cannot make for you:

- **Where the prose goes.** A section with no image is not deleted, it is
  *relocated*. If it explains a picture it becomes a caption or a numbered
  panel note on that picture; if it explains a number it becomes a tuning
  comment beside the number. Before cutting anything, grep for it — the
  pyramidal page's paragraph on why `shaft` anchors sit below the first spine
  was already written at `biodraw/neuro/pyramidal.py:120`, so the cut cost
  nothing. **Check that before you cut, not after.**
- **What survives as a table.** An essay listing four limitations is four
  paragraphs; the same four as a two-column table is catalog data and costs
  no prose budget. That is a real conversion, not a loophole — the cell
  atlas's *what this shape cannot say* went that way and reads better for it.

The failure this catches is not "the page is long". It is **a reader who
wants to know whether a shape suits them having to read an essay to find
out.**

---

### 12 · No drawing colour is a hex literal

**The comment that produced it:** *"these specific blue and red are from my
paper, you dont have to commit to those, but rather choose nicer colours for
the website."*

Retuning the palette moved every shape that asks for its colour properly, and
missed three `ax.fill(..., color="#FFE3E3")` calls in a blueprint — a pale
tint of the *old* red, still sitting behind cells now drawn in blue. A
hardcoded colour does not fail; it silently keeps the palette you have just
replaced, which is the worst way for this to go wrong because the build stays
green.

Two colours are legitimately literal, and the distinction is the whole check:

- **Drawing colours** — anything inking a shape, its wall or its interior —
  must come from `bd.style.palette.get()` or be derived from something that
  did (`render.resolve_fill(None, None, ink)` for a wash).
- **Annotation colours** — the arrows, spans and markers on a *blueprint*, and
  the greys of axis furniture — are a diagram *about* the drawing, not the
  drawing, and may be literal. Declare them once at module scope with a
  comment saying so, rather than inline at the point of use.

```bash
# every hex literal in the example and site sources
grep -rn '"#[0-9A-Fa-f]\{6\}"' --include=*.py examples site
```

---

### 13 · The frame is the drawing's shape, not the figure's

**The comment that produced it:** *"the 'on a branch' eight image is almost
only white space image."*

It was, and it was measurable: the ink filled **62% of that file's width**.
Nothing was watching, so the three emptiest images in the entire catalog were
all sitting on the one page a reader had just complained about.

Two causes, and neither is visible in the code that draws the figure:

1. `save_compact` trims with `bbox_inches="tight"`, which trims to the
   **axes** — not to the ink. The axes are equal-aspect, so a drawing three
   times as tall as it is wide inside a square figure keeps its side margins
   all the way into the committed PNG.
2. `pad_inches` defaults to a **fixed** 0.1 inch. On a wide sheet that is 1%
   of the width; on a portrait 0.86 inches across it is 19% of the file.

```bash
python tools/build_gallery.py <example>     # every run reports loose frames
```

**Fails if** the ink's bounding box uses less than `FRAME_MIN` (72%) of
either axis. **Fix** by shaping the figure like the data — see `_framed` in
`examples/dendritic_spine/build.py`, four lines that take the figsize from
the parts about to be drawn — or by tightening the limits a phantom box set.
Do **not** fix it by cropping in an editor: the image has to regenerate.

It reports rather than fails the build, because a portrait of a round cell
cannot fill a rectangle and the practical floor is around 0.75. The point is
that a 0.62 can no longer pass unnoticed. After the fix: worst frame in the
catalog 75%, median 93%.

The transferable part is the same one as check 11: **a defect a reader can
see in one glance and you cannot see at all is exactly the kind that needs a
number.** Anything about how a drawing *sits on the page* — margins, framing,
alignment across panels, the size of one panel against its neighbour — is
invisible to you and obvious to them.

Every hit must be either a named annotation constant at module scope, or
gone. If a shape's ink is a literal, replace it; if a wash is a literal,
derive it — `resolve_fill` exists precisely so a hand-drawn fill can ask for
the same interior `render_hollow` would have produced.

**Also check the palette's own slots are role-named.** They are `primary`,
`secondary`, `tertiary` — not `excitatory` / `inhibitory`. The old names read
well in `biodraw.neuro` and nowhere else, and the evidence was already in the
tree: `examples/epithelial_sheet` coloured a **nucleus** with
`palette["inhibitory"]` because there was no other slot to reach for. A shared
palette carrying one field's vocabulary is the same mistake as the claim
colours, one level up.

## Reporting

Say what you measured and what you did not. "Tests pass" and "it looks right"
are different claims, and you are not in a position to make the second one.

When a check moves a pin, say **what moved and by how much**. A regenerated
pin with no account of it is a silent regression waiting to happen:

```bash
python tools/update_pins.py --dry-run
```

## When to ask instead of deciding

Where a choice is a scientific claim, **ask**:

- which compartment a contact lands on — a synapse on a spine head and one on
  a shaft are different statements about the circuit;
- whether two cells are level, since nothing should sit on a baseline by
  accident;
- whether an asymmetry is meaningful or decorative.

The library deliberately does not decide any of these for you — there is no
contact-placement engine, because there is no sensible default for a claim.
Name the anchors the figure means, and if you are unsure which it means, ask.

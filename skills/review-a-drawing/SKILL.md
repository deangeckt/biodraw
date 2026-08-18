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

Note that `build_gallery.py --check` cannot tell "untracked" from "modified",
so in a repo where `examples/` was never committed it exits 1 regardless. Use
the hash comparison above until it is committed.

### 9 · The counts in the prose are the counts in the drawing

Anything a README asserts — how many anchors, what fits, what raises — run it.

```python
print({k: len(cell.anchors(k)) for k in ("spine", "shaft", "soma", "axon")})
```

---

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

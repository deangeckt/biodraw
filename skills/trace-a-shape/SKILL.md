---
name: trace-a-shape
description: Turn a photograph, sketch or hand drawing into a biodraw Profile that stamps along a branch like the bundled ones. Use when someone shows you a drawing and wants the library to draw something like it, and the shape does not exist yet. Not for composing a figure from shapes that already exist.
---

# Tracing a shape from a drawing

Derived from `examples/dendritic_spine/`, by starting from the original
whiteboard photograph and rebuilding the blueprint from it. That exercise *is*
this skill.

## Trigger

Someone shows you a picture — a photo of a whiteboard, a sketch, a figure from
a paper — and wants the library to draw something like it. The prompt is
usually as vague as *"let's draw a python-based image like my drawing showing
dendritic spines"*.

**Not** for composing a figure from shapes that exist: that is
[`draw-a-figure`](../draw-a-figure/SKILL.md).

## Why tracing rather than synthesis

The spine that ships here was traced, not built. Every attempt to synthesise
it from ellipses and smoothsteps read as a cone, a bead on a stick, or a leaf.
What makes it read as a spine is a **constant thin neck for the first third,
then an accelerating flare into a blunt, slightly up-tilted head** — and the
cheapest way to get those proportions right is to draw them and trace them.

So when the synthesised version looks wrong, do not add another parameter.
Trace it.

## The method

### 1 · Turn the picture into a parts list, before any code

Counts, angles, fractions. From the worked example: one triangular soma; a
bare apical trunk; the apical **forks at ~40%** into daughters splaying ~35°;
two basals at ~55°; large spines clustered near the tips.

Write this down and show it to the person. It is also the cheapest place to
find out you misread the picture.

### 2 · Check the inventory against the library, and name the gaps out loud

In the worked example the apical fork did not exist. Saying so is what led to
`Branch.child()` — which now also serves axon arbors and astrocytes. Routing
around a gap with a second dendrite drawn at an angle would have produced a
worse drawing *and* left the gap.

**Fix a gap in the core, never in the domain package.**

### 3 · Measure the outline off the image

What actually has to be right, in order:

- **the neck fraction** — how much of the length is constant-width;
- **where the widest point sits** along the axis (`head_t`);
- **how blunt the tip is** — a rounded end and a pointed one read as different
  organelles;
- **the asymmetry** — a hand-drawn profile is not symmetric about its axis,
  and removing that is most of what makes a synthesised one look wrong.

Twenty to forty points around the outline is plenty. More does not help; the
profile is resampled anyway.

### 4 · Put it in the canonical frame

```python
prof = bd.Profile(
    points=traced,          # (N, 2), any units, any orientation
    normalize=True,         # → base chord at the origin, tip at x=1
    tip="wide",             # 'wide' for a spine or bouton; 'narrow' for a thorn
    n_pts=120,              # resampled evenly along its arclength
    head_t=0.82,            # where the widest point sits, as a fraction
    head_r=0.28,            # stand-off radius there
    stretch=(0.10, 0.38),   # the span that absorbs `extend` — the neck
    source="Dean's whiteboard, 2026-08-16",     # provenance; see below
)
bd.core.profile.register("mine", prof)
```

**`tip` cannot be guessed** and is the one argument that silently ruins a
trace: a spine is attached by a narrow neck and ends wide; a thorn is the
other way round. Getting it backwards places every decoration head-down.

**`stretch` is the knob that matters.** It marks the span that absorbs
`extend`, so the shape can stand further off its branch *without* the head
growing with it. Scaling a profile whole makes a densely decorated branch
whose heads touch. For a spine the span is the neck.

It does double duty, so set it honestly: `place(head=, neck=)` scales the two
widths, and the blend between them runs from the **end of `stretch`** to
`head_t`. Those two numbers are what let one traced outline cover thin,
stubby and mushroom spines — a `stretch` that stops halfway up the flare will
put the neck's width where the head's should be.

### 5 · Check it against the drawing, numerically

You cannot see the result. Compare what you can compute:

```python
print(prof.describe())      # length, width, head_t, head_r, stretch, source
```

- Is the width/length ratio what you measured off the image?
- Does `head_offset()` land where the widest point looked?
- Stamp it along a branch and confirm the heads do not overlap:
  compare `head_r * size` against the spacing between consecutive heads.

Then render at `--quality debug` and **send the image to the person who
supplied the drawing.** They have the original in front of them; you do not.

### 6 · Record the provenance

`source` is not optional in spirit. A traced profile is a *claim about what
something looks like*, and the next person deserves to know whose drawing it
came from and when.

### 7 · Lock it

A shape is finished when it exposes anchors, has a pinned digest, and appears
in an example. Add it to `tests/shapes.py` and run:

```bash
python tools/update_pins.py --dry-run
```

Pin the geometry; do **not** write tests asserting how it looks. See the note
at the top of `tests/test_pyramidal.py`.

## The transferable lessons

These are the payload, and they generalise past tracing:

- **Inventory before code.**
- **Name gaps rather than routing around them**, and fix them in the core.
- **Diagnose numerically, because you cannot see.** In the worked example the
  first render came out lopsided; one number (39.5° of tangent error) found
  the cause, where staring at it would not have.
- **Document the surprising defaults.** A naive agent picks
  `relative_to="tangent"` every time and then chases the error with
  `angle_deg`, which never converges.
- **Symmetry is a claim.** The second render was symmetric and still wrong —
  the daughters curved inward and read as two branches about to rejoin. The
  third was wrong *because* it was symmetric.

## Then

Run [`review-a-drawing`](../review-a-drawing/SKILL.md).

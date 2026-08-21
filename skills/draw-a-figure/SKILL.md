---
name: draw-a-figure
description: Build a figure from biodraw shapes that already exist — a cell, a panel, a wired circuit. Covers the order of work, the two unit systems, and where to stop and ask. Use when someone describes a figure they want; use trace-a-shape instead when the shape itself does not exist yet.
---

# Building a figure

Derived from `examples/pyramidal_cell/`, `examples/generic_cell/` and
`examples/epithelial_sheet/`, which are the worked cases.

## Trigger

Someone describes a drawing they want and the shapes for it exist. If the
shape does not exist, that is [`trace-a-shape`](../trace-a-shape/SKILL.md);
if the shape exists but the core cannot express it, extend the **core**, never
the domain package.

## Order of work

1. **Inventory before code.** Turn the description into a parts list — counts,
   angles, fractions — before writing a line. One triangular soma; a bare
   trunk; the apical forks at ~40%; two basals at ~55°. Doing this first is
   what surfaces the gaps.
2. **Check the inventory against the library and name any gap out loud.** Say
   "the apical fork does not exist" rather than routing around it with a
   second dendrite drawn at an angle.
3. **`bd.catalog()` before writing code** — the API surface as data. Do not
   grep the source to find what a shape takes. *(Not yet implemented; until it
   is, read the class docstring, which documents every knob's effect.)*
4. **Build one shape, check it, then compose.** A panel that is wrong is
   usually wrong in one shape.
5. **Fit last.** `bd.fit(ax, parts, pad=...)` after everything is drawn.
6. **Save with `bd.save`**, not `fig.savefig` — it keeps text as text, names
   the SVG layers, refuses a rasterized artist, and writes byte-reproducibly.
7. **Run [`review-a-drawing`](../review-a-drawing/SKILL.md)** before saying it
   is done, and send the image to the user.

## Units: the one thing that bites

| in **local units** | in **points** |
|---|---|
| lengths, widths, gaps, `pad`, positions | `wall_lw`, dot sizes, font sizes |
| scale with the drawing | **do not** scale with the drawing |

A panel drawn at half size keeps its linewidths and comes out heavy. Reach for
a `biodraw.style` preset rather than patching it per figure.

## Composing a panel

Shapes draw onto an ordinary matplotlib axes, so a figure can be half cartoon
and half data.

```python
fig, ax = bd.canvas(figsize=(6.0, 3.0))

pyr = bd.neuro.Pyramidal(spines=8, basal=2, at=(0.0, 0.0))
bas = bd.cells.Blob(organelles=6, at=(3.0, 0.4), seed=1)
for shape in (pyr, bas):
    shape.draw(ax=ax, wall_lw=1.0, gid=type(shape).__name__.lower())

bd.fit(ax, pyr.points + bas.points, pad=0.25)
```

Anything drawn in one `render_hollow` call **fuses**. Parts that must occlude
each other belong in different layers — see `core.shape.Layer`.

## Wiring cells together

Connectors consume anchors, so they stand off correctly at any angle without
per-figure tuning:

```python
bd.connect(
    ax=ax,
    source=bas.anchor("soma", deg=0.0),          # where it leaves
    target=pyr.anchor("spine", branch="apical", rank=-1),
    gap=0.03,               # clearance at the target, in local units
    drop=0.45,              # straight descent before the run begins
    rad=0.06,               # bow; positive always bows *up*
    endcap="bar",           # the claim: a bar is inhibition
)
```

One source reaching several targets is **one branching arbor**, not several
strokes — `bd.connect_tree`. Two lines out of one body running side by side
read as two axons, and on a staggered row they cross each other.

## Marking contacts

There is **no contact-placement engine, on purpose.** Which compartment a
synapse lands on is the figure's scientific claim, not a drawing decision, so
the library gives you the places and you say which:

```python
targets = [cell.anchor("soma", side=1, t=t) for t in (0.24, 0.42, 0.60)]
bd.connect_tree(ax=ax, source=src, targets=targets, endcap="bar")
```

If you want a bare mark rather than a connector, `Anchor.offset(gap)` gives
the stand-off and `ax.scatter` does the rest. That is the right amount of
library for it.

## House style

- **Vector only.** Never `rasterized=True`, never a PNG intermediate.
- **Colour means something.** Identity colours name what a thing *is*; claim
  colours name what the figure *asserts*. Anything belonging to neither takes
  grey. Do not introduce a fourth hue for decoration. To make one thing read
  as denser than another, use *more of the same ink* — a layer's `fill_alpha`
  — not a second hue.
- **One idea per panel**, said in the heading.
- **Nothing sits on a baseline by accident.** If two cells are level, it is
  because being level means something.
- **Keep the tuning comments.** They record why a number is what it is,
  usually after something looked wrong.

## Where to stop and ask

- which compartment a contact lands on;
- whether two cells should be level;
- whether an asymmetry is meaningful or decorative;
- anything where two readings of the request give materially different
  figures.

These are scientific claims, not styling choices.

## Documenting it

If the figure becomes an example, the rules are in `docs/RULES.md`. The short
version: **image first, code second**, always; more images than prose; every
documented call uses named arguments with trailing comments; variants are the
unit of documentation, shown as grids rather than portraits; every example
folder carries a blueprint.

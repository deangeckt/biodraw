# Contributing to biodraw

New shapes, new domains, palettes, examples, and traced profiles from your own
drawings are all welcome.

## Setup

```bash
pip install -e ".[dev]"
pytest --mpl
```

`--mpl` turns on the image comparisons. Without it the figures are still built
(so an exception still fails), just not compared.

## The one architectural rule

`biodraw.core` knows nothing about biology. Cells, dendrites and synapses live
in domain packages (`biodraw.neuro`, `biodraw.cells`, `biodraw.micro`) built
entirely on the core's primitives — profiles, branches, tubes, bodies,
connectors, anchors, hollow rendering.

If your shape cannot be expressed with those, **extend the core**. Do not
special-case it upstairs. The last time a drawing kit grew neuron-shaped
assumptions it took a rewrite to get them out, which is why this repo exists.

## Adding a shape

A shape is finished when it:

1. **exposes anchors** — `(point, outward normal)` for its named parts, so
   connectors, synapse dots and leader labels all work on it without knowing
   what it is;
2. **documents every knob's effect**, not just its type. `basal_angle_deg:
   float` is useless; "how far a basal leans off straight down; larger splays
   the legs wider; past ~60 deg they lie along the soma's bottom edge and
   flatten the triangle" is what someone actually needs;
3. **has an `explain()` view** showing how it is constructed;
4. **has a pinned baseline image** in `tests/baseline/`;
5. **carries its provenance** if traced from a drawing — whose drawing, and
   how it was normalised.

## Contributing a traced profile

This is the most welcome kind of contribution, and the reason `biodraw` looks
the way it does. Shapes drawn by hand read as drawn; shapes synthesised from
ellipses read as clip art.

```python
pts  = bd.trace.from_image("sketch.jpg")
prof = bd.trace.normalize(pts, tip="wide")
bd.explain(prof)                 # check the frame, the stretch span, the head
bd.profile.register("bouton", prof)
```

Then add it under `biodraw/core/profiles/`, following `spine.py`: the points
array, the metadata (`head_t`, `head_r`, `stretch`), and a docstring saying
where the shape came from and what makes it read as that shape and not
something else. Commit the sketch alongside it.

## Regression nets

**Geometry pins** are the main one. `tests/shape_pins.json` holds a digest of
every shape's vertices — vertex count, bounding box, centroid, path length and
a hash. Add your shape to `tests/shapes.py` and it is covered.

```bash
pytest tests/test_pins.py             # what moved
python tools/update_pins.py --dry-run # what would change
python tools/update_pins.py           # regenerate, if intended
```

Digests rather than images because this is a geometry library: what a refactor
silently breaks is the vertices, not the pixels. A digest is ~240 bytes and
exact; a PNG is tens of kilobytes and tolerance-based. With dozens of shapes,
that difference is the whole repo.

**Two baseline images** cover what geometry cannot: that the two-pass union
really fuses, and that a wall comes out the weight it was asked for. Keep it at
two.

Either way, describe the change in the PR. "Regenerated pins" on its own is not
a review anyone can do.

## Example images

Each folder under `examples/` owns a `build.py` that regenerates every image
the gallery shows for it:

```bash
python tools/build_gallery.py           # rebuild all
python tools/build_gallery.py --check   # rebuild and fail on any diff
```

The page that reads those images is `site/content/<name>.py`, and the two
rebuild separately:

```bash
python tools/build_site.py              # the gallery, from site/content/*.py
```

Adding an example means adding both — a folder under `examples/` and a content
module — and nothing else; neither tool keeps a list.

Images must regenerate byte-identically, so nothing may depend on unseeded
randomness — on *one machine*. matplotlib's raster and SVG output both move
with the underlying libpng/freetype build, so rebuilding on a different OS
changes every file and proves nothing.

## Code style

- `ruff check .` and `ruff format --diff .` should be clean; line length 79.
- Geometry code is written in the vocabulary of its maths — `u`, `v`, `t`,
  `hw` are fine when the docstring defines them.
- **Keep and extend the comments.** The ones in this codebase record why a
  number is what it is, usually discovered after something looked wrong. They
  are the most expensive thing in the repo to rediscover.

## Scope

In: anything that helps draw biology as clean vectors.

Out: reading data formats, analysis, anything requiring a dependency beyond
`numpy` and `matplotlib`. Draw the cartoon here; plot your data with
matplotlib beside it.

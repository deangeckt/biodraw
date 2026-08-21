# Scope

Why `biodraw` is shaped the way it is: where it came from, what it is for,
what it deliberately is not, and what it will not trade away.

For the rules this shape implies, see [RULES.md](RULES.md); for what is
coming, [ROADMAP.md](ROADMAP.md); for what has already been built and what
broke on the way, [MILESTONES.md](MILESTONES.md) and [STATE.md](STATE.md).

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

## Non-negotiables

- **Keep the tuning comments.** They record why a number is what it is,
  usually discovered after something looked wrong. They are the most expensive
  thing here to rediscover.
- Vector only. No rasterized fallback anywhere.
- Runtime dependencies: `numpy` and `matplotlib`. Nothing else.
- Pin a drawing before refactoring it.

## Verification

```bash
pip install -e ".[dev]"
pytest --mpl                                  # geometry + pinned images
pytest --mpl-generate-path=tests/baseline     # regenerate, if intended
ruff check .
python tools/build_gallery.py --check         # examples rebuild identically
```

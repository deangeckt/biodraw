# Roadmap

Where `biodraw` is going. Short on purpose — the long version is four files,
listed at the bottom.

`biodraw` draws cartoon biology as vectors onto a matplotlib axes, so a figure
sits beside real data and a *variant* is a parameter rather than a second file
to download. → **[Browse the catalog](https://deangeckt.github.io/biodraw/)**

## What is in it now

| domain | what it draws |
|---|---|
| `neuro` | pyramidal and basket cells, a radial body plan behind bipolar, granule, Purkinje and astrocyte, dendritic spines, circuit motifs and wiring |
| `cells` | a generic cell body with nucleus, organelles and protrusions; an epithelial sheet, curvable into a villus or a duct; twelve named cell types from that one class |
| `micro` | bacteria — coccus, bacillus, vibrio and spirillum as points in one space, with flagellar arrangements |
| `genetics` | construct tracks (repeats, promoters, CDSs, terminators) and lobed proteins with domain tags |
| `animals` | mouse, fly, zebrafish and worm as silhouettes, each mirrored by `facing=±1` |
| `lab` | a compound microscope, upright or inverted, with *n* objectives on the nosepiece |

Plus the domain-neutral core everything is built on — branches, profiles,
bodies, tracks, anchors, connectors, scatter, layers — and the two things
that consume anchors rather than drawing shapes: `connect` for strokes
between shapes, and `label` / `scalebar` for the text beside one. Then three
[skills](../skills/README.md), which are the supported way to drive it.

## What is next

1. **The agent-facing layer — `bd.catalog()`, `bd.check()`, `bd.explain()`.**
   Milestone 7 shipped its skills half only, and milestone 5 never started.
   The package docstring currently promises all three by name and none of them
   exists. `bd.check()` in particular is `review-a-drawing`'s prose checks
   written as code, which is this repo's own rule about rules applied to
   itself.
2. **Layout and style presets — milestone 4.** Fully specified, both design
   decisions taken, and byte-identity is its acceptance test. It ranks here
   rather than higher precisely because of that: it changes no committed
   image.
3. **Smaller, and open:** a crossbar tuft (the one drawing gap left from the
   neuron summary figure); more organisms — frog, macaque, chick,
   *Arabidopsis*; more instruments, if any of them turns out to have a count
   in it the way a nosepiece does; a general `neck_polygon`; the variant
   pop-out on contact sheets. Details in [STATE.md](STATE.md), *Open, in
   priority order*.

Nobody has yet needed a **pose knob** on an animal, which was the open design
question when that category was built. Silhouettes were shipped instead of a
jointed rig, and that is still the right call until someone asks.

Items 1 and 2 are **utilities** rather than shapes, and neither gets a
catalog page: the catalog is a catalog of drawings, and a page for something
the library does not draw came back off within the hour it went up.
Documentation rule 9 in [RULES.md](RULES.md) has the argument. Item 3 is
shapes, and those do belong in the catalog.

## What is deliberately not planned

The most useful column in a roadmap, and the one that keeps getting longer:

- **Competing with stock asset libraries.** NIAID's
  [BioArt](https://bioart.niaid.nih.gov/) carries thousands of vectors. If a
  figure needs a virion or a centrifuge, download one. What is built here is
  what a static asset cannot be: a thing that varies.
- **A placement engine.** Built, worked, removed. Which compartment a synapse
  lands on is the author's scientific claim, not a drawing decision.
- **Claim colours.** Removed with it — one paper's argument, living in a
  general library's palette.
- **A realistic axon.** Built, and deleted: at the size an axon appears in a
  circuit panel it reads as a fat beaded worm and pulls the eye off the cells
  it exists to connect. A line with a mark on the end is faster to parse.
- **An image-tracing parser.** Someone with a drawing photographs it and talks
  to an agent about it. The recipe is [`skills/trace-a-shape`](../skills/trace-a-shape/SKILL.md);
  a `from_image` toolkit would be a worse version of the conversation they
  were going to have anyway.
- **Cloning reference figures.** A reference is a source of *capabilities*.
  `examples/summary_figure/` reproduced one closely and was removed the same
  session; its three capabilities went into the catalog and the figure did
  not.
- **Runtime dependencies beyond numpy and matplotlib**, and any rasterized
  fallback. Neither is negotiable.
- **CI.** The rebuild check is same-machine by nature and could never pass on
  a hosted runner. See [STATE.md](STATE.md), *CI, and why there isn't any*.

## The long version

| | |
|---|---|
| [SCOPE.md](SCOPE.md) | why the library is shaped this way, and what it will not trade away |
| [RULES.md](RULES.md) | the rules pages, drawings, images and skills are checked against |
| [MILESTONES.md](MILESTONES.md) | what was built, in order, and what each one cost |
| [STATE.md](STATE.md) | where it stands: decisions taken, bugs found, what is open |

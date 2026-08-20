"""The radial body plan, and the cells that are settings of it.

A basket, bipolar, granule, Purkinje and astrocyte are not five shapes. They
are `RadialCell` at five settings — a soma with processes leaving it, differing
in how many leave, over what arc, how long they are and how often they branch.
This page is the evidence for that claim and the catalog of what it buys.

    python tools/build_gallery.py radial
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

import biodraw as bd  # noqa: E402
from biodraw.neuro.radial import RadialCell  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
PAL = bd.style.palette.get()
EXC, INH = PAL["primary"], PAL["secondary"]
# Annotation colour for the sheet captions — not part of any drawing.
TEXT = "#555555"

FORMS = [("Pyramidal", bd.neuro.Pyramidal, EXC),
         ("Basket", bd.neuro.Basket, INH),
         ("Bipolar", bd.neuro.Bipolar, INH),
         ("Granule", bd.neuro.Granule, INH),
         ("Purkinje", bd.neuro.Purkinje, INH),
         ("Astrocyte", bd.neuro.Astrocyte, INH)]


def _row(ax, shape, ink, wall_lw=0.85, pad=0.22):
    bd.canvas(ax=ax)
    shape.draw(ax=ax, edge=ink, wall_lw=wall_lw)
    shape.fit(ax, pad=pad)


def types():
    """The whole set, at the size a reader meets them."""
    fig, axes = plt.subplots(1, len(FORMS), figsize=(2.1 * len(FORMS), 3.0),
                             dpi=110)
    for ax, (name, cls, ink) in zip(axes, FORMS, strict=True):
        _row(ax, cls(), ink)
        ax.set_title(name, fontsize=9, color=TEXT)
    fig.tight_layout(pad=0.3)
    return fig, "types.png"


def told_apart():
    """The same six with no colour at all.

    The check that matters: if a cell is only recognisable by its hue it will
    fail a greyscale printout, and a reader with the commonest form of colour
    blindness never had the hue to begin with. Every one of these is named by
    its silhouette.
    """
    fig, axes = plt.subplots(1, len(FORMS), figsize=(2.1 * len(FORMS), 3.0),
                             dpi=110)
    for ax, (name, cls, _) in zip(axes, FORMS, strict=True):
        _row(ax, cls(), "#333333")
        ax.set_title(name, fontsize=9, color=TEXT)
    fig.tight_layout(pad=0.3)
    return fig, "told_apart.png"


def arc():
    """The arc is what turns a star into a fan.

    360 degrees is a stellate cell, a wedge is a Purkinje, and 180 with two
    processes is bipolar — one parameter covering three cells nobody would
    call related.
    """
    arcs = (360.0, 240.0, 150.0, 80.0, 34.0)
    fig, axes = plt.subplots(1, len(arcs), figsize=(1.9 * len(arcs), 2.9),
                             dpi=110)
    for ax, a in zip(axes, arcs, strict=True):
        _row(ax, RadialCell(dendrites=5, arc_deg=a, start_deg=90.0 - a / 2,
                            length=1.0, forks=0.55, depth=2, seed=1), INH)
        ax.set_title(f"arc {a:g}°", fontsize=9, color=TEXT)
    fig.tight_layout(pad=0.3)
    return fig, "arc.png"


def depth():
    """Branching depth, and where it stops helping.

    Branch count is `dendrites * (2^(depth+1) - 1)`, so it climbs far faster
    than it reads: three processes at depth 4 is forty-five branches sweeping
    one arc. The recursion does not avoid itself, so past about 3 the extra
    generation stops adding detail and starts adding crossings.
    """
    fig, axes = plt.subplots(1, 4, figsize=(7.8, 2.9), dpi=110)
    for ax, d in zip(axes, (1, 2, 3, 4), strict=True):
        cell = RadialCell(dendrites=3, arc_deg=150.0, start_deg=15.0,
                          length=1.1, forks=0.5, depth=d, taper=0.5, seed=4)
        _row(ax, cell, INH)
        ax.set_title(f"depth {d} — {len(cell._branches())} branches",
                     fontsize=8.5, color=TEXT)
    fig.tight_layout(pad=0.3)
    return fig, "depth.png"


def sizes():
    """Proportion is identity too.

    A granule cell drawn at a basket cell's proportions stops reading as one.
    Same process count, same branching — only the ratio of soma to process
    length changes.
    """
    lengths = (0.5, 0.8, 1.2, 1.8)
    fig, axes = plt.subplots(1, len(lengths),
                             figsize=(1.9 * len(lengths), 2.9), dpi=110)
    for ax, ln in zip(axes, lengths, strict=True):
        _row(ax, RadialCell(dendrites=5, length=ln, forks=0.55, depth=2,
                            seed=1), INH)
        ax.set_title(f"length {ln:g}", fontsize=9, color=TEXT)
    fig.tight_layout(pad=0.3)
    return fig, "sizes.png"


BUILDS = (types, told_apart, arc, depth, sizes)


def main():
    for build in BUILDS:
        fig, name = build()
        bd.save_compact(fig, HERE / name)
        plt.close(fig)
        size = (HERE / name).stat().st_size / 1024
        print(f"wrote {(HERE / name).relative_to(HERE.parent.parent)} "
              f"({size:.0f} KB)")


if __name__ == "__main__":
    main()

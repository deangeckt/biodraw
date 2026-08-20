"""The Purkinje cell: a flat fan over one soma.

The most recognisable neuron there is, and the recognition is entirely about
the **arc** — everything leaves upward into a wedge rather than in every
direction — and the **depth** it branches to. Both are `RadialCell`
parameters, so this whole page is one shape at settings; see
`biodraw/neuro/types.py`.

    python tools/build_gallery.py purkinje
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

import biodraw as bd  # noqa: E402
from biodraw.neuro import Purkinje  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
INK = bd.style.palette.get()["secondary"]
# Annotation colour for the panel captions — a caption is not a drawing.
TEXT = "#555555"


def _panel(ax, cell, pad=0.20):
    bd.canvas(ax=ax)
    cell.draw(ax=ax, edge=INK, wall_lw=0.85)
    cell.fit(ax, pad=pad)


def _sheet(cells, name, width=1.9, height=3.0):
    """One row of cells, each with its caption underneath."""
    fig, axes = plt.subplots(1, len(cells), figsize=(width * len(cells),
                                                     height), dpi=110)
    for ax, (label, cell) in zip(axes, cells, strict=True):
        _panel(ax, cell)
        ax.set_title(label, fontsize=9, color=TEXT)
    fig.tight_layout(pad=0.3)
    return fig, name


def portrait():
    """The cell as a reader meets it."""
    fig, ax = bd.canvas(figsize=(2.6, 3.4))
    cell = Purkinje()
    cell.draw(ax=ax, edge=INK, wall_lw=1.0)
    cell.fit(ax, pad=0.12)
    return fig, "purkinje.png"


def wedge():
    """The arc, which is the whole identity.

    Wide enough and it is a stellate cell with a preference; narrow enough
    and the primaries overlap before they have branched. The default sits at
    55 degrees, where the fan is flat but the daughters still have room.
    """
    return _sheet([(f"arc {a:g}°",
                    Purkinje(arc_deg=a, start_deg=90.0 - a / 2))
                   for a in (28.0, 55.0, 90.0, 140.0)], "wedge.png")


def fan():
    """How dense the fan is, and where the extra generation stops helping.

    Branch count is `dendrites * (2^(depth+1) - 1)`, so it climbs far faster
    than it reads: three primaries at depth 4 is ninety-three branches
    sweeping one wedge, and they cross each other until the union fuses the
    fan into a lattice with holes in it. Depth is not a quality knob.
    """
    cells = []
    for d in (1, 2, 3, 4):
        cell = Purkinje(depth=d)
        cells.append((f"depth {d} — {len(cell._branches())} branches", cell))
    return _sheet(cells, "fan.png")


BUILDS = (portrait, wedge, fan)


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

"""The granule cell: a small soma with a few short, clawed dendrites.

The smallest neuron in the set, and the one whose **proportions** carry the
identity: a granule cell is mostly soma, with dendrites barely longer than the
cell body and ending in short forked claws. Drawn at a basket cell's
proportions it stops reading as a granule cell at all, which is why `length`
is the knob that matters here and not the count.

    python tools/build_gallery.py granule
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

import biodraw as bd  # noqa: E402
from biodraw.neuro import Granule  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
INK = bd.style.palette.get()["secondary"]
# Annotation colour for the panel captions — a caption is not a drawing.
TEXT = "#555555"


def _sheet(cells, name, width=1.8, height=2.6):
    fig, axes = plt.subplots(1, len(cells), figsize=(width * len(cells),
                                                     height), dpi=110)
    for ax, (label, cell) in zip(axes, cells, strict=True):
        bd.canvas(ax=ax)
        cell.draw(ax=ax, edge=INK, wall_lw=0.85)
        cell.fit(ax, pad=0.18)
        ax.set_title(label, fontsize=9, color=TEXT)
    fig.tight_layout(pad=0.3)
    return fig, name


def portrait():
    """The cell as a reader meets it."""
    fig, ax = bd.canvas(figsize=(2.8, 2.8))
    cell = Granule()
    cell.draw(ax=ax, edge=INK, wall_lw=1.0)
    cell.fit(ax, pad=0.10)
    return fig, "granule.png"


def proportion():
    """Dendrite length against a soma that does not change.

    The identity knob. Every panel is the same cell with the same four
    processes and the same branching — only the ratio of soma to process
    moves — and only the first two read as a granule cell. The last is a
    small stellate cell, which is a different claim about what it is.
    """
    return _sheet([(f"length {ln:g}", Granule(length=ln))
                   for ln in (0.60, 0.85, 1.25, 1.80)], "proportion.png")


def claws():
    """How many dendrites, and how much claw is on the end of each.

    A granule cell's dendrites end in a short, wide fork — the claw — which
    is `forks` late along the process and a wide `fork_angle_deg`. Drop the
    fork and the cell reads as a tiny multipolar neuron instead.
    """
    cells = [("no claw", Granule(forks=None)),
             ("3 dendrites", Granule(dendrites=3)),
             ("4 — the default", Granule()),
             ("6 dendrites", Granule(dendrites=6))]
    return _sheet(cells, "claws.png")


BUILDS = (portrait, proportion, claws)


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

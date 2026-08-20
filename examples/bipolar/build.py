"""The bipolar cell: one process out of each end of an elongated soma.

The simplest body plan in the library and the most distinctive, because two
opposed processes is a silhouette nothing else here shares. Retinal bipolar
cells, many sensory neurons and most cultured cells at an early stage read
this way — and the same shape at a narrower arc is a bitufted interneuron,
which is the argument for one shape with an `arc_deg` rather than two
classes. See `biodraw/neuro/types.py`.

    python tools/build_gallery.py bipolar
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import biodraw as bd  # noqa: E402
from biodraw.neuro import Bipolar  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
INK = bd.style.palette.get()["secondary"]
# Annotation colour for the panel captions — a caption is not a drawing.
TEXT = "#555555"


def _sheet(cells, name, width=1.7, height=3.2):
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
    """The cell as a reader meets it, in a frame shaped like it.

    A bipolar cell is four times as tall as it is wide, so a figure that is
    not loses the difference to white space — caught at 61% of its width by
    the frame report in `tools/build_gallery.py`.
    """
    cell = Bipolar()
    xy = np.concatenate(cell.points)
    w, h = np.ptp(xy[:, 0]) + 0.24, np.ptp(xy[:, 1]) + 0.24
    fig, ax = bd.canvas(figsize=(3.6 * w / h, 3.6))
    cell.draw(ax=ax, edge=INK, wall_lw=1.0)
    cell.fit(ax, pad=0.10)
    return fig, "bipolar.png"


def separation():
    """The angle between the two processes, and where the name changes.

    At 180 degrees they are opposed and the cell is bipolar. Bring them round
    to the same side and the same two processes read as a bitufted cell — one
    parameter covering two cell types nobody would draw with one class.
    """
    return _sheet([(f"arc {a:g}°", Bipolar(arc_deg=a, start_deg=90.0 - a / 2))
                   for a in (180.0, 140.0, 100.0, 60.0)], "separation.png")


def soma():
    """`aspect` — the soma stretched along the axis the processes leave on.

    Not decoration. A circular soma with two arms reads as a cell that
    *happens* to have two processes; stretched along their axis it reads as
    **polarised**, which is the claim a bipolar cell is making.
    """
    return _sheet([(f"aspect {a:g}", Bipolar(aspect=a))
                   for a in (1.0, 1.4, 1.75, 2.4)], "soma.png")


BUILDS = (portrait, separation, soma)


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

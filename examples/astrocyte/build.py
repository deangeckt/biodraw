"""The astrocyte: a bush of fine processes in every direction.

Not a neuron, and drawn so nobody mistakes it for one — where a Purkinje cell
is a fan, this is a cloud. Two knobs carry it: how many processes leave, and
how fast they thin. Both are `RadialCell` parameters; see
`biodraw/neuro/types.py`.

    python tools/build_gallery.py astrocyte
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

import biodraw as bd  # noqa: E402
from biodraw.neuro import Astrocyte  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
INK = bd.style.palette.get()["tertiary"]
# Annotation colour for the panel captions — a caption is not a drawing.
TEXT = "#555555"


def _sheet(cells, name, width=1.9, height=2.8):
    fig, axes = plt.subplots(1, len(cells), figsize=(width * len(cells),
                                                     height), dpi=110)
    for ax, (label, cell) in zip(axes, cells, strict=True):
        bd.canvas(ax=ax)
        cell.draw(ax=ax, edge=INK, wall_lw=0.8)
        cell.fit(ax, pad=0.18)
        ax.set_title(label, fontsize=9, color=TEXT)
    fig.tight_layout(pad=0.3)
    return fig, name


def portrait():
    """The cell as a reader meets it."""
    fig, ax = bd.canvas(figsize=(3.0, 3.0))
    cell = Astrocyte()
    cell.draw(ax=ax, edge=INK, wall_lw=0.9)
    cell.fit(ax, pad=0.10)
    return fig, "astrocyte.png"


def bushiness():
    """How many processes leave, which is the only count that reads.

    Under about six the cell reads as a small neuron with untidy dendrites;
    past about fourteen the soma disappears inside its own bush and the whole
    thing becomes a blot. The default sits at ten.
    """
    return _sheet([(f"{n} processes", Astrocyte(dendrites=n))
                   for n in (5, 10, 14, 18)], "bushiness.png")


def fineness():
    """`taper` — the width at the tip, as a multiple of the width at the soma.

    Severe on purpose here. Astrocytic processes get very fine very fast, and
    a bush drawn at near-constant width reads as a root system: the eye takes
    a process that stays thick for its whole length as a *tube* rather than a
    tapering arbour.
    """
    return _sheet([(f"taper {t:g}", Astrocyte(taper=t))
                   for t in (0.85, 0.60, 0.38, 0.22)], "fineness.png")


BUILDS = (portrait, bushiness, fineness)


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

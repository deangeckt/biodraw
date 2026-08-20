"""Model organisms as silhouettes: mouse, fly, zebrafish, worm.

The house style is the whole point here, and it came from the maintainer:
*"use very simple drawings, not complex realistic images, sometimes an
outline is even enough."* Every animal on this page is a handful of fused
bodies with no interior detail beyond an eye — the shape that survives at the
centimetre a methods figure prints it at.

What each one varies is what somebody would actually change: the mouse's tail
against its body, the fly's wings, the fish's stripe count, how curled the
worm is — and, on all four, **which way it faces**, which is the thing a
stock library cannot give you because it ships one file per view.

    python tools/build_gallery.py animals
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import biodraw as bd  # noqa: E402
from biodraw.animals import Fly, Mouse, Worm, Zebrafish  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
INK = bd.style.palette.get()["neutral"]
# Annotation colours for the sheets and the blueprint — a caption is not a
# drawing, and neither is a construction arrow.
TEXT = "#555555"
GREY = "#9AA0A6"

plt.rcParams.update({"font.size": 9})

FORMS = (("Mouse", Mouse), ("Fly", Fly), ("Zebrafish", Zebrafish),
         ("Worm", Worm))


def _panel(ax, animals, pad=0.12, lw=1.1):
    bd.canvas(ax=ax)
    for animal in animals:
        animal.draw(ax=ax, edge=INK, wall_lw=lw)
    bd.fit(ax, [p for a in animals for p in a.points], pad=pad)


def portraits():
    """The four, each at its own drawn size."""
    fig, axes = plt.subplots(1, len(FORMS), figsize=(2.5 * len(FORMS), 2.2),
                             dpi=110)
    for ax, (name, cls) in zip(axes, FORMS, strict=True):
        _panel(ax, [cls()])
        ax.set_title(name, fontsize=9.5, color=TEXT)
    fig.tight_layout(pad=0.3)
    return fig, "animals.png"


def blueprint():
    """A mouse, taken apart and put back together.

    Four bodies, two legs and a tube — and the only reason it reads as a
    mouse rather than as seven shapes is that `render_hollow` fuses them into
    one contour. The middle panel is what the parts look like before that.
    """
    fig, axes = plt.subplots(1, 3, figsize=(9.6, 2.5), dpi=150)
    mouse = Mouse()

    # -- 1. the parts, each on its own --------------------------------------
    ax = axes[0]
    bd.canvas(ax=ax)
    closed, open_ = mouse.parts
    for part in [*closed, *open_]:
        p = np.asarray(part)
        ax.plot(p[:, 0], p[:, 1], color=GREY, lw=0.9)
    mouse.fit(ax, pad=0.12)
    ax.set_title("1 · seven outlines", fontsize=9.5, loc="left", color=TEXT)

    # -- 2. fused -----------------------------------------------------------
    ax = axes[1]
    _panel(ax, [mouse])
    ax.set_title("2 · one union", fontsize=9.5, loc="left", color=TEXT)

    # -- 3. the anchors it exposes ------------------------------------------
    ax = axes[2]
    _panel(ax, [mouse])
    for a in mouse.anchors("wall"):
        ax.plot(*a.xy, "o", ms=2.6, color=GREY, zorder=8)
    for kind in ("nose", "tail"):
        a = mouse.anchor(kind)
        ax.annotate(kind, xy=a.xy, xytext=a.offset(0.22), fontsize=8,
                    color=TEXT, ha="center",
                    arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    ax.set_title("3 · wall anchors, and the two it names", fontsize=9.5,
                 loc="left", color=TEXT)

    fig.tight_layout(w_pad=1.4)
    return fig, "blueprint.png"


def facing():
    """The knob a downloaded silhouette cannot have.

    A figure with the animal on the left of the panel and one with it on the
    right want the same animal turned round — not rotated, which would put it
    on its back. Mirrored, both drawings are one object at `facing=+1` and
    `facing=-1`, and they match each other exactly.
    """
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.4), dpi=150)
    _panel(axes[0], [Mouse(facing=1, at=(-0.75, 0.0)),
                     Mouse(facing=-1, at=(0.75, 0.0))])
    axes[0].set_title("facing +1 and -1", fontsize=9.5, color=TEXT)
    _panel(axes[1], [Zebrafish(facing=1, at=(-0.55, 0.18)),
                     Zebrafish(facing=-1, at=(0.55, -0.18))])
    axes[1].set_title("...on any of them", fontsize=9.5, color=TEXT)
    fig.tight_layout(pad=0.4)
    return fig, "facing.png"


def knobs():
    """One sweep per animal, of the parameter that animal is about."""
    # Every sweep is a *vertical* stack, for two reasons: a mouse's tail runs
    # backwards far enough to reach into the next mouse in a row, and four
    # panels of equal-aspect axes only come out the same size on the page if
    # their contents have roughly the same aspect.
    sheets = [
        ("mouse · tail", [Mouse(tail=t, at=(0.0, -i * 0.88))
                          for i, t in enumerate((0.25, 0.78, 1.30))]),
        ("fly · wings", [Fly(wings=w, legs=lg, at=(0.0, -i * 0.80))
                         for i, (w, lg) in enumerate([(True, 3), (False, 3),
                                                      (False, 0)])]),
        ("fish · stripes", [Zebrafish(stripes=n, at=(0.0, -i * 0.52))
                            for i, n in enumerate((0, 3, 6))]),
        ("worm · curl", [Worm(curl=c, waves=w, at=(0.0, -i * 0.52))
                         for i, (c, w) in enumerate([(0.02, 0.4),
                                                     (0.10, 1.4),
                                                     (0.22, 2.2)])]),
    ]
    fig, axes = plt.subplots(1, len(sheets), figsize=(2.2 * len(sheets), 2.6),
                             dpi=150)
    for ax, (name, animals) in zip(axes, sheets, strict=True):
        _panel(ax, animals, pad=0.10, lw=0.95)
        ax.set_title(name, fontsize=9.5, color=TEXT)
    fig.tight_layout(pad=0.3)
    return fig, "knobs.png"


def to_scale():
    """The four at true relative size, and why `size` is a drawn size.

    A mouse is about 8 cm nose to rump, a zebrafish 4 cm, a fly 3 mm and
    *C. elegans* 1 mm. Drawn honestly, the worm is a hair beside the mouse —
    which is the right answer for a figure about scale and the wrong one for
    a figure that has to *name* four organisms. Hence `size`: a drawn size,
    set per animal, and true scale is one line when you want it.
    """
    real = (("Mouse", Mouse, 80.0), ("Zebrafish", Zebrafish, 40.0),
            ("Fly", Fly, 3.0), ("Worm", Worm, 1.0))
    fig, ax = bd.canvas(figsize=(7.0, 1.9))
    x = 0.0
    drawn = []
    for name, cls, mm in real:
        animal = cls(size=mm / 80.0, at=(x, 0.0))
        animal.draw(ax=ax, edge=INK, wall_lw=0.9)
        drawn.append(animal)
        ax.text(x, -0.34, f"{name}\n{mm:g} mm", ha="center", va="top",
                fontsize=8, color=TEXT)
        x += 1.25
    bd.fit(ax, [p for a in drawn for p in a.points], pad=0.12)
    ax.set_ylim(-0.62, ax.get_ylim()[1])
    return fig, "to_scale.png"


BUILDS = (portraits, blueprint, facing, knobs, to_scale)


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

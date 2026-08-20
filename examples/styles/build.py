"""Two drawing languages, and the settings inside each.

The distinction this page exists to make, because it was got wrong once:
**a colour and a linewidth are not a style.** Re-inking the same drawing gives
you the same drawing. There are two genuinely different ways to draw a cell
here, and everything else is a setting within one of them:

* **hollow** — every process is walled into a tube and the whole cell fuses
  into one unbroken contour. It says *this process has a width and a wall*.
* **skeleton** — the centrelines are stroked and there are no walls at all. It
  says *this process exists and connects these two places*, which is what a
  circuit diagram or a connectome figure actually claims, and it is the only
  one of the two that survives at small sizes, where two walls a fraction of a
  point apart merge into a smudge.

Journals and posters do not agree on which they want, and the same cell
appears as a hollow line drawing in a methods figure and a stroked skeleton in
the circuit panel two pages later.

    python tools/build_gallery.py styles
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

import biodraw as bd  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
PAL = bd.style.palette.get()
EXC, INH = PAL["primary"], PAL["secondary"]
# Annotation colour for the labels on these sheets — a caption is not a
# drawing, so it is not the identity palette's business.
TEXT = "#555555"


# Every style is a `draw` keyword set. `fill` is doing most of the work:
#
#   None      wash the interior with the cell's own ink — the default, and
#             what a line drawing wants
#   the ink   collapse the two-pass union into a solid silhouette
#   'white'   leave the paper showing through
#
# `alpha` fades by pre-blending onto the page rather than by transparency, so
# a faded cell still occludes what is behind it (see `render.blend`).
# One caution the grid makes obvious: on a **flat** fill `wall_lw` has nothing
# to contrast against, so it does not thicken a visible wall — it inflates the
# silhouette. The wall is stroked at twice the asked-for width and then the
# interior is repainted in the same colour, which on a hollow cell leaves a
# wall and on a solid one just makes the cell fatter, swallowing the spines.
# Keep a flat style near `wall_lw=1.0` and use `bold` when you want weight.
STYLES = {
    # -- the hollow language: walls, fused into one contour ----------------
    "hollow": dict(wall_lw=1.0),
    "outline": dict(wall_lw=1.0, fill="white"),
    "solid": dict(wall_lw=1.0, fill="__ink__"),
    "ghost": dict(wall_lw=0.8, alpha=0.35),
    "ink": dict(wall_lw=1.2, edge="#111111", fill="white"),
    # -- the other language: no walls at all -------------------------------
    "skeleton": dict(style="skeleton", wall_lw=0.9),
    "skeleton bold": dict(style="skeleton", wall_lw=1.9),
}


def _draw(ax, shape, ink, style):
    """Apply one named style. `'__ink__'` means *this shape's own colour*."""
    kw = dict(STYLES[style])
    edge = kw.pop("edge", ink)
    fill = kw.pop("fill", None)
    if fill == "__ink__":
        fill = edge
    if kw.get("style") == "skeleton":
        kw.pop("fill", None)
        return shape.draw(ax=ax, edge=edge, **kw)
    return shape.draw(ax=ax, edge=edge, fill=fill, **kw)


def _pyr(**kw):
    return bd.neuro.Pyramidal(spines=7, basal=2, basal_spines=3, **kw)


def styles():
    """Every style, on a cell simple enough to compare them on."""
    names = list(STYLES)
    fig, axes = plt.subplots(1, len(names), figsize=(1.25 * len(names), 2.6),
                             dpi=110)
    for ax, name in zip(axes, names, strict=True):
        bd.canvas(ax=ax)
        cell = _pyr()
        _draw(ax, cell, EXC, name)
        cell.fit(ax, pad=0.28)
        ax.set_title(name, fontsize=8.5, color=TEXT)
    fig.tight_layout(pad=0.3)
    return fig, "styles.png"


def both():
    """Both cell types under each style, so the pair is checked together.

    A style that separates a pyramidal cell from a basket cell in the default
    palette may stop separating them once both are flat, or ghosted, or
    reduced to one ink — which is exactly when a figure quietly starts
    depending on colour it no longer has.
    """
    names = list(STYLES)
    fig, axes = plt.subplots(2, len(names),
                             figsize=(1.25 * len(names), 4.6), dpi=110)
    for c, name in enumerate(names):
        for r, (shape, ink) in enumerate([(_pyr(), EXC),
                                          (bd.neuro.Basket(dendrites=6),
                                           INH)]):
            ax = axes[r, c]
            bd.canvas(ax=ax)
            _draw(ax, shape, ink, name)
            shape.fit(ax, pad=0.28)
        axes[0, c].set_title(name, fontsize=8.5, color=TEXT)
    fig.tight_layout(pad=0.3)
    return fig, "both.png"


def detail():
    """How much cell to draw — the other half of a house style.

    Spines and a forked apical are information. At the size a cell appears in
    a circuit panel they are noise, and the reader is counting cells rather
    than reading morphology.
    """
    variants = [
        (dict(spines=9, basal=2, basal_spines=5, apical_fork=0.55,
              fork_spines=4), "full"),
        (dict(spines=6, basal=2, basal_spines=3), "spiny"),
        (dict(spines=0, basal=2, basal_spines=0, apical_fork=0.52,
              fork_spines=0), "tufted"),
        (dict(spines=0, basal=2, basal_spines=0), "schematic"),
    ]
    fig, axes = plt.subplots(1, len(variants), figsize=(7.6, 3.0), dpi=110)
    for ax, (kw, label) in zip(axes, variants, strict=True):
        bd.canvas(ax=ax)
        cell = bd.neuro.Pyramidal(**kw)
        cell.draw(ax=ax, edge=EXC, wall_lw=1.0)
        cell.fit(ax, pad=0.28)
        ax.set_title(label, fontsize=9, color=TEXT)
    fig.tight_layout(pad=0.3)
    return fig, "detail.png"


def palettes():
    """Both cells in each bundled palette, flat and hollow.

    `mono` is the check that matters: a drawing that stops making sense there
    is leaning on colour to carry a claim, and will fail on a greyscale
    printout. The default is red and green, which is the pair around 8% of
    men cannot separate — so `colorblind` is one argument away.
    """
    names = bd.style.palette.available()
    fig, axes = plt.subplots(2, len(names), figsize=(2.3 * len(names), 4.6),
                             dpi=110)
    for c, pname in enumerate(names):
        p = bd.style.palette.get(pname)
        for r, solid in enumerate((False, True)):
            ax = axes[r, c]
            bd.canvas(ax=ax)
            pyr = _pyr()
            bas = bd.neuro.Basket(dendrites=6, at=(2.5, 0.3), scale=0.85)
            for shape, ink in ((pyr, p["primary"]), (bas, p["secondary"])):
                shape.draw(ax=ax, edge=ink, fill=ink if solid else None,
                           wall_lw=1.0)
            bd.fit(ax, pyr.points + bas.points, pad=0.3)
        axes[0, c].set_title(pname, fontsize=9, color=TEXT)
    fig.tight_layout(pad=0.3)
    return fig, "palettes.png"


BUILDS = (styles, both, detail, palettes)


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

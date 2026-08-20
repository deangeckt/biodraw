"""The dendritic spine: from a hand drawing to a placeable shape.

Builds every image this folder's gallery page shows:

    python examples/dendritic_spine/build.py

`blueprint.png` is the interesting one — the maths behind the shape, drawn by
matplotlib from the same `Profile` object that draws the spine itself. It is a
hand-written prototype of what `bd.explain()` will do for every shape in the
library.
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import biodraw as bd  # noqa: E402
from biodraw.core import profile, render  # noqa: E402
from biodraw.core.branch import Branch  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
PAL = bd.style.palette.get()
INK = PAL["primary"]
# Annotation colours for the construction figures. Local on purpose:
# these label a *diagram about* the drawing, not the drawing, so they
# are not the library's identity palette's business.
NECK = "#7C3AED"
HEAD = "#059669"
GREY = "#9AA0A6"

plt.rcParams.update({
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
})


def _framed(parts, height=4.0, pad=0.12):
    """A canvas shaped like the drawing that is going on it.

    `save_compact` trims to the *axes*, and the axes are equal-aspect, so a
    tall narrow drawing in a square figure keeps its white margins into the
    committed PNG. Measured on the old `branch.png`: the ink used 62% of the
    width. Shaping the figure like the data takes it over 90%, and the file
    gets smaller as well. See the frame report in `tools/build_gallery.py`.
    """
    xy = np.concatenate([np.asarray(part) for part in parts])
    w = float(np.ptp(xy[:, 0])) + 2 * pad
    h = float(np.ptp(xy[:, 1])) + 2 * pad
    return bd.canvas(figsize=(height * w / h, height))


def _hollow(ax, parts, color=INK, wall=1.4, gid=None, open_parts=()):
    return render.render_hollow(ax, parts,
                                render.resolve_fill(None, None, color),
                                color, wall, open_parts=list(open_parts),
                                gid=gid)


# ---------------------------------------------------------------------------
# blueprint.png — the four steps from traced points to placed shape
# ---------------------------------------------------------------------------

def blueprint():
    sp = profile.get("spine")
    p = sp.points
    lo, hi = sp.stretch

    fig, axes = plt.subplots(1, 4, figsize=(14.0, 3.6), dpi=150)

    # -- 1. the trace --------------------------------------------------------
    ax = axes[0]
    ax.fill(p[:, 0], p[:, 1], color=render.resolve_fill(None, None, INK),
            zorder=1)
    ax.plot(np.append(p[:, 0], p[0, 0]), np.append(p[:, 1], p[0, 1]),
            color=INK, lw=1.2, zorder=2)
    ax.scatter(p[:, 0], p[:, 1], s=7, color=INK, zorder=3)
    ax.plot([0, 0], [p[0, 1], p[-1, 1]], color=GREY, lw=1.0, ls="--", zorder=4)
    ax.annotate("base chord\n(sits inside the dendrite)", xy=(0.0, 0.0),
                xytext=(0.30, -0.62), ha="center", fontsize=8, color=GREY,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    ax.annotate("tip at x = 1", xy=(1.0, -0.045), xytext=(0.72, 0.62),
                ha="center", fontsize=8, color=GREY,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    ax.set_title("1 · traced, then normalised", fontsize=10, loc="left")
    ax.set_xlabel("x  (long axis, 0 → 1)")
    ax.set_ylabel("y  (across)")
    ax.set_aspect("equal")
    ax.set_xlim(-0.12, 1.12)
    ax.set_ylim(-0.72, 0.72)

    # -- 2. the maths --------------------------------------------------------
    # Split the closed outline into its two walls at the tip, and plot each as
    # a half-width against x. This is the panel that shows *why* the shape
    # reads as a spine: a flat neck, then an accelerating flare.
    ax = axes[1]
    k_tip = int(np.argmax(p[:, 0]))
    upper, lower = p[:k_tip + 1], p[k_tip:]
    ax.axvspan(lo, hi, color=NECK, alpha=0.10, lw=0)
    ax.plot(upper[:, 0], upper[:, 1], color=INK, lw=1.6)
    ax.plot(lower[:, 0], lower[:, 1], color=INK, lw=1.6, ls="--")
    ax.axhline(0.0, color=GREY, lw=0.6, ls=":")
    ax.axvline(sp.head_t, color=HEAD, lw=1.0, ls="--")
    # Walls labelled in place rather than in a legend — a key here would sit
    # on top of the very curve it is describing.
    ax.text(0.30, 0.20, "upper wall", fontsize=7.5, color=INK, ha="center")
    ax.text(0.30, -0.24, "lower wall", fontsize=7.5, color=INK, ha="center")
    ax.text(hi / 2, -0.66, "neck\nconstant width", ha="center", fontsize=8,
            color=NECK)
    ax.annotate("", xy=(0.57, 0.26), xytext=(0.50, 0.66),
                arrowprops=dict(arrowstyle="->", color=HEAD, lw=1.0))
    ax.text(0.48, 0.72, "concave flare", fontsize=8, color=HEAD, ha="center")
    ax.text(sp.head_t - 0.04, 0.84, f"head_t = {sp.head_t}", fontsize=8,
            color=HEAD, ha="right")
    ax.set_title("2 · the shape as a function", fontsize=10, loc="left")
    ax.set_xlabel("x")
    ax.set_ylabel("half-width")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.80, 1.00)

    # -- 3. the stretch ------------------------------------------------------
    # The map x -> x' that lengthens the neck without touching the head.
    ax = axes[2]
    x = np.linspace(0, 1, 400)
    for ext, alpha in ((0.0, 0.35), (0.25, 0.7), (0.60, 1.0)):
        ax.plot(x, sp._stretched_x(x, ext), color=NECK, lw=1.6, alpha=alpha,
                label=f"extend = {ext:g}")
    ax.axvspan(lo, hi, color=NECK, alpha=0.10, lw=0)
    ax.axvline(sp.head_t, color=HEAD, lw=1.0, ls="--")
    ax.text(hi / 2, 1.80, "only this span\nstretches", ha="center",
            fontsize=8, color=NECK)
    ax.text(0.99, 0.22, "beyond it the head\nrides out rigidly", fontsize=8,
            color=HEAD, ha="right", va="bottom")
    ax.set_title("3 · lengthen the neck, keep the head", fontsize=10,
                 loc="left")
    ax.set_xlabel("x  in")
    ax.set_ylabel("x′  out")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 2.05)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left",
              bbox_to_anchor=(0.40, 0.72))

    # -- 4. the result -------------------------------------------------------
    ax = axes[3]
    bd.canvas(ax=ax)
    exts = (0.0, 0.25, 0.60)
    parts = [sp.place((i * 0.62, 0.0), (0.0, 1.0), size=0.5, extend=e)
             for i, e in enumerate(exts)]
    _hollow(ax, parts, gid="spine")
    for i, ext in enumerate(exts):
        ax.text(i * 0.62, -0.22, f"{ext:g}", ha="center", fontsize=8,
                color=GREY)
    ax.text(0.62, -0.40, "extend", ha="center", fontsize=8, color=GREY)
    bd.fit(ax, parts, pad=0.08)
    ax.set_ylim(-0.50, ax.get_ylim()[1])
    ax.set_title("4 · placed — same head, three necks", fontsize=10,
                 loc="left")

    fig.tight_layout(w_pad=2.0)
    return fig, "blueprint.png"


# ---------------------------------------------------------------------------
# the plain deliverables
# ---------------------------------------------------------------------------

def one_spine():
    """The shape on its own."""
    fig, ax = bd.canvas(figsize=(1.8, 2.4))
    part = profile.get("spine").place((0, 0), (0, 1), size=1.0)
    _hollow(ax, [part], wall=2.0, gid="spine")
    bd.fit(ax, [part], pad=0.08)
    return fig, "spine.png"


# The named spine shapes, as settings of the one traced outline. These are
# the shapes every paper on spines names, and they are three numbers apart:
# how wide the head is, how thin the neck is, and how far it stands off.
# Nothing here is a second profile — see `Profile._width_scale`.
FORMS = (
    ("traced", dict(size=0.34)),
    ("thin", dict(size=0.34, head=0.72, neck=0.62, extend=0.16)),
    ("stubby", dict(size=0.22, head=0.92, neck=1.30)),
    # 1.45 read as a trumpet rather than a mushroom: the knob widens the
    # head without lengthening it, so past ~1.25 the flare flattens out.
    ("mushroom", dict(size=0.34, head=1.22, neck=0.55)),
    ("long-necked", dict(size=0.30, head=0.95, neck=0.70, extend=0.34)),
)


def forms():
    """The named spine shapes, and the traced one they all come from."""
    sp = profile.get("spine")
    step = 0.40
    parts = [sp.place((i * step, 0.0), (0.0, 1.0), **kw)
             for i, (_, kw) in enumerate(FORMS)]
    fig, ax = _framed(parts, height=2.6, pad=0.22)
    _hollow(ax, parts, wall=1.6, gid="spine")
    for i, (name, _) in enumerate(FORMS):
        ax.text(i * step, -0.10, name, ha="center", va="top", fontsize=8.5,
                color=GREY)
    bd.fit(ax, parts, pad=0.08)
    ax.set_ylim(-0.20, ax.get_ylim()[1])
    return fig, "forms.png"


def head_and_neck():
    """The two width knobs, swept against each other.

    A grid rather than two rows: what a reader is choosing between is a
    *combination* — a fat head on a thin neck is a mushroom spine, the same
    head on a fat neck is barely a spine at all — and a pair of one-knob rows
    cannot show that.
    """
    sp = profile.get("spine")
    heads = (0.70, 1.00, 1.30)
    necks = (0.60, 1.00, 1.40)
    dx, dy = 0.42, 0.54
    parts = []
    for r, neck in enumerate(necks):
        for _c, head in enumerate(heads):
            parts.append(sp.place((_c * dx, -r * dy), (0.0, 1.0), size=0.34,
                                  head=head, neck=neck))
    fig, ax = _framed(parts, height=3.4, pad=0.34)
    _hollow(ax, parts, wall=1.3, gid="grid")
    for c, head in enumerate(heads):
        ax.text(c * dx, 0.44, f"head {head:g}", ha="center", fontsize=8.5,
                color=GREY)
    for r, neck in enumerate(necks):
        ax.text(-0.28, -r * dy + 0.14, f"neck {neck:g}", ha="right",
                fontsize=8.5, color=GREY)
    bd.fit(ax, parts, pad=0.12)
    ax.set_xlim(-0.52, ax.get_xlim()[1])
    ax.set_ylim(ax.get_ylim()[0], 0.56)
    return fig, "head_neck.png"


def on_a_branch():
    """The same dendrite carrying three of the spine shapes.

    Was one dendrite in a frame two-thirds paper — *"the 'on a branch' eight
    image is almost only white space"*. Three of them, at the shapes above,
    is the same width of page carrying three times the drawing, and it says
    what a single one could not: the head and neck knobs survive being
    stamped along a branch, and the wall still fuses into one contour.
    """
    kinds = (("thin", dict(head=0.72, neck=0.62, extend=0.12)),
             ("traced", dict(extend=0.04)),
             ("mushroom", dict(head=1.22, neck=0.55, extend=0.04)))
    per, groups = 0.95, []
    for i, (_, kw) in enumerate(kinds):
        br = Branch((i * per, 0.0), (0.0, 1.0), length=1.8, bend=0.10)
        br.decorate("spine", n=8, size=0.21, first_t=0.30, last_t=0.86, **kw)
        groups.append(br.parts(width=0.11, taper=0.72, base_ext=0.05))
    everything = [part for closed, open_ in groups for part in closed + open_]

    fig, ax = _framed(everything, height=4.0, pad=0.20)
    # One `render_hollow` per branch: unioning all three would fuse any two
    # that touched into one impossible dendrite.
    for (closed, open_), (name, _) in zip(groups, kinds, strict=True):
        _hollow(ax, closed, wall=1.0, gid=name, open_parts=open_)
    for i, (name, _) in enumerate(kinds):
        ax.text(i * per, -0.16, name, ha="center", va="top", fontsize=8.5,
                color=GREY)
    bd.fit(ax, everything, pad=0.10)
    ax.set_ylim(-0.40, ax.get_ylim()[1])
    return fig, "branch.png"


def density():
    """The same branch at three spine densities."""
    fig, axes = plt.subplots(1, 3, figsize=(6.6, 4.2), dpi=150)
    for ax, n in zip(axes, (3, 8, 14), strict=True):
        bd.canvas(ax=ax)
        br = Branch((0.0, 0.0), (0.0, 1.0), length=1.8, bend=0.10)
        br.decorate("spine", n=n, size=0.19, extend=0.05, first_t=0.22,
                    last_t=0.90)
        closed, open_ = br.parts(width=0.11, taper=0.72, base_ext=0.05)
        _hollow(ax, closed, wall=1.0, gid=f"n{n}", open_parts=open_)
        bd.fit(ax, closed + open_, pad=0.14)
        ax.set_title(f"n = {n}", fontsize=9)
    fig.tight_layout()
    return fig, "density.png"


# Palettes used to be here too, on a page about one shape. They are a
# property of every drawing rather than of this one, so they live on the
# standalone styles page now — one place, all of them.
BUILDS = (blueprint, one_spine, forms, head_and_neck, on_a_branch, density)


def main():
    for build in BUILDS:
        fig, name = build()
        # Compact raster for anything the gallery shows — see
        # `biodraw.io.save_compact`, and the weight budget in docs/PLAN.md.
        bd.save_compact(fig, HERE / name)
        plt.close(fig)
        size = (HERE / name).stat().st_size / 1024
        print(f"wrote {(HERE / name).relative_to(HERE.parent.parent)} "
              f"({size:.0f} KB)")
    # ...and one true vector deliverable, which is what you would actually
    # drop into a paper.
    fig, _ = one_spine()
    bd.save(fig, HERE / "spine.svg")
    plt.close(fig)
    print("wrote", (HERE / "spine.svg").relative_to(HERE.parent.parent))


if __name__ == "__main__":
    main()

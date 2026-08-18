"""The dendritic spine: from a hand drawing to a placeable shape.

Builds every image in this folder's README:

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
INK = PAL["excitatory"]
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


def stretch_series():
    """One profile, one size, three neck extensions."""
    fig, ax = bd.canvas(figsize=(4.4, 2.6))
    sp = profile.get("spine")
    parts = [sp.place((i * 0.42, 0.0), (0.0, 1.0), size=0.3, extend=e)
             for i, e in enumerate((0.0, 0.10, 0.25))]
    _hollow(ax, parts, wall=1.6, gid="spine")
    bd.fit(ax, parts, pad=0.08)
    return fig, "stretch.png"


def on_a_branch():
    """Stamped along a curved branch, alternating, fused into one wall."""
    fig, ax = bd.canvas(figsize=(2.8, 4.4))
    br = Branch((0.0, 0.0), (0.0, 1.0), length=1.8, bend=0.10)
    br.decorate("spine", n=8, size=0.21, extend=0.04, first_t=0.30,
                last_t=0.86)
    closed, open_ = br.parts(width=0.11, taper=0.72, base_ext=0.05)
    _hollow(ax, closed, wall=1.0, gid="branch", open_parts=open_)
    bd.fit(ax, closed + open_, pad=0.12)
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


def palettes():
    """The same branch in each bundled palette."""
    names = bd.style.palette.available()
    fig, axes = plt.subplots(1, len(names), figsize=(2.0 * len(names), 3.4),
                             dpi=150)
    for ax, name in zip(axes, names, strict=True):
        bd.canvas(ax=ax)
        br = Branch((0.0, 0.0), (0.0, 1.0), length=1.6, bend=0.08)
        br.decorate("spine", n=6, size=0.2, extend=0.04)
        closed, open_ = br.parts(width=0.11, taper=0.72, base_ext=0.05)
        _hollow(ax, closed, color=bd.style.palette.get(name)["excitatory"],
                wall=1.0, gid=name, open_parts=open_)
        bd.fit(ax, closed + open_, pad=0.15)
        ax.set_title(name, fontsize=9)
    fig.tight_layout()
    return fig, "palettes.png"


BUILDS = (blueprint, one_spine, stretch_series, on_a_branch, density,
          palettes)


def main():
    for build in BUILDS:
        fig, name = build()
        # Compact raster for anything in a README — see
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

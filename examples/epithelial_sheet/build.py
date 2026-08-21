"""The epithelium: a row of cells that must not become one cell.

    python tools/build_gallery.py epithelial
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import biodraw as bd  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
PAL = bd.style.palette.get()
INK = PAL["ink"]
NUC = PAL["secondary"]
JOIN = PAL["primary"]
# Annotation colour for the construction figure, local on purpose.
# Annotation colours for the construction figures. Local on purpose:
# these label a *diagram about* the drawing, not the drawing, so they
# are not the library's identity palette's business.
APICAL_C = "#059669"
GREY = "#9AA0A6"
# *"this 'grey' default color ... is shouting claude"*. Measured at the time:
# 27 of the 79 committed images had no saturated ink in them at all, and
# every one of those was in a non-neuroscience folder — the newer domains
# fetched the palette for `ink` and `neutral` and never reached for an
# identity hue.
#
# The fix is not a second hue per part: `Blob.WASH` deliberately inks the
# nucleus as *more of the same ink* rather than a different colour, because a
# nucleus is a denser part of the cell and not a different kind of thing.
# Passing `edge=` a hue keeps that intact — every wash inherits it — so the
# drawing gains colour without gaining a claim.
SUBJECT = PAL["tertiary"]

plt.rcParams.update({
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
})


def _sheet(**kw):
    return bd.cells.Sheet(**{"cells": 6, "microvilli": 5, "seed": 1, **kw})


# ---------------------------------------------------------------------------
# the deliverables
# ---------------------------------------------------------------------------

def portrait():
    """A columnar epithelium with a brush border, on its membrane."""
    fig, ax = bd.canvas(figsize=(4.4, 2.6))
    sheet = _sheet()
    sheet.draw(ax=ax, edge=SUBJECT, wall_lw=1.0, gid="epithelium")
    sheet.fit(ax, pad=0.10)
    return fig, "epithelium.png"


def curvature():
    """The knob that turns a sheet into a villus, a duct or an acinus.

    Negative curls the apical surface inward, so the cells enclose a lumen;
    at a full turn the ring closes on itself exactly, whatever the count.
    """
    # Nine cells at this height so the closed ring is actually reachable: the
    # radius follows from the pitch, and a row of seven cannot enclose a wall
    # 0.62 high — `Sheet` refuses rather than drawing itself inside out.
    fig, _ = bd.contact_sheet(
        factory=bd.cells.Sheet,
        variants=[
            dict(cells=9, curve_deg=d, microvilli=4, height=0.36, seed=1)
            for d in (0, 60, 140, -60, -140, -360)],
        labels=["flat", "60° — a fold", "140° — a villus",
                "-60°", "-140° — a duct", "-360° — closed"],
        cols=3, cell_in=1.9, aspect=0.95, pad=0.10,
        draw_kw=dict(edge=SUBJECT),
    )
    return fig, "curvature.png"


def cell_shapes():
    """Squamous, cuboidal, columnar — the same object, three heights — and
    what the taper does to each."""
    heights, tapers = (0.34, 0.70, 1.25), (0.72, 1.0, 1.28)
    variants = [dict(cells=6, height=h, taper=t, microvilli=0, seed=1,
                     nucleus=0.26)
                for h in heights for t in tapers]
    fig, _ = bd.contact_sheet(
        factory=bd.cells.Sheet, variants=variants, cols=3, cell_in=1.9,
        aspect=0.8, pad=0.08,
        row_labels=["squamous", "cuboidal", "columnar"],
        col_labels=[f"taper {t:g}" for t in tapers],
        draw_kw=dict(edge=SUBJECT),
    )
    return fig, "cell_shapes.png"


def borders():
    """How much brush border, and how coarse."""
    counts = (0, 3, 6, 10)
    variants = [dict(cells=5, microvilli=n, height=0.85,
                     microvilli_len=length, microvilli_width=0.55 / max(n, 4),
                     seed=1)
                for length in (0.20, 0.40)
                for n in counts]
    fig, _ = bd.contact_sheet(
        factory=bd.cells.Sheet, variants=variants, cols=4, cell_in=1.7,
        aspect=0.85, pad=0.08,
        row_labels=["short", "long"],
        col_labels=[f"{n} per cell" for n in counts],
        draw_kw=dict(edge=SUBJECT),
    )
    return fig, "borders.png"


# ---------------------------------------------------------------------------
# blueprint.png
# ---------------------------------------------------------------------------

def blueprint():
    sheet = _sheet(cells=5)
    g = sheet.geometry
    fig, axes = plt.subplots(1, 4, figsize=(14.5, 3.6), dpi=150)

    # -- 1. one call versus one call per cell --------------------------------
    ax = axes[0]
    outlines = [c["outline"] for c in g["cells"]]
    # Everything in one call: the union dissolves every shared wall.
    bd.core.render.render_hollow(
        ax, outlines, fill=bd.core.render.resolve_fill(None, None, INK),
        edge=INK, wall_lw=1.1, gid="fused")
    ax.text(0.0, 1.28, "one render_hollow call — five cells become one",
            fontsize=8, color=GREY, ha="center")
    # And below it, the same outlines a layer each.
    lowered = sheet.moved(at=(0.0, -1.55))
    lowered.draw(ax=ax, edge=SUBJECT, wall_lw=1.1, gid="layered")
    ax.text(0.0, -1.85, "a Layer each — the walls survive", fontsize=8,
            color=JOIN, ha="center")
    bd.fit(ax, outlines + lowered.points, pad=0.16)
    ax.set_title("1 · why every cell is its own layer", fontsize=10,
                 loc="left")

    # -- 2. the gap ----------------------------------------------------------
    ax = axes[1]
    for c in g["cells"][:2]:
        v = c["outline"].vertices
        ax.fill(v[:, 0], v[:, 1], color=INK, alpha=0.10, zorder=2)
        ax.plot(v[:, 0], v[:, 1], color=INK, lw=1.4, zorder=3)
    left, right = g["cells"][0], g["cells"][1]
    boundary = 0.5 * (left["origin"][0] + right["origin"][0])
    ax.axvline(boundary, color=GREY, lw=0.8, ls=":", zorder=1)
    gap = sheet.gap * sheet.cell_w
    ax.annotate("", xy=(boundary - gap / 2, 0.52), xytext=(boundary + gap / 2,
                                                           0.52),
                arrowprops=dict(arrowstyle="<->", color=JOIN, lw=1.0))
    ax.text(boundary, 0.62, f"gap = {gap:.3f}", fontsize=8, color=JOIN,
            ha="center")
    ax.text(boundary, 0.20,
            "at gap=0 the two walls land on\nthe same line and each cell's\n"
            "fill erases half of the other's",
            fontsize=7.5, color=GREY, ha="center", va="top")
    ax.set_title("2 · the hairline between neighbours", fontsize=10,
                 loc="left")
    ax.set_aspect("equal")
    ax.set_xlim(left["origin"][0] - 0.34, right["origin"][0] + 0.34)
    ax.set_ylim(-0.12, 0.95)
    ax.axis("off")

    # -- 3. the arc ----------------------------------------------------------
    ax = axes[2]
    bent = bd.cells.Sheet(cells=7, curve_deg=150.0, height=0.55,
                          microvilli=0, seed=1)
    bent.draw(ax=ax, edge=SUBJECT, wall_lw=0.9, fill="white", gid="arc")
    theta, r, centre = bent.arc
    ax.scatter(*centre, s=30, color=JOIN, zorder=6)
    for c in bent.geometry["cells"][::3]:
        ax.plot([centre[0], c["origin"][0]], [centre[1], c["origin"][1]],
                color=JOIN, lw=0.7, ls=":", zorder=5)
    phis = np.linspace(-abs(theta) * 3.5, abs(theta) * 3.5, 80)
    for radius, color, ls in ((r, GREY, "--"),
                              (r + bent.height, APICAL_C, "--")):
        arc = centre + radius * np.column_stack([np.sin(phis), np.cos(phis)])
        ax.plot(arc[:, 0], arc[:, 1], color=color, lw=0.8, ls=ls, zorder=4)
    ax.text(centre[0], centre[1] - 0.10,
            f"centre; r = {r:.2f} from the pitch", fontsize=7.5, color=JOIN,
            ha="center", va="top")
    ax.text(0.0, r + bent.height + 0.30 - abs(centre[1]) * 0 + centre[1],
            "each cell widens by (r+h)/r,\nso the gap stays even to the top",
            fontsize=7.5, color=APICAL_C, ha="center")
    bd.fit(ax, bent.points + [np.array([centre])], pad=0.18)
    ax.set_title("3 · the arc, derived from the pitch", fontsize=10,
                 loc="left")

    # -- 4. anchors ----------------------------------------------------------
    ax = axes[3]
    bd.canvas(ax=ax)
    sheet.draw(ax=ax, edge=SUBJECT, wall_lw=0.7, fill="white",
               gid="anchors")
    colors = {"apical": APICAL_C, "basal": GREY, "nucleus": NUC,
              "junction": JOIN}
    for kind, color in colors.items():
        found = sheet.anchors(kind)
        if not found:
            continue
        p = found.points()
        n = np.array([a.normal for a in found])
        ax.quiver(p[:, 0], p[:, 1], n[:, 0], n[:, 1], color=color,
                  scale=12, width=0.006, zorder=7)
        ax.scatter(p[:, 0], p[:, 1], s=13, color=color, zorder=8,
                   label=f"{kind} ({len(found)})")
    sheet.fit(ax, pad=0.30)
    ax.legend(fontsize=7.5, frameon=False, loc="lower center", ncol=2)
    ax.set_title("4 · anchors", fontsize=10, loc="left")

    fig.tight_layout(w_pad=1.4)
    return fig, "blueprint.png"


BUILDS = (blueprint, portrait, curvature, cell_shapes, borders)


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

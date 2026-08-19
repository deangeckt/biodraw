"""Bacteria: a capsule body, and what is hung off it.

    python tools/build_gallery.py bacteria

The third domain, and the first whose body is a tube rather than a ring. The
figures below are organised around the one design decision worth arguing
about: the named forms are *settings*, not classes, so the space between a
bacillus and a vibrio is drawable too.
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import biodraw as bd  # noqa: E402
from biodraw.core.paths import tube  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
PAL = bd.style.palette.get()
INK = PAL["ink"]
GREY = PAL["neutral"]
# Annotation colours for the construction figure. Local on purpose: these
# label a diagram *about* the drawing, not the drawing.
MARK_A, MARK_B, MARK_C = "#7C3AED", "#059669", "#D97706"

plt.rcParams.update({
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
})


# The named forms, as settings. Read each as a diff against the default rod —
# what is not named is left alone, so the keywords that appear are the whole
# of what makes that form that form.
NAMED = [
    ("coccus", dict(length=0.0, width=0.62)),
    ("bacillus", dict(length=1.40)),
    ("vibrio", dict(length=1.40, curve_deg=72.0)),
    ("spirillum", dict(length=2.20, twists=1.8, twist_amp=0.62)),
    ("spirochaete", dict(length=2.60, width=0.20, twists=4.2,
                         twist_amp=1.60)),
    ("coryneform", dict(length=1.10, width=0.44, taper=0.58,
                        curve_deg=22.0)),
]


def _cell(**kw):
    return bd.micro.Bacterium(**{"seed": 3, **kw})


# ---------------------------------------------------------------------------
# the deliverables
# ---------------------------------------------------------------------------

def portrait():
    """One cell with everything turned on."""
    fig, ax = bd.canvas(figsize=(4.6, 2.6))
    cell = _cell(length=1.50, capsule=0.16, nucleoid=0.62, granules=4,
                 flagella=7, flagella_arc_deg=360.0, pili=16)
    cell.draw(ax=ax, wall_lw=1.0, gid="bacterium")
    cell.fit(ax, pad=0.10)
    return fig, "bacterium.png"


def named():
    """Six forms a reader can name, all of them settings of three knobs."""
    fig, _ = bd.contact_sheet(
        factory=bd.micro.Bacterium,
        variants=[dict(seed=3, **kw) for _, kw in NAMED],
        labels=[name for name, _ in NAMED],
        cols=3, cell_in=1.9, aspect=0.72, pad=0.10,
    )
    return fig, "named.png"


def forms():
    """The space between the named forms, which is the reason they are knobs.

    Length across, and the axis's own shape down. Nothing here is a mode: a
    curved rod with a twist in it is as reachable as either on its own.
    """
    axes = [("straight", dict(curve_deg=0.0, twists=0.0)),
            ("curve 45°", dict(curve_deg=45.0, twists=0.0)),
            ("curve 90°", dict(curve_deg=90.0, twists=0.0)),
            ("twists 1.5", dict(curve_deg=0.0, twists=1.5)),
            ("both", dict(curve_deg=45.0, twists=1.5))]
    lengths = (0.40, 0.90, 1.50, 2.20)
    fig, _ = bd.contact_sheet(
        factory=bd.micro.Bacterium,
        variants=[dict(seed=3, length=ln, **kw)
                  for _, kw in axes for ln in lengths],
        cols=len(lengths), cell_in=1.35, aspect=0.80, pad=0.10,
        row_labels=[name for name, _ in axes],
        col_labels=[f"length={ln:g}" for ln in lengths],
    )
    return fig, "forms.png"


def flagella():
    """The four textbook arrangements, as two numbers each.

    `flagella_arc_deg` is a sweep of the outline with 0° at one pole and 180°
    at the other, which is `Blob`'s protrusion vocabulary reused exactly. That
    reuse is the point: a reader who has met one shape already knows this one.
    """
    kinds = [
        ("monotrichous", dict(flagella=1, flagella_arc_deg=0.0)),
        ("amphitrichous", dict(flagella=2, flagella_arc_deg=360.0)),
        ("lophotrichous", dict(flagella=4, flagella_arc_deg=74.0,
                               flagella_start_deg=-37.0)),
        ("peritrichous", dict(flagella=9, flagella_arc_deg=360.0)),
    ]
    fig, _ = bd.contact_sheet(
        factory=bd.micro.Bacterium,
        variants=[dict(seed=5, length=1.30, **kw) for _, kw in kinds],
        labels=[name for name, _ in kinds],
        cols=4, cell_in=1.9, aspect=0.80, pad=0.08,
    )
    return fig, "flagella.png"


def envelope():
    """What goes outside the wall, and what goes inside it."""
    variants = [
        ("plain", {}),
        ("capsule", dict(capsule=0.20)),
        ("nucleoid", dict(nucleoid=0.66)),
        ("granules", dict(granules=5)),
        ("pili", dict(pili=20)),
        ("all of it", dict(capsule=0.20, nucleoid=0.66, granules=5, pili=20)),
    ]
    fig, _ = bd.contact_sheet(
        factory=bd.micro.Bacterium,
        variants=[dict(seed=2, length=1.40, **kw) for _, kw in variants],
        labels=[name for name, _ in variants],
        cols=6, cell_in=1.45, aspect=0.86, pad=0.10,
    )
    return fig, "envelope.png"


# ---------------------------------------------------------------------------
# colony.png — arrangement is composition, not a keyword
# ---------------------------------------------------------------------------
#
# A diplococcus is two cocci. There is deliberately no `arrangement=` knob:
# placing cells relative to each other is `moved()`, which every shape in this
# library already has, and a colony keyword would be one paper's idea of a
# colony living inside a general drawing library. Same argument that removed
# the contact-placement engine — see docs/STATE.md.

def _diplo(r):
    return [(0.0, 0.0, 0.0), (2.05 * r, 0.0, 0.0)]


def _strepto(r, n=5):
    # A chain that is dead straight reads as printed, so it sags — one arc,
    # seeded nowhere because a fixed curve is a drawing decision, not noise.
    out = []
    for k in range(n):
        t = k / (n - 1) - 0.5
        out.append((2.02 * r * k, -1.5 * r * t * t, 0.0))
    return out


def _staphylo(r, seed=4):
    # A cluster, and close-packed is what a cluster of cocci actually is — so
    # the slots are a hexagon at 2.3 radii and the irregularity comes from
    # the jitter, seeded so the bunch regenerates byte-identically.
    #
    # 2.3 is not a look, it is a clearance. Two cocci of radius r overlap
    # below 2r, and the jitter can take 0.16 r out of any gap, so anything
    # under ~2.2 draws cells through each other. The first version of this
    # figure used slots written as if they were in diameters and produced
    # eleven overlapping pairs out of twenty-one.
    rng = np.random.default_rng(seed)
    s, h = 2.30, 2.30 * np.sqrt(3.0) / 2.0
    slots = [(0.0, 0.0), (s, 0.0), (0.5 * s, h), (-0.5 * s, h),
             (1.5 * s, h), (0.5 * s, -h), (1.5 * s, -h)]
    return [(r * (x + rng.uniform(-0.08, 0.08)),
             r * (y + rng.uniform(-0.08, 0.08)), 0.0) for x, y in slots]


def _palisade(hw, n=4):
    # Rods standing side by side, so they are turned across the row: a
    # palisade is cells shoulder to shoulder, and offsetting them along their
    # own long axis instead puts them end to end and straight through each
    # other. Each leans a little differently — a row of exactly parallel
    # cells is the same failure as a perfectly level apical surface.
    rng = np.random.default_rng(7)
    return [(2.6 * hw * k, 0.0, 90.0 + float(rng.uniform(-7.0, 7.0)))
            for k in range(n)]


def colony():
    """Four arrangements, each of them `moved()` and nothing else."""
    groups = [
        ("diplococcus", dict(length=0.0, width=0.54), _diplo(0.27)),
        ("streptococcus", dict(length=0.0, width=0.46), _strepto(0.23)),
        ("staphylococcus", dict(length=0.0, width=0.44), _staphylo(0.22)),
        ("palisade", dict(length=1.05, width=0.34), _palisade(0.17)),
    ]
    fig, axes = plt.subplots(1, len(groups), figsize=(9.6, 2.9), dpi=150)
    for ax, (name, kw, places) in zip(axes, groups, strict=True):
        bd.canvas(ax=ax)
        cells = [_cell(**kw).moved(at=(x, y), rotate_deg=rot)
                 for x, y, rot in places]
        for i, cell in enumerate(cells):
            cell.draw(ax=ax, wall_lw=0.9, gid=f"{name}.{i}")
        bd.fit(ax, [p for cell in cells for p in cell.points], pad=0.10)
        ax.set_title(f"{name}\n{len(cells)} cells, one `moved()` each",
                     fontsize=8, color=GREY)
    fig.tight_layout(w_pad=1.0)
    return fig, "colony.png"


# ---------------------------------------------------------------------------
# blueprint.png
# ---------------------------------------------------------------------------

def blueprint():
    cell = _cell(length=1.50, curve_deg=30.0, twists=0.9, flagella=5,
                 flagella_arc_deg=360.0, nucleoid=0.62, granules=3)
    g = cell.geometry
    fig, axes = plt.subplots(1, 4, figsize=(14.0, 3.6), dpi=150)

    # -- 1. the three body knobs compose ------------------------------------
    ax = axes[0]
    stages = [
        ("straight", dict(length=1.50)),
        ("+ curve_deg=30", dict(length=1.50, curve_deg=30.0)),
        ("+ twists=0.9", dict(length=1.50, curve_deg=30.0, twists=0.9)),
    ]
    for i, (label, kw) in enumerate(stages):
        c = _cell(**kw)._centreline()
        shift = np.array([0.0, -0.62 * i])
        v = c + shift
        ax.plot(v[:, 0], v[:, 1], color=[MARK_A, MARK_B, MARK_C][i], lw=1.6)
        ax.text(v[0, 0] - 0.12, v[0, 1], label, fontsize=7.5, ha="right",
                va="center", color=[MARK_A, MARK_B, MARK_C][i])
    ax.text(0.0, -2.05, "one centreline, three terms —\n"
                        "a bend and a wave, not three modes",
            fontsize=8, color=GREY, ha="center")
    ax.set_title("1 · the axis", fontsize=10, loc="left")
    ax.set_aspect("equal")
    ax.axis("off")

    # -- 2. why the base is capped ------------------------------------------
    ax = axes[1]
    c, w = g["centre"], g["widths"]
    open_ring = tube(c, w, cap_base=False) + np.array([0.0, 0.52])
    shut_ring = np.asarray(g["outline"]) + np.array([0.0, -0.52])
    for ring, color, label in ((open_ring, MARK_C, "cap_base=False — a cut"),
                              (shut_ring, MARK_B, "cap_base=True — a cell")):
        ax.fill(ring[:, 0], ring[:, 1], color=color, alpha=0.14, zorder=2)
        ax.plot(ring[:, 0], ring[:, 1], color=color, lw=1.4, zorder=3)
        ax.text(ring[:, 0].min() - 0.10, ring[:, 1].mean(), label, fontsize=8,
                color=color, ha="right", va="center")
    ax.annotate("a flat chord reads as\na specimen that was sectioned",
                xy=(open_ring[:, 0].min() + 0.02, 0.52),
                xytext=(0.35, 1.30), fontsize=8, color=MARK_C, ha="center",
                arrowprops=dict(arrowstyle="->", color=MARK_C, lw=0.8))
    ax.set_title("2 · both ends, or it is not a cell", fontsize=10,
                 loc="left")
    ax.set_aspect("equal")
    ax.axis("off")

    # -- 3. where an appendage leaves ---------------------------------------
    ax = axes[2]
    ring = np.asarray(g["outline"])
    mid = c.mean(axis=0)
    ax.fill(ring[:, 0], ring[:, 1], color="#F2F2F2", zorder=1)
    ax.plot(ring[:, 0], ring[:, 1], color=GREY, lw=1.2, zorder=2)
    for deg in (0, 90, 180, 270):
        xy, n = cell.wall_at(deg)
        ax.plot([mid[0], xy[0]], [mid[1], xy[1]], color=MARK_A, lw=0.7,
                ls=":", zorder=3)
        ax.scatter(*xy, s=22, color=MARK_A, zorder=5)
        ax.quiver(xy[0], xy[1], n[0], n[1], color=MARK_A, scale=9,
                  width=0.008, zorder=5)
        ax.text(xy[0] + n[0] * 0.20, xy[1] + n[1] * 0.20, f"{deg}°",
                fontsize=7.5, color=MARK_A, ha="center", va="center")
    ax.text(mid[0], ring[:, 1].min() - 0.34,
            "0° is one pole, 180° the other —\n"
            "resolved against the outline as drawn",
            fontsize=8, color=GREY, ha="center")
    ax.set_title("3 · flagella_arc_deg", fontsize=10, loc="left")
    ax.set_aspect("equal")
    ax.axis("off")

    # -- 4. anchors ----------------------------------------------------------
    ax = axes[3]
    bd.canvas(ax=ax)
    cell.draw(ax=ax, wall_lw=0.7, fill="white", gid="anchors")
    for kind, color in (("pole", MARK_C), ("wall", MARK_B),
                        ("flagellum", MARK_A)):
        found = cell.anchors(kind)
        if not found:
            continue
        p = found.points()
        n = np.array([a.normal for a in found])
        ax.quiver(p[:, 0], p[:, 1], n[:, 0], n[:, 1], color=color, scale=13,
                  width=0.006, zorder=7)
        ax.scatter(p[:, 0], p[:, 1], s=13, color=color, zorder=8,
                   label=f"{kind} ({len(found)})")
    cell.fit(ax, pad=0.20)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.set_title("4 · anchors", fontsize=10, loc="left")

    fig.tight_layout(w_pad=1.4)
    return fig, "blueprint.png"


BUILDS = (blueprint, portrait, named, forms, flagella, envelope, colony)


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

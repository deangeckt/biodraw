"""The pyramidal cell: soma, apical, basals — one unbroken outline.

    python tools/build_gallery.py pyramidal
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import biodraw as bd  # noqa: E402
from biodraw.core.paths import neck_polygon  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
PAL = bd.style.palette.get()
INK = PAL["excitatory"]
SOMA_C = PAL["inhibitory"]
# Annotation colours for the construction figures. Local on purpose:
# these label a *diagram about* the drawing, not the drawing, so they
# are not the library's identity palette's business.
MARK_A, MARK_B = "#7C3AED", "#059669"
SPINE_C, SHAFT_C = MARK_A, MARK_B
GREY = "#9AA0A6"

plt.rcParams.update({
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
})


def _cell(**kw):
    return bd.neuro.Pyramidal(spines=8, basal=2, basal_spines=5, **kw)


# ---------------------------------------------------------------------------
# the deliverables
# ---------------------------------------------------------------------------

def portrait():
    """The cell on its own."""
    fig, ax = bd.canvas(figsize=(3.0, 4.2))
    cell = _cell()
    cell.draw(ax=ax, wall_lw=1.0, gid="pyramidal")
    cell.fit(ax, pad=0.2)
    return fig, "pyramidal.png"


def spininess():
    """One knob, six settings."""
    fig, _ = bd.contact_sheet(
        factory=bd.neuro.Pyramidal,
        variants=[dict(spines=n, basal=2, basal_spines=max(1, n // 2))
                  for n in (0, 3, 6, 9, 12, 16)],
        labels="auto", cols=6, cell_in=1.15,
    )
    return fig, "spininess.png"


def body_plans():
    """The shape space: how many basals, how wide, and whether the apical
    forks. Cheap to show all of it — see the note on cost in the README."""
    basals, angles = (0, 1, 2), (25, 40, 55)
    variants = [
        dict(spines=0 if fork else 7, apical_fork=fork, fork_spines=4,
             basal=basal, basal_angle_deg=angle, basal_spines=3)
        for fork in (None, 0.42)
        for basal in basals
        for angle in angles
    ]
    fig, _ = bd.contact_sheet(
        factory=bd.neuro.Pyramidal, variants=variants, cols=9, cell_in=1.05,
        # A grid sweep wants headers, not a caption under every cell — three
        # keys repeated eighteen times is the same text written eighteen
        # times, and it crowds out the drawings.
        row_labels=["apical straight", "apical forked"],
        col_labels=[f"basal={b}\n{a}°" for b in basals for a in angles],
    )
    return fig, "body_plans.png"


def forks():
    """Where the apical splits, and how wide."""
    forks_at, angles = (0.25, 0.45, 0.65), (15, 32, 50)
    variants = [dict(spines=0, apical_fork=f, fork_angle_deg=a, fork_spines=3,
                     basal=2, basal_spines=3)
                for f in forks_at for a in angles]
    fig, _ = bd.contact_sheet(
        factory=bd.neuro.Pyramidal, variants=variants, cols=3, cell_in=1.5,
        row_labels=[f"fork at {f:g}" for f in forks_at],
        col_labels=[f"{a}°" for a in angles],
    )
    return fig, "forks.png"


# ---------------------------------------------------------------------------
# blueprint.png
# ---------------------------------------------------------------------------

def blueprint():
    cell = _cell()
    g = cell.geometry
    fig, axes = plt.subplots(1, 4, figsize=(14.0, 4.2), dpi=150)

    # -- 1. the skeleton -----------------------------------------------------
    ax = axes[0]
    tri = np.array([g["apex"], g["base_l"], g["base_r"], g["apex"]])
    ax.plot(tri[:, 0], tri[:, 1], color=GREY, lw=1.0, ls="--")
    ax.scatter(tri[:3, 0], tri[:3, 1], s=22, color=GREY, zorder=4)
    for _, br, _ in cell._branches():
        ax.plot(br.centre[:, 0], br.centre[:, 1], color=INK, lw=1.4)
        bases = np.array([d["base"] for d in br.decorations])
        heads = np.array([d["head"] for d in br.decorations])
        ax.scatter(bases[:, 0], bases[:, 1], s=12, color=SPINE_C, zorder=5)
        for b, h in zip(bases, heads, strict=True):
            ax.plot([b[0], h[0]], [b[1], h[1]], color=SPINE_C, lw=0.8,
                    alpha=0.7)
    ax.text(g["apex"][0] + 0.08, g["apex"][1] + 0.12, "apex", fontsize=8,
            color=GREY)
    ax.text(g["base_l"][0] - 0.05, g["base_l"][1] - 0.22, "base corners",
            fontsize=8, color=GREY)
    ax.text(0.30, 1.55, "each dendrite\nis a Branch", fontsize=8, color=INK)
    ax.text(0.62, 0.75, "spine bases → heads", fontsize=8, color=SPINE_C)
    ax.set_title("1 · the skeleton", fontsize=10, loc="left")
    ax.set_aspect("equal")
    ax.axis("off")

    # -- 2. the neck ---------------------------------------------------------
    # Why the apex is not simply cut flat.
    ax = axes[1]
    path, pts = neck_polygon(
        g["apex"], g["base_l"], g["base_r"], hw=cell.half_width,
        neck_r=cell.soma_neck_r, corner_r=cell.soma_round,
        bow_bottom=cell.soma_bow_bottom, bow_side=cell.soma_bow_side)
    v = path.vertices
    hw = cell.half_width
    ax.fill(v[:, 0], v[:, 1], color="#FFE3E3", zorder=1)
    ax.plot(v[:, 0], v[:, 1], color=INK, lw=1.6, zorder=3)
    # The apical tube walls, carrying on up out of the neck.
    for s in (-1, 1):
        ax.plot([s * hw, s * hw], [pts["P_t_l"][1], 0.78], color=INK, lw=1.6,
                zorder=3)
    ax.fill_betweenx([pts["P_t_l"][1], 0.78], -hw, hw, color="#FFE3E3",
                     zorder=1)
    # Where a flat cut would have gone instead — two corner stacks per side.
    ax.plot([-hw - 0.10, hw + 0.10], [pts["P_t_l"][1]] * 2, color=GREY,
            lw=0.9, ls=":", zorder=2)

    ax.scatter(*pts["P_s_l"], s=36, color=SHAFT_C, zorder=6)
    ax.scatter(*pts["P_s_r"], s=36, color=SHAFT_C, zorder=6)
    ax.scatter(*pts["P_t_l"], s=36, color=SOMA_C, zorder=6)
    ax.scatter(*pts["P_t_r"], s=36, color=SOMA_C, zorder=6)
    ax.annotate("P_s  slant leaves\nthe straight edge",
                xy=tuple(pts["P_s_l"]), xytext=(-0.50, 0.15), fontsize=8,
                color=SHAFT_C, ha="center",
                arrowprops=dict(arrowstyle="->", color=SHAFT_C, lw=0.8))
    ax.annotate("P_t  arc meets\nthe tube wall",
                xy=tuple(pts["P_t_r"]), xytext=(0.46, 0.62), fontsize=8,
                color=SOMA_C, ha="center",
                arrowprops=dict(arrowstyle="->", color=SOMA_C, lw=0.8))
    ax.text(-0.20, 0.47, "a flat cut here would leave\na corner stack at each "
            "shoulder", fontsize=7.5, color=GREY, ha="right", va="center")
    ax.set_title("2 · the neck, not a flat top", fontsize=10, loc="left")
    ax.set_aspect("equal")
    ax.set_xlim(-0.95, 0.62)
    ax.set_ylim(-0.05, 0.80)
    ax.axis("off")

    # -- 3. burying the basal corner -----------------------------------------
    ax = axes[2]
    corner = g["base_l"]
    br = g["basals"][0]["branch"]
    # The soma itself, so "inside the soma" is something you can see.
    ax.fill(v[:, 0], v[:, 1], color="#F2F2F2", zorder=1)
    ax.plot(v[:, 0], v[:, 1], color=GREY, lw=1.2, zorder=2)
    outline = br.outline(width=cell.width * cell.basal_width,
                         taper=cell.taper,
                         base_ext=1.2 * cell.basal_half_width)
    ax.fill(outline[:, 0], outline[:, 1], color="#FFE3E3", zorder=3)
    ax.plot(outline[:, 0], outline[:, 1], color=INK, lw=1.3, zorder=4)
    ax.plot(br.centre[:, 0], br.centre[:, 1], color=SOMA_C, lw=1.0, ls=":",
            zorder=5)
    ax.scatter(*corner, s=44, color=SHAFT_C, zorder=6)
    ax.scatter(*br.origin, s=34, color=SOMA_C, zorder=6)
    ax.annotate("the branch axis starts\nback up inside the soma",
                xy=tuple(br.origin), xytext=(0.20, -0.18), fontsize=8,
                color=SOMA_C, ha="left",
                arrowprops=dict(arrowstyle="->", color=SOMA_C, lw=0.8))
    ax.annotate("so the tube's fill swallows the\ncorner — and the notch "
                "that\na butt joint would leave",
                xy=tuple(corner), xytext=(0.10, -1.30), fontsize=8,
                color=SHAFT_C, ha="left",
                arrowprops=dict(arrowstyle="->", color=SHAFT_C, lw=0.8))
    ax.set_title("3 · rooting a basal through its corner", fontsize=10,
                 loc="left")
    ax.set_aspect("equal")
    ax.set_xlim(-1.30, 1.55)
    ax.set_ylim(-1.55, 0.55)
    ax.axis("off")

    # -- 4. anchors ----------------------------------------------------------
    ax = axes[3]
    bd.canvas(ax=ax)
    cell.draw(ax=ax, wall_lw=0.7, fill="white", gid="anchors")
    colors = {"spine": SPINE_C, "shaft": SHAFT_C, "soma": SOMA_C,
              "axon": GREY}
    for kind, color in colors.items():
        found = cell.anchors(kind)
        if not found:
            continue
        p = found.points()
        n = np.array([a.normal for a in found])
        ax.quiver(p[:, 0], p[:, 1], n[:, 0], n[:, 1], color=color,
                  scale=14, width=0.006, zorder=7)
        ax.scatter(p[:, 0], p[:, 1], s=14, color=color, zorder=8,
                   label=f"{kind} ({len(found)})")
    cell.fit(ax, pad=0.4)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.set_title("4 · anchors — every place things attach", fontsize=10,
                 loc="left")

    fig.tight_layout(w_pad=1.5)
    return fig, "blueprint.png"


BUILDS = (blueprint, portrait, spininess, body_plans, forks)


def main():
    for build in BUILDS:
        fig, name = build()
        # Compact raster for anything that lives in a README — see
        # `biodraw.io.save_compact` for why documentation is the one place
        # this library is not vector.
        bd.save_compact(fig, HERE / name)
        plt.close(fig)
        size = (HERE / name).stat().st_size / 1024
        print(f"wrote {(HERE / name).relative_to(HERE.parent.parent)} "
              f"({size:.0f} KB)")
    # No committed SVG here, deliberately. `bd.save(fig, "cell.svg")` gives
    # you the vector file, and this cell's runs to 98 kB — more than all five
    # rasters above put together, because the hollow render carries two paths
    # per part. `examples/dendritic_spine/spine.svg` is kept as the one
    # demonstration that vector export works; re-proving it in every folder
    # would cost ~100 kB each for nothing. See docs/PLAN.md.


if __name__ == "__main__":
    main()

"""The basket cell: a round soma with smooth dendrites in every direction.

    python tools/build_gallery.py basket
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import biodraw as bd  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
PAL = bd.style.palette.get()
INK = PAL["secondary"]
EXC = PAL["primary"]
# Annotation colours for the construction figures. Local on purpose:
# these label a *diagram about* the drawing, not the drawing, so they
# are not the library's identity palette's business.
MARK_A, MARK_B = "#7C3AED", "#059669"
SHAFT_C, TIP_C = MARK_B, MARK_A
GREY = "#9AA0A6"

plt.rcParams.update({"font.size": 9, "axes.linewidth": 0.8})


def _cell(**kw):
    return bd.neuro.Basket(**{"dendrites": 7, "forks": 0.55, "seed": 2, **kw})


def portrait():
    fig, ax = bd.canvas(figsize=(3.6, 3.6))
    cell = _cell()
    cell.draw(ax=ax, wall_lw=1.0, gid="basket")
    cell.fit(ax, pad=0.14)
    return fig, "basket.png"


def told_apart():
    """The point of this class: an inhibitory cell has to be distinguishable
    from an excitatory one *structurally*, so it survives greyscale."""
    fig, axes = plt.subplots(1, 4, figsize=(11.0, 3.4), dpi=150)
    pairs = [("default", None), ("mono", "mono")]
    for col, (name, pal) in enumerate(pairs):
        p = bd.style.palette.get(pal)
        for row, (cls, kw, key) in enumerate([
                (bd.neuro.Pyramidal, dict(spines=8, basal=2, basal_spines=4),
                 "primary"),
                (bd.neuro.Basket, dict(dendrites=7, forks=0.55, seed=2),
                 "secondary")]):
            ax = axes[col * 2 + row]
            bd.canvas(ax=ax)
            shape = cls(**kw)
            shape.draw(ax=ax, edge=p[key], wall_lw=1.0)
            shape.fit(ax, pad=0.16)
            ax.set_title(f"{cls.__name__.lower()} · {name}", fontsize=9,
                         color=GREY, loc="left")
    fig.tight_layout(w_pad=1.0)
    return fig, "told_apart.png"


def body_plans():
    """How many dendrites, over how much of the soma."""
    counts, arcs = (3, 5, 7, 10), (360.0, 200.0, 110.0)
    variants = [dict(dendrites=n, arc_deg=a, start_deg=90.0 - a / 2,
                     forks=None, seed=2)
                for a in arcs for n in counts]
    fig, _ = bd.contact_sheet(
        factory=bd.neuro.Basket, variants=variants, cols=4, cell_in=1.5,
        aspect=1.0, pad=0.16,
        row_labels=[f"{a:g}° of soma" for a in arcs],
        col_labels=[f"{n} dendrites" for n in counts],
    )
    return fig, "body_plans.png"


def branching():
    """Where a dendrite forks, and how wide."""
    forks, angles = (0.35, 0.55, 0.75), (20, 34, 52)
    variants = [dict(dendrites=6, forks=f, fork_angle_deg=a, seed=2)
                for f in forks for a in angles]
    fig, _ = bd.contact_sheet(
        factory=bd.neuro.Basket, variants=variants, cols=3, cell_in=1.6,
        aspect=1.0, pad=0.14,
        row_labels=[f"fork at {f:g}" for f in forks],
        col_labels=[f"{a}°" for a in angles],
    )
    return fig, "branching.png"


def regularity():
    """`jitter` and `length_ratio`: the difference between a cell and a
    snowflake."""
    jitters, ratios = (0.0, 0.22, 0.45), (1.0, 0.68, 0.40)
    variants = [dict(dendrites=8, jitter=j, length_ratio=r, forks=None,
                     seed=2)
                for j in jitters for r in ratios]
    fig, _ = bd.contact_sheet(
        factory=bd.neuro.Basket, variants=variants, cols=3, cell_in=1.5,
        aspect=1.0, pad=0.14,
        row_labels=[f"jitter {j:g}" for j in jitters],
        col_labels=[f"lengths {r:g}" for r in ratios],
    )
    return fig, "regularity.png"


def seeds():
    fig, _ = bd.contact_sheet(
        factory=bd.neuro.Basket,
        variants=[dict(dendrites=7, forks=0.55, seed=s) for s in range(8)],
        labels="auto", cols=8, cell_in=1.15, aspect=1.0, pad=0.16,
    )
    return fig, "seeds.png"


def blueprint():
    cell = _cell()
    g = cell.geometry
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.8), dpi=150)

    # -- 1. the skeleton -----------------------------------------------------
    ax = axes[0]
    soma = g["soma"]
    ax.plot(soma[:, 0], soma[:, 1], color=GREY, lw=1.2, ls="--")
    for d in g["dendrites"]:
        br = d["branch"]
        ax.plot(br.centre[:, 0], br.centre[:, 1], color=INK, lw=1.4)
        ax.scatter(*br.origin, s=16, color=SHAFT_C, zorder=5)
        for c in d["children"]:
            cb = c["branch"]
            ax.plot(cb.centre[:, 0], cb.centre[:, 1], color=INK, lw=1.0,
                    alpha=0.75)
    ax.text(0.0, -0.05, "roots start\ninside the soma", fontsize=8,
            color=SHAFT_C, ha="center")
    ax.set_title("1 · even slots, then knocked off them", fontsize=10,
                 loc="left")
    ax.set_aspect("equal")
    ax.axis("off")

    # -- 2. what jitter buys -------------------------------------------------
    ax = axes[1]
    for dx, jit, lab, color in ((-1.3, 0.0, "jitter 0 — a snowflake", GREY),
                                (1.3, 0.22, "jitter 0.22", INK)):
        c = bd.neuro.Basket(dendrites=8, jitter=jit, length_ratio=1.0
                            if jit == 0 else 0.68, forks=None, seed=2,
                            at=(dx, 0.0))
        c.draw(ax=ax, edge=color, wall_lw=0.9)
        ax.text(dx, -1.55, lab, fontsize=8, color=color, ha="center")
    bd.fit(ax, [np.vstack([np.asarray(p) for p in
                           bd.neuro.Basket(dendrites=8, forks=None, seed=2,
                                           at=(dx, 0.0)).points])
                for dx in (-1.3, 1.3)], pad=0.35)
    ax.set_title("2 · a repeated part must not repeat exactly", fontsize=10,
                 loc="left")

    # -- 3. anchors ----------------------------------------------------------
    ax = axes[2]
    bd.canvas(ax=ax)
    cell.draw(ax=ax, wall_lw=0.7, fill="white", gid="anchors")
    for kind, color, step in (("soma", EXC, 1), ("shaft", SHAFT_C, 7),
                              ("tip", TIP_C, 1)):
        found = list(cell.anchors(kind))[::step]
        if not found:
            continue
        p = np.array([a.xy for a in found])
        n = np.array([a.normal for a in found])
        ax.quiver(p[:, 0], p[:, 1], n[:, 0], n[:, 1], color=color, scale=14,
                  width=0.005, zorder=7)
        ax.scatter(p[:, 0], p[:, 1], s=11, color=color, zorder=8,
                   label=f"{kind} ({len(cell.anchors(kind))})")
    cell.fit(ax, pad=0.30)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.set_title("3 · anchors (shaft thinned 7x to show)", fontsize=10,
                 loc="left")

    fig.tight_layout(w_pad=1.3)
    return fig, "blueprint.png"


BUILDS = (blueprint, portrait, told_apart, body_plans, branching, regularity,
          seeds)


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

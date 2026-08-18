"""The generic cell: a body, a nucleus, and things inside it.

    python tools/build_gallery.py generic
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
NUC = PAL["inhibitory"]
# Annotation colours for the construction figures. Local on purpose:
# these label a *diagram about* the drawing, not the drawing, so they
# are not the library's identity palette's business.
MARK_A, MARK_B = "#7C3AED", "#059669"
ORG, WALL_C = MARK_A, MARK_B
GREY = "#9AA0A6"

plt.rcParams.update({
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
})


def _cell(**kw):
    return bd.cells.Blob(**{"organelles": 7, "seed": 3, **kw})


# ---------------------------------------------------------------------------
# the deliverables
# ---------------------------------------------------------------------------

def portrait():
    """The cell on its own."""
    fig, ax = bd.canvas(figsize=(3.4, 3.2))
    cell = _cell()
    cell.draw(ax=ax, wall_lw=1.0, gid="cell")
    cell.fit(ax, pad=0.12)
    return fig, "cell.png"


def contents():
    """How much is in the cytoplasm — and what it costs to fit more.

    At the default size and separation the body holds ten; past that
    `scatter_in` raises rather than quietly drawing fewer. Getting more in
    means smaller organelles packed closer, which is a real statement about
    the cell and not a rendering detail, so the last two cells here say so.
    """
    packed = dict(organelle_size=0.115, organelle_sep=0.22)
    variants = [dict(organelles=n, seed=3) for n in (0, 3, 6, 10)]
    variants += [dict(organelles=n, seed=3, **packed) for n in (16, 22)]
    fig, _ = bd.contact_sheet(
        factory=bd.cells.Blob, variants=variants, cols=6, cell_in=1.15,
        aspect=1.0,
        labels=["0", "3", "6", "10 — the most that fits",
                "16, smaller", "22, smaller still"],
    )
    return fig, "contents.png"


def body_shapes():
    """The three knobs that decide what kind of cell this is."""
    squares, wobbles = (2.0, 2.6, 3.6), (0.0, 0.03, 0.07)
    variants = [dict(squareness=s, wobble=w, wobble_n=5, organelles=5,
                     aspect=a, seed=3)
                for a in (1.0, 0.62)
                for s in squares
                for w in wobbles]
    fig, _ = bd.contact_sheet(
        factory=bd.cells.Blob, variants=variants, cols=9, cell_in=1.05,
        aspect=1.0,
        row_labels=["round", "flattened"],
        col_labels=[f"s={s:g}\nwobble={w:g}" for s in squares
                    for w in wobbles],
    )
    return fig, "body_shapes.png"


def membranes():
    """Protrusions: the same branch engine that draws a dendrite, doing
    microvilli, filopodia and pseudopodia instead."""
    kinds = [
        dict(protrusions=18, protrusion_len=0.16, protrusion_width=0.05),
        dict(protrusions=10, protrusion_len=0.34, protrusion_width=0.07),
        dict(protrusions=5, protrusion_len=0.52, protrusion_width=0.13),
    ]
    arcs = (360.0, 180.0, 90.0)
    variants = [dict(organelles=4, seed=3, protrusion_arc_deg=arc, **k)
                for k in kinds for arc in arcs]
    fig, _ = bd.contact_sheet(
        factory=bd.cells.Blob, variants=variants, cols=3, cell_in=1.5,
        aspect=1.0,
        row_labels=["microvilli", "filopodia", "pseudopodia"],
        col_labels=[f"{a:g}° of wall" for a in arcs],
    )
    return fig, "membranes.png"


def seeds():
    """One cell, eight seeds. Nothing else differs — this is the whole of what
    `seed` names."""
    fig, _ = bd.contact_sheet(
        factory=bd.cells.Blob,
        variants=[dict(organelles=8, protrusions=9, seed=s)
                  for s in range(8)],
        labels="auto", cols=8, cell_in=1.05, aspect=1.0,
    )
    return fig, "seeds.png"


# ---------------------------------------------------------------------------
# blueprint.png
# ---------------------------------------------------------------------------

def blueprint():
    cell = _cell(protrusions=9)
    g = cell.geometry
    fig, axes = plt.subplots(1, 4, figsize=(14.0, 3.9), dpi=150)

    # -- 1. the layer stack --------------------------------------------------
    # The reason this shape exists: it is the first that is not one contour.
    ax = axes[0]
    for i, (lay, name, color) in enumerate(zip(
            cell.layers, ("wall + protrusions", "organelles", "nucleus",
                          "nucleolus"),
            (INK, ORG, NUC, WALL_C), strict=True)):
        # Fan the layers out to the right so the stack is legible as a stack.
        shift = np.array([i * 1.35, 0.0])
        for part in lay.closed:
            v = np.asarray(part) + shift
            ax.fill(v[:, 0], v[:, 1], color=color, alpha=0.16, zorder=2)
            ax.plot(v[:, 0], v[:, 1], color=color, lw=1.3, zorder=3)
        for part in lay.open_:
            v = np.asarray(part) + shift
            ax.plot(v[:, 0], v[:, 1], color=color, lw=1.0, zorder=3)
        ax.text(shift[0], -0.75, f"{i}. {name}", fontsize=7.5, color=color,
                ha="center")
        if i:
            ax.annotate("", xy=(shift[0] - 0.52, 0.0),
                        xytext=(shift[0] - 0.83, 0.0),
                        arrowprops=dict(arrowstyle="->", color=GREY, lw=0.9))
    ax.text(2.0, 0.92, "each layer is its own render pass,\n"
                       "so it covers the one below instead of fusing",
            fontsize=8, color=GREY, ha="center")
    ax.set_title("1 · four layers, not one union", fontsize=10, loc="left")
    ax.set_aspect("equal")
    ax.axis("off")

    # -- 2. why it cannot be one union --------------------------------------
    ax = axes[1]
    closed, _ = cell.parts
    wrong = [np.asarray(p) for p in closed]
    bd.core.render.render_hollow(
        ax, wrong, fill=bd.core.render.resolve_fill(None, None, INK),
        edge=INK, wall_lw=1.2, gid="fused")
    ax.text(0.0, -0.78, "everything in ONE render_hollow call", fontsize=8,
            color=GREY, ha="center")
    ax.annotate("the nucleus is still there —\nit just fused into the body",
                xy=tuple(g["nucleus_centre"]), xytext=(0.0, 0.80),
                fontsize=8, color=NUC, ha="center",
                arrowprops=dict(arrowstyle="->", color=NUC, lw=0.8))
    bd.fit(ax, wrong, pad=0.18)
    ax.set_title("2 · the same parts, unioned", fontsize=10, loc="left")

    # -- 3. scattering the cytoplasm ----------------------------------------
    ax = axes[2]
    wall, nucleus = g["wall"], g["nucleus"]
    size = cell.organelle_size * cell.radius
    ax.fill(wall[:, 0], wall[:, 1], color="#F2F2F2", zorder=1)
    ax.plot(wall[:, 0], wall[:, 1], color=GREY, lw=1.2, zorder=2)
    ax.plot(nucleus[:, 0], nucleus[:, 1], color=NUC, lw=1.2, zorder=3)
    # The two exclusions the sampler is actually working against.
    for ring, color, label in ((wall, WALL_C, "margin from the wall"),
                               (nucleus, NUC, "clearance from the nucleus")):
        inner = _inset(ring, size)
        ax.plot(inner[:, 0], inner[:, 1], color=color, lw=0.9, ls="--",
                zorder=4, label=label)
    for o in g["organelles"]:
        v = o["outline"]
        ax.fill(v[:, 0], v[:, 1], color=ORG, alpha=0.20, zorder=5)
        ax.plot(v[:, 0], v[:, 1], color=ORG, lw=1.0, zorder=6)
    centres = np.array([o["centre"] for o in g["organelles"]])
    ax.scatter(centres[:, 0], centres[:, 1], s=14, color=ORG, zorder=7)
    # The separation constraint, drawn on the closest surviving pair.
    i, j = _closest_pair(centres)
    ax.plot(centres[[i, j], 0], centres[[i, j], 1], color=ORG, lw=0.9,
            ls=":", zorder=7)
    ax.text(*(centres[[i, j]].mean(axis=0) + [0.0, 0.03]),
            f"min_sep = {cell.organelle_sep * cell.radius:.2f}", fontsize=7.5,
            color=ORG, ha="center")
    ax.legend(fontsize=7, frameon=False, loc="lower center")
    ax.set_title("3 · scatter_in, and what it avoids", fontsize=10,
                 loc="left")
    ax.set_aspect("equal")
    ax.axis("off")

    # -- 4. anchors ----------------------------------------------------------
    ax = axes[3]
    bd.canvas(ax=ax)
    cell.draw(ax=ax, wall_lw=0.7, fill="white", gid="anchors")
    colors = {"wall": WALL_C, "nucleus": NUC, "organelle": ORG, "tip": GREY}
    for kind, color in colors.items():
        found = cell.anchors(kind)
        if not found:
            continue
        p = found.points()
        n = np.array([a.normal for a in found])
        ax.quiver(p[:, 0], p[:, 1], n[:, 0], n[:, 1], color=color,
                  scale=13, width=0.006, zorder=7)
        ax.scatter(p[:, 0], p[:, 1], s=13, color=color, zorder=8,
                   label=f"{kind} ({len(found)})")
    cell.fit(ax, pad=0.30)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.set_title("4 · anchors", fontsize=10, loc="left")

    fig.tight_layout(w_pad=1.4)
    return fig, "blueprint.png"


def _inset(ring, d):
    """`ring` pulled `d` toward its own centroid — a stand-in for the offset
    curve, good enough to show *where* a margin bites without bringing in a
    real polygon-offset routine for one annotation."""
    c = ring.mean(axis=0)
    v = ring - c
    r = np.linalg.norm(v, axis=1)[:, None]
    return c + v * (1.0 - d / r)


def _closest_pair(pts):
    d = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=2)
    np.fill_diagonal(d, np.inf)
    return np.unravel_index(np.argmin(d), d.shape)


BUILDS = (blueprint, portrait, contents, body_shapes, membranes, seeds)


def main():
    for build in BUILDS:
        fig, name = build()
        # Compact raster for anything that lives in a README — see
        # `biodraw.io.QUALITY` for the three profiles and which one is in
        # force. `--quality debug` on the gallery builder is how you get an
        # image big enough to actually check geometry in.
        bd.save_compact(fig, HERE / name)
        plt.close(fig)
        size = (HERE / name).stat().st_size / 1024
        print(f"wrote {(HERE / name).relative_to(HERE.parent.parent)} "
              f"({size:.0f} KB)")


if __name__ == "__main__":
    main()

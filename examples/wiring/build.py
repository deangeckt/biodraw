"""Wiring cells to each other: connectors, endcaps, and branching arbors.

    python tools/build_gallery.py wiring
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import biodraw as bd  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
PAL = bd.style.palette.get()
EXC = PAL["primary"]
INH = PAL["secondary"]
GREY = PAL["neutral"]

plt.rcParams.update({"font.size": 9, "axes.linewidth": 0.8})


def endcaps():
    """The mark at the far end is a claim, not decoration."""
    kinds = bd.core.connectors.ENDCAPS
    # The panel is as tall as the drawing needs and no taller: the phantom
    # box below sets the frame, and an over-tall figure turns the surplus
    # into white space in the committed PNG (the frame report in
    # `tools/build_gallery.py` had this one at 69% of its height).
    fig, axes = plt.subplots(1, len(kinds), figsize=(11.5, 1.55), dpi=150)
    for ax, kind in zip(axes, kinds, strict=True):
        bd.canvas(ax=ax)
        cell = bd.cells.Blob(radius=0.30, organelles=0, nucleolus=0.0,
                             at=(1.25, 0.0))
        cell.draw(ax=ax, edge=GREY, wall_lw=0.9)
        bd.connect(
            ax=ax,
            source=(-0.35, 0.10),                 # a bare point, for clarity
            target=cell.anchor("wall", deg=180.0),
            gap=0.05,                             # clearance at the wall
            rad=0.05,                             # bow; positive bows up
            endcap=kind,                          # <- the thing being shown
            color=EXC if kind in ("dot", "arrow") else INH,
            lw=1.4, cap_size=44.0,
        )
        ax.set_title(repr(kind), fontsize=9, color=GREY)
        # A phantom box, so every panel is framed identically whatever its
        # endcap does. Its half-height clears the cell wall (0.30) and the
        # bowed connector (~0.20) and nothing more.
        bd.fit(ax, cell.points + [np.array([[-0.45, -0.34], [1.7, 0.34]])],
               pad=0.05)
    fig.tight_layout(w_pad=0.6)
    return fig, "endcaps.png"


def connector_shapes():
    """`drop`, `rad` and `smooth` — the three knobs that decide whether a
    connection reads as a process or as a circuit diagram's wire."""
    fig, axes = plt.subplots(3, 4, figsize=(11.0, 6.2), dpi=150)
    rows = [("drop", (0.0, 0.4, 0.9, 1.5), dict(rad=0.06, smooth=0.25)),
            ("rad", (-0.12, 0.0, 0.10, 0.25), dict(drop=0.7, smooth=0.25)),
            ("smooth", (0.0, 0.2, 0.5, 0.9), dict(drop=0.7, rad=0.06))]
    for r, (name, values, fixed) in enumerate(rows):
        for c, v in enumerate(values):
            ax = axes[r][c]
            bd.canvas(ax=ax)
            src = bd.cells.Blob(radius=0.22, organelles=0, nucleus=0.35,
                                nucleolus=0.0, at=(-1.5, 0.9))
            dst = bd.cells.Blob(radius=0.22, organelles=0, nucleus=0.35,
                                nucleolus=0.0, at=(1.5, -0.5))
            for s in (src, dst):
                s.draw(ax=ax, edge=GREY, wall_lw=0.8)
            bd.connect(ax=ax, source=src.anchor("wall", deg=270.0),
                       target=dst.anchor("wall", deg=90.0), gap=0.05,
                       color=EXC, lw=1.4, endcap="dot", cap_size=30.0,
                       **{name: v, **fixed})
            ax.set_title(f"{name}={v:g}", fontsize=8, color=GREY, pad=2)
            bd.fit(ax, src.points + dst.points, pad=0.3)
    fig.tight_layout(pad=0.4)
    return fig, "connector_shapes.png"


def one_to_many():
    """A cell reaching several targets is one *branching* arbor, not several
    strokes — which is both what the cell has and what stops the lines
    crossing on a staggered row."""
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.6), dpi=150)
    places = [(-2.2, -1.5), (0.2, -2.1), (2.4, -1.2)]
    for ax, mode in zip(axes, ("separate strokes", "one arbor"), strict=True):
        bd.canvas(ax=ax)
        src = bd.neuro.Basket(dendrites=6, radius=0.30, length=0.55,
                              forks=None, seed=2, at=(0.0, 1.4))
        src.draw(ax=ax, wall_lw=0.9)
        targets = []
        for k, p in enumerate(places):
            cell = bd.neuro.Pyramidal(spines=5, basal=2, basal_spines=3,
                                      scale=0.5, at=p, seed=k)
            cell.draw(ax=ax, wall_lw=0.9)
            targets.append(cell.anchor("soma", nearest=src.at))
        if mode == "one arbor":
            bd.connect_tree(ax=ax, source=src.anchor("soma", deg=270.0),
                            targets=targets, gap=0.04, drop=0.55, rad=0.05,
                            fork=0.45, spread=0.4, color=INH, lw=1.4,
                            endcap="bar", cap_size=40.0)
        else:
            for t in targets:
                bd.connect(ax=ax, source=src.anchor("soma", deg=270.0),
                           target=t, gap=0.04, drop=0.55, rad=0.05,
                           color=INH, lw=1.4, endcap="bar", cap_size=40.0)
        ax.set_title(mode, fontsize=10, color=GREY, loc="left")
        bd.fit(ax, src.points + [np.array([[-3.0, -2.8], [3.2, 2.2]])],
               pad=0.15)
    fig.tight_layout(w_pad=1.2)
    return fig, "one_to_many.png"


def bus():
    """Curves fan; a bus shares. Same source, same three targets, two claims.

    A separate curve per target says *three separate things happened*. A stem
    dropping to one horizontal, with a riser turning up into each target, says
    *these all share a source* — and the eye follows a straight line where it
    has to trace a curve.

    The right angles are the point rather than a limitation: a square corner
    reads as **routing**, which is exactly what a shared rail is claiming, so
    `corner` defaults to 0.
    """
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.4), dpi=150)
    places = [(-2.6, 1.1), (0.0, 1.1), (2.6, 1.1)]
    for ax, mode in zip(axes, ("one curve each", "one bus"), strict=True):
        bd.canvas(ax=ax)
        src = bd.neuro.Pyramidal(spines=0, basal=2, basal_spines=0,
                                 scale=0.62, at=(0.0, -1.7))
        src.draw(ax=ax, wall_lw=0.9)
        targets = []
        for k, place in enumerate(places):
            cell = bd.neuro.Pyramidal(spines=0, basal=2, basal_spines=0,
                                      scale=0.52, at=place, seed=k)
            cell.draw(ax=ax, wall_lw=0.9)
            low = min(a.xy[1] for a in cell.anchors("soma"))
            targets.append(bd.Anchor((cell.at[0], low), (0.0, -1.0), "soma"))
        if mode == "one bus":
            # The rail goes *below* every cell, including the source. Put it
            # between them and the stem climbs back through the source's own
            # soma, which reads as an overdrawn dendrite rather than a route.
            bd.connect_bus(ax=ax, source=src.anchor("axon"), targets=targets,
                           rail=-3.05, gap=0.10, color=EXC, lw=1.8,
                           # weight is a variable: the third is the weak one
                           lws=[1.8, 1.8, 0.7],
                           endcap="arrow", cap_size=120.0)
        else:
            for k, target in enumerate(targets):
                bd.connect(ax=ax, source=src.anchor("axon"), target=target,
                           gap=0.10, drop=0.85, rad=0.06, color=EXC,
                           lw=1.8 if k < 2 else 0.7, endcap="arrow",
                           cap_size=120.0)
        ax.set_title(mode, fontsize=10, color=GREY, loc="left")
        bd.fit(ax, src.points + [np.array([[-3.4, -3.5], [3.4, 2.3]])],
               pad=0.15)
    fig.tight_layout(w_pad=1.2)
    return fig, "bus.png"


def circuit():
    """Two cell types and one branching arbor onto three named places.

    No drawn axon. A projection between cells is a line with a mark on the
    end — see the note in `biodraw/neuro/__init__.py` for why the "realistic"
    axon was removed.
    """
    fig, ax = bd.canvas(figsize=(7.2, 4.2))

    pyr = bd.neuro.Pyramidal(spines=9, basal=2, basal_spines=5,
                             apical_fork=0.5, at=(0.0, 0.0))
    bas = bd.neuro.Basket(dendrites=7, forks=0.5, radius=0.34, length=0.85,
                          seed=2, at=(2.9, -0.45))
    for shape, gid in ((pyr, "pyramidal"), (bas, "basket")):
        shape.draw(ax=ax, wall_lw=1.0, gid=gid)

    # Perisomatic — what a basket cell does. The three places are named
    # outright: which compartment a contact lands on is a claim about the
    # circuit, and the figure's author makes it, not the library.
    bd.connect_tree(
        ax=ax,
        source=bas.anchor("soma", nearest=pyr.at),
        targets=[pyr.anchor("soma", side=1, t=t) for t in (0.24, 0.42, 0.60)],
        gap=0.035,              # clearance at the wall
        drop=0.30,              # drop clear of the cell before running
        rad=0.05,               # bow, always upward
        fork=0.5, spread=0.42,
        color=INH, lw=1.3,
        endcap="bar",           # a bar: inhibition
        cap_size=42.0,
    )

    ax.text(0.0, 2.60, "pyramidal", fontsize=9, color=EXC, ha="center")
    ax.text(2.9, 0.95, "basket", fontsize=9, color=INH, ha="center")
    ax.text(1.70, 0.55, "perisomatic inhibition", fontsize=8.5, color=INH,
            ha="center")

    bd.fit(ax, pyr.points + bas.points, pad=0.22)
    return fig, "circuit.png"


BUILDS = (circuit, endcaps, connector_shapes, one_to_many, bus)


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

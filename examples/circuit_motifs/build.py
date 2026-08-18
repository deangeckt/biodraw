"""Circuit motifs, and a cortical column — everything composed at once.

    python tools/build_gallery.py motifs
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

import biodraw as bd  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
PAL = bd.style.palette.get()
EXC, INH, GREY = PAL["excitatory"], PAL["inhibitory"], PAL["neutral"]

plt.rcParams.update({"font.size": 9, "axes.linewidth": 0.8})


def _pyr(at, scale=1.0, **kw):
    return bd.neuro.Pyramidal(**{"spines": 6, "basal": 2, "basal_spines": 3,
                                 "at": at, "scale": scale, **kw})


def _bas(at, scale=1.0, **kw):
    return bd.neuro.Basket(**{"dendrites": 6, "radius": 0.32, "length": 0.62,
                              "forks": None, "seed": 2, "at": at,
                              "scale": scale, **kw})


def _wire(ax, src, dst, kind, **kw):
    """One connection, with the endcap that names what it is.

    `'exc'` and `'inh'` are the only two this figure uses, and each keeps one
    colour and one mark throughout — which is what lets the key be three lines
    long instead of a paragraph.
    """
    excite = kind == "exc"
    return bd.connect(
        ax=ax, source=src, target=dst,
        gap=kw.pop("gap", 0.05),
        drop=kw.pop("drop", 0.35),
        rad=kw.pop("rad", 0.07),
        color=EXC if excite else INH,
        endcap="arrow" if excite else "bar",
        cap_size=kw.pop("cap_size", 40.0), lw=1.3, **kw)


# ---------------------------------------------------------------------------
# motifs
# ---------------------------------------------------------------------------

def _feedforward(ax):
    a = _pyr((-1.9, 0.0), 0.55)
    i = _bas((0.0, -0.30), 0.85)
    b = _pyr((1.9, 0.0), 0.55)
    for s in (a, i, b):
        s.draw(ax=ax, wall_lw=0.9)
    _wire(ax, a.anchor("soma", nearest=i.at), i.anchor("soma", nearest=a.at),
          "exc", drop=0.15)
    _wire(ax, i.anchor("soma", nearest=b.at), b.anchor("soma", nearest=i.at),
          "inh", drop=0.15)
    _wire(ax, a.anchor("soma", side=1, t=0.24),
          b.anchor("soma", side=-1, t=0.24), "exc", drop=0.0, rad=0.22)
    return [a, i, b], "feedforward inhibition"


def _feedback(ax):
    a = _pyr((-1.3, 0.0), 0.55)
    i = _bas((1.4, 0.15), 0.85)
    for s in (a, i):
        s.draw(ax=ax, wall_lw=0.9)
    _wire(ax, a.anchor("soma", side=1, t=0.24),
          i.anchor("soma", nearest=a.at), "exc", drop=0.10, rad=0.14)
    _wire(ax, i.anchor("soma", deg=225.0),
          a.anchor("soma", side=1, t=0.60), "inh", drop=0.35, rad=-0.10)
    return [a, i], "feedback inhibition"


def _disinhibition(ax):
    i1 = _bas((-1.7, 0.0), 0.8, seed=4)
    i2 = _bas((0.1, -0.1), 0.8, seed=2)
    b = _pyr((1.9, 0.0), 0.55)
    for s in (i1, i2, b):
        s.draw(ax=ax, wall_lw=0.9)
    _wire(ax, i1.anchor("soma", nearest=i2.at),
          i2.anchor("soma", nearest=i1.at), "inh", drop=0.12)
    _wire(ax, i2.anchor("soma", nearest=b.at),
          b.anchor("soma", nearest=i2.at), "inh", drop=0.12)
    return [i1, i2, b], "disinhibition"


def _convergence(ax):
    sources = [_pyr((-2.0, y), 0.42) for y in (1.15, 0.0, -1.15)]
    target = _pyr((1.9, 0.0), 0.60)
    for s in (*sources, target):
        s.draw(ax=ax, wall_lw=0.9)
    for s in sources:
        _wire(ax, s.anchor("soma", nearest=target.at),
              target.anchor("soma", nearest=s.at), "exc", drop=0.10,
              rad=0.05)
    return [*sources, target], "convergence"


def _divergence(ax):
    src = _bas((-1.9, 0.4), 0.85)
    targets = [_pyr((1.5, y), 0.42) for y in (1.2, 0.0, -1.2)]
    for s in (src, *targets):
        s.draw(ax=ax, wall_lw=0.9)
    # One *branching* arbor, not three strokes — see the wiring example.
    bd.connect_tree(
        ax=ax, source=src.anchor("soma", deg=315.0),
        targets=[t.anchor("soma", nearest=src.at) for t in targets],
        gap=0.05, drop=0.5, rad=0.05, fork=0.45, spread=0.45,
        color=INH, lw=1.3, endcap="bar", cap_size=40.0)
    return [src, *targets], "divergence"


def _recurrent(ax):
    a = _pyr((-1.5, 0.0), 0.55, seed=1)
    b = _pyr((1.5, 0.0), 0.55, seed=3)
    for s in (a, b):
        s.draw(ax=ax, wall_lw=0.9)
    _wire(ax, a.anchor("soma", side=1, t=0.24),
          b.anchor("soma", side=-1, t=0.24), "exc", drop=0.0, rad=0.26)
    _wire(ax, b.anchor("soma", side=-1, t=0.60),
          a.anchor("soma", side=1, t=0.60), "exc", drop=0.0, rad=0.26)
    return [a, b], "recurrent excitation"


def motifs():
    """Six canonical motifs, wired the same way throughout so the key holds
    across every panel."""
    builders = (_feedforward, _feedback, _disinhibition,
                _convergence, _divergence, _recurrent)
    fig, axes = plt.subplots(2, 3, figsize=(12.0, 7.0), dpi=150)
    for ax, build, letter in zip(axes.ravel(), builders, "ABCDEF",
                                 strict=True):
        bd.canvas(ax=ax)
        shapes, title = build(ax)
        bd.fit(ax, [p for s in shapes for p in s.points], pad=0.30)
        ax.set_title(f"{letter}   {title}", fontsize=10, loc="left",
                     color="#333333")
    fig.tight_layout(pad=1.0)
    return fig, "motifs.png"


# ---------------------------------------------------------------------------
# the column
# ---------------------------------------------------------------------------

def column():
    """A cortical column: cells of one kind at several depths, one inhibitory
    cell, and a projection leaving the bottom.

    The layer rules are the only place a horizontal line is allowed in this
    figure — nothing else sits on a baseline by accident.
    """
    fig, ax = bd.canvas(figsize=(6.6, 6.4))

    layers = [("I", 3.05), ("II/III", 1.55), ("IV", 0.15),
              ("V", -1.45), ("VI", -2.75)]
    for name, y in layers:
        ax.axhline(y, color="#DDDDDD", lw=0.9, zorder=0)
        ax.text(-3.35, y + 0.10, name, fontsize=8.5, color=GREY, va="bottom")

    cells = []
    # Layer II/III: small pyramidal cells, apicals into layer I.
    for k, x in enumerate((-1.9, -0.5, 0.9)):
        c = _pyr((x, 0.55), 0.62, spines=7, basal_spines=4,
                 apical_fork=0.55, fork_spines=3, seed=k)
        c.draw(ax=ax, wall_lw=0.9)
        cells.append(c)
    # Layer V: one big pyramidal cell, apical reaching the top.
    big = _pyr((0.1, -1.15), 1.05, spines=10, basal_spines=5,
               trunk_len=2.9, apical_fork=0.68, fork_spines=4, seed=7)
    big.draw(ax=ax, wall_lw=1.0)
    cells.append(big)
    # And one basket cell, beside it.
    bas = _bas((2.05, -0.85), 1.0, dendrites=7, forks=0.55)
    bas.draw(ax=ax, wall_lw=0.9)
    cells.append(bas)

    # Perisomatic inhibition onto the layer V cell — the canonical thing, and
    # the three places are named outright rather than allocated: which
    # compartment a contact lands on is the author's claim about the circuit.
    bd.connect_tree(
        ax=ax, source=bas.anchor("soma", nearest=big.at),
        targets=[big.anchor("soma", side=1, t=t) for t in (0.24, 0.42, 0.60)],
        gap=0.035, drop=0.28, rad=0.05, fork=0.5, spread=0.42,
        color=INH, lw=1.3, endcap="bar", cap_size=42.0)

    # The layer V cell's output, leaving the column — a line with an arrow,
    # not a drawn axon. See `biodraw/neuro/__init__.py`.
    leaving = big.anchor("axon")
    bd.connect(ax=ax, source=leaving, target=leaving.offset(1.7),
               gap=0.0, drop=0.0, rad=0.0, color=EXC, lw=1.3,
               endcap="arrow", cap_size=46.0)
    ax.text(-1.15, -3.35, "to subcortical targets", fontsize=8, color=EXC,
            ha="center")

    ax.text(2.05, 0.30, "basket", fontsize=8.5, color=INH, ha="center")
    ax.text(1.55, -1.35, "perisomatic\ninhibition", fontsize=8, color=INH,
            ha="center")

    bd.fit(ax, [p for c in cells for p in c.points], pad=0.30)
    return fig, "column.png"


def claims():
    """The same two cells, four different assertions. Only the endcap and the
    colour change — which is exactly how much should have to."""
    kinds = [("dot", EXC, "contact, unspecified"),
             ("arrow", EXC, "excitation"),
             ("bar", INH, "inhibition"),
             ("open", GREY, "putative — not asserted")]
    fig, axes = plt.subplots(1, 4, figsize=(12.0, 3.2), dpi=150)
    for ax, (kind, color, title) in zip(axes, kinds, strict=True):
        bd.canvas(ax=ax)
        src = _bas((-1.5, 0.55), 0.85)
        dst = _pyr((1.3, 0.0), 0.62)
        for s in (src, dst):
            s.draw(ax=ax, wall_lw=0.9)
        bd.connect(ax=ax, source=src.anchor("soma", nearest=dst.at),
                   target=dst.anchor("soma", nearest=src.at), gap=0.05,
                   drop=0.30, rad=0.06, color=color, endcap=kind,
                   cap_size=48.0, lw=1.4)
        ax.set_title(f"{kind!r} — {title}", fontsize=9, color="#333333",
                     loc="left")
        bd.fit(ax, src.points + dst.points, pad=0.28)
    fig.tight_layout(w_pad=1.0)
    return fig, "claims.png"


def palettes():
    """One circuit, three palettes. `mono` is the check that the drawing still
    reads when its colours are taken away."""
    names = bd.style.palette.available()
    fig, axes = plt.subplots(1, len(names), figsize=(4.0 * len(names), 3.4),
                            dpi=150)
    for ax, name in zip(axes, names, strict=True):
        p = bd.style.palette.get(name)
        bd.canvas(ax=ax)
        src = _bas((-1.6, 0.5), 0.85)
        dst = _pyr((1.4, 0.0), 0.62)
        src.draw(ax=ax, edge=p["inhibitory"], wall_lw=0.9)
        dst.draw(ax=ax, edge=p["excitatory"], wall_lw=0.9)
        bd.connect(ax=ax, source=src.anchor("soma", nearest=dst.at),
                   target=dst.anchor("soma", nearest=src.at), gap=0.05,
                   drop=0.30, rad=0.06, color=p["inhibitory"], endcap="bar",
                   cap_size=44.0, lw=1.4)
        ax.set_title(name, fontsize=10, color="#333333", loc="left")
        bd.fit(ax, src.points + dst.points, pad=0.28)
    fig.tight_layout(w_pad=1.0)
    return fig, "palettes.png"


BUILDS = (column, motifs, claims, palettes)


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

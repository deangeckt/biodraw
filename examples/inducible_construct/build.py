"""A chemically inducible expression system, and the pieces it is made of.

The first `biodraw.genetics` example, and the first drawing in the catalog
that is a *construct* rather than a cell. Its parts list was read off figure 1
of doi.org/10.1016/j.tibtech.2023.03.007 — a copper-inducible system: a
four-repeat operator, a minimal promoter, a gene of interest, a terminator,
and the two-lobed CUP2 protein that closes around a Cu(II) ion and carries a
transactivation domain.

What the figure is *for* here is the argument in `docs/PLAN.md`, milestone 10:
every knob on this page is a count or a length that somebody currently draws
by hand — your repeat number, your insert, your domain list — and a stock
asset cannot know any of them.

    python tools/build_gallery.py construct
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import biodraw as bd  # noqa: E402
from biodraw.genetics import (  # noqa: E402
    CDS,
    Promoter,
    Protein,
    Repeat,
    Terminator,
)

HERE = pathlib.Path(__file__).resolve().parent
PAL = bd.style.palette.get()
INK = PAL["ink"]
PROTEIN = PAL["tertiary"]
LIGAND = PAL["primary"]
# Annotation colours for the captions and the blueprint's rulers — a diagram
# *about* the drawing is not the drawing, and is not the palette's business.
TEXT = "#555555"
GREY = "#9AA0A6"

plt.rcParams.update({"font.size": 9})


def _label(ax, anchor, text, gap=0.05, **kw):
    """Text at an anchor, standing off along its normal.

    Every label on this page is placed this way rather than at a hand-tuned
    offset: the track's `label` anchor sits at that glyph's *own* top, so a
    tall promoter and a short coding sequence both get their name clear of
    themselves and neither is tuned by hand. This is the one-line stand-in
    for `annotate.label` (milestone 8).
    """
    kw.setdefault("ha", "center")
    kw.setdefault("va", "bottom" if anchor.normal[1] >= 0 else "top")
    kw.setdefault("fontsize", 8)
    kw.setdefault("color", TEXT)
    return ax.text(*anchor.offset(gap), text, **kw)


def _system(operator=4):
    """The construct and the protein that regulates it, as objects."""
    track = bd.Track([
        Repeat(n=operator, label=f"CBS operator x{operator}"),
        Promoter(label="minimal promoter"),
        CDS(width=0.92, label="GOI"),
        Terminator(label="term."),
    ])
    # Over the operator, because that is what it binds — the position is the
    # figure's claim, so it is arithmetic here and not a knob on the shape.
    # Scaled well down: at full size the protein is twice the height of the
    # construct it regulates, which says the wrong thing about both.
    x = 0.5 * sum(track.spans[0])
    cup2 = Protein(lobes=2, open_deg=30.0, tags=(42.0,), face_deg=90.0,
                   at=(x, 0.52), scale=0.62, seed=3)
    return track, cup2


# ---------------------------------------------------------------------------
# construct.png — the panel a reader recognises
# ---------------------------------------------------------------------------

def construct():
    track, cup2 = _system()
    fig, ax = bd.canvas(figsize=(7.4, 2.6))

    track.draw(ax=ax, edge=INK, wall_lw=1.0, gid="construct")
    cup2.draw(ax=ax, edge=PROTEIN, wall_lw=1.0, gid="cup2")

    # The ligand is a dot at an anchor, not a shape. See the module docstring
    # of `biodraw.genetics`, and the same call made for synapses.
    ion = cup2.anchor("cleft")
    ax.plot(*ion.xy, "o", ms=5.5, color=LIGAND, zorder=6)
    # A leader, because the ion is *inside* the closed body: a label beside
    # it would sit on the protein's own wall.
    ax.annotate("Cu²⁺", xy=ion.xy, xytext=ion.xy + np.array([-0.62, 0.30]),
                fontsize=8.5, color=LIGAND, ha="right", va="center",
                arrowprops=dict(arrowstyle="-", color=LIGAND, lw=0.7))

    # The row of names goes **below**, on the shared baseline — except the
    # promoter's, which goes above. Two long names centred on two narrow
    # neighbouring glyphs collide, and the promoter is the one glyph tall
    # enough to carry its own callout clear of everything. That is the whole
    # reason `label` hugs its glyph and `tick` shares a baseline.
    for a in track.anchors("tick"):
        if a.meta.get("label") and a.meta["name"] != "promoter":
            _label(ax, a, a.meta["label"], gap=0.06)
    # Left-aligned rather than centred: a centred name on a 0.30-wide glyph
    # reaches back under the protein bound beside it. Running it rightwards
    # puts it over the empty air above the coding sequence.
    _label(ax, track.anchor("label", name="promoter"), "minimal promoter",
           gap=0.05, ha="left")
    _label(ax, cup2.anchor("tag"), "Gal4-TAD", gap=0.04)
    _label(ax, cup2.anchor("wall", deg=180.0), "CUP2", gap=0.06,
           color=PROTEIN, ha="right", va="center")

    bd.fit(ax, track.points + cup2.points, pad=0.34)
    return fig, "construct.png"


# ---------------------------------------------------------------------------
# blueprint.png — what a track actually does
# ---------------------------------------------------------------------------

def blueprint():
    """What a track actually does, in two panels.

    Two, not three, and side by side rather than stacked. A track is a wide,
    short object: three equal-aspect rows of one came out as a column of
    drawings with a third of each row white on both sides, because an axes
    that is far wider than its data shrinks its own box and leaves the
    margin. The left panel is a schematic and says so by dropping the equal
    aspect; the right one is the drawing and keeps it.
    """
    track, _ = _system()
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 2.3), dpi=150)

    # -- 1. the cursor ------------------------------------------------------
    ax = axes[0]
    spans = track.spans
    ax.set_aspect("auto")
    for i, ((x0, x1), glyph) in enumerate(zip(spans, track.glyphs,
                                              strict=True)):
        ax.add_patch(plt.Rectangle((x0, -0.5), x1 - x0, 1.0, lw=0.9,
                                   edgecolor=INK, facecolor="none"))
        # Names above the boxes rather than inside them: "terminator" is ten
        # characters and its box is 0.18 wide, so an inside label overflows
        # the very box that is meant to be showing its width.
        ax.text(0.5 * (x0 + x1), 0.62, glyph.name, ha="center", va="bottom",
                fontsize=8, color=TEXT, rotation=0 if x1 - x0 > 0.25 else 30)
        ax.text(0.5 * (x0 + x1), 0.0, f"{glyph.width:.2f}", ha="center",
                va="center", fontsize=8, color=GREY)
        if i:
            prev = spans[i - 1][1]
            ax.add_patch(plt.Rectangle((prev, -0.5), x0 - prev, 1.0, lw=0,
                                       facecolor=GREY, alpha=0.30))
    ax.annotate("", xy=(0.0, 1.30), xytext=(track.length, 1.30),
                arrowprops=dict(arrowstyle="<->", color=GREY, lw=0.8))
    ax.text(0.5 * track.length, 1.36, f"length = {track.length:.2f}",
            ha="center", fontsize=8, color=GREY)
    ax.annotate(f"gap = {track.gap:g}",
                xy=(spans[0][1] + 0.5 * track.gap, -0.5),
                xytext=(spans[0][1] + 0.5 * track.gap, -0.92),
                ha="center", va="top", fontsize=8, color=GREY,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    ax.set_xlim(-0.12, track.length + 0.12)
    ax.set_ylim(-1.25, 1.72)
    ax.set_axis_off()
    ax.set_title("1 · a cursor advances by each glyph's own width",
                 fontsize=9.5, loc="left", color=TEXT)

    # -- 2. the drawing -----------------------------------------------------
    ax = axes[1]
    bd.canvas(ax=ax)
    track.draw(ax=ax, edge=INK, wall_lw=0.9)
    for x0, x1 in spans:
        ax.annotate("", xy=(x0, -0.30), xytext=(x1, -0.30),
                    arrowprops=dict(arrowstyle="<->", color=GREY, lw=0.7))
    for kind in ("label", "tick", "end"):
        for a in track.anchors(kind):
            ax.plot(*a.xy, "o", ms=2.8, color=GREY, zorder=6)
    ax.text(0.5 * track.length, -0.40,
            "label anchors hug each glyph · ticks share a baseline",
            ha="center", va="top", fontsize=8, color=GREY)
    ax.set_xlim(-track.lead - 0.08, track.length + track.lead + 0.08)
    ax.set_ylim(-0.62, 0.50)
    ax.set_title("2 · drawn, with the anchors it exposes", fontsize=9.5,
                 loc="left", color=TEXT)

    fig.tight_layout(w_pad=1.6)
    return fig, "blueprint.png"


# ---------------------------------------------------------------------------
# the variant sheets
# ---------------------------------------------------------------------------

def vocabulary():
    """The four glyphs, forward and reverse."""
    rows = [("forward", 1), ("reverse", -1)]
    fig, axes = plt.subplots(len(rows), 4, figsize=(9.0, 3.2), dpi=150)
    for r, (_name, strand) in enumerate(rows):
        glyphs = [Repeat(n=4), Promoter(strand=strand),
                  CDS(width=0.6, strand=strand), Terminator()]
        for c, glyph in enumerate(glyphs):
            ax = axes[r][c]
            bd.canvas(ax=ax)
            one = bd.Track([glyph], lead=0.16)
            one.draw(ax=ax, edge=INK, wall_lw=1.0)
            one.fit(ax, pad=0.10)
            ax.set_ylim(-0.42, 0.52)
            if not r:
                ax.set_title(glyph.name, fontsize=9, color=TEXT)
    fig.tight_layout(pad=0.4)
    # Row names after the layout, in figure coordinates: `bd.canvas` turns
    # the axis furniture off, so an `ylabel` on a drawing panel is invisible.
    for r, (name, _strand) in enumerate(rows):
        box = axes[r][0].get_position()
        fig.text(0.012, box.y0 + 0.5 * box.height, name, rotation=90,
                 va="center", ha="left", fontsize=8.5, color=TEXT)
    return fig, "vocabulary.png"


def repeats():
    """The operator at four repeat counts — the knob a stock icon fixes."""
    counts = (1, 2, 4, 8)
    fig, axes = plt.subplots(1, len(counts), figsize=(2.3 * len(counts), 1.7),
                             dpi=150)
    for ax, n in zip(axes, counts, strict=True):
        bd.canvas(ax=ax)
        track = bd.Track([Repeat(n=n), Promoter(), CDS(width=0.5)])
        track.draw(ax=ax, edge=INK, wall_lw=1.0)
        track.fit(ax, pad=0.08)
        ax.set_ylim(-0.34, 0.52)
        ax.set_title(f"n = {n}", fontsize=9, color=TEXT)
    fig.tight_layout(pad=0.3)
    return fig, "repeats.png"


def proteins():
    """The body: lobes, how far open, and how many domains."""
    cases = [("1 lobe", dict(lobes=1, tags=(90.0,))),
             ("2, open", dict(lobes=2, open_deg=64.0, tags=(35.0, 145.0))),
             ("2, closed", dict(lobes=2, open_deg=10.0, tags=(35.0, 145.0))),
             ("3 lobes", dict(lobes=3, open_deg=44.0, tags=(90.0,))),
             ("no domains", dict(lobes=2, open_deg=30.0))]
    fig, axes = plt.subplots(1, len(cases), figsize=(1.8 * len(cases), 2.4),
                             dpi=150)
    for i, (ax, (name, kw)) in enumerate(zip(axes, cases, strict=True)):
        bd.canvas(ax=ax)
        p = Protein(seed=i, **kw)
        p.draw(ax=ax, edge=PROTEIN, wall_lw=1.0)
        ax.plot(*p.anchor("cleft").xy, "o", ms=4.5, color=LIGAND, zorder=6)
        p.fit(ax, pad=0.16)
        ax.set_title(name, fontsize=9, color=TEXT)
    fig.tight_layout(pad=0.3)
    return fig, "proteins.png"


BUILDS = (construct, blueprint, vocabulary, repeats, proteins)


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

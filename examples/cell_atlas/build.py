"""The cell atlas: one shape, twelve cells a reader can name.

    python tools/build_gallery.py atlas

Nothing new was added to the library for this. Every drawing here is
`cells.Blob` with different keywords, which is the whole argument: the unit of
documentation is a variant, and a shape worth having is one that reaches
twelve recognisable cells without twelve classes.

On what these claim
-------------------
They are **cartoons keyed to what a reader recognises**, not measured
morphologies. A macrophage is drawn with pseudopodia and a lot of loose
cytoplasmic content because that is how a macrophage is drawn; nothing here
was traced off a micrograph, and none of the numbers came from one. The
library draws, and the figure's claims stay the author's — see
`docs/MILESTONES.md`.
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
GREY = PAL["neutral"]
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
SUBJECT = PAL["primary"]

plt.rcParams.update({
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
})


# ---------------------------------------------------------------------------
# the atlas itself
# ---------------------------------------------------------------------------
#
# Each entry is a name and the keywords that get there from the default
# `Blob`. Read the second column as the answer to "what makes this one that
# cell rather than the generic one" — anything not named here is the default,
# on purpose, so the diff is the definition.

ATLAS = [
    # Anucleate and empty. The degenerate case of `nucleus=None` is not
    # degenerate at all: it is a red cell.
    ("erythrocyte", dict(nucleus=None, nucleolus=None, organelles=0,
                         aspect=1.0, squareness=2.05, wobble=0.018,
                         wobble_n=4, seed=11)),
    # Also anucleate, but with granules in it, and small enough that the
    # wobble reads as a shape rather than as texture.
    ("platelet", dict(nucleus=None, nucleolus=None, organelles=5,
                      organelle_size=0.14, organelle_aspect=0.80,
                      organelle_sep=0.30, aspect=0.72, squareness=2.2,
                      wobble=0.055, wobble_n=4, seed=4)),
    # Nucleus nearly filling the cell, leaving a rim of cytoplasm — the one
    # cue that tells a lymphocyte from anything else its size.
    ("lymphocyte", dict(nucleus=0.70, nucleolus=0.0, nucleus_at=(-0.08, 0.05),
                        organelles=2, organelle_size=0.085,
                        organelle_sep=0.18, aspect=0.96, squareness=2.2,
                        wobble=0.020, seed=6)),
    # Pseudopodia and a cytoplasm full of vesicles. `protrusion_len` at 0.45
    # of the body radius is the boundary where a protrusion stops reading as
    # a microvillus and starts reading as the cell reaching.
    ("macrophage", dict(nucleus=0.30, nucleolus=0.30, organelles=9,
                        organelle_size=0.125, organelle_aspect=0.80,
                        organelle_sep=0.26, wobble=0.050, wobble_n=4,
                        protrusions=6, protrusion_len=0.45,
                        protrusion_width=0.155, protrusion_jitter=0.42,
                        seed=2)),
    # A spindle: flattened body, two poles. Two protrusions on a 180-degree
    # arc land at 0 and 180, which is what makes the poles opposite without
    # placing them by hand.
    ("fibroblast", dict(aspect=0.30, squareness=2.05, wobble=0.030,
                        nucleus=0.26, nucleus_aspect=0.55,
                        nucleus_at=(-0.06, 0.0), nucleolus=0.34,
                        organelles=4, organelle_size=0.090,
                        organelle_sep=0.30,
                        protrusions=2, protrusion_arc_deg=180.0,
                        protrusion_len=0.95, protrusion_width=0.058,
                        protrusion_jitter=0.30, seed=8)),
    # The same spindle *without* the poles, which is the whole visible
    # difference between the two at this size — so they are next to each
    # other, where that can be seen.
    ("smooth muscle", dict(aspect=0.22, squareness=2.4, wobble=0.016,
                           nucleus=0.17, nucleus_aspect=0.95,
                           nucleus_at=(0.0, 0.0), nucleolus=0.0,
                           organelles=0, seed=5)),
    # A cell that is mostly one lipid droplet: nothing in it, and the nucleus
    # squashed against the wall. The droplet is drawn by *absence* — there is
    # no second body knob, and inventing one for a single cell type would be
    # the wrong trade. See the gallery page on what this cannot say.
    ("adipocyte", dict(nucleus=0.14, nucleolus=0.0,
                       nucleus_at=(-0.78, 0.12), organelles=0,
                       aspect=1.0, squareness=2.25, wobble=0.016,
                       wobble_n=4, seed=9)),
    # Big, round, and the one cell where the nucleolus is a headline feature.
    ("oocyte", dict(nucleus=0.40, nucleolus=0.44, nucleus_at=(-0.12, 0.10),
                    organelles=14, organelle_size=0.095,
                    organelle_aspect=0.85, organelle_sep=0.185,
                    aspect=0.98, squareness=2.1, wobble=0.018, seed=1)),
    # One protrusion, very long and very thin. `protrusion_jitter=0` is right
    # here and wrong nearly everywhere else: a single part cannot repeat, so
    # there is nothing for the jitter to break up.
    ("spermatozoon", dict(nucleus=0.62, nucleolus=0.0, nucleus_at=(0.0, 0.06),
                          organelles=0, aspect=0.66, squareness=2.3,
                          wobble=0.015,
                          protrusions=1, protrusion_start_deg=268.0,
                          protrusion_len=2.6, protrusion_width=0.048,
                          protrusion_jitter=0.0,
                          geom_kw=dict(wave_amp=0.055, wave_n=1.9),
                          seed=7)),
    # Deliberately the most irregular thing here: heavy wobble at a low cycle
    # count reads as a cell changing shape, where the same wobble at a high
    # count reads as a crenellated membrane.
    ("amoeba", dict(nucleus=0.26, nucleolus=0.38, organelles=7,
                    organelle_size=0.115, organelle_sep=0.24,
                    wobble=0.075, wobble_n=3, aspect=0.92, squareness=2.3,
                    protrusions=3, protrusion_len=0.70,
                    protrusion_width=0.215, protrusion_jitter=0.50,
                    seed=3)),
    # Many long thin protrusions over a narrow arc: a ciliated face, and the
    # rest of the membrane bare.
    ("ciliated cell", dict(nucleus=0.28, nucleolus=0.30, organelles=5,
                           organelle_size=0.105, organelle_sep=0.26,
                           aspect=1.0, squareness=2.5, wobble=0.020,
                           protrusions=13, protrusion_arc_deg=115.0,
                           protrusion_start_deg=33.0, protrusion_len=0.62,
                           protrusion_width=0.036, protrusion_jitter=0.22,
                           seed=10)),
    # Squareness past 3.5 is the cheapest cue that a cell is walled rather
    # than membraned. It is a cue and not a wall — there is no second contour
    # here, which the page says out loud.
    ("plant cell", dict(squareness=3.9, aspect=0.82, wobble=0.010,
                        wobble_n=4, nucleus=0.23, nucleolus=0.34,
                        nucleus_at=(-0.56, -0.44), organelles=8,
                        organelle_size=0.125, organelle_aspect=0.62,
                        organelle_sep=0.28, seed=0)),
]


def atlas():
    """Twelve cells, one class, no new code."""
    fig, _ = bd.contact_sheet(
        factory=bd.cells.Blob,
        variants=[kw for _, kw in ATLAS],
        labels=[name for name, _ in ATLAS],
        cols=6, cell_in=1.5, aspect=1.0, pad=0.16,
        draw_kw=dict(edge=SUBJECT),
    )
    return fig, "atlas.png"


# ---------------------------------------------------------------------------
# how each one is reached
# ---------------------------------------------------------------------------

def derivations():
    """From the default `Blob` to a named cell, a few knobs at a time.

    Each cell is captioned with what was *added* to the one on its left, so
    the row reads as a derivation rather than as four unrelated settings. The
    captions are per-cell rather than per-column because the steps are not the
    same kind of step in every row, and pretending otherwise would be the
    honest column headers lying about one of them:

    **The fibroblast's second step could not be a body change alone.** At
    `aspect=0.30` the body is 0.165 local units half-tall and the default
    nucleus is 0.187 in radius, so it would stand through the wall — and the
    default six organelles do not fit either, which is not a guess:
    `scatter_in` raises rather than drawing fewer. A flatter cell holds less,
    so its contents come down with it, and the caption says so.
    """
    rows = [
        ("macrophage", 2, [
            ("wobble=0.05, n=4",
             dict(wobble=0.050, wobble_n=4)),
            ("9 organelles, smaller",
             dict(organelles=9, organelle_size=0.125, organelle_aspect=0.80,
                  organelle_sep=0.26, nucleus=0.30, nucleolus=0.30)),
            ("6 pseudopodia",
             dict(protrusions=6, protrusion_len=0.45, protrusion_width=0.155,
                  protrusion_jitter=0.42)),
        ]),
        ("fibroblast", 8, [
            ("aspect=0.30 + contents to fit",
             dict(aspect=0.30, squareness=2.05, nucleus=0.26,
                  nucleus_aspect=0.55, organelles=4, organelle_size=0.090,
                  organelle_sep=0.30)),
            ("wobble, nucleolus, off-centre",
             dict(wobble=0.030, nucleolus=0.34, nucleus_at=(-0.06, 0.0))),
            ("2 poles, 180° apart",
             dict(protrusions=2, protrusion_arc_deg=180.0,
                  protrusion_len=0.95, protrusion_width=0.058,
                  protrusion_jitter=0.30)),
        ]),
        ("ciliated cell", 10, [
            ("aspect=1.0, squareness=2.5",
             dict(aspect=1.0, squareness=2.5, wobble=0.020)),
            ("nucleus=0.28, 5 organelles",
             dict(nucleus=0.28, nucleolus=0.30, organelles=5,
                  organelle_size=0.105, organelle_sep=0.26)),
            ("13 cilia over 115°",
             dict(protrusions=13, protrusion_arc_deg=115.0,
                  protrusion_start_deg=33.0, protrusion_len=0.62,
                  protrusion_width=0.036, protrusion_jitter=0.22)),
        ]),
    ]

    variants, labels = [], []
    for _, seed, steps in rows:
        kw = dict(seed=seed)
        variants.append(dict(kw))
        labels.append("bd.cells.Blob()")
        for caption, step in steps:
            kw.update(step)
            variants.append(dict(kw))
            labels.append(caption)

    fig, _ = bd.contact_sheet(
        factory=bd.cells.Blob, variants=variants, labels=labels, cols=4,
        cell_in=1.6, aspect=1.0, pad=0.16, label_size=6.5,
        row_labels=[name for name, _, _ in rows],
        draw_kw=dict(edge=SUBJECT),
    )
    return fig, "derivations.png"


# ---------------------------------------------------------------------------
# one number, true relative size
# ---------------------------------------------------------------------------
#
# Textbook round numbers, not measurements — enough to make the point that
# `scale` is one knob and that the cells in a figure can be honest about size
# relative to each other without anything being redrawn.

SIZES_UM = [("platelet", 3.0), ("erythrocyte", 8.0), ("lymphocyte", 10.0),
            ("ciliated cell", 20.0), ("macrophage", 21.0)]
UM_PER_UNIT = 10.0          # one local unit is ten micrometres


def scale_row(gap=0.30):
    """The cells of `SIZES_UM`, placed left to right at true relative size.

    Separate from `to_scale` so the review pass can measure the same
    placement the drawing uses rather than a second copy of the arithmetic —
    the first version of this figure spaced the row on body radii and buried
    one cell's wall under the next one's cilia, and a check written against
    its own layout would have agreed with it.

    Returns `[(name, micrometres, placed Blob), ...]`.
    """
    by_name = dict(ATLAS)
    x, placed = 0.0, []
    for name, um in SIZES_UM:
        # `Blob.radius` is the body's semi-axis in local units, so the scale
        # that makes a cell `um` across is set by that and nothing else. One
        # number, and every part of the cell follows it — which is the whole
        # claim being made here.
        cell = bd.cells.Blob(**by_name[name])
        scale = (um / UM_PER_UNIT) / (2.0 * cell.radius)
        cell = cell.moved(at=(0.0, 0.0), scale=scale)
        # Space by the ink, not by the body. A ciliated cell 20 µm across
        # throws 27 µm of drawing, and a row laid out on body radii alone
        # overlapped by 0.52 local units before this was measured.
        ink = np.vstack([np.asarray(p) for p in cell.points])
        x += -ink[:, 0].min()
        placed.append((name, um, cell.moved(at=(x, 0.0), scale=scale)))
        x += ink[:, 0].max() + gap
    return placed


def to_scale():
    """The same cells, sized against each other by one number each."""
    fig, ax = bd.canvas(figsize=(7.6, 2.5))

    right = 0.0
    for name, um, cell in scale_row():
        cell.draw(ax=ax, edge=SUBJECT, wall_lw=0.9,
                  gid=name.replace(" ", "_"))
        ink = np.vstack([np.asarray(p) for p in cell.points])
        right = max(right, ink[:, 0].max())
        # Under the drawing, not under the body, or a caption lands inside
        # the cilia of the cell it names.
        ax.text(cell.at[0], ink[:, 1].min() - 0.10, f"{name}\n{um:g} µm",
                fontsize=7.5, color=GREY, ha="center", va="top")
    ax.set_xlim(-0.15, right + 0.15)

    # A 10 um bar. `per_unit` is the whole of it: the library does the
    # division, and the butt cap — a projecting cap would make the bar
    # longer than the length it claims.
    bd.scalebar(ax=ax, at=(0.0, 1.30), size=10, per_unit=UM_PER_UNIT,
                units="µm", fontsize=8, color=INK)
    ax.set_ylim(-1.35, 1.65)
    return fig, "to_scale.png"


BUILDS = (atlas, derivations, to_scale)


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

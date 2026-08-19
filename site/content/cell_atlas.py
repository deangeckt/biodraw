"""Content for the cell atlas page."""

PAGE = dict(
    title="Cell atlas",
    category="Cells & tissues",
    order=1,
    build_pattern="atlas",
    tagline="Twelve cells a reader can name, from one class and no new code. "
            "The unit of documentation is a variant, and this is what that "
            "buys.",
    hero="atlas.png",
    hero_alt="Twelve cell types drawn from one shape",
    shapes=["cells.Blob"],
    keywords=[
              "erythrocyte",
              "red blood cell",
              "platelet",
              "lymphocyte",
              "macrophage",
              "fibroblast",
              "smooth muscle",
              "adipocyte",
              "oocyte",
              "spermatozoon",
              "amoeba",
              "cilia",
              "plant cell",
              "cell types",
              "scale bar",
    ],

    intro=[
        "Every drawing on this page is `cells.Blob` with different keywords. "
        "Nothing was added to the library to make it, and that is the "
        "argument: a shape worth having reaches a dozen recognisable cells "
        "without a dozen classes.",
        "**They are cartoons keyed to what a reader recognises, not measured "
        "morphologies.** A macrophage is drawn with pseudopodia and a busy "
        "cytoplasm because that is how a macrophage is drawn. Nothing here "
        "was traced off a micrograph. The library draws; what a figure "
        "claims stays yours.",
    ],

    sections=[
        dict(
            title="Twelve cells, one class",
            images=[dict(src="atlas.png",
                         alt="Twelve cell types drawn from cells.Blob")],
            body=[
                "Read each of these as a diff against the default `Blob`. "
                "Anything not named below is left at its default on purpose, "
                "so the keywords that appear *are* the definition of that "
                "cell.",
            ],
            code="""
import biodraw as bd

# a red cell: the anucleate case is not degenerate, it is a cell type
rbc = bd.cells.Blob(
    nucleus=None,           # no nucleus, and so no nucleolus either
    organelles=0,           # nor anything loose in the cytoplasm
    aspect=1.0,             # round
    squareness=2.05,        # very nearly a plain ellipse
    wobble=0.018,           # just enough that it is not an equation
    seed=11,
)

# a macrophage: the same class, reaching
mac = bd.cells.Blob(
    organelles=9,           # a busy cytoplasm
    organelle_size=0.125,   # smaller, so nine of them fit
    organelle_sep=0.26,     # ...and closer together
    wobble=0.050,           # an irregular outline
    protrusions=6,          # pseudopodia
    protrusion_len=0.45,    # x the body radius — past ~0.4 it reads as reaching
    protrusion_width=0.155, # thick enough to be a lobe, not a hair
    seed=2,
)
""",
        ),

        dict(
            title="How each one is reached",
            images=[dict(src="derivations.png",
                         alt="Three cells derived from the default Blob in "
                             "three steps each")],
            body=[
                "Left to right: the default `Blob`, then the body, then the "
                "contents, then the membrane. That is the order to work in "
                "when you want a cell this page does not have — get the "
                "silhouette, fill it, then decide what comes out of it.",
                "**The fibroblast's second step could not be a body change "
                "alone**, and the caption says so rather than hiding it. At "
                "`aspect=0.30` the body is 0.165 local units half-tall while "
                "the default nucleus is 0.187 in radius, so it would stand "
                "straight through the wall — and the default six organelles "
                "do not fit either. That second part is not a judgement "
                "call: `scatter_in` raises. A flatter cell holds less, and "
                "its contents have to come down with it.",
            ],
        ),

        dict(
            title="One number, true relative size",
            images=[dict(src="to_scale.png",
                         alt="Five cells drawn at their true relative sizes "
                             "with a 10 micrometre bar")],
            body=[
                "`scale` multiplies every local length in the shape, so one "
                "number resizes a cell coherently — the wall, the nucleus, "
                "the organelles and the protrusions all follow it, and "
                "nothing has to be re-tuned. That is what lets a panel be "
                "honest about size without anything being redrawn.",
                "The round numbers here are textbook ones, not measurements. "
                "An adipocyte at ~100 µm would be four times the width of "
                "the widest cell shown.",
            ],
            code="""
UM_PER_UNIT = 10.0                      # one local unit is ten micrometres

cell = bd.cells.Blob(**{...})           # any of the twelve above
cell = cell.moved(
    at=(x, 0.0),
    scale=(diameter_um / UM_PER_UNIT) / (2 * cell.radius),
)
""",
            after=[
                "Lay the row out on the **ink**, not on the body. A ciliated "
                "cell 20 µm across throws 27 µm of drawing, and spacing this "
                "row on body radii alone buried one cell's wall under the "
                "next one's cilia by 0.52 local units. `shape.points` is "
                "every drawn vertex, which is what the spacing is measured "
                "from.",
            ],
        ),

        dict(
            title="What this shape cannot say",
            body=[
                "Worth naming, because the honest answer to \"can it draw "
                "X\" is sometimes no, and a page that only shows successes "
                "is not documentation:",
                "**A lobed nucleus.** A neutrophil's nucleus is three or "
                "four connected lobes, and `nucleus` is one ring. There is "
                "no lobe count and adding one for a single cell type would "
                "be the wrong trade.",
                "**A cell wall as a second contour.** The plant cell above "
                "leans on `squareness=3.9` as a cue that it is walled. A "
                "real wall is a second closed outline outside the membrane, "
                "which is a `Layer` this shape does not build.",
                "**A bud, or anything with two bodies.** A budding yeast is "
                "two joined cells; `Blob` is one.",
                "**Contents confined to part of the cytoplasm** — the apical "
                "mucin granules of a goblet cell, say. `core.scatter` takes "
                "exclusion regions, but `Blob` does not expose them, so "
                "organelles spread through the whole cell.",
            ],
        ),
    ],
)

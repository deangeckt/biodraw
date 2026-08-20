"""Content for the cell atlas page.

*What this shape cannot say* used to be four paragraphs here. It is a table on
the atlas section now — the same four limitations, as data rather than an
essay. A page that only shows successes is not documentation, so it stays on
the page; it just stopped being prose.
"""

PAGE = dict(
    title="Cell atlas",
    category="Cells & tissues",
    order=1,
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
        "Every drawing here is `cells.Blob` with different keywords — nothing "
        "was added to the library to make it. **They are cartoons keyed to "
        "what a reader recognises, not measured morphologies.**",
    ],

    sections=[
        dict(
            title="Twelve cells, one class",
            images=[dict(src="atlas.png",
                         alt="Twelve cell types from cells.Blob. Read each as "
                             "a diff against the default — what is unnamed "
                             "is deliberate.")],
            table=dict(
                head=["what it cannot say", "why"],
                rows=[
                    ["a lobed nucleus",
                     "`nucleus` is one ring; a neutrophil's is three or four "
                     "connected lobes"],
                    ["a cell wall as a second contour",
                     "the plant cell leans on `squareness=3.9` instead; a "
                     "real wall is a `Layer` this shape does not build"],
                    ["a bud, or two bodies",
                     "a budding yeast is two joined cells, `Blob` is one"],
                    ["contents in part of the cytoplasm",
                     "`core.scatter` takes exclusion regions, `Blob` does not "
                     "expose them"],
                ],
            ),
        ),

        dict(
            title="Drawing one",
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
    protrusions=6,          # pseudopodia
    protrusion_len=0.45,    # x the body radius — past ~0.4 it reads as reaching
    wobble=0.050,           # an irregular outline
    seed=2,
)

# true relative size is one number: `scale` multiplies every local length
UM_PER_UNIT = 10.0
mac = mac.moved(scale=(21.0 / UM_PER_UNIT) / (2 * mac.radius))
""",
        ),

        dict(
            title="How each one is reached",
            images=[dict(src="derivations.png",
                         alt="Three cells derived in three steps each: the "
                             "silhouette, then the contents, then the "
                             "membrane. Work in that order.")],
        ),

        dict(
            title="One number, true relative size",
            images=[dict(src="to_scale.png",
                         alt="Five cells at true relative size, 10 µm bar. "
                             "Lay a row out on the ink, not the body.")],
        ),
    ],
)

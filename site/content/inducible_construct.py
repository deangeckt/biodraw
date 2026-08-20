"""Content for the inducible construct page — the first genetics card.

The parts list came off figure 1 of doi.org/10.1016/j.tibtech.2023.03.007,
which Dean supplied as a screenshot, and not off the field. Worth keeping in
mind when reading the page: `docs/PLAN.md` had argued genetics on double
helices, plasmid maps and exon structure, and the figure contains none of
them. Taking the inventory off the picture is the step this repository keeps
proving it cannot skip.
"""

PAGE = dict(
    title="Inducible construct",
    category="Genetics",
    order=0,
    tagline="A construct is glyphs laid along a line, each taking its own "
            "width — and the protein that switches it on.",
    hero="construct.png",
    hero_alt="A copper-inducible expression construct with CUP2 bound to "
             "its operator",
    shapes=["Track", "genetics.Repeat", "genetics.Promoter", "genetics.CDS",
            "genetics.Terminator", "genetics.Protein"],
    keywords=[
        "genetics",
        "construct",
        "plasmid",
        "sbol",
        "promoter",
        "operator",
        "cds",
        "gene",
        "terminator",
        "repeat",
        "inducible",
        "expression",
        "protein",
        "domain",
        "track",
        "ideogram",
        "domain map",
    ],

    intro=[
        "Every knob on this page is a count or a length somebody currently "
        "draws by hand: your repeat number, your insert, your domain list.",
    ],

    sections=[
        dict(
            title="The vocabulary",
            images=[dict(src="vocabulary.png",
                         alt="Four glyphs, forward and reverse. `strand=-1` "
                             "mirrors one about its own span.")],
        ),

        dict(
            title="How many repeats",
            images=[dict(src="repeats.png",
                         alt="`4xUAS`, `(etr)8` and `(C120)5` are one glyph "
                             "at three settings of `n`.")],
        ),

        dict(
            title="The protein it encodes",
            images=[dict(src="proteins.png",
                         alt="Lobes, how far open, and how many domains. The "
                             "ligand is a dot at the `cleft` anchor.")],
        ),

        dict(
            title="What a track does",
            images=[dict(
                src="blueprint.png",
                alt="The layout, and the drawing it produces",
                notes=[
                    "**A glyph brings its own width**; the track only "
                    "advances a cursor and leaves `gap` between neighbours.",
                    "**The anchors are the labels' business.** No text is "
                    "drawn by the library — a name is the author's claim.",
                ])],
        ),

        dict(
            title="Drawing one",
            code="""
import biodraw as bd
from biodraw.genetics import CDS, Promoter, Protein, Repeat, Terminator

track = bd.Track([
    Repeat(n=4, label="CBS operator"),   # n is the biology: 4xUAS, (etr)8
    Promoter(label="minimal promoter"),  # strand=-1 turns it round
    CDS(width=0.92, label="GOI"),        # the point says which way it reads
    Terminator(),
], gap=0.09)                             # page between neighbours

cup2 = Protein(
    lobes=2,                # 1 is an oval, 2 a clamshell, 3+ a complex
    open_deg=30.0,          # how far the lobes hinge apart
    tags=(42.0,),           # a domain tag leaves the body at this angle
    at=(0.17, 0.52),        # over the operator — that is your claim
    scale=0.62,
)
for shape in (track, cup2):
    shape.draw(ax=ax, wall_lw=1.0)

# The ligand is a dot at an anchor, and the labels are your own text.
ax.plot(*cup2.anchor("cleft").xy, "o", ms=5.5)
for a in track.anchors("tick"):
    ax.text(*a.offset(0.06), a.meta["label"], ha="center", va="top")
""",
        ),
    ],
)

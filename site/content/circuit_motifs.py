"""Content for the circuit motifs page."""

PAGE = dict(
    title="Circuit motifs",
    category="Circuits",
    order=1,
    build_pattern="motifs",
    tagline="Cells wired to each other — which is what everything else in "
            "this library was building toward.",
    hero="column.png",
    hero_alt="A cortical column",
    shapes=["neuro.Pyramidal", "neuro.Basket", "connect_tree"],
    keywords=[
              "circuit",
              "motif",
              "column",
              "cortical",
              "layer",
              "excitation",
              "inhibition",
              "palette",
              "colorblind",
              "mono",
    ],

    intro=[
        "A cortical column: layer II/III cells with forked apicals, one large "
        "layer V cell, a basket cell contacting it perisomatically, and the "
        "layer V output leaving as a projection. The layer rules are the only "
        "horizontal lines — **nothing else sits on a baseline by accident.**",
    ],

    sections=[
        dict(
            title="Six motifs",
            images=[dict(src="motifs.png",
                         alt="Six circuit motifs. One colour and one mark per "
                             "claim across all six, so the key is three lines.")],
            table=dict(
                head=["", "claim"],
                rows=[
                    ["red, arrowhead", "excitation"],
                    ["blue, bar", "inhibition"],
                    ["`'open'`", "the same contact, **not** asserted"],
                ],
            ),
        ),

        dict(
            title="Drawing one",
            code="""
import biodraw as bd

pyr = bd.neuro.Pyramidal(spines=6, basal=2, at=(-1.9, 0.0), scale=0.55)
bas = bd.neuro.Basket(dendrites=6, forks=None, at=(0.0, -0.3), scale=0.85)
for cell in (pyr, bas):
    cell.draw(ax=ax, wall_lw=0.9)

bd.connect(
    ax=ax,
    source=pyr.anchor("soma", nearest=bas.at),   # the flank facing the target
    target=bas.anchor("soma", nearest=pyr.at),   # ...and the one facing back
    gap=0.05,               # clearance at the wall, in local units
    drop=0.15,              # drop clear of the cell before running
    rad=0.07,               # bow; positive always bows up
    endcap="arrow",         # the claim: excitation
)

p = bd.style.palette.get("colorblind")   # or 'default', or 'mono'
""",
        ),

        dict(
            title="The same pair, four claims",
            images=[dict(src="claims.png",
                         alt="Four claims. Identical cells and geometry — "
                             "only the endcap and the colour change.")],
        ),

        dict(
            title="Three palettes",
            images=[dict(src="palettes.png",
                         alt="One circuit, three palettes. `mono` is the "
                             "check that a drawing still reads with its "
                             "colours taken away.")],
            table=dict(
                head=["palette", "for"],
                rows=[
                    ["`default`", "what the reference figure was drawn in"],
                    ["`colorblind`", "Okabe-Ito. Use this for print"],
                    ["`mono`", "greyscale journals, and as the check above"],
                ],
            ),
        ),
    ],
)

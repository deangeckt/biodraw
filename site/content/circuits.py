"""Content for the circuits page — wiring and circuit motifs, merged.

*"circuit motifs and wiring should be merged into one card in the main
page."* They were two cards for one subject: wiring was the connector and its
endcaps, motifs was those connectors between cells, and a reader looking for
"how do I draw a projection from A to B" had no way to tell which card held
it. One card, one page, both example folders — the site builder takes an
image as `<example>/<file>` precisely so a page and a build folder no longer
have to be the same thing.

The two prose sections wiring used to carry — *where contacts land is yours
to say* and *why there is no axon class* — were cut when the pages went to a
catalog. Neither was lost: the first is `docs/PLAN.md` and the placement
engine's entry in `docs/STATE.md`, the second is the module docstring of
`biodraw/neuro/__init__.py`, where someone reaching for `neuro.Axon` will
actually meet it.
"""

PAGE = dict(
    title="Circuits & wiring",
    category="Neuroscience",
    order=8,
    examples=["circuit_motifs", "wiring"],
    tagline="Cells wired to each other: the connectors, the endcaps that say "
            "what a connection is, and the motifs they build.",
    hero="circuit_motifs/column.png",
    hero_alt="A cortical column",
    shapes=["connect", "connect_tree", "connectors.endcap", "neuro.Pyramidal",
            "neuro.Basket"],
    keywords=[
              "circuit",
              "motif",
              "column",
              "cortical",
              "layer",
              "excitation",
              "inhibition",
              "connector",
              "endcap",
              "arrow",
              "bar",
              "synapse",
              "contact",
              "axon",
              "projection",
              "arbor",
              "palette",
              "colorblind",
              "mono",
    ],

    intro=[
        "The mark at the far end is a claim, not decoration. Use one meaning "
        "per figure and say which in the key.",
    ],

    sections=[
        dict(
            title="Six motifs",
            images=[dict(src="circuit_motifs/motifs.png",
                         alt="Six circuit motifs. One colour and one mark per "
                             "claim across all six, so the key is three "
                             "lines.")],
            table=dict(
                head=["", "claim"],
                rows=[
                    ["red, arrowhead", "excitation"],
                    ["green, bar", "inhibition"],
                    ["`'open'`", "the same contact, **not** asserted"],
                ],
            ),
        ),

        dict(
            title="The same pair, four claims",
            images=[dict(src="circuit_motifs/claims.png",
                         alt="Four claims. Identical cells and geometry — "
                             "only the endcap and the colour change.")],
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

# One process that leaves and *branches*, rather than several strokes.
bd.connect_tree(
    ax=ax,
    source=bas.anchor("soma", deg=270.0),
    targets=[cell.anchor("soma", nearest=bas.at) for cell in row],
    fork=0.45,              # how far along the shared stem it splits
    spread=0.4,             # how far each branch turns at the fork
    endcap="bar",           # the claim: inhibition
)

# Which compartment a contact lands on is your claim, not the library's.
targets = [pyr.anchor("soma", side=1, t=t) for t in (0.24, 0.42, 0.60)]
""",
        ),

        dict(
            title="Endcaps",
            images=[dict(src="wiring/endcaps.png",
                         alt="The five endcaps. Both ends are anchors, so a "
                             "clearance means the same at any angle on any "
                             "shape.")],
            table=dict(
                head=["endcap", "what it says"],
                rows=[
                    ["`'dot'`", "a synapse, a contact, a junction"],
                    ["`'open'`", "the same kind of contact, not asserted"],
                    ["`'bar'`", "inhibition, a block"],
                    ["`'arrow'`", "flow, direction, causation"],
                    ["`None`", "the line simply reaches the wall"],
                ],
            ),
        ),

        dict(
            title="Connector shape",
            images=[dict(src="wiring/connector_shapes.png",
                         alt="Twelve connector shapes: `drop` clears the "
                             "cell, `rad` bows the run, `smooth` widens the "
                             "turn out of the descent.")],
        ),

        dict(
            title="One source, several targets",
            images=[dict(src="wiring/one_to_many.png",
                         alt="Separate strokes versus one arbor. Separate "
                             "strokes run side by side and cross on a "
                             "staggered row.")],
        ),

        dict(
            title="A bus, when several targets share a source",
            images=[dict(src="wiring/bus.png",
                         alt="Curves fan and cross; risers off one rail read "
                             "as sharing a source, and weight marks the weak "
                             "one.")],
        ),

        dict(
            title="Three palettes",
            images=[dict(src="circuit_motifs/palettes.png",
                         alt="One circuit, three palettes. `mono` is the "
                             "check that a drawing still reads with its "
                             "colours taken away.")],
            table=dict(
                head=["palette", "for"],
                rows=[
                    ["`default`", "red excitatory, green inhibitory"],
                    ["`colorblind`", "Okabe-Ito. Use this for print"],
                    ["`mono`", "greyscale journals, and as the check above"],
                ],
            ),
        ),
    ],
)

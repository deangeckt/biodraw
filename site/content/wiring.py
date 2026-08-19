"""Content for the wiring page.

Rewritten from `examples/wiring/README.md`, which had gone stale: it still
documented `neuro.Axon` — removed a session earlier — and pointed at five
images of it that were not on disk. Those sections are gone here. A projection
is now a line with a mark on the end; see `docs/PLAN.md`, drawing rule 4.

The two prose sections this page used to carry — *where contacts land is yours
to say* and *why there is no axon class* — were cut when the pages went to a
catalog. Neither was lost: the first is `docs/PLAN.md` and the placement
engine's entry in `docs/STATE.md`, the second is the module docstring of
`biodraw/neuro/__init__.py`, where someone reaching for `neuro.Axon` will
actually meet it.
"""

PAGE = dict(
    title="Wiring",
    category="Circuits",
    order=0,
    build_pattern="wiring",
    tagline="Everything needed to connect one cell to another: connectors, "
            "and the endcaps that say what a connection is.",
    hero="circuit.png",
    hero_alt="A wired circuit panel",
    shapes=["connect", "connect_tree", "connectors.endcap"],
    keywords=[
              "connector",
              "endcap",
              "arrow",
              "bar",
              "synapse",
              "contact",
              "axon",
              "projection",
              "arbor",
              "circuit",
    ],

    intro=[
        "The mark at the far end is a claim, not decoration. Use one meaning "
        "per figure and say which in the key.",
    ],

    sections=[
        dict(
            title="Endcaps",
            images=[dict(src="endcaps.png",
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
            title="Drawing one",
            code="""
import biodraw as bd

bd.connect(
    ax=ax,
    source=basket.anchor("soma", deg=270.0),
    target=pyramidal.anchor("soma", nearest=basket.at),
    gap=0.04,               # clearance at the target, in local units
    drop=0.30,              # straight descent before the run begins
    rad=0.05,               # bow; positive always bows *up*
    endcap="bar",           # the claim
)

# One process that leaves and *branches*, rather than several strokes.
bd.connect_tree(
    ax=ax,
    source=basket.anchor("soma", deg=270.0),
    targets=[cell.anchor("soma", nearest=basket.at) for cell in row],
    fork=0.45,              # how far along the shared stem it splits
    spread=0.4,             # how far each branch turns at the fork
    endcap="bar",
)

# Which compartment a contact lands on is your claim, not the library's.
targets = [pyr.anchor("soma", side=1, t=t) for t in (0.24, 0.42, 0.60)]
""",
        ),

        dict(
            title="Connector shape",
            images=[dict(src="connector_shapes.png",
                         alt="Twelve connector shapes: `drop` clears the "
                             "cell, `rad` bows the run, `smooth` widens the "
                             "turn out of the descent.")],
        ),

        dict(
            title="One source, several targets",
            images=[dict(src="one_to_many.png",
                         alt="Separate strokes versus one arbor. Separate "
                             "strokes run side by side and cross on a "
                             "staggered row.")],
        ),
    ],
)

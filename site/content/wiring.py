"""Content for the wiring page.

Rewritten from `examples/wiring/README.md`, which had gone stale: it still
documented `neuro.Axon` — removed a session earlier — and pointed at five
images of it that were not on disk. Those sections are gone here. A projection
is now a line with a mark on the end; see `docs/PLAN.md`, drawing rule 4.
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
        "Two cell types, one branching arbor, and four contacts placed "
        "perisomatically — which is what a basket cell does, and the reason "
        "it is drawn as a basket cell.",
    ],

    sections=[
        dict(
            title="Endcaps",
            images=[dict(src="endcaps.png", alt="The five endcaps")],
            body=["The mark at the far end is a claim, not decoration."],
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
            code="""
bd.connect(
    ax=ax,
    source=basket.anchor("soma", deg=270.0),
    target=pyramidal.anchor("soma", nearest=basket.at),
    gap=0.04,               # clearance at the target, in local units
    drop=0.30,              # straight descent before the run begins
    rad=0.05,               # bow; positive always bows *up*
    endcap="bar",           # the claim
)
""",
            after=[
                "Use one meaning per figure and say which in the key.",
                "Because both ends are **anchors**, the clearance means the "
                "same thing at any angle and on any shape. That is the whole "
                "reason a stand-off never has to be tuned per contact per "
                "figure.",
            ],
        ),

        dict(
            title="Connector shape",
            images=[dict(src="connector_shapes.png",
                         alt="Twelve connector shapes")],
            body=[
                "**`drop`** — a process does not set off toward its target "
                "the moment it leaves the cell; it drops clear of the cell's "
                "own dendrites first.",
                "**`rad`** — how far the run bows. Positive bows *up* "
                "whichever way the connector runs, so a row wired in both "
                "directions does not come out with half its lines sagging "
                "into whatever is below.",
                "**`smooth`** — how wide the turn out of the descent is. At 0 "
                "the join is a corner, and a schematic process that turns a "
                "hard corner reads as a circuit diagram's wire.",
            ],
        ),

        dict(
            title="One source, several targets",
            images=[dict(src="one_to_many.png",
                         alt="Separate strokes versus one arbor")],
            body=[
                "Drawn as separate strokes, two outputs run side by side for "
                "as far as their targets agree — which reads as two axons — "
                "and on a staggered row they cross, since the lower target's "
                "line starts above the higher one's. One process that leaves "
                "and *branches* is both what the cell has and what a drawn "
                "arbor looks like.",
            ],
            code="""
bd.connect_tree(
    ax=ax,
    source=basket.anchor("soma", deg=270.0),
    targets=[cell.anchor("soma", nearest=basket.at) for cell in row],
    fork=0.45,              # how far along the shared stem it splits
    spread=0.4,             # how far each branch turns at the fork
    endcap="bar",
)
""",
        ),

        dict(
            title="Where contacts land is yours to say",
            body=[
                "Deliberately **not** a feature. This library draws the cell "
                "and hands you the places on it; which compartment a contact "
                "lands on is a claim about the circuit, and the author makes "
                "it.",
            ],
            code="""
targets = [pyr.anchor("soma", side=1, t=t) for t in (0.24, 0.42, 0.60)]
""",
            after=[
                "An earlier version had an allocator — \"eight contacts, five "
                "on spines, two on shaft, one on soma\" — and it was removed. "
                "Once a cell is drawn, marking it is a line of matplotlib "
                "against anchors that are already public, and a general "
                "drawing library has no business holding one paper's argument "
                "about where synapses go.",
                "What survives is the part that really is drawing: a "
                "connector has to *end* in something, and whether that mark "
                "is an arrowhead or a bar is how the figure says excitation "
                "or inhibition.",
            ],
        ),

        dict(
            title="Why there is no axon class",
            body=[
                "There was one: a tapered tube with Gaussian bouton swellings "
                "and collaterals sized by Rall. It worked, and it was "
                "removed.",
                "At the size an axon appears in a circuit panel it read as a "
                "fat beaded worm, and pulled the eye away from the cells it "
                "existed to connect. A line with a mark on the end says the "
                "same thing and is parsed instantly. The test is not \"is "
                "this anatomically fuller\" but \"does the reader get the "
                "claim faster\".",
            ],
        ),
    ],
)

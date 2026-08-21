"""Content for the bipolar cell page.

One of four cells that used to share a single *Neuron types* card. *"neuron
types — each type should get a card on its own."* A reader looking for a
bipolar cell searches for "bipolar", and a card called "Neuron types" is not
that.

The family argument — that all of these are one body plan at five settings —
kept a *Radial body plan* card of its own for a while, and that has gone too:
*"i dont see why we need a card for 'Radial body plan', lets remove it."*
A card is something a reader looks for by name, and nobody searches a
drawing catalog for a body plan. The argument still lives where it is
load-bearing: in `neuro.RadialCell`, which every one of these cells is.
"""

PAGE = dict(
    title="Bipolar cell",
    category="Neuroscience",
    order=2,
    tagline="Two opposed processes on a stretched soma — the one silhouette "
            "nothing else in the library shares.",
    hero="bipolar.png",
    hero_alt="A bipolar cell",
    shapes=["neuro.Bipolar"],
    keywords=[
        "bipolar",
        "bitufted",
        "retina",
        "sensory",
        "polarised",
        "neuron",
        "dendrite",
        "soma",
        "arc",
    ],

    intro=[
        "Retinal bipolar cells, many sensory neurons, and most cultured cells "
        "at an early stage read this way.",
    ],

    sections=[
        dict(
            title="How far apart the two processes leave",
            images=[dict(src="separation.png",
                         alt="At 180° it is bipolar; brought round to one "
                             "side the same cell is bitufted.")],
        ),

        dict(
            title="A polarised soma",
            images=[dict(src="soma.png",
                         alt="A round soma with two arms happens to have "
                             "them. A stretched one is polarised.")],
        ),

        dict(
            title="Drawing one",
            code="""
import biodraw as bd

cell = bd.neuro.Bipolar(
    arc_deg=180.0,      # 180 is opposed; narrower reads as bitufted
    aspect=1.75,        # soma stretched along the process axis
    length=1.35,        # process length, against a soma radius of 0.26
    forks=0.72,         # where along a process it splits, or None for plain
    depth=1,            # how many generations of splitting
)
cell.draw(ax=ax, wall_lw=0.9)
cell.fit(ax, pad=0.12)

# Where a connector may land: the soma wall, any shaft, any tip.
target = cell.anchor("soma", deg=270.0)
""",
        ),
    ],
)

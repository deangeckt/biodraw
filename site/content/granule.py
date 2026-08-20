"""Content for the granule cell page. See `site/content/bipolar.py` for why
the four named types are four cards.
"""

PAGE = dict(
    title="Granule cell",
    category="Neuroscience",
    order=3,
    tagline="Mostly soma, with four short dendrites that end in claws — the "
            "cell whose proportions are its identity.",
    hero="granule.png",
    hero_alt="A granule cell",
    shapes=["neuro.Granule"],
    keywords=[
        "granule",
        "cerebellum",
        "dentate",
        "claw",
        "small",
        "proportion",
        "neuron",
        "dendrite",
    ],

    intro=[
        "Drawn at a basket cell's proportions it stops reading as a granule "
        "cell, so `length` is the knob that matters here — not the count.",
    ],

    sections=[
        dict(
            title="Proportion is the identity",
            images=[dict(src="proportion.png",
                         alt="Same soma, same four processes. Only the first "
                             "two read as a granule cell.")],
        ),

        dict(
            title="The claw on the end",
            images=[dict(src="claws.png",
                         alt="A late fork at a wide angle is the claw. "
                             "Without it, a tiny multipolar neuron.")],
        ),

        dict(
            title="Drawing one",
            code="""
import biodraw as bd

cell = bd.neuro.Granule(
    length=0.85,            # barely longer than the soma — the identity knob
    dendrites=4,            # how many leave
    forks=0.62,             # the claw: a late split...
    fork_angle_deg=44.0,    # ...at a wide angle
    depth=2,
)
cell.draw(ax=ax, wall_lw=0.9)
cell.fit(ax, pad=0.12)
""",
        ),
    ],
)

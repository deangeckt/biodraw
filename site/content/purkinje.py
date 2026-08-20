"""Content for the Purkinje cell page. See `site/content/bipolar.py` for why
the four named types are four cards.
"""

PAGE = dict(
    title="Purkinje cell",
    category="Neuroscience",
    order=4,
    tagline="A flat, densely branched fan over one soma — an arc and a "
            "branching depth, and nothing else.",
    hero="purkinje.png",
    hero_alt="A Purkinje cell",
    shapes=["neuro.Purkinje"],
    keywords=[
        "purkinje",
        "cerebellum",
        "fan",
        "planar",
        "arbor",
        "wedge",
        "branching",
        "depth",
        "neuron",
        "dendrite",
    ],

    intro=[
        "A real Purkinje arbor is planar, and a drawing of one is a "
        "projection of that plane — so the flat fan is not a simplification.",
    ],

    sections=[
        dict(
            title="The wedge",
            images=[dict(src="wedge.png",
                         alt="Everything leaves upward into an arc. Widen it "
                             "far enough and this is a stellate cell.")],
        ),

        dict(
            title="How dense the fan is",
            images=[dict(src="fan.png",
                         alt="Branch count is dendrites x (2^(depth+1) - 1). "
                             "Past 3 it adds crossings, not detail.")],
        ),

        dict(
            title="Drawing one",
            code="""
import biodraw as bd

cell = bd.neuro.Purkinje(
    arc_deg=55.0,       # the wedge everything leaves into
    dendrites=3,        # primaries; each one splits `depth` times
    depth=3,            # 3 primaries at depth 3 is 45 branches
    forks=0.52,         # how far along a branch the split happens
    length=1.45,
)
cell.draw(ax=ax, wall_lw=0.85)
cell.fit(ax, pad=0.12)
""",
        ),
    ],
)

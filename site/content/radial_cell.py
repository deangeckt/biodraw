"""Content for the radial body plan page.

This page used to be *Neuron types* — six cells on one card. The named cells
are cards of their own now (see `site/content/bipolar.py`); what stayed here
is the thing none of them could carry alone: they are **one shape at five
settings**, and the settings are available to a reader whose cell the library
does not name.
"""

PAGE = dict(
    title="Radial body plan",
    category="Neuroscience",
    order=6,
    tagline="A soma with processes leaving it. Five named cells are this "
            "shape at five settings — and so is the one you need next.",
    hero="types.png",
    hero_alt="Six cell types side by side, each named by its silhouette",
    shapes=["neuro.RadialCell"],
    keywords=[
        "radial",
        "body plan",
        "cell type",
        "custom",
        "stellate",
        "multipolar",
        "arc",
        "branching",
        "depth",
        "arbor",
        "dendrite",
    ],

    intro=[
        "How many processes leave, over what arc, and how often they branch. "
        "Those three carry every cell on this page.",
    ],

    sections=[
        dict(
            title="Named by silhouette, not by colour",
            images=[dict(src="told_apart.png",
                         alt="A cell recognisable only by its hue fails a "
                             "greyscale printout.")],
        ),

        dict(
            title="The arc",
            images=[dict(src="arc.png",
                         alt="360° is a stellate cell, a wedge is a Purkinje, "
                             "180° with two processes is bipolar.")],
        ),

        dict(
            title="Branching depth",
            images=[dict(src="depth.png",
                         alt="Branch count is dendrites x (2^(depth+1) - 1) — "
                             "past 3 it adds crossings, not detail.")],
        ),

        dict(
            title="Proportion",
            images=[dict(src="sizes.png",
                         alt="A granule cell at a basket cell's proportions "
                             "stops reading as a granule cell.")],
        ),

        dict(
            title="Setting one yourself",
            code="""
import biodraw as bd

cell = bd.neuro.RadialCell(
    dendrites=5,        # how many processes leave the soma
    arc_deg=150.0,      # over what arc — 360 is a star, a wedge is a fan
    start_deg=15.0,     # where that arc begins, counter-clockwise from +x
    length=1.1,         # process length, against a soma radius of ~0.4
    forks=0.5,          # where along a process it splits, or None for plain
    depth=3,            # how many generations of splitting
    seed=1,             # fixes the jitter, so the figure regenerates
)
cell.draw(ax=ax, wall_lw=0.85)
cell.fit(ax, pad=0.22)

# ...or take one of the five that are already named
bd.neuro.Purkinje()     # or Basket, Bipolar, Granule, Astrocyte
""",
        ),
    ],
)

"""Content for the astrocyte page. See `site/content/bipolar.py` for why the
four named types are four cards.
"""

PAGE = dict(
    title="Astrocyte",
    category="Neuroscience",
    order=5,
    tagline="A bush of fine processes in every direction — where a Purkinje "
            "cell is a fan, this is a cloud.",
    hero="astrocyte.png",
    hero_alt="An astrocyte",
    shapes=["neuro.Astrocyte"],
    keywords=[
        "astrocyte",
        "glia",
        "glial",
        "bush",
        "star",
        "stellate",
        "process",
        "taper",
        "brain",
    ],

    intro=[
        "Not a neuron, and drawn so nobody mistakes it for one: no long axis, "
        "no dominant direction, and a soma nearly lost inside its own bush.",
    ],

    sections=[
        dict(
            title="How bushy",
            images=[dict(src="bushiness.png",
                         alt="Under six it reads as an untidy neuron; past "
                             "fourteen the soma disappears into a blot.")],
        ),

        dict(
            title="How fast the processes thin",
            images=[dict(src="fineness.png",
                         alt="A process that stays thick reads as a tube. "
                             "Astrocytic ones get very fine, very fast.")],
        ),

        dict(
            title="Drawing one",
            code="""
import biodraw as bd

cell = bd.neuro.Astrocyte(
    dendrites=10,       # processes leaving the soma, over the full turn
    taper=0.38,         # tip width, x the width at the soma — severe here
    length=0.70,
    jitter=0.45,        # how far each leaves its even slot: high, so no star
    depth=2,            # every process branches, twice
)
# Glia in the third identity colour, so neither cell class is implied.
cell.draw(ax=ax, edge=bd.style.palette.get()["tertiary"], wall_lw=0.8)
cell.fit(ax, pad=0.12)
""",
        ),
    ],
)

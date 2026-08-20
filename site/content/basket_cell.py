"""Content for the basket cell page."""

PAGE = dict(
    title="Basket cell",
    category="Neuroscience",
    order=1,
    tagline="A round soma with smooth dendrites leaving in every direction — "
            "the counterpart to the pyramidal cell, drawn to be told apart "
            "from it at a glance.",
    hero="basket.png",
    hero_alt="A basket cell",
    shapes=["neuro.Basket"],
    keywords=[
              "basket",
              "interneuron",
              "secondary",
              "aspiny",
              "multipolar",
              "bitufted",
              "bipolar",
              "dendrite",
              "neuron",
    ],

    sections=[
        dict(
            title="Told apart without colour",
            images=[dict(src="told_apart.png",
                         alt="Pyramidal and basket, in colour and in `mono`. "
                             "Round soma, dendrites all round, no "
                             "spines — every cue structural.")],
        ),

        dict(
            title="How it is built",
            images=[dict(
                src="blueprint.png",
                alt="Blueprint of the basket cell, in three panels",
                notes=[
                    "**Even slots, then knocked off them.** Displaced by at "
                    "most half a step, so the order round the soma survives.",
                    "**A repeated part must not repeat exactly.** At "
                    "`jitter=0` with equal lengths the cell reads as a "
                    "snowflake.",
                    "**Anchors.** Round the soma, along every shaft, and at "
                    "every tip.",
                ])],
            table=dict(
                head=["anchor", "where", "count above"],
                rows=[
                    ["`soma`", "eight points round the wall", "8"],
                    ["`shaft`", "both walls of every branch, three per branch",
                     "126"],
                    ["`tip`", "the end of each branch", "21"],
                ],
            ),
        ),

        dict(
            title="Drawing one",
            code="""
import biodraw as bd

cell = bd.neuro.Basket(
    dendrites=7,            # how many leave the soma
    forks=0.55,             # fraction along each at which it splits, None for straight
    length_ratio=0.68,      # shortest dendrite as a fraction of the longest
    jitter=0.22,            # how far each wanders off its even slot
    seed=2,                 # fixes both — same seed, same cell, forever
)

fig, ax = bd.canvas(figsize=(3.6, 3.6))
cell.draw(ax=ax, wall_lw=1.0, gid="basket")
cell.fit(ax, pad=0.14)
bd.save(fig, "basket.svg")

top = cell.anchor("soma", deg=90.0)
""",
        ),

        dict(
            title="Body plans",
            images=[dict(src="body_plans.png",
                         alt="Twelve body plans: `dendrites` against "
                             "`arc_deg`. A narrower arc gives a bitufted "
                             "cell without another class.")],
        ),

        dict(
            title="Branching",
            images=[dict(src="branching.png",
                         alt="Nine branch settings. Daughters are Rall-sized, "
                             "so both come out thinner than what they "
                             "leave — otherwise the joint spurs.")],
        ),

        dict(
            title="Regularity",
            images=[dict(src="regularity.png",
                         alt="Nine regularity settings. Top-left is the "
                             "failure case: identical dendrites at identical "
                             "spacing.")],
        ),

        dict(
            title="Seeds",
            images=[dict(src="seeds.png",
                         alt="Eight seeds. Same parameters, eight cells — "
                             "same seed, same cell, forever.")],
        ),
    ],
)

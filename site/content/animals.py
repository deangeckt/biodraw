"""Content for the model organisms page.

Built to the house style Dean set for this whole half of the roadmap: *"use
very simple drawings, not complex realistic images, sometimes an outline is
even enough."* Every drawing on the page is an outline with no interior
detail beyond the eyes, which is also why the page is light: five images and
about 80 kB.
"""

PAGE = dict(
    title="Model organisms",
    category="Animals",
    order=0,
    tagline="Mouse, fly, zebrafish and worm as silhouettes — and facing "
            "whichever way your panel needs.",
    hero="animals.png",
    hero_alt="A mouse, a fly, a zebrafish and a worm in outline",
    shapes=["animals.Mouse", "animals.Fly", "animals.Zebrafish",
            "animals.Worm"],
    keywords=[
        "animal",
        "model organism",
        "mouse",
        "rodent",
        "fly",
        "drosophila",
        "insect",
        "zebrafish",
        "fish",
        "worm",
        "c. elegans",
        "nematode",
        "silhouette",
        "outline",
        "methods figure",
    ],

    intro=[
        "An outline is enough. At the size a methods figure prints one of "
        "these, detail is bytes and attention spent on nothing a reader sees.",
    ],

    sections=[
        dict(
            title="Facing either way",
            images=[dict(src="facing.png",
                         alt="Mirrored, not rotated — a rotated animal is an "
                             "animal on its back.")],
        ),

        dict(
            title="One knob each",
            images=[dict(src="knobs.png",
                         alt="Tail against body, wings on or off, body "
                             "depth, how curled the worm is.")],
        ),

        dict(
            title="Drawn size, and true size",
            images=[dict(src="to_scale.png",
                         alt="A mouse is 80 mm and a worm 1 mm. True scale "
                             "suits one figure and wrecks most.")],
        ),

        dict(
            title="How one is built",
            images=[dict(
                src="blueprint.png",
                alt="A mouse, taken apart and put back together",
                notes=[
                    "**Seven outlines** — four bodies, two legs and a tapered "
                    "tube for the tail.",
                    "**One union.** Nothing else makes them a mouse rather "
                    "than a pile of shapes.",
                    "**Anchors**, so a label or a connector can find the nose "
                    "without measuring anything.",
                ])],
        ),

        dict(
            title="Drawing one",
            code="""
import biodraw as bd

mouse = bd.animals.Mouse(
    tail=0.78,          # tail length against a body of 1 — a stub is a vole
    ear=1.0,
    facing=-1,          # mirrored, so it faces into your panel
    at=(0.0, 0.0),
)
mouse.draw(ax=ax, wall_lw=1.1)
mouse.fit(ax, pad=0.12)

fish = bd.animals.Zebrafish(depth=1.35)  # a deeper-bodied fish
fly = bd.animals.Fly(wings=False)        # a wingless mutant, in one word
worm = bd.animals.Worm(curl=0.22, waves=2.2)

# Every animal exposes anchors: `wall` all round, plus its own named ones.
ax.annotate("wild type", xy=mouse.anchor("nose").xy,
            xytext=mouse.anchor("nose").offset(0.35))
""",
        ),
    ],
)

"""Content for the dendritic spine page."""

PAGE = dict(
    title="Dendritic spine",
    category="Dendrites & spines",
    order=0,
    build_pattern="spine",
    tagline="The shape biodraw grew out of, and the clearest example of why "
            "it traces rather than synthesises.",
    hero="spine.png",
    hero_alt="A dendritic spine",
    shapes=["profile.get('spine')", "Branch"],
    keywords=[
              "spine",
              "dendrite",
              "profile",
              "traced",
              "neck",
              "head",
              "extend",
              "density",
              "synapse",
    ],

    intro=[
        "Every attempt to build this profile out of ellipses read as a cone, "
        "a bead on a stick, or a leaf. Easier to draw by hand and trace — and "
        "once traced, it is maths you can place anywhere.",
    ],

    sections=[
        dict(
            title="How it is built",
            images=[dict(
                src="blueprint.png",
                alt="Blueprint of the spine profile, in four panels",
                notes=[
                    "**Traced, then normalised.** 56 vertices from a hand "
                    "drawing, rotated onto their long axis and scaled.",
                    "**The shape as a function.** Half-width against `x`: "
                    "flat neck, then flare. The asymmetry is the "
                    "drawing's own wobble.",
                    "**Lengthening the neck.** `extend` stretches only the "
                    "shaded span, so the head rides out rigidly instead of "
                    "inflating.",
                    "**Placed.** Same head, three neck lengths.",
                ])],
        ),

        dict(
            title="Drawing one",
            code="""
import biodraw as bd
from biodraw.core import profile, render
from biodraw.core.branch import Branch

spine = profile.get("spine")

branch = Branch(
    origin=(0, 0),
    direction=(0, 1),
    length=1.8,
    bend=0.10,              # the slow lean; sign picks the side
)
branch.decorate(
    profile="spine",
    n=8,                    # how many
    size=0.21,              # each spine's length
    extend=0.04,            # ...plus this much extra neck
    first_t=0.30,           # leave the proximal shaft bare for shaft contacts
    last_t=0.86,            # ...and stop short of the tip
)
wall, open_tip = branch.parts(
    width=0.11,             # full tube width where it leaves the origin
    taper=0.72,             # width at the tip, as a multiple of that
    base_ext=0.05,          # bury the base inside whatever it grows from
)

fig, ax = bd.canvas(figsize=(2.8, 4.4))
render.render_hollow(
    ax=ax,
    parts=wall,             # closed outlines — the spines
    open_parts=open_tip,    # the tube, whose far end stops rather than caps
    fill="#FFD9D9",         # the interior wash
    edge="#FF0000",         # the wall
    wall_lw=1.0,            # wall thickness, in points
    gid="dendrite",         # names the layer in the exported SVG
)
bd.fit(ax, wall + open_tip, pad=0.12)
bd.save(fig, "dendrite.svg")
""",
        ),

        dict(
            title="Turning the knobs",
            images=[dict(src="stretch.png",
                         alt="Three neck extensions. `extend` changes how far "
                             "a spine stands off its branch without resizing "
                             "it.")],
        ),

        dict(
            title="On a branch",
            images=[
                dict(src="branch.png",
                     alt="A spiny dendrite. Tube and every spine fuse into "
                         "one unbroken outline — no seam where they meet."),
                dict(src="density.png",
                     alt="Three spine densities. A count spread over a length "
                         "is a density."),
            ],
        ),

        dict(
            title="Colour",
            images=[dict(src="palettes.png",
                         alt="Three palettes. `mono` is the check that the "
                             "drawing still reads with its colours taken "
                             "away.")],
        ),
    ],
)

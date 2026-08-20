"""Content for the dendritic spine page.

Reordered after: *"in spine page — still there is too much [prose] which
appear almost at the start of the page, figures are higher prio then text."*
The page used to open with the blueprint and its four panel notes, so the
first screen was a diagram *about* the shape plus sixty words. It now opens
with the shapes themselves and the blueprint sits near the end, where a
reader who wants the derivation will go looking for it.

The old *Colour* section is gone as well — palettes are a property of every
drawing rather than of this one, and they are all on the standalone styles
page now. What took its place is what was actually missing: the spine's own
variation, head and neck.
"""

PAGE = dict(
    title="Dendritic spine",
    category="Neuroscience",
    order=7,
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
              "mushroom",
              "thin",
              "stubby",
              "extend",
              "density",
              "synapse",
    ],

    intro=[
        "Traced off a hand drawing, because every attempt to build this "
        "profile out of ellipses read as a cone or a bead on a stick.",
    ],

    sections=[
        dict(
            title="One outline, the shapes people name",
            images=[dict(src="forms.png",
                         alt="Thin, stubby, mushroom and long-necked — three "
                             "numbers apart, not four traced shapes.")],
        ),

        dict(
            title="Head and neck",
            images=[dict(src="head_neck.png",
                         alt="`head` and `neck` scale one width each. Length "
                             "stays with `size` and `extend`.")],
        ),

        dict(
            title="On a branch",
            images=[
                dict(src="branch.png",
                     alt="Tube and every spine fuse into one unbroken "
                         "outline — no seam where they meet."),
                dict(src="density.png",
                     alt="Three spine densities. A count spread over a length "
                         "is a density."),
            ],
        ),

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
    head=1.22,              # head width, x the traced one — a mushroom spine
    neck=0.55,              # ...on a neck thinned to just over half
    first_t=0.30,           # leave the proximal shaft bare for shaft contacts
    last_t=0.86,            # ...and stop short of the tip
)
wall, open_tip = branch.parts(
    width=0.11,             # full tube width where it leaves the origin
    taper=0.72,             # width at the tip, as a multiple of that
    base_ext=0.05,          # bury the base inside whatever it grows from
)

ink = bd.style.palette.get()["primary"]

fig, ax = bd.canvas(figsize=(2.8, 4.4))
render.render_hollow(
    ax=ax,
    parts=wall,             # closed outlines — the spines
    open_parts=open_tip,    # the tube, whose far end stops rather than caps
    fill=None,              # None washes the interior with the wall colour
    edge=ink,               # the wall
    wall_lw=1.0,            # wall thickness, in points
    gid="dendrite",         # names the layer in the exported SVG
)
bd.fit(ax, wall + open_tip, pad=0.12)
bd.save(fig, "dendrite.svg")
""",
        ),
    ],
)

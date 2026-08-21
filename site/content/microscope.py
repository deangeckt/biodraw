"""Content for the microscope page.

The first catalog entry that is not alive. `docs/SCOPE.md` is explicit that
this library should never compete with a stock asset library, and a
microscope looks exactly like the thing to download — so the page has to
carry the argument that admits it, which is the library's own roster test:
**a thing that wants varying belongs here, a thing that only wants
downloading does not.** A nosepiece has a count on it.

Worth recording for whoever writes the next instrument: the parts list came
off textbook schematics as proportions, nothing traced and nothing committed
(drawing rule 6), and one of the five knobs the inventory asked for did not
survive contact with the drawing. *Binocular* is unbuildable in a strict side
elevation — the two tubes separate into the page — and it was measured at
0.0% difference on the inverted body before it was cut.
"""

PAGE = dict(
    title="Microscope",
    category="Lab & methods",
    order=0,
    tagline="An instrument with counts in it: n objectives, an upright body "
            "or an inverted one.",
    hero="microscope.png",
    hero_alt="An upright compound microscope with a camera port",
    shapes=["lab.Microscope"],
    keywords=[
        "microscope",
        "objective",
        "nosepiece",
        "turret",
        "eyepiece",
        "stage",
        "condenser",
        "inverted",
        "upright",
        "instrument",
        "equipment",
        "methods",
    ],

    intro=[
        "Free libraries carry thousands of scientific icons and this library "
        "does not compete with them. What a downloaded microscope cannot "
        "know is **your** nosepiece — so the count is the reason to draw it.",
    ],

    sections=[
        dict(
            title="However many objectives",
            images=[dict(src="objectives.png",
                         alt="A turret is indexed: one barrel sits on the "
                             "optical axis, the rest fan around it.")],
        ),

        dict(
            title="Upright, or inverted",
            images=[dict(src="bodies.png",
                         alt="Not a mirror. Inverted optics look up from "
                             "under the stage, with the lamp above.")],
        ),

        dict(
            title="Fitted, or stripped back",
            images=[dict(src="fittings.png",
                         alt="A figure about optics wants the light path. A "
                             "workflow figure wants the silhouette.")],
        ),

        dict(
            title="Drawing one",
            code="""
import biodraw as bd

scope = bd.lab.Microscope(
    objectives=4,        # the knob it exists for
    inverted=False,      # a different instrument, not a flipped one
    condenser=True,      # sub-stage optics and the lamp under them
    camera=True,         # the port on top
)
scope.draw(ax=ax, edge=ink, wall_lw=1.2)

# Anchors, like every shape here: `objective`, `eyepiece`, `stage`, `base`,
# plus `wall` all round for a caption to stand off.
bd.label(ax=ax, at=scope.anchor("stage"), text="specimen", gap=0.08)
""",
        ),

        dict(
            title="How it is put together",
            images=[dict(src="blueprint.png",
                         alt="The working distance is the one number that "
                             "must be positive. It was negative at first.")],
        ),
    ],
)

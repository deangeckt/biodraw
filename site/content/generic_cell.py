"""Content for the generic cell page."""

PAGE = dict(
    title="Generic cell",
    category="Cells & tissues",
    order=0,
    build_pattern="generic",
    tagline="A body, a nucleus, and whatever is loose in the cytoplasm. The "
            "first shape in this library that is not one unbroken outline.",
    hero="cell.png",
    hero_alt="A generic cell with nucleus, nucleolus and organelles",
    shapes=["cells.Blob", "core.scatter", "shape.Layer"],
    keywords=[
              "cell",
              "nucleus",
              "nucleolus",
              "organelle",
              "membrane",
              "microvilli",
              "filopodia",
              "pseudopodia",
              "protrusion",
              "cytoplasm",
    ],

    intro=[
        "This is the reason `biodraw.core.shape.Layer` exists.",
    ],

    sections=[
        dict(
            title="How it is built",
            images=[dict(
                src="blueprint.png",
                alt="Blueprint of the generic cell, in four panels",
                notes=[
                    "**Four layers, not one union.** Each is its own render "
                    "pass at its own zorder, *covering* what is beneath.",
                    "**The same parts, unioned.** What happens without "
                    "layers: everything is still there, absorbed into the "
                    "body's fill.",
                    "**`scatter_in`.** Rejection-sampled with a wall "
                    "margin and a separation. Ask for more than fits "
                    "and it **raises**.",
                    "**Anchors.** Round the wall, on the nuclear envelope, "
                    "one per organelle, one per protrusion tip.",
                ])],
            table=dict(
                head=["anchor", "where", "count above"],
                rows=[
                    ["`wall`", "eight round the membrane — on the *wobbled* "
                     "outline, not the ideal superellipse", "8"],
                    ["`nucleus`", "top and bottom of the nuclear envelope",
                     "2"],
                    ["`organelle`", "one each, pointing away from the centre",
                     "7"],
                    ["`tip`", "the end of each protrusion", "9"],
                ],
            ),
        ),

        dict(
            title="Drawing one",
            code="""
import biodraw as bd

cell = bd.cells.Blob(
    radius=0.55,            # the one size knob; everything else is a fraction of it
    squareness=2.6,         # 2 is an ellipse, 4 a rounded box
    wobble=0.028,           # swells the wall, so it does not read as an equation
    nucleus=0.34,           # nuclear radius, x the body radius
    nucleolus=0.36,         # ...and the nucleolus, x the nuclear radius
    organelles=7,           # scattered in the cytoplasm
    protrusions=0,          # microvilli, filopodia or pseudopodia
    seed=3,                 # fixes the scatter — same seed, same cell, forever
)

fig, ax = bd.canvas(figsize=(3.4, 3.2))
cell.draw(
    ax=ax,
    wall_lw=1.0,            # wall thickness, in points
    gid="cell",             # names each layer in the exported SVG:
)                           # cell.nucleus.wall, cell.organelles.fill, ...
cell.fit(ax, pad=0.12)
bd.save(fig, "cell.svg")

top = cell.anchor("wall", deg=90.0)
""",
        ),

        dict(
            title="How much is in it",
            images=[dict(src="contents.png",
                         alt="Six organelle counts. Past ten `scatter_in` "
                             "raises — more means smaller and closer, a "
                             "claim you must make.")],
        ),

        dict(
            title="Body plans",
            images=[dict(src="body_shapes.png",
                         alt="Eighteen body shapes: `squareness` against "
                             "`aspect`. Wobble past 0.08 stops reading as a "
                             "cell and starts reading as damage.")],
        ),

        dict(
            title="Membranes",
            images=[dict(src="membranes.png",
                         alt="Nine membrane treatments — the same `Branch` "
                             "engine that draws a dendrite, doing microvilli, "
                             "filopodia and pseudopodia.")],
        ),

        dict(
            title="Seeds",
            images=[dict(src="seeds.png",
                         alt="Eight seeds. At `protrusion_jitter=0` they sit "
                             "on perfect 40° centres and the cell reads as a "
                             "gear.")],
        ),
    ],
)

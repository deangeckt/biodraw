"""Content for the pyramidal cell page."""

PAGE = dict(
    title="Pyramidal cell",
    category="Neuroscience",
    order=0,
    tagline="A triangular soma with spiny dendrites out of it — apical up, "
            "basals down — soma, dendrites and every spine forming one "
            "unbroken outline.",
    hero="pyramidal.png",
    hero_alt="A pyramidal cell",
    shapes=["neuro.Pyramidal"],
    keywords=[
              "pyramidal",
              "neuron",
              "primary",
              "soma",
              "apical",
              "basal",
              "cortex",
              "spiny",
              "fork",
              "dendrite",
    ],

    sections=[
        dict(
            title="How it is built",
            images=[dict(
                src="blueprint.png",
                alt="Blueprint of the pyramidal cell, in four panels",
                notes=[
                    "**The skeleton.** Three points, a `Branch` per dendrite, "
                    "a traced `Profile` per spine. Nothing neuron-specific.",
                    "**The neck, not a flat top.** Each slanted edge turns "
                    "tangentially into the tube wall — no corner left.",
                    "**A basal roots through its corner.** The axis starts "
                    "inside the body, so the fill swallows the vertex.",
                    "**Anchors.** Every place something attaches, with the "
                    "direction leading away. Connectors and labels consume "
                    "these.",
                ])],
            table=dict(
                head=["anchor", "where", "count above"],
                rows=[
                    ["`spine`", "each spine head, the widest point", "18"],
                    ["`shaft`", "the bare proximal apical, both walls", "4"],
                    ["`soma`", "down each slanted flank", "4"],
                    ["`axon`", "the bottom of the soma, pointing down", "1"],
                ],
            ),
        ),

        dict(
            title="Drawing one",
            code="""
import biodraw as bd

cell = bd.neuro.Pyramidal(
    spines=8,               # spines along the apical
    basal=2,                # basal branches off the soma's bottom corners
    basal_spines=5,         # ...and spines on each of those
    spine_extend=0.04,      # extra neck, so heads stand clear of each other
)

fig, ax = bd.canvas(figsize=(3.0, 4.2))
cell.draw(
    ax=ax,
    wall_lw=1.0,            # wall thickness, in points
    gid="pyramidal",        # names the layers in the exported SVG
)
cell.fit(ax, pad=0.2)
bd.save(fig, "pyramidal.svg")

distal = cell.anchor("spine", branch="apical", rank=-1)
""",
        ),

        dict(
            title="Spininess",
            images=[dict(src="spininess.png",
                         alt="Six spine densities, `spines=0` to `spines=16`. "
                             "A count spread over a length is a density.")],
        ),

        dict(
            title="Body plans",
            images=[dict(src="body_plans.png",
                         alt="Eighteen body plans: `basal` 0–2 legs against "
                             "`basal_angle_deg`. Past 60° the triangle "
                             "flattens into a trapeze.")],
        ),

        dict(
            title="Forking the apical",
            images=[dict(src="forks.png",
                         alt="Nine forks. `trunk_len` stays the full apical "
                             "reach either way, so forking never silently "
                             "grows the cell.")],
        ),
    ],
)

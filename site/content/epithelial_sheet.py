"""Content for the epithelial sheet page."""

PAGE = dict(
    title="Epithelial sheet",
    category="Cells & tissues",
    order=1,
    build_pattern="epithelial",
    tagline="A row of cells standing on a basement membrane — many cells that "
            "must not become one.",
    hero="epithelium.png",
    hero_alt="A columnar epithelium with a brush border",
    shapes=["cells.Sheet", "shape.Layer"],
    keywords=[
              "epithelium",
              "epithelial",
              "tissue",
              "duct",
              "villus",
              "lumen",
              "brush border",
              "columnar",
              "cuboidal",
              "squamous",
              "basement membrane",
              "junction",
              "polarity",
    ],

    intro=[
        "Where the [generic cell](generic_cell.html) is one cell that is not "
        "one contour, this is many cells that must **not** become one.",
    ],

    sections=[
        dict(
            title="How it is built",
            images=[dict(
                src="blueprint.png",
                alt="Blueprint of the epithelial sheet, in four panels",
                notes=[
                    "**Why every cell is its own layer.** One union "
                    "dissolves every shared wall into one long cell.",
                    "**The hairline between neighbours.** `gap` is real page. "
                    "At zero, each cell's second pass erases half the other's "
                    "wall.",
                    "**The arc, derived from the pitch.** One cell subtends "
                    "one pitch angle, so `-360` closes exactly at any "
                    "count.",
                    "**Anchors.** Apical and basal per cell, one nucleus, one "
                    "junction at the apical end of each shared wall.",
                ])],
            table=dict(
                head=["anchor", "where", "count on a 6-cell row"],
                rows=[
                    ["`apical`", "middle of each apical surface, pointing out",
                     "6"],
                    ["`basal`", "middle of each basal surface, pointing down",
                     "6"],
                    ["`nucleus`", "one per nucleus", "6"],
                    ["`junction`", "the apical end of each shared wall — one "
                     "*per cell* on a closed ring", "5"],
                ],
            ),
        ),

        dict(
            title="Drawing one",
            code="""
import biodraw as bd

sheet = bd.cells.Sheet(
    cells=6,                # how many, side by side
    cell_w=0.46,            # the pitch, at the basal line
    height=1.0,             # basal surface to apical surface
    gap=0.06,               # page left between neighbours, x cell_w
    nucleus=0.30,           # nuclear semi-axis, x cell_w
    nucleus_at=0.32,        # basal — the cheapest cue that the sheet has a polarity
    nucleus_jitter=0.05,    # ...because a row of identical cells is a row of copies
    height_jitter=0.04,     # and a level apical surface is the first thing the eye finds
    microvilli=5,           # brush border, per cell
    curve_deg=0,            # -360 closes into a ring; refuses if height will not fit
    basement=True,          # the band the sheet stands on
    seed=1,                 # fixes both jitters — still byte-identical on rebuild
)

fig, ax = bd.canvas(figsize=(4.4, 2.6))
sheet.draw(
    ax=ax,
    wall_lw=1.0,            # wall thickness, in points
    gid="epithelium",       # names the layers in the exported SVG
)
sheet.fit(ax, pad=0.10)
bd.save(fig, "epithelium.svg")

lumen_side = sheet.anchor("apical", cell=2)
""",
        ),

        dict(
            title="Curvature",
            images=[dict(src="curvature.png",
                         alt="Six curvatures. Positive puts the apical "
                             "surface outside; negative encloses a lumen and "
                             "`-360` closes exactly.")],
        ),

        dict(
            title="Cell shapes",
            images=[dict(src="cell_shapes.png",
                         alt="Nine cell shapes — squamous, cuboidal, "
                             "columnar — one object at three heights crossed "
                             "with `taper`.")],
        ),

        dict(
            title="Brush border",
            images=[dict(src="borders.png",
                         alt="Eight brush borders. Aimed along each cell's "
                             "own axis, not the local radius — which fans "
                             "them into fraying.")],
        ),
    ],
)

"""Content for the bacteria page."""

PAGE = dict(
    title="Bacteria",
    category="Microbes",
    order=0,
    tagline="A capsule body and what is hung off it. The named forms — "
            "coccus, bacillus, vibrio, spirillum — are settings of three "
            "knobs, so the space between them is drawable too.",
    hero="bacterium.png",
    hero_alt="A flagellated bacillus with capsule, nucleoid and granules",
    shapes=["micro.Bacterium", "paths.tube"],
    keywords=[
              "bacteria",
              "bacterium",
              "microbe",
              "coccus",
              "bacillus",
              "rod",
              "vibrio",
              "spirillum",
              "spirochaete",
              "flagellum",
              "flagella",
              "pili",
              "fimbriae",
              "capsule",
              "nucleoid",
              "colony",
              "diplococcus",
              "streptococcus",
              "staphylococcus",
    ],

    intro=[
        "The first domain whose body is a **tube** rather than a ring. A "
        "`Blob` is a closed outline with things inside it; a bacillus is a "
        "centreline with a width, which is the same object a dendrite is.",
    ],

    sections=[
        dict(
            title="How it is built",
            images=[dict(
                src="blueprint.png",
                alt="Blueprint of the bacterial cell, in four panels",
                notes=[
                    "**The axis.** A straight run, bent by `curve_deg`, waved "
                    "by `twists`. They compose rather than switch, at "
                    "constant arclength.",
                    "**Both ends, or it is not a cell.** A flat end reads as "
                    "a specimen that was sectioned. `paths.tube(cap_base=True)`.",
                    "**`flagella_arc_deg`.** Where an appendage leaves, "
                    "resolved against the outline *as drawn* — cap and bend "
                    "included.",
                    "**Anchors.** Two poles, eight round the wall, one per "
                    "appendage tip.",
                ])],
            table=dict(
                head=["anchor", "where", "count above"],
                rows=[
                    ["`pole`", "the two ends of the axis, pointing away", "2"],
                    ["`wall`", "eight round the outline — `wall_at(deg)` is "
                     "exact on a rod, best-effort on a spirillum", "8"],
                    ["`flagellum`", "the free end of each flagellum", "7"],
                    ["`pilus`", "the free end of each pilus", "16"],
                ],
            ),
        ),

        dict(
            title="Drawing one",
            code="""
import biodraw as bd

# The named forms are settings, not classes — so the space between them draws too.
coccus    = bd.micro.Bacterium(length=0.0, width=0.62)    # no length: a circle
bacillus  = bd.micro.Bacterium(length=1.40)
vibrio    = bd.micro.Bacterium(length=1.40, curve_deg=72)  # the comma
spirillum = bd.micro.Bacterium(length=2.20, twists=1.8, twist_amp=0.62)

cell = bd.micro.Bacterium(
    length=1.40,
    capsule=0.20,           # slime layer thickness, x width — drawn under the wall
    nucleoid=0.66,          # x the body half-width, following its own axis
    granules=5,             # inclusions, scattered by core.scatter
    pili=20,                # fimbriae: many more and much shorter than flagella
    flagella=4,             # 1 monotrichous · 2 at 360 amphitrichous · 9 peritrichous
    flagella_arc_deg=74,    # a narrow sweep...
    flagella_start_deg=-37,  # ...centred on one pole: a lophotrichous tuft
)

# Arrangements are composition. `moved()` is the whole vocabulary — there is
# deliberately no `arrangement=` keyword. Spacing is a clearance you check:
# two cocci of radius r draw through each other below 2r.
pair = [cell.moved(at=(0.0, 0.0)), cell.moved(at=(2.05 * 0.27, 0.0))]
""",
        ),

        dict(
            title="Six forms a reader can name",
            images=[dict(src="named.png",
                         alt="Six named bacterial forms. An enum would make "
                             "these the only reachable shapes, and the rest "
                             "dead code.")],
        ),

        dict(
            title="The space between them",
            images=[dict(src="forms.png",
                         alt="Twenty bodies: length across, axis down. The "
                             "bottom row is bent *and* twisted, which no "
                             "named form covers.")],
        ),

        dict(
            title="Flagella",
            images=[dict(src="flagella.png",
                         alt="The four arrangements — two numbers each. "
                             "`Branch` tubes, with the waver turned up until "
                             "it is the whole shape.")],
        ),

        dict(
            title="Envelope and contents",
            images=[dict(src="envelope.png",
                         alt="Capsule, nucleoid, granules and pili. A "
                             "nucleoid and deliberately no nucleus — the "
                             "loudest error this shape could make.")],
        ),

        dict(
            title="Arrangements are composition",
            images=[dict(src="colony.png",
                         alt="Diplococcus, streptococcus, staphylococcus and "
                             "a palisade — every one of them `moved()`, with "
                             "no colony keyword.")],
        ),
    ],
)

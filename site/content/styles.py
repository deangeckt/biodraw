"""Content for the drawing-styles page.

Built after Dean pointed at a journal summary figure and said the catalog
should gain **new styles of neuron**, not a copy of that figure. So this page
is the styles themselves: the same two cells under every house style the
library can draw, plus the detail levels that are the other half of the same
decision.

Then: *"neuron style is great! ... but i dont think it should be in a card,
rather, somewhere else, which is more of a 'global' or parallel to the main
page cards."* A card is one drawing among many and invites comparison with
its neighbours; a style is a property **of** every card in the grid. So this
page is `standalone`: it is in the masthead of every page and in a band
beside the grid, and it is not in the grid. `tools/build_site.py` grew the
flag; the band is generated from this same dict, so there is no second copy
of it to drift.
"""

PAGE = dict(
    title="Drawing styles",
    standalone=True,
    order=0,
    examples=["styles"],
    tagline="Two drawing languages — walled tubes and stroked "
            "centrelines — and the settings inside each.",
    hero="styles.png",
    hero_alt="One cell under seven house styles",
    shapes=["Shape.draw", "style.palette"],
    keywords=[
        "style",
        "flat",
        "silhouette",
        "outline",
        "hollow",
        "skeleton",
        "ghost",
        "greyscale",
        "house style",
        "journal",
        "poster",
    ],

    intro=[
        "A colour and a linewidth are not a style. `hollow` says a process "
        "has a width and a wall; `skeleton` says it exists and connects two "
        "places.",
    ],

    sections=[
        dict(
            title="Two languages",
            images=[dict(src="both.png",
                         alt="Both cell types under every style. One that "
                             "stops telling them apart is one you cannot "
                             "use.")],
        ),

        dict(
            title="Drawing in one",
            code="""
import biodraw as bd

cell = bd.neuro.Pyramidal(spines=7, basal=2, basal_spines=3)
ink = bd.style.palette.get()["primary"]

# the hollow language: walls, fused into one contour
cell.draw(ax=ax, edge=ink)                      # washed interior
cell.draw(ax=ax, edge=ink, fill="white")        # paper shows through
cell.draw(ax=ax, edge=ink, fill=ink)            # a silhouette
cell.draw(ax=ax, edge=ink, alpha=0.35)          # a background cell

# the other language: no walls, centrelines stroked at the cell's own taper
cell.draw(ax=ax, edge=ink, style="skeleton")
""",
        ),

        dict(
            title="How much cell to draw",
            images=[dict(src="detail.png",
                         alt="Spines are information at portrait size and "
                             "noise at circuit size.")],
        ),

        dict(
            title="In every palette",
            images=[dict(src="palettes.png",
                         alt="mono is the check: a drawing that needs colour "
                             "to be read will fail a greyscale printout.")],
        ),
    ],
)

"""Colours.

**Identity colours only.** A hue here names *what a thing is* within one
figure — the subject, the thing it contrasts against, a third class — and is
used everywhere that kind appears. Anything belonging to nobody takes grey, so
it cannot be mistaken for either.

Why the slots are named by role and not by biology
--------------------------------------------------
They used to be `excitatory` and `inhibitory`. That reads well in
`biodraw.neuro` and nowhere else, and the evidence was already in the tree:
`examples/epithelial_sheet` coloured a **nucleus** with `palette["inhibitory"]`
because there was no other slot to reach for, and three other non-neuro
examples did the same. A general drawing library carrying one field's
vocabulary in its shared palette is the same mistake as the claim colours
below, one level up.

So the slots are `primary`, `secondary` and `tertiary`. Which biology they
denote is the figure's business, said in the figure's own key — exactly as
this module already argues for claims.

What is deliberately not here
-----------------------------
An earlier version also carried "claim" colours — one per compartment a
synapse might land on — so a figure could say *which* part of a cell a contact
hit. That is a **logic layer**, not a drawing layer: deciding what a figure
asserts about a circuit is the author's scientific judgement, and colouring it
is two lines of matplotlib once the drawing exists. Carrying it here meant
carrying one particular paper's argument inside a general drawing library.

So the palette stops at identity, and a figure that needs to say something
extra says it in its own script, in its own colours, with its own key. See
`examples/circuit_motifs/` — the claim there is carried by the *endcap* (an
arrowhead or a bar), which is part of drawing a connector rather than a
separate object.

A blueprint or construction figure may of course use whatever annotation
colours it likes; those are diagrams about the drawing, not the drawing.
"""

__all__ = ["PALETTES", "DEFAULT", "IDENTITIES", "get", "available"]

#: The identity slots every palette defines, in the order a figure should
#: reach for them.
IDENTITIES = ("primary", "secondary", "tertiary")


PALETTES = {
    # The default. Blue, lavender and sage — chosen for the gallery over the
    # saturated red/blue the seed figure used, which read as harsh on a white
    # page and left no third hue for a figure with three cell classes.
    #
    # Three identities rather than two on purpose: a circuit panel almost
    # always has one more class than you planned for, and inventing a fourth
    # hue per figure is how a catalog stops looking like one library.
    #
    # Red for excitatory, green for inhibitory — the convention most
    # neuroscience readers already carry, so the figure spends none of the
    # reader's attention teaching it. Both are muted rather than pure: a
    # saturated red on white is harsh at any size, and the point of a default
    # is to look right in a catalog of a hundred drawings, not in one.
    #
    # **Red and green together is the classic colour-blind hazard** — around
    # 8% of men cannot reliably separate them, and this is the one pair a
    # scientific library should be honest about. Two things make it defensible
    # rather than careless:
    #
    #   - structure carries the distinction *first* (see `biodraw.neuro`): a
    #     triangle with one apical up is not a round soma with arms in every
    #     direction, whatever colour either is printed in. Colour is the
    #     second signal here, never the only one.
    #   - `palettes['colorblind']` is one argument away and every example
    #     renders in it, so a figure going to print has a tested escape.
    #
    # A drawing that stops making sense in `mono` is leaning on colour to
    # carry a claim, and that is a defect in the drawing.
    "default": {
        "primary": "#C0392B",      # red
        "secondary": "#2E8B57",    # green
        "tertiary": "#2E6F95",     # blue
        "neutral": "#8A8A8A",
        "ink": "#111111",
        "page": "#FFFFFF",
    },
    # Okabe-Ito, distinguishable under all common forms of colour blindness.
    # Recommended for anything going into print.
    "colorblind": {
        "primary": "#0072B2",      # blue
        "secondary": "#CC79A7",    # reddish purple
        "tertiary": "#009E73",     # bluish green
        "neutral": "#999999",
        "ink": "#111111",
        "page": "#FFFFFF",
    },
    # No hue at all — for journals that charge for colour figures, and as a
    # check that a drawing still reads when its colours are taken away. If a
    # figure only works in the first palette, it is leaning on colour to carry
    # a claim and will fail on someone's greyscale printout.
    "mono": {
        "primary": "#222222",
        "secondary": "#777777",
        "tertiary": "#AAAAAA",
        "neutral": "#999999",
        "ink": "#111111",
        "page": "#FFFFFF",
    },
}

DEFAULT = "default"


def get(name=None):
    """A palette dict by name. `None` gives the default."""
    key = DEFAULT if name is None else str(name)
    try:
        return dict(PALETTES[key])
    except KeyError:
        raise KeyError(f"unknown palette {key!r}; "
                       f"available: {sorted(PALETTES)}") from None


def available():
    """Every palette name."""
    return sorted(PALETTES)

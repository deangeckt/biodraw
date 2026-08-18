"""Colours.

**Identity colours only.** A hue here names *what a thing is* — an excitatory
cell, an inhibitory one — and is used everywhere that kind appears. Anything
that is neither takes grey, so it cannot be mistaken for either.

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

__all__ = ["PALETTES", "DEFAULT", "get", "available"]


PALETTES = {
    # The palette the reference figure was drawn in. Kept as the default
    # because it is what the bundled examples are tuned against.
    "default": {
        "excitatory": "#FF0000",
        "inhibitory": "#0072BD",
        "neutral": "#8A8A8A",
        "ink": "#111111",
        "page": "#FFFFFF",
    },
    # Okabe-Ito, which is distinguishable under all common forms of colour
    # blindness. Recommended for anything going into print.
    "colorblind": {
        "excitatory": "#D55E00",
        "inhibitory": "#0072B2",
        "neutral": "#999999",
        "ink": "#111111",
        "page": "#FFFFFF",
    },
    # No hue at all — for journals that charge for colour figures, and as a
    # check that a drawing still reads when its colours are taken away. If a
    # figure only works in the first palette, it is leaning on colour to carry
    # a claim and will fail on someone's greyscale printout.
    "mono": {
        "excitatory": "#222222",
        "inhibitory": "#777777",
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

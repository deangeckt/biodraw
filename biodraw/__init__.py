"""biodraw — bio-inspired vector drawings for papers, posters and slides.

Cartoon cells, dendrites with spines, axons, synapses and wired circuit
panels, drawn as clean vector output you can restyle, extend, and put beside
your own data.

Two faces, on purpose
---------------------
**The usage side is for people.** Short, readable, and hard to get wrong::

    import biodraw as bd

    cell = bd.neuro.Pyramidal(spines=8)
    fig, ax = bd.canvas()
    cell.draw(ax)
    bd.save(fig, "cell.svg")

**The implementation side is for agents.** Most people will not write this
code themselves — they will describe the figure they want and let a model
build it. So the library is built to be driven by one: every shape is
introspectable (`bd.catalog`), every knob documents its own effect and range,
drawings are checkable without eyes (`bd.check`), and every shape can render
its own construction figure (`bd.explain`) so both of you can see what the
maths is doing.

The shapes themselves come from hand drawings, traced and normalised —
`Profile(points=..., normalize=True, tip=...)` puts your own outline into the
same canonical frame as the bundled spine, and `core.profile.register` makes
it available by name everywhere. That path is part of the API, not a story
about how it was made: your sketch becomes a shape in this library the same
way the spine did. The recipe for doing it is `skills/trace-a-shape`.
"""

from . import cells, core, io, layout, micro, neuro, style
from .core import Branch, Profile
from .core.anchor import Anchor
from .core.connectors import connect, connect_tree, endcap
from .core.shape import Layer, Shape
from .io import canvas, fit, save, save_compact, set_quality
from .layout import contact_sheet

__version__ = "0.1.0.dev0"

__all__ = [
    "cells", "core", "io", "layout", "micro", "neuro", "style",
    "Anchor", "Branch", "Layer", "Profile", "Shape",
    "connect", "connect_tree", "endcap",
    "canvas", "contact_sheet", "fit", "save", "save_compact", "set_quality",
    "__version__",
]

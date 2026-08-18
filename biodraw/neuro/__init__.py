"""Neurons and their parts.

The first domain built on `biodraw.core`, and the reference for what a domain
package looks like: every shape here is assembled from core primitives —
branches, traced profiles, tubes, bowed bodies — and exposes anchors, so
connectors and markers work on it without knowing what a neuron is.

Two cell types, drawn to be told apart **structurally** rather than by colour:
a pyramidal cell is a triangle with one apical up and basals down, a basket
cell is a round soma with smooth dendrites in every direction. That survives
greyscale printing, which a hue difference does not.

There is no `Axon` shape. One was built — a tapered tube with swellings along
it — and removed: at the size an axon appears in a circuit panel a "realistic"
one reads as a fat beaded worm rather than as a process, and it competes for
attention with the cells it is meant to connect. **A projection between cells
is drawn as a line with a mark on the end** (`core.connectors`), which is what
circuit figures actually do and what a reader parses instantly.
"""

from .basket import Basket
from .pyramidal import Pyramidal

__all__ = ["Basket", "Pyramidal"]

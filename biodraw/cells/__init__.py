"""Cells that are not neurons.

The second domain on `biodraw.core`, and the one that exists to test a claim
the first cannot: that the core is domain-neutral. Both earlier examples are
neurons, so every primitive had so far been exercised by exactly the kind of
drawing it was ported from — and a body primitive that quietly assumes a
dendrite is coming out of the top of it would never have shown up.

What building these two found missing is recorded in `docs/MILESTONES.md`.
In short: `core.shape.Layer`, because a nucleus has to occlude the body
rather than fuse with it, and `core.scatter`, because nothing here grows
along a path.
"""

from .blob import Blob
from .sheet import Sheet

__all__ = ["Blob", "Sheet"]

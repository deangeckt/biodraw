"""Microbes.

The third domain on `biodraw.core`, after `neuro` and `cells`, and the one
that tests a different corner of the claim that the core is domain-neutral.
`Blob` and `Sheet` are bodies — closed rings with things inside them. A
bacterium is a **tube**: a centreline with a width, which is structurally the
same object as a dendrite and nothing at all like a cell body.

What building it found missing, which is the useful output of any new domain
here:

1. **`paths.tube(cap_base=True)`.** Every tube in the library until now grew
   out of something, so its near end was a flat chord to be buried in a
   parent. A free-floating cell has no parent, and a flat end reads as a cut
   specimen. One semicircle, in the primitive that already drew the other
   one — the alternative was a second primitive differing from `tube` by a
   cap.

Nothing else. That is the point of a third domain: the first two paid for the
core, and this one mostly spends it.
"""

from .bacterium import Bacterium

__all__ = ["Bacterium"]

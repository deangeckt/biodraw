"""Model organisms as silhouettes.

The fifth domain package, and the one with the widest reach: nearly every
methods figure in biology opens with a mouse, a fly, a fish or a worm, and
what those figures need is not a photograph. It is a shape a reader names in
half a second, at the size the panel left for it, **facing the right way** —
which is the thing a stock library structurally cannot give you, because it
ships one file per view and they never match each other.

So `facing` is on the base class, `size` is on the base class, and each
animal's own knobs are the parts somebody would actually change: the mouse's
tail against its body, the fly's wings, the fish's body depth, how curled
the worm is.

House style, from the maintainer: *"use very simple drawings, not complex
realistic images, sometimes an outline is even enough."* Nothing in here has
interior detail beyond an eye, because at the centimetre these are printed at,
detail is bytes and attention spent on something no reader will see. The same
argument the library already made for axons, applied to whole organisms.

Where the proportions came from
-------------------------------
Reference figures, read as a **parts list and a set of proportions**, then
written as numbers in `forms.py`. Nothing here is traced off a downloaded
image and no reference image is committed — which is the rule in
`docs/RULES.md` for this category and also the only version that leaves a
shape with knobs: a traced JPEG scales and does nothing else.
"""

from .animal import Animal
from .forms import Fly, Mouse, Worm, Zebrafish

__all__ = ["Animal", "Fly", "Mouse", "Worm", "Zebrafish"]

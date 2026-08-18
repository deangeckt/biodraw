"""Domain-neutral drawing engine: paths, profiles, branches, rendering.

Nothing in here knows what a neuron is. The domain packages
(`biodraw.neuro`, `biodraw.cells`, ...) are built entirely on these pieces,
and a new domain should be too — if something cannot be expressed here, that
is a gap in the core rather than a reason to special-case it upstairs.
"""

from . import connectors, geom, paths, profile, render, scatter
from .branch import WIDTH_PER_DECORATION, Branch
from .connectors import connect, connect_tree, endcap
from .profile import Profile

# Importing the bundled profiles registers them by name, so
# `profile.get('spine')` works without the caller importing anything.
from .profiles import spine as _spine  # noqa: F401
from .render import FILL_ALPHA, blend, render_hollow, resolve_fill, shade
from .scatter import scatter_in
from .shape import Layer, Shape

__all__ = [
    "connectors", "geom", "paths", "profile", "render", "scatter",
    "Branch", "WIDTH_PER_DECORATION",
    "Profile", "Layer", "Shape",
    "render_hollow", "resolve_fill", "blend", "shade", "FILL_ALPHA",
    "scatter_in", "connect", "connect_tree", "endcap",
]

"""Bundled profiles.

Importing a module in here registers its profile by name (see
`biodraw.core.profile.register`), so anything that takes a profile can be
handed the string instead.

To add your own, trace it (`biodraw.trace`), then register it — either in your
own code or by contributing a module here. See `examples/01_spine/` for what a
well-documented profile looks like, including where the shape came from.
"""

from . import spine
from .spine import SPINE_POINTS

__all__ = ["spine", "SPINE_POINTS"]

"""The base every animal silhouette is built on.

Model organisms are the one category on `docs/PLAN.md` where what people need
to vary is **orientation**, not identity: a mouse facing left and a mouse
facing right are the same animal, and a stock library makes you download two
files that will not match. So `facing` is on the base class rather than on
any one animal, and it is a *mirror* — not a rotation, which would put the
animal on its back.

The other decision the base carries is the house style, and it came from the
maintainer: *"use very simple drawings, not complex realistic images,
sometimes an outline is even enough."* An animal here is a handful of fused
bodies and tubes with no interior detail — the silhouette that survives at
the size a methods figure actually prints it, which is about a centimetre.
Anything finer is bytes and attention spent on something the reader will
never see.

Subclasses implement `_forms()`, returning `(closed, open_)` in local units
**facing +x**, and may implement `_named()` for anchors that mean something
particular to that animal — a nose, a tail tip. The base mirrors both if
`facing` is negative, places them, and adds the generic `wall` anchors every
shape here exposes.
"""

import numpy as np

from ..core.anchor import Anchor, AnchorSet
from ..core.geom import support
from ..core.shape import Shape
from ..style.palette import get as get_palette

__all__ = ["Animal"]


class Animal(Shape):
    """A silhouette, facing `+1` (right) or `-1` (left).

      size        overall length, in local units. Every animal here is drawn
                  about 1 long by default, so a row of them at one `scale`
                  comes out at *drawn* sizes rather than true relative ones —
                  a fly beside a mouse at true scale is an invisible fly.
      facing      +1 or -1. Mirrors the whole animal about its own x axis.
      seed        fixes whatever wobble the animal has, so it regenerates.
    """

    edge = get_palette()["neutral"]

    #: Directions the generic `wall` anchors are taken along.
    WALL_DEGS = tuple(range(0, 360, 30))

    def __init__(self, size=1.0, facing=1, seed=0,
                 at=(0.0, 0.0), scale=1.0, rotate_deg=0.0):
        super().__init__(at=at, scale=scale, rotate_deg=rotate_deg)
        self.size = float(size)
        self.facing = -1 if float(facing) < 0 else 1
        self.seed = int(seed)

    # -- geometry ----------------------------------------------------------

    def _forms(self):
        """`(closed, open_)` in local units, drawn facing +x."""
        raise NotImplementedError

    def _named(self):
        """`[(name, xy, direction), ...]` in the same local units."""
        return []

    def _faced(self, points):
        """Local points at this animal's size, mirrored if it faces left."""
        p = np.asarray(points, dtype=float) * self.size
        return p * np.array([self.facing, 1.0])

    def _faced_dir(self, v):
        """A *direction* mirrored the same way — no size, or a normal drawn
        from `_named` would come back scaled and stop being a unit vector."""
        return np.asarray(v, dtype=float) * np.array([self.facing, 1.0])

    def _geometry(self):
        closed, open_ = self._forms()
        return {"closed": [self._faced(p) for p in closed],
                "open": [self._faced(p) for p in open_]}

    def _parts(self):
        g = self.geometry
        return ([self.to_world(p) for p in g["closed"]],
                [self.to_world(p) for p in g["open"]])

    # -- anchors -----------------------------------------------------------

    def _anchors(self):
        """`wall` all round the silhouette, plus whatever the animal names.

        The wall anchors are supporting points of the **union**, which is the
        only definition that works here: an animal is several fused bodies
        and a tube or two, and there is no single outline to walk.

        Taken over everything *drawn* — `self.points`, so layers count — and
        in **world** directions. Both halves were wrong first time round and
        the test caught it: the fly's wings are a layer rather than part of
        `_forms()`, so anchors computed from the geometry alone sat under its
        own wing, which is exactly where a label must not go.
        """
        pts = np.concatenate(self.points)
        out = AnchorSet()
        for deg in self.WALL_DEGS:
            d = np.array([np.cos(np.deg2rad(deg)), np.sin(np.deg2rad(deg))])
            out.append(Anchor(support(pts, d), d, "wall", deg=float(deg)))
        for name, xy, direction in self._named():
            out.append(Anchor(self.to_world(self._faced(xy)),
                              self.dir_to_world(self._faced_dir(direction)),
                              name))
        return out

    def __repr__(self):
        return (f"{type(self).__name__}(size={self.size:g}, "
                f"facing={self.facing:+d}, "
                f"at=({self.at[0]:.3g}, {self.at[1]:.3g}), "
                f"scale={self.scale:g})")

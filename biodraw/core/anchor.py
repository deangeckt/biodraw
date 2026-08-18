"""Anchors: named places on a shape that other things can attach to.

An `Anchor` is a point, the direction that leads *away* from the shape there,
and a name for what kind of place it is. That is the whole idea, and it is what
makes contributed shapes interoperate: connectors, synapse markers, leader
labels and scale bars all consume anchors, so a new cell type gets every one of
them the moment it exposes some.

Why the normal matters
----------------------
Everything that attaches to a shape has to stand *off* it by some clearance —
a dot beside a spine head, an arrowhead short of a soma wall, a label clear of
a dendrite. Without a direction, "clearance" has no meaning at an arbitrary
point on a curved outline, and callers end up hand-tuning an offset per
contact per figure. With one, `anchor.offset(gap)` is the same call wherever it
lands and at whatever angle the thing arrives.

Selecting
---------
Shapes expose `.anchor(kind, **sel)` for one and `.anchors(kind, **sel)` for
all of them. `rank` indexes into the ordered set, and negative indices count
from the far end — so `rank=-1` is the distal-most, whatever the shape's size:

    cell.anchor("spine", branch="apical", rank=-1)
    cell.anchor("soma", side=-1, t=0.40)
    cell.anchors("spine")
"""

import numpy as np

from .geom import unit

__all__ = ["Anchor", "AnchorSet", "select"]


class Anchor:
    """A place on a shape, and the way out of it.

      xy      the point itself, in world units.
      normal  unit vector pointing away from the shape — the direction to
              stand off along.
      kind    what sort of place this is ('spine', 'soma', 'shaft', 'axon',
              ...). Consumers use it to decide how to draw: a contact on a
              spine and one on a shaft are different claims and get different
              colours.
      meta    anything the shape wants to carry along — which branch, which
              parameter along it, the local radius. Free-form on purpose;
              a shape knows things about its own anatomy that the core does
              not need to model.
    """

    __slots__ = ("xy", "normal", "kind", "meta")

    def __init__(self, xy, normal, kind="point", **meta):
        self.xy = np.asarray(xy, dtype=float)
        self.normal = unit(normal)
        self.kind = str(kind)
        self.meta = meta

    def offset(self, gap):
        """The point `gap` away from the shape, along the outward normal.

        This is the one call that stands anything off anything: a dot off a
        spine head, a bar off a soma wall, a label off a dendrite.
        """
        return self.xy + self.normal * float(gap)

    def toward(self, point):
        """Whether `point` lies on the outward side of this anchor.

        Used to pick which of several equivalent anchors faces a given source
        — the spine on the side the axon is arriving from, rather than the one
        behind the cell.
        """
        return float(np.dot(np.asarray(point, dtype=float) - self.xy,
                            self.normal)) > 0.0

    def distance_to(self, point):
        """Straight-line distance from this anchor to `point`."""
        return float(np.linalg.norm(np.asarray(point, dtype=float) - self.xy))

    def rotated(self, matrix, about=(0.0, 0.0), scale=1.0, shift=(0.0, 0.0)):
        """This anchor under a local -> world map.

        Shapes build their anchors in local units and map them out with the
        same transform as their outlines, so the normal takes the rotation but
        neither the translation nor the scale.
        """
        about = np.asarray(about, dtype=float)
        shift = np.asarray(shift, dtype=float)
        xy = shift + about + (self.xy - about) @ np.asarray(matrix).T * scale
        return Anchor(xy, np.asarray(self.normal) @ np.asarray(matrix).T,
                      self.kind, **self.meta)

    def __repr__(self):
        extra = "".join(f", {k}={v!r}" for k, v in self.meta.items())
        return (f"Anchor({self.kind!r}, xy=({self.xy[0]:.3g}, "
                f"{self.xy[1]:.3g}){extra})")


class AnchorSet(list):
    """An ordered list of anchors, with the selectors shapes hand out.

    Ordering is the shape's own and is meaningful: spines run proximal to
    distal, soma anchors run apex to base. That is what makes `rank=-1` mean
    "the distal-most one" rather than "an arbitrary one".
    """

    def of_kind(self, kind):
        """Just the anchors of one kind."""
        return AnchorSet(a for a in self if a.kind == kind)

    def where(self, **sel):
        """Anchors whose `meta` matches every given key.

        A key the anchor does not carry never matches, so selecting on
        something a shape does not model returns nothing rather than
        everything.
        """
        return AnchorSet(
            a for a in self
            if all(a.meta.get(k) == v for k, v in sel.items())
        )

    def rank(self, k):
        """The `k`-th anchor; negative counts from the far end."""
        if not self:
            raise IndexError("no anchors to choose from")
        return self[int(k)]

    def nearest(self, point, facing=True):
        """The anchor closest to `point`.

        With `facing`, anchors pointing away from `point` are skipped where
        possible — a connector should land on the side of the shape it is
        arriving from, not reach around the back. If none face it, the plain
        nearest is returned rather than nothing.
        """
        if not self:
            raise IndexError("no anchors to choose from")
        pool = [a for a in self if a.toward(point)] if facing else list(self)
        return min(pool or list(self), key=lambda a: a.distance_to(point))

    def points(self):
        """(n, 2) array of just the positions."""
        return np.array([a.xy for a in self], dtype=float)


def select(anchors, rank=None, nearest=None, facing=True, **sel):
    """Pick one anchor out of `anchors`, the way every shape's `.anchor` does.

    The order of precedence is deliberate: filter on `sel` first, then take
    `rank` if given, then `nearest` if given, and otherwise the first. Sharing
    it here means a contributed shape does not have to reimplement — or
    subtly vary — the selection rules.
    """
    pool = AnchorSet(anchors).where(**sel) if sel else AnchorSet(anchors)
    if not pool:
        raise LookupError(f"no anchor matches {sel}")
    if rank is not None:
        return pool.rank(rank)
    if nearest is not None:
        return pool.nearest(nearest, facing=facing)
    return pool[0]

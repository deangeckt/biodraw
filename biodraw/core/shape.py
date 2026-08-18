"""The base every drawable shape is built on.

A shape is defined once in **local units**, around its own origin, and then
placed with `at` / `scale` / `rotate_deg`. Everything downstream — outlines,
anchors, the fitted axes — is built from already-transformed points, so no
part of a shape has to know where it ended up.

Subclasses implement two things:

    _geometry()   -> local geometry, as a dict of vertex arrays. Pure numpy;
                     no matplotlib, no colours, no drawing.
    _parts()      -> (closed outlines, open outlines) in world units, ready
                     for `render.render_hollow`.

and optionally `_anchors()` to expose named attachment points. Keeping
geometry separate from rendering is what lets the same shape be drawn, or
measured, or explained, without any of those knowing about the others.

A shape whose parts do not all fuse into one contour — a body with a nucleus
inside it, a row of cells meeting at shared walls — overrides `_layers()`
instead of `_parts()`. See `Layer`.
"""

import numpy as np

from .anchor import AnchorSet, select
from .geom import rot_matrix
from .render import render_hollow, resolve_fill

__all__ = ["Layer", "Shape"]


class Layer:
    """One render group: everything in it fuses, and it covers what is below.

    `render_hollow` fakes a boolean union over everything handed to it in a
    single call, which is exactly right for a shape that is one unbroken
    contour — a soma with its dendrites and every spine on them. It is exactly
    wrong for a part that has to sit *inside* another and still be seen: a
    nucleus unioned with its cell body vanishes into it, and two cells of an
    epithelium meeting at a shared wall fuse into one long cell.

    matplotlib has no boolean difference either, so "on top of" can only be
    said by making a second call at a higher zorder. A layer is that call.
    Shapes return a list of them, bottom first, from `_layers()`.

      closed / open_   the parts, exactly as `_parts()` returns them.
      name             appended to the shape's `gid`, so exported SVG carries
                       `blob.nucleus.wall` rather than one more anonymous
                       path.
      edge             wall colour for this layer alone. `None` takes what
                       `draw` was asked for.
      fill/fill_alpha  likewise for the interior. Raising `fill_alpha` on an
                       inner layer is how a nucleus reads as denser than the
                       cytoplasm around it *without* introducing a second hue:
                       the same ink, more of it.
      dz               z-offset from the shape's own `zorder`. `None` stacks
                       the layers in the order given, 0.1 apart —
                       `render_hollow` already puts 0.05 between its own two
                       passes, so a smaller step would interleave them and the
                       walls of one layer would land above the fill of the
                       next.
    """

    __slots__ = ("closed", "open_", "name", "edge", "fill", "fill_alpha", "dz")

    def __init__(self, closed=(), open_=(), name=None, edge=None, fill=None,
                 fill_alpha=None, dz=None):
        self.closed = list(closed)
        self.open_ = list(open_)
        self.name = name
        self.edge = edge
        self.fill = fill
        self.fill_alpha = fill_alpha
        self.dz = dz

    def __repr__(self):
        return (f"Layer({self.name!r}, closed={len(self.closed)}, "
                f"open={len(self.open_)})")


class Shape:
    """Placement, drawing and anchor lookup, shared by every shape.

      at          where the shape's origin lands, in world units.
      scale       how big it is drawn. Every local length is multiplied by
                  this, so one number resizes the whole shape coherently.
      rotate_deg  turned counter-clockwise about `at`. Applied inside the
                  local -> world map, so anchors and their normals come back
                  already rotated.
    """

    #: Default wall colour, overridden per domain.
    edge = "#111111"

    def __init__(self, at=(0.0, 0.0), scale=1.0, rotate_deg=0.0):
        self.at = np.asarray(at, dtype=float)
        self.scale = float(scale)
        self.rotate_deg = float(rotate_deg)
        self._geom = None
        self._cache = {}

    # -- the local -> world map -------------------------------------------

    @property
    def _matrix(self):
        return rot_matrix(self.rotate_deg)

    def to_world(self, points):
        """Local points to world: rotate about the origin, scale, translate."""
        p = np.asarray(points, dtype=float)
        return self.at + (p @ self._matrix.T) * self.scale

    def dir_to_world(self, v):
        """Local direction to world: the rotation only, no scale or shift."""
        return np.asarray(v, dtype=float) @ self._matrix.T

    def moved(self, at=None, scale=None, rotate_deg=None):
        """A copy of this shape placed somewhere else.

        Cheap: the geometry is rebuilt, but the parameters are not re-derived,
        so laying out a row of identical cells stays one line per cell.
        """
        import copy
        other = copy.copy(self)
        other.at = self.at if at is None else np.asarray(at, dtype=float)
        other.scale = self.scale if scale is None else float(scale)
        other.rotate_deg = (self.rotate_deg if rotate_deg is None
                            else float(rotate_deg))
        other._geom = None
        other._cache = {}
        return other

    # -- geometry ----------------------------------------------------------

    def _geometry(self):
        raise NotImplementedError

    def _parts(self):
        raise NotImplementedError

    def _layers(self):
        """The shape's render groups, bottom first.

        The default is a single layer holding everything `_parts()` returns,
        which is the right answer for any shape that draws as one unbroken
        contour. Override this instead of `_parts()` when some part has to
        *occlude* another rather than fuse with it — see `Layer` for why that
        needs a second render pass and cannot be said in one.
        """
        closed, open_ = self._parts()
        return [Layer(closed=closed, open_=open_)]

    def _anchors(self):
        return AnchorSet()

    @property
    def geometry(self):
        """The shape's local geometry, built once and cached."""
        if self._geom is None:
            self._geom = self._geometry()
        return self._geom

    @property
    def layers(self):
        """The shape's render groups, built once and cached."""
        if "layers" not in self._cache:
            self._cache["layers"] = list(self._layers())
        return self._cache["layers"]

    @property
    def parts(self):
        """Every world-unit outline the shape draws, as `(closed, open)`.

        Closed outlines fuse into the union; open ones are strokes whose far
        end stops rather than closing — see `render.render_hollow`.

        Flattened **across layers**, in layer order, because everything that
        consumes this — fitting the axes, the geometry pins, a caller
        measuring a drawing — wants all of the ink and does not care which
        pass put it down. Only `draw` needs the layers kept apart.
        """
        if "parts" not in self._cache:
            closed, open_ = [], []
            for layer in self.layers:
                closed += list(layer.closed)
                open_ += list(layer.open_)
            self._cache["parts"] = (closed, open_)
        return self._cache["parts"]

    @property
    def points(self):
        """Every drawn vertex, for fitting axes around the shape."""
        closed, open_ = self.parts
        return [p.vertices if hasattr(p, "vertices") else np.asarray(p)
                for p in list(closed) + list(open_)]

    # -- anchors -----------------------------------------------------------

    def anchors(self, kind=None, **sel):
        """Every anchor, optionally filtered by kind and metadata."""
        if "anchors" not in self._cache:
            self._cache["anchors"] = AnchorSet(self._anchors())
        found = self._cache["anchors"]
        if kind is not None:
            found = found.of_kind(kind)
        return found.where(**sel) if sel else found

    def anchor(self, kind=None, rank=None, nearest=None, facing=True, **sel):
        """One anchor. See `biodraw.core.anchor.select` for the rules."""
        return select(self.anchors(kind), rank=rank, nearest=nearest,
                      facing=facing, **sel)

    # -- drawing -----------------------------------------------------------

    def draw(self, ax, edge=None, fill=None, fill_alpha=None, wall_lw=1.0,
             alpha=1.0, bg="white", zorder=3, gid=None):
        """Render the shape onto `ax`.

          edge        the wall colour. `None` takes the class default.
          fill        the interior. `None` washes it with `edge` (the usual
                      case); `'white'` gives a hollow outline; anything else
                      is used as given.
          fill_alpha  how strongly that wash is inked, 0-1.
          wall_lw     wall thickness, **in points** — so it does not scale
                      with `scale`. See `biodraw.style` for per-medium presets.
          alpha       fades the shape by pre-blending onto `bg`, not by patch
                      transparency, so the union stays seamless. Anything
                      drawn underneath stays hidden.
          gid         names this shape's layers in exported SVG.

        A multi-layer shape gets one `render_hollow` call per layer, stacked
        in order, and each layer may override `edge` / `fill` / `fill_alpha`
        for itself. A single-layer shape — which is most of them — comes out
        of exactly the one call it always did.

        Returns the list of artists, bottom layer first.
        """
        from .render import blend

        edge = self.edge if edge is None else edge
        gid = gid or type(self).__name__.lower()

        artists = []
        for i, layer in enumerate(self.layers):
            lay_edge = edge if layer.edge is None else layer.edge
            lay_fill = fill if layer.fill is None else layer.fill
            lay_alpha = (fill_alpha if layer.fill_alpha is None
                         else layer.fill_alpha)
            artists += render_hollow(
                ax, list(layer.closed),
                fill=blend(resolve_fill(lay_fill, lay_alpha, lay_edge, bg),
                           alpha, bg),
                edge=blend(lay_edge, alpha, bg),
                wall_lw=wall_lw,
                zorder=zorder + (0.1 * i if layer.dz is None else layer.dz),
                open_parts=list(layer.open_),
                gid=f"{gid}.{layer.name}" if layer.name else gid,
            )
        return artists

    def fit(self, ax, pad=0.2):
        """Fit the axes around this shape, with `pad` in **local** units."""
        from ..io import fit as _fit
        return _fit(ax, self.points, pad=pad * self.scale)

    def __repr__(self):
        return (f"{type(self).__name__}(at=({self.at[0]:.3g}, "
                f"{self.at[1]:.3g}), scale={self.scale:g})")

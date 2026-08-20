"""The track: parts laid along an axis, each consuming its own width.

The one core addition the genetics inventory asked for, and it is deliberately
**not** a genetics primitive. "Lay glyphs left to right along a line, each
taking as much of the axis as it needs, in the order given" is a genetic
construct, a protein domain map, a chromosome ideogram, a gene model and a
timeline — the same object with different glyphs on it. `Sheet` distributes
*identical* cells across a span, which is a different problem: there, the
pitch is the input and the cells are interchangeable; here, each item brings
its own width and the order is the content.

What a glyph owes the track
---------------------------
Three things, and nothing about what it means:

    width           how much of the axis it consumes, in local units
    outline(x0)     `(closed, open_)` vertex arrays with its left edge at
                    `x0` and the axis at `y = 0`
    name / label    free text; the track carries them on its anchors so a
                    caller can put text where the glyph is

`Glyph` below is that contract as a base class. Anything satisfying it can go
on a track, which is what keeps this file domain-neutral: `biodraw.genetics`
supplies promoters and coding sequences, and the track has never heard of
either.

Text is not drawn here
----------------------
A construct is full of labels — `GOI`, `35S`, `4xUAS` — and none of them are
drawn by this module. Every glyph gets `label` and `tick` anchors above and
below it, and the figure writes its own text at them. That is the same line
the rest of the library draws: what a part *is called* is the author's claim,
and `annotate.label` (milestone 8) will render it against these anchors when
it exists.
"""

import numpy as np

from ..style.palette import get as get_palette
from .anchor import Anchor, AnchorSet
from .shape import Shape

__all__ = ["Glyph", "Track"]


class Glyph:
    """One item on a track. See the module docstring for the contract.

    Subclasses set `width` and implement `outline`. `label` is free text the
    track hands back on its anchors; `name` is what the glyph *is*, and shows
    up in `repr` and in the exported SVG's layer names.
    """

    name = "glyph"

    def __init__(self, width, label=None):
        self.width = float(width)
        self.label = label

    def outline(self, x0):
        """`(closed, open_)` for this glyph, left edge at `x0`."""
        raise NotImplementedError

    def __repr__(self):
        label = "" if self.label is None else f", label={self.label!r}"
        return f"{type(self).__name__}(width={self.width:.3g}{label})"


class Track(Shape):
    """Glyphs laid along an axis, on a backbone line.

      glyphs      in order, left to right. Each consumes its own `width`.
      gap         page left between neighbours, in local units. A run of
                  glyphs that touch reads as one long glyph, because the
                  union fuses them — the same reason `Sheet` cannot have a
                  zero gap.
      rail        half-width of the backbone line. `None` draws no backbone,
                  which is what a domain map on a protein wants.
      lead        how far the backbone runs past the first and last glyph.
                  Not decoration: a construct that starts exactly at its
                  first glyph reads as *the whole molecule*, and one with a
                  lead reads as a window onto a longer one, which is what a
                  construct diagram is claiming.

    Everything is in **one layer**, so the backbone and every glyph on it fuse
    into a single contour the way a soma and its dendrites do. Two glyphs
    closer than the line is thick would fuse into each other as well, which is
    what `gap` is for.
    """

    # A construct is line art: the ink slot rather than an identity colour,
    # because a promoter is not a *kind of thing* the way a cell class is.
    # Colour a track by all means — but from the figure's key, not from here.
    edge = get_palette()["ink"]

    def __init__(self, glyphs=(), gap=0.09, rail=0.020, lead=0.10,
                 at=(0.0, 0.0), scale=1.0, rotate_deg=0.0):
        super().__init__(at=at, scale=scale, rotate_deg=rotate_deg)
        self.glyphs = list(glyphs)
        self.gap = float(gap)
        self.rail = None if rail is None else float(rail)
        self.lead = float(lead)

    # -- layout ------------------------------------------------------------

    @property
    def spans(self):
        """`(x0, x1)` for each glyph, in local units, left to right.

        The layout *is* the primitive: a cursor that advances by each glyph's
        own width plus the gap. Everything else here is drawing.
        """
        out, x = [], 0.0
        for g in self.glyphs:
            out.append((x, x + g.width))
            x += g.width + self.gap
        return out

    @property
    def length(self):
        """Total width of the run, glyphs and gaps, without the leads."""
        spans = self.spans
        return spans[-1][1] if spans else 0.0

    def _geometry(self):
        closed, open_ = [], []
        for glyph, (x0, _x1) in zip(self.glyphs, self.spans, strict=True):
            c, o = glyph.outline(x0)
            closed += [np.asarray(p, dtype=float) for p in c]
            open_ += [np.asarray(p, dtype=float) for p in o]
        return {"glyphs": closed, "open": open_, "backbone": self._backbone()}

    def _backbone(self):
        """The line the run sits on, as a plain rectangle.

        Not a `tube`: walling a straight centreline gives it end caps, and a
        rounded cap on a 0.02 rail renders as a small spearhead at each end
        of the construct — an arrowhead nobody asked for, on the one part of
        the drawing that is making no claim at all. A backbone is a rule, so
        it is drawn as one.
        """
        if self.rail is None or not self.glyphs:
            return None
        x0, x1, r = -self.lead, self.length + self.lead, self.rail
        return np.array([[x0, -r], [x1, -r], [x1, r], [x0, r], [x0, -r]])

    def _parts(self):
        g = self.geometry
        closed = [self.to_world(p) for p in g["glyphs"]]
        if g["backbone"] is not None:
            closed.append(self.to_world(g["backbone"]))
        return closed, [self.to_world(p) for p in g["open"]]

    # -- anchors -----------------------------------------------------------

    def _anchors(self):
        """`label` above each glyph, `tick` below the run, plus the two ends.

        The two are deliberately not symmetric, and the asymmetry is what a
        construct figure actually does:

        **`label` hugs its own glyph.** A promoter stands 0.37 tall and a
        coding sequence 0.13, and a callout above either one wants to be just
        clear of *it* — put them on a shared line and the short glyph's name
        floats in space with nothing under it.

        **`tick` sits on a shared baseline**, the lowest point of the whole
        run. Below a track is where the row of names goes, and a row that
        steps up and down with each glyph's underside is not a row — the
        first draft of `examples/inducible_construct/` had the promoter's
        name inside the coding sequence next to it, because the promoter's
        own underside is the backbone.
        """
        out = AnchorSet()
        drawn = [(g, x0, x1,
                  np.concatenate([np.asarray(p, dtype=float)
                                  for p in [*g.outline(x0)[0],
                                            *g.outline(x0)[1]]]))
                 for g, (x0, x1) in zip(self.glyphs, self.spans, strict=True)]
        floor = min((pts[:, 1].min() for *_rest, pts in drawn),
                    default=-self.rail if self.rail else 0.0)
        for i, (glyph, x0, x1, pts) in enumerate(drawn):
            mid = 0.5 * (x0 + x1)
            meta = dict(index=i, name=glyph.name, label=glyph.label)
            out.append(Anchor(self.to_world((mid, pts[:, 1].max())),
                              self.dir_to_world((0.0, 1.0)), "label", **meta))
            out.append(Anchor(self.to_world((mid, floor)),
                              self.dir_to_world((0.0, -1.0)), "tick", **meta))
        if self.glyphs:
            out.append(Anchor(self.to_world((-self.lead, 0.0)),
                              self.dir_to_world((-1.0, 0.0)), "end", side=-1))
            out.append(Anchor(self.to_world((self.length + self.lead, 0.0)),
                              self.dir_to_world((1.0, 0.0)), "end", side=1))
        return out

    def __repr__(self):
        names = ", ".join(g.name for g in self.glyphs)
        return (f"Track([{names}], length={self.length:.3g}, "
                f"at=({self.at[0]:.3g}, {self.at[1]:.3g}))")

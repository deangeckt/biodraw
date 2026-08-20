"""Construct glyphs: the parts of a genetic construct, laid on a `Track`.

The vocabulary here is SBOL Visual's, reduced to the four glyphs that carry a
regulation figure: a repeat, a promoter, a coding sequence and a terminator.
Every one of them is a `core.track.Glyph` — a width and an outline — so the
track has never heard of genetics and this module has never heard of layout.

Read off figure 1 of doi.org/10.1016/j.tibtech.2023.03.007, not off the
field: the parts list came from the figure Dean supplied, which is why there
are no double helices, plasmid maps or exon structures in it. See
`docs/PLAN.md`, milestone 10.

What varies, and why that is the whole argument
-----------------------------------------------
Every knob below is a **count or a length that a person currently draws by
hand**: how many repeats are in the operator (`4xUAS`, `(etr)8` and `(C120)5`
are one glyph at three settings), how long a coding sequence is, which way it
reads. A stock asset cannot know any of them, which is the roster test this
category had to pass and a proteins category failed.

Two conventions worth knowing before reading the code
-----------------------------------------------------
**`strand=-1` mirrors a glyph about its own span**, so a reverse-oriented
gene is an argument rather than a second drawing — and because the mirror is
about the glyph's own centre, nothing downstream of it moves.

**Anything standing on the backbone is sunk into it** by `sink`, the same
move a dendrite makes into a soma: the stem starts *below* the line so the
two fuse into one contour instead of butting at a seam the union would draw.
"""

import numpy as np

from ..core.paths import round_polyline, rounded_ring, tube
from ..core.track import Glyph

__all__ = ["CDS", "Promoter", "Repeat", "Terminator"]

#: How far a glyph that stands on the backbone starts below it. It has to be
#: **shallower than the rail's half-width** (`Track.rail`, 0.020) or the stem
#: pokes out the underside of the line as a tick — visible at 0.03, which is
#: what the first draft used.
SINK = 0.012


def _flip(points, x0, width, strand):
    """Mirror a glyph's own points about the centre of its own span."""
    p = np.asarray(points, dtype=float)
    if strand >= 0:
        return p
    out = p.copy()
    out[:, 0] = 2.0 * x0 + width - out[:, 0]
    return out


def _box(x0, x1, y0, y1, radius=0.0):
    """An axis-aligned box, optionally with rounded corners."""
    verts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if radius <= 0:
        return np.asarray(verts + [verts[0]], dtype=float)
    return rounded_ring(verts, radius)


def _bent_arrow(x0, width, height, stroke, head, head_w, radius, sink=SINK):
    """A stem up off the backbone turning right into an arrowhead.

    Two parts, not one: the bent stem is a walled centreline (so the corner
    is a real fillet at a real width) and the head is a triangle. They fuse
    in the union, which is why the stem stops short of the tip — overlapping
    them would leave the arrow's shoulders inside the head.
    """
    # Inset by half the stroke, because the spine is a *centreline*: run it
    # up x0 itself and the wall lands 0.0175 to the left of the glyph's own
    # span, which the track then lays a neighbour into. Caught by
    # `test_every_glyph_stays_inside_its_own_span`.
    left = x0 + 0.5 * stroke
    spine = round_polyline(
        np.array([[left, -sink], [left, height],
                  [x0 + width - head, height]]),
        radius, n_arc=10)
    stem = tube(spine, np.full(len(spine), 0.5 * stroke))
    tip = np.array([[x0 + width - head, height + 0.5 * head_w],
                    [x0 + width, height],
                    [x0 + width - head, height - 0.5 * head_w]])
    return [stem, np.vstack([tip, tip[0]])]


class Repeat(Glyph):
    """An operator or binding site, drawn as `n` bars.

    A `CBS operator` at four bars, `4xUAS`, `(etr)8` and a gRNA binding site
    are this glyph at four settings of `n` — the clearest case on the page for
    parameters over assets, because the *number of repeats* is the biology and
    it is the one thing a downloaded icon fixes forever.

    The bars straddle the backbone rather than standing on it, so a repeat
    reads as part of the sequence rather than as something bound to it.
    """

    name = "repeat"

    def __init__(self, n=4, bar_w=0.05, bar_gap=0.045, height=0.26,
                 radius=0.015, label=None):
        n = max(1, int(n))
        self.n = n
        self.bar_w = float(bar_w)
        self.bar_gap = float(bar_gap)
        self.height = float(height)
        self.radius = float(radius)
        super().__init__(width=n * self.bar_w + (n - 1) * self.bar_gap,
                         label=label)

    def outline(self, x0):
        h = 0.5 * self.height
        step = self.bar_w + self.bar_gap
        return [_box(x0 + k * step, x0 + k * step + self.bar_w, -h, h,
                     self.radius) for k in range(self.n)], []


class Promoter(Glyph):
    """A promoter: the bent arrow that says transcription starts here.

    The one part of a construct diagram every reader can name, and the reason
    `strand` exists — a divergent promoter pair is this glyph twice, once
    mirrored.
    """

    name = "promoter"

    def __init__(self, width=0.30, height=0.30, stroke=0.035, head=0.10,
                 head_w=0.13, radius=0.05, label=None, strand=1):
        self.height = float(height)
        self.stroke = float(stroke)
        self.head = float(head)
        self.head_w = float(head_w)
        self.radius = float(radius)
        self.strand = int(np.sign(strand) or 1)
        super().__init__(width=width, label=label)

    def outline(self, x0):
        parts = _bent_arrow(x0, self.width, self.height, self.stroke,
                            self.head, self.head_w, self.radius)
        return [_flip(p, x0, self.width, self.strand) for p in parts], []


class CDS(Glyph):
    """A coding sequence: an arrow-box carrying a gene's name.

    `GOI`, `dCas9-VP64` and `Guide RNA` are this glyph at three widths. The
    pointed end is not decoration — it is the only thing in a construct
    diagram that says which way the gene is read, and a plain rectangle
    (`head=0`) drops that claim rather than simplifying it.
    """

    name = "cds"

    def __init__(self, width=0.62, height=0.26, head=0.13, radius=0.03,
                 label=None, strand=1):
        self.height = float(height)
        self.head = float(head)
        self.radius = float(radius)
        self.strand = int(np.sign(strand) or 1)
        super().__init__(width=width, label=label)

    def outline(self, x0):
        h, w = 0.5 * self.height, self.width
        head = min(self.head, w)
        if head <= 0:
            body = _box(x0, x0 + w, -h, h, self.radius)
        else:
            body = rounded_ring([(x0, -h), (x0 + w - head, -h),
                                 (x0 + w, 0.0), (x0 + w - head, h),
                                 (x0, h)], self.radius)
        return [_flip(body, x0, w, self.strand)], []


class Terminator(Glyph):
    """A terminator: the stem and crossbar that closes a track.

    Nothing about it varies with the biology — a terminator is a full stop —
    which is exactly why it is the cheapest glyph here and why it has no
    knobs beyond its size.
    """

    name = "terminator"

    def __init__(self, width=0.18, height=0.24, stroke=0.035, radius=0.01,
                 label=None):
        self.height = float(height)
        self.stroke = float(stroke)
        self.radius = float(radius)
        super().__init__(width=width, label=label)

    def outline(self, x0):
        mid, h, s = x0 + 0.5 * self.width, self.height, 0.5 * self.stroke
        return [_box(mid - s, mid + s, -SINK, h),
                _box(x0, x0 + self.width, h - self.stroke, h, self.radius)], []

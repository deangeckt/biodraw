"""The instrument a methods figure opens with.

Why this is drawn here at all, when `docs/SCOPE.md` says not to compete with
stock asset libraries: **a drawn microscope has counts in it.** Nobody needs
the same microscope at three objective counts from a download — they need
*their* nosepiece, *their* body, and it beside their data on a matplotlib
axes. Every knob below is something a person currently redraws by hand:

    objectives   n on the nosepiece — the one everybody redraws
    inverted     a different instrument, not a flipped one
    stage        present or not
    condenser    the sub-stage optics and the lamp under them
    camera       the port on top

Drawn as an outline, in the house schematic style — `docs/RULES.md` drawing
rule 7. A microscope at figure size is about two centimetres tall, and every
knurl and screw thread drawn on it is bytes and attention spent on something
the reader will never resolve. The parts list came off textbook schematics as
a set of proportions, nothing traced and nothing committed (drawing rule 6).

What is not a knob: binocular
-----------------------------
The inventory this was built from listed *monocular or binocular* as one of
the five things to vary, and it is not drawable here. Two eyepiece tubes are
separated **across the viewing axis** — into the page — so a strict side
elevation puts one exactly behind the other. Splayed far enough apart to be
seen they stop being a binocular head and become a pair of antennae.

Built anyway, and measured before it was cut: on the inverted body the flag
changed the drawing by **0.0%**, and on the upright it widened a single tube
by 11.6% with the two barrels still fused (0.057 apart, 0.076 wide) — so it
read as one fatter eyepiece rather than two. That is the zebrafish's three
stripes again (*a capability that only looks right at a size nobody views it
at is not a capability*) and the side-on fly (*projection is part of the
parts list*) in one knob. A figure that must say **binocular** should say it
in a word next to the drawing.

Upright against inverted
------------------------
These are **not** mirror images and the difference is the whole reason
`inverted` is a knob rather than two classes. On an upright the objectives
hang down onto the specimen from above and the light comes up through the
condenser from below. On an inverted the objectives look *up* at the
specimen from beneath the stage, and the illuminator rides a gantry over the
top — which is exactly why it can hold a culture flask, and why anyone
draws one.
"""

import numpy as np

from ..core.anchor import Anchor, AnchorSet
from ..core.geom import support
from ..core.paths import rounded_ring
from ..core.shape import Layer, Shape
from ..style.palette import get as get_palette

__all__ = ["Microscope"]


def _box(x0, y0, x1, y1, r=0.02):
    """A rounded rectangle as vertices. Most of an instrument is boxes."""
    return rounded_ring([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], r)


def _taper(x0, y0, x1, y1, top_in=0.0, r=0.015):
    """A box whose top edge is inset by `top_in` a side — a turret, a lamp."""
    return rounded_ring([(x0, y0), (x1, y0),
                         (x1 - top_in, y1), (x0 + top_in, y1)], r)


def _barrel(centre, deg, length, hw_top, hw_tip, r=0.012):
    """A short tapered tube leaving `centre` at `deg` from straight down.

    An objective and an eyepiece are the same solid: a stubby cone with its
    corners knocked off. Positive `deg` swings it clockwise.
    """
    t = np.deg2rad(deg)
    d = np.array([np.sin(t), -np.cos(t)])          # down, rotated
    n = np.array([d[1], -d[0]])
    c = np.asarray(centre, dtype=float)
    tip = c + d * length
    return rounded_ring([c - n * hw_top, c + n * hw_top,
                         tip + n * hw_tip, tip - n * hw_tip], r)


class Microscope(Shape):
    """A compound microscope, upright or inverted.

      size        overall height in local units; everything is drawn to about
                  1.0 tall, so a row of instruments at one `scale` matches.
      objectives  how many hang from (or point up at) the nosepiece. The knob
                  the shape exists for — 0 draws a bare turret.
      inverted    objectives below the stage and the lamp on a gantry above.
                  A different instrument, not a mirrored one.
      stage       draw the specimen stage.
      condenser   draw the sub-stage optics and the lamp housing under them
                  (upright), or the gantry head above (inverted).
      camera      a camera port standing off the top of the head.
    """

    edge = get_palette()["neutral"]

    #: Directions the generic `wall` anchors are taken along. Twelve, as
    #: everywhere else — a label wants somewhere to stand, not a contour.
    WALL_DEGS = tuple(range(0, 360, 30))

    #: Degrees between **adjacent** barrels — a step, not a total spread.
    #:
    #: This is `docs/RULES.md` drawing rule 3 one axis over: *a count spread
    #: over a length is a density*, and a count spread over an **angle** is
    #: an angular one. Held as a total half-spread of 18 deg, the step shrank
    #: as barrels were added — at `objectives=5` adjacent tips came out 0.023
    #: apart with a combined width of 0.032, so they fused into a lump you
    #: could not count. The knob the shape exists for stopped working at the
    #: settings it exists to show.
    #:
    #: 15 deg is the number that separates the *tips*: at the barrel length
    #: of 0.15 that is 0.039 between centres against 0.032 of barrel. Nearer
    #: the hub they still overlap, which is what a real nosepiece does.
    FAN_STEP_DEG = 15.0

    def __init__(self, size=1.0, objectives=3, inverted=False, stage=True,
                 condenser=True, camera=False,
                 at=(0.0, 0.0), scale=1.0, rotate_deg=0.0):
        super().__init__(at=at, scale=scale, rotate_deg=rotate_deg)
        self.size = float(size)
        self.objectives = max(0, int(objectives))
        self.inverted = bool(inverted)
        self.stage = bool(stage)
        self.condenser = bool(condenser)
        self.camera = bool(camera)

    # -- geometry ----------------------------------------------------------

    def _fan(self):
        """The angle of each objective, in order, left to right.

        One barrel points straight down rather than splitting the difference:
        a turret is *indexed*, and the one in use is the one on the optical
        axis. Two barrels straddling the axis would say no objective is
        engaged, which is not what any figure means.

        The consequence, kept on purpose: an **even** count comes out
        lopsided. There is no arrangement that both centres the fan and puts
        a barrel on the axis, and of the two the axis is the one that carries
        meaning — a nosepiece is a disc turned to a detent, and nothing says
        the idle barrels have to sit evenly either side of the one in use.
        """
        n = self.objectives
        k = (n - 1) // 2
        return [(i - k) * self.FAN_STEP_DEG for i in range(n)]

    def _layout(self):
        """Every number both the outline and the anchors depend on.

        One dict rather than two copies. The first version had `_forms` and
        `_named` each carrying their own turret centre and their own idea of
        which way an objective points, and they disagreed: the upright
        anchors came out pointing **up**, 0.14 above the turret, while the
        barrels were drawn hanging below it. Nothing could have caught that
        except reading the numbers, because both halves were internally
        consistent.

          turret      centre of the nosepiece disc
          obj_dir     +1 objectives hang down, -1 they look up
          obj_len     barrel length, tip to turret centre
          stage_y     the specimen surface — the face things sit on
          stage_x0    its far edge. Here because it is *not* recoverable
                      from the outline: the foot reaches further left than
                      the stage does, so the shape's leftmost wall anchor is
                      the base, and a caption that trusted it labelled the
                      wrong part
          eye, eye_deg, eye_len   the eyepiece root, angle and length
        """
        if self.inverted:
            return dict(turret=np.array([-0.015, 0.395]), obj_dir=-1.0,
                        obj_len=0.115, stage_y=0.560, stage_x0=-0.30,
                        eye=np.array([-0.255, 0.250]), eye_deg=180.0 - 38.0,
                        eye_len=0.225)
        return dict(turret=np.array([-0.015, 0.490]), obj_dir=1.0,
                    obj_len=0.150, stage_y=0.305, stage_x0=-0.28,
                    eye=np.array([-0.015, 0.690]), eye_deg=180.0 - 22.0,
                    eye_len=0.235)

    def _objectives(self, L):
        """The barrels, and the direction each points, from one layout.

        Long and thin, with the corner fillet almost off. At 0.032 half-width
        and a 0.012 fillet the three of them fused into a rounded lump that
        read as a paw — the radius was a quarter of the part it was rounding.
        A fillet has to be small *relative to the thing it is cutting*, and
        an objective is the smallest named part on the instrument.
        """
        out = []
        for deg in self._fan():
            # `_barrel` measures from straight *down*; an inverted turret
            # looks up, which is the same angle taken from straight up.
            swing = deg if L["obj_dir"] > 0 else 180.0 - deg
            out.append(_barrel(L["turret"], swing, L["obj_len"],
                               0.024, 0.016, r=0.006))
        return out

    def _upright(self, L):
        """Base, arm, head; optics hanging down onto a lit stage.

        Slim, not blocky. The first pass drew the arm 0.20 wide and the head
        0.52 by 0.18, and the two fused into an L-shaped slab with a few
        nubs on it — an instrument-shaped bracket. A microscope's silhouette
        is a **tall column with a heavy foot**, and the parts that identify
        it are small: the angled eyepiece, the fan of barrels, the thin
        stage.
        """
        closed = [
            _box(-0.30, 0.0, 0.34, 0.060, r=0.018),         # foot
            _box(0.22, 0.04, 0.32, 0.700, r=0.026),         # arm
            _box(-0.06, 0.620, 0.32, 0.700, r=0.022),       # head
            _box(-0.06, 0.500, 0.03, 0.660, r=0.016),       # body tube
            _taper(-0.10, 0.455, 0.07, 0.515, top_in=0.020, r=0.010),
        ]
        closed += self._objectives(L)
        if self.stage:
            closed.append(_box(L["stage_x0"], L["stage_y"] - 0.036, 0.26,
                               L["stage_y"], r=0.008))
        if self.condenser:
            closed.append(_taper(-0.085, 0.185, 0.045, 0.262, top_in=0.022,
                                 r=0.010))
            closed.append(_box(-0.095, 0.052, 0.055, 0.190, r=0.014))
        closed.append(_barrel(L["eye"], L["eye_deg"], L["eye_len"],
                              0.050, 0.042))
        if self.camera:
            closed.append(_barrel(np.array([0.135, 0.700]), 180.0, 0.20,
                                  0.036, 0.044, r=0.010))
        return closed

    def _inverted(self, L):
        """Optics under the stage looking up, and the lamp on a gantry.

        The body is deep and low because on an inverted scope the optical
        train lives *in* the base — which is as much the instrument's tell
        as the barrels pointing the wrong way.
        """
        closed = [
            _box(-0.30, 0.0, 0.32, 0.265, r=0.026),         # deep body
            _box(0.20, 0.24, 0.32, 0.570, r=0.026),         # rear column
            _taper(-0.09, 0.330, 0.06, 0.400, top_in=-0.018, r=0.010),
        ]
        closed += self._objectives(L)
        if self.stage:
            closed.append(_box(L["stage_x0"], L["stage_y"], 0.24,
                               L["stage_y"] + 0.038, r=0.008))
        if self.condenser:
            closed.append(_box(0.21, 0.570, 0.31, 0.930, r=0.026))
            closed.append(_box(-0.055, 0.855, 0.31, 0.930, r=0.022))
            closed.append(_taper(-0.055, 0.740, 0.045, 0.865,
                                 top_in=-0.022, r=0.010))
        closed.append(_barrel(L["eye"], L["eye_deg"], L["eye_len"],
                              0.050, 0.042))
        if self.camera:
            closed.append(_box(0.30, 0.050, 0.48, 0.170, r=0.022))
        return closed

    def _geometry(self):
        L = self._layout()
        forms = self._inverted(L) if self.inverted else self._upright(L)
        body = [np.asarray(p, dtype=float) * self.size for p in forms]
        # The focus knob is a *marking*, not a part: fused into the arm it
        # disappears, and stroked at the body's own wall weight it reads as a
        # pipe laid across the instrument rather than a control.
        knob_c = np.array([0.27, 0.190] if not self.inverted
                          else [0.26, 0.130]) * self.size
        t = np.linspace(0.0, 2.0 * np.pi, 48, endpoint=False)
        knob = knob_c + np.stack([np.cos(t), np.sin(t)], 1) * 0.045 * self.size
        return {"body": body, "knob": knob}

    def _layers(self):
        g = self.geometry
        return [
            Layer([self.to_world(p) for p in g["body"]], [], name="body"),
            Layer([self.to_world(g["knob"])], [], name="knob",
                  wall_lw="0.8x", fill_alpha=0.0),
        ]

    # -- anchors -----------------------------------------------------------

    def _named(self):
        """The places a figure points at, all read off `_layout`."""
        L = self._layout()
        up, down = np.array([0.0, 1.0]), np.array([0.0, -1.0])
        out = [("stage", np.array([-0.09, L["stage_y"]
                                   + (0.042 if self.inverted else 0.0)]), up)]
        for i, deg in enumerate(self._fan()):
            swing = np.deg2rad(deg if L["obj_dir"] > 0 else 180.0 - deg)
            d = np.array([np.sin(swing), -np.cos(swing)])
            out.append((f"objective{i}", L["turret"] + d * L["obj_len"], d))
        t = np.deg2rad(L["eye_deg"])
        d = np.array([np.sin(t), -np.cos(t)])
        out.append(("eyepiece", L["eye"] + d * L["eye_len"], d))
        out.append(("base", np.array([0.0, 0.0]), down))
        return out

    def _anchors(self):
        """`wall` all round the union, plus the named places.

        Supporting points of everything *drawn*, for the reason the animals
        found the hard way: a shape whose parts live in more than one layer
        has no single outline to walk, and anchors taken off the geometry
        alone land under something.
        """
        pts = np.concatenate(self.points)
        out = AnchorSet()
        for deg in self.WALL_DEGS:
            d = np.array([np.cos(np.deg2rad(deg)), np.sin(np.deg2rad(deg))])
            out.append(Anchor(support(pts, d), d, "wall", deg=float(deg)))
        for i, (name, xy, direction) in enumerate(self._named()):
            kind = "objective" if name.startswith("objective") else name
            meta = {"rank": i} if kind == "objective" else {}
            out.append(Anchor(self.to_world(np.asarray(xy) * self.size),
                              self.dir_to_world(direction), kind, **meta))
        return out

    def __repr__(self):
        return (f"Microscope(size={self.size:g}, "
                f"objectives={self.objectives}, "
                f"{'inverted' if self.inverted else 'upright'}, "
                f"at=({self.at[0]:.3g}, {self.at[1]:.3g}))")

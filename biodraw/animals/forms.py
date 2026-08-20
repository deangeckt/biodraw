"""Four model organisms as silhouettes: mouse, fly, zebrafish, worm.

Nearly every methods figure in biology opens with one of these, and what a
figure needs is not a photograph — it is a shape the reader names in half a
second, at whatever size the panel left for it, pointing the right way. So
each of these is an outline built from the same core primitives as everything
else: superellipse bodies, `Branch` tubes for tails and legs, and one union.

Each one's knobs are the parts a reader would actually change: how long the
mouse's tail is, whether the fly has its wings, how many stripes the fish
carries, how curled the worm is. Identity is carried by the **silhouette**,
which is why none of these needs colour to be told apart — the same rule the
neurons are drawn under.

Proportions were read off reference figures and then written as numbers here;
nothing is traced, and no reference image is committed. That is the rule in
`docs/PLAN.md` for this whole category: a reference is a parts list and a set
of proportions, and a shape that came from tracing a downloaded picture has
no knobs.
"""

import numpy as np

from ..core.branch import Branch
from ..core.paths import bowed_ring, rounded_ring, superellipse, tube
from ..core.shape import Layer
from .animal import Animal

__all__ = ["Fly", "Mouse", "Worm", "Zebrafish"]


def _blob(a, b, at, squareness=2.4, deg=0.0, wobble=0.0, phase=0.0):
    """A superellipse body, turned and placed — the workhorse here."""
    from ..core.geom import rot_matrix
    ring = superellipse(a, b, squareness, wobble=wobble, wobble_n=3,
                        wobble_phase=phase)
    return ring @ rot_matrix(deg).T + np.asarray(at, dtype=float)


def _limb(origin, direction, length, w0, w1, bend=0.0, n=40):
    """A short tapered tube — a leg, an antenna, a fin ray."""
    br = Branch(origin, direction, length=length, bend=bend, wave_amp=0.0,
                n_pts=n)
    return tube(br.centre, np.linspace(w0, w1, n))


class Mouse(Animal):
    """A mouse in side view: body, head, ear, tail, two legs.

    The tail is the knob that matters and the reason this is a shape rather
    than an icon — a mouse drawn with a stub reads as a vole, and the tail's
    length against the body is exactly what a comparative figure varies.
    """

    def __init__(self, tail=0.78, ear=1.0, plump=1.0, legs=True, **kw):
        self.tail = float(tail)
        self.ear = float(ear)
        self.plump = float(plump)
        self.legs = bool(legs)
        super().__init__(**kw)

    def _forms(self):
        closed = [
            _blob(0.40, 0.25 * self.plump, (-0.08, 0.0), squareness=2.9,
                  deg=-4.0, wobble=0.02, phase=0.15),          # body
            _blob(0.19, 0.155, (0.36, 0.04), squareness=2.2, deg=-16.0),
            # A snout, because an ellipse head has no nose and a mouse is
            # mostly recognised by the wedge at the front of it.
            _blob(0.115, 0.075, (0.53, -0.03), squareness=2.0, deg=-14.0),
            _blob(0.115 * self.ear, 0.105 * self.ear, (0.275, 0.265),
                  squareness=2.0),                             # ear
        ]
        if self.legs:
            closed += [
                _limb((0.20, -0.14), (0.30, -1.0), 0.24, 0.055, 0.045),
                _limb((-0.22, -0.14), (-0.18, -1.0), 0.26, 0.070, 0.048),
            ]
        # The tail runs off and stops: an open end, like a dendrite's tip.
        br = Branch((-0.42, 0.03), (-1.0, 0.22), length=self.tail,
                    bend=-0.16, wave_amp=0.02, wave_per=0.6, n_pts=70)
        open_ = [tube(br.centre, np.linspace(0.036, 0.010, 70),
                      base_ext=0.05, open_end=True)]
        return closed, open_

    def _named(self):
        return [("nose", (0.645, -0.03), (1.0, 0.0)),
                ("tail", (-0.42 - self.tail, 0.20), (-1.0, 0.2))]


class Fly(Animal):
    """A fly in side view: head, thorax, abdomen, wings, legs.

    Wings are a separate layer rather than part of the union, because a wing
    laid over an abdomen has to still *have* an edge where it crosses it —
    fused, the two become one blob and the drawing loses the one feature that
    says insect.
    """

    def __init__(self, wings=True, legs=3, **kw):
        self.wings = bool(wings)
        self.legs = max(0, int(legs))
        super().__init__(**kw)

    def _body(self):
        return [
            # Abdomen: tapered and tipped down, which is what makes the
            # three-part body read as an insect rather than as a bean.
            _blob(0.27, 0.165, (-0.26, -0.06), squareness=2.6, deg=-10.0),
            _blob(0.20, 0.185, (0.10, 0.01), squareness=2.5),   # thorax
            _blob(0.115, 0.115, (0.36, 0.02), squareness=2.2),  # head
        ]

    def _forms(self):
        closed = self._body()
        # Legs leave the underside of the thorax and bend back, the way a
        # standing fly's do. Straight spokes read as a spider.
        for k in range(self.legs):
            closed.append(_limb((0.18 - 0.15 * k, -0.13),
                                (0.45 - 0.34 * k, -1.0), 0.26 - 0.015 * k,
                                0.024, 0.011, bend=0.06))
        return closed, []

    def _wing(self, lift, length):
        """A leaf, not an ellipse.

        A fly's wing is a teardrop rooted at the thorax and widest two-thirds
        of the way out. Drawn as an ellipse it reads as a balloon tied to the
        insect, which is what the first two drafts of this looked like.
        """
        return bowed_ring([(0.05, 0.055 + lift),
                           (-length, 0.115 + lift),
                           (-0.62 * length, 0.005 + lift)],
                          [0.09, 0.035, 0.07], n_per_edge=20)

    def _layers(self):
        """Body first, then the wings over it, then the eye."""
        closed, open_ = self._parts()
        layers = [Layer(closed=closed, open_=open_, name="body")]
        if self.wings:
            wings = [self.to_world(self._faced(self._wing(*a)))
                     for a in ((-0.02, 0.50), (-0.075, 0.44))]
            layers.append(Layer(closed=wings, name="wings", fill="white",
                                wall_lw="0.8x"))
        # A fly is mostly eye, and that is the one interior mark it gets.
        eye = self.to_world(self._faced(_blob(0.075, 0.080, (0.40, 0.03))))
        layers.append(Layer(closed=[eye], name="eye", fill_alpha=0.75))
        return layers

    def _named(self):
        return [("head", (0.475, 0.02), (1.0, 0.0))]


class Zebrafish(Animal):
    """A zebrafish in side view: body, three fins, stripes.

    The stripes are a count, and that is the argument for drawing rather than
    downloading one: a figure comparing wild type with a striping mutant
    needs the same fish at two stripe numbers, which no asset can give. They
    are drawn as bars trimmed to the body outline, in their own layer.
    """

    def __init__(self, stripes=4, fins=True, depth=1.0, **kw):
        self.stripes = max(0, int(stripes))
        self.fins = bool(fins)
        self.depth = float(depth)
        super().__init__(**kw)

    def _body_ring(self):
        """Nose, back, peduncle, belly.

        Seven vertices rather than five: with five the back ran straight from
        the shoulder to the tail and the fish came out a blimp. The narrowing
        behind the dorsal fin — the caudal peduncle — is most of what says
        *fish*, and it needs its own vertex on each side.
        """
        d = self.depth
        return bowed_ring(
            [(0.50, 0.015), (0.14, 0.135 * d), (-0.14, 0.095 * d),
             (-0.36, 0.035), (-0.36, -0.035), (-0.12, -0.075 * d),
             (0.16, -0.115 * d)],
            [0.07, 0.02, 0.015, 0.0, 0.015, 0.02, 0.07], n_per_edge=22)

    def _forms(self):
        closed = [self._body_ring()]
        if self.fins:
            closed += [
                # caudal: a notched triangle off the peduncle
                rounded_ring([(-0.33, 0.035), (-0.54, 0.135), (-0.46, 0.0),
                              (-0.54, -0.135), (-0.33, -0.035)], 0.02),
                # dorsal, raked back the way a swimming fish's is
                rounded_ring([(-0.04, 0.115), (-0.17, 0.205), (0.10, 0.13)],
                             0.02),
                # pelvic
                rounded_ring([(0.04, -0.10), (-0.04, -0.185),
                              (0.16, -0.11)], 0.02),
            ]
        return closed, []

    def _stripe_bars(self):
        """Horizontal bars trimmed to the body's own outline.

        A stripe has to end where the fish does. There is no clipping in the
        renderer — `render_hollow` unions, it does not intersect — so the
        trim is arithmetic: cross the body ring with the stripe's centre line
        and take the span between the outermost crossings.
        """
        ring = self._body_ring()
        bars, ys = [], np.linspace(0.068, -0.050, self.stripes)
        for y in ys:
            xs = []
            for (x0, y0), (x1, y1) in zip(ring, np.roll(ring, -1, axis=0),
                                          strict=True):
                if (y0 - y) * (y1 - y) < 0:
                    xs.append(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
            if len(xs) < 2:
                continue
            lo, hi = min(xs), max(xs)
            inset = 0.075 + 0.05 * abs(y)
            lo, hi = lo + inset, hi - inset
            if hi - lo < 0.05:
                continue
            h = 0.007
            bars.append(rounded_ring([(lo, y - h), (hi, y - h),
                                      (hi, y + h), (lo, y + h)], 0.012))
        return bars

    def _layers(self):
        closed, open_ = self._parts()
        layers = [Layer(closed=closed, open_=open_, name="body")]
        if self.stripes:
            bars = [self.to_world(self._faced(b)) for b in self._stripe_bars()]
            # Solid, not washed: at this size a stripe is two wall strokes
            # with a sliver of fill between them, and a washed one reads as a
            # grey pipe laid on the fish rather than as a marking in it.
            layers.append(Layer(closed=bars, name="stripes", fill_alpha=1.0,
                                wall_lw=0.0))
        eye = self.to_world(self._faced(_blob(0.030, 0.028, (0.315, 0.042))))
        layers.append(Layer(closed=[eye], name="eye", fill_alpha=0.8))
        return layers

    def _named(self):
        return [("nose", (0.50, 0.02), (1.0, 0.0)),
                ("tail", (-0.55, 0.0), (-1.0, 0.0))]


class Worm(Animal):
    """*C. elegans*: one tapered tube on a curved centreline.

    The whole animal is a spindle — widest in the middle, coming to a point
    at both ends — so it is the one shape in the library that wants a width
    profile rather than a taper, and the cheapest silhouette here by a long
    way. `curl` bends it and `waves` sets how many times it crosses its own
    axis, which is what separates a moving worm from a dead straight one.
    """

    def __init__(self, waves=1.4, curl=0.10, girth=1.0, **kw):
        self.waves = float(waves)
        self.curl = float(curl)
        self.girth = float(girth)
        super().__init__(**kw)

    def _forms(self):
        n = 160
        br = Branch((-0.5, 0.0), (1.0, 0.0), length=1.0, bend=self.curl,
                    wave_amp=0.085, wave_n=self.waves, wave_phase=0.0,
                    n_pts=n)
        t = np.linspace(0.0, 1.0, n)
        # A spindle, not a taper: sin^0.55 is round through the middle and
        # comes to a point at both ends without a visible corner.
        hw = 0.045 * self.girth * np.sin(np.pi * t) ** 0.55
        return [tube(br.centre, np.maximum(hw, 1e-4))], []

    def _named(self):
        return [("head", (0.5, 0.0), (1.0, 0.0)),
                ("tail", (-0.5, 0.0), (-1.0, 0.0))]

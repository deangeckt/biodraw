"""Four model organisms as silhouettes: mouse, fly, zebrafish, worm.

Nearly every methods figure in biology opens with one of these, and what a
figure needs is not a photograph — it is a shape the reader names in half a
second, at whatever size the panel left for it, pointing the right way. So
each of these is an outline built from the same core primitives as everything
else: superellipse bodies, `Branch` tubes for tails and legs, and one union.

Each one's knobs are the parts a reader would actually change: how long the
mouse's tail is, whether the fly has its wings, how deep the fish's body
is, how curled the worm is. Identity is carried by the **silhouette**,
which is why none of these needs colour to be told apart — the same rule the
neurons are drawn under.

Proportions were read off reference figures and then written as numbers here;
nothing is traced, and no reference image is committed. That is the rule in
`docs/RULES.md` for this whole category: a reference is a parts list and a set
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
    """A fly seen from above: head, two eyes, thorax, abdomen, wings, legs.

    **Dorsal, where the other three are in side view.** *"the fly in the
    animals sections doesnt look like one"*, with a reference of the clean
    top-down fly every methods figure uses. The side view was the mistake:
    from the side a fly is a lumpy bean with a dark blob at one end, and the
    two features a reader actually names it by — the pair of eyes and the two
    wings spread behind — are edge-on and invisible. Projection is part of
    the parts list, and for this animal the recognisable one is from above.

    It costs nothing structurally: drawn head-to-`+x` like everything else
    here, `facing` still mirrors it correctly, so it sits in a row beside the
    side-view animals without special-casing.

    Wings are a separate layer rather than part of the union, because a wing
    laid over the abdomen has to still *have* an edge where it crosses it —
    fused, the two become one blob and the drawing loses the one feature that
    says insect.
    """

    def __init__(self, wings=True, legs=3, **kw):
        self.wings = bool(wings)
        #: Legs **per side** — a fly has three, and they mirror.
        self.legs = max(0, int(legs))
        super().__init__(**kw)

    #: Eye centres, as `(x, |y|)`. They are in the union *and* marked on top:
    #: from above a fly's eyes are most of the head's outline, so an eye that
    #: is only an interior blob sits on the drawing rather than in it.
    EYE_AT = (0.300, 0.057)

    def _eye(self, side):
        return _blob(0.070, 0.050, (self.EYE_AT[0], self.EYE_AT[1] * side),
                     squareness=2.1, deg=-20.0 * side)

    def _body(self):
        return [
            # Abdomen: the long taper at the back, and narrower than the
            # thorax. Squareness near 2 keeps it a true oval — at 2.7 the
            # sides run straight and it came out a blunt rectangle, which
            # reads as a beetle and buried the wings behind it.
            _blob(0.22, 0.120, (-0.28, 0.0), squareness=2.1),
            # The waist. Without it the thorax and abdomen union into one
            # bean and the animal loses its three-part body — which was most
            # of why the old drawing read as a mammal.
            _blob(0.085, 0.052, (-0.07, 0.0), squareness=2.2),
            # Thorax: the widest thing on the animal, and the only part that
            # is wider than it is long. Get this backwards and it reads ant.
            _blob(0.175, 0.155, (0.10, 0.0), squareness=2.4),
            # The head is a wide capsule *across* the body, because from
            # above a fly's head is the pair of eyes and little else. Wide
            # enough to contain them: eyes that stand out past the head
            # silhouette read as two balloons stuck on the front.
            _blob(0.085, 0.113, (0.295, 0.0), squareness=2.3),
        ]

    def _forms(self):
        closed = self._body()
        # Three legs a side, leaving the thorax: front pair forward, middle
        # pair out, hind pair back. All six are drawn because a fly seen from
        # above shows all six, and drawing three was most of why the old one
        # looked like a quadruped.
        for side in (+1, -1):
            for k in range(self.legs):
                closed.append(_limb(
                    (0.18 - 0.11 * k, 0.10 * side),
                    (0.55 - 0.55 * k, 1.0 * side), 0.30 - 0.02 * k,
                    0.021, 0.010, bend=0.05 * side))
        return closed, []

    def _wing(self, side, length=0.62):
        """A leaf, not an ellipse.

        A fly's wing is a teardrop rooted at the thorax and widest two-thirds
        of the way out. Drawn as an ellipse it reads as a balloon tied to the
        insect, which is what the first two drafts of this looked like. The
        pair sweeps back and outward past the abdomen tip — a wing that stops
        short of the abdomen reads as a beetle's case.

        The far wing is the near wing mirrored in y, rather than the same
        construction with `side` multiplied through it. Mirroring the
        *vertices* reverses the ring's handedness, so the bulges bow the
        wrong way and the two wings come out different shapes — which is
        exactly what the first dorsal draft did.
        """
        ring = bowed_ring([(0.12, 0.055), (-0.29 - 0.63 * length, 0.27),
                           (-0.24, 0.030)],
                          [0.115, 0.050, 0.045], n_per_edge=22)
        return ring if side > 0 else ring * np.array([1.0, -1.0])

    def _layers(self):
        """Wings *under* the body, then the body, then the eyes.

        Over the body the wings are two opaque leaves laid across the animal
        and the abdomen disappears under them — which is what the first
        dorsal draft did. Underneath, the body occludes them exactly where a
        real wing passes behind it, and what is left showing is the part that
        says insect.
        """
        closed, open_ = self._parts()
        layers = []
        if self.wings:
            wings = [self.to_world(self._faced(self._wing(s)))
                     for s in (+1, -1)]
            layers.append(Layer(closed=wings, name="wings", fill="white",
                                wall_lw="0.8x"))
        layers.append(Layer(closed=closed, open_=open_, name="body"))
        # A fly is mostly eye, and from above that is *two* of them, meeting
        # near the midline. They are the interior mark that carries the
        # animal: covered up, the silhouette could be any winged insect.
        eyes = [self.to_world(self._faced(self._eye(s))) for s in (+1, -1)]
        layers.append(Layer(closed=eyes, name="eyes", fill_alpha=0.75))
        return layers

    def _named(self):
        return [("head", (0.380, 0.0), (1.0, 0.0))]


class Zebrafish(Animal):
    """A zebrafish in side view: body and three fins.

    **The stripes are gone.** *"why is the zebrafish is having 3 stripes? no
    need i think."* They were four horizontal bars trimmed to the body, and
    the argument for them was that a stripe *count* is the knob no downloaded
    asset can give you. That argument was true and still lost: at catalog
    size the bars did not follow the body's taper, stopped abruptly inboard
    of the outline, and the middle one ran through the eye — so the feature
    that was supposed to justify the shape was the worst-looking thing on it.
    A capability that only looks right at a size nobody views it at is not a
    capability. The fish reads as a fish from its silhouette, which is the
    rule the rest of this module is drawn under.
    """

    def __init__(self, fins=True, depth=1.0, **kw):
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

    def _layers(self):
        closed, open_ = self._parts()
        layers = [Layer(closed=closed, open_=open_, name="body")]
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

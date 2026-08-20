"""Proteins: a lobed body with domain tags stuck to it.

The other half of the regulation figure. Where the construct track says *what
is encoded*, this says *what the product does* — and in every figure of this
kind that is a body with named domains hanging off it, opening or closing
around a ligand.

Three things vary, and they are the three the figure varies:

* **how many lobes.** One is an oval (`HIF1α`, `dCas9`); two is the clamshell
  that closes around an ion (`CUP2`); three or more is a complex.
* **how far open.** `open_deg` hinges the lobes apart. The figure draws the
  same protein twice, open and closed, and that pair *is* its claim — so it
  has to be one parameter, or the two drawings drift apart.
* **which domains are on it.** `tags` is a list of angles: `Gal4-TAD`,
  `Gal4-DBD`, `VP16`, `SRDX`, `LOV`, `HTH` are the same glyph with different
  text, and how many there are is the biology.

The ligand is not here. A `Cu2+` or an `O2` in these figures is a filled dot,
and a dot is not a shape — it is a mark at an anchor, which is the call this
library already made for synapses. `Protein.anchor('cleft')` is where it
goes, and the figure draws it in one line, in whatever colour its own key
says.
"""

import numpy as np

from ..core.anchor import Anchor, AnchorSet
from ..core.geom import rot, rot_matrix
from ..core.paths import rounded_ring, superellipse
from ..core.shape import Shape
from ..style.palette import get as get_palette

__all__ = ["Protein"]


class Protein(Shape):
    """A protein body, drawn as fused lobes with domain tags on its rim.

    Body
      lobes        how many lobes fuse into the body.
      radius       a lobe's short semi-axis, in local units.
      aspect       its long semi-axis, x `radius`. Lobes are elongated along
                   the direction they point, so a two-lobed body reads as a
                   clamshell rather than as two circles.
      open_deg     the angle between neighbouring lobes. Small values close
                   the body around the cleft; large ones open it. Past about
                   90 with two lobes the lobes stop overlapping and the union
                   would break into two bodies, so it is clamped.
      reach        how far each lobe's centre sits from the hinge, x
                   `radius`. This is what keeps the lobes overlapping at the
                   base whatever `open_deg` does.
      squareness   superellipse exponent, as everywhere else. 2 is an
                   ellipse.
      wobble       swells each lobe's wall, seeded per lobe so two lobes of
                   one body are not the same lobe twice (drawing rule 1).

    Domains
      tags         angles, in degrees, at which domain tags leave the body.
                   `Protein(tags=(35.0, 145.0))` is a body carrying two.
      tag_len /
      tag_w        the tag's size. A tag is deliberately a plain rounded box:
                   what makes it a `VP16` rather than a `SRDX` is the text
                   the figure writes at the `tag` anchor, not its shape.
      tag_sink     how far the tag is buried in the body, so the two fuse
                   into one contour instead of butting.
    """

    edge = get_palette()["tertiary"]

    #: Two lobes stop overlapping past this, and the body would come apart.
    MAX_OPEN_DEG = 96.0

    def __init__(self, lobes=2, radius=0.20, aspect=1.55, open_deg=42.0,
                 reach=0.62, squareness=2.1, wobble=0.035,
                 tags=(), tag_len=0.20, tag_w=0.13, tag_sink=0.05,
                 tag_radius=0.03, face_deg=90.0, seed=0,
                 at=(0.0, 0.0), scale=1.0, rotate_deg=0.0):
        super().__init__(at=at, scale=scale, rotate_deg=rotate_deg)
        self.lobes = max(1, int(lobes))
        self.radius = float(radius)
        self.aspect = float(aspect)
        self.open_deg = float(np.clip(open_deg, 0.0, self.MAX_OPEN_DEG))
        self.reach = float(reach)
        self.squareness = float(squareness)
        self.wobble = float(wobble)
        self.face_deg = float(face_deg)
        self.tags = tuple(float(t) for t in tags)
        self.tag_len = float(tag_len)
        self.tag_w = float(tag_w)
        self.tag_sink = float(tag_sink)
        self.tag_radius = float(tag_radius)
        self.seed = int(seed)

    # -- geometry ----------------------------------------------------------

    def _lobe_degs(self):
        """Which way each lobe points, spread about `face_deg`."""
        n = self.lobes
        return [self.face_deg + (k - (n - 1) / 2.0) * self.open_deg
                for k in range(n)]

    def _geometry(self):
        rng = np.random.default_rng(self.seed)
        lobes = []
        for deg in self._lobe_degs():
            ring = superellipse(self.radius * self.aspect, self.radius,
                                self.squareness, wobble=self.wobble,
                                wobble_n=3,
                                wobble_phase=float(rng.random()))
            # Turned onto its own direction, then pushed out from the hinge —
            # which stays at the origin, so every lobe still overlaps every
            # other one there and the union is a single contour.
            centre = rot((1.0, 0.0), deg) * (self.reach * self.radius
                                             * self.aspect)
            lobes.append(ring @ rot_matrix(deg).T + centre)
        body = np.concatenate(lobes)
        return {"lobes": lobes,
                "cleft": self._cleft(lobes),
                "tags": [self._tag(body, deg) for deg in self.tags]}

    def _cleft(self, lobes):
        """Where a ligand sits: the deepest point inside **every** lobe.

        That one definition covers both halves of the pair the figure draws.
        Open, the lobes overlap only near the hinge, so it lands at the
        bottom of the notch, where an ion is about to be caught. Closed, they
        overlap most of the way out, so it lands further along the face axis
        — inside the body, which is where the ion has gone.

        A single-lobed protein has no cleft, and gets the middle of itself
        rather than a pretend one.
        """
        from matplotlib.path import Path

        d = rot((1.0, 0.0), self.face_deg)
        # Past the far tip of a lobe (its centre is `reach` out and it is one
        # semi-axis long), or the walk ends while still inside the body and
        # every opening reports the same depth — which is what the first
        # version did, at 2.2 x `reach` alone.
        far = (self.reach + 1.15) * self.radius * self.aspect
        ray = d * np.linspace(0.0, far, 240)[:, None]
        if len(lobes) == 1:
            inside = Path(lobes[0], closed=True).contains_points(ray)
        else:
            inside = np.ones(len(ray), dtype=bool)
            for lobe in lobes:
                inside &= Path(lobe, closed=True).contains_points(ray)
        hits = np.nonzero(inside)[0]
        return ray[hits[-1]] if len(hits) else np.zeros(2)

    def _support(self, body, deg):
        """The outermost drawn point in direction `deg`, and that direction.

        A tag has to start *on* the rim of a union of overlapping lobes, and
        the union has no closed form here. The supporting point — the vertex
        furthest along the direction — is on the rim by construction,
        whatever the lobes are doing, which is the cheap correct answer.
        """
        d = rot((1.0, 0.0), deg)
        return body[np.argmax(body @ d)], d

    def _tag(self, body, deg):
        """One domain tag: a rounded box standing off the rim at `deg`."""
        p, d = self._support(body, deg)
        n = np.array([-d[1], d[0]])
        base = p - d * self.tag_sink
        far = base + d * self.tag_len
        hw = 0.5 * self.tag_w
        return rounded_ring([base - n * hw, far - n * hw,
                             far + n * hw, base + n * hw], self.tag_radius)

    def _parts(self):
        g = self.geometry
        return [self.to_world(p) for p in [*g["lobes"], *g["tags"]]], []

    # -- anchors -----------------------------------------------------------

    def _anchors(self):
        """`tag` at the far end of each domain, `cleft` where a ligand sits,
        and `wall` round the body for connectors and labels."""
        g = self.geometry
        body = np.concatenate(g["lobes"])
        out = AnchorSet()

        for i, deg in enumerate(self.tags):
            p, d = self._support(body, deg)
            out.append(Anchor(self.to_world(p + d * self.tag_len),
                              self.dir_to_world(d), "tag", index=i,
                              deg=float(deg)))

        out.append(Anchor(self.to_world(g["cleft"]),
                          self.dir_to_world(rot((1.0, 0.0), self.face_deg)),
                          "cleft"))

        for deg in range(0, 360, 30):
            p, d = self._support(body, float(deg))
            out.append(Anchor(self.to_world(p), self.dir_to_world(d),
                              "wall", deg=float(deg)))
        return out

    def __repr__(self):
        return (f"Protein(lobes={self.lobes}, open_deg={self.open_deg:g}, "
                f"tags={len(self.tags)}, "
                f"at=({self.at[0]:.3g}, {self.at[1]:.3g}))")

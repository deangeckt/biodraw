"""The generic cell: a wall, a nucleus, and whatever is loose in between.

The shape every biology textbook opens with, and the first thing in this
library that is *not* one unbroken outline. A pyramidal cell is a single
contour — soma, dendrites and spines all fusing — because that is what the
hand drawing it came from does. A cell with a nucleus in it cannot be: union
the nucleus with the body and it disappears into the body's own fill. So this
is the shape that made `core.shape.Layer` necessary, and the layer stack here
is the whole of what it needed.

Built entirely on `biodraw.core`. The wall and the nucleus are `superellipse`
rings, the organelles are small ones scattered by `core.scatter`, and the
protrusions are `Branch` tubes — the same engine that draws a dendrite, doing
microvilli instead, which is the claim about domain-neutrality being cashed.
"""

import numpy as np

from ..core.anchor import Anchor, AnchorSet
from ..core.branch import Branch
from ..core.geom import rot, unit
from ..core.paths import superellipse, superellipse_radius, tube
from ..core.scatter import scatter_in
from ..core.shape import Layer, Shape
from ..style.palette import get as get_palette

__all__ = ["Blob"]


class Blob(Shape):
    """A cartoon cell body.

    Body
      radius           semi-axis along x, in local units. The one size knob;
                       everything else below is a fraction of it, so changing
                       it rescales the whole cell coherently.
      aspect           semi-axis along y, x `radius`. 1.0 is round; below it
                       the cell lies down.
      squareness       superellipse exponent. 2 is a plain ellipse and 4 a
                       rounded box; the 2.4-3 window is a cell that has
                       settled against its neighbours without looking drafted.
      wobble           swells and pinches the wall by that fraction of the
                       radius, over `wobble_n` cycles. This is what keeps the
                       outline from reading as a primitive — at 0 it is
                       visibly an equation. Past ~0.08 it reads as damage
                       rather than as a hand.
      wobble_n         how many swells go round. Low numbers read as a cell
                       resting against something; high ones as a crenellated
                       membrane.

    Nucleus
      nucleus          nuclear radius, x the body radius. `None` or 0 leaves
                       the cell anucleate, which is a real thing to want (a
                       red cell, a platelet) and not just a degenerate case.
      nucleus_at       where its centre sits, in body radii from the cell's
                       own centre. Off-centre by default: a nucleus dead in
                       the middle of a symmetrical body reads as a target.
      nucleus_aspect / nucleus_squareness / nucleus_wobble
                       the same three shape knobs as the body, for the
                       nucleus.
      nucleolus        nucleolar radius, x the *nuclear* radius. 0 for none.

    Cytoplasm
      organelles       how many to scatter. Drawn as small elongated
                       superellipses at seeded angles — deliberately generic,
                       since calling them mitochondria would be a claim this
                       shape has no way to support.
      organelle_size   their long semi-axis, x the body radius.
      organelle_aspect their short semi-axis, x the long one.
      organelle_sep    the closest two may sit, x the body radius. This is
                       what stops them clumping; `scatter_in` raises rather
                       than quietly placing fewer, so a count that will not
                       fit is something you hear about.
      seed             the scatter and the organelle angles. Same seed, same
                       cell, forever.

    Membrane
      protrusions      short tubes out of the wall — microvilli, filopodia or
                       pseudopodia, depending on the length and width given.
                       They fuse with the body, so they grow out of it rather
                       than sitting on it.
      protrusion_len / protrusion_width
                       x the body radius.
      protrusion_arc_deg / protrusion_start_deg
                       the sweep of wall they cover, and where it starts
                       (counter-clockwise from +x). The default is all the
                       way round; a narrower arc puts a brush border on one
                       face and leaves the rest bare.
      protrusion_jitter
                       how far each one wanders off its even slot and away
                       from the nominal length, as a fraction of each. 0
                       spaces them exactly, which is the look of a gear
                       rather than of a membrane — evenly repeated parts are
                       the single loudest tell that a drawing was generated.

    `geom_kw` passes anything else through to the protrusion branches
    (`bend`, `wave_amp`, `wave_n`, ...).
    """

    edge = get_palette()["ink"]

    # How strongly each inner layer is washed. A nucleus has to read as denser
    # than the cytoplasm around it, and the honest way to say that is more of
    # the same ink — not a second hue, which would claim the nucleus is a
    # different *kind* of thing rather than a thicker part of the same one.
    # See `style.palette` on identity colours versus claim colours.
    WASH = {"body": None, "organelles": 0.26, "nucleus": 0.30,
            "nucleolus": 0.55}
    # Where the wall anchors sit, in degrees counter-clockwise from +x. Eight,
    # so several connectors can land on one cell without stacking, and on the
    # diagonals as well as the axes because a squarish body has its corners
    # there and a connector aimed at a corner should find one.
    WALL_DEGS = tuple(range(0, 360, 45))

    def __init__(self, radius=0.55, aspect=0.88, squareness=2.6,
                 wobble=0.028, wobble_n=5, wobble_phase=0.20,
                 nucleus=0.34, nucleus_at=(-0.16, 0.14), nucleus_aspect=0.92,
                 nucleus_squareness=2.3, nucleus_wobble=0.030,
                 nucleolus=0.36,
                 organelles=6, organelle_size=0.17, organelle_aspect=0.44,
                 organelle_sep=0.34, seed=0,
                 protrusions=0, protrusion_len=0.30, protrusion_width=0.085,
                 protrusion_arc_deg=360.0, protrusion_start_deg=0.0,
                 protrusion_jitter=0.28,
                 at=(0.0, 0.0), scale=1.0, rotate_deg=0.0, geom_kw=None):
        super().__init__(at=at, scale=scale, rotate_deg=rotate_deg)
        self.radius = float(radius)
        self.aspect = float(aspect)
        self.squareness = float(squareness)
        self.wobble = float(wobble)
        self.wobble_n = int(wobble_n)
        self.wobble_phase = float(wobble_phase)

        self.nucleus = 0.0 if nucleus is None else float(nucleus)
        self.nucleus_at = np.asarray(nucleus_at, dtype=float)
        self.nucleus_aspect = float(nucleus_aspect)
        self.nucleus_squareness = float(nucleus_squareness)
        self.nucleus_wobble = float(nucleus_wobble)
        self.nucleolus = 0.0 if nucleolus is None else float(nucleolus)

        self.organelles = int(organelles)
        self.organelle_size = float(organelle_size)
        self.organelle_aspect = float(organelle_aspect)
        self.organelle_sep = float(organelle_sep)
        self.seed = int(seed)

        self.protrusions = int(protrusions)
        self.protrusion_len = float(protrusion_len)
        self.protrusion_width = float(protrusion_width)
        self.protrusion_arc_deg = float(protrusion_arc_deg)
        self.protrusion_start_deg = float(protrusion_start_deg)
        self.protrusion_jitter = float(protrusion_jitter)
        self.geom_kw = dict(geom_kw or {})

    # -- geometry ----------------------------------------------------------

    @property
    def semi(self):
        """`(a, b)` semi-axes of the body wall, in local units."""
        return self.radius, self.radius * self.aspect

    def wall_radius(self, deg):
        """Distance from the centre out to the wobbled wall, at `deg`.

        The plain `superellipse_radius` is the un-wobbled wall, so anything
        rooted with it — a protrusion, a wall anchor — floats a little off a
        wobbled outline or sinks into it. Re-applying the same swell here is
        what keeps them on it, and it has to be the *same* expression as
        `superellipse` uses or they drift apart the moment a phase changes.
        """
        a, b = self.semi
        d = rot((1.0, 0.0), deg)
        r = superellipse_radius(d, a, b, self.squareness)
        return d, r * (1.0 + self.wobble
                       * np.sin(self.wobble_n * np.deg2rad(deg)
                                + 2 * np.pi * self.wobble_phase))

    def _branch_kw(self, **over):
        # A microvillus is short, so it gets less than one cycle of waver. The
        # waver is a sine whose cycle count does not scale with length, so the
        # same `wave_n` that reads as a hand on a long dendrite reads as a
        # corkscrew on a stub — the identical trap that threw the apical fork
        # off by 39.5 degrees. See `Branch.child` on `relative_to`.
        kw = dict(bend=0.06, wave_amp=0.012, wave_n=0.7, wave_phase=0.25,
                  n_pts=24)
        kw.update({k: v for k, v in self.geom_kw.items() if k in kw})
        kw.update(over)
        return kw

    def _geometry(self):
        """Local geometry: the wall, the nucleus, what is scattered inside
        it, and the protrusions."""
        a, b = self.semi
        # One stream for the whole cell, drawn from in a fixed order, so that
        # `seed` names a cell rather than a rendering of one.
        rng = np.random.default_rng(self.seed)
        wall = superellipse(a, b, self.squareness, wobble=self.wobble,
                            wobble_n=self.wobble_n,
                            wobble_phase=self.wobble_phase)

        nucleus = nucleolus = None
        centre = self.nucleus_at * self.radius
        if self.nucleus > 0:
            nr = self.nucleus * self.radius
            nucleus = centre + superellipse(
                nr, nr * self.nucleus_aspect, self.nucleus_squareness,
                wobble=self.nucleus_wobble, wobble_n=3, wobble_phase=0.55)
            if self.nucleolus > 0:
                # Off-centre inside the nucleus, for the same reason the
                # nucleus is off-centre inside the cell.
                nnr = self.nucleolus * nr
                nucleolus = (centre + np.array([0.22 * nr, -0.18 * nr])
                             + superellipse(nnr, nnr * 0.92, 2.2,
                                            wobble=0.05, wobble_n=4))

        return {"wall": wall,
                "nucleus": nucleus,
                "nucleus_centre": centre,
                "nucleolus": nucleolus,
                "organelles": self._organelles(wall, nucleus, rng),
                "protrusions": self._protrusions(rng)}

    def _organelles(self, wall, nucleus, rng):
        """Small rings loose in the cytoplasm.

        The margin from the wall is one organelle length rather than a fixed
        number: at any body size an organelle then stays wholly inside the
        cell instead of poking out through the membrane, which is the one way
        this can go visibly wrong.
        """
        if self.organelles <= 0:
            return []
        size = self.organelle_size * self.radius
        centres = scatter_in(
            wall, self.organelles, seed=rng,
            min_sep=self.organelle_sep * self.radius,
            margin=size, exclude=[] if nucleus is None else [nucleus],
            exclude_margin=size)
        # Angles off the same stream, so one `seed` fixes the whole cell.
        angles = rng.uniform(0.0, 180.0, size=len(centres))
        out = []
        for c, ang in zip(centres, angles, strict=True):
            ring = superellipse(size, size * self.organelle_aspect, 2.6,
                                wobble=0.04, wobble_n=3)
            rad = np.deg2rad(ang)
            m = np.array([[np.cos(rad), -np.sin(rad)],
                          [np.sin(rad), np.cos(rad)]])
            out.append({"outline": c + ring @ m.T, "centre": c,
                        "angle_deg": float(ang)})
        return out

    def _protrusions(self, rng):
        """Tubes out of the wall, rooted just inside it.

        Each is rooted back inside the wall along its own outward direction,
        so the tube's flat base is swallowed by the body's fill and the two
        fuse. That is the same trick a basal dendrite uses on a soma corner,
        which is why it lives in `paths.tube` and not in either domain.

        Placed on even slots and then knocked off them. Exactly even spacing
        with exactly equal lengths is the same mistake as a mirror-image
        bifurcation, one level down: a repeated part that repeats perfectly
        reads as machined. `protrusion_jitter` at 0 is the gear.
        """
        if self.protrusions <= 0:
            return []
        n = self.protrusions
        # A full turn wraps, so the last protrusion must not land on the
        # first: divide by n. A partial arc has two ends and wants one at
        # each: divide by n-1.
        full = abs(self.protrusion_arc_deg) >= 359.999
        step = self.protrusion_arc_deg / (n if full or n == 1 else n - 1)
        j = self.protrusion_jitter

        out = []
        for k in range(n):
            # Half the step is the most a slot can move without swapping with
            # its neighbour, so the jitter is scaled to that and the order
            # round the wall is preserved whatever it is set to.
            deg = (self.protrusion_start_deg + step * k
                   + rng.uniform(-1.0, 1.0) * j * 0.5 * step)
            d, r = self.wall_radius(deg)
            width = self.protrusion_width * self.radius
            length = (self.protrusion_len * self.radius
                      * (1.0 + rng.uniform(-1.0, 1.0) * j))
            br = Branch(origin=d * (r - width), direction=d,
                        length=length + width,
                        **self._branch_kw(bend=0.06 * (-1) ** k))
            out.append({"branch": br, "width": width, "deg": float(deg)})
        return out

    # -- rendering ---------------------------------------------------------

    def _layers(self):
        """Four groups, bottom first.

        The body and its protrusions fuse into one contour, so they share a
        layer. Everything inside the cell has to *occlude* that contour rather
        than join it — a nucleus unioned with the body is a nucleus you cannot
        see — so each gets a layer of its own.
        """
        g = self.geometry
        layers = [Layer(
            closed=[self.to_world(g["wall"])],
            open_=[self.to_world(tube(p["branch"].centre, p["width"],
                                      open_end=True))
                   for p in g["protrusions"]],
            fill_alpha=self.WASH["body"])]

        if g["organelles"]:
            layers.append(Layer(
                closed=[self.to_world(o["outline"]) for o in g["organelles"]],
                name="organelles", fill_alpha=self.WASH["organelles"]))
        if g["nucleus"] is not None:
            layers.append(Layer(closed=[self.to_world(g["nucleus"])],
                                name="nucleus",
                                fill_alpha=self.WASH["nucleus"]))
        if g["nucleolus"] is not None:
            layers.append(Layer(closed=[self.to_world(g["nucleolus"])],
                                name="nucleolus",
                                fill_alpha=self.WASH["nucleolus"]))
        return layers

    # -- anchors -----------------------------------------------------------

    def _anchors(self):
        """Named places: round the wall, on the nuclear envelope, one per
        organelle, and the tip of every protrusion."""
        g = self.geometry
        out = AnchorSet()

        for deg in self.WALL_DEGS:
            d, r = self.wall_radius(deg)
            out.append(Anchor(self.to_world(d * r), self.dir_to_world(d),
                              "wall", deg=float(deg)))

        if g["nucleus"] is not None:
            c = g["nucleus_centre"]
            nr = self.nucleus * self.radius
            for deg in (90.0, 270.0):
                d = rot((1.0, 0.0), deg)
                r = superellipse_radius(d, nr, nr * self.nucleus_aspect,
                                        self.nucleus_squareness)
                out.append(Anchor(self.to_world(c + d * r),
                                  self.dir_to_world(d), "nucleus",
                                  deg=float(deg)))

        for k, o in enumerate(g["organelles"]):
            # Outward from the cell's own centre — the direction a leader line
            # should leave in to clear the rest of the cytoplasm. The zero case
            # is guarded rather than left to `unit`: an organelle can land
            # exactly on the centre, and a figure should not die of it.
            v = o["centre"]
            n = unit(v) if np.linalg.norm(v) > 1e-12 else np.array([0.0, 1.0])
            out.append(Anchor(self.to_world(o["centre"]),
                              self.dir_to_world(n), "organelle", rank=k))

        for k, p in enumerate(g["protrusions"]):
            xy, tang = p["branch"].at(1.0)
            out.append(Anchor(self.to_world(xy), self.dir_to_world(tang),
                              "tip", rank=k, deg=p["deg"]))
        return out

    def __repr__(self):
        return (f"Blob(radius={self.radius:g}, organelles={self.organelles}, "
                f"protrusions={self.protrusions}, "
                f"at=({self.at[0]:.3g}, {self.at[1]:.3g}), "
                f"scale={self.scale:g})")

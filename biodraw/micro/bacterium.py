"""Bacteria: a capsule body, and the appendages that tell them apart.

The third domain on `biodraw.core`, and the first whose body is a **tube**
rather than a ring. `Blob` and `Sheet` are both closed outlines with things
inside them; a bacillus is a centreline with a width, which is the same object
a dendrite is — so this shape is mostly `paths.tube` with both ends capped,
and the interesting part is that it needed almost nothing new.

Why the forms are knobs and not a list
--------------------------------------
The textbook names — coccus, bacillus, vibrio, spirillum — describe one axis
each: how long the body is, how far it bends, how many times it twists. Given
those three as numbers, every named form is a setting and the ones in between
are drawable too, which is what this library is for. An enum would have made
the four names the only reachable shapes and turned the space between them
into dead code.

    coccus      length=0
    bacillus    length=1.4, curve_deg=0
    vibrio      length=1.4, curve_deg=70
    spirillum   length=2.0, twists=1.8

Flagellar arrangement is the same story, and reuses `Blob`'s vocabulary
exactly: a count over an arc of the outline, with 0 degrees at one pole and
180 at the other. Monotrichous, amphitrichous, lophotrichous and peritrichous
are then four settings of two numbers rather than four keywords.
"""

import numpy as np

from ..core.anchor import Anchor, AnchorSet
from ..core.branch import Branch
from ..core.geom import perp, unit
from ..core.paths import superellipse, tube
from ..core.scatter import scatter_in
from ..core.shape import Layer, Shape
from ..style.palette import get as get_palette

__all__ = ["Bacterium"]


class Bacterium(Shape):
    """A cartoon bacterial cell.

    Body
      length          the body's length along its own axis, in local units,
                      not counting the two hemispherical caps. **0 is a
                      coccus** — a capsule of zero length is a circle, so the
                      round form is the degenerate case of the rod rather
                      than a shape of its own.
      width           the body's width. The caps are semicircles of half
                      this, so a rod's overall length is `length + width`.
      curve_deg       how far the axis bends over its own length. 0 is a
                      straight rod; ~70 is the comma of a vibrio. The bend is
                      a circular arc, so the width stays honest along it.
      twists          helical turns along the body — a spirillum, drawn the
                      way a helix projects into two dimensions, as a wave.
      twist_amp       how far that wave swings, x `width`.
      taper           the far pole's width as a multiple of the near pole's.
                      1.0 is a proper capsule; below it the cell comes to a
                      blunter end at one side, which is what tells a
                      club-shaped cell from a rod.

    Envelope
      capsule         a slime layer outside the wall, thick by that multiple
                      of `width`. 0 for none. Drawn *under* the body in its
                      own layer and washed lighter, so the body reads as
                      sitting inside it rather than as a second outline.

    Contents
      nucleoid        the nucleoid, as a fraction of the body's half-width. A
                      bacterium has no nucleus, and drawing one would be the
                      single loudest error this shape could make — so this
                      follows the body's own centreline as a shrunken tube,
                      which is both what a nucleoid looks like and impossible
                      to mistake for a nuclear envelope.
      granules        inclusions scattered in the cytoplasm, via
                      `core.scatter` — the same sampler that fills a `Blob`.
      granule_size / granule_sep
                      x the body's half-width.
      seed            fixes the granules and every jitter below.

    Appendages
      flagella        how many, drawn as long thin `Branch` tubes: the waver
                      that makes a dendrite look hand-drawn, turned up until
                      it is the whole shape.
      flagella_arc_deg / flagella_start_deg
                      where they leave, as a sweep of the outline measured
                      from the +axis pole. **0 is one pole and 180 the
                      other**, which is what makes the four textbook
                      arrangements two numbers:

                        monotrichous   flagella=1, arc=0
                        amphitrichous  flagella=2, arc=360
                        lophotrichous  flagella=4, arc=70, start=-35
                        peritrichous   flagella=9, arc=360

      flagellum_len   x the body's overall span.
      flagellum_width x `width`.
      flagellum_waves how many cycles of waver over one flagellum. Turned
                      into a *wavelength* before it reaches `Branch`, so the
                      jittered ones stay equally wavy per unit of themselves.
      pili            fimbriae: many more, much shorter, much straighter.
      pili_len / pili_width / pili_arc_deg / pili_start_deg
                      as for the flagella.
      jitter          how far each appendage wanders off its even slot and
                      away from its nominal length, as a fraction of each. A
                      run of identical hairs on identical centres is the
                      loudest tell that a drawing was generated.
    """

    edge = get_palette()["ink"]

    # Same principle as `Blob.WASH`: an inner part reads as denser by taking
    # more of the same ink, never a second hue. The capsule goes the other
    # way — it is *outside* the wall and must read as looser than the cell.
    WASH = {"capsule": 0.10, "nucleoid": 0.26, "granules": 0.46}
    # Where the wall anchors sit, as a sweep from the +axis pole. The poles
    # themselves get their own kind, so these are the eight round the body.
    WALL_DEGS = tuple(range(0, 360, 45))
    #: Centreline resolution. Enough that a spirillum's wave is smooth and the
    #: outline's own normals are usable for placing appendages.
    N_CENTRE = 160

    def __init__(self, length=1.40, width=0.42, curve_deg=0.0,
                 twists=0.0, twist_amp=0.55, twist_phase=0.0, taper=1.0,
                 capsule=0.0,
                 nucleoid=0.0, granules=0, granule_size=0.30,
                 granule_sep=0.75, seed=0,
                 flagella=0, flagella_arc_deg=0.0, flagella_start_deg=0.0,
                 flagellum_len=1.15, flagellum_width=0.085,
                 flagellum_waves=2.6,
                 pili=0, pili_arc_deg=360.0, pili_start_deg=0.0,
                 pili_len=0.30, pili_width=0.045,
                 jitter=0.30,
                 at=(0.0, 0.0), scale=1.0, rotate_deg=0.0, geom_kw=None):
        super().__init__(at=at, scale=scale, rotate_deg=rotate_deg)
        self.length = float(length)
        self.width = float(width)
        self.curve_deg = float(curve_deg)
        self.twists = float(twists)
        self.twist_amp = float(twist_amp)
        self.twist_phase = float(twist_phase)
        self.taper = float(taper)

        self.capsule = float(capsule)

        self.nucleoid = float(nucleoid)
        self.granules = int(granules)
        self.granule_size = float(granule_size)
        self.granule_sep = float(granule_sep)
        self.seed = int(seed)

        self.flagella = int(flagella)
        self.flagella_arc_deg = float(flagella_arc_deg)
        self.flagella_start_deg = float(flagella_start_deg)
        self.flagellum_len = float(flagellum_len)
        self.flagellum_width = float(flagellum_width)
        self.flagellum_waves = float(flagellum_waves)

        self.pili = int(pili)
        self.pili_arc_deg = float(pili_arc_deg)
        self.pili_start_deg = float(pili_start_deg)
        self.pili_len = float(pili_len)
        self.pili_width = float(pili_width)

        self.jitter = float(jitter)
        self.geom_kw = dict(geom_kw or {})

    # -- the body ----------------------------------------------------------

    @property
    def half_w(self):
        """Half the body's width, which is also the radius of its caps."""
        return 0.5 * self.width

    @property
    def span(self):
        """The cell's overall extent along its own axis, caps included.

        The size reference for everything hung off it. A coccus has
        `length == 0`, so an appendage scaled on `length` alone would vanish
        on exactly the form where it is most visible.
        """
        return self.length + self.width

    def _centreline(self):
        """The body's axis: a straight line, bent into an arc, then waved.

        The three body knobs compose here rather than switching between
        forms, which is the whole reason a vibrio with a twist in it is
        drawable at all.
        """
        t = np.linspace(0.0, 1.0, self.N_CENTRE)
        # A capsule of zero length is a circle, and the caps supply all of it.
        # `np.gradient` needs distinct points to find a direction, so the
        # degenerate case is nudged rather than special-cased — at 1e-4 of the
        # width it is four orders below anything drawn.
        length = max(self.length, 1e-4 * self.width)

        theta = np.deg2rad(self.curve_deg)
        if abs(theta) < 1e-9:
            c = np.column_stack([(t - 0.5) * length, np.zeros_like(t)])
        else:
            # An arc of the same arclength, so bending a cell does not also
            # stretch it. Centred so the midpoint sits at the origin with its
            # tangent along +x, whatever the bend.
            r = length / theta
            ang = theta * (t - 0.5)
            c = np.column_stack([r * np.sin(ang), r * (np.cos(ang) - 1.0)])

        if self.twists:
            # The helix, projected. Applied across the *local* axis so it
            # composes with the bend instead of fighting it.
            d = np.gradient(c, axis=0)
            d = d / np.linalg.norm(d, axis=1)[:, None]
            n = np.column_stack([-d[:, 1], d[:, 0]])
            off = (self.twist_amp * self.half_w
                   * np.sin(2 * np.pi * (self.twists * t + self.twist_phase)))
            c = c + n * off[:, None]
        return c

    def _widths(self, c):
        """Half-width along the centreline, tapered from one pole to the
        other."""
        t = np.linspace(0.0, 1.0, len(c))
        return self.half_w * (1.0 + (self.taper - 1.0) * t)

    # -- geometry ----------------------------------------------------------

    def _geometry(self):
        rng = np.random.default_rng(self.seed)
        c = self._centreline()
        mid = c.mean(axis=0)
        w = self._widths(c)
        outline = tube(c, w, cap_base=True, n_cap=24)

        capsule = None
        if self.capsule > 0:
            # The same centreline at a larger width, so the slime layer is a
            # true offset of the cell rather than a scaled copy of it — a
            # scaled copy would sit closer to the wall at the poles than
            # along the sides, which is the one place the difference shows.
            capsule = tube(c, w + self.capsule * self.width,
                           cap_base=True, n_cap=24)

        nucleoid = None
        if self.nucleoid > 0:
            # Trimmed **along the body's own axis**, not scaled toward its
            # centroid. Scaling a curved centreline about its midpoint pulls
            # it off the arc it was drawn on — measured at 26 points outside
            # the wall on a cell bent 30 degrees with a twist in it, which is
            # a nucleoid hanging out through the membrane. Taking the middle
            # fraction of the axis keeps it on whatever curve the body has,
            # so this stays correct for a vibrio and a spirochaete too.
            k = float(np.clip(self.nucleoid, 0.0, 0.95))
            lo = int(round(0.5 * (1.0 - k) * (len(c) - 1)))
            hi = len(c) - lo
            nucleoid = tube(c[lo:hi], w[lo:hi] * k, cap_base=True, n_cap=18)

        return {"centre": c, "widths": w, "outline": outline,
                "capsule": capsule, "nucleoid": nucleoid,
                "granules": self._granules(outline, rng),
                "flagella": self._appendages(
                    outline, mid, rng, self.flagella, self.flagella_arc_deg,
                    self.flagella_start_deg,
                    self.flagellum_len * self.span,
                    self.flagellum_width * self.width,
                    self.flagellum_waves, amp=0.50),
                "pili": self._appendages(
                    outline, mid, rng, self.pili, self.pili_arc_deg,
                    self.pili_start_deg, self.pili_len * self.span,
                    self.pili_width * self.width, waves=0.55, amp=0.06)}

    def _granules(self, outline, rng):
        """Inclusions loose in the cytoplasm, on the body's own stream."""
        if self.granules <= 0:
            return []
        size = self.granule_size * self.half_w
        centres = scatter_in(outline, self.granules, seed=rng,
                             min_sep=self.granule_sep * self.half_w,
                             margin=size)
        angles = rng.uniform(0.0, 180.0, size=len(centres))
        out = []
        for p, ang in zip(centres, angles, strict=True):
            ring = superellipse(size, size * 0.82, 2.4, wobble=0.05,
                                wobble_n=3)
            rad = np.deg2rad(ang)
            m = np.array([[np.cos(rad), -np.sin(rad)],
                          [np.sin(rad), np.cos(rad)]])
            out.append({"outline": p + ring @ m.T, "centre": p})
        return out

    # -- placing things on the outline -------------------------------------

    def wall_at(self, deg):
        """`(point, outward normal)` on the outline, `deg` from the +x pole.

        Measured as a direction from the body's centre and resolved against
        the outline **as drawn**, so a cap, a taper or a bend is accounted for
        rather than idealised away — the same reason `paths.buried_base`
        searches the real tube instead of using its own closed form.

        Exact on a rod, where the map from direction to outline point is one
        to one. On a strongly twisted spirillum it is not: a ray from the
        centre can cross the outline more than once, and this takes the
        best-aligned vertex. Flagella on a spirillum are polar in practice, so
        the ambiguous region is not where they are asked for — but it is a
        real limit, and it is why this is a method you can check rather than
        arithmetic buried in the constructor.
        """
        g = self.geometry
        return self._wall_at(g["outline"], g["centre"].mean(axis=0), deg)

    @staticmethod
    def _wall_at(ring, mid, deg):
        """`wall_at` without the shape.

        Split out because the appendages are placed *while* `_geometry` is
        still running, and reaching for `self.geometry` from inside it is an
        infinite recursion — which is exactly what the first version of this
        shape did. Anything a shape needs during its own construction has to
        take its inputs as arguments.
        """
        ring = np.asarray(ring, dtype=float)
        d = np.array([np.cos(np.deg2rad(deg)), np.sin(np.deg2rad(deg))])
        v = ring - mid
        aligned = v @ d / np.maximum(np.linalg.norm(v, axis=1), 1e-12)
        i = int(np.argmax(aligned))
        # Outward from the ring's own edge, turned to agree with the body's
        # centre. Settling "outward" against the centre rather than against a
        # winding order is the fix for a bug this repository has had twice.
        tang = ring[(i + 1) % len(ring)] - ring[i - 1]
        n = unit(perp(tang))
        if np.dot(n, ring[i] - mid) < 0:
            n = -n
        return ring[i], n

    def _appendages(self, outline, mid, rng, n, arc_deg, start_deg, length,
                    width, waves, amp):
        """Flagella or pili: `n` tubes rooted round the outline.

        One routine for both because they differ only in how many, how long
        and how wavy — which is the same claim `Blob` makes about microvilli
        and pseudopodia, and it held there too.
        """
        if n <= 0:
            return []
        full = abs(arc_deg) >= 359.999
        step = arc_deg / (n if full or n == 1 else n - 1)
        j = self.jitter
        # A wavelength, not a count. `jitter` varies the lengths, and a shared
        # count would make the short ones wiggle faster — the bug this
        # library has now found three times, most recently in `Blob`.
        wave_per = (length / waves) if waves else None

        out = []
        for k in range(n):
            deg = (start_deg + step * k
                   + (rng.uniform(-1.0, 1.0) * j * 0.5 * step if n > 1 else 0))
            xy, nrm = self._wall_at(outline, mid, deg)
            ln = length * (1.0 + rng.uniform(-1.0, 1.0) * j)
            kw = dict(bend=0.10 * (-1) ** k, wave_amp=amp * self.width,
                      wave_phase=float(rng.uniform(0.0, 1.0)), n_pts=90)
            kw.update({k2: v for k2, v in self.geom_kw.items() if k2 in kw})
            if wave_per:
                kw["wave_per"] = wave_per
            else:
                kw["wave_n"] = 0.0
            # Rooted a width back inside the wall, so the flat base chord is
            # swallowed by the body's own fill and the two fuse.
            br = Branch(origin=xy - nrm * width, direction=nrm,
                        length=ln + width, **kw)
            out.append({"branch": br, "width": width, "deg": float(deg)})
        return out

    # -- rendering ---------------------------------------------------------

    def _layers(self):
        """Bottom first: the capsule, the cell, then what is inside it.

        The capsule is the only thing in this library so far that has to go
        *under* a body rather than over it, and it still needs its own layer:
        unioned with the cell it would simply become a fatter cell.
        """
        g = self.geometry
        layers = []
        if g["capsule"] is not None:
            layers.append(Layer(closed=[self.to_world(g["capsule"])],
                                name="capsule",
                                fill_alpha=self.WASH["capsule"]))
        layers.append(Layer(
            closed=[self.to_world(g["outline"])],
            open_=[self.to_world(tube(a["branch"].centre, a["width"],
                                      open_end=True))
                   for a in g["flagella"] + g["pili"]],
            name="cell" if g["capsule"] is not None else None))
        if g["nucleoid"] is not None:
            layers.append(Layer(closed=[self.to_world(g["nucleoid"])],
                                name="nucleoid",
                                fill_alpha=self.WASH["nucleoid"]))
        if g["granules"]:
            layers.append(Layer(
                closed=[self.to_world(x["outline"]) for x in g["granules"]],
                name="granules", fill_alpha=self.WASH["granules"]))
        return layers

    # -- anchors -----------------------------------------------------------

    def _anchors(self):
        """The two poles, eight points round the wall, and one per appendage
        tip."""
        g = self.geometry
        out = AnchorSet()

        c, w = g["centre"], g["widths"]
        # Each pole points away from its own neighbour, which is outward at
        # both ends without any sign arithmetic. Deriving "outward" from a
        # sign is what got the soma normals backwards twice — see the note in
        # `wall_at`.
        for name, i, nbr in (("far", -1, -2), ("near", 0, 1)):
            d = unit(c[i] - c[nbr])
            out.append(Anchor(self.to_world(c[i] + d * w[i]),
                              self.dir_to_world(d), "pole", end=name))

        for deg in self.WALL_DEGS:
            xy, n = self.wall_at(deg)
            out.append(Anchor(self.to_world(xy), self.dir_to_world(n),
                              "wall", deg=float(deg)))

        for kind, items in (("flagellum", g["flagella"]),
                            ("pilus", g["pili"])):
            for k, a in enumerate(items):
                xy, tang = a["branch"].at(1.0)
                out.append(Anchor(self.to_world(xy), self.dir_to_world(tang),
                                  kind, rank=k, deg=a["deg"]))
        return out

    def __repr__(self):
        return (f"Bacterium(length={self.length:g}, width={self.width:g}, "
                f"curve_deg={self.curve_deg:g}, twists={self.twists:g}, "
                f"flagella={self.flagella}, "
                f"at=({self.at[0]:.3g}, {self.at[1]:.3g}), "
                f"scale={self.scale:g})")

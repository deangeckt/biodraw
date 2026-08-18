"""The pyramidal cell: a triangular soma with spiny dendrites out of it.

One apical dendrite up from the top, and up to two basal ones down off the
bottom corners — soma, dendrites and every spine forming **one unbroken
outline**, the way the hand drawing this came from does it. Every branch ends
*open*: two walls that run out and stop, never a cap and never a spine sitting
on the tip.

Built entirely on `biodraw.core`: the dendrites are `Branch`es, the spines are
placed `Profile`s, the soma is a bowed polygon whose apex turns tangentially
into the apical tube, and all of it is rendered by the two-pass union.
"""

import numpy as np

from ..core.anchor import Anchor, AnchorSet
from ..core.branch import WIDTH_PER_DECORATION, Branch
from ..core.paths import (
    bowed_ring,
    buried_base,
    neck_polygon,
    rall_widths,
    rounded_polygon,
    tube,
)
from ..core.shape import Shape
from ..style.palette import get as get_palette

__all__ = ["Pyramidal"]


class Pyramidal(Shape):
    """A cartoon pyramidal cell.

    Shape
      spines           spines along the apical dendrite, at the default
                       `trunk_len`. Really a **density**: what is fixed is
                       spines per unit of dendrite, so a trunk shortened by a
                       fork carries proportionally fewer rather than the same
                       number crammed in. Sharing a count between branches of
                       different lengths is the same mistake as sharing a
                       waver's cycle count, and it shows the same way — an
                       apical forked at 0.5 carried nine spines on half a
                       trunk and the tuft came out a mass of touching heads.
      basal            basal branches off the soma's bottom edge: 2 for the
                       three-branch cell of the reference drawing, 1 for a
                       single one on the left, 0 for a bare apical-only cell.
      basal_spines     spines per basal branch.
      trunk_len        apical length, in local units. Not microns — the axes
                       are fitted to whatever is drawn.
      spine_size       spine length, but really the *head* size, since the
                       whole traced profile scales with it.
      spine_extend     extra neck, same units, added without resizing the
                       head. This is the knob for making spines pop out;
                       raising `spine_size` alone inflates the heads with them
                       and on a densely spined branch they start to touch.
      basal_len        visible basal length (soma corner -> tip), x
                       `trunk_len`.
      basal_angle_deg  how far a basal leans off straight down; larger splays
                       the legs wider. Clamped to a few degrees wider than the
                       soma's own slanted edge, below which the branch cannot
                       be rooted through its corner. Past ~60 the legs lie
                       along the soma's bottom edge and flatten the triangle
                       back into a trapeze.

    Asymmetry
      fork_ratio       the lesser daughter as a fraction of the greater — in
                       length, width and spine count, and *inversely* in
                       angle, because the thinner daughter is the one that
                       branches off wide while the thicker one carries on
                       near the parent's axis. 1.0 restores an exact mirror,
                       which is precisely what a bifurcation is not: two
                       daughters reflected about the trunk read as a drawn
                       symbol rather than as a cell that branched.
      basal_ratio      the same for the pair of basal legs. A cell with two
                       identical legs stands like a letter A.
      seed             which side each dominant branch lands on, and each
                       branch's own waver phase. Fixed, so the cell redraws
                       byte-identically; change it for a different cell of
                       the same kind rather than a different rendering of
                       this one.

    Tubes
      width            full dendrite width where it leaves the soma. `None`
                       ties it to `spine_size` so dendrite and spines stay in
                       proportion at any spine size.
      taper            width at the tip, x `width`; 1.0 is parallel-sided.
      basal_width      basal width, x the apical `width`, so the basals read
                       as thinner children of the same cell.

    Soma
      soma_w/_top/_bot half-width, and how far the apex and the base sit above
                       and below the origin.
      soma_neck_r      radius of the fillet that turns each slanted edge
                       tangentially into the apical tube wall. This is the
                       *only* mechanism for closing the top; 0 falls back to a
                       plain rounded triangle, which leaves a visible corner
                       stack at each shoulder.
      soma_round       fillet radius of the two base corners. Those corners
                       live inside the basal tubes and are never actually
                       seen, so this is a shape knob for the fill rather than
                       something the eye picks up.
      soma_bow_bottom  bow of the bottom edge, as a fraction of its length.
                       **Negative arches it up** into the soma — the way a
                       membrane sits between two basal roots pulling down on
                       its corners — which is what stops the edge reading as a
                       drafted straight line. Past about -0.05 it looks
                       pinched.
      soma_bow_side    the same for the slanted edges; positive bulges them
                       out for a plumper soma.
      soma_sink        how far the apical tube's flat base is buried inside
                       the triangle, as a fraction of the soma's height.

    `geom_kw` passes anything else through to the branch construction (`bend`,
    `wave_amp`, `wave_n`, `spine_angle_deg`, `first_t`, `last_t`, ...).
    """

    edge = get_palette()["excitatory"]

    # Where along the bare proximal trunk shaft contacts may land. Kept below
    # `first_t` so a shaft contact never arrives beside a spine head — that
    # reads as a spine contact, which is the wrong claim.
    SHAFT_TS = (0.02, 0.11)
    # How far down each slanted soma edge the soma anchors sit, as fractions
    # of apex -> base corner. Four a side rather than two: a basket cell makes
    # *perisomatic* contacts — several of them, round the soma — which is the
    # canonical thing an inhibitory cell does. At two a side there was nowhere
    # for the third and fourth to land without stacking on the first two.
    SOMA_FRACS = (0.24, 0.42, 0.60, 0.78)
    # A basal has to flare *wider* than the soma's own slanted edge, or its
    # axis runs back out through that edge instead of up into the soma and the
    # corner cannot be buried. This is the minimum clearance, in degrees.
    MIN_FLARE = 6.0
    # How deep the bottom corner is buried inside its basal tube, in tube
    # half-widths.
    BURY = 1.15
    # The waver's wavelength, in local units. Every branch on the cell gets
    # this rather than a shared cycle *count*, because the cell's branches
    # differ in length: a trunk forked at 0.25 is a quarter of the apical, and
    # 1.6 cycles crammed into it ran at four times the reference frequency and
    # swung the trunk 44 degrees off axis against the unforked cell's 22. That
    # is the S-kink under a fork. The value is the one the drawing was tuned
    # at — 1.80 of apical carrying 1.6 cycles — so an unforked cell at the
    # default `trunk_len` is unchanged, and everything shorter than it is now
    # wavered at the same rate rather than proportionally harder.
    WAVE_PER = 1.80 / 1.6

    def __init__(self, spines=6, basal=2, basal_spines=3,
                 trunk_len=1.80, spine_size=0.21, spine_extend=0.04,
                 apical_fork=None, fork_angle_deg=32.0, fork_spines=None,
                 fork_ratio=0.74, basal_ratio=0.82, seed=0,
                 basal_len=0.70, basal_angle_deg=40.0,
                 width=None, taper=0.72, basal_width=0.86,
                 soma_w=0.62, soma_top=0.40, soma_bot=0.60,
                 soma_neck_r=0.25, soma_round=5.0,
                 soma_bow_bottom=0.02, soma_bow_side=-0.005, soma_sink=0.45,
                 spine_profile="spine",
                 at=(0.0, 0.0), scale=1.0, rotate_deg=0.0, geom_kw=None):
        super().__init__(at=at, scale=scale, rotate_deg=rotate_deg)
        self.spines = int(spines)
        self.basal = int(basal)
        self.basal_spines = int(basal_spines)
        self.trunk_len = float(trunk_len)
        self.spine_size = float(spine_size)
        self.spine_extend = float(spine_extend)
        # `None` leaves the apical unbranched. A fraction forks it there, into
        # two daughters that carry the remaining length between them — which
        # is what a real apical does at the top of layer 1, and what most
        # hand-drawn pyramidal cells show.
        self.apical_fork = None if apical_fork is None else float(apical_fork)
        self.fork_angle_deg = float(fork_angle_deg)
        self.fork_spines = fork_spines
        self.fork_ratio = float(fork_ratio)
        self.basal_ratio = float(basal_ratio)
        self.seed = int(seed)
        self.basal_len = float(basal_len)
        self.basal_angle_deg = float(basal_angle_deg)
        # Tying the tube to the spine size by default means changing one knob
        # rescales the drawing coherently, instead of leaving fat spines on a
        # hairline dendrite.
        self.width = (WIDTH_PER_DECORATION * self.spine_size if width is None
                      else float(width))
        self.taper = float(taper)
        self.basal_width = float(basal_width)
        self.soma_w = float(soma_w)
        self.soma_top = float(soma_top)
        self.soma_bot = float(soma_bot)
        self.soma_neck_r = float(soma_neck_r or 0.0)
        self.soma_round = float(soma_round)
        self.soma_bow_bottom = float(soma_bow_bottom)
        self.soma_bow_side = float(soma_bow_side)
        self.soma_sink = float(soma_sink)
        self.spine_profile = spine_profile
        self.geom_kw = dict(geom_kw or {})

    # -- geometry ----------------------------------------------------------

    def _n_spines(self, length):
        """How many spines a branch of `length` carries.

        `spines` names the count at the default reach, and this holds the
        *density* constant from there. An unforked apical at the default
        `trunk_len` therefore gets exactly `spines`, and everything shorter
        gets fewer instead of the same number packed tighter.
        """
        if self.spines <= 0:
            return 0
        per = self.spines / self.trunk_len
        return max(1, int(round(per * float(length))))

    @property
    def half_width(self):
        """Drawn half-width of the apical tube, in local units."""
        return 0.5 * self.width

    @property
    def basal_half_width(self):
        return 0.5 * self.width * self.basal_width

    def _branch_kw(self, **over):
        kw = dict(bend=0.10, wave_amp=0.055, wave_per=self.WAVE_PER,
                  wave_phase=0.35, n_pts=120)
        kw.update({k: v for k, v in self.geom_kw.items() if k in kw})
        # `wave_n` through `geom_kw` is still honoured, and then has to
        # displace the wavelength — passing both to `Branch` would leave the
        # wavelength silently winning, which is the opposite of what someone
        # naming a cycle count meant.
        if "wave_n" in self.geom_kw and "wave_n" not in over:
            kw.pop("wave_per", None)
            kw["wave_n"] = self.geom_kw["wave_n"]
        kw.update(over)
        return kw

    def _decorate_kw(self, **over):
        kw = dict(angle_deg=72.0, first_t=0.30, last_t=0.86, first_side=-1)
        kw.update({k: v for k, v in self.geom_kw.items() if k in kw})
        kw.update(over)
        return kw

    def _geometry(self):
        """Local geometry: the soma triangle, the apical, and the basals."""
        apex = np.array([0.0, self.soma_top])
        base_l = np.array([-self.soma_w, -self.soma_bot])
        base_r = np.array([self.soma_w, -self.soma_bot])
        # One stream for the whole cell, drawn from in a fixed order, so that
        # `seed` names a cell rather than a rendering of one.
        rng = np.random.default_rng(self.seed)

        # Start the apical inside the soma so no seam shows at the join. When
        # it forks, the trunk runs only as far as the fork and the daughters
        # carry the rest — so `trunk_len` still means the cell's full apical
        # reach either way.
        frac = 1.0 if self.apical_fork is None else self.apical_fork
        apical = Branch(origin=(0.0, self.soma_top - 0.12),
                        direction=(0.0, 1.0), length=self.trunk_len * frac,
                        **self._branch_kw())
        dec = self._decorate_kw()
        apical.decorate(self.spine_profile, n=self._n_spines(apical.length),
                        size=self.spine_size, extend=self.spine_extend, **dec)

        return {"apex": apex, "base_l": base_l, "base_r": base_r,
                "apical": apical,
                "daughters": self._daughters(apical, rng),
                "basals": self._basals(base_l, base_r, apex, rng)}

    def _daughters(self, apical, rng):
        """The two branches an apical forks into, if it forks.

        Rooted at the trunk's own tip (`at_t=1.0`), so the trunk's open end and
        both daughters' buried bases all meet at one point and the union fuses
        them into a single fork — no cap, no seam, no three-way notch.

        The two are deliberately **not** mirror images. A bifurcation drawn as
        a reflection reads as a symbol for branching rather than as something
        that branched, and the giveaway is that both daughters leave at the
        same angle with the same calibre and the same waver reversed. Real
        ones split unequally, and the ways they do move together: the daughter
        that keeps more of the parent's calibre also runs further and turns
        *less* off its axis, while the thin one branches off wide. Driving all
        of that from one `fork_ratio` is what keeps the fork reading as a
        single event instead of three knobs that happen to be set.
        """
        if self.apical_fork is None:
            return []
        rest = self.trunk_len * (1.0 - self.apical_fork)
        r = self.fork_ratio
        # `None` lets each daughter take its share of the density; an explicit
        # `fork_spines` overrides that for both.
        n = None if self.fork_spines is None else int(self.fork_spines)
        dec = self._decorate_kw()
        # Which side carries the greater daughter. Drawn rather than fixed:
        # pinning it to one side makes every cell in a row lean the same way,
        # which is the same manufactured look one level up.
        major_side = -1 if rng.random() < 0.5 else 1
        # Rall: the daughters' cross-sections sum to the trunk's, so *both*
        # come out thinner than it. Not a refinement — giving the greater
        # daughter the trunk's own width makes the crotch unbuildable, since
        # `paths.buried_base` then has no depth at which the daughter's flat
        # base is both clear of the trunk's open end and inside its wall. See
        # `_parts`.
        w_major, w_minor = rall_widths(1.0, r)
        out = []
        for side in (-1, 1):
            major = side == major_side
            # The greater daughter carries the apical's remaining reach, so
            # `trunk_len` still means the cell's full reach however unequally
            # the fork splits.
            length = rest if major else rest * r
            # Halves that sum to 2 x fork_angle either way, so the total
            # crotch angle is what `fork_angle_deg` says and only its
            # *division* moves with the ratio.
            angle = 2.0 * self.fork_angle_deg * ((r if major else 1.0)
                                                 / (1.0 + r))
            # Negative turns clockwise off a tangent pointing up, so -side
            # sends side=+1 to the right.
            # Bend signed so the daughters lean *apart* as they rise. Curving
            # them inward closes the tuft into a tulip, which reads as two
            # branches about to rejoin — the opposite of what a fork says.
            br = apical.child(
                at_t=1.0, angle_deg=-side * angle, length=length,
                **self._branch_kw(
                    bend=0.10 * side, wave_amp=0.055 * side,
                    # Its own phase, so the two wavers are not each other's
                    # reflection either. Mirroring is the right answer for a
                    # *texture* — see `Profile.place(mirror=...)`, where it
                    # stops N decorations sharing one asymmetry — and the
                    # wrong answer for structure.
                    wave_phase=float(rng.uniform(0.0, 1.0))))
            br.decorate(self.spine_profile,
                        n=(n if n is not None
                           else self._n_spines(br.length)),
                        size=self.spine_size, extend=self.spine_extend,
                        angle_deg=dec["angle_deg"],
                        # Start clear of the crotch: a spine sitting in the
                        # fork reads as belonging to neither daughter.
                        first_t=0.22, last_t=dec["last_t"],
                        first_side=dec["first_side"] * -side)
            out.append({"branch": br, "side": side, "major": major,
                        "width_f": w_major if major else w_minor,
                        "turn_deg": float(angle)})
        return out

    def _basals(self, base_l, base_r, apex, rng):
        """The basal branches, each rooted *through* its own soma corner.

        Running the axis through the corner and starting it back up inside the
        soma is what makes the branch read as growing out of the corner: the
        tube's fill erases the vertex and the two soma edges where they enter
        it. Root it anywhere else and the vertex survives alongside the branch
        with a sliver of a notch between them — and because the soma's slanted
        edge and the branch run nearly parallel, that sliver is long and very
        visible.

        Unequal, for the same reason the fork is: a cell standing on two
        identical legs reads as a letter A. `basal_ratio` shortens, thins and
        widens the lesser one.
        """
        if self.basal <= 0:
            return []

        bhw = self.basal_half_width
        edge_deg = np.degrees(np.arctan2(self.soma_w,
                                         self.soma_top + self.soma_bot))
        r = self.basal_ratio
        # A lone basal is the cell's only leg and gets full length — there is
        # nothing for it to be the lesser of.
        major_side = -1 if self.basal == 1 or rng.random() < 0.5 else 1

        out = []
        for side, corner in ((-1, base_l), (1, base_r))[:self.basal]:
            major = side == major_side
            # Halves summing to 2 x basal_angle_deg, so the span between the
            # legs is what the knob says and only its division moves.
            angle_deg = 2.0 * self.basal_angle_deg * ((r if major else 1.0)
                                                      / (1.0 + r))
            flare = max(angle_deg - edge_deg, self.MIN_FLARE)
            a = np.deg2rad(edge_deg + flare)
            d = np.array([side * np.sin(a), -np.cos(a)])
            # Backing up the axis buys clearance from the slanted edge at
            # exactly sin(flare) per unit, so a narrow flare is expensive.
            back = self.BURY * bhw / np.sin(np.deg2rad(flare))
            # `back` varies with the angle, so add it on top of the asked-for
            # length and re-map the spine range onto the part that is actually
            # outside the soma. `basal_len` and the spine range then all mean
            # what they say about the *visible* branch, whatever burial costs.
            length = (self.basal_len * self.trunk_len
                      * (1.0 if major else r) + back)
            f0 = back / length
            dec = self._decorate_kw()
            br = Branch(origin=corner - d * back, direction=d, length=length,
                        **self._branch_kw(
                            bend=-0.10 * side, wave_amp=0.055 * side,
                            wave_phase=float(rng.uniform(0.0, 1.0))))
            br.decorate(self.spine_profile,
                        n=(self.basal_spines if major
                           else max(1, int(round(self.basal_spines * r)))),
                        size=self.spine_size, extend=self.spine_extend,
                        angle_deg=dec["angle_deg"],
                        first_t=f0 + 0.32 * (1 - f0),
                        last_t=f0 + 0.70 * (1 - f0),
                        first_side=dec["first_side"] * side)
            out.append({"branch": br, "side": side, "t0": float(f0),
                        "major": major, "width_f": 1.0 if major else r})
        return out

    # -- rendering ---------------------------------------------------------

    def _parts(self):
        g = self.geometry
        hw = self.half_width
        bhw = self.basal_half_width
        closed, open_ = [], []

        # The apical tube, sunk far enough into the soma that its flat base
        # never surfaces through the wall.
        #
        # Left **open** only when the apical really ends — two walls that run
        # out and stop, the un-closed end of a hand-drawn process. Where it
        # forks, its tip is not an end but a junction, and an open end there
        # is what made the crotch undrawable: the daughters had nothing above
        # them to bury their flat bases in, and at the narrow end of a tapered
        # trunk there is no depth at which a base chord is both clear of the
        # tip and inside the wall. Capping it puts a dome of solid trunk at
        # the joint — which the daughters root into, and whose visible sliver
        # is the rounded bottom of the crotch, which is what a real
        # bifurcation has anyway.
        sink = self.soma_sink * (g["apex"][1] - g["base_l"][1])
        apical = g["apical"]
        forked = bool(g["daughters"])
        trunk_tube = self.to_world(
            tube(apical.centre,
                 np.linspace(hw, hw * self.taper, len(apical.centre)),
                 base_ext=sink, open_end=not forked))
        # A capped tube is a closed shape and joins the union as one; an open
        # one is a stroke whose far end never closes.
        (closed if forked else open_).append(trunk_tube)
        closed += [self.to_world(d["outline"]) for d in apical.decorations]

        # Daughters, at their Rall share of the width the trunk had tapered to
        # where they leave — so the lesser one is visibly thinner rather than
        # merely shorter, and both are thinner than the trunk.
        dhw = hw * self.taper
        # Burial searched against the trunk tube as actually drawn, rather
        # than computed from a multiple of the daughter's own width. A fixed
        # multiple knows nothing about the angle, and at 2 x width it swung
        # each daughter's base chord out through the far side of the trunk —
        # a spur across the crotch, which is exactly what a fork must not
        # have. Searching the real outline also takes the trunk's taper and
        # its lean into account, which no closed form of mine did.
        for b in g["daughters"]:
            br = b["branch"]
            w = dhw * b["width_f"]
            depth, _ = buried_base(trunk_tube, self.to_world(br.centre[0]),
                                   self.dir_to_world(br.direction),
                                   w * self.scale)
            open_.append(self.to_world(
                tube(br.centre,
                     np.linspace(w, w * self.taper, len(br.centre)),
                     base_ext=depth / self.scale, open_end=True)))
            closed += [self.to_world(d["outline"]) for d in br.decorations]

        for b in g["basals"]:
            br = b["branch"]
            w = bhw * b["width_f"]
            # The basal base is already rooted inside the triangle, so it only
            # has to clear the wall — the apical's `sink` would drive it out
            # the far side.
            open_.append(self.to_world(
                tube(br.centre,
                     np.linspace(w, w * self.taper, len(br.centre)),
                     base_ext=1.2 * w, open_end=True)))
            closed += [self.to_world(d["outline"]) for d in br.decorations]

        closed.append(self._soma_path())
        return closed, open_

    def _soma_path(self):
        """The soma outline, in world units."""
        from matplotlib.path import Path

        g = self.geometry
        apex, base_l, base_r = g["apex"], g["base_l"], g["base_r"]

        if self.soma_neck_r > 0:
            path, _ = neck_polygon(
                apex, base_l, base_r, hw=self.half_width,
                neck_r=self.soma_neck_r, corner_r=self.soma_round,
                bow_bottom=self.soma_bow_bottom, bow_side=self.soma_bow_side)
            # Built in local units, so map every vertex the same way the
            # spines and tubes are; the codes carry through unchanged.
            return Path(self.to_world(path.vertices), path.codes)

        ring = bowed_ring([apex, base_l, base_r],
                          [self.soma_bow_side, self.soma_bow_bottom,
                           self.soma_bow_side])
        return rounded_polygon(self.to_world(ring),
                               self.soma_round * self.scale)

    @property
    def soma_polygon(self):
        """A 4-vertex stand-in for the drawn soma, in world units.

        `[P_s_l, base_l, base_r, P_s_r]` where `P_s` are the points at which
        the slanted edges turn into the neck. Close enough to the real outline
        that anything placed *on* the soma lands on the correct slanted edge
        without having to know about the neck arc at all.
        """
        g = self.geometry
        apex, base_l, base_r = g["apex"], g["base_l"], g["base_r"]
        if self.soma_neck_r > 0:
            _, pts = neck_polygon(
                apex, base_l, base_r, hw=self.half_width,
                neck_r=self.soma_neck_r, corner_r=self.soma_round,
                bow_bottom=self.soma_bow_bottom, bow_side=self.soma_bow_side)
            local = [pts["P_s_l"], base_l, base_r, pts["P_s_r"]]
        else:
            local = [apex, base_l, base_r]
        return self.to_world(np.array(local))

    # -- anchors -----------------------------------------------------------

    def _anchors(self):
        """Named places on the cell: every spine head, the bare shaft, each
        slanted soma flank, and where the axon leaves."""
        g = self.geometry
        out = AnchorSet()

        for name, br, extra in self._branches():
            for k, d in enumerate(br.decorations):
                out.append(Anchor(
                    self.to_world(d["head"]), self.dir_to_world(d["dir"]),
                    "spine", branch=name, rank=k, t=d["t"], side=d["side"],
                    head_r=d["profile"].head_r * d["size"] * self.scale,
                    **extra))

        # The bare proximal apical, on both walls, so a contact can arrive
        # from either side of the cell.
        apical = g["apical"]
        for t in self.SHAFT_TS:
            xy, tang = apical.at(t)
            n = np.array([-tang[1], tang[0]])
            for side in (-1, 1):
                out.append(Anchor(
                    self.to_world(xy + n * side * self.half_width),
                    self.dir_to_world(n * side),
                    "shaft", branch="apical", t=float(t), side=side))

        # The two slanted soma flanks.
        apex, base_l, base_r = g["apex"], g["base_l"], g["base_r"]
        centre = (apex + base_l + base_r) / 3.0
        for side, corner in ((-1, base_l), (1, base_r)):
            edge = corner - apex
            n = np.array([edge[1], -edge[0]])
            n = n / np.linalg.norm(n)
            for f in self.SOMA_FRACS:
                xy = apex + edge * f
                # Which of the two perpendiculars is the outward one depends
                # on the winding, and picking by sign is easy to get backwards
                # — with the result that every connector landing here reaches
                # *through* the cell instead of stopping at its wall. Settle
                # it against the body's own centre, where there is nothing to
                # get backwards.
                outward = n if np.dot(n, xy - centre) > 0 else -n
                out.append(Anchor(self.to_world(xy),
                                  self.dir_to_world(outward),
                                  "soma", side=side, t=float(f)))

        # Where the axon leaves: the middle of the bottom edge, pointing down.
        out.append(Anchor(self.to_world((base_l + base_r) / 2.0),
                          self.dir_to_world((0.0, -1.0)), "axon"))
        return out

    def _branches(self):
        """`(name, Branch, extra anchor metadata)` for every dendrite.

        `branch_side` is which side of the *cell* the branch is on, and is
        deliberately not called `side` — a spine anchor already carries `side`
        for which wall of its own branch it sits on, and the two are different
        questions.
        """
        g = self.geometry
        found = [("apical", g["apical"], {})]
        for b in g["daughters"]:
            side = "l" if b["side"] < 0 else "r"
            found.append((f"apical.{side}", b["branch"],
                          {"branch_side": b["side"]}))
        for i, b in enumerate(g["basals"]):
            found.append((f"basal{i}", b["branch"],
                          {"branch_side": b["side"]}))
        return found

    def __repr__(self):
        return (f"Pyramidal(spines={self.spines}, basal={self.basal}, "
                f"at=({self.at[0]:.3g}, {self.at[1]:.3g}), "
                f"scale={self.scale:g})")

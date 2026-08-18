"""The basket cell: a round soma with smooth dendrites out of it.

The counterpart to `Pyramidal`, and drawn to be told apart from it at a
glance — which is the whole job of an inhibitory cell in a circuit panel. Three
cues do that work, and all three are structural rather than a change of
colour:

* a **round** soma instead of a triangle;
* dendrites that leave in several directions rather than one up and two down;
* **smooth** dendrites — no spines. A basket cell is aspiny, and drawing it
  that way means a reader can tell the two cells apart in greyscale, which
  colour alone would not survive.

Built on the same core as everything else: the soma is a `superellipse`, the
dendrites are `Branch`es walled by `tube`, and the whole cell is one unbroken
contour, so it fuses exactly the way a pyramidal cell does.
"""

import numpy as np

from ..core.anchor import Anchor, AnchorSet
from ..core.branch import WIDTH_PER_DECORATION, Branch
from ..core.paths import superellipse, superellipse_radius, tube
from ..core.shape import Shape
from ..style.palette import get as get_palette

__all__ = ["Basket"]


class Basket(Shape):
    """A cartoon basket (inhibitory) cell.

    Soma
      radius          semi-axis along x, in local units.
      aspect          semi-axis along y, x `radius`. Just over 1 by default:
                      a soma that is exactly circular reads as a drawn dot,
                      and the eye finds a perfect circle immediately.
      squareness      superellipse exponent — 2 is an ellipse. Kept low, so
                      the soma stays visibly *round* against the pyramidal
                      triangle it will be drawn beside.
      wobble          swells the wall by that fraction of the radius, so it
                      does not read as a primitive.

    Dendrites
      dendrites       how many leave the soma.
      arc_deg         the sweep of soma they leave over, and
      start_deg       where that sweep begins (counter-clockwise from +x).
                      The default is the full turn: a multipolar cell. A
                      narrower arc gives a bitufted or bipolar-looking cell
                      without needing another class.
      length          dendrite length, in local units.
      length_ratio    the shortest dendrite as a fraction of the longest.
                      Not decoration: dendrites of one length make a
                      snowflake, and the eye reads regularity as a diagram.
      width           full dendrite width where it leaves the soma. `None`
                      ties it to the soma radius so the cell rescales
                      coherently.
      taper           width at the tip, x `width`.
      jitter          how far each dendrite wanders off its even slot and its
                      nominal length, as a fraction of each. 0 spaces them
                      exactly, which is the snowflake.
      forks           fraction along a dendrite at which it splits in two, or
                      `None` for unbranched. Basket dendrites do branch, and
                      the fork machinery is already in the core.
      fork_angle_deg / fork_ratio
                      as on `Pyramidal` — the daughters are unequal for the
                      same reason.
      seed            fixes the jitter and which daughter dominates.

    `geom_kw` passes anything else through to the branch construction.
    """

    edge = get_palette()["inhibitory"]

    # The waver's wavelength, in local units, shared by every branch on the
    # cell — a cycle *count* shared between branches of different lengths runs
    # the short ones at a higher frequency. See `Branch`'s module docstring.
    WAVE_PER = 0.85
    # Where the soma anchors sit, in degrees. Eight, on the axes and the
    # diagonals, so several connectors can land without stacking.
    SOMA_DEGS = tuple(range(0, 360, 45))
    # Where along a dendrite a contact may land, as fractions of its length.
    # Away from both ends: at the base it would sit on the soma, and at the
    # tip it reads as the process ending in a synapse rather than passing one.
    SHAFT_TS = (0.30, 0.55, 0.80)

    def __init__(self, radius=0.40, aspect=1.12, squareness=2.2, wobble=0.03,
                 dendrites=6, arc_deg=360.0, start_deg=18.0,
                 length=1.05, length_ratio=0.68, jitter=0.22,
                 width=None, taper=0.62,
                 forks=None, fork_angle_deg=34.0, fork_ratio=0.76,
                 seed=0, at=(0.0, 0.0), scale=1.0, rotate_deg=0.0,
                 geom_kw=None):
        super().__init__(at=at, scale=scale, rotate_deg=rotate_deg)
        self.radius = float(radius)
        self.aspect = float(aspect)
        self.squareness = float(squareness)
        self.wobble = float(wobble)

        self.dendrites = int(dendrites)
        self.arc_deg = float(arc_deg)
        self.start_deg = float(start_deg)
        self.length = float(length)
        self.length_ratio = float(length_ratio)
        self.jitter = float(jitter)

        # Tied to the soma rather than to a decoration size, since there are
        # no decorations on this cell — but the same idea: one knob rescales
        # the drawing coherently.
        self.width = (WIDTH_PER_DECORATION * self.radius if width is None
                      else float(width))
        self.taper = float(taper)

        self.forks = None if forks is None else float(forks)
        self.fork_angle_deg = float(fork_angle_deg)
        self.fork_ratio = float(fork_ratio)
        self.seed = int(seed)
        self.geom_kw = dict(geom_kw or {})

    # -- geometry ----------------------------------------------------------

    @property
    def semi(self):
        return self.radius, self.radius * self.aspect

    @property
    def half_width(self):
        return 0.5 * self.width

    def wall_radius(self, deg):
        """Centre to the wobbled soma wall at `deg`, and the direction there.

        Same expression as `superellipse` uses for its wobble, so a dendrite
        rooted with this starts exactly on the drawn wall rather than floating
        off it or sinking in. See `cells.Blob.wall_radius`.
        """
        from ..core.geom import rot
        a, b = self.semi
        d = rot((1.0, 0.0), deg)
        r = superellipse_radius(d, a, b, self.squareness)
        return d, r * (1.0 + self.wobble * np.sin(3 * np.deg2rad(deg)
                                                  + 2 * np.pi * 0.20))

    def _branch_kw(self, **over):
        kw = dict(bend=0.09, wave_amp=0.035, wave_per=self.WAVE_PER,
                  wave_phase=0.35, n_pts=90)
        kw.update({k: v for k, v in self.geom_kw.items() if k in kw})
        if "wave_n" in self.geom_kw and "wave_n" not in over:
            kw.pop("wave_per", None)
            kw["wave_n"] = self.geom_kw["wave_n"]
        kw.update(over)
        return kw

    def _geometry(self):
        a, b = self.semi
        rng = np.random.default_rng(self.seed)
        soma = superellipse(a, b, self.squareness, wobble=self.wobble,
                            wobble_n=3, wobble_phase=0.20)
        dends = self._dendrites(rng)
        return {"soma": soma, "dendrites": dends}

    def _dendrites(self, rng):
        """The processes, on even slots round the soma and then knocked off
        them.

        Each is rooted *inside* the wall, so the tube's flat base is swallowed
        by the soma's fill and the two fuse rather than butt.
        """
        n = self.dendrites
        if n <= 0:
            return []
        full = abs(self.arc_deg) >= 359.999
        step = self.arc_deg / (n if full or n == 1 else n - 1)
        hw = self.half_width
        out = []
        for k in range(n):
            # Half a step is the most a slot can move without swapping with
            # its neighbour, so order round the soma survives any jitter.
            deg = (self.start_deg + step * k
                   + rng.uniform(-1.0, 1.0) * self.jitter * 0.5 * step)
            d, r = self.wall_radius(deg)
            # Lengths spread across the ratio rather than randomly, so the
            # cell has a long axis and a short one instead of noise.
            f = self.length_ratio + (1.0 - self.length_ratio) * rng.random()
            length = self.length * f * (1.0 + rng.uniform(-1.0, 1.0)
                                        * self.jitter * 0.35)
            br = Branch(origin=d * (r - 1.6 * hw), direction=d,
                        length=length + 1.6 * hw,
                        **self._branch_kw(
                            bend=0.09 * (1 if k % 2 else -1),
                            wave_phase=float(rng.uniform(0.0, 1.0))))
            out.append({"branch": br, "deg": float(deg),
                        "children": self._fork(br, rng)})
        return out

    def _fork(self, parent, rng):
        """A dendrite's two daughters, if it forks.

        Sized by Rall like the pyramidal apical's, so both are thinner than
        the parent — which is what leaves room to bury their flat bases in it.
        See `paths.buried_base` for why a full-width daughter cannot be
        joined at all.
        """
        if self.forks is None:
            return []
        from ..core.paths import rall_widths
        r = self.fork_ratio
        w_major, w_minor = rall_widths(1.0, r)
        rest = parent.length * (1.0 - self.forks)
        major_side = -1 if rng.random() < 0.5 else 1
        out = []
        for side in (-1, 1):
            major = side == major_side
            angle = 2.0 * self.fork_angle_deg * ((r if major else 1.0)
                                                 / (1.0 + r))
            br = parent.child(
                at_t=self.forks, angle_deg=-side * angle,
                length=rest if major else rest * r,
                **self._branch_kw(bend=0.09 * side,
                                  wave_phase=float(rng.uniform(0.0, 1.0))))
            out.append({"branch": br, "side": side, "major": major,
                        "width_f": w_major if major else w_minor})
        return out

    # -- rendering ---------------------------------------------------------

    def _parts(self):
        """One unbroken contour: soma, dendrites and any daughters all fuse."""
        from ..core.paths import buried_base

        g = self.geometry
        hw = self.half_width
        closed, open_ = [], []

        for d in g["dendrites"]:
            br = d["branch"]
            forked = bool(d["children"])
            # A dendrite that forks ends in a junction, not an end, so it is
            # capped and joins the union as a closed part — the same reason
            # the pyramidal trunk is. An unforked one runs off and stops.
            at_fork = self.forks if forked else 1.0
            n_keep = max(2, int(round(len(br.centre) * at_fork)))
            centre = br.centre[:n_keep] if forked else br.centre
            widths = np.linspace(hw, hw * self.taper, len(br.centre))[:n_keep]
            tube_w = self.to_world(tube(centre, widths, base_ext=1.4 * hw,
                                        open_end=not forked))
            (closed if forked else open_).append(tube_w)

            for c in d["children"]:
                cb = c["branch"]
                w = widths[-1] * c["width_f"]
                depth, _ = buried_base(tube_w,
                                       self.to_world(cb.centre[0]),
                                       self.dir_to_world(cb.direction),
                                       w * self.scale)
                open_.append(self.to_world(
                    tube(cb.centre,
                         np.linspace(w, w * self.taper, len(cb.centre)),
                         base_ext=depth / self.scale, open_end=True)))

        closed.append(self.to_world(g["soma"]))
        return closed, open_

    # -- anchors -----------------------------------------------------------

    def _anchors(self):
        """Round the soma, along each dendrite's shaft, and at every tip."""
        g = self.geometry
        out = AnchorSet()

        for deg in self.SOMA_DEGS:
            d, r = self.wall_radius(deg)
            out.append(Anchor(self.to_world(d * r), self.dir_to_world(d),
                              "soma", deg=float(deg)))

        for i, dend in enumerate(g["dendrites"]):
            for br, name in self._walk(dend, f"dend{i}"):
                for t in self.SHAFT_TS:
                    xy, tang = br.at(t)
                    n = np.array([-tang[1], tang[0]])
                    for side in (-1, 1):
                        out.append(Anchor(
                            self.to_world(xy + n * side * self.half_width),
                            self.dir_to_world(n * side),
                            "shaft", branch=name, t=float(t), side=side))
                xy, tang = br.at(1.0)
                out.append(Anchor(self.to_world(xy), self.dir_to_world(tang),
                                  "tip", branch=name))
        return out

    def _walk(self, dend, name):
        """`(Branch, name)` for a dendrite and any daughters it has."""
        found = [(dend["branch"], name)]
        for c in dend["children"]:
            found.append((c["branch"],
                          f"{name}.{'l' if c['side'] < 0 else 'r'}"))
        return found

    def _branches(self):
        """Every branch on the cell, for blueprints and introspection."""
        out = []
        for i, d in enumerate(self.geometry["dendrites"]):
            out += self._walk(d, f"dend{i}")
        return out

    def __repr__(self):
        return (f"Basket(dendrites={self.dendrites}, "
                f"forks={self.forks}, at=({self.at[0]:.3g}, "
                f"{self.at[1]:.3g}), scale={self.scale:g})")

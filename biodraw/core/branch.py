"""The branch: a curved centreline that can be walled into a tube and
decorated along its length.

This is the workhorse. A dendrite, an axon collateral, a hypha, a rootlet and a
tentacle are all the same object here — a slow lean with a hand-drawn waver on
top — and what tells them apart is the tube width, the taper, and what (if
anything) is stamped along them.

The curve
---------
Written in the branch's own frame, `u` along `direction` and `v` 90 degrees
*clockwise* from it, so that a branch and its mirror image are the same
formula with one sign flipped:

    along(t)  = length * t
    across(t) = bend * t^2.2  +  wave_amp * t * sin(2*pi*wave_n*t + 2*pi*phase)

i.e. a slow lean (`bend`) with a waver on top, which reads as a *drawn* line
without needing a Bezier path or any control points to tune. The waver is
ramped by `t` so it vanishes at the base: an offset there would plant the
branch off-centre on whatever it grows out of, whatever the phase.

Cycles, and why they are the wrong unit
--------------------------------------
`wave_n` counts cycles *over the branch*, so it is a count and not a
frequency: halve a branch's length at a fixed `wave_n` and the waver runs at
twice the spatial frequency. A value tuned on a long dendrite therefore
corkscrews on a short one, and the shorter the branch the worse it gets —
measured on this library's own pyramidal cell, an apical forked at 0.25
drove its trunk at **four times** the frequency the hand was tuned at, and
swung it 44 degrees off axis against the reference 22.

Anything that shortens a branch without meaning to change how wavy it looks
should therefore give `wave_per` — the wavelength, in local units — and let
`wave_n` be derived. That is the same class of mistake as keying a fork off
the local tangent (see `Branch.child`): a cosmetic term that does not scale
with length, quietly driving something structural.

The frame flips handedness when `direction` is mirrored across x, so a pair of
mirror-image branches needs `bend` and `wave_amp` negated on one of them. That
is the caller's job — see how the basal pair of a pyramidal cell is built.
"""

import numpy as np

from .geom import perp, rot, unit
from .paths import tube
from .profile import get as get_profile

__all__ = ["Branch", "WIDTH_PER_DECORATION"]


# Default tube width, as a multiple of the decoration size, so changing the
# spine size rescales the whole drawing coherently instead of leaving fat
# spines on a hairline dendrite.
WIDTH_PER_DECORATION = 0.50


class Branch:
    """One curved process, with optional decorations stamped along it.

      origin      where it leaves, in local units.
      direction   which way it sets off.
      length      how far it runs, along the axis.
      bend        the slow lean, as an across-offset at the tip. Signed: the
                  sign is in the branch's own frame, so mirrored pairs negate.
      wave_amp    amplitude of the waver on top of the lean, same units.
      wave_n      how many cycles of it over the branch's length. A *count*,
                  not a frequency — see the note at the top of this module
                  before reusing one across branches of different lengths.
      wave_per    the waver's wavelength, in local units. Given instead of
                  `wave_n`, which is then derived as `length / wave_per`, so
                  a branch keeps the same waviness per unit of itself however
                  long it is. This is what a family of branches that differ in
                  length — a trunk and the daughters it forks into — has to
                  share if they are to look like one hand drew them.
      wave_phase  where in the cycle it starts, in turns.
      n_pts       centreline resolution. Only matters for the tube's smoothness
                  and for how finely `at` can be sampled.

    The centreline is available as `.centre`, and `.at(t)` gives the point and
    unit tangent at any parameter — which is what everything placed *on* a
    branch (decorations, dots, contacts) is positioned with.
    """

    def __init__(self, origin, direction, length, bend=0.10, wave_amp=0.055,
                 wave_n=1.6, wave_phase=0.35, n_pts=120, wave_per=None):
        self.origin = np.asarray(origin, dtype=float)
        self.direction = unit(direction)
        self.length = float(length)
        self.bend = float(bend)
        self.wave_amp = float(wave_amp)
        self.wave_per = None if wave_per is None else float(wave_per)
        # Derived, not stored alongside: everything downstream reads `wave_n`,
        # so a wavelength has to become a count here or the two could disagree.
        self.wave_n = (float(wave_n) if self.wave_per is None
                       else self.length / self.wave_per)
        self.wave_phase = float(wave_phase)
        self.n_pts = int(n_pts)

        self.u = self.direction
        self.v = -perp(self.u)          # 90 degrees clockwise of `u`
        self.decorations = []

        t = np.linspace(0.0, 1.0, self.n_pts)
        self.t_grid = t
        self.centre = (self.origin + np.outer(self.length * t, self.u)
                       + np.outer(self.across(t), self.v))

    # -- the curve, in pieces, so `explain` can show them apart ------------

    def lean(self, t):
        """The `bend` term alone: a slow parabolic-ish drift, t^2.2."""
        return self.bend * np.asarray(t, dtype=float) ** 2.2

    def waver(self, t):
        """The `wave` term alone, ramped by `t` so it vanishes at the base."""
        t = np.asarray(t, dtype=float)
        return self.wave_amp * t * np.sin(2 * np.pi * self.wave_n * t
                                          + 2 * np.pi * self.wave_phase)

    def across(self, t):
        """Total offset across the axis: the lean plus the waver."""
        return self.lean(t) + self.waver(t)

    def along(self, t):
        """Distance along the axis at `t`."""
        return self.length * np.asarray(t, dtype=float)

    def at(self, t):
        """`(xy, unit tangent)` at parameter `t`, analytically."""
        t = float(t)
        w, p0 = 2 * np.pi * self.wave_n, 2 * np.pi * self.wave_phase
        xy = self.origin + self.length * t * self.u + self.across(t) * self.v
        d = (self.length * self.u
             + (self.bend * 2.2 * t ** 1.2
                + self.wave_amp * (np.sin(w * t + p0)
                                   + t * w * np.cos(w * t + p0))) * self.v)
        return xy, d / np.linalg.norm(d)

    def normal_at(self, t, side=1):
        """Outward unit normal at `t`, on `side` (+1 / -1) of the branch."""
        _, tang = self.at(t)
        return perp(tang) * float(np.sign(side) or 1)

    # -- decorations ------------------------------------------------------

    def decorate(self, profile, n, size, angle_deg=72, first_t=0.30,
                 last_t=0.98, first_side=-1, extend=0.0, alternate=True,
                 head=1.0, neck=1.0):
        """Stamp `n` copies of `profile` along the branch, alternating sides.

        Each sits at `angle_deg` off the local tangent, rotated *toward the
        tip* so they angle along the branch the way a drawn one does rather
        than sticking straight out.

        Decorations start at `first_t`, leaving the proximal stretch bare. That
        matters more than it looks: a bare shaft is where anything contacting
        the *shaft* has to land, and a shaft contact arriving next to a spine
        head reads as a spine contact — exactly the wrong message. Keep
        anything aimed at the shaft below `first_t`.

        `extend` lengthens each decoration's stretch span (its neck, for a
        spine) without resizing its head — see `Profile.place`. `head` and
        `neck` scale the two widths, which is what separates a mushroom spine
        from a thin one.

        Returns the list of decoration dicts and also stores it on
        `.decorations`. Each is
        `{'base', 'dir', 'side', 't', 'head', 'outline', 'profile'}`, where
        `head` is the widest point (what a connector should aim at) and
        `outline` is the closed polygon to render.
        """
        prof = get_profile(profile)
        size = float(size)
        out = []
        ts = np.linspace(first_t, last_t, int(n)) if n else []
        for k, tt in enumerate(ts):
            side = first_side * ((-1) ** k if alternate else 1)
            base, tang = self.at(tt)
            # +angle rotates a mostly-forward tangent to the left, hence -side.
            d = rot(tang, -side * float(angle_deg))
            out.append({
                "base": base,
                "dir": d,
                "side": int(side),
                "t": float(tt),
                # Aim point is the widest part of the head, not the tip, so a
                # stand-off radius stays symmetric. `extend` carries the head
                # out rigidly, so it lands on this one-for-one.
                "head": base + d * prof.head_offset(size, extend),
                "outline": prof.place(base, d, size, mirror=(side > 0),
                                      extend=extend, head=head, neck=neck),
                "profile": prof,
                "size": size,
                "extend": float(extend),
                # Not "head": that key is already the aim *point*. These are
                # the two width multipliers `Profile.place` was given.
                "head_scale": float(head),
                "neck_scale": float(neck),
            })
        self.decorations = out
        return out

    def child(self, at_t, angle_deg, length, relative_to="axis", **kw):
        """A daughter branch leaving this one at parameter `at_t`.

        `angle_deg` is counter-clockwise, so on a branch running upward a
        negative angle sends the daughter to the right.

        `relative_to` says what that angle is measured from, and the default
        is not the obvious one:

          'axis'     the branch's nominal `direction` — the way it was
                     launched. **The default.**
          'chord'    origin -> tip, so the daughter follows where the branch
                     actually ended up, lean included.
          'tangent'  the local tangent at `at_t`.

        The local tangent is the intuitive choice and the wrong one. The waver
        that makes a branch look drawn rather than ruled is a *sine*, and its
        derivative scales with `wave_n` while its amplitude does not scale with
        length — so on a short branch the tangent at the tip can sit tens of
        degrees off the direction the branch visibly runs in. A fork keyed to
        it comes out lopsided, with both daughters swung the same way, and no
        amount of adjusting `angle_deg` fixes it because the error moves with
        every other knob. Structure should not inherit cosmetic noise; use
        'tangent' only on a long, gently wavered branch where the two agree.

        The daughter is a `Branch` like any other, so it can be decorated,
        walled and forked again. Rooting it exactly *on* the parent's
        centreline is what lets the union fuse the two into one contour: give
        the daughter's tube a `base_ext` and its flat base disappears inside
        the parent instead of showing as a butt joint.

        Anything not given is inherited from the parent, so a fork keeps the
        same hand unless it is told otherwise.
        """
        xy, tang = self.at(at_t)
        if relative_to == "axis":
            base = self.direction
        elif relative_to == "chord":
            base = unit(self.centre[-1] - self.centre[0])
        elif relative_to == "tangent":
            base = tang
        else:
            raise ValueError(
                f"relative_to must be 'axis', 'chord' or 'tangent', "
                f"not {relative_to!r}")

        # A daughter is nearly always shorter than its parent, so inheriting
        # the parent's cycle *count* is precisely the thing that makes a fork
        # come out over-wavered. When the parent was given a wavelength, that
        # is what the child inherits, and the count follows from its own
        # length.
        inherited = dict(bend=self.bend, wave_amp=self.wave_amp,
                         wave_phase=self.wave_phase, n_pts=self.n_pts)
        if self.wave_per is None:
            inherited["wave_n"] = self.wave_n
        else:
            inherited["wave_per"] = self.wave_per
        inherited.update(kw)
        return Branch(origin=xy, direction=rot(base, float(angle_deg)),
                      length=float(length), **inherited)

    @property
    def head_r(self):
        """Stand-off radius of this branch's decorations, in local units.

        Tied to `size` alone, deliberately: `extend` carries the head out
        rigidly without resizing it, so the radius that clears the head is the
        same however far the neck has been stretched. Deriving it from the head
        *offset* instead would inflate it with every extension.
        """
        if not self.decorations:
            return 0.0
        d = self.decorations[0]
        return d["profile"].head_r * d["size"]

    # -- rendering --------------------------------------------------------

    def outline(self, width, taper=1.0, base_ext=0.0, open_end=True):
        """This branch as a walled tube.

        `width` is the *full* width where the branch leaves its origin, and
        `taper` the width at the tip as a multiple of it (1.0 = parallel
        sided). `base_ext` pushes the flat base back along the starting tangent
        so it buries inside whatever the branch grows out of.
        """
        hw = 0.5 * float(width)
        return tube(self.centre,
                    np.linspace(hw, hw * float(taper), len(self.centre)),
                    base_ext=base_ext, open_end=open_end)

    def parts(self, width, taper=1.0, base_ext=0.0, open_end=True):
        """`(closed parts, open parts)` ready for `render.render_hollow`.

        The decorations are closed outlines that fuse into the union; the tube
        is an open part, so its far end stops as two walls rather than a cap.
        """
        closed = [d["outline"] for d in self.decorations]
        open_ = [self.outline(width, taper, base_ext, open_end)]
        return closed, open_

    def __repr__(self):
        return (f"Branch(length={self.length:g}, bend={self.bend:g}, "
                f"decorations={len(self.decorations)})")

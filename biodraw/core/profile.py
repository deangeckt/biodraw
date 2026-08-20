"""Profiles: a traced unit outline that can be placed anywhere on a path.

A `Profile` is one small closed shape — a dendritic spine, a bouton, a thorn, a
microvillus — stored once in a canonical frame and then stamped along a
centreline at any size, angle and handedness.

This is the mechanism behind the whole library's look. The spine that ships
with it was **traced off a hand drawing**, not synthesised: every attempt to
build that profile out of ellipses and smoothsteps read as a cone, a bead on a
stick, or a leaf. What makes it read as a spine is a *constant thin neck* for
the first third and then an accelerating flare into a blunt, slightly
up-tilted head — and the easiest way to get those proportions right is to draw
them by hand and trace them.

So tracing is a first-class path, not a fallback: see `biodraw.trace` for
turning your own drawing into a `Profile`, and `biodraw.explain` for checking
the result.

The canonical frame
-------------------
Base chord midpoint at the origin, `+x` along the long axis with the tip at
`x = 1`, `y` across. A profile therefore always has length 1 and is scaled by
`size` at placement time.
"""

import numpy as np

from .geom import perp, resample, unit

__all__ = ["Profile", "register", "get", "available"]


class Profile:
    """A closed unit outline, placeable along any path.

    points   (N, 2) in the canonical frame described above.
    head_t   where along the long axis the widest part sits, as a fraction of
             the length. Anything that has to *aim* at the profile — a
             connector, a synapse dot, a label's leader line — targets this
             rather than the tip, so that a stand-off radius stays symmetric
             however the shape arrives.
    head_r   the stand-off radius to use there, again as a fraction of length.
    stretch  `(lo, hi)` span of the long axis that absorbs `extend` at
             placement time. For a spine that is the neck: extending it makes
             the shape stand further off its branch *without* inflating the
             head, which plain scaling cannot do. `None` disables extension.
    source   free text provenance — where this shape came from. Kept because a
             traced profile is a claim about what something looks like, and the
             next person deserves to know whose drawing it was.
    """

    __slots__ = ("points", "name", "head_t", "head_r", "stretch", "source")

    def __init__(self, points, name=None, head_t=0.82, head_r=0.28,
                 stretch=None, source=None, normalize=False, n_pts=None,
                 tip="wide"):
        p = np.asarray(points, dtype=float)
        if p.ndim != 2 or p.shape[1] != 2:
            raise ValueError("profile points must be an (N, 2) array")
        if normalize:
            p = _to_canonical(p, tip=tip)
        if n_pts:
            p = resample(p, int(n_pts), closed=True)
        self.points = p
        self.name = name
        self.head_t = float(head_t)
        self.head_r = float(head_r)
        self.stretch = None if stretch is None else (float(stretch[0]),
                                                     float(stretch[1]))
        self.source = source

    # -- geometry ---------------------------------------------------------

    def _stretched_x(self, x, ext):
        """The long-axis coordinate with `ext` of extra length inserted into
        the `stretch` span.

        Scaling a profile whole makes a spine that stands further off its
        branch also grow a bigger head — and past a point the heads on a
        densely decorated branch start touching while the necks stay stubby.
        This lengthens the shape *without* resizing anything: the span
        `(lo, hi)` is stretched to hold `ext` more, and everything distal to it
        — the flare and the head, the whole recognisable part — is carried out
        rigidly by the same `ext`.

        `ext` is in canonical units (fractions of the placed `size`), so the
        total length becomes `1 + ext`.
        """
        x = np.asarray(x, dtype=float)
        if not ext or self.stretch is None:
            return x
        lo, hi = self.stretch
        span = hi - lo
        if span <= 0:
            raise ValueError("stretch span must be positive")
        return np.select(
            [x <= lo, x <= hi],
            [x, lo + (x - lo) * (1.0 + ext / span)],
            default=x + ext,
        )

    def head_offset(self, size=1.0, extend=0.0):
        """Distance from the base to the widest point, at this size.

        `extend` carries the head out rigidly, so it lands on the offset
        one-for-one and `head_r` is unchanged — which is why a stand-off
        computed from `head_r` keeps working at any extension.
        """
        return float(size) * self.head_t + float(extend)

    def _width_scale(self, x, head, neck):
        """Per-point multiplier on the half-width: `neck` over the neck,
        `head` over the head, blended between.

        A traced profile is one shape, and the thing people vary about a
        spine is not its length — it is how fat the head is against how thin
        the neck is. Thin, stubby and mushroom spines are the same outline at
        three settings of these two, in the same way the radial cells are one
        body plan at five settings.

        The blend runs from the end of the `stretch` span (the neck, for a
        spine) to `head_t` (the widest point), smoothstepped so neither end
        of the transition shows as a crease in the wall. Only the *width*
        moves: length stays with `size` and `extend`, so `head_offset` — what
        a connector aims at — is unchanged by either of these.
        """
        if head == 1.0 and neck == 1.0:
            return 1.0
        x0 = self.stretch[1] if self.stretch is not None else 0.0
        x1 = self.head_t
        if x1 <= x0:                      # no room to blend: a hard step
            return np.where(x <= x0, neck, head)
        t = np.clip((x - x0) / (x1 - x0), 0.0, 1.0)
        return neck + (head - neck) * t * t * (3.0 - 2.0 * t)

    def place(self, base, direction, size, mirror=False, sink=0.06,
              extend=0.0, head=1.0, neck=1.0):
        """This profile, rotated onto `direction`, scaled by `size`, and rooted
        at `base`.

        `base` is expected to be on the host path's *centreline*, so the shape
        is sunk `sink` of its length back along the axis — enough that the flat
        base chord ends up inside the host's wall instead of showing as a stub.
        Sinking further eats the neck, which is short to begin with and is most
        of what makes a spine read as a spine.

        `mirror` flips the traced wobble across the long axis, so decorations
        on the two sides of a branch are mirror images rather than N copies of
        the same asymmetry.

        `extend` lengthens the `stretch` span only, in the same units as
        `size`.

        `head` and `neck` scale the width of each — see `_width_scale`. The
        defaults are the traced shape.

        Returns the closed outline in the host's units.
        """
        u = unit(direction)
        v = perp(u)                       # across the profile
        q = self.points.copy()
        if mirror:
            q[:, 1] *= -1.0
        size = float(size)
        # Widths come off the *traced* x, before the stretch moves it: the
        # neck is the neck however long it has been made.
        q[:, 1] *= self._width_scale(q[:, 0], float(head), float(neck))
        if extend:
            q[:, 0] = self._stretched_x(q[:, 0], float(extend) / size)
        q[:, 0] -= float(sink)
        return np.asarray(base, dtype=float) + size * (np.outer(q[:, 0], u)
                                                       + np.outer(q[:, 1], v))

    # -- introspection ----------------------------------------------------

    @property
    def length(self):
        """Extent along the long axis, in canonical units (1.0 when traced)."""
        return float(self.points[:, 0].max() - self.points[:, 0].min())

    @property
    def width(self):
        """Widest extent across the long axis, in canonical units."""
        return float(self.points[:, 1].max() - self.points[:, 1].min())

    def describe(self):
        """A plain dict of what this profile is — for `biodraw.catalog` and for
        anything else that needs to report on a shape without drawing it."""
        return {
            "name": self.name,
            "n_points": int(len(self.points)),
            "length": round(self.length, 4),
            "width": round(self.width, 4),
            "head_t": self.head_t,
            "head_r": self.head_r,
            "stretch": self.stretch,
            "source": self.source,
        }

    def __repr__(self):
        name = self.name or "unnamed"
        return (f"Profile({name!r}, n={len(self.points)}, "
                f"head_t={self.head_t}, stretch={self.stretch})")


def _to_canonical(points, tip="wide"):
    """Put a traced outline into the canonical frame.

    The long axis is taken as the direction of greatest spread (the first
    principal component), the shape is turned onto it, and it is scaled so it
    spans x=0 to x=1.

    Which *end* becomes the tip cannot be guessed reliably, because it differs
    by shape: a spine is attached by a narrow neck and ends in a wide head,
    while a thorn or a cilium is the other way round. So `tip` says which:

      'wide'    the broader end becomes the tip (a spine, a bouton, a club)
      'narrow'  the narrower end becomes the tip (a thorn, a cone, a cilium)
      None      leave the orientation the trace came in with

    Ends are compared by how far the outline spreads across the axis within the
    outer tenth of the length at each end.
    """
    p = np.asarray(points, dtype=float)
    c = p - p.mean(axis=0)
    _, _, vt = np.linalg.svd(c, full_matrices=False)
    u = vt[0]
    q = np.column_stack([c @ u, c @ perp(u)])

    lo, hi = q[:, 0].min(), q[:, 0].max()
    span = hi - lo
    if tip is not None:
        wide_lo = np.ptp(q[q[:, 0] <= lo + 0.1 * span, 1])
        wide_hi = np.ptp(q[q[:, 0] >= hi - 0.1 * span, 1])
        tip_at_hi = (wide_hi >= wide_lo) if tip == "wide" \
            else (wide_hi <= wide_lo)
        if not tip_at_hi:
            q[:, 0] *= -1.0
            lo, hi = -hi, -lo

    q[:, 0] -= lo
    return q / (hi - lo)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_REGISTRY = {}


def register(name, profile, overwrite=False):
    """Add a profile to the registry under `name`.

    This is how a contributed shape becomes available by name everywhere —
    `branch.decorate('bouton', ...)` finds it without importing anything.
    """
    if not overwrite and name in _REGISTRY:
        raise KeyError(f"profile {name!r} is already registered; "
                       "pass overwrite=True to replace it")
    if profile.name is None:
        profile.name = name
    _REGISTRY[name] = profile
    return profile


def get(profile):
    """A `Profile`, from either a registered name or a `Profile` itself.

    Accepting both means every call site that takes a profile takes a string
    too, which keeps the usage side short.
    """
    if isinstance(profile, Profile):
        return profile
    try:
        return _REGISTRY[profile]
    except KeyError:
        raise KeyError(
            f"unknown profile {profile!r}; available: {sorted(_REGISTRY)}"
        ) from None


def available():
    """Every registered profile name."""
    return sorted(_REGISTRY)

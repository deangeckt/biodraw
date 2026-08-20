"""Small vector and polyline utilities.

Everything in `biodraw` works in plain (n, 2) float arrays of *local units* —
there is no coordinate class and no unit system. A drawing is built in whatever
units are convenient for it, and the axes are fitted around the result
(`biodraw.io.fit`), so "1 unit" means only what a given shape decides it means.

The one convention that is figure-wide: a **direction** is a unit vector, and
the **outward normal** of a polyline point is 90 degrees counter-clockwise of
its tangent. Anchors (`biodraw.core.anchor`) rely on that sign.
"""

import numpy as np

__all__ = [
    "unit", "rot", "rot_matrix", "perp",
    "tangents", "normals", "arclength", "resample",
    "signed_area",
    "support", "close_ring", "is_closed",
]


def unit(v):
    """`v` scaled to length 1."""
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    if n == 0:
        raise ValueError("cannot take the direction of a zero-length vector")
    return v / n


def rot(v, deg):
    """`v` turned `deg` degrees counter-clockwise."""
    a = np.deg2rad(float(deg))
    c, s = np.cos(a), np.sin(a)
    v = np.asarray(v, dtype=float)
    return np.array([v[0] * c - v[1] * s, v[0] * s + v[1] * c])


def rot_matrix(deg):
    """The 2x2 rotation by `deg` counter-clockwise.

    Returned rather than applied so a caller can fold the turn into its own
    local -> world map and have everything downstream — outlines, anchors,
    fitted limits — come out already rotated. See `biodraw.core.shape`.
    """
    a = np.deg2rad(float(deg))
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s], [s, c]])


def perp(v):
    """`v` turned 90 degrees CCW — the outward-normal convention."""
    v = np.asarray(v, dtype=float)
    return np.array([-v[1], v[0]])


def tangents(pts):
    """Unit tangent at every point of a polyline, by central difference."""
    c = np.asarray(pts, dtype=float)
    d = np.gradient(c, axis=0)
    return d / np.linalg.norm(d, axis=1)[:, None]


def normals(pts):
    """Unit normal at every polyline point, 90 degrees CCW of the tangent."""
    t = tangents(pts)
    return np.column_stack([-t[:, 1], t[:, 0]])


def arclength(pts, normalized=False):
    """Cumulative distance along a polyline, starting at 0.

    `normalized` divides through by the total, giving the arclength parameter
    that `resample` inverts.
    """
    c = np.asarray(pts, dtype=float)
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(c, axis=0),
                                                        axis=1))])
    if normalized:
        total = s[-1]
        return s / total if total else s
    return s


def resample(pts, n, closed=False):
    """A polyline re-sampled to `n` points evenly spaced *along its arclength*.

    Traced outlines come in with whatever spacing the tracing produced —
    bunched on the curves, sparse on the straights — which makes two profiles
    impossible to compare or blend point-for-point. Everything stored as a
    `Profile` is resampled through here first, so a profile's vertex `k` always
    means the same fraction of the way around it.
    """
    c = np.asarray(pts, dtype=float)
    if closed:
        c = np.vstack([c, c[:1]])
    s = arclength(c, normalized=True)
    # Duplicate points give a zero-length step and a flat stretch in `s`, which
    # np.interp handles by taking the last of the tied values — fine here, but
    # it wastes an output vertex, so drop them first.
    keep = np.concatenate([[True], np.diff(s) > 0])
    c, s = c[keep], s[keep]
    t = np.linspace(0.0, 1.0, int(n), endpoint=not closed)
    return np.column_stack([np.interp(t, s, c[:, 0]),
                            np.interp(t, s, c[:, 1])])


def support(points, direction):
    """The vertex furthest along `direction` — a point on the outer rim.

    The cheap answer to "where is the edge of this thing at that angle?" for
    a shape that is a **union of parts** and therefore has no closed-form
    outline: a supporting point is on the rim by construction, whatever the
    parts are doing. Anchors on a lobed protein and on an animal silhouette
    are both placed this way.
    """
    d = unit(direction)
    p = np.asarray(points, dtype=float)
    return p[int(np.argmax(p @ d))]


def signed_area(ring):
    """Twice the signed area of a closed ring: positive when counter-clockwise.

    The sign is what "outward" means for a ring whose winding the caller did
    not promise — see `biodraw.core.paths.bowed_ring`.
    """
    v = np.asarray(ring, dtype=float)
    return float(np.sum(v[:, 0] * np.roll(v[:, 1], -1)
                        - np.roll(v[:, 0], -1) * v[:, 1]))


def close_ring(pts):
    """`pts` with the first vertex repeated at the end, if not already."""
    c = np.asarray(pts, dtype=float)
    if np.allclose(c[0], c[-1]):
        return c
    return np.vstack([c, c[:1]])


def is_closed(pts, tol=1e-9):
    """Whether a polyline's ends meet."""
    c = np.asarray(pts, dtype=float)
    return bool(np.linalg.norm(c[0] - c[-1]) <= tol)

"""Path primitives: the shapes everything else is assembled out of.

Pure geometry — these return vertex arrays or `matplotlib.path.Path` objects
and draw nothing. Three families:

* **bodies** — `superellipse`, `bowed_ring`, `rounded_polygon`, `neck_polygon`:
  closed outlines for a cell body.
* **processes** — `tube`: a polyline wrapped into a walled tube, tapered, and
  optionally left open at the far end.
* **connectors** — `elbow`, `cubic_connector`, `fork_tree` and their helpers:
  the strokes that run *between* shapes.

None of this is neuron-specific. A tapered open-ended tube is a dendrite, a
hypha, a vessel or a root hair depending only on what is drawn beside it.
"""

import numpy as np

from .geom import rot, signed_area, unit

__all__ = [
    "tube", "buried_base", "rall_widths",
    "superellipse", "superellipse_radius", "superellipse_param", "bowed_ring",
    "rounded_polygon",
    "rounded_ring", "neck_polygon", "elbow", "round_polyline",
    "orthogonal_route",
    "arc_rad", "arc3_control", "cubic_connector", "bezier_split",
    "stroke_path", "connector_path", "fork_tree",
]


# ---------------------------------------------------------------------------
# Processes
# ---------------------------------------------------------------------------

def tube(centre, half_w, base_ext=0.0, n_cap=18, open_end=False,
         cap_base=False):
    """Polygon wrapping a polyline: a process drawn as a *tube* with two walls,
    rather than as a stroked line.

    `half_w` is either a scalar or one half-width per centreline point, which
    is what gives the tube its taper. The near end is left as a flat chord and
    pushed `base_ext` back along the starting tangent, so it buries inside
    whatever the tube grows out of (a cell body, or a parent branch) instead of
    showing as a butt joint.

    The far end is capped with a semicircle, unless `open_end` — then there is
    no cap and the vertices are re-ordered to run *tip -> base -> tip*, so the
    one unwalked gap in the ring is the tip chord. Stroke that sequence as an
    open polyline (see `render.render_hollow`'s `open_parts`) and the tube ends
    as two walls that simply stop: the un-closed, runs-off-the-page end of a
    hand-drawn process.

    `cap_base` rounds the near end too, which makes the tube a **capsule**
    rather than a process: closed at both ends, growing out of nothing. That
    is a whole cell rather than a part of one — a bacillus, a mitochondrion, a
    vesicle. It is here rather than in a domain because the alternative was a
    second primitive that differed from this one by a semicircle, and the flat
    base only ever existed to be buried in a parent that a free-floating body
    does not have. Incompatible with `open_end`, which says the opposite
    thing, and with `base_ext`, which exists to bury the chord this removes.
    """
    c = np.asarray(centre, dtype=float)
    w = np.broadcast_to(np.asarray(half_w, dtype=float), (len(c),)).copy()

    d = np.gradient(c, axis=0)
    d = d / np.linalg.norm(d, axis=1)[:, None]
    if base_ext:
        c = np.vstack([c[0] - d[0] * base_ext, c])
        w = np.concatenate([w[:1], w])
        d = np.vstack([d[:1], d])
    n = np.column_stack([-d[:, 1], d[:, 0]])

    left, right = c + n * w[:, None], c - n * w[:, None]
    if open_end:
        if cap_base:
            raise ValueError(
                "open_end and cap_base say opposite things about the near "
                "end: one leaves it running off the page, the other closes "
                "it. Pick one.")
        return np.vstack([right[::-1], left])
    a0 = np.arctan2(n[-1, 1], n[-1, 0])
    ang = a0 - np.linspace(0, np.pi, n_cap)
    cap = c[-1] + w[-1] * np.column_stack([np.cos(ang), np.sin(ang)])
    if not cap_base:
        return np.vstack([left, cap[1:-1], right[::-1]])

    # The ring so far ends at `right[0]`, which is the base on the -n side.
    # Sweeping the angle *down* by pi from there passes through -d[0] — out
    # past the near end — and arrives at +n. Sweeping up would pass through
    # +d[0] instead and fold the cap back inside the tube.
    a1 = np.arctan2(-n[0, 1], -n[0, 0])
    ang = a1 - np.linspace(0, np.pi, n_cap)
    base = c[0] + w[0] * np.column_stack([np.cos(ang), np.sin(ang)])
    return np.vstack([left, cap[1:-1], right[::-1], base[1:-1]])


def buried_base(parent, origin, direction, half_w, n_depth=96, n_chord=24):
    """How far to push a child tube's flat base back so it stays out of sight
    inside the parent outline it grows from.

    A tube's near end is a straight chord across its base, and `tube`'s
    `base_ext` slides that chord back along the axis. Where a child leaves at
    an angle the chord is *tilted*, and burying it is not a matter of pushing
    it deeper: past a point the chord's outer corner swings out through the
    parent's far wall and gets drawn as a spur across the crotch. There is a
    window, not a minimum. Idealising the parent as a straight strip of
    half-width `p` and the child as one of half-width `c` at angle `a`:

        b >= c * tan(a)                 near corner drops below the parent's
                                        own open end
        b <= (p - c * cos(a)) / sin(a)  far corner stays inside its wall

    which is worth knowing because it says when there is *no* window: a child
    as wide as its parent cannot have its base hidden at any depth whatever,
    and neither can one leaving at a steep angle. On a fork that is the whole
    reason two daughters must be thinner than the trunk — see `rall_widths`.

    Rather than use that formula, this searches the real outline, because a
    parent tube is neither straight nor of constant width: it tapers, and it
    leans and wavers. Candidate depths are sampled, the chord is tested
    against the outline at each, and the middle of the widest run of fully
    buried depths is returned — the middle because it is the depth furthest
    from failing at either end.

    If no depth buries the chord completely, the least-exposed one is returned
    rather than raising. A partly visible base chord is a blemish, not a false
    statement about the specimen, and refusing to draw a cell because one
    joint is awkward is the worse failure. `fully_buried` reports which
    happened.

    Returns `(depth, fully_buried)`.
    """
    from matplotlib.path import Path

    poly = parent if isinstance(parent, Path) else Path(
        np.asarray(parent, dtype=float), closed=True)
    o = np.asarray(origin, dtype=float)
    u = unit(direction)
    v = np.array([-u[1], u[0]]) * float(half_w)

    # Far enough to cover the whole window even when the angle is shallow and
    # the child has to reach a long way back.
    span = np.linspace(0.0, 8.0 * float(half_w), int(n_depth))
    ts = np.linspace(-1.0, 1.0, int(n_chord))[:, None]
    scores = np.empty(len(span))
    for i, b in enumerate(span):
        chord = (o - u * b) + ts * v
        scores[i] = poly.contains_points(chord).mean()

    ok = scores >= 1.0
    if not ok.any():
        return float(span[int(np.argmax(scores))]), False

    # Middle of the longest run of buried depths.
    best_len = best_mid = 0
    run = 0
    for i, good in enumerate(ok):
        run = run + 1 if good else 0
        if run > best_len:
            best_len, best_mid = run, i - run // 2
    return float(span[best_mid]), True


def rall_widths(parent_w, ratio=1.0):
    """The two daughter widths at a bifurcation, as `(greater, lesser)`.

    Rall's rule: the daughters' cross-sections sum to the parent's, which for
    the 3/2 power law is `d_p**1.5 == d_1**1.5 + d_2**1.5`. With the lesser
    daughter a fraction `ratio` of the greater, that fixes both.

    Not decoration. Giving each daughter the parent's full width — the obvious
    thing, and what this library did first — makes a fork whose crotch cannot
    be drawn at all: `buried_base` has no solution, and the flat cut across
    each daughter's base is left showing as a spur through the trunk wall.
    Even at `ratio=1.0` the daughters come out at 0.63 of the parent, which is
    what leaves room for the joint.
    """
    r = float(ratio)
    greater = float(parent_w) / (1.0 + r ** 1.5) ** (2.0 / 3.0)
    return greater, greater * r


# ---------------------------------------------------------------------------
# Bodies
# ---------------------------------------------------------------------------

def superellipse(a, b, squareness=3.0, n_pts=240, wobble=0.0, wobble_n=3,
                 wobble_phase=0.20):
    """Closed ring between an ellipse and a rectangle, semi-axes `a`, `b`.

    |x/a|^s + |y/b|^s = 1: s=2 is an ellipse, s -> infinity a rectangle, and
    the ~2.5-4 window is a rounded-square cell body — round enough to read as a
    cell, cornered enough that a process can come out of each corner instead of
    sliding around a circle.

    `wobble` swells and pinches the radius by that fraction over `wobble_n`
    cycles, which is what keeps the ring from reading as a drafted primitive.
    """
    t = np.linspace(0, 2 * np.pi, int(n_pts), endpoint=False)
    ct, st = np.cos(t), np.sin(t)
    e = 2.0 / float(squareness)
    xy = np.column_stack([a * np.sign(ct) * np.abs(ct) ** e,
                          b * np.sign(st) * np.abs(st) ** e])
    if wobble:
        xy = xy * (1 + wobble * np.sin(wobble_n * t
                                       + 2 * np.pi * wobble_phase))[:, None]
    return xy


def superellipse_radius(direction, a, b, squareness):
    """Distance from the centre to the `superellipse` wall along `direction`.

    This is how a process finds the point on a body to grow out of: root it at
    `centre + radius * direction` and it starts exactly on the wall, whatever
    the body's proportions.
    """
    d = unit(direction)
    s = float(squareness)
    return (abs(d[0] / a) ** s + abs(d[1] / b) ** s) ** (-1.0 / s)


def superellipse_param(direction, a, b, squareness):
    """The `t` at which `superellipse` draws the wall point along `direction`.

    The inverse of the map `superellipse` runs forward, and it exists because
    the two angles are not the same one. `superellipse` sweeps a *parameter*
    `t` and puts the wall at `(a|cos t|^e, b|sin t|^e)`; the polar angle of
    that point equals `t` only when `a == b` and the exponent is 1.

    Anything that has to re-evaluate a `t`-indexed term at a known direction
    therefore has to come back through here first. The wobble is exactly that
    term: `Blob.wall_radius` re-applied it at the polar angle, so on a
    flattened cell every wall anchor and every protrusion root sat off the
    drawn wall — measured at 0.011 local units on a body of radius 0.55, and
    exactly 0 on every round one, which is the signature of this mistake.
    """
    d = unit(direction)
    r = superellipse_radius(d, a, b, squareness)
    x, y = r * d[0] / float(a), r * d[1] / float(b)
    # e = 2/s is the forward exponent, so 1/e = s/2 undoes it. Both components
    # are inverted on their own magnitude and given the sign back, which is
    # what keeps this exact in all four quadrants.
    p = float(squareness) / 2.0
    return np.arctan2(np.sign(y) * abs(y) ** p, np.sign(x) * abs(x) ** p)


def bowed_ring(verts, bows, n_per_edge=16):
    """Ring of `verts` with each edge replaced by a shallow parabolic arc.

    `bows[i]` bows edge i (`verts[i]` -> `verts[i+1]`) by that fraction of its
    own length, positive = outward, and is at its full value at the midpoint,
    falling to nothing at both ends (4t(1-t)) so the corners stay put. A body
    drawn with dead-straight edges reads as a drafted polygon; a hair of bow is
    what makes it read as a cell — in particular a bottom edge with two
    processes hanging off its corners wants a *negative* bow, arching up
    between the two roots that pull down on it.

    The orientation is taken from the ring's signed area, so "outward" means
    outward whichever way the caller happened to list the vertices.
    """
    v = np.asarray(verts, dtype=float)
    sign = np.sign(signed_area(v)) or 1.0
    t = np.linspace(0, 1, n_per_edge, endpoint=False)
    ring = []
    for i, bow in enumerate(bows):
        a, b = v[i], v[(i + 1) % len(v)]
        d = b - a
        length = np.linalg.norm(d)
        out = np.array([d[1], -d[0]]) / length * sign
        ring.append(a + np.outer(t, d)
                    + np.outer(4 * t * (1 - t) * bow * length, out))
    return np.vstack(ring)


def rounded_polygon(verts, radius):
    """Closed Path through `verts` with each corner cut to a quadratic fillet.

    matplotlib's `joinstyle='round'` only rounds the *stroke*, so a thin-edged
    triangle still has needle-sharp corners. Cutting the corner into a CURVE3
    fillet rounds the filled shape itself, which is what a hand-drawn body
    looks like.
    """
    from matplotlib.path import Path
    verts = np.asarray(verts, dtype=float)
    pts, codes = [], []
    n = len(verts)
    for i in range(n):
        p_prev, p, p_next = verts[i - 1], verts[i], verts[(i + 1) % n]
        v_in, v_out = p - p_prev, p_next - p
        l_in, l_out = np.linalg.norm(v_in), np.linalg.norm(v_out)
        r = min(radius, l_in / 2, l_out / 2)
        a = p - v_in / l_in * r
        b = p + v_out / l_out * r
        pts.append(a)
        codes.append(Path.MOVETO if i == 0 else Path.LINETO)
        pts += [p, b]
        codes += [Path.CURVE3, Path.CURVE3]
    pts.append(pts[0])
    codes.append(Path.CLOSEPOLY)
    return Path(np.array(pts), codes)


def neck_polygon(apex, base_l, base_r, hw, neck_r, corner_r,
                 bow_bottom, bow_side, n_arc=24, n_edge=16):
    """Triangular body whose apex is replaced by a smooth *neck* into a
    vertical tube of half-width `hw`.

    On each side, the slanted edge rises from its base corner up to a tangent
    point `P_s`, then turns tangentially into the tube wall via a fillet arc of
    radius `neck_r` — ending at `P_t` on the wall (x = +/- hw). The polygon
    closes with a straight horizontal chord across the top from `P_t_right` to
    `P_t_left`; that chord lies inside the tube's fill and never surfaces in
    the render. Base corners are rounded by `corner_r` (clamped to half of each
    incident edge), and each straight edge carries the same shallow parabolic
    bow (`4t(1-t)`) as `bowed_ring`.

    The reason for going to the trouble: cutting the apex flat leaves two
    visible corner *stacks* at each shoulder — slanted-edge -> flat-top, then
    flat-top -> tube-wall — and a scalar fillet fed through `bowed_ring` +
    `rounded_polygon` gets clamped by the ring's sub-edge spacing to nothing at
    those shoulders. The arc replaces both corners with one C1-smooth
    transition where the outline itself curves from slanted into vertical, and
    there is no corner left to round.

    Specialised, for now, to an upright triangle joining a *vertical* tube
    centred on x=0 — which is what a pyramidal soma needs. The general version
    (any polygon edge into any tube at any angle) is the natural next step and
    would subsume this one.

    Returns (Path, {'P_s_l', 'P_s_r', 'P_t_l', 'P_t_r'}). The two tangent
    points are handed back so a caller can expose a 4-vertex stand-in polygon
    (`[P_s_l, base_l, base_r, P_s_r]`) — close enough to the drawn outline that
    dot placement lands on the correct slanted edges without knowing about the
    neck at all.
    """
    from matplotlib.path import Path
    apex = np.asarray(apex, dtype=float)
    base_l = np.asarray(base_l, dtype=float)
    base_r = np.asarray(base_r, dtype=float)

    bx = float(-base_l[0])
    by_ = float(base_l[1])
    ay = float(apex[1])
    L_slant = np.hypot(bx, ay - by_)
    ux, uy = bx / L_slant, (ay - by_) / L_slant
    px, py = -uy, ux                             # perp, 90 deg CCW of edge

    # Left arc: solve C.x = -hw - r, with C = P_s + r * perp and
    # P_s = base_l + s * edge.
    s = (bx - hw - neck_r - neck_r * px) / bx
    P_s_l = np.array([-bx + s * bx, by_ + s * (ay - by_)])
    C_l = P_s_l + neck_r * np.array([px, py])
    P_t_l = np.array([-hw, C_l[1]])
    # Mirror for the right side.
    P_s_r = np.array([-P_s_l[0], P_s_l[1]])
    C_r = np.array([-C_l[0], C_l[1]])
    P_t_r = np.array([-P_t_l[0], P_t_l[1]])

    ang_s_l = np.arctan2(P_s_l[1] - C_l[1], P_s_l[0] - C_l[0])
    ang_t_l = np.arctan2(P_t_l[1] - C_l[1], P_t_l[0] - C_l[0])
    alpha = (ang_t_l - ang_s_l) % (2 * np.pi)         # CCW sweep, left side
    thetas_l = ang_s_l + np.linspace(0, alpha, n_arc)
    arc_l = C_l + neck_r * np.column_stack([np.cos(thetas_l),
                                            np.sin(thetas_l)])
    ang_s_r = np.arctan2(P_s_r[1] - C_r[1], P_s_r[0] - C_r[0])
    thetas_r = ang_s_r + np.linspace(0, -alpha, n_arc)   # CW sweep, right side
    arc_r = C_r + neck_r * np.column_stack([np.cos(thetas_r),
                                            np.sin(thetas_r)])

    slant_visible = L_slant * (1.0 - s)               # P_s -> base corner
    r_c = min(float(corner_r), slant_visible / 2, bx)
    u_dn_l = np.array([-ux, -uy])                # P_s_l -> base_l (unit)
    u_dn_r = np.array([ux, -uy])                 # P_s_r -> base_r (unit)
    # Both trims step back *up* their own slant, against the direction that
    # runs down to the corner — hence the minus on each. Getting the right
    # one's sign wrong pushes the fillet's control point outside the body and
    # the corner comes out as a spike instead of a round. It stays invisible
    # in the common case, where a branch is rooted through the corner and its
    # tube covers the evidence.
    trim_bl_slant = base_l - u_dn_l * r_c
    trim_br_slant = base_r - u_dn_r * r_c
    trim_bl_bot = base_l + np.array([r_c, 0.0])
    trim_br_bot = base_r + np.array([-r_c, 0.0])

    def _bowed(a, b, bow, out):
        """`n_edge` samples from a to b, bowed by `bow` x edge-length outward
        along `out` (a unit vector). First/last coincide with a/b."""
        d = b - a
        L = np.linalg.norm(d)
        t = np.linspace(0.0, 1.0, n_edge)
        return a[None] + np.outer(t, d) + np.outer(4 * t * (1 - t) * bow * L,
                                                   out)

    def _out(a, b):
        """Outward normal (rotated 90 deg CW of a->b), which for this clockwise
        traversal points away from the interior."""
        d = b - a
        L = np.linalg.norm(d)
        return np.array([d[1], -d[0]]) / L

    slant_l = _bowed(P_s_l, trim_bl_slant, bow_side, _out(P_s_l,
                                                          trim_bl_slant))
    bot = _bowed(trim_bl_bot, trim_br_bot, bow_bottom,
                 _out(trim_bl_bot, trim_br_bot))
    slant_r = _bowed(trim_br_slant, P_s_r, bow_side, _out(trim_br_slant,
                                                          P_s_r))

    pts, codes = [P_t_l.copy()], [Path.MOVETO]
    # Left arc reversed: P_t_l already placed; walk down to P_s_l.
    for p in arc_l[-2::-1]:
        pts.append(p)
        codes.append(Path.LINETO)
    # Slanted down to the trim near base_l (skip the endpoint already placed).
    for p in slant_l[1:]:
        pts.append(p)
        codes.append(Path.LINETO)
    # Fillet at base_l.
    pts.append(base_l)
    codes.append(Path.CURVE3)
    pts.append(trim_bl_bot)
    codes.append(Path.CURVE3)
    # Bowed bottom.
    for p in bot[1:]:
        pts.append(p)
        codes.append(Path.LINETO)
    # Fillet at base_r.
    pts.append(base_r)
    codes.append(Path.CURVE3)
    pts.append(trim_br_slant)
    codes.append(Path.CURVE3)
    # Slanted up to P_s_r.
    for p in slant_r[1:]:
        pts.append(p)
        codes.append(Path.LINETO)
    # Right arc P_s_r -> P_t_r.
    for p in arc_r[1:]:
        pts.append(p)
        codes.append(Path.LINETO)
    # CLOSEPOLY draws the straight horizontal top back to P_t_l — the segment
    # that stays hidden inside the tube.
    pts.append(pts[0])
    codes.append(Path.CLOSEPOLY)

    return Path(np.array(pts), codes), {"P_s_l": P_s_l, "P_s_r": P_s_r,
                                        "P_t_l": P_t_l, "P_t_r": P_t_r}


# ---------------------------------------------------------------------------
# Connectors
# ---------------------------------------------------------------------------

def elbow(start, direction, run, turn_deg, radius, n_pts=32):
    """The kink between a body and the connector proper: a straight `run` out
    along `direction`, then a fillet of `radius` turning through `turn_deg`,
    and the connector starts where that arc leaves off.

    A real axon does not set off toward its targets the moment it leaves the
    soma — it drops clear of the cell's own dendrites first and turns once it
    is out. Rounding that turn rather than mitring it is what keeps it reading
    as a process and not as a circuit diagram's right angle: `radius` is the
    whole difference between the two, and at 0 the corner is a hard one.

    `turn_deg` is signed counter-clockwise, so with a cell drawn upright and
    `direction` pointing down out of it, +90 sends the connector off right.

    Returns (polyline (n,2), the xy it ends at, the unit direction it ends in).
    """
    d0 = unit(direction)
    s = np.asarray(start, dtype=float)
    p = s + d0 * float(run)
    a, r = float(turn_deg), float(radius)
    if r <= 0 or a == 0:
        return np.vstack([s, p]), p, rot(d0, a)

    # Centre of the fillet, `r` off to whichever side it turns toward. The arc
    # starts where the radius points back at the straight run, so the two meet
    # tangentially and the corner has no visible join.
    n = rot(d0, np.sign(a) * 90.0)
    c = p + r * n
    t = (np.arctan2(-n[1], -n[0])
         + np.deg2rad(a) * np.linspace(0.0, 1.0, int(n_pts)))
    arc = c + r * np.stack([np.cos(t), np.sin(t)], axis=1)
    return np.vstack([[s], arc]), arc[-1], rot(d0, a)


def arc_rad(src, dst, rad):
    """`arc3` curvature that bows a connector *upward* whichever way it runs.

    matplotlib puts the control point at `mid + rad*(dy, -dx)` — 90 degrees
    clockwise off the A->B direction — so one fixed `rad` bows a rightward line
    down and a leftward line up, and a row of cells wired in both directions
    comes out with half its connectors sagging into whatever is below. Flipping
    the sign with the direction is what keeps them all arcing over the row:
    positive `rad` means "bow up" either way.
    """
    return float(rad) * (-1.0 if np.asarray(dst)[0] >= np.asarray(src)[0]
                         else 1.0)


def arc3_control(a, b, rad):
    """Where `arc3,rad=...` places its quadratic control point.

    Every connector is built off this, so a stroke keeps bowing the way `rad`
    has always made it bow however the rest of it is assembled.
    """
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    d = b - a
    return 0.5 * (a + b) + float(rad) * np.array([d[1], -d[0]])


def cubic_connector(a, b, drop, rad, smooth):
    """The cubic one connector runs on: `(start, q1, q2, end)`, `start` being
    the foot of the straight descent out of the body rather than the body.

    Drawing the descent and the run as two pieces — a straight line down and an
    `arc3` on from its end — makes them meet at whatever angle the target
    happens to lie at, and a schematic process that turns a hard corner reads
    as a circuit diagram's wire rather than as part of a cell. Here the descent
    ends in a cubic whose first control point carries *straight on down*, so
    the curve leaves it tangentially and the join disappears; `smooth` is how
    far that control point reaches, as a fraction of the remaining run, and so
    how wide the turn comes out. The far control point is `arc3`'s own
    quadratic one raised to cubic, which leaves the arrival angle and the bow
    `rad` asks for exactly as they were — only the corner changes.

    With `drop` at 0 there is no corner to round, and the whole thing collapses
    back to the plain `arc3` between the two points.
    """
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    a1 = a - [0.0, float(drop)]
    c = arc3_control(a1, b, rad)
    q1 = (a1 - [0.0, float(smooth) * float(np.linalg.norm(b - a1))] if drop
          else a1 + (2.0 / 3.0) * (c - a1))
    return a1, q1, b + (2.0 / 3.0) * (c - b), b


def bezier_split(cubic, t, fallback=(0.0, -1.0)):
    """de Casteljau: the cubic cut at `t` -> (the piece before the cut, the
    unit tangent there). The piece after it is not wanted — what continues past
    a fork is a branch of its own, not the rest of this curve.

    A cubic collapsed to a point has no tangent to report, and `fallback`
    stands in: a stem whose aim lands exactly on the foot of its own descent is
    all descent, so what it hands the branches is the direction it fell in.
    """
    p0, p1, p2, p3 = (np.asarray(p, dtype=float) for p in cubic)
    t = float(t)
    u, v, w = p0 + (p1 - p0) * t, p1 + (p2 - p1) * t, p2 + (p3 - p2) * t
    x, y = u + (v - u) * t, v + (w - v) * t
    d = y - x
    return ((p0, u, x, x + d * t),
            unit(d) if np.linalg.norm(d) > 1e-12 else unit(fallback))


def stroke_path(cubic, start=None):
    """One drawn stroke: a straight run from `start` into the cubic's first
    point (skipped when `start` is None), then the cubic itself."""
    from matplotlib.path import Path
    verts = ([np.asarray(start, dtype=float)] if start is not None else []) \
        + [np.asarray(p, dtype=float) for p in cubic]
    codes = ([Path.MOVETO, Path.LINETO] if start is not None
             else [Path.MOVETO]) + [Path.CURVE4] * 3
    return Path(np.asarray(verts, dtype=float), codes)


def connector_path(a, b, drop, rad, smooth):
    """One connector, `a` -> `b`, as a single stroke with no kink in it."""
    return stroke_path(cubic_connector(a, b, drop, rad, smooth),
                       start=(a if drop else None))


def fork_tree(a, bs, drop, rads, smooth, fork, spread):
    """The connector of a body that reaches several others, as one
    **branching** arbor: a shared stem that forks into a branch per target.

    A cell with two outputs drawn as two separate strokes puts two lines out of
    one body running side by side for as far as their targets agree, which
    reads as two axons — and on a staggered row they promptly cross each other,
    since the lower target's line starts above the higher one's. One process
    that leaves and *branches* is both what the cell actually has and the shape
    a drawn arbor takes, so wiring between cells and a cell's own arbor come
    out in the same hand.

    The stem is the ordinary `cubic_connector` aimed at the targets' centroid
    (but never above the foot of the descent — see below), cut off at `fork` of
    the way along (`bezier_split`), so it descends and turns exactly as a lone
    connector would, toward where its targets are as a group. Each branch then
    leaves the cut on a direction `spread` of the way from the stem's own
    tangent round to its target's bearing, and curves from there on the same
    `smooth` / `rad` terms as any other connector.

    `spread` is that turn, as a fraction of the angle between the stem and the
    branch's own bearing — 0 leaves tangent to the stem, 1 leaves pointing
    straight at the target — and it is what keeps the fork a bifurcation rather
    than a hairpin. Tangent is the smoothest possible crotch and fine while the
    targets lie on ahead, but a staggered row often has a cell sending one
    branch off down the row and one back up it: a target *behind* the fork then
    has its branch turn through most of 180 degrees inside the crotch. Turning
    it at the fork instead splits that between the fork and the run.

    Returns (stem Path, [branch Path per entry of `bs`]).
    """
    a = np.asarray(a, dtype=float)
    bs = [np.asarray(x, dtype=float) for x in bs]
    aim = np.mean(bs, axis=0)
    # ...but never at anything above the foot of the descent. A cell that sends
    # one branch off down the row and one back up it has its targets' centroid
    # level with its own body, and a stem aimed *there* runs straight down for
    # `drop` and then climbs back up through itself: the fork lands above the
    # foot and what is drawn is a needle hanging below the crotch. Holding the
    # aim down at the foot makes the stem the descent and nothing more, and the
    # cell forks at the bottom of it — which is the shape that was wanted.
    aim[1] = min(aim[1], a[1] - float(drop))
    stem_cubic, tang = bezier_split(
        cubic_connector(a, aim, drop, float(np.mean(rads)), smooth), fork)
    f = stem_cubic[-1]
    branches = []
    for b, rad in zip(bs, rads, strict=True):
        u = unit(b - f)
        turn = np.degrees(np.arctan2(tang[0] * u[1] - tang[1] * u[0],
                                     tang @ u))       # stem -> target, signed
        d = rot(tang, turn * float(spread))
        c = arc3_control(f, b, rad)
        q1 = f + d * (float(smooth) * float(np.linalg.norm(b - f)))
        branches.append(stroke_path((f, q1, b + (2.0 / 3.0) * (c - b), b)))
    return stroke_path(stem_cubic, start=(a if drop else None)), branches

def round_polyline(pts, radius, n_arc=8):
    """An open polyline with every interior corner cut to a circular fillet.

    `rounded_polygon` does this for a closed ring; a routed connector is open,
    and its ends must stay exactly where they were put — one of them is a
    shape's anchor and the other is where an arrowhead lands.

    The radius is clamped per corner to half of the shorter adjacent segment,
    so a short leg between two turns cannot produce a fillet that overshoots
    its own neighbours and folds the route back on itself.

    `radius=0` returns the polyline unchanged, which is the right default for
    a bus: a schematic that turns a hard right angle reads as *routing*, and
    that is exactly the claim a shared rail is making. Round it only when the
    line is meant to read as a process.
    """
    q = np.asarray(pts, dtype=float)
    if radius <= 0 or len(q) < 3:
        return q
    out = [q[0]]
    for i in range(1, len(q) - 1):
        prev, here, nxt = q[i - 1], q[i], q[i + 1]
        v_in, v_out = here - prev, nxt - here
        l_in, l_out = np.linalg.norm(v_in), np.linalg.norm(v_out)
        if l_in < 1e-12 or l_out < 1e-12:
            continue
        r = min(float(radius), l_in / 2, l_out / 2)
        a = here - v_in / l_in * r
        b = here + v_out / l_out * r
        # Quadratic Bezier through the corner, sampled — the fillet only has
        # to look round, and sampling keeps the result a plain polyline that
        # anything downstream can measure.
        t = np.linspace(0.0, 1.0, int(n_arc))[:, None]
        out.append(a)
        out.append((1 - t) ** 2 * a + 2 * (1 - t) * t * here + t ** 2 * b)
        out.append(b)
    out.append(q[-1])
    return np.vstack([o if o.ndim == 2 else o[None] for o in out])


def rounded_ring(verts, radius, n_arc=10):
    """`rounded_polygon`'s fillets as plain vertices, closed.

    The Path form is what matplotlib wants to *draw*; anything that has to be
    transformed, measured or fused — a glyph on a `Track`, a shape's own
    `_parts` — needs vertices. Rather than a second fillet implementation,
    this walks the ring as an open polyline with the seam moved to the
    **midpoint of the closing edge**, so every original corner is an interior
    one that `round_polyline` will round, and the seam itself falls where no
    fillet reaches.
    """
    q = np.asarray(verts, dtype=float)
    seam = 0.5 * (q[-1] + q[0])
    return round_polyline(np.vstack([seam, q, seam]), radius, n_arc)


def orthogonal_route(a, b, rail, axis="h"):
    """A right-angle route from `a` to `b` by way of a shared `rail`.

    `axis='h'` puts the rail at `y = rail`: the route leaves `a` vertically,
    runs along the rail, and rises into `b` vertically. `'v'` is the same about
    the other axis.

    This is the shape a **bus** makes, and it is what most summary and circuit
    figures actually draw. A fan of curves from one source to four targets says
    "four separate things happened"; four risers off one horizontal says "these
    all share a source", which is usually the claim. It is also far easier to
    read at a glance, because the eye follows a straight line and has to trace
    a curve.

    Degenerate legs are dropped, so a target already on the rail gives a plain
    two-point line rather than a zero-length kink.
    """
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    rail = float(rail)
    if axis == "h":
        pts = [a, [a[0], rail], [b[0], rail], b]
    elif axis == "v":
        pts = [a, [rail, a[1]], [rail, b[1]], b]
    else:
        raise ValueError(f"axis must be 'h' or 'v', not {axis!r}")
    out = [np.asarray(pts[0], dtype=float)]
    for q in pts[1:]:
        q = np.asarray(q, dtype=float)
        if np.linalg.norm(q - out[-1]) > 1e-12:
            out.append(q)
    return np.vstack(out)

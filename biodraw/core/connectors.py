"""Connectors: the strokes that run *between* shapes.

`paths` already has the curves — `cubic_connector` for one target, `fork_tree`
for several. What is missing between those and a figure is everything about
where a connector *starts and stops*: it should leave a shape at the place
that shape says things leave from, arrive at the face of its target rather
than in the middle of it, stand off by a clearance that means the same at
every angle, and end in a mark that says what kind of contact it is.

That is what an `Anchor` is for, and this module is the half that consumes
them. Hand it two anchors and it does the rest — which is why a shape that
exposes anchors gets connectors for free, without this module knowing whether
it joined two neurons, two organs or two boxes.

Endcaps
-------
The mark at the far end is a claim, not decoration:

    'dot'    a filled disc — a synapse, a contact, a junction
    'bar'    a stroke across the arrival direction — inhibition, a block
    'arrow'  a head — flow, direction, causation
    'open'   an unfilled disc — a contact of the same kind, not asserted
    None     nothing; the line simply reaches the wall

Use one meaning per figure and say which in the key.
"""

import numpy as np

from .geom import perp, unit
from .paths import arc_rad, connector_path, fork_tree

__all__ = ["connect", "connect_bus", "connect_tree", "endcap",
           "ENDCAPS"]


#: The marks a connector may end in. Kept as data so `catalog()` can report
#: them and a figure's key can be built from the same list the drawing used.
ENDCAPS = ("dot", "open", "bar", "arrow", None)


def _resolve(point, gap=0.0, toward=None):
    """A connector endpoint, from either an `Anchor` or a bare xy.

    An anchor knows which way is *out* of its shape, so a clearance means the
    same thing wherever it lands and at whatever angle the connector arrives —
    which is the entire reason a stand-off does not have to be hand-tuned per
    contact per figure. A bare point has no such direction and takes the gap
    along the line of travel instead, which is the best that can be done.

    Returns `(xy, outward direction or None)`.
    """
    if hasattr(point, "normal"):
        return point.offset(gap), np.asarray(point.normal, dtype=float)
    p = np.asarray(point, dtype=float)
    if gap and toward is not None:
        d = np.asarray(toward, dtype=float) - p
        if np.linalg.norm(d) > 1e-12:
            p = p - unit(d) * float(gap)
    return p, None


def connect(ax, source, target, gap=0.0, source_gap=None, rad=0.06, drop=0.0,
            smooth=0.25, color="#8A8A8A", lw=1.2, endcap="dot",
            cap_size=26.0, cap_color=None, zorder=2, gid=None, label=None):
    """Draw one connector from `source` to `target`.

    Both may be `Anchor`s or bare `(x, y)` points; anchors are much the
    better idea, because they carry the direction that leads out of their
    shape and so know what a clearance means.

      gap         clearance at the target, in local units — how far short of
                  the wall the line stops. `source_gap` for the other end;
                  `None` reuses `gap`.
      rad         how far the run bows. Positive always bows **up**, whichever
                  way the connector runs, so a row of cells wired in both
                  directions does not come out with half its lines sagging.
      drop        a straight descent out of the source before the run begins.
                  A process does not set off toward its target the moment it
                  leaves the cell; it drops clear of the cell's own dendrites
                  first. At 0 there is no descent and the whole thing is the
                  plain bowed curve.
      smooth      how wide the turn out of that descent is, as a fraction of
                  the remaining run. This is what stops the join reading as a
                  circuit diagram's corner.
      endcap      the mark at the target — see `ENDCAPS`. It is a claim about
                  what kind of contact this is; keep one meaning per figure.
      label       text at the target end, offset along its normal.

    Returns the list of artists.
    """
    src, _ = _resolve(source, 0.0)
    dst, dst_n = _resolve(target, gap, toward=src)
    src, _ = _resolve(source, gap if source_gap is None else source_gap,
                      toward=dst)

    artists = []
    path = connector_path(src, dst, drop=drop, rad=arc_rad(src, dst, rad),
                          smooth=smooth)
    from matplotlib.patches import PathPatch
    line = PathPatch(path, facecolor="none", edgecolor=color, lw=lw,
                     joinstyle="round", capstyle="round", zorder=zorder)
    ax.add_patch(line)
    artists.append(line)

    artists += endcap_at(ax, dst, dst_n, kind=endcap, size=cap_size,
                         color=cap_color or color, lw=lw, zorder=zorder + 0.1)

    if label:
        pos = dst + (dst_n if dst_n is not None else np.array([0.0, 1.0])) \
            * (gap + 0.12)
        artists.append(ax.text(pos[0], pos[1], label, fontsize=7.5,
                               color=color, ha="center", va="center",
                               zorder=zorder + 0.2))

    if gid:
        for i, a in enumerate(artists):
            a.set_gid(f"{gid}.{i}")
    return artists


def endcap_at(ax, xy, normal=None, kind="dot", size=26.0, color="#8A8A8A",
              lw=1.2, zorder=3):
    """The mark a connector ends in, at `xy`.

    `normal` is the direction the connector arrived *against* — the way out of
    the target — and orients anything that has an orientation. A bar drawn
    without it lies at whatever angle the axes happen to have, which is the
    one way a bar can say the wrong thing.
    """
    if kind is None:
        return []
    if kind not in ENDCAPS:
        raise ValueError(f"unknown endcap {kind!r}; available: {ENDCAPS}")

    xy = np.asarray(xy, dtype=float)
    n = unit(normal) if normal is not None else np.array([0.0, 1.0])

    if kind == "dot":
        return [ax.scatter([xy[0]], [xy[1]], s=size, color=color,
                           zorder=zorder, linewidths=0)]
    if kind == "open":
        return [ax.scatter([xy[0]], [xy[1]], s=size, facecolor="white",
                           edgecolor=color, linewidths=lw, zorder=zorder)]
    if kind == "bar":
        # Across the arrival direction. Sized off the dot area so a bar and a
        # dot in the same figure read as the same weight of statement.
        half = 0.5 * np.sqrt(float(size)) / 72.0 * 1.8
        t = perp(n) * half
        (ln,) = ax.plot([xy[0] - t[0], xy[0] + t[0]],
                        [xy[1] - t[1], xy[1] + t[1]], color=color,
                        lw=lw * 1.8, solid_capstyle="round", zorder=zorder)
        return [ln]
    # arrow: drawn pointing *into* the target, i.e. against its outward normal.
    #
    # `mutation_scale` is what sizes the head, and leaving it unset pins it to
    # the default font size — so `size` moved the tail and the head stayed put,
    # and an arrowhead could not be made bigger however large a value was
    # passed. On a heavy bus line that came out as a speck on a 2.6pt stroke.
    # The factor is chosen so the default `size=26` renders at ~10.2, which is
    # what the old unset default gave: existing figures are unchanged, and the
    # knob now does what its name says.
    length = np.sqrt(float(size)) / 72.0 * 2.2
    tail = xy + n * length
    return [ax.annotate("", xy=tuple(xy), xytext=tuple(tail),
                        arrowprops=dict(arrowstyle="-|>", color=color,
                                        lw=lw, shrinkA=0, shrinkB=0,
                                        mutation_scale=np.sqrt(float(size))
                                        * 2.0),
                        zorder=zorder)]


def connect_tree(ax, source, targets, gap=0.0, rad=0.06, drop=0.45,
                 smooth=0.25, fork=0.5, spread=0.35, color="#8A8A8A",
                 lw=1.2, endcap="dot", cap_size=26.0, cap_color=None,
                 zorder=2, gid=None):
    """One source reaching several targets, as a single **branching** arbor.

    A cell with two outputs drawn as two separate strokes puts two lines out
    of one body running side by side for as far as their targets agree, which
    reads as two axons — and on a staggered row they promptly cross, since the
    lower target's line starts above the higher one's. One process that leaves
    and *branches* is both what the cell has and what a drawn arbor looks like.

    `fork` is how far along the shared stem the split happens, and `spread`
    how far each branch turns toward its own target at the fork rather than
    leaving tangent to the stem. See `paths.fork_tree` for why tangent is not
    the right default.

    Returns the list of artists.
    """
    from matplotlib.patches import PathPatch

    src, _ = _resolve(source, 0.0)
    ends = [_resolve(t, gap, toward=src) for t in targets]
    pts = [e[0] for e in ends]

    stem, branches = fork_tree(
        src, pts, drop=drop,
        rads=[arc_rad(src, p, rad) for p in pts],
        smooth=smooth, fork=fork, spread=spread)

    artists = []
    for path in [stem, *branches]:
        p = PathPatch(path, facecolor="none", edgecolor=color, lw=lw,
                      joinstyle="round", capstyle="round", zorder=zorder)
        ax.add_patch(p)
        artists.append(p)

    for xy, n in ends:
        artists += endcap_at(ax, xy, n, kind=endcap, size=cap_size,
                             color=cap_color or color, lw=lw,
                             zorder=zorder + 0.1)

    if gid:
        for i, a in enumerate(artists):
            a.set_gid(f"{gid}.{i}")
    return artists


#: `endcap` reads better at a call site than `endcap_at` when the position
#: is obvious; both names are the same function.
endcap = endcap_at

def connect_bus(ax, source, targets, rail, axis="h", gap=0.0, source_gap=0.0,
                corner=0.0, color="#8A8A8A", lw=1.4, lws=None, endcap="arrow",
                cap_size=26.0, cap_color=None, zorder=2, gid=None,
                labels=None):
    """One source reaching several targets through a shared right-angle rail.

    The alternative — a separate curve per target — says *four separate things
    happened*. A stem that drops to one horizontal, with a riser turning up
    into each target, says *these all share a source*, which is usually the
    claim a summary figure is making. It also reads faster: the eye follows a
    straight line and has to trace a curve.

    Drawn as three kinds of stroke so each can carry its own weight:

      the stem   source -> the rail, drawn once
      the rail   one segment spanning every riser, drawn once, so overlapping
                 routes do not stack up into a heavier line than the rest
      a riser    the rail -> each target, one per target

    `lws` gives a per-target riser width. **Line weight is a variable here**:
    a hairline riser beside a heavy one says "this projection is weaker"
    without introducing a second colour, which is the whole reason to keep
    identity colours for identity.

    `corner` rounds the turns. It defaults to 0 — square — because a hard
    right angle is what makes the line read as *routing* rather than as a
    process, and that distinction is the point of using a bus at all.

    `rail` is the coordinate the shared segment sits at: a `y` when `axis='h'`,
    an `x` when `'v'`.

    Returns the list of artists.
    """
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path as MPath

    from .paths import orthogonal_route, round_polyline

    src, _ = _resolve(source, source_gap)
    ends = [_resolve(t, gap, toward=src) for t in targets]
    if lws is None:
        lws = [lw] * len(ends)
    if labels is None:
        labels = [None] * len(ends)

    def _stroke(pts, width):
        pts = round_polyline(pts, corner)
        line = PathPatch(MPath(pts), facecolor="none", edgecolor=color,
                         lw=width, joinstyle="miter", capstyle="butt",
                         zorder=zorder)
        ax.add_patch(line)
        return line

    artists = []
    k = 1 if axis == "h" else 0          # the coordinate the rail fixes
    j = 1 - k                            # the one it runs along

    # The stem, from the source out to the rail.
    foot = np.array(src, dtype=float)
    foot[k] = float(rail)
    artists.append(_stroke(np.vstack([src, foot]), lw))

    # One rail spanning every riser, drawn once at the stem's weight.
    along = [src[j]] + [e[0][j] for e in ends]
    a = np.zeros(2)
    b = np.zeros(2)
    a[k] = b[k] = float(rail)
    a[j], b[j] = min(along), max(along)
    artists.append(_stroke(np.vstack([a, b]), lw))

    # A riser per target, each at its own weight.
    for (dst, dst_n), width, label in zip(ends, lws, labels, strict=True):
        artists.append(_stroke(orthogonal_route(foot, dst, rail, axis=axis),
                               width))
        artists += endcap_at(ax, dst, dst_n, kind=endcap, size=cap_size,
                             color=cap_color or color, lw=width,
                             zorder=zorder + 0.1)
        if label:
            pos = dst + (dst_n if dst_n is not None
                         else np.array([0.0, 1.0])) * (gap + 0.12)
            artists.append(ax.text(pos[0], pos[1], label, fontsize=7.5,
                                   color=color, ha="center", va="center",
                                   zorder=zorder + 0.2))

    if gid:
        for i, art in enumerate(artists):
            art.set_gid(f"{gid}.{i}")
    return artists


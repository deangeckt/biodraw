"""The rendering model: how a set of overlapping outlines becomes one shape.

Everything `biodraw` draws is a *hollow* shape — a wall of some thickness
around a washed interior — and the parts of one drawing (a soma, its
dendrites, every spine on them) must read as **one unbroken contour**, with no
seam where a part meets its neighbour and no line crossing the interior.

matplotlib has no boolean union, so `render_hollow` fakes one. It is the single
most load-bearing function in the package: every shape ultimately draws through
it, and adding a new one is mostly a matter of handing it the right parts.
"""

import numpy as np

__all__ = ["FILL_ALPHA", "shade", "blend", "resolve_fill", "render_hollow"]


# How strongly a shape's interior is tinted with its own (wall) colour, when
# the caller leaves `fill=None`. The shape then reads as a body washed in its
# own ink rather than as an empty outline; 1.0 is the flat colour, 0 the bare
# page. Set here so every shape in a figure — down to the small ones in an
# inset — is washed to the same strength from one place. Pass `fill='white'`
# for a hollow look.
FILL_ALPHA = 0.15


def shade(color, factor):
    """Multiply a colour's RGB by `factor` (<1 darkens, >1 lightens)."""
    import matplotlib.colors as mcolors
    r, g, b = mcolors.to_rgb(color)
    if factor <= 1:
        return (r * factor, g * factor, b * factor)
    return tuple(min(1.0, c + (1 - c) * (factor - 1)) for c in (r, g, b))


def blend(color, alpha, bg="white"):
    """`color` composited onto `bg` at `alpha`, as an *opaque* RGB.

    A hollow shape is faked from overlapping opaque patches (see
    `render_hollow`), so a real `alpha` on those patches would let the pass-1
    strokes show through the pass-2 fill and the seams the whole trick exists
    to hide would come back. Pre-blending onto the page colour instead gives
    the identical result on a `bg`-coloured background while keeping every
    patch opaque.

    The cost is that anything drawn *underneath* a faded shape stays hidden
    rather than showing through it. That is usually what a schematic wants —
    an axon passing behind a cell should be occluded by it — but it is the
    reason `alpha` here is not interchangeable with matplotlib's.
    """
    import matplotlib.colors as mcolors
    a = float(alpha)
    if a >= 1.0:
        return color
    c, b = mcolors.to_rgb(color), mcolors.to_rgb(bg)
    return tuple(ci * a + bi * (1 - a) for ci, bi in zip(c, b, strict=True))


def resolve_fill(fill, fill_alpha, edge, bg="white"):
    """The interior colour of a shape.

    `fill=None` (the default everywhere) means *tint it with the shape's own
    ink*: `edge` pre-blended onto the page at `fill_alpha` (`FILL_ALPHA` when
    that is `None` too). Anything else is taken literally — `'white'` gives
    back a hollow outline.
    """
    if fill is not None:
        return fill
    a = FILL_ALPHA if fill_alpha is None else float(fill_alpha)
    return blend(edge, a, bg)


def render_hollow(ax, parts, fill, edge, wall_lw, zorder=3, open_parts=(),
                  gid=None, alpha=1.0):
    """Draw a group of outlines as one continuous hollow shape.

    The reference is a single unbroken contour: where a spine meets a
    dendrite, or a branch meets a soma, there is no seam and no line crossing
    the interior. This fakes a boolean union in two passes over the same parts:

      1. every part filled *and* stroked in `edge` — a stroke straddles the
         boundary, so each part now covers itself plus `wall_lw/2` beyond it;
      2. every part filled in `fill` with no stroke — which repaints the whole
         union's interior, wiping the pass-1 strokes that fell *inside* a
         neighbouring part.

    What survives is exactly the outer rim of the union: a wall `wall_lw/2`
    points thick with mitre-free joins wherever two parts overlap. Everything
    passed in one call fuses, so parts that must *occlude* each other rather
    than merge have to be rendered as separate groups at different `zorder`.

    `open_parts` are vertex sequences whose wall stops short of closing — the
    open-ended tubes of `paths.tube(open_end=True)`. They join the union the
    same way, except pass 1 strokes them as a *polyline* instead of a patch, so
    the segment that would close the ring never gets any ink. Their area still
    takes part in both fills, which is what leaves the gap the same `fill`
    colour as the interior rather than showing the paper through a notch.

    `wall_lw` is in **points**, so it does not scale when the same drawing is
    rendered smaller — see `biodraw.style` for the per-medium presets that
    exist to handle exactly that.

    `gid` names the group in exported SVG: the artists come back tagged
    `<gid>.wall` and `<gid>.fill`, which is what lets `biodraw.io.save` produce
    a file with labelled layers instead of anonymous paths.

    Returns the list of artists added, pass 1 first.
    """
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path

    def _path(p):
        return p if isinstance(p, Path) else Path(np.asarray(p, dtype=float),
                                                  closed=True)

    paths = [_path(p) for p in parts]
    opens = [np.asarray(p, dtype=float) for p in open_parts]
    artists = []

    # Pass 1 — the wall. Stroked at twice the asked-for width because only the
    # outer half of the stroke survives pass 2; the inner half is what gets
    # repainted, so a stroke of `wall_lw * 2` leaves a wall of `wall_lw`.
    for pth in paths:
        a = PathPatch(pth, facecolor=edge, edgecolor=edge,
                      linewidth=wall_lw * 2, joinstyle="round",
                      capstyle="round", zorder=zorder, alpha=alpha)
        ax.add_patch(a)
        artists.append(a)
    for xy in opens:
        a = PathPatch(_path(xy), facecolor=edge, edgecolor="none",
                      linewidth=0, zorder=zorder, alpha=alpha)
        ax.add_patch(a)
        artists.append(a)
        (line,) = ax.plot(xy[:, 0], xy[:, 1], color=edge,
                          linewidth=wall_lw * 2, solid_joinstyle="round",
                          solid_capstyle="round", zorder=zorder, alpha=alpha)
        artists.append(line)

    # Pass 2 — the interior, a hair above pass 1 so it lands on top of it.
    n_wall = len(artists)
    for pth in paths + [_path(xy) for xy in opens]:
        a = PathPatch(pth, facecolor=fill, edgecolor="none", linewidth=0,
                      zorder=zorder + 0.05, alpha=alpha)
        ax.add_patch(a)
        artists.append(a)

    if gid:
        for i, a in enumerate(artists):
            a.set_gid(f"{gid}.{'wall' if i < n_wall else 'fill'}.{i}")

    return artists

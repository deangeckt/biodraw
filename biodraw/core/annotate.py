"""Annotation: the text that names what a drawing shows.

`connectors` is the half of the anchor contract that draws strokes *between*
shapes. This is the other half — the marks that name *one* place on a shape,
and the bar that says how big it all is.

Why this is in the library at all
---------------------------------
The library draws no text of its own: a glyph carries a `label` string and
exposes an anchor, and the figure writes the words. That stays true here —
nothing below invents a caption. What it owns is the *arithmetic of putting a
given string in the right place*, and the reason is that a `biodraw` drawing
varies by design. Measured across `examples/` before this module existed:

- **61 hand-written label sites.** 50 plain `ax.text`, 11 `ax.annotate` with
  a leader line.
- **20 of them positioned by a typed-in `x, y`.** Those are pinned to numbers
  found by eye: change the shape they name — a wider neck, more spines, an
  animal at `facing=-1` — and the word stays put while the thing moves out
  from under it. Nothing fails. It is wrong only in the picture.
- **30 of them already computing position from the drawing** —
  `ink[:, 1].min() - 0.10`, `ring[:, 0].min() - 0.10`, `0.5 * (x0 + x1)`.
  That is this module, written thirty times, slightly differently each time.

A stock asset can bake its text in because it never changes. Ours changes on
purpose, which is the whole argument for the library — so text that does not
move with it is a defect waiting for a revision.

Alignment is the part that gets reinvented
------------------------------------------
An anchor carries the direction that leads *away* from the shape, and that
direction fixes both halves of the problem at once: where the text sits, and
how it is aligned. A label standing off to the left must be right-aligned or
it grows back over the shape it is naming — which is why the hand-written
sites read `ring[:, 0].min() - 0.10, ..., ha="right"`, an offset and an
alignment that have to be kept in step by hand and silently disagree the
moment either is touched. Here they are one number: `_align`.
"""

import numpy as np

from ..style import palette as _palette

__all__ = ["label", "scalebar"]


#: How far off-axis a normal may lean before its alignment stops being
#: centred. A normal pointing straight up wants centred text above; one
#: pointing up-and-left wants it right-aligned so it grows away from the
#: shape. 0.35 is roughly 20 degrees off the axis — tuned on the mouse's
#: `nose` and `tail` anchors, which lean about 30 degrees and read wrong when
#: centred.
_LEAN = 0.35


def _align(normal):
    """`(ha, va)` for text standing off along `normal`.

    Text grows *away* from the anchor, so the alignment is the side of the
    text nearest the shape: a normal pointing left puts the text's right edge
    against the gap, which is `ha='right'`.
    """
    nx, ny = float(normal[0]), float(normal[1])
    ha = "left" if nx > _LEAN else "right" if nx < -_LEAN else "center"
    va = "bottom" if ny > _LEAN else "top" if ny < -_LEAN else "center"
    return ha, va


def _at(anchor):
    """`(xy, normal)` from an anchor, with a usable error if it is not one.

    Deliberately strict, where `connectors._resolve` is not. A connector
    between two bare points is a real thing to want; a *label* at a bare
    point is `ax.text`, and wrapping it here would add a second way to do
    something matplotlib already does in one line — while quietly dropping
    the only thing this function is for, which is the normal.
    """
    if hasattr(anchor, "xy") and hasattr(anchor, "normal"):
        return (np.asarray(anchor.xy, dtype=float),
                np.asarray(anchor.normal, dtype=float))
    raise TypeError(
        f"label() needs an anchor with a normal, not {type(anchor).__name__}. "
        f"Get one from the shape — cell.anchor('soma'), track.anchor('label', "
        f"index=0) — or, for a position you have already worked out yourself, "
        f"call ax.text directly.")


def label(ax, at, text, gap=0.10, leader=False, fontsize=None, color=None,
          leader_color=None, leader_lw=0.7, palette=None, zorder=6, gid=None,
          **kw):
    """Write `text` beside the anchor `at`, standing off by `gap`.

      ax            the axes to draw on.
      at            an `Anchor`. Its normal sets both the direction the text
                    stands off in and how it is aligned.
      text          the string. The library never invents one.
      gap           clearance from the anchor, in the drawing's own units, so
                    it scales with the shape.
      leader        draw a hairline from the shape out to the text. Off by
                    default: measured over `examples/`, 11 of 61 label sites
                    use one, and the other 50 sit close enough that a line
                    between them would be clutter. Turn it on when the text
                    has to sit clear of a busy drawing.
      fontsize      points. `None` takes matplotlib's own `font.size`, which
                    is the key that already means this — so a future
                    `style.use('poster')` moves labels without this module
                    owning a second copy of the number.
      color         the text. Defaults to the palette's `ink`.
      leader_color  the line. Defaults to the palette's `neutral`, because a
                    leader is furniture: it points, it does not claim.

    Anything else goes through to matplotlib, so `ha`/`va` can override the
    alignment the normal chose when a figure genuinely wants something else.

    Returns the artists drawn, for handing to `bd.fit(..., marks=...)` — text
    is not ink, so nothing else can see it.
    """
    xy, normal = _at(at)
    tip = xy + normal * float(gap)
    colors = _palette.get(palette)
    ha, va = _align(normal)
    kw.setdefault("ha", ha)
    kw.setdefault("va", va)

    artists = []
    if leader:
        # The line stops at the anchor and starts at the text, not the other
        # way round: the gap belongs to the text, so a leader that overshoots
        # into the shape would undo the clearance the anchor exists to give.
        line, = ax.plot([xy[0], tip[0]], [xy[1], tip[1]],
                        color=leader_color or colors["neutral"],
                        lw=float(leader_lw), solid_capstyle="butt",
                        zorder=zorder - 1)
        artists.append(line)

    artists.append(ax.text(
        tip[0], tip[1], text,
        fontsize=fontsize, color=color or colors["ink"], zorder=zorder, **kw))

    if gid:
        for i, a in enumerate(artists):
            a.set_gid(f"{gid}.{i}" if len(artists) > 1 else gid)
    return artists


def scalebar(ax, at, size, per_unit=1.0, units="", side=1, text=None,
             lw=2.0, gap=0.06, fontsize=None, color=None, palette=None,
             zorder=6, gid=None):
    """A bar of a stated real-world length, with the length written on it.

      ax        the axes to draw on.
      at        the bar's **left end**, in the drawing's own units.
      size      how long the bar is *in real units* — 10, for 10 µm.
      per_unit  how many of those real units one drawing unit spans. The bar
                comes out `size / per_unit` long, which is the arithmetic
                every figure currently does by hand.
      units     'µm', 'mm', 'nm'. Only used to write the caption.
      side      +1 puts the caption above the bar, -1 below. Both occur: a
                bar above a row of cells wants its text above it, a bar in
                the corner under a drawing wants it below.
      text      overrides the caption entirely, for '10 µm (approx.)' and the
                like.

    Returns the artists drawn, for `bd.fit(..., marks=...)`. The bar is
    returned as well as the caption because a bar is routinely wider than the
    words under it, so measuring only the text would crop its far end.

    Why this is not four lines of matplotlib
    ----------------------------------------
    A scale bar is the only text on a figure that makes a claim about
    *reality*, and a reader takes it on trust. Two ways the hand-written
    version gets that claim wrong, both silent:

    - **the caps.** A stroked line with the default projecting cap is longer
      than the length it is claiming, by one linewidth — at `lw=2` and a bar
      an inch long that is a 3% overstatement of every measurement a reader
      takes off the figure. `solid_capstyle='butt'` is not cosmetic here, it
      is the difference between the bar being its stated length and not.
    - **the division.** `size / per_unit` inverted still draws a perfectly
      convincing bar. Doing it here means it is done once and pinned by a
      test, rather than retyped per figure.
    """
    colors = _palette.get(palette)
    x0, y0 = float(at[0]), float(at[1])
    length = float(size) / float(per_unit)

    bar, = ax.plot([x0, x0 + length], [y0, y0], color=color or colors["ink"],
                   lw=float(lw), solid_capstyle="butt", zorder=zorder)
    cap = ax.text(
        x0 + length / 2.0, y0 + float(gap) * (1 if side >= 0 else -1),
        text if text is not None else f"{size:g} {units}".strip(),
        ha="center", va="bottom" if side >= 0 else "top",
        fontsize=fontsize, color=color or colors["ink"], zorder=zorder)

    if gid:
        bar.set_gid(f"{gid}.bar")
        cap.set_gid(f"{gid}.text")
    return [bar, cap]

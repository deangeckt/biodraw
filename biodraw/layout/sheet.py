"""Contact sheets: one drawing per parameter setting, laid out as a grid.

The cheapest and most informative thing a shape's documentation can show is
*the same shape under many settings*. A reader learns more from twenty small
cells that differ in one knob each than from one large cell and a paragraph
about what the knob does.

It is also the only thing that scales. A variant drawn into a shared sheet
costs well under a kilobyte once the sheet is saved with
`biodraw.io.save_compact`; the same variant as its own image costs tens of
kilobytes. At a hundred examples that is the difference between a repository
someone can clone and one they cannot.

Beyond documentation, this is how you sweep a parameter you are tuning: build
the sheet, look at it, pick the setting.
"""

import numpy as np

__all__ = ["contact_sheet"]


def contact_sheet(factory, variants, cols=6, labels=None, cell_in=1.0,
                  aspect=1.25, dpi=100, pad=0.25, wall_lw=0.5,
                  label_size=6.0, label_color="#666666", title=None,
                  title_size=10.0, draw_kw=None,
                  row_labels=None, col_labels=None):
    """A grid of shapes, one per entry in `variants`.

      factory   called with each variant's keywords, returning a `Shape`.
      variants  a list of keyword dicts — the settings to compare.
      labels    one caption per variant. `None` labels nothing; `'auto'`
                builds a caption from whichever keys actually differ across
                the variants — it names the thing being varied and stays
                silent about the rest. Good for one or two varying knobs;
                past that the captions are longer than the cells are wide and
                the sheet becomes unreadable.
      row_labels / col_labels
                headers down the left and across the top, for a sweep that is
                genuinely a grid. **Prefer these to per-cell captions when
                more than two knobs vary**: three keys repeated under every
                cell is the same text written twenty times, and it crowds out
                the drawings the sheet exists to show.
      cols      how many across. Rows follow.
      cell_in   width of one cell, in inches; `aspect` its height as a
                multiple of that.
      pad       margin fitted around each shape, in the shape's own units.
                This sets how big the drawing comes out inside its cell.
      wall_lw   wall thickness in points. Small by default: at icon size the
                figure-scale weight reads as a blob.

    Returns `(fig, axes)`.
    """
    import matplotlib.pyplot as plt

    from ..io import canvas

    variants = list(variants)
    if not variants:
        raise ValueError("contact_sheet needs at least one variant")

    if labels == "auto":
        labels = _differing_labels(variants)

    cols = max(1, int(cols))
    rows = -(-len(variants) // cols)
    fig, axes = plt.subplots(rows, cols, dpi=dpi, squeeze=False,
                             figsize=(cols * cell_in,
                                      rows * cell_in * float(aspect)))
    flat = axes.ravel()

    for i, kw in enumerate(variants):
        ax = flat[i]
        canvas(ax=ax)
        shape = factory(**kw)
        shape.draw(ax=ax, wall_lw=wall_lw, **dict(draw_kw or {}))
        shape.fit(ax, pad=pad)
        if labels is not None:
            ax.set_title(labels[i], fontsize=label_size, color=label_color,
                         pad=2.0)
        if col_labels is not None and i < cols:
            ax.set_title(col_labels[i], fontsize=label_size,
                         color=label_color, pad=3.0)
        if row_labels is not None and i % cols == 0:
            # `axis('off')` hides the ylabel with everything else, so put the
            # row header on as text in axes coordinates instead.
            ax.text(-0.08, 0.5, row_labels[i // cols], transform=ax.transAxes,
                    fontsize=label_size, color=label_color, ha="right",
                    va="center", rotation=90)

    # Blank the remainder of the last row rather than leaving empty framed
    # axes, which read as variants that failed to draw.
    for ax in flat[len(variants):]:
        ax.axis("off")

    if title:
        fig.suptitle(title, fontsize=title_size)
    fig.tight_layout(pad=0.2)
    return fig, axes


def _differing_labels(variants):
    """Caption each variant with only the keys that differ between them.

    Naming every keyword would bury the comparison in the settings the
    variants have in common, which is exactly the information the reader
    already has from the surrounding text.
    """
    keys = sorted({k for v in variants for k in v})
    varying = [k for k in keys
               if len({_hashable(v.get(k)) for v in variants}) > 1]
    return [", ".join(f"{k}={_short(v.get(k))}" for k in varying)
            for v in variants]


def _hashable(v):
    return tuple(v) if isinstance(v, (list, np.ndarray)) else v


def _short(v):
    if isinstance(v, float):
        return f"{v:g}"
    return "off" if v is None else str(v)

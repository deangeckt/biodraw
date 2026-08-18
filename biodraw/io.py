"""Canvases and export.

A `biodraw` drawing lives on an ordinary matplotlib axes, which is the point:
everything here composes with real data plots, and a figure can be half
cartoon and half measurement without any special support.

What this module adds is the two ends of that — a canvas set up the way a
drawing needs (aspect-locked, no frame), and an export that produces an SVG a
person can actually edit afterwards.
"""

import os

import numpy as np

__all__ = ["canvas", "fit", "save", "save_compact",
           "QUALITY", "set_quality", "get_quality"]


# How hard documentation rasters are squeezed. Three profiles, because
# "documentation image" turns out to be two different products with opposite
# requirements, and the library was shipping only one of them:
#
#   compact  what a *published* repository can afford to carry. Capped at
#            1000 px and quantized to 32 colours, which is visually lossless
#            on flat line art and about a third the bytes. See the weight
#            budget in docs/PLAN.md.
#   review   the default while this repository is unpublished. A contact
#            sheet of eighteen cells capped at 1000 px gives each cell about
#            55 pixels, which is too few to see a kink in a fork, an overlap
#            between two spine heads, or a wall coming out the wrong weight —
#            the exact things these images exist to let someone check.
#   debug    uncapped, unquantized, 300 dpi. For looking at one shape hard.
#            Never commit these; they are for the screen, not the repo.
#
# The budget is a *publication* constraint, not a development one, so it is
# set in one place and flipped in one place. `BIODRAW_IMAGE_QUALITY` overrides
# it per run without touching code.
QUALITY = {
    "compact": {"max_width": 1000, "colors": 32, "dpi": 100},
    "review": {"max_width": 2400, "colors": 64, "dpi": 200},
    "debug": {"max_width": None, "colors": None, "dpi": 300},
}

#: The profile `save_compact` uses when not told otherwise. Set to 'compact'
#: before publishing, which is the single change that puts the weight budget
#: back in force across every example at once.
DEFAULT_QUALITY = "review"

#: Salt for the ids matplotlib puts on SVG clip paths and gradients. Fixed
#: rather than left to a per-process `uuid4`, so the same figure written twice
#: is the same file — which is what lets CI diff `examples/` and mean it. Any
#: constant string does; changing it rewrites every committed SVG for nothing.
SVG_HASHSALT = "biodraw"

_quality = os.environ.get("BIODRAW_IMAGE_QUALITY", DEFAULT_QUALITY)


def set_quality(name):
    """Choose the raster profile for every later `save_compact`.

    Returns the profile that was in force, so a caller can put it back:

        was = bd.io.set_quality('debug')
        ...
        bd.io.set_quality(was)
    """
    global _quality
    if str(name) not in QUALITY:
        raise KeyError(f"unknown image quality {name!r}; "
                       f"available: {sorted(QUALITY)}")
    was, _quality = _quality, str(name)
    return was


def get_quality(name=None):
    """The named profile as a dict, or the one currently in force."""
    key = _quality if name is None else str(name)
    try:
        return dict(QUALITY[key])
    except KeyError:
        raise KeyError(f"unknown image quality {key!r}; "
                       f"available: {sorted(QUALITY)}") from None


def canvas(figsize=(4.0, 4.0), dpi=150, ax=None, facecolor="white"):
    """A figure and axes ready to be drawn on.

    Aspect-locked, because every shape here is drawn in its own units and a
    non-square axes would shear it; frameless, because a drawing has no axes to
    speak of. Pass an existing `ax` to draw into a panel of a larger figure and
    it is configured in place.

    Returns `(fig, ax)`.
    """
    import matplotlib.pyplot as plt

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=facecolor)
    else:
        fig = ax.figure
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def fit(ax, points, pad=0.20):
    """Fit the axes around everything drawn, with `pad` of margin.

    `pad` is in the drawing's own **local units**, so it scales with the shape
    rather than with the figure. It is also what sets how big the drawing comes
    out inside a fixed panel: the axes box fills its cell whatever it holds, so
    a larger pad shrinks the ink and a smaller one squeezes out the white
    around it.

    `points` may be a single (n, 2) array or any mix of arrays and
    `matplotlib.path.Path` objects.
    """
    parts = []
    for p in ([points] if isinstance(points, np.ndarray) and points.ndim == 2
              else points):
        parts.append(p.vertices if hasattr(p, "vertices")
                     else np.asarray(p, dtype=float))
    pts = np.vstack(parts)
    (x0, y0) = pts.min(axis=0) - pad
    (x1, y1) = pts.max(axis=0) + pad
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    return (x0, y0, x1, y1)


def save_compact(fig, path, quality=None, max_width=None, colors=None,
                 dpi=None, facecolor="white"):
    """Save a raster preview of a drawing.

    Documentation images are the one place `biodraw` is not vector, for a
    reason worth stating: the hollow renderer strokes *and* fills every part,
    so an SVG of a page of cells carries two paths per part and runs to
    megabytes. A PNG of the same page is tens of kilobytes. Measured on a
    sheet of 36 cells: 2,970 kB as SVG, 29 kB as a quantized PNG.

    Three knobs do the work, and each defaults to whatever the current
    `QUALITY` profile says — `set_quality` moves all of them together:

      `max_width`  caps the pixel width. This is the one that decides whether
                   a sheet can be *read*: eighteen cells across a 1000 px
                   image is 55 px each, which is enough to see that a cell
                   was drawn and not enough to see whether it was drawn
                   right.
      `colors`     quantizes to a palette. Flat line art in a handful of inks
                   survives 32 colours essentially unchanged, at about a
                   third the size. `None` skips it.
      `dpi`        what matplotlib renders at before any of the above.

    Pass any of them explicitly to override the profile for one call.

    Pillow does the quantizing and is already a matplotlib dependency, so
    this costs no new install.

    Keep `biodraw.save` for the deliverable itself — a figure going into a
    paper must stay vector.
    """
    from PIL import Image

    prof = get_quality(quality)
    max_width = prof["max_width"] if max_width is None else max_width
    colors = prof["colors"] if colors is None else colors
    dpi = prof["dpi"] if dpi is None else dpi

    path = str(path)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=facecolor)

    im = Image.open(path).convert("RGB")
    if max_width and im.width > int(max_width):
        h = round(im.height * int(max_width) / im.width)
        im = im.resize((int(max_width), h), Image.LANCZOS)
    if colors:
        im = im.quantize(colors=int(colors), method=Image.MEDIANCUT)
    im.save(path, optimize=True)
    return path


def save(fig, path, dpi=300, transparent=False, tight=True, check=True):
    """Save a figure, with the settings a vector drawing actually wants.

    For `.svg` and `.pdf` this keeps text as **text** rather than converting it
    to outlines, so labels stay editable and searchable in Illustrator or
    Inkscape, and the named groups that `render_hollow` tags its artists with
    survive into the file as `id` attributes — which is what lets you select
    "all the spines" in an editor instead of hunting through anonymous paths.

    `check` raises if any artist in the figure is marked for rasterization. A
    single rasterized artist silently turns a vector figure into a vector
    figure with a bitmap stuck in the middle of it, and that is not something
    you want to discover at proof stage.

    The file is also **byte-reproducible**, which matplotlib's own defaults
    are not: an SVG carries a `<dc:date>` of the moment it was written, and
    its clip-path ids come from a `uuid4` regenerated per process. Two
    identical figures therefore produced two different files, which quietly
    breaks the determinism CI enforces on `examples/` and makes every rebuild
    a diff. Both are pinned here — see `SVG_HASHSALT`.
    """
    import matplotlib as mpl

    path = str(path)
    ext = path.rsplit(".", 1)[-1].lower()
    kw = {}

    if check:
        raster = [a for a in fig.findobj() if a.get_rasterized()]
        if raster:
            raise ValueError(
                f"{len(raster)} artist(s) are rasterized, which would embed a "
                f"bitmap in {path}. Pass check=False to save anyway."
            )

    rc = {}
    if ext == "svg":
        rc["svg.fonttype"] = "none"      # text stays text
        # Fixed salt, so clip-path and gradient ids come out the same on every
        # run instead of from a fresh uuid4 each process.
        rc["svg.hashsalt"] = SVG_HASHSALT
        # ...and no creation timestamp, which is the other half of it.
        kw["metadata"] = {"Date": None}
    elif ext in ("pdf", "eps", "ps"):
        rc["pdf.fonttype"] = 42          # TrueType, not Type 3
        rc["ps.fonttype"] = 42
        kw["metadata"] = {"CreationDate": None}

    with mpl.rc_context(rc):
        fig.savefig(path, dpi=dpi, transparent=transparent,
                    bbox_inches="tight" if tight else None, **kw)
    return path

"""Rendering: colour resolution, the hollow union, and two pinned images.

Shape *geometry* is pinned numerically in `test_pins.py` — cheap, exact, and
it does not grow a binary file per shape. Kept here are the two things a
vertex array cannot express, and their count stays at two however many shapes
the library gains:

  * `test_hollow_union` — that overlapping parts really do fuse into one
    contour, which is a fact about paint order, not about geometry;
  * `test_hollow_integration` — a tube, its taper, its open end and its
    decorations rendered together, at a known wall weight.

They run under `pytest --mpl`; without that flag the figures are still built
(so an exception still fails) but not compared. If you change one on purpose::

    pytest --mpl-generate-path=tests/baseline

and say in the PR what changed visually.
"""

import numpy as np
import pytest

import biodraw as bd
from biodraw.core import paths, render
from biodraw.core.branch import Branch

EX = "#FF0000"


# -- colour -----------------------------------------------------------------

def test_blend_is_a_no_op_at_full_alpha():
    assert render.blend(EX, 1.0) == EX


def test_blend_reaches_the_background_at_zero():
    np.testing.assert_allclose(render.blend(EX, 0.0, "white"), (1, 1, 1))


def test_blend_returns_opaque_rgb():
    """Faded shapes are pre-blended, not alpha'd — see `render.blend`."""
    out = render.blend(EX, 0.5, "white")
    assert len(out) == 3
    assert all(0.0 <= c <= 1.0 for c in out)


def test_shade_darkens_and_lightens():
    dark = render.shade("#808080", 0.5)
    light = render.shade("#808080", 1.5)
    assert sum(dark) < 1.5 < sum(light)


def test_resolve_fill_washes_with_the_edge_colour_by_default():
    washed = render.resolve_fill(None, None, EX, "white")
    # A faint red, not the flat colour and not the page.
    assert washed != EX
    assert washed[0] > washed[1]


def test_resolve_fill_takes_an_explicit_colour_literally():
    assert render.resolve_fill("white", 0.5, EX) == "white"


# -- the union --------------------------------------------------------------

def test_render_hollow_draws_two_passes():
    fig, ax = bd.canvas()
    parts = [paths.superellipse(1.0, 1.0)]
    arts = render.render_hollow(ax, parts, "pink", EX, 1.0)
    assert len(arts) == 2                       # one wall, one fill
    assert arts[0].get_zorder() < arts[1].get_zorder()


def test_render_hollow_tags_artists_for_svg():
    fig, ax = bd.canvas()
    arts = render.render_hollow(ax, [paths.superellipse(1.0, 1.0)],
                                "pink", EX, 1.0, gid="cell")
    gids = [a.get_gid() for a in arts]
    assert any(g.startswith("cell.wall") for g in gids)
    assert any(g.startswith("cell.fill") for g in gids)


def test_render_hollow_strokes_open_parts_as_polylines():
    """An open tube gets a patch *and* a line, so its tip chord is uninked."""
    fig, ax = bd.canvas()
    line = np.column_stack([np.linspace(0, 1, 20), np.zeros(20)])
    arts = render.render_hollow(ax, [], "pink", EX, 1.0,
                                open_parts=[paths.tube(line, 0.1,
                                                       open_end=True)])
    assert len(arts) == 3                       # patch + polyline + fill


# -- pinned drawings --------------------------------------------------------

@pytest.mark.mpl_image_compare(baseline_dir="baseline", tolerance=2,
                               remove_text=True)
def test_hollow_union():
    """Three overlapping bodies must come out as one unbroken contour, with
    no seam where any two of them meet."""
    fig, ax = bd.canvas(figsize=(3.0, 3.0))
    parts = [paths.superellipse(0.5, 0.5, 3.0),
             paths.superellipse(0.5, 0.5, 3.0) + [0.55, 0.0],
             paths.superellipse(0.5, 0.5, 3.0) + [0.27, 0.5]]
    render.render_hollow(ax, parts, render.resolve_fill(None, None, EX),
                         EX, 2.0, gid="union")
    bd.fit(ax, parts, pad=0.1)
    return fig


@pytest.mark.mpl_image_compare(baseline_dir="baseline", tolerance=2,
                               remove_text=True)
def test_hollow_integration():
    """Everything the renderer does, in one drawing: a tapered tube whose far
    end is left open, with decorations fused into its wall."""
    fig, ax = bd.canvas(figsize=(2.6, 4.2))
    br = Branch((0.0, 0.0), (0.0, 1.0), length=1.8, bend=0.10)
    br.decorate("spine", n=8, size=0.21, extend=0.04, first_t=0.30,
                last_t=0.86)
    closed, open_ = br.parts(width=0.11, taper=0.72, base_ext=0.05)
    render.render_hollow(ax, closed, render.resolve_fill(None, None, EX),
                         EX, 1.0, open_parts=open_, gid="branch")
    bd.fit(ax, closed + open_, pad=0.12)
    return fig

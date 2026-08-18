"""The cells domain: layers, scattering, and the epithelial row.

These exist to test the claim that the core is domain-neutral, so the
assertions are about the *core* behaving itself on a shape that is not a
neuron — that a nucleus occludes rather than fuses, that neighbours stay
separate, that a seeded scatter is a scatter.

What a cell looks like is the geometry pins' business, not this file's. See
the note at the top of `test_pyramidal.py`.
"""

import numpy as np
import pytest

import biodraw as bd
from biodraw.cells import Blob, Sheet
from biodraw.core.scatter import scatter_in

# -- Blob --------------------------------------------------------------------


def test_an_anucleate_cell_has_no_nucleus_layers():
    """A red cell is a real thing to want, not a degenerate case."""
    cell = Blob(nucleus=None, organelles=3)
    assert [lay.name for lay in cell.layers] == [None, "organelles"]
    assert cell.geometry["nucleolus"] is None
    assert not cell.anchors("nucleus")


def test_the_nucleus_does_not_fuse_into_the_body():
    """The whole reason `Layer` exists: unioned with the body, a nucleus is
    a nucleus you cannot see."""
    cell = Blob(organelles=0, nucleus=0.34, nucleolus=0.0)
    body, nucleus = cell.layers
    assert len(body.closed) == 1
    assert len(nucleus.closed) == 1
    # ...and it is washed harder, which is how it reads as denser without
    # bringing in a second hue.
    assert nucleus.fill_alpha > bd.core.render.FILL_ALPHA


def test_organelles_stay_inside_the_wall_and_out_of_the_nucleus():
    from matplotlib.path import Path
    cell = Blob(organelles=7, seed=4)
    g = cell.geometry
    wall = Path(g["wall"], closed=True)
    nucleus = Path(g["nucleus"], closed=True)
    for o in g["organelles"]:
        assert wall.contains_points(o["outline"]).all()
        assert not nucleus.contains_points(o["outline"]).any()


def test_the_same_seed_gives_the_same_cell():
    a = Blob(organelles=6, seed=11).geometry["organelles"]
    b = Blob(organelles=6, seed=11).geometry["organelles"]
    c = Blob(organelles=6, seed=12).geometry["organelles"]
    for x, y in zip(a, b, strict=True):
        np.testing.assert_allclose(x["centre"], y["centre"])
        assert x["angle_deg"] == y["angle_deg"]
    assert not np.allclose([x["centre"] for x in a], [x["centre"] for x in c])


def test_protrusions_are_rooted_inside_the_wall():
    """Their flat base has to be swallowed by the body's fill, or it shows as
    a butt joint."""
    from matplotlib.path import Path
    cell = Blob(protrusions=8, organelles=0)
    wall = Path(cell.geometry["wall"], closed=True)
    for p in cell.geometry["protrusions"]:
        assert wall.contains_point(p["branch"].origin)
        assert not wall.contains_point(p["branch"].centre[-1])


def test_wall_anchors_point_away_from_the_centre():
    """The bug that made every connector reach through a soma, guarded here
    for a body whose wall is not a straight edge."""
    cell = Blob()
    for a in cell.anchors("wall"):
        assert np.dot(a.normal, a.xy - cell.at) > 0
        assert np.isclose(np.linalg.norm(a.normal), 1.0)


def test_wall_anchors_land_on_the_wobbled_wall():
    """`superellipse_radius` gives the un-wobbled wall; an anchor placed with
    it alone floats off a wobbled outline."""
    cell = Blob(wobble=0.06, wobble_n=5)
    ring = cell.geometry["wall"]
    for a in cell.anchors("wall"):
        gap = np.linalg.norm(ring - a.xy, axis=1).min()
        assert gap < 0.02, f"anchor at {a.meta['deg']}deg sits {gap:.3f} off"


def test_repeated_parts_differ_but_stay_in_order():
    """The same design rule as the pyramidal fork, one level down. The wrap
    case is the one worth guarding: on a full turn the last protrusion must
    not land back on the first."""
    cell = Blob(protrusions=8, protrusion_arc_deg=360.0)
    degs = [p["deg"] for p in cell.geometry["protrusions"]]
    lens = [p["branch"].length for p in cell.geometry["protrusions"]]
    assert np.std(np.diff(degs)) > 1e-6           # not evenly spaced
    assert np.std(lens) > 1e-6                    # nor equally long
    assert (np.diff(degs) > 0).all()              # still in order round it
    assert degs[-1] - degs[0] < 360.0             # and it does not wrap


def test_rotation_carries_the_layers_round():
    """A tip normal is the branch's own tangent, lean and waver included, so
    it is not (1, 0) even on a protrusion aimed along +x. What must hold is
    that turning the cell turns it by the same angle."""
    upright = Blob(protrusions=4)
    turned = Blob(protrusions=4, rotate_deg=90.0)
    for a, b in zip(upright.anchors("tip"), turned.anchors("tip"),
                    strict=True):
        np.testing.assert_allclose(b.normal, (-a.normal[1], a.normal[0]),
                                   atol=1e-9)


# -- Sheet -------------------------------------------------------------------


def test_neighbours_do_not_touch():
    """`gap` is what keeps two walls from erasing half of each other."""
    sheet = Sheet(cells=4, gap=0.06, curve_deg=0.0, corner_r=0.0)
    xs = [c["outline"].vertices[:, 0] for c in sheet.geometry["cells"]]
    for left, right in zip(xs, xs[1:], strict=False):
        assert left.max() < right.min()


def test_a_curved_cell_is_wider_at_the_apical_surface():
    """On an arc the apical surface is longer than the basal one; not
    widening each cell to match opens a wedge between every pair."""
    flat = Sheet(cells=6, curve_deg=0.0).geometry["cells"][0]
    bowed = Sheet(cells=6, curve_deg=120.0).geometry["cells"][0]
    assert np.isclose(flat["hw_apical"], flat["hw_basal"])
    assert bowed["hw_apical"] > bowed["hw_basal"]


def test_a_full_turn_closes_the_ring():
    sheet = Sheet(cells=10, curve_deg=-360.0, height=0.30)
    assert sheet.closed_ring
    # Every cell has a neighbour on both sides, so there is one junction per
    # cell rather than one fewer.
    assert len(sheet.anchors("junction")) == 10
    first = sheet.geometry["cells"][0]["origin"]
    last = sheet.geometry["cells"][-1]["origin"]
    # First and last sit one pitch apart, not a whole row apart.
    assert np.linalg.norm(first - last) < 2 * sheet.cell_w


def test_bending_too_far_for_the_height_is_refused():
    """Rather than drawing a row turned inside out."""
    with pytest.raises(ValueError, match="bends the row tighter"):
        assert Sheet(cells=6, curve_deg=-300.0, height=1.0).geometry


def test_a_gap_wider_than_the_cell_is_refused():
    with pytest.raises(ValueError, match="no apical width"):
        assert Sheet(cells=3, gap=1.4).geometry


# -- scatter -----------------------------------------------------------------

def test_scatter_respects_separation_and_margin():
    from biodraw.core.paths import superellipse
    ring = superellipse(1.0, 0.8, 2.6)
    pts = scatter_in(ring, 8, seed=2, min_sep=0.30, margin=0.15)
    assert len(pts) == 8
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            assert np.linalg.norm(pts[i] - pts[j]) >= 0.30


def test_scatter_says_so_when_it_cannot_fit():
    """Silently placing four when nine were asked for makes the drawing a
    claim the code did not make."""
    from biodraw.core.paths import superellipse
    ring = superellipse(1.0, 1.0, 2.0)
    with pytest.raises(ValueError, match="could not place"):
        scatter_in(ring, 60, seed=0, min_sep=0.9)


def test_scatter_of_nothing_is_empty_rather_than_an_error():
    from biodraw.core.paths import superellipse
    assert scatter_in(superellipse(1.0, 1.0, 2.0), 0).shape == (0, 2)


# -- drawing -----------------------------------------------------------------

def test_blob_draws_and_names_its_layers():
    fig, ax = bd.canvas()
    artists = Blob(organelles=4, protrusions=6).draw(ax=ax, gid="cell")
    gids = {a.get_gid().rsplit(".", 2)[0] for a in artists}
    assert gids == {"cell", "cell.organelles", "cell.nucleus",
                    "cell.nucleolus"}


def test_sheet_draws_and_fits():
    fig, ax = bd.canvas(figsize=(4, 2))
    sheet = Sheet(cells=5, microvilli=4)
    assert sheet.draw(ax=ax, wall_lw=1.0)
    x0, y0, x1, y1 = sheet.fit(ax, pad=0.1)
    assert x1 > x0 and y1 > y0

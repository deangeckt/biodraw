"""The genetics glyphs and the protein body.

Same division as everywhere else: what *must* be true is tested here — a
repeat's width follows its count, a mirrored glyph stays in its own span, a
protein is one connected body and its cleft is inside it — and what merely
*is* true of the drawn outlines is pinned in `tests/shapes.py`.
"""

import numpy as np
from matplotlib.path import Path

from biodraw.genetics import CDS, Promoter, Protein, Repeat, Terminator


def _pts(glyph, x0=0.0):
    closed, open_ = glyph.outline(x0)
    return np.concatenate([np.asarray(p) for p in [*closed, *open_]])


def test_a_repeats_width_follows_its_count():
    """The count is the biology, so the glyph has to grow with it."""
    widths = [Repeat(n=n).width for n in (1, 2, 4, 8)]
    assert all(b > a for a, b in zip(widths, widths[1:], strict=False))
    one, two = Repeat(n=1), Repeat(n=2)
    assert np.isclose(two.width - one.width, one.bar_w + one.bar_gap)


def test_a_repeat_draws_one_part_per_bar():
    closed, _ = Repeat(n=6).outline(0.0)
    assert len(closed) == 6


def test_every_glyph_stays_inside_its_own_span():
    """The track lays glyphs by width alone, so a glyph that draws outside
    its own span silently overlaps its neighbour."""
    for glyph in (Repeat(n=4), Promoter(), CDS(), Terminator()):
        pts = _pts(glyph, x0=1.0)
        assert pts[:, 0].min() >= 1.0 - 1e-9, glyph.name
        assert pts[:, 0].max() <= 1.0 + glyph.width + 1e-9, glyph.name


def test_mirroring_is_about_the_glyphs_own_centre():
    """`strand=-1` must not move anything downstream of it, so the mirror is
    about the glyph's own span and not about the track's origin.

    Not tested as "the extents match": a coding sequence's pointed end is
    filleted and its flat end is not, so the drawn extent is asymmetric by
    the fillet radius even though the mirror is exact.
    """
    for cls in (Promoter, CDS):
        x0, glyph = 1.4, cls(strand=1)
        fwd, rev = _pts(glyph, x0), _pts(cls(strand=-1), x0)
        assert np.allclose(np.sort(2 * x0 + glyph.width - fwd[:, 0]),
                           np.sort(rev[:, 0]))
        assert not np.allclose(np.sort(fwd[:, 0]), np.sort(rev[:, 0]))


def test_a_glyph_that_stands_on_the_line_is_sunk_into_it():
    """Anything rooted on the backbone starts below it, or the union draws a
    seam where the two meet. Shallower than the rail, or it pokes through."""
    from biodraw.core.track import Track

    for glyph in (Promoter(), Terminator()):
        assert -Track().rail < _pts(glyph)[:, 1].min() < 0.0


def test_a_headless_cds_is_a_plain_box():
    """`head=0` drops the direction claim rather than simplifying it, so it
    has to actually square the end off."""
    pointed, plain = _pts(CDS()), _pts(CDS(head=0.0))
    assert np.isclose(plain[:, 1].max(), plain[:, 1].min(), atol=0.28)
    # the pointed one reaches its full width at y=0 only
    tip = pointed[np.argmax(pointed[:, 0])]
    assert abs(tip[1]) < 0.02
    assert (np.abs(plain[np.argmax(plain[:, 0]), 1]) > 0.05)


# ---------------------------------------------------------------------------
# the protein
# ---------------------------------------------------------------------------

def test_the_lobes_overlap_so_the_body_is_one_piece():
    """A body whose lobes come apart is two proteins, whatever it is called.
    Checked at the widest opening the class allows."""
    p = Protein(lobes=2, open_deg=999.0)          # clamped
    assert p.open_deg == Protein.MAX_OPEN_DEG
    a, b = p.geometry["lobes"]
    assert Path(a, closed=True).contains_points(b).any()


def test_the_cleft_is_inside_the_body():
    for open_deg in (8.0, 30.0, 64.0, 90.0):
        p = Protein(lobes=2, open_deg=open_deg)
        cleft = p.geometry["cleft"]
        assert any(Path(lobe, closed=True).contains_point(cleft)
                   for lobe in p.geometry["lobes"]), open_deg


def test_opening_the_body_moves_the_cleft_in_toward_the_hinge():
    """The pair of drawings the figure makes: open, the ligand sits in the
    notch; closed, it is held further out, inside the body."""
    depth = [np.linalg.norm(Protein(open_deg=d).geometry["cleft"])
             for d in (10.0, 40.0, 80.0)]
    assert depth[0] > depth[1] > depth[2]


def test_a_tag_starts_on_the_body_and_ends_off_it():
    p = Protein(lobes=2, tags=(40.0,))
    tag = p.geometry["tags"][0]
    lobes = [Path(lobe, closed=True) for lobe in p.geometry["lobes"]]
    inside = [any(lobe.contains_point(v) for lobe in lobes) for v in tag]
    assert any(inside) and not all(inside)


def test_tag_anchors_stand_clear_of_the_body():
    p = Protein(lobes=2, tags=(40.0, 140.0))
    lobes = [Path(lobe, closed=True) for lobe in p.geometry["lobes"]]
    assert len(p.anchors("tag")) == 2
    for a in p.anchors("tag"):
        assert not any(lobe.contains_point(a.xy) for lobe in lobes)


def test_wall_anchors_point_outward_and_sit_on_the_drawing():
    p = Protein(lobes=2, tags=(40.0,))
    body = np.concatenate(p.geometry["lobes"])
    for a in p.anchors("wall"):
        assert np.isclose(np.linalg.norm(a.normal), 1.0)
        # a supporting point is the extreme one in its own direction
        assert np.max(body @ a.normal) <= a.xy @ a.normal + 1e-9


def test_one_lobe_is_an_oval_and_still_has_a_cleft_point():
    p = Protein(lobes=1)
    assert len(p.geometry["lobes"]) == 1
    assert Path(p.geometry["lobes"][0],
                closed=True).contains_point(p.geometry["cleft"])


def test_lobes_are_not_identical_copies():
    """Drawing rule 1: a repeated part must not repeat exactly. The wobble
    phase is seeded per lobe, so two lobes of one body differ."""
    a, b = Protein(lobes=2, open_deg=0.0).geometry["lobes"]
    assert not np.allclose(a, b)

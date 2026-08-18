"""The pyramidal cell: assembly, placement and anchors.

**What is tested here, and what deliberately is not.** This is a drawing
library, so most of what could be asserted about a cell is a statement about
how it *looks* — how many spines, which leg is longer, how wide the fork
splays. Those are recorded by the geometry pins, which report a change as a
readable diff and cost nothing to accept when the change was wanted.

Tests are for the things that must hold however the drawing is tuned:
placement algebra, anchors pointing out of the shape rather than into it,
determinism, guards that refuse rather than draw nonsense, and the mechanisms
that stop a seam showing. The distinction earned itself — an earlier test
asserted that the two fork daughters were mirror images, which turned the
defect into the specification and had to be deleted before the bug could be
fixed.
"""

import numpy as np
import pytest

import biodraw as bd
from biodraw.neuro import Pyramidal


def test_every_part_is_finite():
    cell = Pyramidal(spines=8, basal=2, basal_spines=5)
    for p in cell.points:
        assert np.isfinite(p).all()


def test_width_follows_spine_size_by_default():
    """One knob should rescale the drawing coherently, not leave fat spines on
    a hairline dendrite."""
    small = Pyramidal(spine_size=0.10)
    big = Pyramidal(spine_size=0.30)
    assert big.width / small.width == pytest.approx(3.0)
    assert Pyramidal(spine_size=0.30, width=0.05).width == 0.05


def test_basal_flare_is_clamped_clear_of_the_soma_edge():
    """A basal narrower than the soma's own slanted edge cannot be rooted
    through its corner, so the flare is clamped rather than allowed to fail."""
    for angle in (0.0, 5.0, 20.0, 40.0):
        cell = Pyramidal(spines=3, basal=2, basal_spines=1,
                         basal_angle_deg=angle)
        for b in cell.geometry["basals"]:
            assert np.isfinite(b["branch"].centre).all()
            # The branch must actually leave the soma, not curl back inside.
            assert b["branch"].centre[-1][1] < cell.geometry["base_l"][1]


def test_basal_root_starts_inside_the_soma():
    """The corner is buried in the tube — that is what stops a notch showing
    where the branch meets the slanted edge."""
    cell = Pyramidal(spines=5, basal=2, basal_spines=3)
    corner = cell.geometry["base_l"]
    origin = cell.geometry["basals"][0]["branch"].origin
    assert origin[1] > corner[1]          # above the base line
    assert origin[0] > corner[0]          # ...and inboard of the corner


def test_forking_adds_two_daughters():
    cell = Pyramidal(spines=0, apical_fork=0.42, fork_spines=4, basal=2,
                     basal_spines=2)
    assert [n for n, _, _ in cell._branches()] == [
        "apical", "apical.l", "apical.r", "basal0", "basal1"]
    # One open-ended tube per branch that ends open: the two daughters and
    # the two basals. The forked trunk is capped, so it is a closed part.
    assert len(cell.parts[1]) == 4
    # An explicit `fork_spines` is taken literally on both daughters; left to
    # itself, each takes its share of the spine *density*.
    counts = sorted(len(cell.anchors("spine", branch=f"apical.{s}"))
                    for s in "lr")
    assert counts == [4, 4]


def test_daughters_leave_from_the_trunk_tip():
    cell = Pyramidal(spines=0, apical_fork=0.5)
    tip = cell.geometry["apical"].centre[-1]
    for d in cell.geometry["daughters"]:
        np.testing.assert_allclose(d["branch"].origin, tip, atol=1e-12)


def test_fork_splits_the_apical_reach_rather_than_extending_it():
    """`trunk_len` must still mean the cell's full apical reach, forked or
    not, or turning the fork on silently grows the cell. It is the *greater*
    daughter that carries the remainder; the lesser one falls short of it,
    which is the point of the fork being unequal."""
    plain = Pyramidal(spines=4, trunk_len=2.0)
    forked = Pyramidal(spines=0, trunk_len=2.0, apical_fork=0.4)
    trunk = forked.geometry["apical"]
    lengths = sorted(d["branch"].length for d in forked.geometry["daughters"])
    assert np.isclose(trunk.length + lengths[-1],
                      plain.geometry["apical"].length)
    assert lengths[0] < lengths[-1]


def test_fork_ratio_of_one_restores_the_mirror():
    """The knob has to be honest about what it does, and 1.0 is the setting
    that gets the old behaviour back."""
    cell = Pyramidal(spines=0, apical_fork=0.42, fork_angle_deg=35,
                     fork_ratio=1.0)
    left, right = (d["branch"] for d in cell.geometry["daughters"])
    assert np.isclose(left.direction[0], -right.direction[0], atol=1e-12)
    assert np.isclose(left.length, right.length)


def test_a_forked_trunk_is_capped_and_its_daughters_are_buried_in_it():
    """The mechanism that stops the crotch showing a glitch, and the same
    class of guard as `test_basal_root_starts_inside_the_soma`.

    An open-ended trunk gives the daughters nothing to bury their flat bases
    in, and at the narrow end of a taper there is no depth at which a base
    chord is both clear of the tip and inside the wall — so the cut is drawn
    as a spur across the fork. Capping the trunk at a junction fixes it; this
    checks the result rather than the reason.
    """
    from matplotlib.path import Path

    for fork in (0.25, 0.45, 0.65):
        for angle in (15, 32, 50):
            cell = Pyramidal(spines=0, apical_fork=fork,
                             fork_angle_deg=angle, fork_spines=3, basal=2)
            closed, open_ = cell.parts
            trunk = Path(np.asarray(closed[0]), closed=True)
            for k in (0, 1):
                v = np.asarray(open_[k])
                m = len(v) // 2                # tip->base->base->tip
                step = (v[m] - v[m - 1])
                chord = v[m - 1] + np.linspace(0, 1, 40)[:, None] * step
                assert trunk.contains_points(chord).all(), (
                    f"daughter {k} of fork={fork} at {angle}° has its base "
                    f"chord showing outside the trunk")


def test_an_unforked_apical_still_ends_open():
    """An open end means the process runs off the page, and that is still
    what an apical that does not fork does."""
    cell = Pyramidal(spines=6, basal=2)
    assert len(cell.parts[1]) == 3           # apical + two basals, all open


def test_spines_are_a_density_not_a_count_per_branch():
    """A count shared between branches of different lengths crowds the short
    ones — the same mistake as sharing a waver's cycle count. Forking halves
    the trunk, so the trunk must carry about half the spines, not all of
    them."""
    plain = Pyramidal(spines=10, basal=0)
    forked = Pyramidal(spines=10, basal=0, apical_fork=0.5)
    assert len(plain.geometry["apical"].decorations) == 10
    trunk = forked.geometry["apical"]
    assert len(trunk.decorations) <= 6
    # ...and the density is what is actually held constant.
    per_plain = 10 / plain.geometry["apical"].length
    per_trunk = len(trunk.decorations) / trunk.length
    assert abs(per_trunk - per_plain) / per_plain < 0.25


def test_repeated_parts_differ():
    """A design rule rather than a look: anything the library makes in pairs
    must differ in the ways real pairs differ. See docs/PLAN.md. The exact
    amounts are the pins' business; that they are not equal is this test's."""
    cell = Pyramidal(spines=4, apical_fork=0.42, basal=2, basal_spines=4)
    for pair in ("daughters", "basals"):
        a, b = (x["branch"] for x in cell.geometry[pair])
        assert not np.isclose(a.length, b.length), f"{pair} equal in length"
        assert not np.isclose(abs(a.direction[0]), abs(b.direction[0])), \
            f"{pair} mirror in angle"
        assert not np.isclose(a.wave_phase, b.wave_phase), \
            f"{pair} share a waver"


def test_a_lone_basal_is_not_the_lesser_one():
    """There is nothing for the cell's only leg to be the lesser of."""
    one = Pyramidal(spines=4, basal=1, basal_spines=4)
    assert one.geometry["basals"][0]["major"]
    assert one.geometry["basals"][0]["width_f"] == 1.0


def test_the_same_seed_gives_the_same_cell():
    a = Pyramidal(spines=0, apical_fork=0.42, seed=7)
    b = Pyramidal(spines=0, apical_fork=0.42, seed=7)
    c = Pyramidal(spines=0, apical_fork=0.42, seed=8)
    for pa, pb in zip(a.points, b.points, strict=True):
        np.testing.assert_allclose(pa, pb)
    assert any(not np.array_equal(pa, pc)
               for pa, pc in zip(a.points, c.points, strict=True))


# -- placement ---------------------------------------------------------------

def test_scale_multiplies_every_length():
    a = Pyramidal(spines=6).points
    b = Pyramidal(spines=6, scale=2.0).points
    for pa, pb in zip(a, b, strict=True):
        np.testing.assert_allclose(pb, pa * 2.0, atol=1e-9)


def test_at_translates_without_resizing():
    a = Pyramidal(spines=6)
    b = Pyramidal(spines=6, at=(3.0, -1.0))
    for pa, pb in zip(a.points, b.points, strict=True):
        np.testing.assert_allclose(pb - np.array([3.0, -1.0]), pa, atol=1e-9)


def test_rotation_carries_the_anchors_round_with_it():
    upright = Pyramidal(spines=6)
    turned = Pyramidal(spines=6, rotate_deg=90.0)
    # The axon leaves downward when upright, and rightward at +90.
    np.testing.assert_allclose(upright.anchor("axon").normal, (0, -1),
                               atol=1e-9)
    np.testing.assert_allclose(turned.anchor("axon").normal, (1, 0), atol=1e-9)


def test_moved_returns_an_independent_copy():
    cell = Pyramidal(spines=6)
    other = cell.moved(at=(5.0, 0.0))
    assert other is not cell
    np.testing.assert_allclose(cell.at, (0.0, 0.0))
    np.testing.assert_allclose(other.at, (5.0, 0.0))


# -- anchors -----------------------------------------------------------------


def test_spine_anchors_are_selectable_by_branch_and_rank():
    cell = Pyramidal(spines=8, basal=2, basal_spines=5)
    apical = cell.anchors("spine", branch="apical")
    assert len(apical) == 8
    distal = cell.anchor("spine", branch="apical", rank=-1)
    proximal = cell.anchor("spine", branch="apical", rank=0)
    assert distal.meta["t"] > proximal.meta["t"]


def test_selecting_on_an_unmodelled_key_finds_nothing():
    cell = Pyramidal(spines=6)
    with pytest.raises(LookupError):
        cell.anchor("spine", nonsense=1)


def test_anchor_normals_are_unit_length():
    cell = Pyramidal(spines=8, basal=2, basal_spines=5)
    for a in cell.anchors():
        assert np.isclose(np.linalg.norm(a.normal), 1.0)


def test_soma_anchors_point_away_from_the_midline():
    cell = Pyramidal(spines=6)
    for a in cell.anchors("soma"):
        assert a.normal[0] * a.meta["side"] > 0


def test_shaft_anchors_sit_below_the_first_spine():
    """A shaft contact arriving beside a spine head reads as a spine contact,
    which is the wrong claim — so the bare shaft must stay bare."""
    cell = Pyramidal(spines=8)
    first_spine_t = min(a.meta["t"] for a in cell.anchors("spine",
                                                          branch="apical"))
    assert max(a.meta["t"] for a in cell.anchors("shaft")) < first_spine_t


def test_offset_stands_off_along_the_normal():
    cell = Pyramidal(spines=6)
    a = cell.anchor("spine", branch="apical", rank=-1)
    out = a.offset(0.05)
    assert np.isclose(np.linalg.norm(out - a.xy), 0.05)
    np.testing.assert_allclose(out, a.xy + a.normal * 0.05)


def test_nearest_prefers_an_anchor_facing_the_source():
    cell = Pyramidal(spines=8, basal=2, basal_spines=3)
    far_left = (-8.0, 1.0)
    chosen = cell.anchors("spine").nearest(far_left)
    assert chosen.toward(far_left)


# -- drawing -----------------------------------------------------------------

def test_draw_and_fit():
    fig, ax = bd.canvas(figsize=(3, 4))
    cell = Pyramidal(spines=8, basal=2, basal_spines=5)
    artists = cell.draw(ax=ax, wall_lw=1.0, gid="cell")
    assert artists
    assert any(a.get_gid().startswith("cell.") for a in artists)
    x0, y0, x1, y1 = cell.fit(ax, pad=0.2)
    assert x1 > x0 and y1 > y0


def test_draw_accepts_an_explicit_hollow_fill():
    fig, ax = bd.canvas()
    Pyramidal(spines=4).draw(ax=ax, fill="white")
    assert ax.patches

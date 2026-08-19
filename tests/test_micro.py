"""The microbe domain: a body that is a tube rather than a ring.

Same principle as `test_cells.py` — these assert what must be *true*, not
what a cell looks like. What it looks like is the geometry pins' business.

The bias here is toward the bent and twisted cases. A straight rod exercises
almost none of the arithmetic that can actually go wrong, and both defects
found while building this shape were invisible on one.
"""

import numpy as np
import pytest
from matplotlib.path import Path

from biodraw.core.paths import tube
from biodraw.core.scatter import _distance_to
from biodraw.micro import Bacterium

# The named forms, as the docstring gives them. Parametrising on these means
# a change to how the axis is built fails on the form it broke.
FORMS = {
    "coccus": dict(length=0.0, width=0.62),
    "bacillus": dict(length=1.40),
    "vibrio": dict(length=1.40, curve_deg=72.0),
    "spirillum": dict(length=2.20, twists=1.8, twist_amp=0.62),
    "spirochaete": dict(length=2.60, width=0.20, twists=4.2, twist_amp=1.60),
}


# -- the capsule primitive ---------------------------------------------------


def test_a_capsule_is_closed_at_both_ends():
    """`cap_base` is the whole of what a free-floating body needed from
    `tube`: a flat chord reads as a sectioned specimen."""
    line = np.column_stack([np.linspace(-0.5, 0.5, 60), np.zeros(60)])
    ring = tube(line, 0.2, cap_base=True)
    # Both caps present, so the body reaches half a width past each end.
    assert np.isclose(ring[:, 0].max(), 0.7, atol=1e-3)
    assert np.isclose(ring[:, 0].min(), -0.7, atol=1e-3)
    # ...and it is a single walk with no jump, which is what a cap swept the
    # wrong way round would leave behind.
    step = np.linalg.norm(np.diff(np.vstack([ring, ring[:1]]), axis=0), axis=1)
    assert step.max() < 0.05
    assert Path(ring, closed=True).contains_point((-0.6, 0.0))


def test_open_end_and_cap_base_are_refused_together():
    """They say opposite things about the near end, and silently honouring
    one would draw a cell that is not the cell that was asked for."""
    line = np.column_stack([np.linspace(0, 1, 20), np.zeros(20)])
    with pytest.raises(ValueError, match="opposite"):
        tube(line, 0.1, open_end=True, cap_base=True)


# -- the body ----------------------------------------------------------------


@pytest.mark.parametrize("form", sorted(FORMS))
def test_every_named_form_is_one_closed_body(form):
    cell = Bacterium(seed=3, **FORMS[form])
    closed, open_ = cell.parts
    assert len(closed) == 1 and not open_
    assert len(np.asarray(closed[0])) > 100


def test_a_coccus_is_the_degenerate_rod_and_is_round():
    """`length=0` is a real setting, not a division by zero. A capsule of no
    length is a circle, which is why there is no separate round shape."""
    cell = Bacterium(length=0.0, width=0.62)
    ring = np.asarray(cell.geometry["outline"])
    assert np.isfinite(ring).all()
    r = np.linalg.norm(ring - ring.mean(axis=0), axis=1)
    assert np.isclose(r.min(), r.max(), rtol=2e-3)
    assert np.isclose(r.mean(), 0.31, atol=1e-3)


def test_bending_does_not_also_stretch():
    """The axis is an arc of the same arclength, so `curve_deg` changes the
    shape of the cell and not how much cell there is."""
    straight = Bacterium(length=1.6, curve_deg=0.0)
    bent = Bacterium(length=1.6, curve_deg=80.0)
    for cell in (straight, bent):
        c = cell.geometry["centre"]
        arc = np.linalg.norm(np.diff(c, axis=0), axis=1).sum()
        assert np.isclose(arc, 1.6, rtol=1e-3)


# -- what is inside it -------------------------------------------------------


@pytest.mark.parametrize("form", sorted(FORMS))
def test_the_nucleoid_stays_inside_the_wall(form):
    """The bug this shape shipped with, for one session's worth of drafts.

    The nucleoid was built by scaling the centreline toward its own centroid,
    which walks off the arc on any cell that is not straight — 26 points
    outside the wall on a cell bent 30 degrees with a twist in it. Trimming
    along the axis instead keeps it on whatever curve the body has, so this
    must hold for every form and not merely for a rod.
    """
    kw = dict(FORMS[form])
    cell = Bacterium(seed=3, nucleoid=0.66, **kw)
    body = Path(np.asarray(cell.geometry["outline"]), closed=True)
    nucleoid = np.asarray(cell.geometry["nucleoid"])
    outside = int((~body.contains_points(nucleoid)).sum())
    assert outside == 0, f"{outside}/{len(nucleoid)} nucleoid points escaped"


def test_the_cell_sits_inside_its_own_capsule():
    """A slime layer is an offset of the wall, not a scaled copy — a scaled
    copy sits closer at the poles than along the sides."""
    cell = Bacterium(length=1.4, curve_deg=40.0, capsule=0.18)
    capsule = Path(np.asarray(cell.geometry["capsule"]), closed=True)
    assert capsule.contains_points(cell.geometry["outline"]).all()


def test_granules_stay_inside_the_wall():
    cell = Bacterium(length=1.6, curve_deg=30.0, granules=4, seed=2)
    body = Path(np.asarray(cell.geometry["outline"]), closed=True)
    for g in cell.geometry["granules"]:
        assert body.contains_points(g["outline"]).all()


def test_the_layers_are_the_ones_that_must_occlude():
    """A nucleoid unioned with the cell is a nucleoid you cannot see, and a
    capsule unioned with it is just a fatter cell."""
    cell = Bacterium(capsule=0.16, nucleoid=0.6, granules=3, seed=1)
    assert [la.name for la in cell.layers] == [
        "capsule", "cell", "nucleoid", "granules"]
    plain = Bacterium()
    assert [la.name for la in plain.layers] == [None]


# -- what is hung off it -----------------------------------------------------


def test_appendages_are_rooted_inside_the_wall_and_reach_outside_it():
    cell = Bacterium(length=1.4, flagella=6, flagella_arc_deg=360.0, pili=12,
                     seed=4)
    body = Path(np.asarray(cell.geometry["outline"]), closed=True)
    items = cell.geometry["flagella"] + cell.geometry["pili"]
    assert len(items) == 18
    for a in items:
        assert body.contains_point(a["branch"].origin)
        assert not body.contains_point(a["branch"].centre[-1])


def test_flagella_are_equally_wavy_per_unit_of_themselves():
    """`jitter` varies their lengths, so a shared cycle *count* would make
    the short ones wiggle faster. Third time this library has had to say it:
    see `Branch`, `Pyramidal.WAVE_PER` and `Blob`."""
    cell = Bacterium(length=1.4, flagella=7, flagella_arc_deg=360.0, seed=6)
    brs = [a["branch"] for a in cell.geometry["flagella"]]
    assert np.std([b.length for b in brs]) > 1e-6       # lengths do vary
    rate = np.array([b.wave_n / b.length for b in brs])
    assert rate.max() / rate.min() < 1.01


def test_a_run_of_appendages_does_not_repeat_exactly():
    cell = Bacterium(length=1.4, flagella=8, flagella_arc_deg=360.0, seed=1)
    items = cell.geometry["flagella"]
    degs = sorted(a["deg"] for a in items)
    assert np.std([a["branch"].length for a in items]) > 1e-6
    assert np.std(np.diff(degs)) > 1e-6
    assert degs[-1] - degs[0] < 360.0                   # and does not wrap


def test_one_appendage_is_not_jittered_off_its_own_pole():
    """A single flagellum has nothing to be irregular against, and knocking
    it off the pole would just be a mono-flagellate cell aimed wrongly."""
    cell = Bacterium(length=1.4, flagella=1, flagella_arc_deg=0.0, seed=9)
    assert cell.geometry["flagella"][0]["deg"] == 0.0


# -- anchors -----------------------------------------------------------------


@pytest.mark.parametrize("form", sorted(FORMS))
def test_anchors_point_outward_and_sit_on_the_drawn_wall(form):
    """Both halves of check 5. Measured to the nearest *edge*: on a wall of
    364 vertices, a nearest-vertex measure hides an error of half the sample
    spacing, which is how the same class of bug survived in `Blob`."""
    cell = Bacterium(seed=3, **FORMS[form])
    mid = cell.geometry["centre"].mean(axis=0)
    for a in list(cell.anchors("wall")) + list(cell.anchors("pole")):
        assert np.isclose(np.linalg.norm(a.normal), 1.0)
        assert np.dot(a.normal, a.xy - mid) > 0
    gaps = _distance_to(cell.anchors("wall").points(),
                        np.asarray(cell.geometry["outline"]))
    assert gaps.max() < 1e-9


def test_the_two_poles_face_opposite_ways_on_a_straight_cell():
    cell = Bacterium(length=1.5)
    far = cell.anchor("pole", end="far")
    near = cell.anchor("pole", end="near")
    assert np.isclose(np.dot(far.normal, near.normal), -1.0, atol=1e-6)


def test_rotation_carries_the_anchors_round():
    upright = Bacterium(length=1.4, flagella=3, flagella_arc_deg=360.0)
    turned = Bacterium(length=1.4, flagella=3, flagella_arc_deg=360.0,
                       rotate_deg=90.0)
    for a, b in zip(upright.anchors("wall"), turned.anchors("wall"),
                    strict=True):
        np.testing.assert_allclose(b.normal, (-a.normal[1], a.normal[0]),
                                   atol=1e-9)


def test_the_same_seed_gives_the_same_cell():
    def flag(seed):
        return [a["deg"] for a in Bacterium(
            length=1.4, flagella=6, flagella_arc_deg=360.0,
            seed=seed).geometry["flagella"]]
    assert flag(3) == flag(3)
    assert flag(3) != flag(4)

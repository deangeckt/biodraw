"""The instrument. Invariants only — see the note in `test_pyramidal.py`.

What the microscope *looks* like is the pins' business. What must be true is
that it is a working instrument: the barrels clear the slide, they point at
the specimen, and the count you asked for is the count you get.
"""

import numpy as np
import pytest

import biodraw as bd
from biodraw.lab import Microscope


@pytest.mark.parametrize("inverted", [False, True])
def test_the_objectives_clear_the_stage(inverted):
    """The gap is the **working distance**, and it is the one thing about a
    microscope that has to be right. Drawn intersecting, the instrument has
    been driven down through its own slide — which is what the first version
    did, by 0.044, and no drawing test would have caught it."""
    scope = Microscope(inverted=inverted)
    layout = scope._layout()
    tips = [a.xy[1] for a in scope.anchors("objective")]
    gap = ((layout["stage_y"] - max(tips)) if inverted
           else (min(tips) - layout["stage_y"]))
    assert gap > 0.0, f"objectives are through the stage by {-gap:.3f}"


@pytest.mark.parametrize("inverted, sign", [(False, -1.0), (True, 1.0)])
def test_objectives_point_at_the_specimen(inverted, sign):
    """Down on an upright, up on an inverted. The first version re-derived
    this in `_named` instead of reading it from `_layout` and got it
    backwards: the anchors pointed *up* out of an upright, 0.14 above a
    turret whose barrels hung below it. Both halves were self-consistent,
    which is why only the numbers showed it."""
    scope = Microscope(inverted=inverted)
    for a in scope.anchors("objective"):
        assert np.sign(a.normal[1]) == sign
        # ...and the tip is on that side of the turret, not merely aimed.
        assert np.sign(a.xy[1] - scope._layout()["turret"][1]) == sign


@pytest.mark.parametrize("n", [0, 1, 2, 3, 5])
def test_you_get_the_objectives_you_asked_for(n):
    """The knob the shape exists for."""
    scope = Microscope(objectives=n)
    assert len(scope.anchors("objective")) == n
    assert scope.parts[0]  # a turret is still drawn with none on it


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_one_objective_sits_on_the_optical_axis(n):
    """A turret is *indexed*: the objective in use is the one on the axis.
    A fan straddling it would say none is engaged. Even counts therefore come
    out lopsided, deliberately — see `_fan`."""
    degs = Microscope(objectives=n)._fan()
    assert min(abs(d) for d in degs) == pytest.approx(0.0)


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6])
def test_adjacent_objectives_stay_apart_at_every_count(n):
    """The knob the shape exists for has to keep working at the settings it
    exists to show. Held as a fixed total spread, the angular step shrank as
    barrels were added and at n=5 the tips fused into a lump nobody could
    count — drawing rule 3 (*a count over a length is a density*) one axis
    over. As a step, the separation is the same at every count."""
    tips = np.array([a.xy for a in Microscope(objectives=n).anchors(
        "objective")])
    sep = np.linalg.norm(np.diff(tips, axis=0), axis=1).min()
    assert sep > 0.032, f"tips {sep:.3f} apart, barrels are 0.032 wide"


def test_inverted_is_a_different_instrument_not_a_flipped_one():
    """If it were a flip, one shape would do and `inverted` would be a
    rendering flag. The stage sits above the turret on an inverted and below
    it on an upright, and the eyepiece leaves from a different height."""
    up, inv = Microscope()._layout(), Microscope(inverted=True)._layout()
    assert up["stage_y"] < up["turret"][1]
    assert inv["stage_y"] > inv["turret"][1]
    assert inv["eye"][1] < up["eye"][1]


def test_every_anchor_normal_points_out_of_the_instrument():
    """Check 5 of `review-a-drawing`, on a shape whose parts span two
    layers — which is where the animals found their inward-pointing bug."""
    scope = Microscope()
    pts = np.concatenate(scope.points)
    centre = pts.mean(axis=0)
    for a in scope.anchors("wall"):
        assert np.dot(a.xy - centre, a.normal) > 0.0, a


def test_the_knob_is_a_marking_and_stays_inside_the_body():
    """A control drawn at the body's own wall weight stops being a control.
    It is a separate layer at 0.8x, and it must sit *on* the instrument."""
    scope = Microscope()
    body, knob = scope._layers()
    assert knob.wall_lw == "0.8x"
    ring = np.asarray(knob.closed[0])
    hull = np.vstack([np.asarray(p) for p in body.closed])
    assert ring[:, 0].min() > hull[:, 0].min()
    assert ring[:, 0].max() < hull[:, 0].max()
    assert ring[:, 1].min() > hull[:, 1].min()


def test_it_draws_and_fits_like_any_other_shape():
    fig, ax = bd.canvas()
    scope = Microscope(camera=True)
    scope.draw(ax=ax)
    box = bd.fit(ax, scope.points, pad=0.1)
    assert box[2] > box[0] and box[3] > box[1]

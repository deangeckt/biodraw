"""The radial cell's named forms.

Deliberately few, and none of them pin a number that merely *is*: the geometry
digests in `test_pins.py` already do that. What is tested here is what has to
stay true for these to be different cells at all — because the whole claim of
`neuro/types.py` is that five recognisable neurons are one shape at five
settings, and that claim breaks silently.
"""

import numpy as np
import pytest

import biodraw as bd
from biodraw.neuro import Astrocyte, Basket, Bipolar, Granule, Purkinje
from biodraw.neuro.radial import RadialCell

FORMS = [Basket, Bipolar, Granule, Purkinje, Astrocyte]


@pytest.mark.parametrize("form", FORMS)
def test_every_form_is_the_one_shape(form):
    assert issubclass(form, RadialCell)


@pytest.mark.parametrize("form", FORMS)
def test_every_form_draws_finite_geometry(form):
    cell = form()
    parts = cell.points
    assert parts
    for p in parts:
        assert np.isfinite(p).all()


@pytest.mark.parametrize("form", FORMS)
def test_every_form_exposes_the_anchor_kinds_connectors_need(form):
    kinds = {a.kind for a in form().anchors()}
    assert {"soma", "tip"} <= kinds


def test_bipolar_processes_are_opposed():
    """Two processes 180 degrees apart is the whole silhouette — if they
    drift together the cell stops being bipolar and becomes a stub."""
    tips = Bipolar().anchors("tip").points()
    assert len(tips) >= 2
    span = tips.max(axis=0) - tips.min(axis=0)
    # Far longer than it is wide, along the soma's own axis.
    assert span[1] > 2.5 * span[0]


def test_purkinje_is_a_fan_not_a_star():
    """Everything leaves upward into a wedge. A Purkinje cell that radiates
    in every direction is a stellate cell with extra branches."""
    cell = Purkinje()
    tips = cell.anchors("tip").points()
    assert (tips[:, 1] > cell.at[1]).all()


def test_astrocyte_has_no_long_axis():
    """A bush, not a fan: no direction dominates."""
    cell = Astrocyte()
    tips = cell.anchors("tip").points() - cell.at
    span = tips.max(axis=0) - tips.min(axis=0)
    assert 0.6 < span[0] / span[1] < 1.7


def test_branching_depth_multiplies_branches():
    """`depth` is the knob that separates a smooth dendrite from a fan."""
    counts = [len(RadialCell(dendrites=2, forks=0.5, depth=d)._branches())
              for d in (1, 2, 3)]
    assert counts == [2 * 3, 2 * 7, 2 * 15]


def test_depth_without_forks_does_nothing():
    """Depth is meaningless if nothing forks, and must not raise."""
    assert len(RadialCell(dendrites=3, forks=None, depth=4)._branches()) == 3


def test_forms_are_deterministic():
    for form in FORMS:
        a, b = form(), form()
        for pa, pb in zip(a.points, b.points, strict=True):
            np.testing.assert_array_equal(pa, pb)


def test_forms_draw(tmp_path):
    fig, ax = bd.canvas()
    for form in FORMS:
        form().draw(ax=ax, wall_lw=0.8)
    assert ax.patches

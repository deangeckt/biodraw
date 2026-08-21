"""Connectors, contact placement, and the two neuro shapes built on them.

Invariants only — see the note at the top of `test_pyramidal.py`. What a
connector *looks* like is the pins' business; what must hold is that it starts
and stops where the anchors say it should.
"""

import numpy as np
import pytest

import biodraw as bd
from biodraw.neuro import Basket, Pyramidal

# -- connectors --------------------------------------------------------------

def test_a_connector_stops_short_of_its_target_by_the_gap():
    """The whole point of an anchor: a clearance means the same thing at any
    angle, so it does not have to be tuned per contact per figure."""
    fig, ax = bd.canvas()
    cell = Pyramidal(spines=8)
    target = cell.anchor("spine", branch="apical", rank=-1)
    artists = bd.connect(ax=ax, source=(-4.0, 0.0), target=target, gap=0.25,
                         endcap=None)
    end = artists[0].get_path().vertices[-1]
    assert np.isclose(np.linalg.norm(end - target.xy), 0.25, atol=1e-9)
    # ...and it stops on the *outward* side, not inside the cell.
    assert target.toward(end)


def test_every_endcap_draws_something_and_an_unknown_one_raises():
    fig, ax = bd.canvas()
    for kind in bd.core.connectors.ENDCAPS:
        got = bd.endcap(ax=ax, xy=(0.0, 0.0), normal=(1.0, 0.0), kind=kind)
        assert (got == []) if kind is None else got
    with pytest.raises(ValueError, match="unknown endcap"):
        bd.endcap(ax=ax, xy=(0, 0), kind="squiggle")


def test_a_tree_draws_one_stem_and_one_branch_per_target():
    fig, ax = bd.canvas()
    targets = [(-2.0, -2.0), (0.5, -2.5), (2.5, -1.5)]
    got = bd.connect_tree(ax=ax, source=(0.0, 1.0), targets=targets,
                          endcap=None)
    assert len(got) == 1 + len(targets)


# -- Basket ------------------------------------------------------------------

def test_basket_is_one_unbroken_contour():
    """Soma and dendrites must fuse, so they belong in one render group."""
    cell = Basket(dendrites=6, forks=None)
    assert len(cell.layers) == 1
    assert all(np.isfinite(np.asarray(p)).all() for p in cell.points)


def test_basket_dendrites_are_rooted_inside_the_soma():
    from matplotlib.path import Path
    cell = Basket(dendrites=7)
    soma = Path(cell.geometry["soma"], closed=True)
    for d in cell.geometry["dendrites"]:
        assert soma.contains_point(d["branch"].origin)


def test_basket_soma_anchors_point_outward():
    cell = Basket()
    for a in cell.anchors("soma"):
        assert np.dot(a.normal, a.xy - cell.at) > 0
        assert np.isclose(np.linalg.norm(a.normal), 1.0)


def test_basket_dendrites_differ():
    """The same rule as the pyramidal fork, applied to a run rather than a
    pair — see docs/RULES.md."""
    cell = Basket(dendrites=8, jitter=0.22, forks=None, seed=2)
    degs = [d["deg"] for d in cell.geometry["dendrites"]]
    lens = [d["branch"].length for d in cell.geometry["dendrites"]]
    assert np.std(np.diff(degs)) > 1e-6
    assert np.std(lens) > 1e-6
    assert (np.diff(degs) > 0).all()          # still in order round the soma


def test_basket_jitter_off_gives_the_even_ring():
    cell = Basket(dendrites=8, jitter=0.0, length_ratio=1.0, forks=None)
    degs = [d["deg"] for d in cell.geometry["dendrites"]]
    assert np.allclose(np.diff(degs), 45.0)


def test_a_forked_basket_dendrite_is_capped_and_buries_its_daughters():
    """Same mechanism as the pyramidal fork, and the same failure if it is
    missing — see `paths.buried_base`."""
    from matplotlib.path import Path
    cell = Basket(dendrites=5, forks=0.55, seed=2)
    closed, open_ = cell.parts
    parents = [Path(np.asarray(p), closed=True) for p in closed[:-1]]
    for k, child in enumerate(open_):
        v = np.asarray(child)
        m = len(v) // 2
        chord = v[m - 1] + np.linspace(0, 1, 30)[:, None] * (v[m] - v[m - 1])
        assert any(p.contains_points(chord).all() for p in parents), \
            f"daughter {k} has its base chord showing"

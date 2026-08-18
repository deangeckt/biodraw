"""The branch: its curve, its decorations, and its tube."""

import numpy as np
import pytest

from biodraw.core import profile
from biodraw.core.branch import Branch


def _branch(**kw):
    return Branch((0.0, 0.0), (0.0, 1.0), length=1.8, **kw)


def test_centreline_starts_at_the_origin_and_runs_its_length():
    br = _branch(bend=0.0, wave_amp=0.0)
    np.testing.assert_allclose(br.centre[0], (0.0, 0.0), atol=1e-12)
    assert np.isclose(br.centre[-1][1], 1.8)


def test_the_waver_vanishes_at_the_base():
    """An offset at t=0 would plant the branch off-centre on whatever it grows
    out of, whatever the phase."""
    for phase in (0.0, 0.35, 0.5, 0.9):
        br = _branch(bend=0.0, wave_amp=0.2, wave_phase=phase)
        assert np.isclose(br.across(0.0), 0.0, atol=1e-12)


def test_across_is_lean_plus_waver():
    br = _branch()
    t = np.linspace(0, 1, 17)
    np.testing.assert_allclose(br.across(t), br.lean(t) + br.waver(t))


def test_bend_sign_picks_the_side():
    left = _branch(bend=0.2, wave_amp=0.0)
    right = _branch(bend=-0.2, wave_amp=0.0)
    np.testing.assert_allclose(left.centre[:, 0], -right.centre[:, 0],
                               atol=1e-12)


def test_at_agrees_with_the_sampled_centreline():
    """The analytic `at` and the sampled `centre` must be the same curve."""
    br = _branch()
    for k in (0, 30, 60, br.n_pts - 1):
        xy, tangent = br.at(br.t_grid[k])
        np.testing.assert_allclose(xy, br.centre[k], atol=1e-12)
        assert np.isclose(np.linalg.norm(tangent), 1.0)


def test_decorations_alternate_sides():
    br = _branch()
    d = br.decorate("spine", n=8, size=0.21)
    sides = [x["side"] for x in d]
    assert sides == [(-1) ** k for k in range(8)] or \
           sides == [-((-1) ** k) for k in range(8)]
    assert all(s * n < 0
               for s, n in zip(sides[:-1], sides[1:], strict=True))


def test_decorations_stay_inside_the_parameter_range():
    br = _branch()
    d = br.decorate("spine", n=6, size=0.2, first_t=0.30, last_t=0.86)
    assert np.isclose(d[0]["t"], 0.30)
    assert np.isclose(d[-1]["t"], 0.86)


def test_decorate_with_zero_leaves_a_bare_branch():
    br = _branch()
    assert br.decorate("spine", n=0, size=0.2) == []
    assert br.head_r == 0.0


def test_head_is_the_aim_point_not_the_tip():
    br = _branch()
    sp = profile.get("spine")
    d = br.decorate("spine", n=3, size=0.3)[0]
    reach = np.linalg.norm(d["head"] - d["base"])
    assert np.isclose(reach, 0.3 * sp.head_t)


def test_head_r_ignores_the_neck_extension():
    """`extend` carries the head out rigidly without resizing it, so the radius
    that clears the head must not grow with it."""
    plain = _branch().decorate("spine", n=3, size=0.21, extend=0.0)
    stretched = _branch().decorate("spine", n=3, size=0.21, extend=0.04)
    a, b = Branch((0, 0), (0, 1), 1.8), Branch((0, 0), (0, 1), 1.8)
    a.decorations, b.decorations = plain, stretched
    assert np.isclose(a.head_r, b.head_r)


def test_extend_pushes_the_head_further_off_the_branch():
    br_a, br_b = _branch(), _branch()
    a = br_a.decorate("spine", n=3, size=0.21, extend=0.0)[0]
    b = br_b.decorate("spine", n=3, size=0.21, extend=0.04)[0]
    assert np.isclose(np.linalg.norm(b["head"] - b["base"])
                      - np.linalg.norm(a["head"] - a["base"]), 0.04)


def test_decoration_outlines_are_finite_and_closed_ish():
    br = _branch()
    for d in br.decorate("spine", n=8, size=0.21, extend=0.04):
        assert np.isfinite(d["outline"]).all()
        assert len(d["outline"]) > 10


def test_parts_splits_closed_decorations_from_the_open_tube():
    br = _branch()
    br.decorate("spine", n=5, size=0.21)
    closed, open_ = br.parts(width=0.11, taper=0.72, base_ext=0.05)
    assert len(closed) == 5
    assert len(open_) == 1
    assert np.isfinite(open_[0]).all()


def test_normal_at_is_perpendicular_to_the_tangent():
    br = _branch()
    for t in (0.1, 0.5, 0.9):
        _, tangent = br.at(t)
        for side in (-1, 1):
            n = br.normal_at(t, side)
            assert np.isclose(n @ tangent, 0.0, atol=1e-12)
            assert np.isclose(np.linalg.norm(n), 1.0)


def test_child_starts_on_the_parent():
    parent = _branch()
    kid = parent.child(at_t=0.6, angle_deg=-30, length=0.8)
    np.testing.assert_allclose(kid.origin, parent.at(0.6)[0], atol=1e-12)


def test_child_angle_is_measured_off_the_axis_by_default():
    """The default must be the branch's nominal direction, not the local
    tangent — see `Branch.child` for why."""
    parent = _branch()
    kid = parent.child(at_t=1.0, angle_deg=-35, length=0.8)
    from biodraw.core.geom import rot
    np.testing.assert_allclose(kid.direction, rot(parent.direction, -35),
                               atol=1e-12)


def test_a_fork_is_symmetric_about_the_parent_axis():
    """The bug this guards: on a short branch the waver's derivative swings
    the tip tangent tens of degrees, and a fork keyed to it comes out with
    both daughters swung the same way."""
    parent = Branch((0, 0), (0, 1), length=0.88, bend=0.10, wave_amp=0.055,
                    wave_n=1.6)
    left = parent.child(at_t=1.0, angle_deg=+35, length=1.2)
    right = parent.child(at_t=1.0, angle_deg=-35, length=1.2)
    # Mirror images about the parent's own axis.
    assert np.isclose(left.direction[0], -right.direction[0], atol=1e-12)
    assert np.isclose(left.direction[1], right.direction[1], atol=1e-12)
    # ...and the tangent basis really would have been lopsided.
    _, tang = parent.at(1.0)
    assert abs(np.degrees(np.arctan2(tang[0], tang[1]))) > 20.0


def test_child_relative_to_tangent_is_still_available():
    parent = _branch()
    kid = parent.child(at_t=0.5, angle_deg=0.0, length=0.5,
                       relative_to="tangent")
    np.testing.assert_allclose(kid.direction, parent.at(0.5)[1], atol=1e-12)


def test_child_rejects_an_unknown_basis():
    with pytest.raises(ValueError, match="relative_to"):
        _branch().child(at_t=0.5, angle_deg=0.0, length=0.5,
                        relative_to="nonsense")


def test_child_inherits_the_parents_hand():
    parent = _branch(bend=0.17, wave_n=2.3)
    kid = parent.child(at_t=0.5, angle_deg=-20, length=0.8)
    assert kid.bend == 0.17
    assert kid.wave_n == 2.3
    assert parent.child(at_t=0.5, angle_deg=-20, length=0.8,
                        bend=0.0).bend == 0.0


def test_branch_is_deterministic():
    """No hidden randomness: same knobs, same curve, every time."""
    a, b = _branch(), _branch()
    np.testing.assert_array_equal(a.centre, b.centre)

"""Profiles: the canonical frame, placement, and the neck stretch."""

import numpy as np
import pytest

from biodraw.core import profile
from biodraw.core.profile import Profile


def test_bundled_spine_is_registered():
    assert "spine" in profile.available()
    assert profile.get("spine") is profile.get(profile.get("spine"))


def test_get_reports_unknown_names():
    with pytest.raises(KeyError, match="unknown profile"):
        profile.get("no-such-shape")


def test_spine_is_in_the_canonical_frame():
    sp = profile.get("spine")
    assert np.isclose(sp.points[:, 0].min(), 0.0)
    assert np.isclose(sp.points[:, 0].max(), 1.0)
    assert np.isclose(sp.length, 1.0)


def test_spine_has_a_neck_narrower_than_its_head():
    """The feature that makes it read as a spine rather than a cone."""
    sp = profile.get("spine")
    x, y = sp.points[:, 0], np.abs(sp.points[:, 1])
    neck = y[x < 0.30].max()
    head = y[(x > 0.75) & (x < 0.90)].max()
    assert head > 2.0 * neck


def test_place_lands_on_the_base_and_points_down_direction():
    sp = profile.get("spine")
    out = sp.place((1.0, 2.0), (0.0, 1.0), size=0.2, sink=0.0)
    # The base chord's midpoint is the origin of the canonical frame.
    assert np.allclose(out[[0, -1]].mean(axis=0), (1.0, 2.0), atol=1e-12)
    # The tip is `size` further along the direction.
    assert out[:, 1].max() > 2.0


def test_place_rotates_rigidly():
    sp = profile.get("spine")
    a = sp.place((0, 0), (1, 0), size=0.3)
    b = sp.place((0, 0), (0, 1), size=0.3)
    # Same shape, turned 90 degrees: the extents swap.
    assert np.isclose(np.ptp(a[:, 0]), np.ptp(b[:, 1]))
    assert np.isclose(np.ptp(a[:, 1]), np.ptp(b[:, 0]))


def test_mirror_flips_across_the_axis():
    sp = profile.get("spine")
    a = sp.place((0, 0), (1, 0), size=0.3, mirror=False)
    b = sp.place((0, 0), (1, 0), size=0.3, mirror=True)
    np.testing.assert_allclose(a[:, 0], b[:, 0])
    np.testing.assert_allclose(a[:, 1], -b[:, 1])


def test_extend_lengthens_the_neck_without_inflating_the_head():
    """The whole reason `stretch` exists.

    Scaling a spine up makes its head grow too, and on a densely spined branch
    the heads start touching. Extending must add length and nothing else.
    """
    sp = profile.get("spine")
    a = sp.place((0, 0), (1, 0), size=0.21, extend=0.0)
    b = sp.place((0, 0), (1, 0), size=0.21, extend=0.04)
    assert np.isclose(np.ptp(b[:, 0]) - np.ptp(a[:, 0]), 0.04)
    assert np.isclose(np.ptp(b[:, 1]), np.ptp(a[:, 1]))     # unchanged width


def test_head_and_neck_scale_their_own_half_of_the_shape():
    """Thin, stubby and mushroom spines are this pair, not three profiles.

    Each multiplier must move *its* end and leave the other one where it was,
    or the two knobs are one knob with a fancy name.
    """
    sp = profile.get("spine")

    def widths(**kw):
        out = sp.place((0, 0), (1, 0), size=1.0, sink=0.0, **kw)
        x, y = out[:, 0], np.abs(out[:, 1])
        return y[x < 0.30].max(), y[(x > 0.75) & (x < 0.90)].max()

    neck, head = widths()
    fat_neck, unchanged_head = widths(head=2.0)
    assert np.isclose(unchanged_head, 2.0 * head)
    assert np.isclose(fat_neck, neck)                  # the neck stayed put

    thin_neck, still_head = widths(neck=0.5)
    assert np.isclose(thin_neck, 0.5 * neck)
    assert np.isclose(still_head, head)


def test_head_and_neck_change_no_length():
    """Width only — so `head_offset`, what a connector aims at, still holds."""
    sp = profile.get("spine")
    a = sp.place((0, 0), (1, 0), size=0.21)
    b = sp.place((0, 0), (1, 0), size=0.21, head=1.6, neck=0.5)
    assert np.isclose(np.ptp(a[:, 0]), np.ptp(b[:, 0]))


def test_the_defaults_are_the_traced_shape():
    sp = profile.get("spine")
    np.testing.assert_array_equal(sp.place((0, 0), (1, 0), size=0.3),
                                  sp.place((0, 0), (1, 0), size=0.3,
                                           head=1.0, neck=1.0))


def test_head_offset_tracks_extension_one_for_one():
    sp = profile.get("spine")
    assert np.isclose(sp.head_offset(0.21, 0.04) - sp.head_offset(0.21, 0.0),
                      0.04)


def test_extend_is_ignored_without_a_stretch_span():
    plain = Profile(profile.get("spine").points, stretch=None)
    a = plain.place((0, 0), (1, 0), size=0.2, extend=0.0)
    b = plain.place((0, 0), (1, 0), size=0.2, extend=0.5)
    np.testing.assert_allclose(a, b)


def _messy(points, angle=31.0, scale=37.0, shift=(12.0, -4.0)):
    """A traced outline as it arrives: rotated, offset, arbitrary scale."""
    from biodraw.core.geom import rot_matrix
    return (points * scale) @ rot_matrix(angle).T + np.array(shift)


def test_normalize_recovers_the_canonical_frame():
    sp = profile.get("spine")
    got = Profile(_messy(sp.points), normalize=True)
    assert np.isclose(got.length, 1.0)
    assert np.isclose(got.points[:, 0].min(), 0.0)


@pytest.mark.parametrize("angle", [0.0, 31.0, 90.0, 150.0, -95.0])
def test_normalize_puts_a_wide_tip_at_the_far_end(angle):
    """A spine is attached by its narrow neck and ends in a wide head, so the
    wide end must come out as the tip whichever way the trace was drawn."""
    sp = profile.get("spine")
    got = Profile(_messy(sp.points, angle=angle), normalize=True, tip="wide")
    x, y = got.points[:, 0], np.abs(got.points[:, 1])
    assert y[x > 0.7].max() > y[x < 0.3].max()


def test_normalize_can_put_a_narrow_tip_at_the_far_end():
    """A thorn or a cilium is the other way round — hence an explicit knob
    rather than a heuristic that is right for half of all shapes."""
    sp = profile.get("spine")
    got = Profile(_messy(sp.points), normalize=True, tip="narrow")
    x, y = got.points[:, 0], np.abs(got.points[:, 1])
    assert y[x > 0.7].max() < y[x < 0.3].max()


def test_register_refuses_to_clobber_silently():
    sp = profile.get("spine")
    with pytest.raises(KeyError, match="already registered"):
        profile.register("spine", sp)
    profile.register("spine", sp, overwrite=True)     # explicit is fine


def test_describe_is_json_shaped():
    d = profile.get("spine").describe()
    assert d["name"] == "spine"
    assert d["n_points"] > 0
    assert d["source"]

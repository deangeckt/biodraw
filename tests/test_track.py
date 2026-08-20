"""The track: the layout algebra, and the anchors it exposes.

What must be true here is arithmetic — a cursor that advances by each glyph's
own width — plus the two anchor conventions the drawing depends on. The
glyphs' shapes are pinned rather than tested; see `tests/shapes.py`.
"""

import numpy as np
import pytest

import biodraw as bd
from biodraw.core.track import Glyph, Track


class Box(Glyph):
    """A test glyph: a plain box of the width it was asked for."""

    name = "box"

    def __init__(self, width=0.5, height=0.2, label=None):
        self.height = float(height)
        super().__init__(width=width, label=label)

    def outline(self, x0):
        h = 0.5 * self.height
        return [np.array([[x0, -h], [x0 + self.width, -h],
                          [x0 + self.width, h], [x0, h], [x0, -h]])], []


def _track(widths=(0.4, 0.9, 0.2), gap=0.1, **kw):
    return Track([Box(width=w, label=f"g{i}")
                  for i, w in enumerate(widths)], gap=gap, **kw)


def test_each_glyph_consumes_its_own_width():
    track = _track()
    for (x0, x1), glyph in zip(track.spans, track.glyphs, strict=True):
        assert np.isclose(x1 - x0, glyph.width)


def test_the_gap_between_neighbours_is_the_gap():
    track = _track(gap=0.17)
    gaps = [b[0] - a[1] for a, b in zip(track.spans, track.spans[1:],
                                        strict=False)]
    assert np.allclose(gaps, 0.17)


def test_length_is_widths_plus_gaps():
    widths, gap = (0.4, 0.9, 0.2), 0.1
    assert np.isclose(_track(widths, gap).length,
                      sum(widths) + gap * (len(widths) - 1))


def test_order_is_the_content():
    """A track is the one shape here where the order of the parts is data."""
    a, b = _track((0.4, 0.9)), _track((0.9, 0.4))
    assert not np.allclose([s[1] for s in a.spans], [s[1] for s in b.spans])


def test_an_empty_track_draws_nothing_and_does_not_raise():
    track = Track([])
    closed, open_ = track.parts
    assert closed == [] and open_ == []
    assert len(track.anchors()) == 0
    assert track.length == 0.0


def test_the_backbone_runs_past_both_ends():
    track = _track(lead=0.25)
    pts = np.concatenate(track.points)
    assert pts[:, 0].min() <= -0.25 + 1e-9
    assert pts[:, 0].max() >= track.length + 0.25 - 1e-9


def test_no_backbone_when_the_rail_is_none():
    """A domain map on a protein is a track with no line under it."""
    assert len(_track(rail=None).parts[0]) == len(_track().parts[0]) - 1


def test_ticks_share_a_baseline_and_labels_do_not():
    """The asymmetry the example depends on: a row of names below the track
    must line up, and a callout above must hug its own glyph."""
    track = Track([Box(width=0.4, height=0.2), Box(width=0.4, height=0.8)])
    ticks = [a.xy[1] for a in track.anchors("tick")]
    labels = [a.xy[1] for a in track.anchors("label")]
    assert np.isclose(ticks[0], ticks[1])
    assert not np.isclose(labels[0], labels[1])


def test_anchor_normals_point_away_from_the_track():
    track = _track()
    for a in track.anchors("label"):
        assert a.normal[1] > 0
    for a in track.anchors("tick"):
        assert a.normal[1] < 0
    for a in track.anchors():
        assert np.isclose(np.linalg.norm(a.normal), 1.0)


def test_labels_travel_with_the_shape():
    """Anchors come back in world units, so placing a track moves them."""
    here = _track()
    there = _track(at=(3.0, -1.0), scale=2.0)
    assert np.allclose(there.anchor("label", index=0).xy,
                       (3.0, -1.0) + 2.0 * here.anchor("label", index=0).xy)


def test_rotating_turns_the_anchors_too():
    turned = _track(rotate_deg=90.0)
    assert np.allclose(turned.anchor("label", index=0).normal, (-1.0, 0.0),
                       atol=1e-12)


def test_a_glyph_must_implement_its_outline():
    with pytest.raises(NotImplementedError):
        Glyph(width=1.0).outline(0.0)


def test_the_track_is_exported_at_the_top_level():
    assert bd.Track is Track

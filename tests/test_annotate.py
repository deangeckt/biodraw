"""Labels, scale bars, and the frame that has to contain them.

Invariants only — see the note at the top of `test_pyramidal.py`. What a
label *looks* like is not pinned; what must hold is that it stands off the
shape it names, grows away from it, and stays inside the axes.
"""

import numpy as np
import pytest

import biodraw as bd
from biodraw.core.anchor import Anchor

# -- label -------------------------------------------------------------------


def test_a_label_stands_off_its_anchor_by_the_gap():
    """The same contract connectors have: a clearance means one thing at any
    angle, so it never has to be tuned per label per figure."""
    fig, ax = bd.canvas()
    for deg in range(0, 360, 30):
        d = np.deg2rad(deg)
        a = Anchor((0.3, -0.2), (np.cos(d), np.sin(d)), "wall")
        text = bd.label(ax=ax, at=a, text="x", gap=0.25)[-1]
        assert np.isclose(
            np.linalg.norm(np.array(text.get_position()) - a.xy), 0.25)
        assert a.toward(text.get_position())


@pytest.mark.parametrize("normal, ha, va", [
    ((1.0, 0.0), "left", "center"),      # out to the right: text runs right
    ((-1.0, 0.0), "right", "center"),    # out to the left: text runs left
    ((0.0, 1.0), "center", "bottom"),    # straight up: centred above
    ((0.0, -1.0), "center", "top"),
    ((0.7, 0.7), "left", "bottom"),      # a corner takes both
    ((-0.7, -0.7), "right", "top"),
])
def test_alignment_follows_the_normal(normal, ha, va):
    """The half that gets reinvented by hand. Text must grow *away* from the
    shape, or a label to the left of a cell runs back across it."""
    fig, ax = bd.canvas()
    text = bd.label(ax=ax, at=Anchor((0, 0), normal, "wall"), text="x")[-1]
    assert (text.get_ha(), text.get_va()) == (ha, va)


def test_a_caller_can_still_override_the_alignment():
    fig, ax = bd.canvas()
    text = bd.label(ax=ax, at=Anchor((0, 0), (-1, 0), "wall"), text="x",
                    ha="center")[-1]
    assert text.get_ha() == "center"


def test_a_leader_runs_from_the_shape_to_the_text_and_no_further():
    """A leader that overshoots into the shape undoes the clearance the
    anchor exists to give."""
    fig, ax = bd.canvas()
    a = Anchor((0.0, 0.0), (0.0, 1.0), "wall")
    line, text = bd.label(ax=ax, at=a, text="x", gap=0.4, leader=True)
    ends = line.get_path().vertices
    assert np.allclose(ends[0], a.xy)
    assert np.allclose(ends[-1], text.get_position())


def test_label_without_a_leader_draws_only_text():
    fig, ax = bd.canvas()
    assert len(bd.label(ax=ax, at=Anchor((0, 0), (0, 1)), text="x")) == 1


def test_a_bare_point_is_refused_and_says_what_to_do_instead():
    """`label` exists for the normal. Given a position with no direction it
    would silently become `ax.text`, which is a second way to do one thing."""
    fig, ax = bd.canvas()
    with pytest.raises(TypeError, match="ax.text"):
        bd.label(ax=ax, at=(0.0, 0.0), text="x")


# -- scalebar ----------------------------------------------------------------


def test_the_bar_is_exactly_its_stated_length():
    """A scale bar is the only text on a figure making a claim about reality.
    `size / per_unit`, done once here rather than retyped per figure."""
    fig, ax = bd.canvas()
    bar, _ = bd.scalebar(ax=ax, at=(0.2, 0.5), size=10, per_unit=12.0)
    (x0, y0), (x1, y1) = bar.get_path().vertices
    assert np.isclose(x1 - x0, 10.0 / 12.0)
    assert np.isclose(y0, y1) and np.isclose(x0, 0.2)


def test_the_bar_has_butt_caps():
    """A projecting cap makes the bar longer than the length it claims — at
    `lw=2` on a bar an inch long, a 3% overstatement of every measurement a
    reader takes off the figure. This is correctness, not styling."""
    fig, ax = bd.canvas()
    bar, _ = bd.scalebar(ax=ax, at=(0, 0), size=1, per_unit=1)
    assert bar.get_solid_capstyle() == "butt"


def test_the_caption_is_centred_on_the_bar_and_takes_the_side():
    fig, ax = bd.canvas()
    for side, va in ((1, "bottom"), (-1, "top")):
        _, cap = bd.scalebar(ax=ax, at=(0.0, 0.0), size=10, per_unit=10.0,
                             units="µm", side=side, gap=0.05)
        assert cap.get_text() == "10 µm"
        assert np.isclose(cap.get_position()[0], 0.5)
        assert np.isclose(cap.get_position()[1], 0.05 * side)
        assert cap.get_va() == va


# -- fit ---------------------------------------------------------------------


def test_fit_keeps_every_mark_inside_the_axes():
    """Text is not ink, so `points` cannot see a label. Measured before this
    existed: at `pad=0.12` all three leader labels on a Blob were clipped."""
    cell = bd.cells.Blob(radius=0.55, organelles=5, seed=3)
    for pad in (0.08, 0.20):
        fig, ax = bd.canvas()
        cell.draw(ax=ax)
        marks = []
        for a in cell.anchors("organelle")[:2]:
            marks += bd.label(ax=ax, at=a, text="organelle", gap=0.52,
                              leader=True, fontsize=8)
        marks += bd.scalebar(ax=ax, at=(-0.6, -0.95), size=10, per_unit=12,
                             units="µm", side=-1, fontsize=8)
        bd.fit(ax, cell.points, pad=pad, marks=marks)

        fig.canvas.draw()
        inv = ax.transData.inverted()
        (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
        for m in marks:
            bb = m.get_window_extent().transformed(inv)
            assert bb.x0 >= x0 and bb.x1 <= x1, f"{m} out of frame at {pad}"
            assert bb.y0 >= y0 and bb.y1 <= y1, f"{m} out of frame at {pad}"


def test_fit_without_marks_is_unchanged():
    """Every committed image was fitted without this argument, so the
    no-marks path has to stay byte-for-byte the same call it always was."""
    cell = bd.cells.Blob(radius=0.55, seed=1)
    fig, ax = bd.canvas()
    cell.draw(ax=ax)
    assert bd.fit(ax, cell.points, pad=0.2) == bd.fit(ax, cell.points,
                                                      pad=0.2, marks=())

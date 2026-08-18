"""Path primitives: bodies, tubes and connectors."""

import numpy as np

from biodraw.core import geom, paths

# -- tubes ------------------------------------------------------------------

def _straight(n=50, length=2.0):
    return np.column_stack([np.linspace(0, length, n), np.zeros(n)])


def test_tube_width_matches_the_half_width_asked_for():
    line = _straight()
    ring = paths.tube(line, 0.1)
    # A capped tube around a straight line spans 2*hw across it.
    assert np.isclose(np.ptp(ring[:, 1]), 0.2)


def test_tube_taper_narrows_toward_the_tip():
    line = _straight()
    hw = np.linspace(0.1, 0.05, len(line))
    ring = paths.tube(line, hw, open_end=True)
    # Open end: vertices run tip -> base -> tip, so both walls are present.
    near_base = ring[np.abs(ring[:, 0]) < 0.1]
    near_tip = ring[ring[:, 0] > 1.9]
    assert np.ptp(near_base[:, 1]) > np.ptp(near_tip[:, 1])


def test_tube_base_ext_pushes_the_flat_base_backwards():
    line = _straight()
    plain = paths.tube(line, 0.1, base_ext=0.0)
    sunk = paths.tube(line, 0.1, base_ext=0.3)
    assert np.isclose(sunk[:, 0].min(), plain[:, 0].min() - 0.3)


def test_open_tube_has_no_cap():
    line = _straight()
    capped = paths.tube(line, 0.1, open_end=False)
    open_ = paths.tube(line, 0.1, open_end=True)
    # The cap adds vertices beyond the last centreline point.
    assert capped[:, 0].max() > open_[:, 0].max()
    assert np.isclose(open_[:, 0].max(), 2.0)


# -- bodies -----------------------------------------------------------------

def test_superellipse_interpolates_ellipse_to_rectangle():
    ellipse = paths.superellipse(1.0, 1.0, squareness=2.0)
    boxy = paths.superellipse(1.0, 1.0, squareness=12.0)
    # An ellipse of unit semi-axes is the unit circle: every point at r=1.
    np.testing.assert_allclose(np.linalg.norm(ellipse, axis=1), 1.0, atol=1e-9)
    # Squarer means more area for the same semi-axes.
    assert abs(geom.signed_area(boxy)) > abs(geom.signed_area(ellipse))


def test_superellipse_radius_agrees_with_the_ring():
    a, b, s = 0.42, 0.40, 3.4
    ring = paths.superellipse(a, b, s, n_pts=4000)
    for direction in [(1, 0), (0, 1), (1, 1), (-0.4, 0.9)]:
        r = paths.superellipse_radius(direction, a, b, s)
        u = geom.unit(direction)
        # The ring point most nearly along `u` should sit at that radius.
        k = np.argmax(ring @ u / np.linalg.norm(ring, axis=1))
        assert np.isclose(np.linalg.norm(ring[k]), r, rtol=2e-3)


def test_bowed_ring_bows_outward_for_positive_bow():
    square = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    flat = paths.bowed_ring(square, [0.0] * 4)
    out = paths.bowed_ring(square, [0.3] * 4)
    assert abs(geom.signed_area(out)) > abs(geom.signed_area(flat))


def test_bowed_ring_outward_is_winding_independent():
    """`bow`'s sign must not depend on how the caller listed the corners."""
    square = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    a = paths.bowed_ring(square, [0.3] * 4)
    b = paths.bowed_ring(square[::-1], [0.3] * 4)
    assert np.isclose(abs(geom.signed_area(a)), abs(geom.signed_area(b)))


def test_bowed_ring_leaves_the_corners_alone():
    square = np.array([(-1.0, -1), (1, -1), (1, 1), (-1, 1)])
    ring = paths.bowed_ring(square, [0.3] * 4)
    for corner in square:
        assert np.min(np.linalg.norm(ring - corner, axis=1)) < 1e-12


def test_rounded_polygon_is_closed():
    p = paths.rounded_polygon([(0, 0), (1, 0), (0.5, 1)], 0.1)
    assert np.allclose(p.vertices[0], p.vertices[-1])


def test_neck_polygon_tangent_points_are_symmetric():
    p, pts = paths.neck_polygon((0, 0.4), (-0.62, -0.6), (0.62, -0.6),
                                hw=0.055, neck_r=0.25, corner_r=0.05,
                                bow_bottom=-0.025, bow_side=0.0)
    assert np.isclose(pts["P_s_l"][0], -pts["P_s_r"][0])
    assert np.isclose(pts["P_s_l"][1], pts["P_s_r"][1])
    # The arcs must land exactly on the tube walls, or the neck shows a step.
    assert np.isclose(pts["P_t_l"][0], -0.055)
    assert np.isclose(pts["P_t_r"][0], 0.055)
    assert np.isfinite(p.vertices).all()


# -- connectors -------------------------------------------------------------

def test_elbow_ends_pointing_the_way_it_turned():
    poly, end, direction = paths.elbow((0, 0), (0, -1), run=2.0,
                                       turn_deg=90.0, radius=0.5)
    np.testing.assert_allclose(direction, (1.0, 0.0), atol=1e-9)
    np.testing.assert_allclose(poly[-1], end)
    assert np.isfinite(poly).all()


def test_elbow_with_zero_radius_is_a_hard_corner():
    poly, _, _ = paths.elbow((0, 0), (0, -1), run=2.0, turn_deg=90.0,
                             radius=0.0)
    assert len(poly) == 2


def test_arc_rad_flips_sign_with_direction():
    """One fixed `rad` must bow *up* whichever way the connector runs."""
    assert paths.arc_rad((0, 0), (1, 0), 0.2) == -0.2
    assert paths.arc_rad((0, 0), (-1, 0), 0.2) == 0.2


def test_cubic_connector_starts_at_the_foot_of_the_drop():
    a, b = np.array([0.0, 0.0]), np.array([3.0, -1.0])
    start, q1, _, end = paths.cubic_connector(a, b, drop=0.9, rad=-0.05,
                                              smooth=0.25)
    np.testing.assert_allclose(start, (0.0, -0.9))
    np.testing.assert_allclose(end, b)
    # The first control point carries straight on down, so the descent and the
    # run meet tangentially instead of at a corner.
    assert q1[0] == start[0]
    assert q1[1] < start[1]


def test_cubic_connector_without_a_drop_is_a_plain_arc():
    a, b = np.array([0.0, 0.0]), np.array([3.0, 0.0])
    start, _, _, end = paths.cubic_connector(a, b, drop=0.0, rad=0.2,
                                             smooth=0.25)
    np.testing.assert_allclose(start, a)
    np.testing.assert_allclose(end, b)


def test_bezier_split_lands_on_the_curve():
    cubic = paths.cubic_connector((0, 0), (3, -1), drop=0.9, rad=-0.05,
                                  smooth=0.25)
    piece, tangent = paths.bezier_split(cubic, 0.5)
    np.testing.assert_allclose(piece[0], cubic[0])
    assert np.isclose(np.linalg.norm(tangent), 1.0)


def test_bezier_split_falls_back_when_the_cubic_is_a_point():
    p = (1.0, 1.0)
    _, tangent = paths.bezier_split((p, p, p, p), 0.5)
    np.testing.assert_allclose(tangent, (0.0, -1.0))


def test_fork_tree_branches_all_reach_their_targets():
    targets = [(3.0, -1.0), (-3.0, 1.0), (6.0, -0.5)]
    stem, branches = paths.fork_tree((0, 0), targets, drop=0.95,
                                     rads=[-0.05] * 3, smooth=0.25,
                                     fork=0.5, spread=0.35)
    assert len(branches) == 3
    for target, br in zip(targets, branches, strict=True):
        np.testing.assert_allclose(br.vertices[-1], target)
    # Every branch must leave the same fork point.
    forks = [br.vertices[0] for br in branches]
    for f in forks[1:]:
        np.testing.assert_allclose(f, forks[0])
    np.testing.assert_allclose(stem.vertices[-1], forks[0])


def test_fork_tree_never_aims_above_the_foot_of_its_drop():
    """Targets straddling the source put their centroid level with it; a stem
    aimed there would climb back up through itself and hang a needle below the
    crotch."""
    stem, branches = paths.fork_tree((0, 0), [(3.0, 1.0), (-3.0, 1.0)],
                                     drop=1.0, rads=[0.0, 0.0], smooth=0.25,
                                     fork=0.5, spread=0.35)
    assert branches[0].vertices[0][1] <= -1.0 + 1e-9

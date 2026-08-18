"""Vector and polyline utilities."""

import numpy as np
import pytest

from biodraw.core import geom


def test_unit_normalises():
    assert np.isclose(np.linalg.norm(geom.unit((3.0, 4.0))), 1.0)
    np.testing.assert_allclose(geom.unit((3.0, 4.0)), (0.6, 0.8))


def test_unit_rejects_zero():
    with pytest.raises(ValueError):
        geom.unit((0.0, 0.0))


def test_rot_is_counter_clockwise():
    np.testing.assert_allclose(geom.rot((1.0, 0.0), 90.0), (0.0, 1.0),
                               atol=1e-12)
    np.testing.assert_allclose(geom.rot((1.0, 0.0), 180.0), (-1.0, 0.0),
                               atol=1e-12)


def test_perp_matches_rot_90():
    v = (0.3, -0.7)
    np.testing.assert_allclose(geom.perp(v), geom.rot(v, 90.0), atol=1e-12)


def test_rot_matrix_agrees_with_rot():
    v = np.array([0.4, 0.9])
    np.testing.assert_allclose(geom.rot_matrix(37.0) @ v, geom.rot(v, 37.0))


def test_normals_are_unit_and_left_of_tangent():
    t = np.linspace(0, 1, 50)
    line = np.column_stack([t, np.zeros_like(t)])     # runs +x
    n = geom.normals(line)
    np.testing.assert_allclose(np.linalg.norm(n, axis=1), 1.0)
    # 90 degrees CCW of +x is +y — the outward-normal convention.
    np.testing.assert_allclose(n[:, 1], 1.0, atol=1e-12)


def test_arclength_of_a_straight_line():
    line = np.column_stack([np.linspace(0, 2, 11), np.zeros(11)])
    assert np.isclose(geom.arclength(line)[-1], 2.0)
    np.testing.assert_allclose(geom.arclength(line, normalized=True)[-1], 1.0)


def test_resample_evens_out_spacing():
    # Deliberately bunched: dense near 0, sparse near 1.
    t = np.linspace(0, 1, 40) ** 3
    line = np.column_stack([t, np.zeros_like(t)])
    out = geom.resample(line, 25)
    steps = np.linalg.norm(np.diff(out, axis=0), axis=1)
    assert out.shape == (25, 2)
    assert steps.std() < 1e-9


def test_resample_handles_duplicate_points():
    pts = np.array([[0.0, 0.0], [0.0, 0.0], [1.0, 0.0], [1.0, 0.0]])
    out = geom.resample(pts, 10)
    assert np.isfinite(out).all()


def test_signed_area_sign_follows_winding():
    ccw = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    assert geom.signed_area(ccw) > 0
    assert geom.signed_area(ccw[::-1]) < 0


def test_close_ring_and_is_closed():
    ring = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
    assert not geom.is_closed(ring)
    assert geom.is_closed(geom.close_ring(ring))

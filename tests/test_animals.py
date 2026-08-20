"""Animal silhouettes: the mirror, the union, and the knobs.

The load-bearing test here is `test_every_animal_is_one_connected_piece`. A
silhouette is several bodies handed to `render_hollow` in one call, and if any
of them fails to touch the rest it does not read as a detached ear — it reads
as a second object in the figure, and nothing else in the suite would notice.
"""

import numpy as np
import pytest
from matplotlib.path import Path

import biodraw as bd
from biodraw.animals import Animal, Fly, Mouse, Worm, Zebrafish

EVERY = (Mouse, Fly, Zebrafish, Worm)


def _parts(animal):
    closed, open_ = animal.parts
    return [np.asarray(p) for p in [*closed, *open_]]


def _touches(a, b):
    """Whether two outlines overlap at all, tested both ways round."""
    return (Path(a, closed=True).contains_points(b).any()
            or Path(b, closed=True).contains_points(a).any())


@pytest.mark.parametrize("cls", EVERY)
def test_every_animal_is_one_connected_piece(cls):
    parts = _parts(cls())
    seen, stack = {0}, [0]
    while stack:
        i = stack.pop()
        for j in range(len(parts)):
            if j not in seen and _touches(parts[i], parts[j]):
                seen.add(j)
                stack.append(j)
    assert len(seen) == len(parts), (
        f"{cls.__name__}: {len(parts) - len(seen)} part(s) float free")


@pytest.mark.parametrize("cls", EVERY)
def test_facing_mirrors_and_does_not_rotate(cls):
    """A rotated animal is an animal on its back, so `facing` is a mirror:
    x flips about the shape's own origin and y is untouched."""
    right, left = _parts(cls(facing=1)), _parts(cls(facing=-1))
    for a, b in zip(right, left, strict=True):
        np.testing.assert_allclose(a[:, 0], -b[:, 0], atol=1e-12)
        np.testing.assert_allclose(a[:, 1], b[:, 1], atol=1e-12)


@pytest.mark.parametrize("cls", EVERY)
def test_size_scales_the_whole_animal(cls):
    small, big = cls(size=1.0), cls(size=2.5)
    np.testing.assert_allclose(np.concatenate(_parts(big)),
                               2.5 * np.concatenate(_parts(small)),
                               atol=1e-12)


@pytest.mark.parametrize("cls", EVERY)
def test_wall_anchors_are_on_the_outer_rim(cls):
    animal = cls()
    pts = np.concatenate(_parts(animal))
    for a in animal.anchors("wall"):
        assert np.isclose(np.linalg.norm(a.normal), 1.0)
        assert np.max(pts @ a.normal) <= a.xy @ a.normal + 1e-9


@pytest.mark.parametrize("cls", EVERY)
def test_every_animal_names_at_least_one_place(cls):
    """A shape without anchors cannot be labelled or connected to, which is
    the one thing every figure using these will want."""
    named = [a for a in cls().anchors() if a.kind != "wall"]
    assert named
    for a in named:
        assert np.isclose(np.linalg.norm(a.normal), 1.0)


def test_a_named_anchor_turns_round_with_the_animal():
    right, left = Mouse(facing=1), Mouse(facing=-1)
    assert right.anchor("nose").normal[0] > 0
    assert left.anchor("nose").normal[0] < 0


def test_the_mouses_tail_is_a_length():
    """The knob the class exists for: a mouse with a stub reads as a vole."""
    spans = [np.ptp(np.concatenate(_parts(Mouse(tail=t)))[:, 0])
             for t in (0.25, 0.78, 1.30)]
    assert spans[0] < spans[1] < spans[2]


def test_stripes_are_trimmed_to_the_body():
    """Stripes are drawn as bars and cut to the outline by arithmetic, since
    the renderer unions and cannot intersect. A stripe that overhangs is a
    line lying across the fish."""
    fish = Zebrafish(stripes=5)
    body = Path(fish._body_ring(), closed=True)
    bars = fish._stripe_bars()
    assert len(bars) == 5
    for bar in bars:
        assert body.contains_points(bar).all()


def test_no_stripes_means_no_stripe_layer():
    assert [lay.name for lay in Zebrafish(stripes=0).layers] == ["body", "eye"]
    assert "stripes" in [lay.name for lay in Zebrafish().layers]


def test_wings_and_legs_can_be_taken_off():
    assert "wings" not in [lay.name for lay in Fly(wings=False).layers]
    assert len(Fly(legs=0).parts[0]) < len(Fly(legs=3).parts[0])


def test_the_worm_is_a_spindle():
    """Pointed at both ends, widest in the middle — the one animal here whose
    whole silhouette is a width profile rather than a set of bodies.

    Measured on a *straightened* worm, so "width" is just `|y|`: on the
    default curved one the two ends are at different heights and any measure
    taken across the whole outline reads that curve as thickness.
    """
    part = _parts(Worm(curl=0.0, waves=0.0))[0]
    x = part[:, 0]
    band = 0.1 * np.ptp(x)
    mid = np.abs(part[np.abs(x - x.mean()) < band, 1]).max()
    ends = np.abs(part[np.abs(x - x.mean()) > 0.48 * np.ptp(x), 1]).max()
    # 3.2x as drawn. Not sharper, because `tube` rounds its end caps: the
    # last tenth of the animal cannot come to less than the cap's own radius,
    # and forcing it to would put a needle on each end of the worm.
    assert mid > 2.5 * ends


def test_the_base_refuses_to_guess_at_a_shape():
    with pytest.raises(NotImplementedError):
        Animal()._forms()


def test_animals_are_exported_from_the_package():
    assert bd.animals.Mouse is Mouse

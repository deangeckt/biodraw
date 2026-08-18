"""Every shape's geometry, pinned.

This is the main regression net: if a refactor changes what a shape *is*, one
of these fails and says exactly which measurement moved. It is exact, tiny on
disk, and readable in a diff — see `tests/pins.py` for why it is digests
rather than images.
"""

import pytest

from . import pins, shapes

SHAPES = shapes.collect()


@pytest.mark.parametrize("name", sorted(SHAPES))
def test_shape_is_unchanged(name):
    stored = pins.load()
    if name not in stored:
        pytest.fail(
            f"{name} has no pin yet. Add it by running:\n"
            "    python tools/update_pins.py"
        )
    ok, message = pins.check(name, SHAPES[name], pins=stored)
    assert ok, message


def test_no_pin_is_orphaned():
    """A pin left behind after its shape was renamed or removed."""
    orphans = sorted(set(pins.load()) - set(SHAPES))
    assert not orphans, (
        f"pins with no shape: {orphans}\n"
        "    Remove them by running: python tools/update_pins.py"
    )


def test_digest_catches_a_moved_vertex():
    """The net has to actually catch things — check it does."""
    import numpy as np
    a = SHAPES["profile.spine.raw"].copy()
    b = a.copy()
    b[3, 1] += 1e-4
    assert pins.digest(a) != pins.digest(b)
    np.testing.assert_array_equal(a, SHAPES["profile.spine.raw"])


def test_digest_rejects_non_finite():
    import numpy as np
    bad = np.array([[0.0, 0.0], [np.nan, 1.0]])
    with pytest.raises(ValueError, match="NaN"):
        pins.digest(bad)

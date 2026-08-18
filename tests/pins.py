"""Numeric shape pins — the cheap way to lock a drawing down.

`biodraw` is a geometry library: what a change can silently break is the
*vertices*, not the pixels. So the primary regression net is a digest of the
geometry, stored as JSON in `tests/shape_pins.json`.

Why not baseline images for everything: a PNG is ~10-40 kB each and the
library will end up with dozens of shapes, which is megabytes of binary in a
repo whose whole product is a few hundred lines of maths. A digest is ~150
bytes, is *exact* rather than tolerance-based, is readable in a diff, and does
not shift when matplotlib changes its anti-aliasing.

A handful of image baselines are still kept, for the things geometry genuinely
cannot capture — that the two-pass union really does fuse, and that a wall
comes out the thickness it was asked for. See `test_render.py`.

A digest holds the vertex count, the bounding box, the centroid, the path
length and a SHA of the rounded vertices. Rounding to `DECIMALS` keeps it
stable across platforms while still catching any real change to a shape.
"""

import hashlib
import json
import pathlib

import numpy as np

PINS = pathlib.Path(__file__).resolve().parent / "shape_pins.json"
DECIMALS = 6


def digest(points):
    """A compact, exact fingerprint of a vertex array.

    Accepts an (N, 2) array or a `matplotlib.path.Path`.
    """
    p = points.vertices if hasattr(points, "vertices") else points
    p = np.asarray(p, dtype=float)
    if p.ndim != 2 or p.shape[1] != 2:
        raise ValueError("expected an (N, 2) array of vertices")
    if not np.isfinite(p).all():
        raise ValueError("vertex array contains NaN or inf")

    rounded = np.round(p, DECIMALS) + 0.0     # +0.0 normalises -0.0 to 0.0
    steps = np.linalg.norm(np.diff(p, axis=0), axis=1)
    # Cast through `float` rather than leaving numpy scalars: they serialise
    # to JSON but their repr is `np.float64(...)`, which makes the diff a
    # regeneration prints unreadable.
    return {
        "n": int(len(p)),
        "bbox": [round(float(v), DECIMALS) for v in
                 (*p.min(axis=0), *p.max(axis=0))],
        "centroid": [round(float(v), DECIMALS) for v in p.mean(axis=0)],
        "length": round(float(steps.sum()), DECIMALS),
        "sha": hashlib.sha256(rounded.tobytes()).hexdigest()[:16],
    }


def load():
    """Every stored pin, or an empty dict if there are none yet."""
    if not PINS.exists():
        return {}
    return json.loads(PINS.read_text(encoding="utf8"))


def save(pins):
    """Write the pins back, sorted and indented so diffs are readable."""
    PINS.write_text(json.dumps(pins, indent=2, sort_keys=True) + "\n",
                    encoding="utf8")


def check(name, points, pins=None, update=False):
    """Compare `points` against the stored pin for `name`.

    Returns `(ok, message)`. With `update`, or when the name is not pinned
    yet, the pin is written instead of compared.
    """
    got = digest(points)
    store = load() if pins is None else pins

    if update or name not in store:
        store[name] = got
        if pins is None:
            save(store)
        return True, f"{name}: pinned"

    want = store[name]
    if got == want:
        return True, f"{name}: unchanged"

    diffs = [f"    {k}: {want[k]!r} -> {got[k]!r}"
             for k in sorted(set(want) | set(got))
             if want.get(k) != got.get(k)]
    return False, (f"{name}: geometry changed\n" + "\n".join(diffs)
                   + "\n    If this was intended, regenerate with:\n"
                     "        python tools/update_pins.py")

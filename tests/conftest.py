"""Test configuration.

Image-comparison baselines are sensitive to backend and rcParams, so both are
pinned here. Every baseline in `tests/baseline/` was generated under exactly
this configuration; if a comparison starts failing everywhere at once, suspect
this file or a matplotlib upgrade before suspecting the geometry.
"""

import matplotlib
import pytest

matplotlib.use("Agg")


@pytest.fixture(autouse=True)
def _pinned_rcparams():
    """Neutral, version-stable rcParams for every test."""
    with matplotlib.rc_context({
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "figure.dpi": 100,
        "savefig.dpi": 100,
        "path.simplify": False,     # keep every vertex we generated
        "svg.fonttype": "none",
    }):
        yield

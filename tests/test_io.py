"""Canvas setup and vector export."""

import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pytest

import biodraw as bd
from biodraw.core import paths, render


def _drawn():
    fig, ax = bd.canvas(figsize=(2.0, 2.0))
    ring = paths.superellipse(1.0, 1.0, 3.0)
    render.render_hollow(ax, [ring], "pink", "#FF0000", 1.5, gid="body")
    bd.fit(ax, [ring], pad=0.1)
    return fig, ax, ring


def test_canvas_is_aspect_locked_and_frameless():
    fig, ax = bd.canvas()
    assert ax.get_aspect() == 1.0
    assert not ax.axison


def test_canvas_configures_an_existing_axes_in_place():
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    got_fig, got_ax = bd.canvas(ax=ax)
    assert got_ax is ax and got_fig is fig
    assert ax.get_aspect() == 1.0


def test_fit_pads_in_local_units():
    fig, ax = bd.canvas()
    ring = paths.superellipse(1.0, 1.0, 2.0)
    x0, y0, x1, y1 = bd.fit(ax, [ring], pad=0.25)
    assert np.isclose(x0, -1.25) and np.isclose(x1, 1.25)
    assert np.isclose(y0, -1.25) and np.isclose(y1, 1.25)


def test_fit_accepts_paths_and_arrays_together():
    fig, ax = bd.canvas()
    ring = paths.superellipse(1.0, 1.0, 2.0)
    tri = paths.rounded_polygon([(0, 2), (-1, 0), (1, 0)], 0.1)
    _, _, _, y1 = bd.fit(ax, [ring, tri], pad=0.0)
    assert np.isclose(y1, 2.0)


def test_fit_accepts_a_bare_array():
    fig, ax = bd.canvas()
    x0, _, x1, _ = bd.fit(ax, paths.superellipse(1.0, 1.0, 2.0), pad=0.0)
    assert np.isclose(x1 - x0, 2.0)


def test_save_svg_keeps_text_as_text_and_names_its_groups(tmp_path):
    fig, ax, _ = _drawn()
    ax.text(0.0, 0.0, "soma", ha="center")
    out = bd.save(fig, tmp_path / "cell.svg")
    svg = open(out, encoding="utf8").read()
    assert 'id="body' in svg            # named layers survived
    assert "<image" not in svg          # nothing rasterized
    assert "soma" in svg                # text is text, not outlines


def test_save_refuses_a_rasterized_artist(tmp_path):
    fig, ax, _ = _drawn()
    for artist in ax.patches:
        artist.set_rasterized(True)
    with pytest.raises(ValueError, match="rasterized"):
        bd.save(fig, tmp_path / "cell.svg")


def test_save_can_be_forced_past_the_raster_check(tmp_path):
    fig, ax, _ = _drawn()
    for artist in ax.patches:
        artist.set_rasterized(True)
    assert bd.save(fig, tmp_path / "cell.svg", check=False)


def test_save_pdf_uses_embeddable_fonts(tmp_path):
    fig, _, _ = _drawn()
    out = bd.save(fig, tmp_path / "cell.pdf")
    assert open(out, "rb").read(5) == b"%PDF-"


def test_save_svg_is_byte_reproducible(tmp_path):
    """A figure written twice must be the same file, or CI cannot diff
    `examples/` and every rebuild is noise. matplotlib's defaults are not:
    it stamps a `<dc:date>` and salts its clip-path ids from a fresh uuid4
    per process."""
    def write(name):
        fig, ax = bd.canvas()
        ax.plot([0, 1], [0, 1])
        # A clip path, so the salted ids are actually exercised.
        ax.set_xlim(0.1, 0.9)
        path = bd.save(fig, tmp_path / name)
        plt.close(fig)
        return pathlib.Path(path).read_bytes()

    assert write("a.svg") == write("b.svg")
    assert b"dc:date" not in write("c.svg")

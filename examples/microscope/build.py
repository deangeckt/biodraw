"""The instrument a methods figure opens with.

`docs/SCOPE.md` says this library should never try to compete with a stock
asset library, and a microscope looks at first like exactly the thing to
download rather than draw. The test that admits it is the library's own:
**anything that wants varying is a candidate, anything that only wants
downloading is not.** A drawn microscope has counts in it — the nosepiece
everybody redraws, an upright body against an inverted one — and no
downloaded picture of somebody else's instrument knows yours.

Drawn as an outline, in the house schematic style: a microscope at figure
size is about two centimetres tall, and a knurled focus wheel at that size is
bytes spent on something the reader cannot resolve.

    python tools/build_gallery.py microscope
"""

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import biodraw as bd  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
PAL = bd.style.palette.get()
BODY = PAL["tertiary"]
MARK = PAL["primary"]
# A caption is not a drawing, so it takes neither identity colour.
TEXT = "#555555"
GREY = "#9AA0A6"


def _panel(ax, scope, pad=0.06, **kw):
    bd.canvas(ax=ax)
    scope.draw(ax=ax, edge=BODY, wall_lw=1.1, **kw)
    bd.fit(ax, scope.points, pad=pad)
    return scope


# ---------------------------------------------------------------------------
# microscope.png — the hero
# ---------------------------------------------------------------------------

def hero():
    """One upright compound microscope, with a camera port."""
    fig, ax = bd.canvas(figsize=(3.0, 3.8))
    scope = bd.lab.Microscope(camera=True)
    scope.draw(ax=ax, edge=BODY, wall_lw=1.2, gid="microscope")
    bd.fit(ax, scope.points, pad=0.05)
    return fig, "microscope.png"


# ---------------------------------------------------------------------------
# objectives.png — the knob it exists for
# ---------------------------------------------------------------------------

def objectives():
    """None through five on the nosepiece.

    The whole argument for drawing an instrument rather than downloading one.
    A turret is *indexed*, so one barrel always sits on the optical axis and
    the rest fan either side of it — an even split straddling the axis would
    say no objective is engaged.
    """
    fig, axes = plt.subplots(1, 6, figsize=(11.4, 2.5), dpi=150)
    for ax, n in zip(axes, range(6), strict=True):
        _panel(ax, bd.lab.Microscope(objectives=n))
        ax.set_title(f"objectives={n}", fontsize=8.5, loc="left", color=TEXT)
    fig.tight_layout(w_pad=0.8)
    return fig, "objectives.png"


# ---------------------------------------------------------------------------
# bodies.png — upright against inverted
# ---------------------------------------------------------------------------

def bodies():
    """The two instruments, each with one objective and with four.

    Not a mirror and not a rotation. On an upright the objectives hang onto
    the specimen from above and the light comes up through the condenser
    below; on an inverted they look *up* from beneath the stage and the lamp
    rides a gantry over the top. That is why an inverted one can sit under a
    culture flask, and why anybody draws the difference.

    This sheet showed monocular against binocular until the difference was
    measured: **0.0%** on the inverted body. Two eyepiece tubes separate into
    the page, so a side elevation hides one behind the other, and the knob
    was cut rather than kept as a lie. See the module docstring.
    """
    cases = (("upright, 1", dict(objectives=1)),
             ("upright, 4", dict(objectives=4)),
             ("inverted, 1", dict(inverted=True, objectives=1)),
             ("inverted, 4", dict(inverted=True, objectives=4)))
    fig, axes = plt.subplots(1, 4, figsize=(9.2, 2.9), dpi=150)
    for ax, (title, kw) in zip(axes, cases, strict=True):
        _panel(ax, bd.lab.Microscope(**kw))
        ax.set_title(title, fontsize=8.5, loc="left", color=TEXT)
    fig.tight_layout(w_pad=1.0)
    return fig, "bodies.png"


# ---------------------------------------------------------------------------
# fittings.png — what is on it, and what is not
# ---------------------------------------------------------------------------

def fittings():
    """Stage, condenser and camera, present or not.

    A figure about optics wants the light path; a figure about a workflow
    wants the silhouette and nothing else. Both are the same object.
    """
    cases = (("everything", dict(camera=True)),
             ("no camera", dict()),
             ("no condenser", dict(condenser=False)),
             ("no stage either", dict(stage=False, condenser=False)))
    fig, axes = plt.subplots(1, 4, figsize=(9.2, 2.9), dpi=150)
    for ax, (title, kw) in zip(axes, cases, strict=True):
        _panel(ax, bd.lab.Microscope(**kw))
        ax.set_title(title, fontsize=8.5, loc="left", color=TEXT)
    fig.tight_layout(w_pad=1.0)
    return fig, "fittings.png"


# ---------------------------------------------------------------------------
# blueprint.png — the parts, and the one distance that has to be right
# ---------------------------------------------------------------------------

def blueprint():
    """Three panels: the parts, the anchors, and the working distance."""
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.6), dpi=150)

    # -- 1. the parts ------------------------------------------------------
    ax = axes[0]
    scope = _panel(ax, bd.lab.Microscope(), pad=0.02)
    layout = scope._layout()
    # Position from the shape, direction chosen for the page. An objective's
    # own normal points at the specimen, which is the right direction for a
    # light ray and the wrong one for a caption — followed literally it put
    # the word "objectives" below the foot of the instrument. Taking the
    # anchor's *place* and overriding its *direction* is the honest way to
    # say that, and it is why `label` takes an anchor rather than a shape.
    left = bd.Anchor(layout["turret"] * scope.size, (-1.0, 0.18), "callout")
    marks = bd.label(ax=ax, at=left, text="objectives", gap=0.30,
                     leader=True, fontsize=8, color=TEXT, leader_color=GREY)
    # The stage's own far edge, from `_layout`. Reaching for the shape's
    # leftmost *wall* anchor instead put the word "stage" on the foot, which
    # sticks out further — a caption is only as good as the anchor under it.
    stage_edge = bd.Anchor(
        (layout["stage_x0"] * scope.size,
         (layout["stage_y"] - 0.018) * scope.size), (-1.0, 0.0), "callout")
    marks += bd.label(ax=ax, at=stage_edge, text="stage", gap=0.05,
                      fontsize=8, color=TEXT)
    for kind, gap in (("eyepiece", 0.09), ("base", 0.07)):
        marks += bd.label(ax=ax, at=scope.anchor(kind), text=kind, gap=gap,
                          fontsize=8, color=TEXT)
    bd.fit(ax, scope.points, pad=0.04, marks=marks)
    ax.set_title("1 · the parts", fontsize=9.5, loc="left", color=TEXT)

    # -- 2. every anchor it exposes ----------------------------------------
    ax = axes[1]
    scope = _panel(ax, bd.lab.Microscope(), pad=0.12)
    for a in scope.anchors("wall"):
        ax.plot(*a.xy, "o", ms=2.4, color=GREY, zorder=6)
    for kind in ("objective", "eyepiece", "stage", "base"):
        for a in scope.anchors(kind):
            ax.plot(*a.xy, "o", ms=3.4, color=MARK, zorder=7)
            ax.quiver(a.xy[0], a.xy[1], a.normal[0], a.normal[1], color=MARK,
                      scale=11, width=0.007, zorder=7)
    ax.set_title("2 · the anchors", fontsize=9.5, loc="left", color=TEXT)

    # -- 3. the working distance -------------------------------------------
    ax = axes[2]
    bd.canvas(ax=ax)
    scope = bd.lab.Microscope(objectives=1)
    scope.draw(ax=ax, edge=BODY, wall_lw=1.1)
    layout = scope._layout()
    tip = scope.anchor("objective").xy
    stage_y = layout["stage_y"] * scope.size
    gap = tip[1] - stage_y
    # The gap that has to be positive, drawn as the dimension it is. The
    # first version of this shape had it at **-0.044**: the barrels ran
    # through the slide. Only the numbers showed it — the outline was
    # perfectly convincing, and it is pinned as a test now.
    # Framed on the business end, not the instrument. The gap is 0.035 on a
    # shape 0.92 tall — 4% of the frame, which is a panel that cannot show
    # the one thing it is for. The library's own rule about the zebrafish
    # stripes applies to blueprints too: draw it at a size where it reads,
    # or do not claim to be showing it.
    x = tip[0] - 0.085
    ax.plot([x - 0.02, tip[0] + 0.15], [stage_y, stage_y], color=MARK,
            lw=0.9, ls=":", zorder=6)
    ax.annotate("", xy=(x, tip[1]), xytext=(x, stage_y),
                arrowprops=dict(arrowstyle="<->", color=MARK, lw=1.0,
                                shrinkA=0, shrinkB=0))
    marks = bd.label(
        ax=ax,
        at=bd.Anchor((x, tip[1] + 0.012), (0.0, 1.0), "callout"),
        text=f"working distance = {gap:.3f}", fontsize=8, gap=0.012,
        color=MARK)
    box = np.array([[tip[0] - 0.26, stage_y - 0.055],
                    [tip[0] + 0.20, tip[1] + 0.075]])
    bd.fit(ax, [box], pad=0.012, marks=marks)
    ax.set_title("3 · the distance that must be positive", fontsize=9.5,
                 loc="left", color=TEXT)

    fig.tight_layout(w_pad=1.2)
    return fig, "blueprint.png"


BUILDS = (hero, objectives, bodies, fittings, blueprint)


def main():
    for build in BUILDS:
        fig, name = build()
        bd.save_compact(fig, HERE / name)
        plt.close(fig)
        size = (HERE / name).stat().st_size / 1024
        print(f"wrote {(HERE / name).relative_to(HERE.parent.parent)} "
              f"({size:.0f} KB)")


if __name__ == "__main__":
    main()

"""The shapes under regression, in one place.

Every entry is `name -> vertex array (or Path)`. `test_pins.py` fingerprints
them all, and `tools/update_pins.py` regenerates the stored digests from the
same dict — so adding a shape to the net means adding one line here.

Keep these deliberately un-clever: fixed numbers, no randomness, no
dependencies on anything a caller could change.
"""

import numpy as np

from biodraw.animals import Fly, Mouse, Worm, Zebrafish
from biodraw.cells import Blob, Sheet
from biodraw.core import paths, profile
from biodraw.core.branch import Branch
from biodraw.core.scatter import scatter_in
from biodraw.core.track import Track
from biodraw.genetics import CDS, Promoter, Protein, Repeat, Terminator
from biodraw.micro import Bacterium
from biodraw.neuro import (
    Astrocyte,
    Basket,
    Bipolar,
    Granule,
    Purkinje,
    Pyramidal,
)


def _straight(n=60, length=2.0):
    return np.column_stack([np.linspace(0, length, n), np.zeros(n)])


def _spiny_branch():
    br = Branch((0.0, 0.0), (0.0, 1.0), length=1.8, bend=0.10)
    br.decorate("spine", n=8, size=0.21, extend=0.04, first_t=0.30,
                last_t=0.86)
    return br


def collect():
    """`{name: vertices}` for everything pinned."""
    sp = profile.get("spine")
    br = _spiny_branch()
    line = _straight()
    hw = np.linspace(0.14, 0.08, len(line))

    shapes = {
        # -- profiles ------------------------------------------------------
        "profile.spine.raw": sp.points,
        "profile.spine.placed": sp.place((0, 0), (0, 1), size=0.3),
        "profile.spine.extended": sp.place((0, 0), (0, 1), size=0.3,
                                           extend=0.12),
        "profile.spine.mirrored": sp.place((0, 0), (0, 1), size=0.3,
                                           mirror=True),
        "profile.spine.rotated": sp.place((1, 2), (0.6, 0.8), size=0.3),
        # A mushroom spine: fat head on a thin neck, same traced outline.
        "profile.spine.mushroom": sp.place((0, 0), (0, 1), size=0.3,
                                           head=1.35, neck=0.62),

        # -- tubes ---------------------------------------------------------
        "tube.capped": paths.tube(line, hw, base_ext=0.1),
        "tube.open": paths.tube(line, hw, base_ext=0.1, open_end=True),
        "tube.parallel": paths.tube(line, 0.12),

        # -- bodies --------------------------------------------------------
        "body.superellipse": paths.superellipse(0.42, 0.40, 3.4,
                                                wobble=0.015),
        "body.ellipse": paths.superellipse(1.0, 0.6, 2.0),
        "body.bowed_triangle": paths.bowed_ring(
            [(0.0, 0.40), (-0.62, -0.60), (0.62, -0.60)],
            [-0.005, 0.02, -0.005]),
        "body.rounded_triangle": paths.rounded_polygon(
            [(0.0, 0.40), (-0.62, -0.60), (0.62, -0.60)], 0.08),
        "body.neck_polygon": paths.neck_polygon(
            (0, 0.40), (-0.62, -0.60), (0.62, -0.60), hw=0.055, neck_r=0.25,
            corner_r=0.05, bow_bottom=-0.025, bow_side=0.0)[0],

        # -- branches ------------------------------------------------------
        "branch.centreline": br.centre,
        "branch.tube": br.outline(width=0.11, taper=0.72, base_ext=0.05),
        "branch.spine.first": br.decorations[0]["outline"],
        "branch.spine.last": br.decorations[-1]["outline"],

        # -- connectors ----------------------------------------------------
        "connector.elbow": paths.elbow((0, 0), (0, -1), run=2.2,
                                       turn_deg=90.0, radius=2.1)[0],
        "connector.cubic": np.asarray(
            paths.cubic_connector((0, 0), (3, -1), drop=0.95, rad=-0.05,
                                  smooth=0.25)),
    }

    stem, branches = paths.fork_tree((0, 0), [(3.0, -1.0), (-2.5, 0.6)],
                                     drop=0.95, rads=[-0.05, -0.05],
                                     smooth=0.25, fork=0.5, spread=0.35)
    shapes["connector.fork.stem"] = stem
    for i, b in enumerate(branches):
        shapes[f"connector.fork.branch{i}"] = b

    # -- cells -------------------------------------------------------------
    # Whole assembled shapes, so a change to how the pieces fit together is
    # caught even when every piece is individually unchanged.
    cell = Pyramidal(spines=8, basal=2, basal_spines=5)
    closed, open_ = cell.parts
    shapes["pyramidal.soma"] = closed[-1]
    shapes["pyramidal.apical.tube"] = open_[0]
    shapes["pyramidal.basal.tube"] = open_[1]
    shapes["pyramidal.spine.first"] = closed[0]
    shapes["pyramidal.anchors"] = cell.anchors().points()
    shapes["pyramidal.anchor_normals"] = np.array(
        [a.normal for a in cell.anchors()])

    bare = Pyramidal(spines=4, basal=0)
    shapes["pyramidal.bare.soma"] = bare.parts[0][-1]

    # -- the rest of neuro -------------------------------------------------
    bask = Basket(dendrites=7, forks=0.55, seed=2)
    b_closed, b_open = bask.parts
    shapes["basket.soma"] = b_closed[-1]
    shapes["basket.dendrite.first"] = b_closed[0]
    shapes["basket.daughter.first"] = b_open[0]
    shapes["basket.anchors"] = bask.anchors().points()

    # -- the non-neuron domain ---------------------------------------------
    # Layered shapes, so the pins also lock down that `parts` keeps gathering
    # every layer in the same order.
    blob = Blob(organelles=6, protrusions=8, seed=0)
    b_closed, b_open = blob.parts
    shapes["blob.wall"] = b_closed[0]
    shapes["blob.organelle.first"] = b_closed[1]
    shapes["blob.nucleus"] = b_closed[-2]
    shapes["blob.nucleolus"] = b_closed[-1]
    shapes["blob.protrusion.first"] = b_open[0]
    shapes["blob.anchors"] = blob.anchors().points()

    # -- animals -----------------------------------------------------------
    # One assembled silhouette per body plan, plus the two that carry a
    # layer the union does not see (the fly's wing, the fish's stripe).
    mouse = Mouse()
    m_closed, m_open = mouse.parts
    shapes["mouse.body"] = m_closed[0]
    shapes["mouse.tail"] = m_open[0]
    shapes["mouse.anchors"] = mouse.anchors().points()
    shapes["mouse.mirrored.body"] = Mouse(facing=-1).parts[0][0]

    fly = Fly()
    shapes["fly.thorax"] = fly.parts[0][1]
    shapes["fly.wing"] = fly.layers[1].closed[0]

    fish = Zebrafish()
    shapes["fish.body"] = fish.parts[0][0]
    shapes["fish.caudal"] = fish.parts[0][1]
    shapes["fish.stripe.first"] = fish.layers[1].closed[0]

    shapes["worm.body"] = Worm().parts[0][0]

    # -- genetics ----------------------------------------------------------
    # The whole track, not the glyphs on their own: what is easy to get wrong
    # here is the *layout*, so the pin has to cover a glyph that has been laid
    # rather than one drawn at the origin.
    track = Track([Repeat(n=4), Promoter(), CDS(width=0.92), Terminator()])
    t_closed, _t_open = track.parts
    shapes["track.repeat.first"] = t_closed[0]
    shapes["track.promoter.stem"] = t_closed[4]
    shapes["track.cds"] = t_closed[6]
    shapes["track.backbone"] = t_closed[-1]
    shapes["track.anchors"] = track.anchors().points()

    prot = Protein(lobes=2, open_deg=30.0, tags=(42.0, 138.0), seed=3)
    p_closed, _p_open = prot.parts
    shapes["protein.lobe.first"] = p_closed[0]
    shapes["protein.tag.first"] = p_closed[2]
    shapes["protein.anchors"] = prot.anchors().points()

    # -- microbes ----------------------------------------------------------
    # A bent, twisted, loaded cell rather than a plain rod: a straight capsule
    # exercises none of the arithmetic that is actually easy to get wrong, and
    # the nucleoid on a curved axis is where this shape's one geometry bug was.
    bug = Bacterium(length=1.5, curve_deg=30.0, twists=0.9, capsule=0.16,
                    nucleoid=0.62, granules=3, flagella=5,
                    flagella_arc_deg=360.0, pili=6, seed=3)
    m_closed, m_open = bug.parts
    shapes["bacterium.capsule"] = m_closed[0]
    shapes["bacterium.wall"] = m_closed[1]
    shapes["bacterium.nucleoid"] = m_closed[2]
    shapes["bacterium.granule.first"] = m_closed[3]
    shapes["bacterium.flagellum.first"] = m_open[0]
    shapes["bacterium.anchors"] = bug.anchors().points()

    # The four named forms, so a change to how the axis is built shows up as
    # four separate failures rather than one — the coccus included, because a
    # capsule of zero length is the degenerate case most likely to break.
    for name, kw in (("coccus", dict(length=0.0, width=0.62)),
                     ("bacillus", dict(length=1.4)),
                     ("vibrio", dict(length=1.4, curve_deg=72.0)),
                     ("spirillum", dict(length=2.2, twists=1.8,
                                        twist_amp=0.62))):
        shapes[f"bacterium.{name}"] = Bacterium(seed=3, **kw).parts[0][0]

    flat = Sheet(cells=5, microvilli=4, seed=0)
    shapes["sheet.membrane"] = flat.geometry["membrane"]
    shapes["sheet.cell.first"] = flat.geometry["cells"][0]["outline"]
    shapes["sheet.nucleus.first"] = flat.geometry["cells"][0]["nucleus"]
    shapes["sheet.anchors"] = flat.anchors().points()

    # The closed ring, which is the case where the arc maths has to come back
    # round to exactly where it started.
    ring = Sheet(cells=10, curve_deg=-360.0, height=0.34, microvilli=3,
                 seed=0)
    shapes["sheet.ring.membrane"] = ring.geometry["membrane"]
    shapes["sheet.ring.cell.first"] = ring.geometry["cells"][0]["outline"]
    shapes["sheet.ring.cell.last"] = ring.geometry["cells"][-1]["outline"]

    # The scatter itself, since a change to the sampler would move every
    # organelle in every drawing at once and nothing else would catch it.
    shapes["scatter.in_superellipse"] = scatter_in(
        paths.superellipse(1.0, 0.8, 2.6), 12, seed=0, min_sep=0.25,
        margin=0.12)

    forked = Pyramidal(spines=0, apical_fork=0.42, fork_angle_deg=35,
                       fork_spines=2, basal=2, basal_spines=2)
    f_closed, f_open = forked.parts
    # A forked trunk is *capped*, so it is a closed part and comes first;
    # the two daughters are then the first two open ones. An unforked apical
    # is open-ended and would be `f_open[0]` instead.
    shapes["pyramidal.forked.trunk"] = f_closed[0]
    shapes["pyramidal.forked.daughter.l"] = f_open[0]
    shapes["pyramidal.forked.daughter.r"] = f_open[1]

    # -- the radial cell's named forms -------------------------------------
    # One shape at five settings, so a change to the shared body plan shows up
    # on whichever form it breaks rather than on none of them.
    for name, cell in (("basket", Basket()), ("bipolar", Bipolar()),
                       ("granule", Granule()), ("purkinje", Purkinje()),
                       ("astrocyte", Astrocyte())):
        closed, open_ = cell.parts
        shapes[f"radial.{name}.soma"] = closed[-1]
        shapes[f"radial.{name}.first"] = (open_ or closed)[0]
        shapes[f"radial.{name}.anchors"] = cell.anchors().points()

    return shapes

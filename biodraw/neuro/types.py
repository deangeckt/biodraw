"""Four more neurons, as settings of the radial body plan.

None of these is a new kind of object. Each is `RadialCell` with the arc, the
process count, the length spread and the branching depth that make a reader
name it — which is the same call `micro.Bacterium` makes for its named forms,
and the reason adding a cell type here costs a docstring rather than a module.

What tells them apart on the page, in the order a reader uses:

    Bipolar    two processes, opposed            arc 180, dendrites 2
    Granule    small soma, few short claws       small radius, depth 2
    Purkinje   a flat fan, densely branched      arc 55, depth 3
    Astrocyte  a bush in every direction         many processes, depth 2

Every one of those is an *arc* and a *depth*, which is the argument for the
shared shape: the differences a reader actually uses are the differences the
parameters already carry.

One caution these settings were tuned against. **The recursion does not avoid
itself.** Branch count is `dendrites * (2^(depth+1) - 1)`, and every one of
them sweeps through the same arc, so density climbs far faster than it looks
like it should: the Purkinje at depth 4 is **93** branches, and in a
55-degree wedge they cross each other until the union fuses the fan into a
lattice with holes in it. The same cell at depth 3 is 45, and fans. Depth is
not a quality knob — past about 3 it stops adding detail and starts adding
collisions.

(Those two numbers were wrong here for three sessions — the docstring claimed
45 for the depth-4 case and 14 for a depth-3 one that is 30. They are printed
on the sheets in `examples/purkinje/` now, from `len(cell._branches())`, so
the prose and the drawing cannot drift apart again.)
"""

from .radial import RadialCell

__all__ = ["Astrocyte", "Bipolar", "Granule", "Purkinje"]


class Bipolar(RadialCell):
    """A bipolar cell: one process out of each end of an elongated soma.

    The simplest body plan here and the most distinctive, because two opposed
    processes is a silhouette nothing else in the library shares. Retinal
    bipolar cells, many sensory neurons and most cultured cells at an early
    stage read this way.

    `arc_deg=180` with two processes puts them exactly opposite; the soma is
    stretched along that axis (`aspect`) so the cell reads as *polarised*
    rather than as a circle that happens to have two arms.
    """

    def __init__(self, radius=0.26, aspect=1.75, squareness=2.1, wobble=0.02,
                 dendrites=2, arc_deg=180.0, start_deg=90.0,
                 length=1.35, length_ratio=0.82, jitter=0.10,
                 width=None, taper=0.55,
                 forks=0.72, fork_angle_deg=26.0, fork_ratio=0.85, depth=1,
                 **kw):
        super().__init__(
            radius=radius, aspect=aspect, squareness=squareness,
            wobble=wobble, dendrites=dendrites, arc_deg=arc_deg,
            start_deg=start_deg, length=length, length_ratio=length_ratio,
            jitter=jitter, width=width, taper=taper, forks=forks,
            fork_angle_deg=fork_angle_deg, fork_ratio=fork_ratio,
            depth=depth, **kw)


class Granule(RadialCell):
    """A granule cell: a small soma with a few short, clawed dendrites.

    The smallest neuron in the set, and the one whose *proportions* carry the
    identity — a granule cell is mostly soma, with dendrites barely longer
    than the cell body and ending in short forked claws. Drawn at a basket
    cell's proportions it stops reading as a granule cell at all, which is why
    `length` is the knob that matters here and not the count.
    """

    def __init__(self, radius=0.30, aspect=1.05, squareness=2.0, wobble=0.03,
                 dendrites=4, arc_deg=360.0, start_deg=40.0,
                 length=0.85, length_ratio=0.72, jitter=0.28,
                 width=0.085, taper=0.62,
                 forks=0.62, fork_angle_deg=44.0, fork_ratio=0.78, depth=2,
                 **kw):
        super().__init__(
            radius=radius, aspect=aspect, squareness=squareness,
            wobble=wobble, dendrites=dendrites, arc_deg=arc_deg,
            start_deg=start_deg, length=length, length_ratio=length_ratio,
            jitter=jitter, width=width, taper=taper, forks=forks,
            fork_angle_deg=fork_angle_deg, fork_ratio=fork_ratio,
            depth=depth, **kw)


class Purkinje(RadialCell):
    """A Purkinje cell: a flat, densely branched fan over one soma.

    The most recognisable neuron there is, and the recognition is entirely
    about the *arc*: everything leaves upward into a wedge rather than in
    every direction, and it branches until the fan is dense. That is an arc
    and a depth, so no new geometry is needed — which is the clearest evidence
    that these belong to one shape.

    A real Purkinje arbor is planar, and a drawing of one is a projection of
    that plane, so the flat fan here is not a simplification.

    Tuned once the cell got a page of its own and its portrait had to carry
    it. Two primaries in a 34-degree wedge is what a Purkinje looks like in a
    *schematic*; at portrait size it read as a two-pronged fork, and the two
    trunks running parallel up the middle crossed their own daughters into a
    lattice with holes in it. Three primaries over 55 degrees is half as many
    branches again — 45 against 30 — spread over enough arc that they stop
    colliding, and it reads as the fan the cell is named for.
    """

    def __init__(self, radius=0.26, aspect=1.15, squareness=2.4, wobble=0.02,
                 dendrites=3, arc_deg=55.0, start_deg=63.0,
                 length=1.45, length_ratio=0.92, jitter=0.14,
                 width=0.10, taper=0.50,
                 forks=0.52, fork_angle_deg=30.0, fork_ratio=0.88, depth=3,
                 **kw):
        super().__init__(
            radius=radius, aspect=aspect, squareness=squareness,
            wobble=wobble, dendrites=dendrites, arc_deg=arc_deg,
            start_deg=start_deg, length=length, length_ratio=length_ratio,
            jitter=jitter, width=width, taper=taper, forks=forks,
            fork_angle_deg=fork_angle_deg, fork_ratio=fork_ratio,
            depth=depth, **kw)


class Astrocyte(RadialCell):
    """An astrocyte: a bush of fine processes in every direction.

    Not a neuron, and drawn so nobody mistakes it for one: a small soma almost
    lost inside many short processes that branch immediately and keep
    branching, with no dominant direction and no long axis. Where a Purkinje
    cell is a fan, this is a cloud.

    `taper` is severe on purpose — astrocytic processes get very fine very
    fast, and a bush drawn at constant width reads as a root system.
    """

    def __init__(self, radius=0.24, aspect=1.06, squareness=2.0, wobble=0.05,
                 dendrites=10, arc_deg=360.0, start_deg=12.0,
                 length=0.70, length_ratio=0.52, jitter=0.45,
                 width=0.070, taper=0.38,
                 forks=0.50, fork_angle_deg=44.0, fork_ratio=0.82, depth=2,
                 **kw):
        super().__init__(
            radius=radius, aspect=aspect, squareness=squareness,
            wobble=wobble, dendrites=dendrites, arc_deg=arc_deg,
            start_deg=start_deg, length=length, length_ratio=length_ratio,
            jitter=jitter, width=width, taper=taper, forks=forks,
            fork_angle_deg=fork_angle_deg, fork_ratio=fork_ratio,
            depth=depth, **kw)

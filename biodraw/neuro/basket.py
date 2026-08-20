"""The basket cell: a round soma with smooth dendrites out of it.

The counterpart to `Pyramidal`, and drawn to be told apart from it at a
glance — which is the whole job of an inhibitory cell in a circuit panel.
Three cues do that work, and all three are structural rather than a change of
colour:

* a **round** soma instead of a triangle;
* dendrites that leave in several directions rather than one up and two down;
* **smooth** dendrites — no spines. A basket cell is aspiny, and drawing it
  that way means a reader can tell the two cells apart in greyscale, which
  colour alone would not survive.

The body plan lives in `RadialCell`, which also draws the bipolar, granule,
Purkinje and astrocyte cells: they differ in how many processes leave, over
what arc, and how often those branch, not in what kind of object they are.
This class is that shape at a basket cell's settings.
"""

from .radial import RadialCell

__all__ = ["Basket"]


class Basket(RadialCell):
    """A cartoon basket cell.

    Every knob is `RadialCell`'s; only the defaults differ. Six dendrites over
    the full circle, of uneven length, smooth and unbranched — which is what
    an aspiny interneuron looks like next to a spiny pyramidal cell.
    """

    def __init__(self, radius=0.40, aspect=1.12, squareness=2.2, wobble=0.03,
                 dendrites=6, arc_deg=360.0, start_deg=18.0,
                 length=1.05, length_ratio=0.68, jitter=0.22,
                 width=None, taper=0.62,
                 forks=None, fork_angle_deg=34.0, fork_ratio=0.76, depth=1,
                 seed=0, at=(0.0, 0.0), scale=1.0, rotate_deg=0.0,
                 geom_kw=None):
        super().__init__(
            radius=radius, aspect=aspect, squareness=squareness,
            wobble=wobble, dendrites=dendrites, arc_deg=arc_deg,
            start_deg=start_deg, length=length, length_ratio=length_ratio,
            jitter=jitter, width=width, taper=taper, forks=forks,
            fork_angle_deg=fork_angle_deg, fork_ratio=fork_ratio, depth=depth,
            seed=seed, at=at, scale=scale, rotate_deg=rotate_deg,
            geom_kw=geom_kw)

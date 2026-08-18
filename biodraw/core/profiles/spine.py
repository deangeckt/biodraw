"""The dendritic spine profile — traced off a hand drawing.

This is the shape the whole library grew out of, and the clearest example of
why `biodraw` traces rather than synthesises.

Every attempt to build this profile out of ellipses and smoothsteps read as a
cone, a bead on a stick, or a leaf. The distinguishing features are the
*concave* flare — a constant thin neck for the first ~35%, then an
accelerating widening — and the blunt, slightly up-tilted head. The gentle
left/right asymmetry is the original drawing's hand-drawn wobble, and is kept
on purpose: it is what stops a branch of these reading as stamped clip art.

Provenance: hand-drawn on paper, photographed, vectorised, then normalised into
the canonical frame (base chord midpoint at the origin, tip at x=1). See
`examples/01_spine/` for the sketch and the derivation, and `biodraw.trace` for
doing the same with your own drawing.
"""

import numpy as np

from ..profile import Profile, register

__all__ = ["SPINE_POINTS", "spine"]


SPINE_POINTS = np.array([
    (0.0000, +0.1503), (0.0487, +0.1349), (0.0997, +0.1293), (0.1510, +0.1282),
    (0.2022, +0.1292), (0.2535, +0.1311), (0.3047, +0.1342), (0.3553, +0.1426),
    (0.4031, +0.1611), (0.4489, +0.1840), (0.4931, +0.2101), (0.5351, +0.2395),
    (0.5754, +0.2713), (0.6142, +0.3048), (0.6522, +0.3393), (0.6907, +0.3733),
    (0.7307, +0.4053), (0.7738, +0.4331), (0.8225, +0.4477), (0.8706, +0.4327),
    (0.9089, +0.3988), (0.9383, +0.3569), (0.9591, +0.3101), (0.9734, +0.2608),
    (0.9833, +0.2105), (0.9899, +0.1596), (0.9945, +0.1085), (0.9974, +0.0573),
    (0.9993, +0.0060), (1.0000, -0.0453), (0.9990, -0.0965), (0.9957, -0.1477),
    (0.9891, -0.1986), (0.9779, -0.2486), (0.9604, -0.2968), (0.9348, -0.3411),
    (0.8946, -0.3719), (0.8442, -0.3794), (0.7936, -0.3721), (0.7478, -0.3495),
    (0.7055, -0.3204), (0.6646, -0.2894), (0.6243, -0.2577), (0.5833, -0.2269),
    (0.5411, -0.1977), (0.4976, -0.1706), (0.4510, -0.1492), (0.4019, -0.1345),
    (0.3516, -0.1242), (0.3008, -0.1173), (0.2496, -0.1135), (0.1984, -0.1128),
    (0.1471, -0.1152), (0.0961, -0.1207), (0.0454, -0.1282), (0.0000, -0.1503),
])


spine = Profile(
    SPINE_POINTS,
    name="spine",
    # The widest point of the head, and the stand-off radius to use there.
    # Anything arriving at a spine comes in close to head-on, so the radius is
    # nearer the tip distance (0.18) than the half-height.
    head_t=0.82,
    head_r=0.28,
    # The constant-width neck: the span that absorbs `extend`, letting a spine
    # stand further off its branch while the head keeps the size `size` gave
    # it. This is the knob that stops heads touching on a densely spined
    # dendrite.
    stretch=(0.0, 0.35),
    source="traced from a hand drawing (Dean Geckt), normalised",
)

register("spine", spine)

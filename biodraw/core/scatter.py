"""Placing things *inside* a shape, rather than along a path.

`Branch.decorate` covers everything that grows out of a line — spines on a
dendrite, thorns on a stem, microvilli on a surface. What it cannot say is
"nine of these, loose in there": organelles in a cytoplasm, vesicles in a
bouton, granules in a mast cell, nuclei in a syncytium. That is a different
question — no host curve, no ordering, and the constraint is *separation*
rather than spacing.

Nothing here knows what an organelle is. It takes a closed outline and hands
back points inside it, which is as domain-neutral as the rest of the core.

Determinism
-----------
Every figure in this library must regenerate byte-identically, so the sampling
is driven by an explicit `seed` and never by the global `np.random` state. The
same seed gives the same points forever; a different one is a different
drawing, not a different rendering of the same one.
"""

import numpy as np

__all__ = ["scatter_in"]


def scatter_in(outline, n, seed=0, min_sep=0.0, margin=0.0, exclude=(),
               exclude_margin=0.0, tries=60):
    """`n` points inside `outline`, no two closer than `min_sep`.

      outline         a closed (N, 2) ring or a `matplotlib.path.Path`.
      n               how many points to place.
      seed            an int, or a `numpy.random.Generator` to draw from —
                      the latter so a shape scattering several populations
                      keeps them all on one reproducible stream.
      min_sep         the closest two placed points may come, in the
                      outline's own units. This is the knob that makes a
                      scatter read as *distributed* rather than clumped;
                      uniform sampling alone produces visible pairs almost
                      every time.
      margin          how far inside the wall a point must stay. Measured to
                      the outline itself, not to its bounding box, so it holds
                      just as well in a corner as on a flat.
      exclude         outlines the points must avoid — the nucleus, for
                      anything scattered in a cytoplasm.
      exclude_margin  clearance from those, same units.
      tries           how many batches to draw before giving up.

    Raises `ValueError` if `n` will not fit. That is deliberate: silently
    placing four organelles when nine were asked for makes the drawing a
    claim about the cell that the code did not make, and a figure is not the
    place to find that out. The message says how many it managed, which is
    usually enough to pick a workable `min_sep`.

    Returns an (n, 2) array, in the order the points were accepted.
    """
    want = int(n)
    if want <= 0:
        return np.zeros((0, 2), dtype=float)

    rng = (seed if isinstance(seed, np.random.Generator)
           else np.random.default_rng(seed))
    ring, path = _ring_and_path(outline)
    blocked = [_ring_and_path(e) for e in exclude]

    lo, hi = ring.min(axis=0), ring.max(axis=0)
    # Sample the bounding box and throw away what lands outside. Cheap for the
    # roundish bodies this is used on, where the box is mostly shape; a long
    # thin diagonal outline would want something better, and does not exist
    # here yet.
    batch = max(4 * want, 32)

    kept = []
    for _ in range(int(tries)):
        cand = lo + rng.random((batch, 2)) * (hi - lo)
        cand = cand[path.contains_points(cand)]
        if margin > 0 and len(cand):
            cand = cand[_distance_to(cand, ring) >= margin]
        for e_ring, e_path in blocked:
            if not len(cand):
                break
            cand = cand[~e_path.contains_points(cand)]
            if exclude_margin > 0 and len(cand):
                cand = cand[_distance_to(cand, e_ring) >= exclude_margin]

        for p in cand:
            # Greedy in draw order: accept a point unless it crowds one
            # already down. Not a Poisson-disc sampler and does not need to
            # be — a dozen organelles in a cell body is not a packing problem.
            if kept and min_sep > 0:
                if np.min(np.linalg.norm(np.asarray(kept) - p,
                                         axis=1)) < float(min_sep):
                    continue
            kept.append(p)
            if len(kept) == want:
                return np.asarray(kept, dtype=float)

    raise ValueError(
        f"could not place {want} points at min_sep={min_sep:g} inside this "
        f"outline; got {len(kept)}. Lower `min_sep`, lower the count, or "
        f"give the shape more room."
    )


def _ring_and_path(outline):
    """`(vertices, Path)` for either form of outline.

    A `Path` carries Bezier control points in `.vertices` that do not lie *on*
    the curve, so measuring a margin against them would be quietly wrong near
    every fillet. `to_polygons` flattens the curve first, which is what the
    distance test actually wants.
    """
    from matplotlib.path import Path

    if isinstance(outline, Path):
        polys = outline.to_polygons()
        ring = np.vstack(polys) if polys else outline.vertices
        return np.asarray(ring, dtype=float), outline
    ring = np.asarray(outline, dtype=float)
    return ring, Path(ring, closed=True)


def _distance_to(points, ring):
    """Distance from each point to the nearest *edge* of a closed ring.

    Nearest-vertex would do on a densely sampled outline and is wrong on a
    coarse one — a bowed quadrilateral has a handful of samples per edge, and
    measuring to those overstates the clearance by most of the sample spacing
    exactly where a margin matters. Projecting onto the segments costs one
    (points x edges) array and is exact.
    """
    a = np.asarray(ring, dtype=float)
    b = np.roll(a, -1, axis=0)
    ab = b - a
    denom = np.einsum("mj,mj->m", ab, ab)
    denom = np.where(denom > 0, denom, 1.0)          # skip repeated vertices
    ap = np.asarray(points, dtype=float)[:, None, :] - a[None, :, :]
    t = np.clip(np.einsum("nmj,mj->nm", ap, ab) / denom, 0.0, 1.0)
    closest = a[None, :, :] + t[:, :, None] * ab[None, :, :]
    return np.linalg.norm(np.asarray(points, dtype=float)[:, None, :]
                          - closest, axis=2).min(axis=1)

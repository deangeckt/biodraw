"""An epithelium: a row of cells standing side by side on a membrane.

Where `Blob` is one cell that is not one contour, this is many cells that must
not become one. Two neighbours handed to `render_hollow` in a single call fuse
into a single long cell with no wall between them — the union does exactly what
it is asked to. So every cell here is its own `Layer`, and the wall between two
of them is two walls with a hairline of page between: `gap`.

That is not a workaround, it is what an epithelium looks like. Cells in a sheet
are drawn with a visible boundary precisely because the boundary is the point —
tight junctions, polarity, what crosses and what does not.

Curvature is the other half. `curve_deg` bends the row around an arc, which is
how the same object draws a flat sheet, a villus, and — at a full turn — the
ring of cells round a duct in cross-section. Nothing about that is
neuron-shaped or cell-shaped; it is a row of bodies on an arc.
"""

import numpy as np

from ..core.anchor import Anchor, AnchorSet
from ..core.branch import Branch
from ..core.paths import bowed_ring, rounded_polygon, superellipse, tube
from ..core.shape import Layer, Shape
from ..style.palette import get as get_palette

__all__ = ["Sheet"]


class Sheet(Shape):
    """A row of epithelial cells.

    The row
      cells            how many.
      cell_w           the pitch — one cell's width at the *basal* line, in
                       local units.
      height           basal surface to apical surface.
      gap              the page left between neighbours, x `cell_w`. Cannot
                       be 0 for free: at 0 the two cells' walls land on the
                       same line and each pass-2 fill erases half of the
                       other's, leaving a half-weight join. A hairline is
                       both cheaper and more honest — an epithelium is drawn
                       with its boundaries showing.
      taper            apical pitch as a multiple of basal, *on top of*
                       whatever the curvature already does. 1.0 is columnar;
                       below it the cells wedge inward.
      curve_deg        total angle the row subtends. 0 is a flat sheet;
                       positive bows it so the apical surface is on the
                       outside (a villus); negative puts the apical surface
                       on the inside (a duct or an acinus). +/-360 closes the
                       ring exactly.
      bow_side         bow on the lateral walls, x their length. Positive
                       bulges a cell out against its neighbours.
      bow_end          the same for the apical and basal surfaces.
      corner_r         corner fillet, in local units.

    Nuclei
      nucleus          nuclear semi-axis, x `cell_w`. 0 for none.
      nucleus_at       its height up the cell, as a fraction. Basal by
                       default (0.32), which is what a columnar epithelium
                       actually looks like and is the cheapest single cue
                       that the drawing has a polarity.
      nucleus_aspect   the nucleus' own shape.
      nucleus_jitter   how far each nucleus wanders from that height, x the
                       cell height. A row of nuclei at identical heights
                       reads as printed rather than as tissue.
      height_jitter    how far each cell's own apical surface departs from
                       `height`, x `height`. Same rule as the nuclei and the
                       same reason: a row of identical cells is a row of
                       copies, and the eye finds a perfectly level apical
                       surface before it finds anything else in the drawing.
      seed             fixes both jitters. Same seed, same sheet, forever.

    Brush border
      microvilli       per cell, on the apical surface. Short `Branch` tubes,
                       so they fuse with their own cell and no other.
      microvilli_len / microvilli_width
                       x `cell_w`.

    Basement membrane
      basement         draw the band the sheet stands on.
      basement_w       its thickness, x `cell_w`.
      basement_gap     how far below the basal surface it sits, x `cell_w`.
      basement_over    how far it runs past the end cells, x `cell_w`. A
                       membrane stopping exactly at the last cell reads as
                       the edge of the tissue rather than as a section
                       through it.
    """

    edge = get_palette()["ink"]

    # The membrane is not a cell and must not be mistaken for one, so it takes
    # grey — see `style.palette` on what is neither an identity nor a claim.
    MEMBRANE_C = get_palette()["neutral"]
    # Nuclei are washed harder than cytoplasm for the same reason as in `Blob`:
    # denser, not different.
    NUCLEUS_WASH = 0.30

    def __init__(self, cells=5, cell_w=0.46, height=1.0, gap=0.06,
                 taper=1.0, curve_deg=0.0,
                 bow_side=0.018, bow_end=0.020, corner_r=0.05,
                 nucleus=0.30, nucleus_at=0.32, nucleus_aspect=1.15,
                 nucleus_jitter=0.05, height_jitter=0.04, seed=0,
                 microvilli=0, microvilli_len=0.30, microvilli_width=0.10,
                 basement=True, basement_w=0.07, basement_gap=0.03,
                 basement_over=0.35,
                 at=(0.0, 0.0), scale=1.0, rotate_deg=0.0, geom_kw=None):
        super().__init__(at=at, scale=scale, rotate_deg=rotate_deg)
        self.cells = int(cells)
        self.cell_w = float(cell_w)
        self.height = float(height)
        self.gap = float(gap)
        self.taper = float(taper)
        self.curve_deg = float(curve_deg)
        self.bow_side = float(bow_side)
        self.bow_end = float(bow_end)
        self.corner_r = float(corner_r)

        self.nucleus = 0.0 if nucleus is None else float(nucleus)
        self.nucleus_at = float(nucleus_at)
        self.nucleus_aspect = float(nucleus_aspect)
        self.nucleus_jitter = float(nucleus_jitter)
        self.height_jitter = float(height_jitter)
        self.seed = int(seed)

        self.microvilli = int(microvilli)
        self.microvilli_len = float(microvilli_len)
        self.microvilli_width = float(microvilli_width)

        self.basement = bool(basement)
        self.basement_w = float(basement_w)
        self.basement_gap = float(basement_gap)
        self.basement_over = float(basement_over)
        self.geom_kw = dict(geom_kw or {})

    # -- the arc the row stands on -----------------------------------------

    @property
    def closed_ring(self):
        """Whether the row comes back round to meet itself."""
        return abs(abs(self.curve_deg) - 360.0) < 1e-9

    @property
    def arc(self):
        """`(pitch angle, basal radius, centre)` — or `None` when flat.

        The radius is set by the pitch: a chord of `cell_w` subtending the
        pitch angle. Deriving it rather than taking it as a knob is what makes
        `curve_deg=-360` close exactly, whatever the cell count, instead of
        leaving a wedge of missing tissue for the caller to tune away.
        """
        if self.curve_deg == 0.0:
            return None
        theta = np.deg2rad(self.curve_deg) / self.cells
        r = self.cell_w / (2.0 * np.tan(theta / 2.0))
        return theta, r, np.array([0.0, -r])

    def _frames(self):
        """`(basal midpoint, across, up, arc radius or None)` per cell.

        `up` is the cell's own outward direction — straight up on a flat
        sheet, radial on a curved one — and `across` completes a right-handed
        pair with it, so one local quad definition serves both cases.
        """
        n, half = self.cells, (self.cells - 1) / 2.0
        curved = self.arc
        if curved is None:
            for _ in range(n):
                yield (np.array([(_ - half) * self.cell_w, 0.0]),
                       np.array([1.0, 0.0]), np.array([0.0, 1.0]), None)
            return

        theta, r, centre = curved
        for k in range(n):
            phi = (k - half) * theta
            up = np.array([np.sin(phi), np.cos(phi)])
            across = np.array([np.cos(phi), -np.sin(phi)])
            yield centre + r * up, across, up, r

    def _widen(self, radius, h):
        """How much longer this cell's apical surface is than its basal one.

        On an arc the cells fan, so the apical surface is longer by exactly
        (r + h) / r. Widening each cell by that is what keeps `gap` even from
        bottom to top; leaving it at 1 opens a wedge between every pair, which
        reads as the tissue tearing. Taken per cell rather than once for the
        row, because `height_jitter` means the cells no longer share an h.
        """
        if radius is None:
            return 1.0
        widen = (radius + h) / radius
        if widen <= 0:
            raise ValueError(
                f"curve_deg={self.curve_deg:g} bends the row tighter than "
                f"height={self.height:g} allows — the apical surface passes "
                f"through the centre of the arc. Reduce the height, widen "
                f"the cells, or bend less far.")
        return widen

    @staticmethod
    def _place(local, origin, across, up):
        """Local cell coordinates into sheet coordinates."""
        p = np.atleast_2d(np.asarray(local, dtype=float))
        return origin + np.outer(p[:, 0], across) + np.outer(p[:, 1], up)

    # -- geometry ----------------------------------------------------------

    def _branch_kw(self, **over):
        # A microvillus is a stub. Under one cycle of waver, for the same
        # reason `Blob` gives its protrusions one: cycles do not scale with
        # length, so a `wave_n` tuned on a dendrite corkscrews on a stub.
        kw = dict(bend=0.05, wave_amp=0.010, wave_n=0.6, wave_phase=0.20,
                  n_pts=20)
        kw.update({k: v for k, v in self.geom_kw.items() if k in kw})
        kw.update(over)
        return kw

    def _geometry(self):
        """One dict per cell, plus the membrane under the row."""
        rng = np.random.default_rng(self.seed)
        gap = self.gap * self.cell_w
        out = []
        for k, (origin, across, up, radius) in enumerate(self._frames()):
            h = self.height * (1.0 + rng.uniform(-1.0, 1.0)
                               * self.height_jitter)
            hw_b = 0.5 * (self.cell_w - gap)
            hw_a = 0.5 * (self.cell_w * self._widen(radius, h) * self.taper
                          - gap)
            if hw_a <= 0:
                raise ValueError(
                    f"gap={self.gap:g} and taper={self.taper:g} leave cell "
                    f"{k} no apical width at all. Lower the gap or raise the "
                    f"taper.")
            out.append({
                "outline": self._cell_outline(hw_b, hw_a, h, origin, across,
                                              up),
                "nucleus": self._nucleus(h, origin, across, up, rng),
                "microvilli": self._microvilli(hw_a, h, origin, across, up),
                "origin": origin, "across": across, "up": up, "height": h,
                "hw_basal": hw_b, "hw_apical": hw_a,
            })
        return {"cells": out, "membrane": self._membrane()}

    def _cell_outline(self, hw_b, hw_a, h, origin, across, up):
        """One cell, as a bowed and filleted quadrilateral.

        Listed counter-clockwise from the basal-left corner, which is the
        winding `bowed_ring` reads "outward" from — get it backwards and every
        bow pulls the wall inward instead.
        """
        # The bow bulges the lateral wall *outward* by `bow_side` x the wall's
        # own length, which comes straight out of the gap: at the defaults
        # that is 0.018 a side against a gap of 0.0276, so neighbours
        # overlapped by 0.008 and `gap` did not mean what it says. Setting the
        # quad in by the bulge puts the widest point of the finished wall back
        # on the nominal half-width. Exact while the cell is columnar, where
        # the wall is vertical and its outward normal horizontal; on a wedge
        # the normal tilts and this is a hair conservative, which is the safe
        # direction. A negative bow pinches inward and costs nothing.
        slant = float(np.hypot(hw_a - hw_b, h))
        bulge = max(self.bow_side, 0.0) * slant
        hw_b, hw_a = hw_b - bulge, hw_a - bulge
        quad = [(-hw_b, 0.0), (hw_b, 0.0), (hw_a, h), (-hw_a, h)]
        ring = bowed_ring(quad, [self.bow_end, self.bow_side,
                                 self.bow_end, self.bow_side])
        return rounded_polygon(
            self.to_world(self._place(ring, origin, across, up)),
            self.corner_r * self.scale)

    def _nucleus(self, h, origin, across, up, rng):
        if self.nucleus <= 0:
            return None
        nr = self.nucleus * self.cell_w
        jitter = self.nucleus_jitter * h
        centre = np.array([rng.uniform(-1.0, 1.0) * jitter * 0.5,
                           self.nucleus_at * h
                           + rng.uniform(-1.0, 1.0) * jitter])
        ring = centre + superellipse(nr, nr * self.nucleus_aspect, 2.2,
                                     wobble=0.03, wobble_n=3,
                                     wobble_phase=0.35)
        return self.to_world(self._place(ring, origin, across, up))

    def _microvilli(self, hw_a, h, origin, across, up):
        """The brush border on one cell's apical surface.

        Rooted a tube-width back inside the cell so the flat base is buried
        under its own fill, and aimed along that cell's own `up` rather than
        along the local radius — on a curved sheet the two differ, and letting
        each villus follow the radius fans them apart at the ends of a cell,
        which reads as a frayed edge rather than as a border.
        """
        n = self.microvilli
        if n <= 0:
            return []
        w = self.microvilli_width * self.cell_w
        # 0.72 keeps the outermost villus clear of the corner fillet, where a
        # tube rooted on the round would stick out sideways through the wall.
        xs = (np.linspace(-hw_a * 0.72, hw_a * 0.72, n) if n > 1
              else np.zeros(1))
        out = []
        for j, x in enumerate(xs):
            br = Branch(origin=(x, h - w), direction=(0.0, 1.0),
                        length=self.microvilli_len * self.cell_w + w,
                        **self._branch_kw(bend=0.05 * (-1) ** j))
            centre = self._place(br.centre, origin, across, up)
            out.append({"centre": centre, "width": w,
                        "tip": centre[-1], "dir": up})
        return out

    def _membrane(self):
        """The band the sheet stands on.

        A closed ring has to be a real annulus — outer ring one way, inner
        ring the other, so the non-zero winding rule leaves the lumen empty.
        Building it as one polygon that walks out and back instead leaves a
        radial seam where the two ends meet, and pass 1 inks half of it.
        """
        if not self.basement:
            return None
        from matplotlib.path import Path

        w = self.basement_w * self.cell_w
        drop = self.basement_gap * self.cell_w
        over = self.basement_over * self.cell_w
        curved = self.arc

        if curved is None:
            half = self.cells * self.cell_w / 2.0
            line = np.column_stack([np.linspace(-half - over, half + over, 24),
                                    np.full(24, -drop)])
            return Path(self.to_world(tube(line, 0.5 * w)), closed=True)

        theta, r, centre = curved
        span = abs(theta) * self.cells
        # Overhang as an angle, so it is the same arc length at any radius.
        pad = 0.0 if self.closed_ring else over / abs(r - drop)
        phis = np.linspace(-span / 2 - pad, span / 2 + pad, 160)

        def ring(radius):
            return centre + radius * np.column_stack([np.sin(phis),
                                                      np.cos(phis)])

        sign = np.sign(r)
        outer = ring(r - sign * drop)
        inner = ring(r - sign * (drop + w))
        if self.closed_ring:
            return Path.make_compound_path(
                Path(self.to_world(outer), closed=True),
                Path(self.to_world(inner[::-1]), closed=True))
        return Path(self.to_world(np.vstack([outer, inner[::-1]])),
                    closed=True)

    # -- rendering ---------------------------------------------------------

    def _layers(self):
        """The membrane, then one layer per cell and one per nucleus.

        Every cell is its own group on purpose: hand two neighbours to one
        `render_hollow` call and the union dissolves the wall between them
        into a single long cell. A cell's own microvilli *do* belong in its
        group — they should fuse with it, and with nothing else.
        """
        g = self.geometry
        layers = []
        if g["membrane"] is not None:
            layers.append(Layer(closed=[g["membrane"]], name="membrane",
                                edge=self.MEMBRANE_C))
        for k, cell in enumerate(g["cells"]):
            layers.append(Layer(
                closed=[cell["outline"]],
                open_=[tube(m["centre"], 0.5 * m["width"], open_end=True)
                       for m in cell["microvilli"]],
                name=f"cell{k}"))
            if cell["nucleus"] is not None:
                layers.append(Layer(closed=[cell["nucleus"]],
                                    name=f"cell{k}.nucleus",
                                    fill_alpha=self.NUCLEUS_WASH))
        return layers

    # -- anchors -----------------------------------------------------------

    def _anchors(self):
        """Apical and basal surfaces, the junction between each pair of
        neighbours, and every nucleus."""
        g = self.geometry
        out = AnchorSet()

        for k, cell in enumerate(g["cells"]):
            o, across, up = cell["origin"], cell["across"], cell["up"]
            apical = self._place([(0.0, cell["height"])], o, across, up)[0]
            out.append(Anchor(self.to_world(apical), self.dir_to_world(up),
                              "apical", cell=k))
            out.append(Anchor(self.to_world(o), self.dir_to_world(-up),
                              "basal", cell=k))
            if cell["nucleus"] is not None:
                out.append(Anchor(cell["nucleus"].mean(axis=0),
                                  self.dir_to_world(up), "nucleus", cell=k))

        # One per boundary, at the apical end of the shared wall — which is
        # where a tight junction sits, and so where a label about one is
        # pointing. The last boundary only exists if the row closed.
        pairs = list(zip(g["cells"], g["cells"][1:], strict=False))
        if self.closed_ring and self.cells > 1:
            pairs.append((g["cells"][-1], g["cells"][0]))
        for k, (left, right) in enumerate(pairs):
            a = self._place([(left["hw_apical"], left["height"])],
                            left["origin"], left["across"], left["up"])[0]
            b = self._place([(-right["hw_apical"], right["height"])],
                            right["origin"], right["across"], right["up"])[0]
            mid = 0.5 * (a + b)
            out.append(Anchor(self.to_world(mid),
                              self.dir_to_world(left["up"] + right["up"]),
                              "junction", rank=k))
        return out

    def __repr__(self):
        return (f"Sheet(cells={self.cells}, curve_deg={self.curve_deg:g}, "
                f"microvilli={self.microvilli}, "
                f"at=({self.at[0]:.3g}, {self.at[1]:.3g}), "
                f"scale={self.scale:g})")

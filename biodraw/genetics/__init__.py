"""Genetic constructs and the proteins they encode.

The fourth domain package, and the first one whose parts list came off a
figure rather than out of the field: chemically and light inducible expression
systems, figure 1 of doi.org/10.1016/j.tibtech.2023.03.007. That matters
because the guess had been wrong. `docs/PLAN.md` argued genetics on double
helices, plasmid maps and exon/intron structure, and the figure contains none
of them — it is **linear constructs and protein complexes**, which is a
different parts list reached by the same reasoning.

Two halves, and one core primitive underneath:

* `core.Track` lays parts along an axis, each consuming its own width. It is
  not a genetics primitive at all — a protein domain map, a chromosome
  ideogram, a gene model and a timeline are the same object with different
  glyphs — which is why it lives in the core and this package only supplies
  the glyphs.
* `Repeat`, `Promoter`, `CDS`, `Terminator` are those glyphs, in SBOL
  Visual's vocabulary, and `Protein` is the product: a lobed body with named
  domains stuck to it.

Everything a reader will want to change is a **count or a length**: how many
repeats in the operator, how long the coding sequence, how many domains on
the protein, how far open the clamshell. That is the roster test in
`docs/PLAN.md` — a stock asset cannot know your repeat number — and it is why
this category exists where a proteins category did not.

What is deliberately absent
---------------------------
No text. A construct is covered in labels (`GOI`, `35S`, `4xUAS`) and not one
of them is drawn here: every glyph carries a `label` string and the track
exposes a `label` anchor above it, so the figure writes its own text where it
wants it. Same call as everywhere else — the library draws, the figure makes
the claims — and `annotate.label` will render them against these anchors when
milestone 8 lands.

No ligand dot, no light cone, no strike-through cross. A filled circle for
`Cu2+` is a mark at an anchor (`Protein.anchor('cleft')`), and a red cross
over an arrow is a claim in a colour the palette deliberately does not carry.
"""

from ..core.track import Glyph, Track
from .glyphs import CDS, Promoter, Repeat, Terminator
from .protein import Protein

__all__ = ["CDS", "Glyph", "Promoter", "Protein", "Repeat", "Terminator",
           "Track"]

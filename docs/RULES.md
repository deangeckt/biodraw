# Rules

The rules everything in this repository is checked against — how a page is
written, how a shape is drawn, what an image is allowed to weigh, and what a
skill must contain. They are gathered here rather than scattered through the
milestone history because they are the part that is still live: each one
arrived as a specific complaint about one figure or one page, and each turned
out to govern everything.

**The ones written as numbers are the ones that hold.** Documentation rule 2
sat here as agreed, undisputed prose for three sessions while the site grew to
a hundred words per picture. Nothing here has ever been fixed by writing a
rule down more firmly — only by turning it into a check that fails a build.
Where a rule has an enforcing check, the check is named beside it.

| enforced by | rules |
|---|---|
| `check_catalog` in `tools/build_site.py` | documentation 1, 6, 7 |
| `check_readme` in `tools/build_site.py` | the front-door rule |
| `build_gallery.py` ink-fraction report | the frame rule in the weight budget |
| [`skills/review-a-drawing`](../skills/review-a-drawing/SKILL.md) | drawing 1, 2, 3, 5 |
| nothing yet | documentation 5, 8, 9, 10; drawing 4, 6, 7 |

For why the library is shaped this way at all, see [SCOPE.md](SCOPE.md).

## Documentation rules

These apply to every page of the gallery, every example folder, and the
main README. Rules 1 and 7 are now **enforced by the build**: a gallery
section is `images` then `body` then `code`, and `tools/build_site.py` has no
field that puts a code block above a picture — and `check_catalog` refuses a
page that exceeds the word, snippet or caption budget, or that carries a
section with no drawing in it. Rule 2 spent three sessions as prose everyone
agreed with while the site grew to a hundred words per picture, which is the
argument for the numbers in rule 7.

The main `README.md` is a **front door, not a second copy**: it says what the
library is, shows the breadth, and links to the catalog. It had drifted into
carrying the index's own pitch and skills paragraph verbatim, so the prose it
duplicated is gone and the one number it still quotes — the catalog's size —
is now checked by `check_readme` rather than trusted. Prose cannot be
diffed against the site automatically; a count can, and a stale count is the
form the drift took last time.

1. **Image first, code second — always.** A reader should see what a thing
   looks like before being shown how to make it. Never open a section with a
   code block; open it with the picture the code produces. If a section has no
   image worth showing, ask whether it needs the code either.
2. **More images than prose.** The product is drawings. A wall of text about a
   drawing library is a failure of the library.
3. **Snippets use keyword arguments with meaningful names.**
   `render_hollow(ax, [part], "#FFD9D9", "#FF0000", 2.0)` tells a reader
   nothing. Every argument in documentation is named, and anything non-obvious
   carries a trailing comment:

   ```python
   render.render_hollow(
       ax=ax,
       parts=[outline],
       fill="#FFD9D9",      # the interior wash
       edge="#FF0000",      # the wall
       wall_lw=2.0,         # wall thickness, in points
   )
   ```

   This doubles as an API test: if a call cannot be written readably with
   named arguments, the signature is wrong.
4. **Every example folder carries a blueprint** — the construction figure, so
   the maths is visible and not just asserted.
5. **Variants are the unit of documentation.** A reader learns more from
   eighteen small cells differing in one knob each than from one large cell
   and a paragraph about what the knob does. Fill a page with icon grids, not
   with a handful of portraits.
6. **A public page shows only what `pip install` can do.** Every detail
   page carried a *Rebuilding these drawings* section ending in
   `python tools/build_gallery.py pyramidal` — a command that presumes a
   clone of this repository, on a page written for someone who has installed
   the library. Maintainer instructions belong in `CONTRIBUTING.md`.
   `tools/build_site.py` now refuses to build a snippet naming `tools/`,
   `build_gallery` or `git`. The positive form matters more than the
   prohibition: the reader's next step is `pip install biodraw` and pointing
   an agent at the skills, so that is what the page should say.
7. **A catalog page shows drawings; every section earns its place with one.**
   The gallery went live and the verdict was *"its still too much text, its
   should be more catalog then code-snippet."* Measured: 6,662 words and 352
   lines of code across 66 drawings — about a hundred words per picture, and
   up to six snippets on a single page. Ten sections carried no image at all.

   A section with no drawing is prose that wandered onto a catalog. It has
   two proper homes and neither is the page: if it explains a picture, it is
   a **caption on that picture**; if it explains a number, it is a **tuning
   comment** next to the number, where the person changing it will actually
   meet it. The check that this loses nothing is cheap and worth running —
   before cutting the pyramidal page's paragraph on why `shaft` anchors sit
   below the first spine, that reasoning was found already written at
   `biodraw/neuro/pyramidal.py:120`.

   There is **one snippet per page**: the one that draws the thing the page
   is about. Five snippets showing five keyword combinations is five copies
   of one snippet, and the variant grid already said it better.

   Numbers, enforced by `check_catalog` in `tools/build_site.py`: ≤150 words
   of prose per page, ≤1 code block, ≤20 words per caption, and no imageless
   section. They took the site to 3,227 words and 10 snippets with all 66
   drawings still on it. Rule 2 said "more images than prose" and was true
   and unenforced for three sessions — which is the whole argument for
   writing a rule as a number.

8. **Hover may affirm, never replace.** The gallery's cards first cross-faded
   each portrait into that example's variant sheet on hover. It read as the
   card changing identity: two cards could not be compared, and what you
   clicked was not what you had been looking at. Hover is allowed to say
   *this one* — a border, a colour, a lift. The moment it substitutes
   different content, the reader has lost the thing they were looking at in
   order to see something the page could simply have shown. If a picture is
   worth putting on the index, put it on the index.

9. **A card is a drawing; a property of every drawing is not a card.** The
   drawing *styles* page — hollow against skeleton, washed against solid, in
   each palette — shipped as one more card in the grid, and the verdict was
   *"neuron style is great! ... but i dont think it should be in a card,
   rather, somewhere else, which is more of a 'global' or parallel to the
   main page cards."* A card invites comparison with its neighbours, and
   comparing "styles" with "bacteria" is a category error: every other card
   *has* styles.

   So a content module may set `standalone=True`. The page is still built and
   still budgeted; it leaves the grid and appears instead in the masthead of
   every page and as a full-width band beside the grid — both generated from
   the same `PAGE` dict, so there is no second copy to drift out of step. The
   general form: **ask whether the thing is one of the items or a property of
   all of them**, and let the layout say which.

   **The third answer, added in session 8: neither — it is not in the catalog
   at all.** `annotate` (labels and scale bars) shipped as a second standalone
   page and the verdict was *"i see the page: 'Labels & scale' its not
   needed."* Card-or-standalone was a false choice, and the question that
   separates them is not *how wide is its scope* but **does the library draw
   it**:

   - *Drawing styles* earns a page because it changes how every drawing
     **looks**. The cells on it are the subject, shown varying.
   - *Labels & scale* did not, because `annotate` changes what a figure
     **says**. The cell on that page was a backdrop for text a figure author
     was going to write anyway — an API reference wearing catalog clothes.

   A utility's home is the API surface: its own docstring, `AGENTS.md`, and
   the skills. It is documented best by the catalog pages that quietly
   **use** it — `bd.scalebar` on the cell atlas, `bd.label` on three
   blueprints — which is better evidence that it works than a page built to
   show it off. This governs everything still unbuilt on the roadmap:
   `bd.panels`, `style.use`, `bd.catalog` and `bd.check` are all utilities,
   and **none of them gets a catalog page by default**.

10. **A name a reader would search for gets its own card.** Bipolar, granule,
    Purkinje and astrocyte cells shared one card called *Neuron types*, and
    nobody looking for a Purkinje cell searches for "neuron types". Each is a
    card now, and what stayed behind is the argument none of them could carry
    alone — that they are one body plan at five settings — on a *Radial body
    plan* card that doubles as the entry point for a cell the library does
    not name.

    The cost is real (four folders, twelve images) and the rule is not "one
    card per class". It is: if a reader arrives with a **name**, the catalog
    should contain that name. The corollary ran the other way the same day —
    *wiring* and *circuit motifs* were two cards for one subject, and a
    reader wanting "how do I draw a projection from A to B" could not tell
    which held it, so they are one card over two example folders. A page and
    a build folder are no longer required to be the same thing.

## Drawing rules

What separates a drawing from a diagram of a drawing. Each of these arrived as
a specific complaint about one figure and turned out to govern everything.

1. **A repeated part must not repeat exactly.** Two fork daughters reflected
   about their trunk, two basal legs of equal length, eight microvilli on
   exactly even slots, a row of cells with a perfectly level apical surface —
   each reads as a symbol *for* the thing rather than as the thing. Anything
   the library produces in pairs or in runs must differ in the ways real ones
   differ, **by default and not on request**, and the variation must be seeded
   so the figure still regenerates byte-identically.

   The distinction that matters is texture versus structure. Mirroring a
   traced profile across a branch is right — it stops N decorations sharing
   one asymmetry (`Profile.place(mirror=...)`). Mirroring a *bifurcation* is
   wrong, because symmetry there is a claim, and a false one: real daughters
   differ in calibre, length and angle, and the three move together — the
   thicker daughter runs further and turns less off the parent's axis while
   the thin one branches off wide. One ratio should drive all of them, or the
   fork reads as three knobs that happen to be set.

2. **A cosmetic term that does not scale with length will end up driving
   something structural.** The waver that makes a branch look drawn is a sine
   with a fixed *cycle count*, so halving a branch's length doubles its
   frequency. An apical forked at 0.25 drove its trunk at four times the rate
   the drawing was tuned at and swung it 44° off axis against a reference of
   22° — which is the "twiddle" visible above the soma. Cycle counts, fixed
   offsets and fixed angles are all suspect the moment they are shared between
   branches of different lengths; prefer a wavelength (`Branch(wave_per=...)`)
   or a fraction. This is the same failure as keying a fork off the local
   tangent, and it is now the second time it has been found.

3. **A count spread over a length is a density.** The same failure as rule 2,
   one level up: `spines=9` on an apical means nine *at the reference length*,
   and forking the apical halves the trunk. Sharing the count crams nine
   spines into half the dendrite and the tuft becomes a mass of touching
   heads. Anything counted along a branch — spines, boutons, microvilli,
   protrusions — has to be derived from a per-unit rate, not carried across
   branches of different lengths.

4. **Prefer the schematic where the realistic one competes for attention.** A
   "realistic" axon was built — a tapered tube with swellings — and removed.
   At the size an axon appears in a circuit panel it reads as a fat beaded
   worm and pulls the eye away from the cells it exists to connect. A line
   with a mark on the end says the same thing and is parsed instantly. The
   test is not "is this anatomically fuller" but "does the reader get the
   claim faster".

5. **When something looks wrong, measure it before changing it.** Neither of
   the two above was found by looking. Both were found by computing one number
   — cycles per unit length, degrees off axis — and comparing it against the
   configuration the drawing was tuned in. An agent cannot see the figure, and
   a human describing what is wrong with one is describing a symptom.

6. **A reference is a parts list and a set of proportions.** *"for animals,
   microscopy, genetics and so on — you can google and grab text book images,
   take the basic ones and add them to the catalog. use very simple drawings,
   not complex realistic images, sometimes an outline is even enough."*

   Look at the reference, write down what the parts are and how big each is
   relative to the others, then build the shape parametrically from the core.
   Nothing is traced off a downloaded figure and no downloaded figure is
   committed — which is the same rule this repo reached from the other
   direction (*a reference figure is a source of capabilities, not a thing to
   reproduce*), and it is also the only version that gives a shape knobs.
   `examples/summary_figure/` was built by ignoring this, reproduced its
   reference closely, and was deleted the same session.

7. **Draw the schematic, not the portrait.** A mouse is a silhouette; a
   coverslip is a rounded square; an organelle is an outline. This is rule 4
   extended from axons to whole organisms: if an outline reads at figure size,
   the detail was costing bytes and attention for nothing.

   The sharper form, from the zebrafish that shipped with three stripes and
   lost them: **a capability that only looks right at a size nobody views it
   at is not a capability.** The stripe count was the documented reason the
   fish was parametric, and it still went. The argument for a feature is not
   evidence that the drawing works.

   The corollary is about **projection**, and it is part of the parts list. A
   fly drawn from the side hides both the eyes and the wings — the two things
   that say *fly* — and no amount of tuning fixes the wrong view. Identity
   lives in the silhouette, so draw the view that puts the identifying
   features in it.

## The image weight budget

**The budget is a publication constraint, not a development one.** It was
imposed before anything needed debugging, and the cost showed up immediately:
at 100 dpi a sheet of eighteen cells gives each cell about 55 pixels, which is
enough to see that a cell was drawn and not enough to see whether it was drawn
*right*. Two real defects sat in the committed images for a whole session
because nobody could see them. So `biodraw.io.QUALITY` holds three profiles —
`compact` (what a published repo carries), `review` (the default while this one
is not published) and `debug` (uncapped, for looking at one shape hard) — and
`DEFAULT_QUALITY` is the single line to flip back before going public.

Worth recording, since the original numbers implied otherwise: **`dpi` is the
binding constraint, not `max_width`.** A three-column sheet at `cell_in=1.5`
comes out 450 px wide, so the 1000 px cap never engages and only the dpi
matters. Going from compact to review roughly doubles the linear resolution
and costs about 2.3x the bytes.

This library is heading for hundreds of examples with thousands of variants
between them. Documentation images are the only thing here that does not
scale for free, so the rules are measured, not guessed:

| for 36 cells | size | per cell |
|---|---|---|
| SVG contact sheet | 2,970 kB | 83 kB |
| PNG, 150 dpi | 157 kB | 4.4 kB |
| PNG, 100 dpi | 87 kB | 2.4 kB |
| **PNG, 100 dpi, quantized** | **29 kB** | **0.81 kB** |

**SVG is the wrong format for documentation.** The hollow renderer strokes
*and* fills every part, so a page of cells carries two paths per part and runs
to megabytes. Vector is for the deliverable — the figure that goes in a paper
— and rasters are for the README.

So:

- **Use `bd.contact_sheet` + `bd.save_compact` for anything in a README.**
  Compact caps the pixel width at 1000 (a README displays at less than that,
  and rendering at three times it is three times the bytes for nothing) and
  quantizes to a 32-colour palette, which is visually lossless on flat line
  art and about a third the size. Pillow does the work and ships with
  matplotlib, so this costs no new dependency.
- **A variant inside a shared sheet costs ~0.8 kB; the same variant as its own
  image costs ~50 kB.** Sixty times cheaper. Show more, in fewer files.
- **Do not commit SVGs of assembled shapes.** A single pyramidal cell is 98 kB
  as SVG — more than all five of that example's rasters put together. The
  vector file is one `bd.save(fig, "cell.svg")` away, and `build.py` is
  committed, so the repository does not need to carry output that regenerates
  in a fraction of a second. One small SVG is kept in
  `examples/dendritic_spine/` as the standing demonstration that vector export
  works; re-proving it per folder costs ~100 kB each for nothing.
- **Budget: about 100 kB per example folder.** At that rate a hundred examples
  is 10 MB, which is a repository people can clone.
- **The frame is the drawing's shape, not the figure's.** *"the 'on a branch'
  eight image is almost only white space image."* Measured: its ink filled
  62% of the file's width. Two causes, both invisible until something counted
  them — `bbox_inches="tight"` trims to the **axes**, which are equal-aspect,
  so a tall drawing in a square figure keeps its side margins; and
  `pad_inches` defaults to a *fixed* 0.1 inch, which is 1% of a wide sheet
  and 19% of a portrait 0.86 inches across. `save_compact` pads 0.02 now, and
  every `build_gallery` run reports any image whose ink leaves a quarter of
  an axis empty. That took the catalog's worst frame from 52% to 75% and its
  median to 93%, and made several files smaller on the way.
- Past two varying knobs, use `row_labels` / `col_labels` rather than a
  caption under every cell — repeating three keys eighteen times is the same
  text written eighteen times, and it crowds out the drawings.


## What makes a skill good

Skills are the main way this library gets used and extended: some shipped
here, some written by others for their own figure styles. That needs a
contract, or the repo fills up with prompts that work once.

A skill in `skills/` must:

1. **Name its trigger precisely.** When it applies, and — as importantly —
   when it does not.
2. **Be derived from a worked example, not imagined.** Do the task once by
   hand, keep what was actually needed, and cut what turned out not to be.
   Anything asserted in a skill that was never exercised is a guess.
3. **State the checks.** What the agent runs to know it succeeded, and what
   the failure looks like. A skill with no verification step is a wish.
4. **Fail loudly on ambiguity.** Where a choice is a scientific claim — which
   compartment a contact lands on, whether two cells are level — the skill
   must say *ask*, not *pick*.
5. **Ship with its example.** The folder under `examples/` that the skill was
   derived from, so the skill can be re-derived and tested against a known
   output.

`trace-a-shape` was derived exactly this way — from
`examples/dendritic_spine/`, by starting from the original photograph and
rebuilding the blueprint from it. That exercise is the method: whatever it
takes to get there *is* the skill.


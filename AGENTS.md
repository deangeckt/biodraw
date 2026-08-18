# Driving biodraw

Notes for coding agents building figures with this library — and for the
humans reading over their shoulder.

Most `biodraw` figures will be *described*, not typed. That is a design
premise, not a concession: the library is shaped so an agent can build a
correct figure without seeing it, and so a person can read the result and know
what it says.

## The contract

**You cannot see the figure. Do not pretend otherwise.** Never report a drawing
as good because the code ran. Use the tools that substitute for eyes:

```python
bd.check(fig)          # geometric problems: overlaps, crossings, ink off-canvas
bd.explain(shape)      # the construction figure — what the maths actually did
bd.catalog()           # every shape, knob, default, range and effect, as data
```

If a check fails, fix the geometry — do not raise the tolerance.

## Order of work

1. **`bd.catalog()` before writing code.** It is the API surface as data. Do
   not grep the source to find out what a shape takes.
2. **Build one shape, check it, then compose.** A panel that is wrong is
   usually wrong in one shape.
3. **Fit last.** `bd.fit(ax, parts, pad=...)` after everything is drawn.
   `pad` is in the drawing's own units and is what sets how big the ink comes
   out inside a fixed panel.
4. **Save with `bd.save`, not `fig.savefig`.** It keeps text as text, names
   the SVG layers, and refuses to write a rasterized artist.

## Units: the one thing that bites

Two unit systems coexist and they behave differently under scaling.

| In **local units** | In **points** |
|---|---|
| lengths, widths, gaps, `pad`, positions | `wall_lw`, dot sizes, font sizes |
| scale with the drawing | **do not** scale with the drawing |

A panel drawn at half size keeps its linewidths and comes out looking heavy.
That is not a bug to route around per figure — reach for a `biodraw.style`
preset (`paper` / `poster` / `slides`), which exists precisely to hold the
point-valued knobs for a medium.

## House style

- **Vector only.** Never `rasterized=True`, never a PNG intermediate.
- **Colour means something.** Identity colours name what a thing *is*; claim
  colours name what the figure *asserts* (which compartment a contact hit).
  Anything belonging to neither takes grey. Do not introduce a fourth hue for
  decoration.
- **One idea per panel**, said in the heading.
- **Nothing sits on a baseline by accident.** If two cells are level, it is
  because being level means something.
- **Keep the comments.** The tuning comments in this codebase record *why* a
  number is what it is, usually after something looked wrong. Do not strip them
  when refactoring, and add one when you discover a constraint.

## Determinism

Any shape with jitter takes a `seed`. Figures must regenerate byte-identically
— CI enforces it on `examples/`. Never call `np.random` without a seeded
generator.

## When you change a drawing

Two nets, and they answer different questions.

**Test what must be true; pin what merely is.** This is a qualitative library
— the product is a picture, and most of what could be asserted about a shape
is a statement about how it looks. Those statements belong in the pins, which
report a change as a readable diff and cost one command to accept. Put them in
a test and you have frozen an opinion: the suite then fails every time a
drawing is *improved*, and the fix to a real defect starts with deleting an
assertion. That is not hypothetical — a test here asserted that a fork's two
daughters were mirror images, which is exactly the flaw that had to be fixed,
and the test had made it the specification.

So a test earns its place when it guards something no amount of retuning may
break:

| Test it | Pin it |
|---|---|
| placement algebra (scale, translate, rotate) | how many spines, how long a branch |
| anchors pointing out of a shape, not into it | where exactly an anchor sits |
| determinism — same seed, same bytes | which side is the longer one |
| guards that refuse rather than draw nonsense | how wide a fork splays |
| mechanisms that stop a seam (a root buried inside its parent) | the resulting outline |
| documented design rules (repeated parts differ) | by how much they differ |

The ratio to expect: the core's geometry is genuinely quantitative and carries
most of the tests, because `resample` spacing and `signed_area` signs have
right answers. A domain shape should carry few.

**Geometry pins** (`tests/shape_pins.json`) are the main one: a compact digest
of every shape's vertices. Exact, tiny, readable in a diff, and they do not
grow a binary file per shape.

```bash
pytest tests/test_pins.py          # what moved, and by how much
python tools/update_pins.py --dry-run
python tools/update_pins.py        # regenerate, if intended
```

**Two baseline images** (`tests/baseline/`) cover the things a vertex array
cannot express — that overlapping parts really fuse, and that a wall comes out
the weight it was asked for. That count stays at two however many shapes get
added; do not add a third without a reason that geometry pins cannot cover.

```bash
pytest --mpl
pytest --mpl-generate-path=tests/baseline     # regenerate, if intended
```

Either way: say in the PR **what changed and why**. A regenerated pin with no
account of it is a silent regression waiting to happen.

## Adding a shape

Build it on `biodraw.core` — `Profile`, `Branch`, `paths`, `render_hollow`,
anchors. If the core cannot express your shape, extend the core; do not
special-case it in the domain package. A shape is finished when it:

1. exposes **anchors**, so connectors, dots and labels work on it for free;
2. registers in `catalog()` with a documented effect for every knob;
3. has an `explain()` view;
4. has a pinned baseline image;
5. carries its provenance, if it was traced from a drawing.

## Tone

The user is a scientist making a figure for a real paper. Report what you
built, what you checked, and what you could not verify. If the geometry is
ambiguous — which compartment a contact should land on, whether two cells
should be level — that is a scientific claim, not a styling choice. Ask.

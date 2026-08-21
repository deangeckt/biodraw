"""Build the static site from `site/content/*.py`.

    python tools/build_site.py            # rebuild site/
    python tools/build_site.py --check    # rebuild, then fail on any diff

One content module per example, one card on the index, one detail page each.
Adding an example means adding `site/content/<slug>.py` — there is no list
here to keep in step.

Why a schema rather than markdown
---------------------------------
`docs/RULES.md` rule 1 is *image first, code second — always. Never open a
section with a code block.* Written as prose that gets read once. Written as a
schema it cannot be violated: a section renders `images`, then `body`, then
`code`, in that order, and there is no field that puts code above a picture.
The rule is the data structure.

A catalog, not an article
-------------------------
*"now that the website is live on gh pages; its still too much text, its
should be more catalog then code-snippet."* Measured at the time: 6,662 words
and 352 lines of code across 66 drawings — about a hundred words per picture,
and up to six snippets on a page. That is an article with figures in it, and
a reader looking for a shape has to read an essay to find out whether they
want it.

The rule that came out of it, and the reason `check_catalog` exists: **every
section on a catalog page shows a drawing.** A section with no image is prose
that wandered onto a catalog — either it belongs on the picture it is talking
about, as a caption, or it belongs in the code's tuning comments where the
reasoning already lives. The one exception is the single snippet that says how
to draw the thing.

`docs/RULES.md` carries the rule; `BUDGET` below is the number, so it cannot
creep back the way it got here.

The checks this runs, each because something real got through:

- **every image referenced exists on disk** — `examples/wiring/README.md`
  pointed at five images of `neuro.Axon`, a class deleted a session earlier,
  and nothing had noticed;
- **no snippet needs a clone** — every page once ended in
  `python tools/build_gallery.py <name>`, a maintainer's command on a
  reader's page;
- **the catalog budget** — see above.

Images are referenced as `../examples/<slug>/<file>` rather than copied into
`site/`, for two reasons: the seven folders are ~1.6 MB and `docs/RULES.md`
budgets image weight explicitly, and a rebuilt gallery is picked up by the
site with no second step. That means **GitHub Pages must publish from the
repository root**, not from `site/` — the site is then served at `/site/`.
"""

import argparse
import html
import importlib.util
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
CONTENT = SITE / "content"
EXAMPLES = ROOT / "examples"

# Order on the index. **A category is a domain package.** `biodraw.neuro` ->
# Neuroscience, `biodraw.cells` -> Cells & tissues, `biodraw.micro` ->
# Microbes, so the structure a reader browses is the structure they import and
# finding a drawing and finding its module are the same act. A new domain gets
# its category for free, and nobody has to adjudicate whether a spine belongs
# under "dendrites" or "neurons".
#
# It used to be five, with Neurons / Dendrites & spines / Circuits split out —
# nine pages across five filters, three of which were the same package, and
# most filters showed one or two cards.
CATEGORIES = (
    "Neuroscience",
    "Cells & tissues",
    "Microbes",
    "Genetics",
    "Animals",
    # `biodraw.lab` — the first category that draws no living thing. It is in
    # the catalog on the roster test, not in spite of it: an instrument with
    # counts in it is a thing that varies, and that is the whole line.
    "Lab & methods",
)

GITHUB = "https://github.com/deangeckt/biodraw"

# The supported way to drive the library. `docs/SCOPE.md`: most figures will be
# described, not typed — so the skills are the interface, not a footnote.
SKILLS = (
    ("draw-a-figure",
     "building a figure from shapes that already exist."),
    ("review-a-drawing",
     "the numeric checks to run before calling a drawing finished. An agent "
     "cannot see the figure, so every check is a measurement."),
    ("trace-a-shape",
     "turning a photograph of your own drawing into a shape the library does "
     "not have yet. Tracing is public API, not a story about how the bundled "
     "shapes were made."),
)


# ---------------------------------------------------------------------------
# inline formatting
# ---------------------------------------------------------------------------
# Deliberately not a markdown parser. Three spans and a link, which is all the
# prose uses; anything more wants a dependency, and the schema already carries
# the block structure a parser would otherwise have to infer.

_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITAL = re.compile(r"(?<![*\w])\*([^*]+)\*(?!\*)")


def inline(text):
    """Escape, then re-admit the four spans the prose actually uses."""
    out = html.escape(text)
    out = _LINK.sub(r'<a href="\2">\1</a>', out)
    out = _CODE.sub(r"<code>\1</code>", out)
    out = _BOLD.sub(r"<strong>\1</strong>", out)
    out = _ITAL.sub(r"<em>\1</em>", out)
    return out


def skill_items():
    return "".join(
        f'<li><a href="{GITHUB}/blob/main/skills/{name}/SKILL.md">'
        f"<code>{name}</code></a> \u2014 {text}</li>"
        for name, text in SKILLS)


def img_src(page, src):
    """Where an image lives, as a URL from `site/`.

    A bare name is that page's own example folder — the 1:1 case, which is
    most of them. A name with a folder in it (`wiring/bus.png`) is another
    example's, which is what lets **one card cover several example folders**:
    wiring and circuit motifs are one page a reader browses and two folders a
    maintainer builds, and neither had to be bent to the other.
    """
    return (f"../examples/{src}" if "/" in src
            else f"../examples/{page['slug']}/{src}")


def page_examples(page):
    """The example folders a page draws from, in order."""
    return page.get("examples") or [page["slug"]]


def section_id(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

def load_pages():
    """Every `site/content/<slug>.py`, as `(cards, standalone pages)`."""
    pages = []
    for path in sorted(CONTENT.glob("*.py")):
        if path.name.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        page = module.PAGE
        page.setdefault("slug", path.stem)
        pages.append(page)

    # A standalone page is not in the grid, so it has no category to be in;
    # everything else must name one that exists.
    unknown = {p["category"] for p in pages
               if not p.get("standalone")} - set(CATEGORIES)
    if unknown:
        plural = "y" if len(unknown) == 1 else "ies"
        raise SystemExit(f"unknown categor{plural}: {sorted(unknown)}. "
                         f"Add to CATEGORIES or fix the content module.")
    cards = sorted((p for p in pages if not p.get("standalone")),
                   key=lambda p: (CATEGORIES.index(p["category"]),
                                  p["order"]))
    extras = sorted((p for p in pages if p.get("standalone")),
                    key=lambda p: p["order"])
    return cards, extras


# Anything a reader could type. `pip install biodraw` gets them the library
# and nothing else — no clone, no `tools/`, no `examples/`. A snippet naming
# any of those is a maintainer's instruction that wandered onto a reader's
# page, which is exactly what happened to "Rebuilding these drawings".
REPO_ONLY = ("tools/", "build_gallery", "build_site", "git ")


def check_snippets(pages):
    """No snippet may need anything `pip install biodraw` does not give."""
    bad = []
    for page in pages:
        for section in page["sections"]:
            code = section.get("code") or ""
            for token in REPO_ONLY:
                if token in code:
                    bad.append(f"{page['slug']} / {section.get('title')}: "
                               f"{token!r}")
    if bad:
        raise SystemExit(
            "snippets that only work in a clone of this repo:\n  "
            + "\n  ".join(bad)
            + "\n\nGallery snippets must run after `pip install biodraw`. "
              "Maintainer commands belong in CONTRIBUTING.md.")


# The catalog budget. These are the numbers behind "more catalog than
# code-snippet", and they are here rather than in prose because a rule written
# as prose gets read once and a rule written as a check gets run every time.
#
# `words` counts prose only — `intro`, `body`, `steps`, `after`. Captions,
# panel notes and tables are not prose in this sense: a caption is part of
# showing the drawing, and a table is the knobs as data. They get their own,
# tighter, per-item cap.
BUDGET = dict(
    words=150,          # prose per page. Was 660 on average.
    code_blocks=1,      # one snippet: how to draw the thing. Was 5.
    caption_words=20,   # per image alt, and per panel note.
)


def _prose_words(page):
    fields = ("body", "steps", "after")
    n = sum(len(t.split()) for t in page.get("intro", ()))
    for section in page["sections"]:
        n += sum(len(t.split())
                 for key in fields for t in section.get(key, ()))
    return n


def check_catalog(pages):
    """The page is a catalog of drawings, not an article with figures.

    Three things, all of them the same rule seen from different sides: a
    section earns its place by showing something, prose is a caption rather
    than an essay, and there is exactly one snippet — the one that draws the
    thing on the page.
    """
    bad = []
    for page in pages:
        coded = [s for s in page["sections"] if s.get("code")]
        if len(coded) > BUDGET["code_blocks"]:
            bad.append(f"{page['slug']}: {len(coded)} code blocks, "
                       f"budget is {BUDGET['code_blocks']} "
                       f"({', '.join(s.get('title', '?') for s in coded)})")

        for section in page["sections"]:
            if section.get("images") or section.get("code"):
                continue
            bad.append(f"{page['slug']} / {section.get('title', '?')!r}: "
                       f"a section with no drawing. Put it on the picture it "
                       f"is about, or in the code's tuning comments.")

        words = _prose_words(page)
        if words > BUDGET["words"]:
            bad.append(f"{page['slug']}: {words} words of prose, "
                       f"budget is {BUDGET['words']}")

        for section in page["sections"]:
            for img in section.get("images", ()) or ():
                for text in [img["alt"], *img.get("notes", ())]:
                    if len(text.split()) > BUDGET["caption_words"]:
                        bad.append(
                            f"{page['slug']} / {img['src']}: caption is "
                            f"{len(text.split())} words, budget is "
                            f"{BUDGET['caption_words']} — {text[:50]}...")

    if bad:
        raise SystemExit(
            "the catalog budget is exceeded:\n  " + "\n  ".join(bad)
            + "\n\nSee `A catalog, not an article` in this file's docstring "
              "and the documentation rules in docs/RULES.md.")


def check_readme(cards, extras):
    """`README.md` quotes the catalog's size; the catalog generates it.

    *"the readme do need a major change to reflect the main website."* The
    README had drifted into a second copy of the index — the same pitch,
    the same skills paragraph — and was cut back to a front door. What a
    front door still has to carry is the one thing a picture cannot say:
    how much is in there. Two numbers, written by hand, next to two numbers
    generated from the content modules; adding an example would silently
    falsify the README the way `examples/wiring/README.md` outlived the class
    it documented.

    So the numbers are checked rather than trusted. The same pair the index
    renders in its tally, counted the same way.
    """
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    figures = sum(1 + sum(len(s.get("images", ())) for s in p["sections"])
                  for p in (*cards, *extras))

    claim = re.search(r"\*\*(\d+) examples, (\d+) figures\*\*", readme)
    if not claim:
        raise SystemExit(
            "README.md no longer states the catalog's size. Expected a line "
            "matching `**N examples, M figures**` — see check_readme in "
            "this file for why it is checked and not trusted.")

    said = (int(claim.group(1)), int(claim.group(2)))
    real = (len(cards), figures)
    if said != real:
        raise SystemExit(
            f"README.md says {said[0]} examples and {said[1]} figures; the "
            f"catalog has {real[0]} and {real[1]}. Update the line in "
            f"README.md.")


def check_docs():
    """Every `docs/*.md` a file points at has to exist.

    PLAN.md was one 862-line file under `docs/` and the masthead's *Roadmap*
    link pointed at it: *"that's too long for users to read."* Splitting it to
    ROADMAP / SCOPE / RULES / MILESTONES dragged **31 inbound references**
    with it — tuning comments in `biodraw/`, docstrings in `tests/`, prose in
    `skills/`, two comments in `site/assets/style.css`. Every one of them was
    a path in a string that no tool had ever read.

    That is the same failure as `examples/wiring/README.md` outliving the
    class it documented, and the same answer: the reference is checked, not
    trusted. Cheap, and it runs on every prose change.
    """
    skip = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", "site"}
    missing = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or set(path.parts) & skip:
            continue
        if path.suffix not in {".py", ".md", ".css", ".html", ".toml"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        # A prefixed path from anywhere; a bare capitalised one only inside
        # docs/, where STATE.md links to its siblings without the prefix.
        names = set(re.findall(r"docs/([A-Z_]+\.md)", text))
        if path.parent == ROOT / "docs":
            names |= set(re.findall(r"\]\(([A-Z_]+\.md)\)", text))
        for name in sorted(names):
            if not (ROOT / "docs" / name).exists():
                missing.append(f"{path.relative_to(ROOT)} → docs/{name}")
    if missing:
        raise SystemExit(
            "These files point at a docs page that does not exist:\n  "
            + "\n  ".join(missing)
            + "\nSee check_docs in this file for why this is checked.")


def check_images(pages):
    """Every referenced image must exist. See the module docstring."""
    missing = []
    for page in pages:
        wanted = [page["hero"]]
        for section in page["sections"]:
            wanted += [img["src"] for img in section.get("images", ())]
        for name in wanted:
            rel = img_src(page, name).replace("../examples/", "")
            if not (EXAMPLES / rel).is_file():
                missing.append(rel)
    if missing:
        raise SystemExit("images referenced but not on disk:\n  " +
                         "\n  ".join(missing))


# ---------------------------------------------------------------------------
# chrome
# ---------------------------------------------------------------------------

# The three families the site actually uses, in the weights it actually
# uses — asking for more is bytes a reader waits for and never sees.
# *"the fontstyle is shouting claude"*: the previous stack was Palatino/
# Georgia over system-ui, which is what every tool defaults to. Every family
# here has a full system fallback in `style.css`, so a blocked or slow
# fonts.googleapis.com costs personality, never legibility — and
# `display=swap` means text paints immediately either way.
#
# This is the site's only external request. The library itself keeps its
# numpy-and-matplotlib-only rule; nothing here is imported by `biodraw`.
FONTS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=Space+Grotesk:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=JetBrains+Mono:wght@400&display=swap">"""


def head(title, description):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
{FONTS}
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
"""


# The GitHub mark, inline. *"the main page in the website [is] missing ... a
# link to github aswell (small icon?)"* — the word "GitHub" in a nav reads as
# one more section of the site; the mark reads as "the code is over there",
# which is the thing a reader is looking for. Inline because the site has no
# asset pipeline and a 700-byte path beats a request.
GITHUB_MARK = (
    '<svg viewBox="0 0 16 16" width="17" height="17" aria-hidden="true" '
    'focusable="false"><path fill="currentColor" fill-rule="evenodd" '
    'd="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 '
    '0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-'
    '1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 '
    '2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59'
    '.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 '
    '2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51'
    '.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 '
    '1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-'
    '3.58-8-8-8Z"/></svg>')


def masthead(extras=()):
    """The header. `extras` are the standalone pages — see `render_index`.

    A standalone page is one that is *about every card* rather than being one
    of them, so it belongs in the chrome and not in the grid: from any page,
    one click away.

    There was a *Roadmap* link here, pointing at the old `PLAN.md`. It went
    when that file was split, and the reason it did not simply follow it is
    that the masthead sits on every catalog page, in front of a reader who
    came for drawings — a roadmap is a contributor document, and the GitHub
    mark beside it already leads to all four. A link that most readers should
    not click is a link that should not be in the chrome.
    """
    links = "".join(
        f'<a href="{e["slug"]}.html">{html.escape(e["title"])}</a>'
        for e in extras)
    return f"""<header class="masthead">
  <div class="masthead-inner">
    <a class="wordmark" href="index.html">biodraw</a>
    <nav class="masthead-links">
      {links}
      <a class="gh" href="{GITHUB}" aria-label="biodraw on GitHub"
         title="biodraw on GitHub">{GITHUB_MARK}</a>
    </nav>
  </div>
</header>
"""


def foot():
    return f"""<footer class="foot">
  <div class="foot-inner">
    <p><strong>biodraw</strong> — MIT. Runtime dependencies: numpy and
       matplotlib, nothing else.</p>
    <p>Every drawing here is regenerated from the <code>build.py</code>
       committed beside it. Nothing on this site is a stored asset.</p>
    <p><a href="{GITHUB}">Source</a></p>
  </div>
</footer>
</body>
</html>
"""


ZOOM = """<div class="lightbox" id="lightbox" hidden>
  <button class="lightbox-close" type="button"
          aria-label="Close">&times;</button>
  <figure><img id="lightbox-img" alt=""><figcaption id="lightbox-cap">
  </figcaption></figure>
</div>
<script>
(function () {
  var box = document.getElementById('lightbox');
  var img = document.getElementById('lightbox-img');
  var cap = document.getElementById('lightbox-cap');
  function open(src, alt) {
    img.src = src; img.alt = alt; cap.textContent = alt;
    box.hidden = false; document.body.classList.add('no-scroll');
  }
  function close() {
    box.hidden = true; img.removeAttribute('src');
    document.body.classList.remove('no-scroll');
  }
  document.querySelectorAll('.zoomable').forEach(function (fig) {
    fig.addEventListener('click', function () {
      var i = fig.querySelector('img');
      open(i.getAttribute('src'), i.getAttribute('alt'));
    });
  });
  box.addEventListener('click', close);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !box.hidden) close();
  });
})();
</script>
"""


# ---------------------------------------------------------------------------
# index
# ---------------------------------------------------------------------------

def card(page):
    chips = "".join(f'<span class="chip">{html.escape(s)}</span>'
                    for s in page.get("shapes", ()))
    haystack = (page["title"] + " " + page["tagline"] + " "
                + " ".join(page.get("shapes", ())) + " "
                + " ".join(page.get("keywords", ())) + " "
                + page["category"]).lower()
    return f"""  <a class="card" href="{page['slug']}.html"
     data-category="{html.escape(page['category'])}"
     data-search="{html.escape(haystack)}">
    <span class="plate card-plate">
      <img class="shot" src="{img_src(page, page['hero'])}"
           alt="{html.escape(page['hero_alt'])}" loading="lazy">
    </span>
    <span class="card-body">
      <span class="card-kicker">{html.escape(page['category'])}</span>
      <span class="card-title">{html.escape(page['title'])}</span>
      <span class="card-tagline">{inline(page['tagline'])}</span>
      <span class="chips">{chips}</span>
    </span>
  </a>
"""


def band(page):
    """A standalone page, as a full-width strip beside the grid.

    *"neuron style is great! ... but i dont think it should be in a card,
    rather, somewhere else, which is more of a 'global' or parallel to the
    main page cards."* A card is one drawing among many and invites
    comparison with its neighbours; a style is a property **of** all of them,
    and putting it in the grid says the wrong thing about what it is. Same
    data as a card, laid out so it cannot be mistaken for one.
    """
    return f"""<section class="band">
  <a class="band-inner" href="{page['slug']}.html">
    <span class="band-copy">
      <span class="card-kicker">Every drawing in the catalog</span>
      <span class="band-title">{html.escape(page['title'])}</span>
      <span class="card-tagline">{inline(page['tagline'])}</span>
      <span class="band-go">See them all &rarr;</span>
    </span>
    <span class="plate band-plate">
      <img src="{img_src(page, page['hero'])}"
           alt="{html.escape(page['hero_alt'])}" loading="lazy">
    </span>
  </a>
</section>
"""


def render_index(pages, extras=()):
    counts = {c: sum(1 for p in pages if p["category"] == c)
              for c in CATEGORIES}
    chips = [f'<button class="filter is-on" data-category="">All'
             f'<span class="count">{len(pages)}</span></button>']
    for cat in CATEGORIES:
        if not counts[cat]:
            continue
        chips.append(
            f'<button class="filter" data-category="{html.escape(cat)}">'
            f'{html.escape(cat)}<span class="count">{counts[cat]}</span>'
            f"</button>")

    figures = sum(1 + sum(len(s.get("images", ())) for s in p["sections"])
                  for p in (*pages, *extras))

    return (
        head("biodraw — bio-inspired vector drawings",
             "A browsable gallery of parametric biological drawings for "
             "matplotlib. Every shape is a few parameters and a seed.")
        + masthead(extras)
        + f"""<main>
<section class="hero-copy">
  <h1>Bio-inspired vector drawings<br>for papers, posters and slides</h1>
  <p class="standfirst">A <strong>Python</strong> library. Hand-drawn shapes,
     turned into maths, drawn onto a matplotlib axes so they sit beside real
     data. Every drawing below is a few parameters and a seed — not a file
     someone saved.</p>
  <p class="hero-install"><code>pip install biodraw</code>
     <a href="{GITHUB}">{GITHUB_MARK}<span>Source on GitHub</span></a></p>
</section>

<section class="controls">
  <div class="filters">{''.join(chips)}</div>
  <input id="search" type="search" placeholder="Search shapes, tissue, knobs…"
         autocomplete="off" aria-label="Search examples">
</section>

<p class="tally"><strong>{len(pages)}</strong> examples ·
   <strong>{figures}</strong> figures · every one a parameter away from the
   next</p>

<section class="grid" id="grid">
{''.join(card(p) for p in pages)}</section>

{''.join(band(e) for e in extras)}

<p class="empty" id="empty" hidden>Nothing matches that.
   <button class="linky" id="reset">Show everything</button></p>

<section class="pitch">
  <h2>Why not a stock illustration?</h2>
  <p>Because you almost never want <em>the</em> picture — you want a variation
     on it. Free libraries of scientific art are good, and nothing here
     competes with them: if you need a virion or a centrifuge, download one.
     What a stock asset cannot do is become the <em>next</em> one.</p>
  <blockquote class="pullquote">
    <p>We already spent the tokens generating these drawings.<br>
       Let's not spend them again.</p>
  </blockquote>
</section>
<section class="pitch">
  <h2>Described, not typed</h2>
  <p>Most figures built with this will never be written by hand. You install
     it, point an agent at it, and describe what you want. Three skills ship
     with the library and are the supported way to drive it:</p>
  <ul class="skills">{skill_items()}</ul>
  <pre><code>pip install biodraw</code></pre>
</section>
</main>
"""
        + foot()
        + """<script>
(function () {
  var grid = document.getElementById('grid');
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.card'));
  var search = document.getElementById('search');
  var empty = document.getElementById('empty');
  var filters = Array.prototype.slice.call(
    document.querySelectorAll('.filter'));
  var category = '';

  function apply() {
    var q = search.value.trim().toLowerCase();
    var shown = 0;
    cards.forEach(function (c) {
      var on = (!category || c.dataset.category === category) &&
               (!q || c.dataset.search.indexOf(q) !== -1);
      c.hidden = !on;
      if (on) shown++;
    });
    empty.hidden = shown !== 0;
  }

  filters.forEach(function (b) {
    b.addEventListener('click', function () {
      filters.forEach(function (o) { o.classList.remove('is-on'); });
      b.classList.add('is-on');
      category = b.dataset.category;
      apply();
    });
  });
  search.addEventListener('input', apply);
  document.getElementById('reset').addEventListener('click', function () {
    search.value = '';
    filters[0].click();
  });
})();
</script>
""")


# ---------------------------------------------------------------------------
# detail
# ---------------------------------------------------------------------------

def render_section(page, section):
    parts = ['<section class="block">']
    if section.get("title"):
        sid = section_id(section["title"])
        parts.append(f'<h2 id="{sid}">{html.escape(section["title"])}</h2>')

    # images → body → code. The order is the point; see the module docstring.
    images = section.get("images", ())
    if images:
        single = " is-single" if len(images) == 1 else ""
        parts.append(f'<div class="figs{single}">')
        for img in images:
            parts.append(
                f'<figure class="plate zoomable">'
                f'<img src="{img_src(page, img["src"])}" '
                f'alt="{html.escape(img["alt"])}" loading="lazy">'
                f'<figcaption>{html.escape(img["alt"])}</figcaption>'
                f"</figure>")
        parts.append("</div>")
        # Panel notes: one line per numbered panel *of that drawing*. This is
        # where the construction prose went when the pages were cut back to a
        # catalog — a blueprint's panels are already titled inside the image,
        # so the page says the one thing the picture cannot, and the long
        # reasoning stays in the tuning comments of the code that draws it.
        for img in images:
            if img.get("notes"):
                parts.append('<ol class="panel-notes">')
                parts += [f"<li>{inline(n)}</li>" for n in img["notes"]]
                parts.append("</ol>")

    for para in section.get("body", ()):
        parts.append(f"<p>{inline(para)}</p>")

    for step in section.get("steps", ()):
        parts.append(f'<p class="step">{inline(step)}</p>')

    if section.get("table"):
        table = section["table"]
        parts.append('<div class="tablewrap"><table><thead><tr>')
        parts += [f"<th>{inline(h)}</th>" for h in table["head"]]
        parts.append("</tr></thead><tbody>")
        for row in table["rows"]:
            parts.append("<tr>" + "".join(f"<td>{inline(c)}</td>"
                                          for c in row) + "</tr>")
        parts.append("</tbody></table></div>")

    if section.get("code"):
        parts.append(
            '<div class="codeblock"><button class="copy" type="button">Copy'
            "</button><pre><code>"
            + html.escape(section["code"].strip("\n"))
            + "</code></pre></div>")

    for para in section.get("after", ()):
        parts.append(f"<p>{inline(para)}</p>")

    parts.append("</section>")
    return "\n".join(parts)


def render_page(page, pages, extras=()):
    # A standalone page is not in the sequence of cards, so it gets no
    # previous/next: it is beside the catalog rather than a place in it.
    order = [p["slug"] for p in pages]
    i = order.index(page["slug"]) if page["slug"] in order else None
    prev_p = pages[i - 1] if i else None
    next_p = (pages[i + 1] if i is not None and i + 1 < len(pages) else None)

    nav = []
    if prev_p:
        nav.append(f'<a class="prev" href="{prev_p["slug"]}.html">'
                   f'<span>Previous</span>{html.escape(prev_p["title"])}</a>')
    if next_p:
        nav.append(f'<a class="next" href="{next_p["slug"]}.html">'
                   f'<span>Next</span>{html.escape(next_p["title"])}</a>')

    rail = "".join(
        f'<li><a href="#{section_id(s["title"])}">'
        f'{html.escape(s["title"])}</a></li>'
        for s in page["sections"] if s.get("title"))

    chips = "".join(f'<span class="chip">{html.escape(s)}</span>'
                    for s in page.get("shapes", ()))
    scripts = ", ".join(
        f'<a href="{GITHUB}/blob/main/examples/{slug}/build.py">'
        f"<code>{slug}/build.py</code></a>"
        for slug in page_examples(page))
    intro = "".join(f'<p class="standfirst">{inline(t)}</p>'
                    for t in page.get("intro", ()))
    crumb = ("" if page.get("standalone") else
             '  <span aria-hidden="true">·</span> '
             + html.escape(page["category"]))
    body = "\n".join(render_section(page, s) for s in page["sections"])

    return (
        head(f"{page['title']} — biodraw", page["tagline"])
        + masthead(extras)
        + f"""<main class="detail">
<article>
  <p class="crumb"><a href="index.html">All examples</a>{crumb}</p>

  <h1>{html.escape(page['title'])}</h1>
  <p class="standfirst">{inline(page['tagline'])}</p>
  <p class="chips">{chips}</p>

  <figure class="hero plate zoomable">
    <img src="{img_src(page, page['hero'])}"
         alt="{html.escape(page['hero_alt'])}">
    <figcaption>{html.escape(page['hero_alt'])}</figcaption>
  </figure>

  {intro}

{body}

  <p class="source-note">Every figure above is output, not a stored asset —
     drawn by {scripts}, in Python, on a matplotlib axes.</p>

  <nav class="pager">{''.join(nav)}</nav>
</article>

<aside class="rail">
  <p class="rail-head">On this page</p>
  <ul>{rail}</ul>
</aside>
</main>
"""
        + ZOOM
        + """<script>
document.querySelectorAll('.copy').forEach(function (b) {
  b.addEventListener('click', function (e) {
    e.stopPropagation();
    var code = b.parentElement.querySelector('code').textContent;
    navigator.clipboard.writeText(code).then(function () {
      b.textContent = 'Copied';
      b.classList.add('is-done');
      setTimeout(function () {
        b.textContent = 'Copy'; b.classList.remove('is-done');
      }, 1400);
    });
  });
});
(function () {
  var links = Array.prototype.slice.call(
    document.querySelectorAll('.rail a'));
  var heads = links.map(function (a) {
    return document.getElementById(a.getAttribute('href').slice(1));
  });
  function mark() {
    var best = 0;
    heads.forEach(function (h, i) {
      if (h && h.getBoundingClientRect().top < 140) best = i;
    });
    links.forEach(function (a, i) {
      a.classList.toggle('is-here', i === best);
    });
  }
  window.addEventListener('scroll', mark, { passive: true });
  mark();
})();
</script>
"""
        + foot())


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="fail if rebuilding changes any tracked file")
    args = ap.parse_args()

    cards, extras = load_pages()
    pages = [*cards, *extras]
    check_images(pages)
    check_snippets(pages)
    check_catalog(pages)
    check_readme(cards, extras)
    check_docs()

    (SITE / "index.html").write_text(render_index(cards, extras),
                                     encoding="utf-8", newline="\n")
    print("wrote site/index.html")
    written = {"index.html"}
    for page in pages:
        out = SITE / f"{page['slug']}.html"
        out.write_text(render_page(page, cards, extras), encoding="utf-8",
                       newline="\n")
        written.add(out.name)
        print(f"wrote site/{out.name}")

    # Nothing else owns `site/*.html`, so a page whose content module was
    # renamed or merged away would otherwise sit there for ever: still the
    # old catalog, still linked from anyone else's history. Merging
    # wiring and circuit motifs into one card is exactly that case.
    for stale in sorted(SITE.glob("*.html")):
        if stale.name not in written:
            stale.unlink()
            print(f"removed site/{stale.name} (no content module)")

    print(f"\n{len(cards)} example(s) across "
          f"{len({p['category'] for p in cards})} categories, "
          f"{len(extras)} standalone page(s).")

    if not args.check:
        return 0

    diff = subprocess.run(
        ["git", "status", "--porcelain", "--", str(SITE)],
        cwd=ROOT, capture_output=True, text=True, check=False)
    changed = [ln for ln in diff.stdout.splitlines() if ln.strip()]
    if changed:
        print("\nRebuilding changed these files:", file=sys.stderr)
        for line in changed:
            print(f"  {line}", file=sys.stderr)
        return 1
    print("no changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

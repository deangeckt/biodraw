"""Build the static site from `site/content/*.py`.

    python tools/build_site.py            # rebuild site/
    python tools/build_site.py --check    # rebuild, then fail on any diff

One content module per example, one card on the index, one detail page each.
Adding an example means adding `site/content/<slug>.py` — there is no list
here to keep in step.

Why a schema rather than markdown
---------------------------------
`docs/PLAN.md` rule 1 is *image first, code second — always. Never open a
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

`docs/PLAN.md` carries the rule; `BUDGET` below is the number, so it cannot
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
`site/`, for two reasons: the seven folders are ~1.6 MB and `docs/PLAN.md`
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

# Order on the index. A category is a domain a reader would search in, not a
# module name — `wiring` is core.connectors and `circuit_motifs` is a
# composition, but both are what someone means by "circuits".
CATEGORIES = (
    "Neurons",
    "Dendrites & spines",
    "Circuits",
    "Cells & tissues",
    "Microbes",
)

GITHUB = "https://github.com/deangeckt/biodraw"

# The supported way to drive the library. `docs/PLAN.md`: most figures will be
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


def section_id(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

def load_pages():
    """Every `site/content/<slug>.py`, as its `PAGE` dict."""
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

    unknown = {p["category"] for p in pages} - set(CATEGORIES)
    if unknown:
        plural = "y" if len(unknown) == 1 else "ies"
        raise SystemExit(f"unknown categor{plural}: {sorted(unknown)}. "
                         f"Add to CATEGORIES or fix the content module.")
    pages.sort(key=lambda p: (CATEGORIES.index(p["category"]), p["order"]))
    return pages


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
              "and the documentation rules in docs/PLAN.md.")


def check_images(pages):
    """Every referenced image must exist. See the module docstring."""
    missing = []
    for page in pages:
        folder = EXAMPLES / page["slug"]
        wanted = [page["hero"]]
        for section in page["sections"]:
            wanted += [img["src"] for img in section.get("images", ())]
        for name in wanted:
            if not (folder / name).is_file():
                missing.append(f"{page['slug']}/{name}")
    if missing:
        raise SystemExit("images referenced but not on disk:\n  " +
                         "\n  ".join(missing))


# ---------------------------------------------------------------------------
# chrome
# ---------------------------------------------------------------------------

def head(title, description):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
"""


def masthead(home="index.html"):
    return f"""<header class="masthead">
  <div class="masthead-inner">
    <a class="wordmark" href="{home}">biodraw</a>
    <nav class="masthead-links">
      <a href="{GITHUB}">GitHub</a>
      <a href="{GITHUB}/blob/main/docs/PLAN.md">Roadmap</a>
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
      <img class="shot" src="../examples/{page['slug']}/{page['hero']}"
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


def render_index(pages):
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
                  for p in pages)

    return (
        head("biodraw — bio-inspired vector drawings",
             "A browsable gallery of parametric biological drawings for "
             "matplotlib. Every shape is a few parameters and a seed.")
        + masthead()
        + f"""<main>
<section class="hero-copy">
  <h1>Bio-inspired vector drawings<br>for papers, posters and slides</h1>
  <p class="standfirst">Hand-drawn shapes, turned into maths, placeable
     anywhere. Every drawing below is a few parameters and a seed — not a file
     someone saved.</p>
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
                f'<img src="../examples/{page["slug"]}/{img["src"]}" '
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


def render_page(page, pages):
    order = [p["slug"] for p in pages]
    i = order.index(page["slug"])
    prev_p = pages[i - 1] if i else None
    next_p = pages[i + 1] if i + 1 < len(pages) else None

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
    build_url = f"{GITHUB}/blob/main/examples/{page['slug']}/build.py"
    intro = "".join(f'<p class="standfirst">{inline(t)}</p>'
                    for t in page.get("intro", ()))
    body = "\n".join(render_section(page, s) for s in page["sections"])

    return (
        head(f"{page['title']} — biodraw", page["tagline"])
        + masthead()
        + f"""<main class="detail">
<article>
  <p class="crumb"><a href="index.html">All examples</a>
     <span aria-hidden="true">·</span> {html.escape(page['category'])}</p>

  <h1>{html.escape(page['title'])}</h1>
  <p class="standfirst">{inline(page['tagline'])}</p>
  <p class="chips">{chips}</p>

  <figure class="hero plate zoomable">
    <img src="../examples/{page['slug']}/{page['hero']}"
         alt="{html.escape(page['hero_alt'])}">
    <figcaption>{html.escape(page['hero_alt'])}</figcaption>
  </figure>

  {intro}

{body}

  <p class="source-note">Every figure above is output, not a stored asset
     — <a href="{build_url}">the full script that draws them</a>.</p>

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

    pages = load_pages()
    check_images(pages)
    check_snippets(pages)
    check_catalog(pages)

    (SITE / "index.html").write_text(render_index(pages), encoding="utf-8",
                                     newline="\n")
    print("wrote site/index.html")
    for page in pages:
        out = SITE / f"{page['slug']}.html"
        out.write_text(render_page(page, pages), encoding="utf-8",
                       newline="\n")
        print(f"wrote site/{out.name}")

    print(f"\n{len(pages)} example(s) across "
          f"{len({p['category'] for p in pages})} categories.")

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

"""Rebuild every example's images.

    python tools/build_gallery.py            # rebuild all
    python tools/build_gallery.py spine      # only examples matching "spine"
    python tools/build_gallery.py --check    # rebuild, then fail on any diff
    python tools/build_gallery.py --quality debug     # big, for looking at

Each folder under `examples/` owns a `build.py` with a `main()`. This just
finds and runs them, so adding an example means adding a folder — there is no
list to keep in step.

`--check` is what CI runs: images must regenerate byte-identically, which is
both a determinism test (no unseeded randomness anywhere) and proof that the
committed images match the code that claims to produce them. It therefore
only means anything at the *committed* quality, which is why `--quality`
refuses to run with it.

`--quality debug` is the way to actually look at geometry: uncapped and
unquantized, several times the bytes, and not something to commit. See
`biodraw.io.QUALITY`.

Every run also reports **loose frames** — images whose drawing leaves a
quarter of the picture empty. See `FRAME_MIN` below for why that is a report
and not a failure.
"""

import argparse
import pathlib
import runpy
import subprocess
import sys

import matplotlib

matplotlib.use("Agg")

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"

sys.path.insert(0, str(ROOT))
from biodraw import io  # noqa: E402

# The frame check.
#
# *"the 'on a branch' eight image is almost only white space image."* True,
# and measurable: the ink in that PNG used 62% of its width. `save_compact`
# trims with `bbox_inches="tight"`, which trims to the **axes**, not to the
# ink — and the axes are equal-aspect, so a tall narrow drawing in a square
# figure keeps its white margins all the way into the committed file. Nothing
# was watching, and the three emptiest images in the whole catalog were all
# on the one page a reader had just complained about.
#
# The measure is the ink's bounding box as a fraction of the frame, per axis.
# The fix is to shape the figure like the data — see `_framed` in
# `examples/dendritic_spine/build.py` — or to tighten the limits.
#
# It reports rather than fails. A portrait of a round cell cannot fill a
# rectangle, so the practical floor is around 0.75 and a threshold sharp
# enough to fail on would be wrong about half the catalog. What it must not
# do is stay silent about a 0.62.
FRAME_MIN = 0.72


def ink_box(path):
    """`(width, height)` of the ink's bounding box, as fractions of the
    image. `None` for an image with no ink in it at all."""
    import matplotlib.image as mpimg
    import numpy as np

    a = mpimg.imread(str(path))
    if a.ndim == 2:                          # greyscale
        ink = a < 0.985
    else:
        ink = a[..., :3].min(axis=2) < 0.985
        if a.shape[-1] == 4:                 # ...and not transparent
            ink &= a[..., 3] > 0.02
    ys, xs = np.nonzero(ink)
    if not len(xs):
        return None
    return ((xs.max() - xs.min() + 1) / a.shape[1],
            (ys.max() - ys.min() + 1) / a.shape[0])


def report_frames(folders):
    """Print any image whose drawing leaves a quarter of its frame empty."""
    loose = []
    for folder in folders:
        for png in sorted(folder.glob("*.png")):
            box = ink_box(png)
            if box is None:
                loose.append((0.0, 0.0, png))
            elif min(box) < FRAME_MIN:
                loose.append((*box, png))
    if not loose:
        return
    print()
    print(f"Loose frames (ink under {FRAME_MIN:.0%} of an axis — the figure "
          f"is a different shape from the drawing on it):")
    for w, h, png in sorted(loose, key=lambda r: min(r[0], r[1])):
        print(f"  {min(w, h):.0%}  (w {w:.0%}, h {h:.0%})  "
              f"{png.relative_to(ROOT)}")


def builds(pattern=None):
    """Every `examples/*/build.py`, optionally filtered by name."""
    found = sorted(EXAMPLES.glob("*/build.py"))
    if pattern:
        found = [p for p in found if pattern.lower() in p.parent.name.lower()]
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pattern", nargs="?",
                    help="only build examples whose folder name matches")
    ap.add_argument("--check", action="store_true",
                    help="fail if rebuilding changes any tracked file")
    ap.add_argument("--quality", choices=sorted(io.QUALITY),
                    help="raster profile to build at "
                         f"(default: {io.DEFAULT_QUALITY})")
    args = ap.parse_args()

    if args.quality and args.check:
        print("--check compares against the committed images, so it only "
              "means anything at the committed quality. Drop one of them.",
              file=sys.stderr)
        return 2
    if args.quality:
        io.set_quality(args.quality)

    scripts = builds(args.pattern)
    if not scripts:
        print(f"no examples matched {args.pattern!r}", file=sys.stderr)
        return 1

    for script in scripts:
        print(f"== {script.parent.name}")
        # run_path rather than a subprocess: one interpreter, so a broken
        # import surfaces here with a real traceback.
        #
        # ...but one interpreter means one set of `plt.rcParams`, and every
        # build.py sets its own at import time. Without this context manager
        # they leak forward: whatever the previous example turned on stays on
        # for the next one, so an example's output depends on **what sorted
        # before it**. Adding `examples/bacteria/` — which turns the top and
        # right spines off, where `basket_cell` only sets the font size —
        # moved it ahead of `basket_cell` alphabetically and silently changed
        # that example's blueprint. Nothing had ever inserted itself earlier
        # in the order before, so the bug had never fired.
        #
        # `rc_context` restores the params on exit, so each script starts from
        # the same state and an example is reproducible on its own as well as
        # in a full run. That equivalence is what `--check` assumes.
        with matplotlib.rc_context():
            runpy.run_path(str(script), run_name="__main__")

    report_frames([script.parent for script in scripts])

    if not args.check:
        return 0

    diff = subprocess.run(
        ["git", "status", "--porcelain", "--", str(EXAMPLES)],
        cwd=ROOT, capture_output=True, text=True, check=False)
    changed = [ln for ln in diff.stdout.splitlines() if ln.strip()]
    if changed:
        print("\nRebuilding changed these files:", file=sys.stderr)
        for line in changed:
            print(f"  {line}", file=sys.stderr)
        print("\nEither commit the new images, or find the "
              "non-determinism that produced them.", file=sys.stderr)
        return 1

    print(f"\n{len(scripts)} example(s) rebuilt, no changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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

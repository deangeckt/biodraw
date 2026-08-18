"""Regenerate the geometry pins in `tests/shape_pins.json`.

    python tools/update_pins.py            # rewrite every pin
    python tools/update_pins.py --dry-run  # just report what would change

Run this only when a shape has changed **on purpose**, and say in the commit
what moved and why. The pins exist so a silent change cannot slip through; a
regeneration with no account of it defeats the point.
"""

import argparse
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve()
                       .parent.parent))

from tests import pins, shapes  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="report changes without writing")
    args = ap.parse_args()

    old = pins.load()
    new = {name: pins.digest(pts)
           for name, pts in sorted(shapes.collect().items())}

    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(n for n in set(old) & set(new) if old[n] != new[n])

    for name in added:
        print(f"  + {name}")
    for name in removed:
        print(f"  - {name}")
    for name in changed:
        diffs = ", ".join(f"{k} {old[name][k]!r} -> {new[name][k]!r}"
                          for k in sorted(new[name])
                          if old[name].get(k) != new[name][k])
        print(f"  ~ {name}: {diffs}")

    if not (added or removed or changed):
        print(f"{len(new)} pins, all unchanged.")
        return 0

    if args.dry_run:
        print(f"\n{len(added)} added, {len(removed)} removed, "
              f"{len(changed)} changed (dry run — nothing written).")
        return 1

    pins.save(new)
    print(f"\nwrote {pins.PINS.name}: {len(new)} pins "
          f"({len(added)} added, {len(removed)} removed, "
          f"{len(changed)} changed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

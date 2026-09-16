#!/usr/bin/env python3
"""Every Wikidata item the frozen extract points at.

OpenStreetMap carries 31 different `*:wikidata` keys in these wards, from
`brand:wikidata` on 25,413 features through `wikidata` on 15,715 to
`architect:wikidata` on 74. This collects the ids off all of them, so that the
dump can be read once for exactly the items that matter rather than for
everything.

    python3 src/qids.py --out tmp/qids.txt
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="tmp/qids.txt")
    a = ap.parse_args()
    ids = set()
    for t in ("planet_osm_point", "planet_osm_polygon", "planet_osm_line"):
        rows = build.pg(f"""
select distinct v from (
  select (each(tags)).key as k, (each(tags)).value as v from {t}) x
 where k like '%%wikidata' and v ~ '^Q[0-9]+$'""")
        ids |= {r[0] for r in rows}
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(ids)) + "\n")
    print(f"{len(ids):,} ids, wrote {a.out}")


if __name__ == "__main__":
    sys.exit(main())

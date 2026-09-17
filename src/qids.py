#!/usr/bin/env python3
"""Every Wikidata item the frozen extract points at.

OpenStreetMap carries 31 different `*:wikidata` keys in these wards, from
`brand:wikidata` on 25,407 features through `wikidata` on 15,715 to
`architect:wikidata` on 74. This collects the ids off all of them, so that the
dump can be read once for exactly the items that matter rather than for
everything.

Read from the extract with osmium, not through PostGIS. osm2pgsql drops the
relation types it has no rule for, and an id only that kind of object points
at would be missing from the scan and so from the file.

    python3 src/qids.py --out tmp/qids.txt
"""
import argparse
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402
import opl  # noqa: E402

QID = re.compile(r"^Q[0-9]+$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="tmp/qids.txt")
    ap.add_argument("--pbf", default=build.EXTRACT)
    a = ap.parse_args()

    tmp = os.path.join(build.BASE, "tmp")
    os.makedirs(tmp, exist_ok=True)
    small = os.path.join(tmp, "wikidata-keys.osm.pbf")
    text = os.path.join(tmp, "wikidata-keys.opl")
    # Every key ending in `wikidata`, which osmium matches with a leading
    # wildcard. Written as one filter so the extract is read once.
    subprocess.run(["osmium", "tags-filter", "--overwrite", "-o", small,
                    a.pbf, "*wikidata"], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["osmium", "cat", "-f", "opl", "--overwrite", "-o", text,
                    small], check=True, stdout=subprocess.DEVNULL)

    ids, keys = set(), set()
    for _, _, tags in opl.objects(text):
        for k, v in tags.items():
            if not k.endswith("wikidata"):
                continue
            keys.add(k)
            # A few features list several ids in one value, separated by a
            # semicolon, which is OpenStreetMap's way of saying "both".
            for part in v.split(";"):
                part = part.strip()
                if QID.match(part):
                    ids.add(part)

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(ids)) + "\n")
    print(f"{len(ids):,} ids off {len(keys)} keys, wrote {a.out}")


if __name__ == "__main__":
    sys.exit(main())

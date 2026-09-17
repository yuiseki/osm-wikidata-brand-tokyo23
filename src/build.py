#!/usr/bin/env python3
"""One record per brand, holding every way the two sources name it.

OpenStreetMap and Wikidata describe the same shops and neither reads the
other. A branded feature in OpenStreetMap carries `brand:wikidata`, which is a
Wikidata item id, and around it whatever names the mappers wrote: `brand:en`,
`brand:ja`, `name:ja_rm` in romaji, `name:ko`, `short_name:ja`. The Wikidata
item carries a label, a description and a list of aliases in each language,
written by different people for a different purpose.

Put side by side they disagree in ways that are the point of the file.
OpenStreetMap writes 7-Eleven as `7-ELEVEN` on 1,513 features and `7-Eleven`
on 428; Wikidata has never heard of the first and offers `7-11` and `711`,
which no map feature uses. The romaji are OpenStreetMap's alone: `Sutābakkusu`
on 123 features and `Sutah-bakkusu` on 72, two ways of writing one long vowel.

Counts are kept. A spelling on 1,513 features and a spelling on one are both
real and are not the same claim.

The extract is read with osmium rather than through PostGIS, which is a
correction. osm2pgsql promotes `name` and `brand` to columns of their own, so
the hstore column this file used to read held every name key except those two,
and they are the two that matter most: together they carried 6,529 of the
15,730 spellings in these wards, and 163 brands whose features spell the name
only those ways were missing from the file altogether. Reading the objects
directly also settles what one feature is without an opinion, where osm2pgsql
splits some relations into several rows and drops the types it has no rule for.

    python3 src/build.py --pbf tokyo23-260831.osm.pbf
"""
import argparse
import collections
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import opl  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Everything this needs is either in this repository or named by an
# environment variable. Nothing reaches into a sibling checkout by absolute
# path, because a reader who clones this cannot follow such a path and the
# file would not be rebuildable by anyone but its author.
EXTRACT = os.environ.get("EXTRACT", os.path.join(BASE, "tmp/tokyo23-260831.osm.pbf"))
WD = os.environ.get("WIKIDATA_ITEMS", os.path.join(BASE, "tmp/wikidata.jsonl"))

# Every key on a branded feature that is a way of saying its name. Taken from
# what the extract actually carries rather than from a list written here, so
# that a key nobody uses is not invented and one in use is not missed.
NAME_KEY = re.compile(r"^(brand|name|alt_name|int_name|official_name|"
                      r"short_name|loc_name|nat_name|reg_name|old_name)(:|$)")
QID = re.compile(r"^Q[0-9]+$")
# Not names: these say where the brand's page is, not what it is called.
NOT_A_NAME = {"brand:wikidata", "brand:wikipedia", "brand:website",
              "name:etymology:wikidata", "name:wikidata"}

SOURCE = {
    "osm": {
        "extract": "tokyo23-260831.osm.pbf",
        "md5": "44a4ba2182379c147f20a27ad1b513ef",
        "osm_base": "2026-08-30T23:50:59Z",
        "published_as": ("https://huggingface.co/datasets/yuiseki/"
                         "osm-tokyo23-src-2026-08"),
        "licence": "ODbL-1.0",
    },
    "wikidata": {
        "dump": "wikidata-20260831-all.json.bz2",
        "bytes": 102943257005,
        "licence": "CC0-1.0",
    },
}


def branded(pbf):
    """Every object carrying brand:wikidata, as (kind, id, tags).

    Two osmium passes into tmp, which are cheap on an 84 MiB extract and keep
    the reading of the data separate from the writing of the file.
    """
    tmp = os.path.join(BASE, "tmp")
    os.makedirs(tmp, exist_ok=True)
    small = os.path.join(tmp, "branded.osm.pbf")
    text = os.path.join(tmp, "branded.opl")
    subprocess.run(["osmium", "tags-filter", "--overwrite", "-o", small,
                    pbf, "brand:wikidata"], check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run(["osmium", "cat", "-f", "opl", "--overwrite", "-o", text,
                    small], check=True, stdout=subprocess.DEVNULL)
    # tags-filter also writes the nodes a matching way refers to, so that the
    # file stays usable as geometry. Those carry no tags and are not features.
    for kind, oid, tags in opl.objects(text):
        q = tags.get("brand:wikidata")
        if q and QID.match(q):
            yield kind, oid, tags


def osm_names_and_counts(pbf):
    """({qid: {key: {spelling: features}}}, {qid: features})."""
    names = collections.defaultdict(
        lambda: collections.defaultdict(collections.Counter))
    counts = collections.Counter()
    for _, _, tags in branded(pbf):
        q = tags["brand:wikidata"]
        counts[q] += 1
        for k, v in tags.items():
            if k in NOT_A_NAME or not NAME_KEY.match(k):
                continue
            names[q][k][v] += 1
    return names, dict(counts)


def wikidata():
    out = {}
    with open(WD, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            out[r["qid"]] = r
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "data/brands.jsonl"))
    ap.add_argument("--pbf", default=EXTRACT)
    a = ap.parse_args()

    names, counts = osm_names_and_counts(a.pbf)
    wd = wikidata()
    rows = []
    for q in sorted(names, key=lambda x: -counts.get(x, 0)):
        w = wd.get(q, {})
        rows.append({
            "qid": q,
            "features": counts.get(q, 0),
            "osm": {k: dict(sorted(v.items(), key=lambda kv: (-kv[1], kv[0])))
                    for k, v in sorted(names[q].items())},
            "wikidata": {
                "label": w.get("label", {}),
                "description": w.get("description", {}),
                "aliases": w.get("aliases", {}),
                "found": bool(w),
            },
        })
    with open(a.out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

    keys = collections.Counter(k for r in rows for k in r["osm"])
    forms = sum(len(v) for r in rows for v in r["osm"].values())
    print(f"{len(rows)} brands, {sum(r['features'] for r in rows):,} features")
    print(f"{forms:,} distinct spellings across {len(keys)} name keys")
    print(f"{sum(1 for r in rows if r['wikidata']['found'])} found in Wikidata")
    al = sum(1 for r in rows if r["wikidata"]["aliases"])
    print(f"{al} have at least one Wikidata alias")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    sys.exit(main())

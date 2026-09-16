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

    python3 src/build.py
"""
import argparse
import collections
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Everything this needs is either in this repository or named by an
# environment variable. Nothing reaches into a sibling checkout by absolute
# path, because a reader who clones this cannot follow such a path and the
# file would not be rebuildable by anyone but its author.
PG_DSN = os.environ.get(
    "PG_DSN", "host=localhost port=55433 dbname=osm user=osm password=osm")
WD = os.environ.get("WIKIDATA_ITEMS", os.path.join(BASE, "tmp/wikidata.jsonl"))

# Every key on a branded feature that is a way of saying its name. Taken from
# what the extract actually carries rather than from a list written here, so
# that a key nobody uses is not invented and one in use is not missed.
NAME_KEY = (r"^(brand|name|alt_name|int_name|official_name|short_name|"
            r"loc_name|nat_name|reg_name|old_name)(:|$)")
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


_conn = None


def pg(sql, params=None):
    global _conn
    import psycopg
    if _conn is None or _conn.closed:
        _conn = psycopg.connect(PG_DSN)
        _conn.read_only = True
        _conn.autocommit = True
    with _conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def osm_names():
    """{qid: {key: {spelling: features}}} from the frozen extract."""
    rows = pg(f"""
select wd, k, v, sum(n) from (
  select tags -> 'brand:wikidata' as wd, (each(tags)).key as k,
         (each(tags)).value as v, 1 as n
    from planet_osm_point where tags ? 'brand:wikidata'
  union all
  select tags -> 'brand:wikidata', (each(tags)).key, (each(tags)).value, 1
    from planet_osm_polygon where tags ? 'brand:wikidata'
  union all
  select tags -> 'brand:wikidata', (each(tags)).key, (each(tags)).value, 1
    from planet_osm_line where tags ? 'brand:wikidata'
) x
 where k ~ '{NAME_KEY}' and wd ~ '^Q[0-9]+$'
 group by 1, 2, 3""")
    out = collections.defaultdict(lambda: collections.defaultdict(dict))
    for q, k, v, n in rows:
        if k in NOT_A_NAME:
            continue
        out[q][k][v] = int(n)
    return out


def osm_features():
    """{qid: features}, so that a brand on one shop is not read as a brand on
    a thousand."""
    rows = pg("""
select wd, sum(n) from (
  select tags -> 'brand:wikidata' as wd, count(*) as n
    from planet_osm_point where tags ? 'brand:wikidata' group by 1
  union all
  select tags -> 'brand:wikidata', count(*)
    from planet_osm_polygon where tags ? 'brand:wikidata' group by 1
  union all
  select tags -> 'brand:wikidata', count(*)
    from planet_osm_line where tags ? 'brand:wikidata' group by 1
) x where wd ~ '^Q[0-9]+$' group by 1""")
    return {q: int(n) for q, n in rows}


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
    a = ap.parse_args()

    names, counts, wd = osm_names(), osm_features(), wikidata()
    rows = []
    for q in sorted(names, key=lambda x: -counts.get(x, 0)):
        w = wd.get(q, {})
        rows.append({
            "qid": q,
            "features": counts.get(q, 0),
            "osm": {k: dict(sorted(v.items(), key=lambda kv: -kv[1]))
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

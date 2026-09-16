#!/usr/bin/env python3
"""What Wikidata says about OpenStreetMap, in one pass over the dump.

Two sets of items, taken together because the dump costs an hour to read and
reading it twice for two questions would be an hour wasted.

`P1282` is "OpenStreetMap tag or key", and its value is the tag as
`shop=bakery`, without the `Tag:` prefix the OSM wiki uses. The item carrying
it is the concept, and its English label and aliases are the words a person
uses for the thing: `shop=florist` is a flower shop, which is the noun wanted
precisely because it is not the tag value.

The other set is every item the frozen extract points at. OpenStreetMap
carries 31 different `*:wikidata` keys in these twenty-three wards, from
`brand:wikidata` on 25,413 features through `wikidata` on 15,715 to
`architect:wikidata` on 74, and between them they name 9,706 items. Those are
not concepts behind tags; they are the brands, the places and the operators
themselves. Starbucks has no P1282 and never will.

Joined back to the extract, the second set is a record of the same concept
said several ways. OpenStreetMap already writes 7-Eleven as `7-ELEVEN` on
1,513 features and `7-Eleven` on 428, in `brand:en`, beside `セブン-イレブン`
in `brand:ja`; Wikidata adds its own label, its aliases and its description,
in English and Japanese. Neither source knows what the other says.

P1282 is "OpenStreetMap tag or key", and its value is the tag as `shop=bakery`,
without the `Tag:` prefix the OSM wiki uses. The item carrying it is the
concept, and its English label and aliases are the words a person uses for the
thing: `shop=florist` is a flower shop, which is the noun wanted precisely
because it is not the tag value.

The live API cannot supply this in bulk. WDQS was rate limited to one request
a minute during an outage, and the search API answers 429 after a few dozen
calls. The dump can, and reading it is the whole cost, so this pass takes
everything that might be wanted rather than what is wanted today.

The dump is one JSON array, one item per line, bz2. It is never decompressed
to disk: 95 GiB compressed is well over a terabyte open, and there is not that
much room. lbzip2 reads it across all cores; bzip2 would take hours on one.

    python3 src/qids.py --out tmp/qids.txt
    python3 src/wikidata_osm_tags.py --dump <the dump> --qids tmp/qids.txt \
        --out tmp/wikidata.jsonl
"""
import argparse
import json
import os
import subprocess
import sys
import time

LANGS = ("en", "ja")


def reader(path, jobs):
    """Lines of the dump, decompressed across cores."""
    tool = "lbzip2" if _have("lbzip2") else "bzip2"
    cmd = ([tool, "-dc", "-n", str(jobs), path] if tool == "lbzip2"
           else [tool, "-dc", path])
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1 << 22)
    for line in p.stdout:
        yield line
    p.wait()


def _have(x):
    return subprocess.run(["which", x], capture_output=True).returncode == 0


def qid_of(raw):
    """The item id, off the front of the line, without parsing the rest."""
    i = raw.find(b'"id":"Q')
    if i < 0:
        return None
    j = raw.find(b'"', i + 7)
    return raw[i + 6:j].decode()


def wanted(entity):
    """The item's P1282 values, or None. Checked on the raw line first, so
    that the 99.9% of items without it are never parsed."""
    claims = entity.get("claims", {}).get("P1282")
    if not claims:
        return None
    out = []
    for c in claims:
        try:
            v = c["mainsnak"]["datavalue"]["value"]
        except (KeyError, TypeError):
            continue
        if isinstance(v, str):
            out.append(v)
    return out or None


def strip(entity, tags, why):
    def lang(field):
        d = entity.get(field, {})
        return {l: d[l]["value"] for l in LANGS if l in d}

    aliases = {}
    for l in LANGS:
        got = entity.get("aliases", {}).get(l) or []
        if got:
            aliases[l] = [a["value"] for a in got]
    return {"qid": entity.get("id"), "why": why, "osm": sorted(set(tags)),
            "label": lang("labels"), "description": lang("descriptions"),
            "aliases": aliases}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True)
    ap.add_argument("--qids", help="one Q-id per line; items to take as well "
                                   "as the ones carrying P1282")
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 4)))
    ap.add_argument("--limit", type=int, default=0, help="stop after N lines")
    a = ap.parse_args()

    qids = set()
    if a.qids:
        qids = {l.strip() for l in open(a.qids) if l.strip()}
        print(f"{len(qids):,} ids wanted from the extract")
    n = kept = 0
    t0 = time.time()
    with open(a.out, "w", encoding="utf-8") as out:
        for raw in reader(a.dump, a.jobs):
            n += 1
            # Both tests on bytes, before any JSON is parsed. Fewer than one
            # item in a thousand is wanted and parsing all of them would
            # dominate the run.
            has_tag = b'"P1282"' in raw
            q = qid_of(raw) if qids else None
            in_extract = q is not None and q in qids
            if not (has_tag or in_extract):
                if a.limit and n >= a.limit:
                    break
                if n % 2_000_000 == 0:
                    _tick(n, kept, t0)
                continue
            try:
                e = json.loads(raw.rstrip().rstrip(b","))
            except ValueError:
                continue
            tags = wanted(e) if has_tag else None
            why = ([] + (["p1282"] if tags else [])
                   + (["in_extract"] if in_extract else []))
            if not why:
                continue
            out.write(json.dumps(strip(e, tags or [], why),
                                 ensure_ascii=False) + "\n")
            kept += 1
            if a.limit and n >= a.limit:
                break
    _tick(n, kept, t0)
    print(f"wrote {a.out}")


def _tick(n, kept, t0):
    dt = time.time() - t0
    print(f"  {n:,} lines, {kept:,} kept, {dt/60:.1f} min, "
          f"{n/max(dt,1):,.0f} lines/s", flush=True)


if __name__ == "__main__":
    sys.exit(main())

# osm-wikidata-brand

Every way two independent sources name the same shop chain, in the
twenty-three special wards of Tokyo.

729 brands, 25,149 features, 9,201 distinct spellings across 80 name keys.

## Where it comes from

A branded feature in OpenStreetMap carries `brand:wikidata`, which is a
Wikidata item id, and around it whatever names the mappers wrote. The Wikidata
item carries a label, a description and aliases in each language, written by
different people for a different purpose. Neither source reads the other.

    OpenStreetMap   tokyo23-260831.osm.pbf, the twenty-three wards cut from
                    the planet file of 2026-08-31
    Wikidata        wikidata-20260831-all.json.bz2, the same day

The two dates are the same day on purpose. A brand added to OpenStreetMap in
September and to Wikidata in October would otherwise look like a source
disagreeing with itself.

## A record

```json
{
  "qid": "Q259340",
  "features": 1942,
  "osm": {
    "brand:en": {"7-ELEVEN": 1513, "7-Eleven": 428},
    "brand:ja": {"セブン-イレブン": 1941},
    "name:ja_rm": {"Sebun Irebun": 1454, "Rōson": 2},
    "name:ko": {"세븐일레븐": 1490}
  },
  "wikidata": {
    "label": {"en": "7-Eleven", "ja": "セブン-イレブン"},
    "description": {"en": "chain of convenience stores"},
    "aliases": {"en": ["Seven Eleven", "7-11", "711"], "ja": ["セブンイレブン"]},
    "found": true
  }
}
```

`osm` is every name key on a feature of that brand, with how many features
carry each spelling. The counts matter: a spelling on 1,513 features and a
spelling on one are both real and are not the same claim.

## What it is for

Matching a name a person types to a thing on a map. `7-ELEVEN`, `7-Eleven`,
`Seven Eleven`, `7-11`, `711`, `セブン-イレブン`, `セブンイレブン` and
`Sebun Irebun` are one shop, and no single source has all eight.

The Japanese side is where the two sources are furthest apart. Romaji are
OpenStreetMap's alone, and they disagree with each other about long vowels:
`Sutābakkusu` on 123 features and `Sutah-bakkusu` on 72. Abbreviations are
Wikidata's alone: `スタバ` is what people say and no map feature is tagged
with it.

## Read this first

`docs/what-is-in-here-and-what-is-wrong-with-it.md`. A name key is not a
brand key, one chain has two Wikidata items, and 143 of the 729 brands appear
on a single feature. Nothing is filtered out over any of it; the keys and the
counts are in the record so that a reader can filter for themselves.

## Building it

Everything is here. Nothing reaches into another checkout by absolute path,
because a reader who clones this could not follow such a path and the file
would be rebuildable by its author alone.

Two inputs have to be in place first, and both are named rather than assumed.

The frozen extract, in PostGIS. `osm-tokyo23-src-2026-08` builds it: fetch the
planet file of 2026-08-31, run its numbered scripts, and the database comes up
on port 55433. `PG_DSN` points somewhere else if it is somewhere else.

The Wikidata dump, 96 GiB, from
`https://dumps.wikimedia.org/wikidatawiki/entities/20260831/`. Do not
decompress it: 96 GiB compressed is well over a terabyte open. `lbzip2` reads
it across all cores and `bzip2` takes hours on one.

In the pinned image, which is where it was built:

```sh
cd docker && docker compose build
docker compose run --rm build sh -c '
  cd /work
  python3 src/qids.py --out tmp/qids.txt
  python3 src/wikidata_osm_tags.py --dump /dump/wikidata-20260831-all.json.bz2 \
      --qids tmp/qids.txt --out tmp/wikidata.jsonl
  python3 src/build.py'
```

Debian bookworm at a fixed digest, python3 3.11.2, lbzip2 2.5 and psycopg
3.3.2, each named in `docker/Dockerfile`. Running the three steps inside the
image reproduced the run made outside it byte for byte, which is the only
reason to believe the pins are the right ones.

Or on the host, if those versions are what the host has:

```sh
python3 src/qids.py --out tmp/qids.txt              # 9,706 ids, seconds
python3 src/wikidata_osm_tags.py \
    --dump .../wikidata-20260831-all.json.bz2 \
    --qids tmp/qids.txt --out tmp/wikidata.jsonl    # 48 min, 121.5M items
python3 src/build.py                                # seconds
```

The middle step reads 121,519,241 items at about 42,000 a second and keeps
13,288: the 9,690 the extract points at, and 3,594 more that carry Wikidata's
property `P1282`, which maps a concept to an OpenStreetMap tag. It decides on
bytes before parsing, because fewer than one item in a thousand is wanted and
parsing all of them would be the whole cost.

Checksums, so that a rebuild can be told from a coincidence:

    tokyo23-260831.osm.pbf  md5 44a4ba2182379c147f20a27ad1b513ef
    wikidata-20260831-all.json.bz2
                            md5  f99e3ee0778ffe1c3b54fa5dbc6ce395
                            sha1 b24eea0dee9f2fbe7ca70e6efe3209eb69bc48af
                            102,943,257,005 bytes

Both are the figures the sources publish, not the figures of the local copy.
The copy that was actually read was checked against the first of them and
matched, so the dump behind this file is the dump Wikimedia put out.

## Two licences in one file

This joins an ODbL source to a CC0 one, so which field came from where is
part of the data rather than a footnote. `data/provenance.yaml` says it field
by field, and the record says it structurally: everything under `osm` is from
OpenStreetMap and everything under `wikidata` is from Wikidata.

    OpenStreetMap   tokyo23-260831.osm.pbf, ODbL-1.0
                    qid, features, and every spelling under `osm`
    Wikidata        wikidata-20260831-all.json.bz2, CC0-1.0
                    label, description and aliases under `wikidata`

Wikidata's CC0 covers structured data in the main, property and lexeme
namespaces; text elsewhere on the site is CC BY-SA 4.0. Everything taken here
is main-namespace structured data. Wikidata asks for no attribution.

The file contains content derived from OpenStreetMap, so redistributing it
means complying with ODbL. That is two obligations and not one: credit
OpenStreetMap, and make clear the data is under ODbL.

    (c) OpenStreetMap contributors, available under the Open Database License.
    https://www.openstreetmap.org/copyright

The CC0 half carries no conditions of its own, and sitting beside ODbL content
does not give it any. Nor does the reverse: the ODbL obligations do not
disappear because CC0 content is alongside.

Whether joining the two on a shared key makes a Derivative Database or a
Collective Database under ODbL section 4.5 is not settled here. They are
joined into one record rather than shipped in one archive, which is why the
stricter reading is the one taken.

That is a position and not legal advice, and it was reached without reading
the ODbL legal text: the OpenStreetMap copyright page does not draw the
distinction and points elsewhere for it. `data/provenance.yaml` says so, and
says where to look.

The code in `src/` is MIT.

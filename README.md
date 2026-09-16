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

Needs the frozen extract in PostGIS and the Wikidata items already pulled out
of the dump.

```sh
python3 src/build.py
```

## Two licences in one file

This joins an ODbL source to a CC0 one, so which field came from where is
part of the data rather than a footnote. `data/provenance.yaml` says it field
by field, and the record says it structurally: everything under `osm` is from
OpenStreetMap and everything under `wikidata` is from Wikidata.

    OpenStreetMap   tokyo23-260831.osm.pbf, ODbL-1.0
                    qid, features, and every spelling under `osm`
    Wikidata        wikidata-20260831-all.json.bz2, CC0-1.0
                    label, description and aliases under `wikidata`

The file contains content derived from OpenStreetMap, so redistributing it
means complying with ODbL:

    (c) OpenStreetMap contributors, available under the Open Database License.
    https://www.openstreetmap.org/copyright

The CC0 half carries no conditions of its own, and sitting beside ODbL content
does not give it any. Nor does the reverse: the ODbL obligations do not
disappear because CC0 content is alongside.

Whether joining the two on a shared key makes a Derivative Database or a
Collective Database under ODbL section 4.5 is not settled here. They are
joined into one record rather than shipped in one archive, which is why the
stricter reading is the one taken. That is a position, not legal advice, and
`data/provenance.yaml` says so in as many words.

The code in `src/` is MIT.

---
license: odbl
language:
- en
- ja
task_categories:
- text-classification
- sentence-similarity
tags:
- openstreetmap
- wikidata
- entity-linking
- name-matching
- brands
- tokyo
- japanese
size_categories:
- n<1K
---

# osm-wikidata-brand

Every way two independent sources name the same shop chain, in the
twenty-three special wards of Tokyo.

729 brands, 25,149 features, 9,201 distinct spellings across 80 name keys.

A branded feature in OpenStreetMap carries `brand:wikidata`, which is a
Wikidata item id, and around it whatever names the mappers wrote. The Wikidata
item carries a label, a description and aliases in each language, written by
different people for a different purpose. Neither source reads the other, and
where they differ is the point of the file.

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
    "description": {"en": "chain of convenience stores", "ja": "コンビニエンスストアチェーン"},
    "aliases": {"en": ["Seven Eleven", "7-11", "711"], "ja": ["セブンイレブン"]},
    "found": true
  }
}
```

## The fields

| field | | |
|---|---|---|
| `qid` | string | the Wikidata item id, and the key the two sources are joined on. Always present, always `Q` followed by digits |
| `features` | integer | how many features in the extract carry this `brand:wikidata`. 1 to 2,334; 143 brands have exactly 1 |
| `osm` | object | from OpenStreetMap. `{name key: {spelling: how many features use it}}`. 80 keys occur; a record has between 1 and 2,515 spellings |
| `wikidata` | object | from Wikidata. Four fields, below |

Inside `wikidata`:

| field | | |
|---|---|---|
| `label` | `{lang: string}` | the item's label. `en` on 726 records, `ja` on 701 |
| `description` | `{lang: string}` | `en` on 709, `ja` on 575 |
| `aliases` | `{lang: [string]}` | other names Wikidata records. `ja` on 466, `en` on 398 |
| `found` | boolean | whether the item was in the dump at all. False on 1 record, where OpenStreetMap points at an id Wikidata does not have |

Only `en` and `ja` were taken. The item may hold a hundred other languages and
they are not here.

The keys inside `osm` are whatever the extract carries. The commonest:

    name:en       on 697 brands        brand:en      on 590
    name:ja       on 646               brand:ja      on 586
    name:ja_rm    on 221   romaji      name:ja-Latn  on 183
    name:ja-Hira  on 177   hiragana    name:ko       on 68

A count is not decoration. A spelling on 1,513 features and a spelling on one
are both in the file and are not the same claim, and the counts are how a
reader tells a chain's name from one shop's.

## What each source knows that the other does not

OpenStreetMap has spellings Wikidata does not:

    7-ELEVEN            on 1,513 features   Wikidata has only 7-Eleven
    LAWSON              on 823
    DOUTOR, DCS         on 297 each         DCS is what the shop sign says
    Sutābakkusu         on 123              two ways of writing one long
    Sutah-bakkusu       on 72               vowel, in one chain

Wikidata has aliases OpenStreetMap does not:

    7-Eleven    Seven Eleven, 7-11, 711
    FamilyMart  Famima, Family Mart, FM
    Lawson      LAWSON, INC.
    Starbucks   スタバ

Neither list corrects the other. Someone looking for a 7-Eleven might type
`7-ELEVEN`, `7-Eleven`, `Seven Eleven`, `7-11`, `711`, `セブン-イレブン`,
`セブンイレブン` or `Sebun Irebun`, and only the union has all eight.

The Japanese side is where they are furthest apart. Romaji are OpenStreetMap's
alone and disagree with themselves about long vowels. Abbreviations are
Wikidata's alone: `スタバ` is what people say and no feature is tagged with it.

## Read this before using it

Three things look like defects and are not. A name key is not a brand key, and
a HELLO CYCLING port standing in a convenience store car park carries the
cycle scheme's `brand:wikidata` beside the shop's `name`. One chain has two
Wikidata items. 143 of the 729 brands appear on a single feature.

Nothing is filtered out over any of it; the keys and the counts are in the
record so that a reader can filter for themselves. The repository's
`docs/what-is-in-here-and-what-is-wrong-with-it.md` has the detail.

## Where it comes from

    OpenStreetMap   tokyo23-260831.osm.pbf, the twenty-three wards cut from
                    the planet file of 2026-08-31
                    md5 44a4ba2182379c147f20a27ad1b513ef
    Wikidata        wikidata-20260831-all.json.bz2, the same day
                    md5 f99e3ee0778ffe1c3b54fa5dbc6ce395

The same day on purpose: a brand added to one in September and the other in
October would look like the sources disagreeing when the only difference is
when each was read. Both checksums are the ones the sources publish, and the
local copies were checked against them.

Built in a pinned image, Debian bookworm at a fixed digest with python3
3.11.2, lbzip2 2.5 and psycopg 3.3.2. Running the three build steps inside it
reproduced the run made outside it byte for byte. `provenance.yaml` beside
this file has the commands, the versions and the item counts.

## Two licences meet here

    OpenStreetMap   ODbL-1.0    `qid`, `features`, everything under `osm`
    Wikidata        CC0-1.0     everything under `wikidata`

The file contains content derived from OpenStreetMap, so redistributing it
means complying with ODbL, which asks two things: credit OpenStreetMap, and
make clear the data is under ODbL.

    (c) OpenStreetMap contributors, available under the Open Database License.
    https://www.openstreetmap.org/copyright

Wikidata's CC0 covers structured data in the main, property and lexeme
namespaces, which is all that was taken, and asks for no attribution. Sitting
beside ODbL content gives it no conditions, and sitting beside CC0 content
removes none from the OpenStreetMap side.

Whether the join makes a Derivative or a Collective Database under ODbL 4.5 is
not settled here, and `provenance.yaml` says so and says where to look.

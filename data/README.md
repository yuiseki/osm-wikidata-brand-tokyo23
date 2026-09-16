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

# osm-wikidata-brand-tokyo23

Every way two independent sources name the same shop chain, in the
twenty-three special wards of Tokyo, and the name of every shop in those
chains.

729 brands, 25,149 features, 9,201 distinct values across 80 keys.

The wards are in the name because the counts are of them. `7-ELEVEN` on 1,513
features is a fact about Tokyo and not about the world.

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
| `osm` | object | from OpenStreetMap. `{key: {value: how many features carry it}}`. 80 keys occur; a record has between 1 and 2,515 values. The keys are two different things and the next section says which |
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

## `brand:*` is the chain. `name:*` is the shop

Two kinds of key are in `osm` and they answer different questions.

`brand:*` is what the chain is called. `brand:ja` on 1,252 FamilyMart
features says `ファミリーマート` on every one of them.

`name:*` is what this particular feature is called, which is usually the
chain's name and sometimes the chain's name with a branch on the end:

    name:ja   ファミリーマート            1251
    name:ja   ファミリーマート 西池袋店         1
    name:ja   マクドナルド                232
    name:ja   マクドナルド下丸子駅前店           1

`マクドナルド下丸子駅前店` is not another way of writing McDonald's. It is a
McDonald's, in Shimomaruko.

How far the two diverge, by how many values appear on exactly one feature:

    name           7,532 values    5,910 on one feature    78%
    brand          1,307             231                   18%
    official_name    156              71                   46%
    alt_name         104              53                   51%

So a reader after spelling variants wants `brand:*`, and a reader after
concrete instances of a brand wants `name:*`. Both are here and the counts
separate them: a value on 1,251 features is what the chain is called, a value
on one is what one shop is called.

Neither is filtered out. The branch names are the reason: they are a list of
real Tokyo shops, tied to a chain and to a Wikidata id, and that is worth
having even though it is not what the rest of the file is.

Where the extract's keys fall:

    name:en       on 697 brands        brand:en      on 590
    name:ja       on 646               brand:ja      on 586
    name:ja_rm    on 221   romaji      name:ja-Latn  on 183
    name:ja-Hira  on 177   hiragana    name:ko       on 68

The romaji are only reachable through a name key: `brand:ja_rm` is almost
never used, so `Famirī Mato` on 313 features and `Dotōru Kōhī Shoppu` on 207
would be lost if the name keys went.

## The columns on the Hub

The file is one JSON object per brand and the Hub wants a table, so the
frequently read fields become columns and the nested ones stay JSON. A brand
has up to 2,515 values under up to eighty keys, and no column arrangement
survives that.

| column | |
|---|---|
| `qid` `features` | the id and the feature count |
| `label_en` `label_ja` `description_en` `description_ja` | from Wikidata, read as they are |
| `osm` | JSON. `{key: {value: count}}`, the whole OpenStreetMap side |
| `aliases` | JSON. `{lang: [string]}` from Wikidata |
| `record` | JSON. The whole object, lossless |

`json.loads` the JSON columns. Nothing in the repository's `brands.jsonl` is
missing from `record`.

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

Three things look like defects and are not. A HELLO CYCLING port standing in a
convenience store car park carries the cycle scheme's `brand:wikidata` beside
the shop's `name`, so 145 features appear to say that HELLO CYCLING is called
Seven-Eleven. One chain has two Wikidata items. 143 of the 729 brands appear
on a single feature.

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

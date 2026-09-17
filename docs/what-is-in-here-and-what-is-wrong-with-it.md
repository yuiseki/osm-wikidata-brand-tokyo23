# What is in here, and what is wrong with it

Read before using it. Two of the three things below look like defects in this
file and are not: they are what the data says, recorded rather than tidied.

## A name key is not a brand key, and that is not a fault

The heading used to say only the first half.

Every record holds nine families of key, and they do not mean the same thing.

    name           2,249 spellings    what this feature is called
    brand          1,238              what the chain is called
    official_name    132
    alt_name         101
    short_name        60
    int_name          17
    old_name           8
    reg_name           2
    loc_name           1

`brand:en` on a FamilyMart says the chain is called FamilyMart. `name:en` on
the same feature usually says the same thing, and sometimes does not: it may
be `FamilyMart Nishi-Ikebukuro`, which is this shop and not the chain.

Counted across the file, 5,910 of the 7,532 values under a `name` key appear
on exactly one feature, against 231 of the 1,307 under a `brand` key. The
name keys are 78% singletons and the brand keys are 18%.

Those singletons are branch names: `マクドナルド下丸子駅前店`,
`ファミリーマート 西池袋店`. They are not other ways of writing McDonald's or
FamilyMart; each is one shop. That makes them useless as spelling variants and
useful as something else, which is a list of real shops tied to a chain and to
a Wikidata id. Both readings are served by keeping them and saying which key
is which.

Where it goes furthest wrong is the share cycle. A HELLO CYCLING port often
stands in a convenience store car park, so the feature carries
`brand:wikidata=Q91231927` for the cycle scheme and `name=Seven-Eleven` for
the shop it is outside. Read as brand names, 145 features say that HELLO
CYCLING is called Seven-Eleven.

Nothing is filtered out over this. The key is in the record, so a reader who
wants brand names can take the `brand:*` keys and a reader who wants feature
names can take the rest. What would have been lost by filtering is the romaji:
`name:ja_rm` carries 5,893 spellings and `brand:ja_rm` carries almost none, so
`Famirī Mato` on 313 features and `Dotōru Kōhī Shoppu` on 207 are only
reachable through a name key.

The counts are the way through. A spelling on 313 of a chain's 1,252 features
is the chain's name; a spelling on one of them is a shop's.

## One brand, two items

    FamilyMart   Q11247682 on 1,252 features,  Q1191685 on 295
    Shell        Q110716465 on 35,             Q154950 on 5

Mappers disagree about which Wikidata item a chain is. Both ids are in the
file with the features that carry them, because merging them would be
asserting an answer to a question Wikidata itself has two entries for.

## Half the brands are almost absent

    256 of the 892 appear on exactly one feature
    298 appear on ten or more

A brand on one feature contributes one spelling and no evidence about which
spelling is usual. The `features` field is on every record so that a reader
can require whatever support they need.

## What the two sources each know that the other does not

This is the reason the file exists rather than a caveat.

OpenStreetMap has spellings Wikidata does not:

    7-ELEVEN      on 1,513 features   Wikidata has only 7-Eleven
    LAWSON        on 823
    DOUTOR, DCS   on 297 each         DCS is the shop sign
    Sutābakkusu, Sutah-bakkusu        two ways of writing one long vowel

Wikidata has aliases OpenStreetMap does not:

    7-Eleven      Seven Eleven, 7-11, 711
    FamilyMart    Famima, Family Mart, FM
    Lawson        LAWSON, INC.

`スタバ` is in both, which is easy to miss: it is a Wikidata alias for
Starbucks and it is also on three of that brand's 283 features, under
`short_name`. An abbreviation reaches Wikidata once and reaches the map only
as often as some mapper wrote it.

Neither list is a correction of the other. A person looking for a 7-Eleven
might type any of `7-ELEVEN`, `7-Eleven`, `Seven Eleven`, `7-11`, `711`,
`セブン-イレブン`, `セブンイレブン` or `Sebun Irebun`, and only the union of the
two sources has all of them.

## Three brands point at Wikidata items that are not there

    Q88485610   7 features
    Q61799370   1
    Q11228227   1

Their records carry `"found": false` and an empty label, description and
aliases. An id in OpenStreetMap is what a mapper typed, and Wikidata deletes
and merges items without telling anyone who linked to one. Nothing is dropped
over it: the OpenStreetMap half of those records is as good as any other, and
`found` is in the record so a reader can require the other half.

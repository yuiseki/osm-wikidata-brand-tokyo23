# What changed in the second version, and why the first was wrong

The first version read the extract through PostGIS. osm2pgsql had loaded it,
and the build asked the `tags` hstore column for every key that is a way of
writing a name.

osm2pgsql promotes some tags to columns of their own. `name` and `brand` are
two of them, and `--hstore` puts into `tags` only what is left over. So the
query could not see them, and no error was raised: a missing key looks exactly
like a key nobody used.

They are the two keys that matter most in a dataset about how a brand is
written.

    name       5,590 spellings
    name:ja    4,869
    name:en    1,488
    brand        939

    name and brand together   6,529 of 15,730

163 brands were missing from the file entirely, because a brand appears only
if some feature carries a name key the query could see, and for those 163
every feature spells the name only as `name` or `brand`.

7-Eleven, which the README uses as its example, lost this:

    brand   7-ELEVEN 1512, セブン-イレブン 428, 7-Eleven 1
    name    セブン-イレブン 1941, セブン-イレブン;平和台駅 1

`brand` holding both `7-ELEVEN` and `セブン-イレブン` is the disagreement this
dataset exists to record, and the first version could not show it.

## What replaced it

The extract is read with `osmium tags-filter` and `osmium cat -f opl`, one
line per object, tags and all. No database, and `docker/Dockerfile` pins
osmium-tool instead of psycopg.

This also settles what one feature is. osm2pgsql splits some relations into
several rows and drops the relation types it has no rule for; an object in OPL
is an object. Four brands are counted lower here for that reason, and one of
them, Q116264906, is a single relation that osm2pgsql had made three rows of.

## Nothing was lost

Checked rather than assumed, record by record against the published first
version:

    brands that disappeared                     0
    key-and-brand pairs that disappeared        0
    spellings that disappeared                  0
    brands whose feature count fell             4, all of them relations
                                                counted once instead of twice

    brands gained                             163
    spellings gained                        6,529
    name keys gained                            2

## What did not change

The sources, their dates, their checksums, and the licensing. The extract is
the same `tokyo23-260831.osm.pbf` with md5 44a4ba2182379c147f20a27ad1b513ef,
and the Wikidata dump is the same one of 2026-08-31.

The Wikidata side was rescanned, because reading the extract with osmium finds
101 more `*:wikidata` ids than reading it through PostGIS did, for the same
reason: the ids on objects that tool never loaded.

#!/usr/bin/env python3
"""Objects and their tags, read from osmium's OPL.

One line is one object, which is the whole reason for using it. A dataset
that counts how many features carry a spelling has to say what one feature is,
and OPL answers that without an opinion: a node is one, a way is one, a
relation is one. Loading the same data through osm2pgsql answers differently,
because that tool splits some relations into several rows, drops relation
types it has no rule for, and turns a closed way into either a line or a
polygon depending on its tags.

Escaping is `%XXXX%` around the hex codepoint, which is how a Japanese name
survives a format whose separators are comma and equals sign.
"""
import re

UNESCAPE = re.compile(r"%([0-9a-fA-F]+)%")


def _unescape(s):
    return UNESCAPE.sub(lambda m: chr(int(m.group(1), 16)), s)


def objects(path):
    """(kind, id, {key: value}) for every object in an OPL file."""
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            kind = {"n": "node", "w": "way", "r": "relation"}.get(line[0])
            if kind is None:
                continue
            head, _, rest = line.partition(" ")
            oid = head[1:]
            tags = {}
            for field in rest.split(" "):
                if field.startswith("T"):
                    body = field[1:]
                    if body:
                        for pair in body.split(","):
                            k, _, v = pair.partition("=")
                            if k:
                                tags[_unescape(k)] = _unescape(v)
                    break
            yield kind, oid, tags

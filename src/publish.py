#!/usr/bin/env python3
"""Push the brands and the files that explain them to the Hugging Face Hub.

The table is one row per brand. Three of its columns hold JSON rather than
strings, because `osm` is a map of maps and `label` is a map of languages, and
flattening either into columns would make eighty of them, most empty. The row
is not lossy: `record` carries the whole object.

    python3 src/publish.py             # dry run, prints the schema
    python3 src/publish.py --push      # uploads
"""
import argparse
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "yuiseki/osm-wikidata-brand-tokyo23"

# Read as they are.
PLAIN = ["qid", "label_en", "label_ja", "description_en", "description_ja"]
# Read as JSON. A brand has up to 2,515 values under up to eighty keys and no
# column arrangement survives that.
AS_JSON = ["osm", "aliases", "record"]


def rows(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            w = r["wikidata"]
            out.append({
                "qid": r["qid"],
                "features": r["features"],
                "label_en": w["label"].get("en"),
                "label_ja": w["label"].get("ja"),
                "description_en": w["description"].get("en"),
                "description_ja": w["description"].get("ja"),
                "osm": json.dumps(r["osm"], ensure_ascii=False, sort_keys=True),
                "aliases": json.dumps(w["aliases"], ensure_ascii=False,
                                      sort_keys=True),
                "record": json.dumps(r, ensure_ascii=False, sort_keys=True),
            })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(BASE, "data/brands.jsonl"))
    ap.add_argument("--card", default=os.path.join(BASE, "data/README.md"))
    ap.add_argument("--extra", nargs="*", default=[
        os.path.join(BASE, "LICENSE"),
        os.path.join(BASE, "data/provenance.yaml")])
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()

    import datasets

    table = rows(a.data)
    features = datasets.Features(dict(
        {k: datasets.Value("string") for k in PLAIN + AS_JSON},
        features=datasets.Value("int64")))
    ds = datasets.Dataset.from_list(table, features=features)
    print(ds)
    print(f"{len(table)} brands, "
          f"{os.path.getsize(a.data)/1e3:.0f} KB of jsonl")
    for p in [a.card] + a.extra:
        if not os.path.exists(p):
            raise SystemExit(f"missing {p}")
    print(f"card {os.path.relpath(a.card, BASE)}, plus "
          + ", ".join(os.path.relpath(p, BASE) for p in a.extra))
    if not a.push:
        print("dry run. pass --push to upload")
        return 0

    from huggingface_hub import DatasetCard, HfApi

    api = HfApi()
    api.create_repo(a.repo, repo_type="dataset", exist_ok=True)
    # Card first: push_to_hub writes dataset_info into its front matter and
    # pushing the card afterwards would erase it.
    DatasetCard(open(a.card, encoding="utf-8").read()).push_to_hub(
        a.repo, repo_type="dataset")
    for p in a.extra:
        api.upload_file(path_or_fileobj=p, path_in_repo=os.path.basename(p),
                        repo_id=a.repo, repo_type="dataset")
    ds.push_to_hub(a.repo)
    print(f"pushed to {a.repo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

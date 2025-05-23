#!/usr/bin/env python3

import os
import json
import argparse
from tqdm import tqdm
from whoosh import index
from whoosh.fields import Schema, ID, TEXT, KEYWORD


def get_schema():
    return Schema(
        word=ID(stored=True),
        lang=ID(stored=True),
        pos=ID(stored=True),
        etymology_text=TEXT(stored=True),
        etymology_langs=KEYWORD(stored=True, commas=True, lowercase=True),
        glosses=TEXT(stored=True),
        related_words=KEYWORD(stored=True, commas=True, lowercase=True),
        cognates=KEYWORD(stored=True, commas=True, lowercase=True),
    )


def create_or_open_index(index_dir):
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
        ix = index.create_in(index_dir, schema=get_schema())
    else:
        ix = index.open_dir(index_dir)
    return ix


def build_index(jsonl_path, index_dir):
    ix = create_or_open_index(index_dir)
    writer = ix.writer()

    # Iterate with progress bar
    with open(jsonl_path, encoding="utf-8") as f:
        for line in tqdm(f, desc="Indexing entries", unit="entry"):
            entry = json.loads(line)
            related = []
            cognates = []
            for tpl in entry.get("etymology_templates", []):
                name = tpl.get("name", "").lower()
                args = tpl.get("args", {})
                if name in ("inh", "bor") and args.get("3"):
                    src = args["3"].strip().lower()
                    related.append(src)
                elif name in ("der", "cog") and args.get("2"):
                    src = args["2"].strip().lower()
                    related.append(src)
                    if name == "cog":
                        cognates.append(src)

            writer.add_document(
                word=entry.get("word", "").lower(),
                lang=entry.get("lang", "").lower(),
                pos=entry.get("pos", ""),
                etymology_text=entry.get("etymology_text", ""),
                etymology_langs=",".join(
                    tpl.get("lang", "").lower()
                    for tpl in entry.get("etymology_templates", [])
                    if tpl.get("lang")
                ),
                glosses="; ".join(
                    gloss
                    for sense in entry.get("senses", [])
                    for gloss in sense.get("glosses", [])
                ),
                related_words=",".join(related),
                cognates=",".join(cognates),
            )

    writer.commit()


def main():
    parser = argparse.ArgumentParser(
        description="Build a Whoosh index from a JSONL etymology dataset"
    )
    parser.add_argument(
        "jsonl_path",
        help="Path to the JSONL dataset file (e.g., kaikki.org dump)"
    )
    parser.add_argument(
        "--index-dir",
        default="indexdir",
        help="Directory where the Whoosh index will be stored"
    )
    args = parser.parse_args()

    print(f"Building index from {args.jsonl_path} into {args.index_dir}...")
    build_index(args.jsonl_path, args.index_dir)
    print("Indexing completed.")


if __name__ == "__main__":
    main()

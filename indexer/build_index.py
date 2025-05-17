from whoosh import index
from whoosh.fields import Schema, ID, TEXT, KEYWORD
import os
import json
from tqdm import tqdm

def get_schema():
    return Schema(
        word=ID(stored=True),
        lang=ID(stored=True),
        pos=ID(stored=True),
        etymology_text=TEXT(stored=True),
        etymology_langs=KEYWORD(stored=True, commas=True, lowercase=True),
        glosses=TEXT(stored=True)
    )

def create_or_open_index(index_dir="indexdir"):
    schema = get_schema()
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
        return index.create_in(index_dir, schema)
    else:
        return index.open_dir(index_dir)

def build_index(jsonl_path, index_dir="indexdir"):
    ix = create_or_open_index(index_dir)

    with open(jsonl_path, "r", encoding="utf-8") as f:
        total_lines = sum(1 for _ in f)

    with ix.writer() as writer:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in tqdm(f, total=total_lines, desc="Indexing"):
                try:
                    entry = json.loads(line)
                    if entry.get("lang") != "English":
                        continue

                    word = entry.get("word", "")
                    pos = entry.get("pos", "")
                    etymology_text = entry.get("etymology_text", "")

                    ety_langs = {tpl.get("lang", "").lower() for tpl in entry.get("etymology_templates", []) if tpl.get("lang")}

                    gloss_list = []
                    for sense in entry.get("senses", []):
                        gloss_list.extend(sense.get("glosses", []))
                    glosses = "; ".join(gloss_list)

                    writer.add_document(
                        word=word,
                        lang="English",
                        pos=pos,
                        etymology_text=etymology_text,
                        etymology_langs=",".join(ety_langs),
                        glosses=glosses
                    )
                except Exception as e:
                    print("Skipping entry due to error:", e)

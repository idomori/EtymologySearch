from whoosh import index
from whoosh.qparser import QueryParser

def search_index(query_str, index_dir="indexdir", field="etymology_text", limit=10):
    ix = index.open_dir(index_dir)
    results_data = []

    with ix.searcher() as searcher:
        query = QueryParser(field, ix.schema).parse(query_str)
        results = searcher.search(query, limit=limit)
        for r in results:
            results_data.append({
                "word": r.get("word", ""),
                "lang": r.get("lang", ""),
                "pos": r.get("pos", ""),
                "etymology_text": r.get("etymology_text", ""),
                "glosses": r.get("glosses", ""),
                "etymology_langs": r.get("etymology_langs", "")
            })

    return results_data

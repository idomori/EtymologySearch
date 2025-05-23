# def search_index(query_str, lang_code, index_dir="indexdir", fields=["related_words", "etymology_text"], limit=20):
#     ix = index.open_dir(index_dir)
#     results_data = []

#     with ix.searcher() as searcher:
#         query_info = searcher.document(word=query_str, lang_code=lang_code)
#         related = query_info.get("related_words", "").split(",") if query_info else []
#         related = [t for t in related if t != "-"]
#         related = [w.replace("(", "").replace(")", "") for w in related]
#         query_terms = set(related) | {query_str}
 
#         query_str = " OR ".join(query_terms)
#         boosts = {
#             "related_words": 2.0,
#             "etymology_text": 1.0
#         }
#         query = MultifieldParser(fields, ix.schema, fieldboosts=boosts).parse(query_str)
#         results = searcher.search(query, limit)
#         for r in results:
#             results_data.append({
#                 "word": r.get("word", ""),
#                 "lang": r.get("lang", ""),
#                 "pos": r.get("pos", ""),
#                 "etymology_text": r.get("etymology_text", ""),
#                 "glosses": (r.get("glosses", "")[:100] + "..."),
#                 "etymology_langs": r.get("etymology_langs", "")
#             })
#     print("Done searching")
#     return query_info, results_data

# def search_index(
#     query_str,
#     lang_code,
#     index_dir="indexdir",
#     fields=["related_words", "etymology_text"],
#     page=1,
#     page_size=20
# ):
#     """
#     Returns a tuple (query_info, page_data) where:
#       - query_info: the stored document for (word=query_str, lang_code)
#       - page_data: {
#           results:   [ ...hit dicts... ],
#           total:     <total matches>,
#           page:      <current page>,
#           pagecount: <total pages>,
#           page_size: <hits per page>
#         }
#     """
#     ix = index.open_dir(index_dir)

#     with ix.searcher() as searcher:
#         # Fetch original document & related terms
#         query_info = searcher.document(word=query_str, lang_code=lang_code)
#         related = query_info.get("related_words", "").split(",") if query_info else []
#         related = [t for t in related if t != "-"]
#         related = [w.replace("(", "").replace(")", "") for w in related]
#         query_terms = set(related) | {query_str}
#         raw_q = " OR ".join(query_terms)

#         # Build boosted multifield query
#         boosts = {"related_words": 2.0, "etymology_text": 1.0}
#         #parser = QueryParser("related_words", schema=ix.schema)
#         parser = MultifieldParser(fields, schema=ix.schema, fieldboosts=boosts)
#         query = parser.parse(raw_q)

#         # Validate and normalize pagination inputs
#         try:
#             p = int(page)
#             if p < 1:
#                 p = 1
#         except (TypeError, ValueError):
#             p = 1
#         try:
#             ps = int(page_size)
#             if ps < 1:
#                 ps = 20
#         except (TypeError, ValueError):
#             ps = 20

#         # Perform paged search
#         page_obj = searcher.search_page(query, pagenum=p, pagelen=ps)
#         total = page_obj.total
#         pagecount = page_obj.pagecount

#         # Collect results
#         results = []
#         for hit in page_obj:
#             results.append({
#                 "word":             hit.get("word", ""),
#                 "lang":             hit.get("lang", ""),
#                 "pos":              hit.get("pos", ""),
#                 "etymology_text":   hit.get("etymology_text", ""),
#                 "glosses":          (hit.get("glosses", "")[:100] + "..."),
#                 "etymology_langs":  hit.get("etymology_langs", "")
#             })

#     # Build pagination payload
#     page_data = {
#         "results":   results,
#         "total":     total,
#         "page":      p,
#         "pagecount": pagecount,
#         "page_size": ps
#     }
#     return query_info, page_data
# indexer/search_index.py

from whoosh import index
from whoosh.query import Or, Term

def search_index(
    query_str,
    lang_code,
    index_dir="indexdir",
    fields=("related_words", "etymology_text"),
    page=1,
    page_size=20
):
    ix = index.open_dir(index_dir)
    with ix.searcher() as searcher:
        # fetch the root doc & its expansions
        query_info = searcher.document(word=query_str, lang_code=lang_code)
        related = (query_info.get("related_words","").split(",") if query_info else [])
        related = [w for w in related if w != "-"]
        related = [w.replace("(","").replace(")","") for w in related]

        # build a small OR-tree, boosting related_words
        query_terms = set(related) | {query_str}
        subq = []
        for t in query_terms:
            subq.append(Term("cognates", t, boost=3.0))
            #subq.append(Term("word", t, boost=2.0))
            subq.append(Term("related_words", t, boost=2.0))
            subq.append(Term("etymology_text", t))
        query = Or(subq)

        # safe pagination
        try: p = max(1, int(page))
        except: p = 1
        try: ps = max(1, int(page_size))
        except: ps = 20

        # pre-filter by language
        # lang_filter = Term("lang_code", lang_code)
        page_obj = searcher.search_page(
            query, pagenum=p, pagelen=ps
        )

        # assemble results
        results = []
        for hit in page_obj:
            gloss = hit.get("glosses", "")
            if len(gloss) >= 100:
                gloss = gloss[:100] + "..."
            results.append({
                "word": hit.get("word", ""),
                "lang": hit.get("lang", ""),
                "lang_code": hit.get("lang_code", ""),
                "pos": hit.get("pos", ""),
                "etymology_text": hit.get("etymology_text", ""),
                "glosses": gloss,
                "etymology_langs": hit.get("etymology_langs", "")
            })

    return query_info, {
        "results":   results,
        "total":     page_obj.total,
        "page":      p,
        "pagecount": page_obj.pagecount,
        "page_size": ps
    }

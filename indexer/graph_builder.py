import requests
import mwparserfromhell
from collections import defaultdict
import requests, mwparserfromhell

TEMPLATE_TYPES = {"inh", "der", "bor", "cal", "cog", "clq", "rel", "root"}

def fetch_templates(word: str):
    url = "https://en.wiktionary.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": word,
        "rvslots": "*",
        "rvprop": "content",
        "formatversion": 2,
        "format": "json",
    }
    try:
        wikitext = requests.get(url, params=params).json()[
            "query"]["pages"][0]["revisions"][0]["slots"]["main"]["content"]
    except Exception:
        return []

    parsed = mwparserfromhell.parse(wikitext)
    return [t for t in parsed.filter_templates()
            if t.name.strip().lower() in TEMPLATE_TYPES]

def parse_template_id(tpl):
    """Return (lang, word) or None."""
    try:
        return (tpl.get(2).value.strip(), tpl.get(3).value.strip())
    except Exception:
        return None



def build_clean_etymology_graph(query_word: str):
    """
    Graph rule:
      • Each first-level source in the query's templates gets ONE edge to the query
      • Deeper ancestors only link to their child source (never to the query node)
      • Relation label (inh/der/bor/…) is kept
      • No duplicate edges
    """
    visited          = set()            # processed (lang, word)
    nodes            = {}               # node_id → node dict
    edge_set         = set()            # {(from, to, label)}
    query_id         = f"en:{query_word}"

    # ── 1. collect first-level sources and their relations ───────────────────
    first_level: dict[tuple, str] = {}
    for tpl in fetch_templates(query_word):
        ident = parse_template_id(tpl)
        if ident:
            first_level[ident] = tpl.name.strip()

    # ── helpers ──────────────────────────────────────────────────────────────
    def add_node(lang, word):
        nid = f"{lang}:{word}"
        if nid not in nodes:
            nodes[nid] = {"id": nid, "label": nid}
        return nid

    def add_edge(src, dst, label):
        edge_set.add((src, dst, label))        # set forbids duplicates

    # ── 2. add the query node + edges from each first-level source ───────────
    add_node("en", query_word)
    for (lang, word), rel in first_level.items():
        src_id = add_node(lang, word)
        add_edge(src_id, query_id, rel)        # direct, single edge

    # ── 3. link sources to each other (one hop deep) ────────────────────────
    def traverse(lang, word):
        key = (lang, word)
        if key in visited:                     # avoid loops
            return
        visited.add(key)

        src_id = add_node(lang, word)
        for tpl in fetch_templates(word):
            child = parse_template_id(tpl)
            if not child or child not in first_level:
                continue                       # skip outside original set
            child_id = add_node(*child)
            add_edge(child_id, src_id, tpl.name.strip())
            traverse(*child)

    for lang, word in first_level.keys():
        traverse(lang, word)

    # ── 4. convert edge_set → list[dict] for vis-network  ────────────────────
    edges = [{"from": f, "to": t, "label": lbl} for f, t, lbl in edge_set]
    return {"nodes": list(nodes.values()), "edges": edges}




# def prune_direct_edges_to_query(query_id, edges):
#     """Remove edges pointing to query_id if an indirect path exists via other source words."""
#     graph = defaultdict(list)
#     for edge in edges:
#         graph[edge["from"]].append(edge["to"])

#     all_paths = []

#     def dfs(node, path):
#         if node == query_id:
#             all_paths.append(path)
#             return
#         for neighbor in graph.get(node, []):
#             if neighbor not in path:
#                 dfs(neighbor, path + [neighbor])

#     start_nodes = {e["from"] for e in edges}
#     for s in start_nodes:
#         dfs(s, [s])

#     longest_paths = {}
#     for path in all_paths:
#         src = path[0]
#         if src not in longest_paths or len(path) > len(longest_paths[src]):
#             longest_paths[src] = path

#     to_remove = {
#         (e["from"], e["to"])
#         for e in edges
#         if e["to"] == query_id and e["from"] in longest_paths and len(longest_paths[e["from"]]) > 2
#     }

#     return [e for e in edges if (e["from"], e["to"]) not in to_remove]



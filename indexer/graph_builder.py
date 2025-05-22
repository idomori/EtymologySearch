import requests
import mwparserfromhell
from collections import defaultdict
import requests, mwparserfromhell
from collections import defaultdict

TEMPLATE_TYPES = {"inh", "der", "bor", "cal", "cog", "clq", "rel", "root", "dbt", "clipping", "compound", "m", "short for", "back-form", "semantic loan", "blend", "lbor", "obor"}

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
    """
    Return a (lang, word) tuple for etymology templates, or None if this template
    isn’t one we recognize.

    Handles:
      - inh (inherited) & bor (borrowed):
          {{inh|<target>|<source lang>|<source word>|…}}
          → ( source lang, source word )
      - der (derived) & cog (cognate):
          {{der|<source lang>|<source word>|…}}
          {{cog|<source lang>|<source word>|…}}
          → ( source lang, source word )
    """
    name = str(tpl.name).strip().lower()
    try:
        if name in ("inh", "bor"):
            # params: 1=target lang, 2=source lang, 3=source word
            lang = tpl.get(2).value.strip()
            word = tpl.get(3).value.strip()
            return lang, word

        if name in ("der", "cog"):
            # params: 1=source lang, 2=source word
            lang = tpl.get(1).value.strip()
            word = tpl.get(2).value.strip()
            return lang, word

    except (IndexError, AttributeError):
        # missing params or not a template with .get()
        return None

    # other templates we’re not graphing
    return None


def build_clean_etymology_graph(query_word: str):
    """
    Build a two-level etymology graph.

    • Removes self-loops
    • Collapses duplicate edges (same from/to; merges labels)
    """
    visited   = set()
    nodes     = {}                  # node_id → node dict
    edge_set  = set()               # {(from, to, label)}
    query_id  = f"en:{query_word}"
    # 1. ─ first-level templates ─────────────────────────────────────────────
    first_level: dict[tuple, str] = {}
    for tpl in fetch_templates(query_word):
        #print("tpl", tpl)
        ident = parse_template_id(tpl)
        #print("ident", ident)
        if ident:
            first_level[ident] = tpl.name.strip()

    # 2. ─ helpers ───────────────────────────────────────────────────────────
    def add_node(lang, word):
        nid = f"{lang}:{word}"
        if nid not in nodes:
            nodes[nid] = {"id": nid, "label": nid}
        return nid

    def add_edge(src, dst, label):
        if src == dst:              # ← self-loop guard
            return
        edge_set.add((src, dst, label))  # set dedups identical triples

    # 3. ─ add query node + direct sources ───────────────────────────────────
    add_node("en", query_word)
    for (lang, word), rel in first_level.items():
        src_id = add_node(lang, word)
        add_edge(src_id, query_id, rel)

    # 4. ─ link sources one hop deeper ───────────────────────────────────────
    def traverse(lang, word):
        key = (lang, word)
        if key in visited:
            return
        visited.add(key)

        src_id = add_node(lang, word)
        for tpl in fetch_templates(word):
            child = parse_template_id(tpl)
            if not child or child not in first_level:
                continue
            child_id = add_node(*child)
            add_edge(child_id, src_id, tpl.name.strip())
            traverse(*child)
    #print("first_level", first_level)
    for lang, word in first_level:
        traverse(lang, word)

    # 5. ─ collapse duplicates & join labels ─────────────────────────────────
    bucket: dict[tuple, set] = defaultdict(set)   # (from, to) → {labels}
    for f, t, lbl in edge_set:
        if f == t:                                # second self-loop guard
            continue
        bucket[(f, t)].add(lbl)

    edges = [
        {"from": f, "to": t, "label": ", ".join(sorted(lbls))}
        for (f, t), lbls in bucket.items()
    ]
    
    return {"nodes": list(nodes.values()), "edges": edges}


def _assign_levels(query_id, nodes, edges):
    """Longest-path (DAG) rank → even layers."""
    from collections import defaultdict

    parents = defaultdict(list)
    for e in edges:
        parents[e["to"]].append(e["from"])

    levels = {query_id: 0}

    # DAG: we can topologically relax longest distance to query
    changed = True
    while changed:
        changed = False
        for node in nodes:
            nid = node["id"]
            if nid == query_id or nid not in parents:
                continue
            parent_levels = [levels[p] for p in parents[nid] if p in levels]
            if parent_levels:
                new_level = max(parent_levels) + 1
                if levels.get(nid, -1) != new_level:
                    levels[nid] = new_level
                    changed = True

    for n in nodes:
        n["level"] = levels.get(n["id"], 1)


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



import json

def build_etymology_graph_from_templates(template_list):
    nodes = {}
    edges = []

    def add_node(label):
        if label not in nodes:
            nodes[label] = {"id": label, "label": label}

    for template in template_list:
        name = template.get("name")
        args = template.get("args", {})

        if name == "root":
            label = args.get("3")
            if label:
                add_node(label)
                nodes["root"] = {"id": "root", "label": label}

        elif name in {"inh", "der", "bor", "cal", "clq", "cog"}:
            from_lang = args.get("2")
            to_lang = args.get("1")
            word = args.get("3")
            if from_lang and word:
                src = word
                dst = "dictionary"  # fallback if we don’t have the target
                if name == "inh" and to_lang == "en":
                    dst = "dictionary"
                add_node(src)
                add_node(dst)
                edges.append({"from": src, "to": dst, "label": name})

        elif name == "surf":
            parts = [args.get("2", ""), args.get("3", "")]
            src = "+".join(parts)
            dst = "dictionary"
            add_node(src)
            add_node(dst)
            edges.append({"from": src, "to": dst, "label": "surf"})

    return {
        "nodes": list(nodes.values()),
        "edges": edges
    }

def load_graph_from_file(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        templates = json.load(f)
    return build_etymology_graph_from_templates(templates)

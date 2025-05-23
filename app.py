from flask import Flask, render_template, request, jsonify
from indexer.search_index import search_index
from indexer.graph_builder import build_clean_etymology_graph
from indexer.llm_parser import extract_etymology_graph

app = Flask(__name__)

SUPPORTED_LANGUAGES = [
    ('en', 'English'),
    #('fr', 'French'),
    ('de', 'German')
    #('es', 'Spanish'),
    # …add whatever your index contains
]

@app.context_processor
def inject_supported_languages():
    # makes `supported_languages` available in every template
    return dict(supported_languages=SUPPORTED_LANGUAGES)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/search')
def search():
    query     = request.args.get('q', '')
    lang      = request.args.get('lang', 'en')
    # always start on page 1 for the full‐page render
    page      = 1
    page_size = 20

    query_info, page_data = search_index(
        query_str=query,
        lang_code=lang,
        page=page,
        page_size=page_size
    )
    print(query_info["related_words"])
    graph_data = extract_etymology_graph(query_info) if query_info else {"nodes": [], "edges": []}

    return render_template(
        'search_results.html',
        query=query,
        lang=lang,
        graph_data=graph_data,
        **page_data
    )

@app.route('/search/results')
def search_results():
    """
    Infinite‐scroll AJAX endpoint: returns JSON with
      { results, total, page, pagecount, page_size }
    """
    query     = request.args.get('q', '')
    lang      = request.args.get('lang', 'en')
    try:
        page = max(1, int(request.args.get('page', 1)))
    except ValueError:
        page = 1
    try:
        page_size = max(1, int(request.args.get('page_size', 20)))
    except ValueError:
        page_size = 20

    _, page_data = search_index(
        query_str=query,
        lang_code=lang,
        page=page,
        page_size=page_size
    )
    return jsonify(page_data)


if __name__ == '__main__':
    app.run(debug=True)

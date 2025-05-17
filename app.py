from flask import Flask, render_template, request
from indexer.search_index import search_index
from indexer.search_index import search_index
from indexer.graph_builder import load_graph_from_file

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = search_index(query)

    try:
        graph_data = load_graph_from_file(f"graph_examples/dictionary.json")
    except Exception:
        graph_data = {"nodes": [{"id": query, "label": query}], "edges": []}

    return render_template(
        'search_results.html',
        query=query,
        graph_data=graph_data,
        results=results
    )


if __name__ == '__main__':
    app.run(debug=True)

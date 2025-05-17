from flask import Flask, render_template, request
from indexer.search_index import search_index

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = search_index(query)

    graph_data = {
        "nodes": [{"id": "word", "label": query}],
        "edges": []
    }
    if results:
        graph_data["nodes"].append({"id": "root", "label": "Proto-Indo-European"})
        graph_data["edges"].append({"from": "root", "to": "word"})

    return render_template('search_results.html', query=query, graph_data=graph_data, results=results)

if __name__ == '__main__':
    app.run(debug=True)

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

    # Hardcoded annotated graph
    graph_data = {
        "nodes": [
            {"id": "root", "label": "*deyḱ-"},
            {"id": "dixionare", "label": "Middle English dixionare"},
            {"id": "dictionary", "label": "English dictionary"},
            {"id": "dictiōnārium", "label": "Medieval Latin dictiōnārium"},
            {"id": "dictiōnārius", "label": "Latin dictiōnārius"},
            {"id": "diction+-ary", "label": "diction + -ary"},
        ],
        "edges": [
            {"from": "root", "to": "dixionare", "label": "inh"},
            {"from": "dixionare", "to": "dictionary", "label": "inh"},
            {"from": "dictiōnārium", "to": "dictionary", "label": "der"},
            {"from": "dictiōnārius", "to": "dictiōnārium", "label": "der"},
            {"from": "diction+-ary", "to": "dictionary", "label": "surf"},
        ]
    }

    return render_template(
        'search_results.html',
        query=query,
        graph_data=graph_data,
        results=results
    )


if __name__ == '__main__':
    app.run(debug=True)

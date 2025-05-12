from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    # Dummy data for graph and results
    graph_data = {
        "nodes": [{"id": "word", "label": query}, {"id": "root", "label": "Proto-Indo-European"}],
        "edges": [{"from": "root", "to": "word"}]
    }
    search_results = [
        {"word": query, "definition": "The origin of the word from XYZ root."},
        {"word": query + "ish", "definition": "Derived from " + query}
    ]
    return render_template('search_results.html', query=query, graph_data=graph_data, results=search_results)

if __name__ == '__main__':
    app.run(debug=True)

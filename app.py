from flask import Flask, render_template, request
from indexer.search_index import search_index
from indexer.graph_builder import build_clean_etymology_graph
from indexer.llm_parser import extract_etymology_graph

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/search')
def search():
    query = request.args.get('q', '')

    #etym_text = get_etym_text(query)
    query_info, results = search_index(query)
    print(extract_etymology_graph(query_info))
    
    

    # build the live graph
    graph_data = build_clean_etymology_graph(query)
    #print(graph_data)
    return render_template(
        'search_results.html',
        query=query,
        graph_data=graph_data,
        results=results
    )


if __name__ == '__main__':
    app.run(debug=True)

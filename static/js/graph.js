document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById('graph-container');
    const data = {
        nodes: new vis.DataSet(graphData.nodes),
        edges: new vis.DataSet(graphData.edges),
    };
    const options = {
        nodes: { shape: 'dot', size: 20 },
        edges: {
            arrows: 'to',
            font: { align: 'middle' },
            labelHighlightBold: true,
            color: { inherit: 'from' }
        },
        physics: { stabilization: false }
    };
    new vis.Network(container, data, options);
});

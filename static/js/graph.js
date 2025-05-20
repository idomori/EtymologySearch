// document.addEventListener("DOMContentLoaded", function () {
//     const container = document.getElementById('graph-container');
//     const data = {
//         nodes: new vis.DataSet(graphData.nodes),
//         edges: new vis.DataSet(graphData.edges),
//     };
//     const options = {
//         nodes: { shape: 'dot', size: 20 },
//         edges: {
//             arrows: 'to',
//             font: { align: 'middle' },
//             labelHighlightBold: true,
//             color: { inherit: 'from' }
//         },
//         physics: { stabilization: false }
//     };
//     new vis.Network(container, data, options);
// });

document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById('graph-container');

    const data = {
        nodes: new vis.DataSet(graphData.nodes),
        edges: new vis.DataSet(graphData.edges),
    };

    const options = {
        layout: {
            hierarchical: {
                enabled: true,
                direction: 'UD',        // top-down tree
                sortMethod: 'directed',
                nodeSpacing: 150,
                levelSeparation: 100
            }
        },
        nodes: {
            shape: 'dot',
            size: 20,
            font: { size: 16 }
        },
        edges: {
            arrows: 'to',
            font: { align: 'middle' },
            labelHighlightBold: true,
            color: { inherit: 'from' },
            smooth: {
                type: 'cubicBezier',
                forceDirection: 'vertical',
                roundness: 0.4
            }
        },
        physics: false
    };

    new vis.Network(container, data, options);
});


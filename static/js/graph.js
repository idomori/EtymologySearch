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

// document.addEventListener("DOMContentLoaded", function () {
//     const container = document.getElementById('graph-container');

//     const data = {
//         nodes: new vis.DataSet(graphData.nodes),
//         edges: new vis.DataSet(graphData.edges),
//     };

//     // const options = {
//     //     layout: {
//     //         hierarchical: {
//     //             enabled: true,
//     //             direction: 'UD',        // top-down tree
//     //             sortMethod: 'directed',
//     //             nodeSpacing: 150,
//     //             levelSeparation: 100
//     //         }
//     //     },
//     //     nodes: {
//     //         shape: 'dot',
//     //         size: 20,
//     //         font: { size: 16 }
//     //     },
//     //     edges: {
//     //         arrows: 'to',
//     //         font: { align: 'middle' },
//     //         labelHighlightBold: true,
//     //         color: { inherit: 'from' },
//     //         smooth: {
//     //             type: 'cubicBezier',
//     //             forceDirection: 'vertical',
//     //             roundness: 0.4
//     //         }
//     //     },
//     //     physics: false
//     // };
//     const options = {
//         layout: {
//             hierarchical: {
//             enabled: true,
//             direction: 'DU',          // root (query) at the bottom
//             sortMethod: 'directed',
//             nodeSpacing: 100,
//             levelSeparation: 100,
//             blockShifting: true,
//             edgeMinimization: true,   // <<< minimises crossings
//             parentCentralization: true
//             }
//         },
//         nodes: {
//             shape: 'dot',
//             size: 22,
//             font: { size: 16 }
//         },
//         edges: {
//             arrows: 'to',
//             labelHighlightBold: true,
//             smooth: {
//                 enabled: true,
//                 type: 'horizontal',   // run horizontal → bend → vertical
//                 roundness: 0          // crisp right-angle corner
//             }
//         },
//         physics: false
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
        enabled: true,           // turn on the tree layout
        direction: 'UD',         // root at the top, leaves at the bottom
        sortMethod: 'directed',  // respect the direction of your edges
        nodeSpacing: 200,        // horizontal spacing between siblings
        levelSeparation: 150,    // vertical spacing between generations
        edgeMinimization: true,  // try to re‐route to avoid crossings
        blockShifting: true,     // don't drag entire subtrees sideways
        parentCentralization: true
      }
    },
    nodes: {
      shape: 'dot',
      size: 20,
      font: { size: 14 }
    },
    edges: {
      arrows: {
        to: { enabled: true, scaleFactor: 0.6 }
      },
      smooth: {
        enabled: true,
        // run horizontal first, then vertical
        type: 'horizontal',
        // no curve—crisp 90° corners
        roundness: 0
      }
    },
    physics: false             // disable the MDS force‐directed so it’s pure hierarchy
  };

  new vis.Network(container, data, options);
});

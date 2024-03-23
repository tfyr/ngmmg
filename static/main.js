import "https://cdn.jsdelivr.net/npm/d3@7";

function ForceGraph(
    {
        nodes, // an iterable of node objects (typically [{id}, …])
        links // an iterable of link objects (typically [{source, target}, …])
    }, 
    {
        nodeId = d => d.id, // given d in nodes, returns a unique identifier (string)
        nodeGroup, // given d in nodes, returns an (ordinal) value for color
        nodeGroups, // an array of ordinal values representing the node groups
        nodeTitle, // given d in nodes, a title string
        nodeFill = "currentColor", // node stroke fill (if not using a group color encoding)
        nodeStroke = "#fff", // node stroke color
        nodeStrokeWidth = 0, // node stroke width, in pixels
        nodeStrokeOpacity = 1, // node stroke opacity
        nodeStrength=-240,
        linkSource = ({source}) => source, // given d in links, returns a node identifier string
        linkTarget = ({target}) => target, // given d in links, returns a node identifier string
        linkValue = ({value}) => value, // given d in links, returns a node identifier string
        linkStroke = "#999", // link stroke color
        linkStrokeOpacity = 0.6, // link stroke opacity
        linkStrokeLinecap = "round", // link stroke linecap
        linkStrength,
        colors = d3.schemeTableau10, // an array of color strings, for the node groups
        width = window.innerWidth, // outer width, in pixels
        height = window.innerHeight, // outer height, in pixels
        invalidation // when this promise resolves, stop the simulation
    } = {}) {
    // Compute values.
    const N = d3.map(nodes, nodeId).map(intern);
    const LS = d3.map(links, linkSource).map(intern);
    const LT = d3.map(links, linkTarget).map(intern);
    const LV = d3.map(links, linkValue).map(intern);
    if (nodeTitle === undefined) 
        nodeTitle = (_, i) => N[i];
    const T = nodeTitle == null ? null : d3.map(nodes, nodeTitle);

    const Balances = d3.map(nodes, (x,i)=>nodes[i].balance);

    // Replace the input nodes and links with mutable objects for the simulation.
    nodes = d3.map(nodes, (_, i) => ({id: N[i]}));
    links = d3.map(links, (_, i) => ({source: LS[i], target: LT[i]}));

    // Construct the scales.
    const color = nodeGroup == null ? null : d3.scaleOrdinal(nodeGroups, colors);

    // Construct the forces.
    const forceNode = d3.forceManyBody();
    const forceLink = d3.forceLink(links).id(({index: i}) => N[i]);
    if (nodeStrength !== undefined) forceNode.strength(nodeStrength);
    if (linkStrength !== undefined) forceLink.strength(linkStrength);

    const simulation = d3.forceSimulation(nodes)
        .force("link", forceLink)
        .force("charge", forceNode)
        .force("center",  d3.forceCenter())
        .on("tick", ticked);

    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [-width / 2, -height / 2, width, height])
        .attr("style", "max-width: 100%; height: auto; height: intrinsic;");

    const defs = svg.append('defs');
    const marker = defs.append("marker")
        .attr("id","head")
        .attr("orient","auto")
        .attr("markerWidth","12")
        .attr("markerHeight","6")
        .attr("refX","12")
        .attr("refY","3");
        //.style("opacity", 0.5);
    marker.append("path")
        .attr("d", 'M0,0 V6 L12,3 Z')
        .attr("fill", '#999')

    const link = svg.append("g")
        .attr("stroke", linkStroke)
        .attr("stroke-opacity", linkStrokeOpacity)
        .attr("stroke-linecap", linkStrokeLinecap)
        .attr("marker-end", 'url(#head)')
        .selectAll("line")
        .data(links)
        .join("line");

    const node = svg.append("g")
        .attr("fill", nodeFill)
        .attr("stroke", nodeStroke)
        .attr("stroke-opacity", nodeStrokeOpacity)
        .attr("stroke-width", nodeStrokeWidth)
        .selectAll("circle")
        .data(nodes)
        .join("g")
        .call(drag(simulation));

    node.append("circle")
        .attr("fill", "#900")
        .attr("r", ({index: i})=> (Math.round(Balances[i]/4)/100))

    if (T) node.append("text").attr("dx", -30).attr("dy", -10).text(({index: i}) => T[i]);

    link.attr("stroke-width", ({index: i}) => 0.9+LV[i]/8);

    if (invalidation != null)
        invalidation.then(() => simulation.stop());

    function intern(value) {
        return value !== null && typeof value === "object" ? value.valueOf() : value;
    }

    function ticked() {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
        node
            .attr("style", d => "transform: translate(" + d.x + "px, " + d.y + "px)");
    }

    function drag(simulation) {    
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }

        return d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);
    }
    return Object.assign(svg.node(), {scales: {color}});
}

let fileName='data.json'
d3.json(fileName).then((data)=>{
    const nodes = data.nodes.map(d => Object.create(d));
    const links = data.links.map(d => Object.create(d));
    let graph = document.getElementById('graph')
    let fg = ForceGraph({nodes, links},{nodeTitle: d => `${d.username?d.username:''}`})
    graph.appendChild(fg)
});

//export {ForceGraph};
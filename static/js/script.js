_.pushAll = (array, values) => {
    array.push.apply(array, values);
}

function draw_instances(json) {
    let data = { "name": "master", "children": _.map(json['workers'], x => { return { "name": x } }) };
    let tree = d3.tree().size([600, 400])(d3.hierarchy(data));

    let margin = { top: 40, right: 90, bottom: 50, left: 90 };
    let svg = d3.select("#info-nodes svg");

    let g = svg.select("g");
    if(g.empty()) {
        g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);
    }

    let links = g.selectAll(".link").data(tree.descendants().slice(1));
    links.enter().append("path")
        .merge(links)
        .attr("class", "link")
        .attr("d", d => "M" + d.x + "," + d.y + "C" + d.x + "," + (d.y + d.parent.y) / 2 + " " + d.parent.x + "," +  (d.y + d.parent.y) / 2 + " " + d.parent.x + "," + d.parent.y);

    links.exit().remove();

    let nodes = g.selectAll(".node").data(tree.descendants());
    let nodes_g = nodes.enter().append("g").classed("node", true)

    nodes_g.append("text")
        .attr("dy", ".35em").attr("y", d => d.children ? -20 : 20)
        .style("text-anchor", "middle")
        .text((d, i) => d.data.name === "master" ? "master" : `worker${i}`);

    nodes_g.merge(nodes).attr("transform", d => `translate(${d.x},${d.y})`);

    nodes.exit().remove();
}

var prev_edges = [], prev_vertices = {}, hostnames = new Set(), i = 0, force;
function draw_graph_faster(json) {
    let vertices = {},
        edges = [],
        new_edges = _.differenceBy(json['edges'], prev_edges, x => `${x[0]}-${x[1]}`),
        first_time = force === undefined;

    if(new_edges.length === 0) { return; }

    if(!first_time && force.links().length > 500) {
        let svg = d3.select("#info-graph svg");
        let info = svg.select(".info-text");
        if(info.empty()) {
            svg.append("text").classed("info-text", true).text("edge limit exceeded")
                .attr("y", 10)
                .attr("x", $("#info-graph svg").width() - 10)
                .attr("text-anchor", "end")
                .attr("dominant-baseline", "hanging")
                .attr("fill", "grey")
        }

        console.log("too many edges!");
        return;
    }

    prev_edges = json['edges'];

    _.each(new_edges, tup => {
        let src = tup[0], dst = tup[1];
        if(prev_vertices[src] === undefined) { prev_vertices[src] = i++; }
        if(prev_vertices[dst] === undefined) { prev_vertices[dst] = i++; }

        vertices[src] = prev_vertices[src];
        vertices[dst] = prev_vertices[dst];

        console.log("adding edge", src, "->", dst, "as", vertices[src], "->", vertices[dst]);
        edges.push({ 'source': vertices[src], 'target': vertices[dst] });
    });

    vertices = _.map(_.sortBy(Object.keys(vertices), x => vertices[x]), url => {
        let hostname = new URL(url).hostname;
        hostnames.add(hostname);
        return { 'name': url, 'hostname': hostname, };
    });

    let colors = d3.scaleOrdinal(d3.schemeCategory10).domain(Array.from(hostnames)),
        svg = d3.select("#info-graph svg");

    if(first_time) {
        console.log("initializing");
        force = cola.d3adaptor(d3).size([600, 400]).jaccardLinkLengths(40,0.7).handleDisconnected(false);
        force.nodes(vertices).links(edges).start(30);
    } else {
        console.log("updating");

        _.pushAll(force.nodes(), _.differenceBy(vertices, force.nodes(), 'name'));
        _.pushAll(force.links(), edges);

        force.start(30);
    }

    let links = svg.selectAll(".link").data(force.links());
    links.enter().insert("line", ".node")
        .classed("link", true)
        .merge(links)
        .style("stroke-width", 2);

    let nodes = svg.selectAll(".node").data(force.nodes(), d => d.name);
    nodes.enter().append("circle")
        .classed("node", true)
        .merge(nodes)
        .attr("r", 8)
        .style("fill", d => colors(d.hostname))
        .call(force.drag)
        .on("mouseenter", d => {
            d3.select("body").append("div")
                .attr("id", "tooltip")
                .classed("tooltip", true)
                .style("top", d3.event.pageY + "px").style("left", d3.event.pageX + 10 + "px")
                .html(`<b>${d.name}</b>`)
        })
        .on("mouseleave", () => d3.select("#tooltip").remove())
        .on("click", d => {
            let win = window.open(d.name, '_blank');
            win.focus();
        });

    force.on("tick", () => {
        svg.selectAll(".link")
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        svg.selectAll(".node")
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
    });
}

function update_progress(url, first_time=false) {
    fetch(url).then(response => response.json()).then(json => {
        draw_instances(json);
        draw_graph_faster(json, first_time);

        $("#no-edges").html(json['edges'].length);
        $("#cur-depth").html(_.maxBy(json['edges'], 2)[2]);
    });
}

function show_content(thing) {
    $(".tab").removeClass("active");
    $(`#tab-${thing}`).addClass("active");

    $(".info").removeClass("active");
    $(`#info-${thing}`).addClass("active");
}
let updating_interval;
$("#start").on("click", e => {
    e.preventDefault();

    let formData = new FormData(document.querySelector("form"));
    fetch("/crawl", {
        method: 'post',
        body: formData
    }).then(response => {
        if(response.ok) {
            $("#start").attr("disabled", true);
            $(".stop").show()

            setTimeout(update_progress, 1000, '/progress', true);
            updating_interval = setInterval(update_progress, 10000, '/progress');
        } else {
            alert("error: did not start crawl");
        }
    })
});

$("#stop").on("click", e => {
    e.preventDefault();

    fetch("/crawl", {
        method: 'delete'
    }).then(response => {
        if(response.ok) {
            $(".stop").hide();
            alert("Please note that stopping is only possible every 60 seconds.");

            clearInterval(updating_interval);
            $("#start").attr("disabled", false);
        } else {
            alert("cancelling crawl did not succeed");
        }
    })
})

function update_progress(url) {
    fetch(url).then(response => response.json()).then(json => {
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
            .text(d => d.data.name);

        nodes_g.merge(nodes).attr("transform", d => `translate(${d.x},${d.y})`);

        nodes.exit().remove();
    });
}

function show_nodes() {
    $("#tab-nodes").addClass("active");
    $("#tab-graph").removeClass("active");

    $("#info-nodes").addClass("active");
    $("#info-graph").removeClass("active");
}

function show_graph() {
    $("#tab-graph").addClass("active");
    $("#tab-nodes").removeClass("active");

    $("#info-graph").addClass("active");
    $("#info-nodes").removeClass("active");
}

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

            setInterval(update_progress, 1000, '/progress');
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
            $("#start").attr("disabled", false);
        } else {
            alert("cancelling crawl did not succeed");
        }
    })
})

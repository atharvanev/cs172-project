"""
Reads output.json and generates visualization.html — a self-contained D3.js
force-directed network graph of the crawled Wikipedia pages.
"""

import json
import sys
from pathlib import Path

OUTPUT_JSON = Path(__file__).parent / "output.json"
VIZ_HTML = Path(__file__).parent / "visualization.html"
MAX_EDGES_PER_NODE = 20


def build_graph(pages):
    url_set = {p["url"] for p in pages}

    nodes = []
    for p in pages:
        nodes.append({
            "id": p["url"],
            "title": p["title"].replace(" - Wikipedia", "").strip(),
            "depth": p.get("depth", 0),
        })

    links = []
    for p in pages:
        src = p["url"]
        count = 0
        for tgt in p.get("outgoing_links", []):
            if tgt in url_set and tgt != src:
                links.append({"source": src, "target": tgt})
                count += 1
                if count >= MAX_EDGES_PER_NODE:
                    break

    return {"nodes": nodes, "links": links}


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Wikipedia Crawl Graph</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0f1117; color: #e0e0e0; font-family: system-ui, sans-serif; overflow: hidden; }
  #canvas { width: 100vw; height: 100vh; }
  .node { cursor: pointer; }
  .link { stroke: #ffffff18; stroke-width: 1; }
  #tooltip {
    position: fixed; pointer-events: none;
    background: #1e2130cc; border: 1px solid #3a3f5c;
    border-radius: 6px; padding: 8px 12px; font-size: 13px;
    max-width: 280px; word-break: break-word;
    backdrop-filter: blur(4px); display: none;
  }
  #legend {
    position: fixed; top: 16px; right: 16px;
    background: #1e2130cc; border: 1px solid #3a3f5c;
    border-radius: 8px; padding: 12px 16px; font-size: 13px;
    backdrop-filter: blur(4px);
  }
  #legend h3 { font-size: 12px; text-transform: uppercase; letter-spacing: .06em; color: #888; margin-bottom: 8px; }
  .legend-row { display: flex; align-items: center; gap: 8px; margin: 4px 0; }
  .legend-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
  #info {
    position: fixed; bottom: 16px; left: 16px;
    font-size: 12px; color: #555;
  }
</style>
</head>
<body>
<svg id="canvas"></svg>
<div id="tooltip"></div>
<div id="legend">
  <h3>Depth</h3>
  <div id="legend-items"></div>
</div>
<div id="info">Scroll to zoom &nbsp;·&nbsp; Drag to pan &nbsp;·&nbsp; Click node to open page</div>

<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<script>
const GRAPH = __GRAPH_DATA__;

const DEPTH_COLORS = [
  "#ff6b6b", // 0 — seed
  "#ffa94d", // 1
  "#ffe066", // 2
  "#69db7c", // 3
  "#4dabf7", // 4
  "#cc5de8", // 5
];

// Build legend
const legendEl = document.getElementById("legend-items");
DEPTH_COLORS.forEach((c, d) => {
  legendEl.innerHTML += `<div class="legend-row">
    <div class="legend-dot" style="background:${c}"></div>
    <span>Depth ${d}${d === 0 ? " (seed)" : ""}</span>
  </div>`;
});

const svg = d3.select("#canvas");
const width = window.innerWidth;
const height = window.innerHeight;
svg.attr("viewBox", `0 0 ${width} ${height}`);

const g = svg.append("g");

// Compute in-degree for node sizing
const inDegree = {};
GRAPH.nodes.forEach(n => inDegree[n.id] = 0);
GRAPH.links.forEach(l => {
  const tgt = typeof l.target === "object" ? l.target.id : l.target;
  if (inDegree[tgt] !== undefined) inDegree[tgt]++;
});

const maxDeg = Math.max(1, d3.max(Object.values(inDegree)));
const rScale = d3.scaleSqrt().domain([0, maxDeg]).range([4, 14]);

// Build index maps for D3 (nodes must use array indices as source/target)
const nodeById = new Map(GRAPH.nodes.map((n, i) => [n.id, i]));
const links = GRAPH.links
  .map(l => ({ source: nodeById.get(l.source), target: nodeById.get(l.target) }))
  .filter(l => l.source !== undefined && l.target !== undefined);

const simulation = d3.forceSimulation(GRAPH.nodes)
  .force("link", d3.forceLink(links).id((_, i) => i).distance(60).strength(0.4))
  .force("charge", d3.forceManyBody().strength(-120))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collision", d3.forceCollide().radius(d => rScale(inDegree[d.id]) + 2));

const linkEl = g.append("g")
  .selectAll("line")
  .data(links)
  .join("line")
  .attr("class", "link");

const nodeEl = g.append("g")
  .selectAll("circle")
  .data(GRAPH.nodes)
  .join("circle")
  .attr("class", "node")
  .attr("r", d => rScale(inDegree[d.id]))
  .attr("fill", d => DEPTH_COLORS[Math.min(d.depth, DEPTH_COLORS.length - 1)])
  .attr("stroke", "#ffffff22")
  .attr("stroke-width", 1)
  .call(d3.drag()
    .on("start", (event, d) => {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x; d.fy = d.y;
    })
    .on("drag", (event, d) => { d.fx = event.x; d.fy = event.y; })
    .on("end", (event, d) => {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null; d.fy = null;
    })
  );

const tooltip = document.getElementById("tooltip");
nodeEl
  .on("mouseover", (event, d) => {
    tooltip.style.display = "block";
    tooltip.innerHTML = `<strong>${d.title}</strong><br><span style="color:#888;font-size:11px">${d.id}</span><br><span style="color:#aaa">depth ${d.depth} · ${inDegree[d.id]} incoming links</span>`;
  })
  .on("mousemove", event => {
    tooltip.style.left = (event.clientX + 14) + "px";
    tooltip.style.top = (event.clientY - 10) + "px";
  })
  .on("mouseout", () => { tooltip.style.display = "none"; })
  .on("click", (_, d) => { window.open(d.id, "_blank"); });

simulation.on("tick", () => {
  linkEl
    .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  nodeEl
    .attr("cx", d => d.x)
    .attr("cy", d => d.y);
});

svg.call(d3.zoom()
  .scaleExtent([0.05, 8])
  .on("zoom", event => g.attr("transform", event.transform))
);

window.addEventListener("resize", () => {
  svg.attr("viewBox", `0 0 ${window.innerWidth} ${window.innerHeight}`);
  simulation.force("center", d3.forceCenter(window.innerWidth / 2, window.innerHeight / 2));
  simulation.alpha(0.1).restart();
});
</script>
</body>
</html>
"""


def main():
    print(f"Loading {OUTPUT_JSON} …", flush=True)
    with open(OUTPUT_JSON, encoding="utf-8") as f:
        pages = json.load(f)
    print(f"  {len(pages)} pages loaded", flush=True)

    print("Building graph …", flush=True)
    graph = build_graph(pages)
    print(f"  {len(graph['nodes'])} nodes, {len(graph['links'])} edges", flush=True)

    print("Writing HTML …", flush=True)
    graph_json = json.dumps(graph, separators=(",", ":"))
    html = HTML_TEMPLATE.replace("__GRAPH_DATA__", graph_json)
    VIZ_HTML.write_text(html, encoding="utf-8")
    print(f"  Done → {VIZ_HTML}", flush=True)


if __name__ == "__main__":
    main()

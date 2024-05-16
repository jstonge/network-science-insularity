---
toc: false
sql: 
  stat_mech: ./data/stat_mech_networks_clean.parquet
  dyn_sync: ./data/dyn_sync_networks_clean.parquet
---

<style>

.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: var(--sans-serif);
  margin: 4rem 0 8rem;
  text-wrap: balance;
  text-align: center;
}

.hero h1 {
  margin: 2rem 0;
  max-width: none;
  font-size: 14vw;
  font-weight: 900;
  line-height: 1;
  background: linear-gradient(30deg, var(--theme-foreground-focus), currentColor);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero h2 {
  margin: 0;
  max-width: 34em;
  font-size: 20px;
  font-style: initial;
  font-weight: 500;
  line-height: 1.5;
  color: var(--theme-foreground-muted);
}

@media (min-width: 640px) {
  .hero h1 {
    font-size: 90px;
  }
}

</style>

# Exploring complex networks related topics in OpenAlex

```js
import * as d3 from "npm:d3";
```

```js
const sel_yr = view(Inputs.range([1990, 2020], {step:1}))
```

```sql id=[...links]
SELECT COUNT(*) as value, source, target 
FROM stat_mech 
WHERE publication_year = ${sel_yr} AND source != target 
GROUP BY source, target
```

```sql id=[...nodes]
SELECT DISTINCT source AS id, source_field as group
FROM stat_mech
WHERE publication_year = ${sel_yr}

UNION

SELECT DISTINCT target AS id, target_field as group
FROM stat_mech
WHERE publication_year = ${sel_yr};
```



```js
function arc(nodes, edges, {width} = {}) {
const step = 14;
const marginTop = 20;
const marginRight = 400;
const marginBottom = 20;
const marginLeft = 230;
const height = 600;
const y = d3.scalePoint(orders.get("by group"), [marginTop, height - marginBottom]);

// A color scale for the nodes and links.
const color = d3.scaleOrdinal()
  .domain(nodes.map(d => d.group).sort(d3.ascending))
  .range(d3.schemeCategory10)
  .unknown("#aaa");

// A function of a link, that checks that source and target have the same group andreturns
// the group; otherwise null. Used to color the links.
const groups = new Map(nodes.map(d => [d.id, d.group]));
function samegroup({ source, target }) {
  return groups.get(source) === groups.get(target) ? groups.get(source) : null;
}

// Create the SVG container.
const svg = d3.create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .attr("style", "max-width: 100%; height: auto;");

// The current position, indexed by id. Will be interpolated.
const Y = new Map(nodes.map(({id}) => [id, y(id)]));

// Add an arc for each link.
function arc(d) {
  const y1 = Y.get(d.source);
  const y2 = Y.get(d.target);
  const r = Math.abs(y2 - y1) / 2;
  return `M${marginLeft},${y1}A${r},${r} 0,0,${y1 < y2 ? 1 : 0} ${marginLeft},${y2}`;
}

const path = svg.insert("g", "*")
    .attr("fill", "none")
    .attr("stroke-opacity", 0.6)
    .attr("stroke-width", 1.5)
  .selectAll("path")
  .data(links)
  .join("path")
    .attr("stroke", d => color(samegroup(d)))
    .attr("d", arc);

// Add a text label and a dot for each node.
const label = svg.append("g")
    .attr("font-family", "sans-serif")
    .attr("font-size", 10)
    .attr("text-anchor", "end")
  .selectAll("g")
  .data(nodes)
  .join("g")
    .attr("transform", d => `translate(${marginLeft},${Y.get(d.id)})`)
    .call(g => g.append("text")
        .attr("x", -6)
        .attr("dy", "0.35em")
        .attr("fill", d => d3.lab(color(d.group)).darker(2))
        .text(d => d.id))
    .call(g => g.append("circle")
        .attr("r", 3)
        .attr("fill", d => color(d.group)));

// Add invisible rects that update the class of the elements on mouseover.
label.append("rect")
    .attr("fill", "none")
    .attr("width", marginLeft + 40)
    .attr("height", step)
    .attr("x", -marginLeft)
    .attr("y", -step / 2)
    .attr("fill", "none")
    .attr("pointer-events", "all")
    .on("pointerenter", (event, d) => {
      svg.classed("hover", true);
      label.classed("primary", n => n === d);
      label.classed("secondary", n => links.some(({source, target}) => (
        n.id === source && d.id == target || n.id === target && d.id === source
      )));
      path.classed("primary", l => l.source === d.id || l.target === d.id).filter(".primary").raise();
    })
    .on("pointerout", () => {
      svg.classed("hover", false);
      label.classed("primary", false);
      label.classed("secondary", false);
      path.classed("primary", false).order();
    });
// Add styles for the hover interaction.
svg.append("style").text(`
  .hover text { fill: #aaa; }
  .hover g.primary text { font-weight: bold; fill: #333; }
  .hover g.secondary text { fill: #333; }
  .hover path { stroke: #ccc; }
  .hover path.primary { stroke: #333; }
`);
// A function that updates the positions of the labels and recomputes the arcs
// when passed a new order.
function update(order) {
  y.domain(order);
  label
      .sort((a, b) => d3.ascending(Y.get(a.id), Y.get(b.id)))
      .transition()
      .duration(750)
      .delay((d, i) => i * 20) // Make the movement start from the top.
      .attrTween("transform", d => {
        const i = d3.interpolateNumber(Y.get(d.id), y(d.id));
        return t => {
          const y = i(t);
          Y.set(d.id, y);
          return `translate(${marginLeft},${y})`;
        }
      });
  path.transition()
      .duration(750 + nodes.length * 20) // Cover the maximum delay of the label transition.
      .attrTween("d", d => () => arc(d));
}

  return svg.node()
}

```

<div class="grid grid-cols-2">
  <div>
    On the right, we have the subfields co-occurences within paper that have as primary topic <em>Statistical mechanics of complex networks</em>. The topic is a clustering of the citation network for works that have incoming and outgoing citations. Then, openAlex team linked the topics with subfield and fields from Scopus using Gpt-3.5 Turbo.
  </div>
  <div>${
    resize((width) => arc(nodes, links, {width}))
  }
  </div>
</div>

```js
const degree = d3.rollup(
  links.flatMap(({ source, target, value }) => [
    { node: source, value },
    { node: target, value }
  ]),
  (v) => d3.sum(v, ({ value }) => value),
  ({ node }) => node
);
```

```js
  const orders = new Map([
    ["by name", d3.sort(nodes.map((d) => d.id))],
    ["by group", d3.sort(nodes, ({group}) => group, ({id}) => id).map(({id}) => id)],
    ["by degree", d3.sort(nodes, ({id}) => degree.get(id), ({id}) => id).map(({id}) => id).reverse()]
  ]);
```

```js
const selected_links = view(Inputs.search(links))
```

<div class="card", style="padding:0">${
  Inputs.table(selected_links)
}
</div>

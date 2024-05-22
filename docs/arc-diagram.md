---
toc: false
sql: 
  stat_mech: ./data/stat_mech_networks_clean.parquet
  timeseries: ./data/timeseries.parquet
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

```js
import * as d3 from "npm:d3";
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

```sql id=[...links]
SELECT COUNT(*) as value, source, target 
FROM stat_mech 
WHERE publication_year = ${sel_yr} AND source != target 
GROUP BY source, target
```

# Exploring complex networks related topics in OpenAlex

```js
function arc(nodes, edges, {width} = {}) {
const step = 14;
const marginTop = 20;
const marginRight = 400;
const marginBottom = 20;
const marginLeft = 250;
const height = (nodes.length - 1) * step + marginTop + marginBottom;
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

We have the following question

> Is network science became more _insular_ overtime? That is, is the physics of complex networks community was more outward looking at its inception than in recent years.

Here is an idea to answer that question. Insularity here means something very close to network modularity. A community is modular when there is more edges within communities than across communities.  

<img src="https://d3i71xaburhd42.cloudfront.net/2a91c8ff11a828209f10714cfc46fd929a51e9dc/1-Figure1-1.png" width=200></img> 

Modularity maximization is an approach to community detection which propose cutting points to find the partition that maximize modularity. In the figure above, modularity is maximize by cutting through the five bridges that separate those 3 communities. 

OpenAlex--an open database for scientific works--provide topics to classify scientific works, e.g. Knowledge Management and Organizational Innovation, Coronavirus Disease 2019, Swarm Intelligence Optimization Algorithms. It is the most fine-grained labels that they have to classify works. Each paper have multiple normalized scores for multiple topics, and openAlex defined the primary topic of a paper as the topic with the greatest score. Each topic is mapped onto a single subfield, which in turn belong to a single field (see [here](https://jstonge.observablehq.cloud/hello-research-groups/overthinking-fos#openalex-taxonomy) for the classification tree). There are 4516 topics, for 252 subfields, and 26 fields.

Where do topics come from? They are clusters identified by maximizing modularity on the citation graph! OpenAlex researchers claim that this approach based on citation networks actually output research communities focused on different topics; they assume that researchers citing each other in a community will maximize modularity, and that this corresponds to topics. Once they have the communites, they ask GPT3.5 Turbo (🥲) to label them using titles (and abstract) from a representative samples of papers. Similarly, once they have the labeled communities (topics), they map those communities to known fields and subfields from SCOPUS, a well known bibliometric database. Although each paper has multiple topics, we will work with their primary topic. 

Now, how does topics relate to the insularity of a field? One way to measure if a community is insular would be to look at how their _papers_ are outward looking. More precisely, our proposal to measure insularity is to look at the _number of works cited by a given paper within the same topic over papers with different topics_. A ratio of one means that a paper, which we assume belong to a given community, is engaging with as many papers within that community than with other communities. 

Lets look at an example to help us understand the proposal. Linton Freeman article on "Centrality in social networks conceptual clarification" is characterized by the topic of _Statistical Mechanics of Complex Networks_.  This work from 1978 was cited 13 347. In return, it has cited 28 other papers, with the following counts with respect to other subfields:

```
{
  'Economic Policy and Development Analysis': 1,
  'Graph Spectra and Topological Indices': 2,
  'Statistical Physics of Opinion Dynamics': 6,
  'Graph Theory and Algorithms': 2,
  'Temporal Dynamics of Team Processes and Performance': 3,
  'Coopetition in Business Networks and Innovation': 1,
  'Stochasticity in Gene Regulatory Networks': 1,
  'The Impact of Digital Media on Public Discourse': 1,
  'Integration of Cyber, Physical, and Social Systems': 1,
  'Assessment of Sustainable Development Indicators and Strategies': 1,
  'Intergroup Relations and Social Identity Theories': 1,
  'Statistical Mechanics of Complex Networks': 2,
  'Understanding Attitudes Towards Public Transport and Private Car': 1,
  'Volunteered Geographic Information and Geospatial Crowdsourcing': 1,
  'Distributed Constraint Optimization Problems and Algorithms': 1,
  'Therapeutic Alliance in Psychotherapy': 1,
  'Impact of Technological Revolutions on Global Economy': 1,
  'Psychodynamic Psychotherapy and Developmental Trauma': 1
 }
```

where 2 papers out of 28 are directed inward, meaning that they cite other papers within the same research communities. If we find topics to be too nitty-gritty, we can do the same exercice at the level of subfields:

```
{
  'Economics and Econometrics': 1,
  'Geometry and Topology': 2,
  'Statistical and Nonlinear Physics': 8,
  'Computational Theory and Mathematics': 2,
  'Social Psychology': 3,
  'Strategy and Management': 1,
  'Molecular Biology': 1,
  'Communication': 1,
  'Control and Systems Engineering': 1,
  'Management, Monitoring, Policy and Law': 1,
  'Sociology and Political Science': 1,
  'Transportation': 1,
  'Geography, Planning and Development': 1,
  'Computer Networks and Communications': 1,
  'Clinical Psychology': 2,
  'General Economics, Econometrics and Finance': 1
}
```

In this case, 8 papers out of 28 are directed inward at the subfield level (Statistical Mechanics of Complex Networks has Statistical and Nonlinear Physics as subfield). In terms of ratio, this means that for each paper cited within the `Statistical and Nonlinear Physics`, there was 2.5 papers cited outside the community. Is both of the numbers above alot?  Lets first do the same for all papers in `Statistical and Nonlinear Physics` for, say, 1990 and 2015, and then think about some kind of null models that would tell us something about insularity of the community.  

## Scaling up

We do the same exercice, but now for each year we count the total number of outward references for all works within the `Statistical and Nonlinear Physics` research communities.

```js
Plot.plot({
  y: {
    grid:true, percent: true, label: "outward link (%)", domain: [0,100]
    },
  fy: {
    reverse: true
  },
  marginRight: 75,
  marks: [
    Plot.frame(),
    Plot.dot(ts_data_prop, 
      {x:"year", y:"outward_prop", stroke: "type", 
      title: d => `Out of ${d.total_count} outgoing citations, ${d.inward_count} were directed within the research community.`, 
      tip: true}
    ),
    Plot.lineY(ts_data_prop, 
      {x:"year", y:"outward_prop", stroke: "type", 
      title: d => `Out of ${d.total_count} outgoing citations, ${d.inward_count} were directed within the research community.`, 
      tip: true}
    ),
    Plot.text(ts_data_prop, Plot.selectLast({
      x:"year", y:"outward_prop", z: "type", fill: "type", strokeWidth: 0.6,
      text: "type",
      textAnchor: "start",
      dx: 10
    }))
  ],
  caption: "There are differences depending on how we aggregate the data. Keeping the most fine-grained level, that of topic, we can see that outward links (links toward other research communities) peak in 1998. At the most coarse-grained level, that peak happens in 1995. Why is that? This means that in 1995, 53% of outward citations in Statistical Mechanics of Complex Networks were not in the 'Physical Sciences'"
})
```

We observe that there is a 38% (going from 95% in 1997 to 57% in 2009) drop in references going outside the `Statistical and Nonlinear Physics` research community. Is this alot? Is this an artefact of our method? Perhaps it has to do with how Leiden's clustering algorithm works with respect to evolving communities? 

```sql id=ts_data_prop display
SELECT
    year,
    SUM(count) AS total_count,
    SUM(CASE WHEN category in ('Statistical Mechanics of Complex Networks', 'Statistical and Nonlinear Physics', 'Physics and Astronomy', 'Physical Sciences') THEN count ELSE 0 END) AS inward_count,
    (SUM(count) - SUM(CASE WHEN category in ('Statistical Mechanics of Complex Networks', 'Statistical and Nonlinear Physics', 'Physics and Astronomy', 'Physical Sciences') THEN count ELSE 0 END)) / SUM(count) AS outward_prop,
    type
FROM
    timeseries
GROUP BY
    year, type;
```

## Overthinking Leiden

- [openAlex: End-to-End Process for Topic Classification](https://docs.google.com/document/d/1bDopkhuGieQ4F8gGNj7sEc8WSE8mvLZS/edit?usp=sharing&ouid=106329373929967149989&rtpof=true&sd=true)
- [An open approach for classifying research publications](https://www.leidenmadtrics.nl/articles/an-open-approach-for-classifying-research-publications)
- [From Louvain to Leiden: guaranteeing well-connected communities](https://www.nature.com/articles/s41598-019-41695-z)
- [CWTSLeiden/publicationclassification](https://github.com/CWTSLeiden/publicationclassification)
- [openAlex_topic_mapping_table](https://docs.google.com/spreadsheets/d/1v-MAq64x4YjhO7RWcB-yrKV5D_2vOOsxl4u6GBKEXY8/edit?usp=sharing)

Leiden is a community-detection method that use modularity maximization to create communities. The network in question is 71 million nodes (journal articles, proceeding papers, preprting, and book chapters) and 1715 million edges (citation links), spanning from 2000 to 2023. The researchers who ran the clustering ended up with 4521 topics, or research areas, at the micro-level. 

It is good to know that the topics seen on the openAlex API is the results of a two step process. The first step included all the papers that had incoming or outgoing citation data, which is a third of the data available in openAlex. As a second step, OpenAlex folks extended the labeling by first embedding combinations of journal title, abstract (when available), and journal names using [setence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), then use that as feature to do another round of supervised topic modeling.

Does Leiden a good algorithm for what we are doing? We want to measure network insularity of what we call network science. Right now, we are assuming that 'network science' is well approximated by the topic of 'Statistical Mechanics of Complex Networks'. But this community was found through the process explained above. What if patterns in citations changed overtime, so that a latent community splitted into two communities? Does the Leiden algorithm will find the dense community at first, and then disregard changes over time? 

## Looking at topic co-occurences for the beauty of it

```js
const sel_yr = view(Inputs.range([1990, 2020], {step:1}))
```

<div class="grid grid-cols-2">
  <div>
    The arc diagram displays subfields co-occurences within paper with <em>Statistical mechanics of complex networks</em> as primary topic. Nodes are colored according to their field of research. This is a very neat way to know which subfields tend to show up together. 
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
const selected_links = view(Inputs.search(nodes))
```

<div class="card", style="padding:0">${
  Inputs.table(selected_links)
}
</div>

```sql id=[...nodesRaw]
SELECT DISTINCT title, cited_by_count, subfield
FROM stat_mech
WHERE publication_year = ${sel_yr}
```

```js
nodesRaw
```

```sql id=[...selflinks]
SELECT COUNT(*) as value, source, target 
FROM stat_mech 
WHERE publication_year = ${sel_yr} AND source = target 
GROUP BY source, target
```
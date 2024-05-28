---
toc: false
sql: 
  stat_mech: ./data/t10064_clean.parquet
---



# Exploring complex networks related topics in OpenAlex

See [docs](https://help.openalex.org/how-it-works/topics)

```js
const topN = view(Inputs.range([30, 100], { step: 1, label: "top N papers by citations", value: 30 }))
```

---

## 10K papers from statistical mechanics of complex networks


- [openAlex query](https://openalex.org/works?page=1&filter=primary_topic.id%3At10064)

```sql id=[...rangeYr]
SELECT MIN(publication_year) as min_yr, MAX(publication_year) as max_yr FROM stat_mech
```

```js
const year = view(Inputs.range([rangeYr[0].min_yr,rangeYr[0].max_yr], { step:1, value: 2000 }) )
```

```sql id=stat_mech
SELECT 
DISTINCT title, cited_by_count, publication_year, source, target, authorships
FROM stat_mech WHERE publication_year = ${year}
```

<div>${
    resize((width) => plot_top_n(stat_mech, {width}))
  }</div>
<div class="card" style="padding:0">
  ${
    Inputs.table(selected_papers)
  }
</div>

```js
const selected_papers=view(Inputs.search(stat_mech, {label: "search table"}))
```

## Who is part of the community?

This plot can be confusing at first, but I swear it is useful. The plot shows ranking across time for the top 30 contributors to the communities by year. For instance, Newman started at rank 14 with 2 papers in 1999 (hover on the names to see details). Then he took first position for the succesive 3 years. He didn't make the top 30 in 2005, then reappeared sporadically in 2006 (r=15) and 2008 (r=29). We only show author names who've been present in 2 consecutive years. What is nice with this plot is that path lengths give an idea of persistence over time for authors, with color indicating if they move up (purple) or down (yellowish) in the hierarchy. 

```js
const f = view(Inputs.form({
  min_yr: Inputs.range([1970, 2020], {step: 1, value: 1998, label: "min year"}),
  max_yr: Inputs.range([1971, 2021], {step: 1, value: 2011, label: "max year"})
}))
```

<div class="card">
 ${BumpChart(dat_count.filter(d => d.year >= new Date(`${f.min_yr}-01-01`) && d.year <= new Date(`${f.max_yr}-01-01`) ), {width:1200})}
</div>


```js
function BumpChart(data, {x = "year", y = "count", z = "display_name", width} = {}) {
  const rank = Plot.stackY2({x, z, order: y, reverse: true});
  const [xmin, xmax] = d3.extent(Plot.valueof(data, x));
  return Plot.plot({
    width,
    height: 800,
    x: { inset: 100, label: null, grid: true},
    y: { inset: 20, reverse: true, label: "Rank (# papers in a given year)", labelAnchor: "center", labelArrow: false, tickSize: 0, tickPadding: -10 },
    color: { scheme: "viridis", range: [0.2, 1], reverse: true },
    marks: [
      Plot.lineY(data, Plot.binX({x: "first", y: "first", filter: null}, {
        ...rank,
        stroke: rank.y,
        strokeWidth: 0.5,
        // strokeWidth: 10,
        curve: "bump-x",
        sort: {color: "y", reduce: "first"},
        interval: "year",
        strokeOpacity: 1,
        // strokeOpacity: 0.2,
        render: halo({stroke: "var(--theme-background-alt)", strokeWidth: 3})
      })),
      Plot.text(data, {
        ...rank,
        text: d => d.consecutive ? d.display_name.split(" ")[d.display_name.split(" ").length-1] : "",
        fill: rank.y,
        fontSize: 10,
        title: d => `${d.display_name} (#papers: ${d.count})`,
        tip: {format: {y: null, text: null}}
      })
    ]
  })
}
```

```js
function halo({stroke = "currentColor", strokeWidth = 3} = {}) {
  return (index, scales, values, dimensions, context, next) => {
    const g = next(index, scales, values, dimensions, context);
    for (const path of [...g.childNodes]) {
      const clone = path.cloneNode(true);
      clone.setAttribute("stroke", stroke);
      clone.setAttribute("stroke-width", strokeWidth);
      path.parentNode.insertBefore(clone, path);
    }
    return g;
  };
}
```

```js
function get_top_10_authors_by_year_with_counts() {
    const authorCountsByYear = {};

  // Collect counts per year and per author
  for (let i = 1; i < rawDat.length; i++) {
    const year = new Date(rawDat[i].publication_year, 0, 1); // Create a Date object for the year
    const authorInfo = JSON.parse(rawDat[i].authorships);

    if (!authorCountsByYear[year.getTime()]) {
      authorCountsByYear[year.getTime()] = {};
    }

    for (let a of authorInfo) {
      const authorName = a.author.display_name;

      if (authorCountsByYear[year.getTime()][authorName]) {
        authorCountsByYear[year.getTime()][authorName].count++;
      } else {
        authorCountsByYear[year.getTime()][authorName] = {
          display_name: authorName,
          count: 1,
        };
      }
    }
  }

  // Flatten the structure and calculate ranks
  const flatList = [];

  for (const yearTime in authorCountsByYear) {
    const year = new Date(parseInt(yearTime)); // Convert back to Date object
    const authors = Object.values(authorCountsByYear[yearTime]);
    authors.sort((a, b) => b.count - a.count);

    // Take only the top 10
    authors.slice(0, 30).forEach((entry, index) => {
      flatList.push({
        year: year,
        display_name: entry.display_name,
        count: entry.count,
        rank: index + 1, // Adding rank here for clarity
      });
    });
  }

  // Track author appearances
  const authorAppearances = {};

  flatList.forEach(entry => {
    const yearTime = entry.year.getTime();
    if (!authorAppearances[entry.display_name]) {
      authorAppearances[entry.display_name] = [];
    }
    authorAppearances[entry.display_name].push(yearTime);
  });

  // Add flag for consecutive appearances
  flatList.forEach(entry => {
    const years = authorAppearances[entry.display_name].sort((a, b) => a - b);
    entry.consecutive = false;

    for (let i = 0; i < years.length - 1; i++) {
      if (years[i + 1] === years[i] + 31536000000) { // 1 year in milliseconds
        entry.consecutive = true;
        break;
      }
    }
  });

  return flatList;
}
```


```js
const dat_count = get_top_10_authors_by_year_with_counts()
```


---

## Raw table

```sql id=[...rawDat] display
SELECT DISTINCT(*) FROM stat_mech ORDER BY publication_year
```

---

## SQL table description

```sql
DESCRIBE TABLE stat_mech
```


```js
function plot_top_n(data, {width} = {}) {
  return Plot.plot({
    marginLeft: 650,
    marginRight: 300,
    width,
    x: {grid: true},
    marks: [
      Plot.barX(data, {
        x: "cited_by_count",
        y: "title",
        sort: { y: "x", reverse: true, limit: topN }
      }),
      Plot.text(data, {
        text: d => `${JSON.parse(d.authorships).map(d=>d.author.display_name).join("; ")}`,
        x: "cited_by_count",
        y: "title",
        textAnchor: "start",
        dx: 3
      })
    ]
  })
}
```
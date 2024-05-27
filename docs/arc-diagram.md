---
toc: false
sql: 
  css: ./data/t13910_clean.parquet
---


<style>

.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
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
        dx: 3,
        fill: "black"
      })
    ]
  })
}
```
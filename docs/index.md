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

## 10K papers from statistical mechanics of complex networks

[openAlex](https://openalex.org/works?page=1&filter=primary_topic.id%3At10064)


```sql id=stat_mech
SELECT DISTINCT title, authorships, cited_by_count FROM stat_mech
```

```js
const selected_papers=view(Inputs.search(stat_mech))
```
```js
Inputs.table(selected_papers)
```

```js
[...stat_mech].map(d=>JSON.parse(d.authorships).map(d=>d.author.display_name).join("; "))
```

```js
Plot.plot({
  marginLeft: 500,
  marginRight: 400,
  width: 1200,
  x: {grid: true},
  marks: [
    Plot.barX(stat_mech, {
      x: "cited_by_count",
      y: "title",
      sort: { y: "x", reverse: true, limit: 40 }
    }),
    Plot.text(stat_mech, {
      text: d => `${JSON.parse(d.authorships).map(d=>d.author.display_name).join("; ")}`,
      x: "cited_by_count",
      y: "title",
      textAnchor: "start",
      dx: 3,
      fill: "black"
    })
  ]
})
```


## 10K papers from Dynamical synchronization of complex networks

[openAlex](https://openalex.org/works?page=1&filter=primary_topic.id%3At10064)

```sql
SELECT * FROM dyn_sync
```


## table description

```sql
DESCRIBE TABLE stat_mech
```
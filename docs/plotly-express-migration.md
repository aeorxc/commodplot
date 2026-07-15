# Plotly Express migration and facet APIs

commodplot keeps desk-specific chart behavior where it adds value: seasonal
and reindex-year transforms, forward overlays, range and average bands, title
summaries, visible-year rules, fitted scatter lines, and last-N paths. Generic
bar and area wrappers now have direct Plotly Express replacements.

## Generic wrapper replacements

The compatibility wrappers remain callable, but emit an actionable
`FutureWarning` at the caller. They continue accepting previously ignored
keyword arguments during the transition.

### `bar_chart`

```python
# Compatibility wrapper
fig = commodplot.bar_chart(df, title="Balances", barmode="stack")

# Native Plotly replacement
fig = px.bar(
    df,
    x=df.index,
    y=list(df.columns),
    title="Balances",
    barmode="stack",
)
```

### `horizontal_bar_plot`

The wrapper plots only the first DataFrame column. Make that selection explicit
when migrating:

```python
fig = px.bar(
    x=df.iloc[:, 0],
    y=df.index,
    orientation="h",
    title="Share by region",
    labels={"x": str(df.columns[0]), "y": str(df.index.name or "")},
)
```

### `stacked_area_chart`

```python
fig = px.area(
    df,
    x=df.index,
    y=list(df.columns),
    title="Capacity offline",
)
```

If a consumer depends on exact serialized trace fields rather than rendered
behavior, compare its generated HTML before switching. The compatibility
wrappers deliberately remove PX-inferred hover, legend-group, orientation, and
axis metadata to retain the existing commodplot contract.

`line_plot` and `timeseries_scatter_plot` are not deprecated. Their public
behavior includes desk-specific forward, title, fit-line, and last-N features
that do not have a complete one-call PX replacement.

## Seasonal facets

`seas_line_facets` accepts either a wide DataFrame or an ordered mapping of
single-series panels. Forward data is matched by column or mapping key, not by
position. Missing forward keys are allowed; unknown forward keys are rejected.

```python
fig = commodplot.seas_line_facets(
    history,
    fwd=forward,
    facet_col_wrap=2,
    facet_titles={"Brent": "Brent $/bbl"},
    shared_xaxes=True,
    shared_yaxes=False,
    legend_mode="shared",  # "shared", "each", or "none"
    shaded_range=5,
    average_line=5,
)
```

Each panel independently seasonalizes its input and retains trace adjacency and
ordering: range maximum, range minimum, average, history, then forward. A
supplied `yaxis_title` is applied to every active panel axis.

## Reindex-year facets

`reindex_year_line_facets` accepts an ordered mapping or sequence of DataFrames.
Each panel independently performs its reindex transform and prompt selection.
`max_results` is applied after each panel is transformed. With independent
x-axes, every panel receives its own trailing three-year range. With
`shared_xaxes=True`, every active panel uses the common union of those local
ranges so Plotly's matched axes cannot clip a longer panel.

```python
fig = commodplot.reindex_year_line_facets(
    {"JanFeb": jan_feb, "JunJul": jun_jul},
    facet_col_wrap=2,
    facet_titles={"JanFeb": "Jan/Feb"},
    legend_mode="shared",
    shaded_range=5,
)
```

`seas_line_subplot` and `reindex_year_line_subplot` remain compatibility
wrappers and now emit `FutureWarning`. New code should use the facet APIs. The
legacy seasonal subplot continues to ignore `average_line`; the new facet API
supports it.

## Seasonal transform shim lifecycle

`commodplot.commodplottransform.seasonalise` remains unchanged in this release.
The canonical transform is `commodutil.transforms.seasonalize`.

The migration audit found two direct external consumers:

- `oilfundamentals/oilfundamentals/highfrequency/summary.py`
- `oilfundamentalsreports/oilfundamentalsreports/tars/tar_pages.py`

commodplot also has two internal calls in
`commodplot/commodplottrace.py`: one for historical seasonal traces and one for
forward seasonal traces. Internal and external calls all count as consumers for
the removal gate.

Lifecycle:

1. During 3.7.x, migrate the two internal and two external calls to
   `commodutil.transforms.seasonalize`. Keep the shim silent and behaviorally
   unchanged until those migrations are published.
2. After all known consumers migrate, emit `FutureWarning` for at least one
   complete published minor cadence: the full 3.8.x line.
3. Remove the shim no earlier than commodplot 4.0, and only after a fresh audit
   confirms zero internal and external consumers.

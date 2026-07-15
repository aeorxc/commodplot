# Plotly migration and facet APIs

commodplot keeps wrappers where they add desk-specific behavior: seasonal and
reindex-year transforms, forward overlays, range bands, title summaries, and
visibility rules. Generic bar and area charts should use Plotly Express.

## Generic wrapper replacements

The compatibility wrappers remain callable and preserve their existing output,
but now emit `FutureWarning` at the caller.

```python
import plotly.express as px

# bar_chart(df, title="Balances", barmode="stack")
fig = px.bar(
    df,
    x=df.index,
    y=list(df.columns),
    title="Balances",
    barmode="stack",
)

# horizontal_bar_plot(df, title="Share") uses only the first column
fig = px.bar(
    x=df.iloc[:, 0],
    y=df.index,
    orientation="h",
    title="Share",
)

# stacked_area_chart(df, title="Capacity offline")
fig = px.area(
    df,
    x=df.index,
    y=list(df.columns),
    title="Capacity offline",
)
```

`line_plot` and `timeseries_scatter_plot` are not deprecated. They retain
forward-overlay, fitted-line, and last-N behavior that is not a one-call Plotly
Express replacement.

## Seasonal facets

`seas_line_facets` accepts a wide history DataFrame and an optional wide forward
DataFrame. It calls `seas_line_plot` independently for each history column, so
the single-panel transform and trace behavior remain canonical. Forward columns
are matched by name; missing columns simply have no forward overlay.

```python
fig = commodplot.seas_line_facets(
    history,
    fwd=forward,
    facet_col_wrap=2,
    subplot_titles=["Brent", "WTI"],
    shaded_range=5,
    average_line=5,
)
```

## Reindex-year facets

`reindex_year_line_facets` accepts a sequence of DataFrames and calls
`reindex_year_line_plot` for each panel.

```python
fig = commodplot.reindex_year_line_facets(
    [jan_feb, jun_jul],
    facet_col_wrap=2,
    subplot_titles=["Jan/Feb", "Jun/Jul"],
    shaded_range=5,
)
```

Both facet helpers accept only `facet_col_wrap` and `subplot_titles` as
facet-specific options. Other keyword arguments are passed to the corresponding
single-panel function. The first panel retains its trace legend settings;
duplicate legend entries are hidden on later panels.

`seas_line_subplot` and `reindex_year_line_subplot` remain exact compatibility
adapters and now emit `FutureWarning`. New code should use the facet helpers.

## Seasonal transform shim lifecycle

`commodplot.commodplottransform.seasonalise` remains unchanged. The canonical
transform is `commodutil.transforms.seasonalize`, but two internal and two known
external callers still use the shim. Migrate those callers during 3.7.x, warn
for at least the complete 3.8.x line, and remove the shim no earlier than 4.0
after a fresh consumer audit.

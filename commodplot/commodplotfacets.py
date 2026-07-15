from collections.abc import Sequence
from copy import deepcopy

import pandas as pd
from plotly.subplots import make_subplots


def _compose(figures, subplot_titles, facet_col_wrap, title):
    if isinstance(facet_col_wrap, bool) or not isinstance(facet_col_wrap, int):
        raise TypeError("facet_col_wrap must be a positive integer.")
    if facet_col_wrap < 1:
        raise ValueError("facet_col_wrap must be a positive integer.")
    if not figures:
        raise ValueError("Facet data must contain at least one panel.")

    if subplot_titles is not None and len(subplot_titles) != len(figures):
        raise ValueError("subplot_titles must contain one title per panel.")
    titles = list(subplot_titles) if subplot_titles is not None else [None] * len(figures)
    cols = min(facet_col_wrap, len(figures))
    rows = (len(figures) + cols - 1) // cols
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=titles)

    for index, child in enumerate(figures):
        row, col = divmod(index, cols)
        row += 1
        col += 1
        for child_trace in child.data:
            trace = deepcopy(child_trace)
            if index > 0:
                trace.showlegend = False
            fig.add_trace(trace, row=row, col=col)

        xaxis = child.layout.xaxis
        axis_kwargs = {
            name: getattr(xaxis, name, None)
            for name in ("type", "tick0", "dtick", "tickformat", "ticklabelmode", "range")
            if getattr(xaxis, name, None) is not None
        }
        fig.update_xaxes(row=row, col=col, **axis_kwargs)
        yaxis_title = child.layout.yaxis.title.text
        if yaxis_title is not None:
            fig.update_yaxes(title_text=yaxis_title, row=row, col=col)

    first = figures[0].layout
    fig.update_layout(
        title=title,
        title_x=0.01,
        legend=first.legend.to_plotly_json(),
        hovermode=first.hovermode,
        margin=first.margin.to_plotly_json(),
        template=first.template,
    )
    return fig


def seas_line_facets(df, fwd=None, *, facet_col_wrap=2, subplot_titles=None, **kwargs):
    """Plot each column of a wide history DataFrame as a seasonal panel."""
    from commodplot import commodplot as cpl

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")
    if fwd is not None and not isinstance(fwd, pd.DataFrame):
        raise TypeError("fwd must be a pandas DataFrame or None.")
    figures = [
        cpl.seas_line_plot(
            df[column],
            fwd=fwd[column] if fwd is not None and column in fwd.columns else None,
            **kwargs,
        )
        for column in df.columns
    ]
    titles = list(map(str, df.columns)) if subplot_titles is None else subplot_titles
    return _compose(figures, titles, facet_col_wrap, kwargs.get("title", ""))


def reindex_year_line_facets(
    dfs, *, facet_col_wrap=2, subplot_titles=None, **kwargs
):
    """Plot a sequence of year-columned DataFrames as reindex-year panels."""
    from commodplot import commodplot as cpl

    if isinstance(dfs, pd.DataFrame) or not isinstance(dfs, Sequence):
        raise TypeError("dfs must be a sequence of pandas DataFrames.")
    if any(not isinstance(df, pd.DataFrame) for df in dfs):
        raise TypeError("Every reindex facet panel must be a pandas DataFrame.")
    figures = [cpl.reindex_year_line_plot(df, **kwargs) for df in dfs]
    return _compose(figures, subplot_titles, facet_col_wrap, kwargs.get("title", ""))

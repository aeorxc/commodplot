import json
from types import SimpleNamespace

import pandas as pd
import plotly.graph_objects as go
import pytest
from commodutil import dates
from plotly.utils import PlotlyJSONEncoder

from commodplot import commodplot
from commodplot.commodplotfacets import _compose


def _normalise_plotly(value):
    return json.loads(json.dumps(value.to_plotly_json(), cls=PlotlyJSONEncoder))


def _seasonal_inputs():
    history_index = pd.date_range(
        f"{dates.curyear - 3}-01-01",
        f"{dates.curyear - 1}-12-31",
        freq="B",
    )
    history = pd.DataFrame(
        {
            "A": range(len(history_index)),
            "B": range(10, 10 + len(history_index)),
        },
        index=history_index,
    )
    forward_index = pd.date_range(f"{dates.curyear}-01-01", periods=4, freq="MS")
    forward = pd.DataFrame({"A": range(100, 104)}, index=forward_index)
    return history, forward


def _reindex_frame(offset=0):
    index = pd.date_range(
        f"{dates.curyear - 3}-01-01",
        f"{dates.curyear}-06-30",
        freq="7D",
    )
    return pd.DataFrame(
        {
            f"Q1 {dates.curyear - 2}": range(offset, offset + len(index)),
            f"Q1 {dates.curyear - 1}": range(offset, offset + len(index)),
            f"Q1 {dates.curyear}": range(offset + 10, offset + 10 + len(index)),
        },
        index=index,
    )


def _panel_traces(figure, xaxis):
    return [trace for trace in figure.data if trace.xaxis == xaxis]


def _assert_trace_equivalence(child, panel, *, first_panel):
    assert len(child.data) == len(panel)
    for expected, actual in zip(child.data, panel):
        assert actual.showlegend == (expected.showlegend if first_panel else False)
        expected_json = _normalise_plotly(expected)
        actual_json = _normalise_plotly(actual)
        for value in (expected_json, actual_json):
            value.pop("xaxis", None)
            value.pop("yaxis", None)
            value.pop("showlegend", None)
        assert actual_json == expected_json


def _axis_contract(axis):
    values = axis.to_plotly_json()
    return {
        key: values[key]
        for key in ("type", "tick0", "dtick", "tickformat", "ticklabelmode", "range")
        if key in values
    }


def test_facet_composer_supports_axes_without_ticklabelmode():
    child = SimpleNamespace(
        data=[],
        layout=SimpleNamespace(
            xaxis=SimpleNamespace(
                type="date", tick0=None, dtick=None, tickformat="%b", range=None
            ),
            yaxis=SimpleNamespace(title=SimpleNamespace(text=None)),
            legend=go.layout.Legend(),
            hovermode=None,
            margin=go.layout.Margin(),
            template=None,
        ),
    )

    figure = _compose([child], subplot_titles=None, facet_col_wrap=1, title="")

    assert figure.layout.xaxis.type == "date"
    assert figure.layout.xaxis.tickformat == "%b"


@pytest.mark.parametrize("empty", [False, True])
def test_deprecated_generic_wrappers_warn_and_preserve_exact_output(empty):
    index = pd.DatetimeIndex([], name="Date") if empty else pd.date_range(
        "2026-01-01", periods=3, name="Date"
    )
    frame = pd.DataFrame(index=index, columns=["A", "B"], dtype=float)
    if not empty:
        frame.loc[:, "A"] = [1, 2, 3]
        frame.loc[:, "B"] = [4, 5, 6]

    with pytest.warns(FutureWarning, match="plotly.express.bar") as bar_warning:
        bars = commodplot.bar_chart(frame, title="Bars", barmode="stack")
    expected_bars = go.Figure(
        [go.Bar(x=frame.index, y=frame[column], name=column) for column in frame]
    )
    expected_bars.update_layout(
        title="Bars", hovermode="x", margin=commodplot.preset_margins, barmode="stack"
    )

    with pytest.warns(FutureWarning, match="orientation='h'") as horizontal_warning:
        horizontal = commodplot.horizontal_bar_plot(
            frame, title="Horizontal", bargap=0.4, width=500, height=300
        )
    expected_horizontal = go.Figure(
        [go.Bar(x=frame.iloc[:, 0], y=frame.index, orientation="h")]
    )
    expected_horizontal.update_layout(
        title="Horizontal",
        xaxis_title="A",
        yaxis_title="Date",
        bargap=0.4,
        width=500,
        height=300,
    )

    with pytest.warns(FutureWarning, match="plotly.express.area") as area_warning:
        area = commodplot.stacked_area_chart(
            frame, title="Area", stackgroup="desk", showlegend=False
        )
    expected_area = go.Figure(
        [
            go.Scatter(
                x=frame.index,
                y=frame[column],
                name=column,
                stackgroup="desk",
                showlegend=False,
            )
            for column in frame
        ]
    )
    expected_area.update_layout(
        title="Area", showlegend=False, margin=commodplot.preset_margins
    )

    assert _normalise_plotly(bars) == _normalise_plotly(expected_bars)
    assert _normalise_plotly(horizontal) == _normalise_plotly(expected_horizontal)
    assert _normalise_plotly(area) == _normalise_plotly(expected_area)
    assert all(
        warning[0].filename == __file__
        for warning in (bar_warning, horizontal_warning, area_warning)
    )


def test_deprecated_subplot_adapters_keep_legacy_quirks():
    history, forward = _seasonal_inputs()
    with pytest.warns(FutureWarning, match="seas_line_facets") as seasonal_warning:
        seasonal = commodplot.seas_line_subplot(
            1,
            2,
            history,
            fwd=forward.assign(B=range(200, 204)),
            average_line=2,
            yaxis_title="ignored",
        )
    assert not any(trace.name.endswith("Avg") for trace in seasonal.data)
    assert seasonal.layout.yaxis.title.text is None
    assert seasonal.layout.yaxis2.title.text is None

    frames = [_reindex_frame(), _reindex_frame(10)]
    with pytest.warns(FutureWarning, match="reindex_year_line_facets") as first_warning:
        limited = commodplot.reindex_year_line_subplot(
            1, 2, frames, max_results=5, yaxis_title="$/bbl"
        )
    with pytest.warns(FutureWarning):
        unlimited = commodplot.reindex_year_line_subplot(1, 2, frames)
    assert [list(trace.x) for trace in limited.data] == [
        list(trace.x) for trace in unlimited.data
    ]
    assert limited.layout.yaxis.title.text == "$/bbl"
    assert limited.layout.yaxis2.title.text is None
    assert seasonal_warning[0].filename == __file__
    assert first_warning[0].filename == __file__


def test_seasonal_facets_compose_single_panel_figures_without_restyling():
    history, forward = _seasonal_inputs()
    kwargs = {
        "title": "Seasonal desk",
        "shaded_range": 2,
        "average_line": 2,
        "yaxis_title": "$/bbl",
        "template": "plotly_white",
    }
    expected = [
        commodplot.seas_line_plot(history["A"], fwd=forward["A"], **kwargs),
        commodplot.seas_line_plot(history["B"], **kwargs),
    ]
    actual = commodplot.seas_line_facets(
        history,
        fwd=forward,
        facet_col_wrap=2,
        subplot_titles=["Alpha", "Beta"],
        **kwargs,
    )

    assert [annotation.text for annotation in actual.layout.annotations] == ["Alpha", "Beta"]
    assert actual.layout.title.text == "Seasonal desk"
    assert _normalise_plotly(actual.layout.template) == _normalise_plotly(
        expected[0].layout.template
    )
    for index, (child, xaxis_name, layout_axis_name) in enumerate(
        zip(expected, ("x", "x2"), ("xaxis", "xaxis2"))
    ):
        _assert_trace_equivalence(
            child, _panel_traces(actual, xaxis_name), first_panel=index == 0
        )
        assert _axis_contract(getattr(actual.layout, layout_axis_name)) == (
            _axis_contract(child.layout.xaxis)
        )
        assert getattr(actual.layout, f"yaxis{index + 1 if index else ''}").title.text == (
            child.layout.yaxis.title.text
        )


def test_reindex_facets_compose_single_panel_figures_without_restyling():
    frames = [_reindex_frame(), _reindex_frame(10)]
    kwargs = {"title": "Reindex desk", "shaded_range": 2, "max_results": 40}
    expected = [commodplot.reindex_year_line_plot(frame, **kwargs) for frame in frames]
    actual = commodplot.reindex_year_line_facets(
        frames, facet_col_wrap=1, subplot_titles=["Front", "Back"], **kwargs
    )

    assert [annotation.text for annotation in actual.layout.annotations] == ["Front", "Back"]
    assert actual.layout.title.text == "Reindex desk"
    for index, (child, xaxis_name, layout_axis_name) in enumerate(
        zip(expected, ("x", "x2"), ("xaxis", "xaxis2"))
    ):
        _assert_trace_equivalence(
            child, _panel_traces(actual, xaxis_name), first_panel=index == 0
        )
        assert _axis_contract(getattr(actual.layout, layout_axis_name)) == (
            _axis_contract(child.layout.xaxis)
        )


def test_lean_facet_contract_rejects_invalid_container_and_grid_inputs():
    history, _ = _seasonal_inputs()
    with pytest.raises(TypeError, match="df must be"):
        commodplot.seas_line_facets([history])
    with pytest.raises(TypeError, match="fwd must be"):
        commodplot.seas_line_facets(history, fwd=history["A"])
    with pytest.raises(TypeError, match="sequence"):
        commodplot.reindex_year_line_facets(_reindex_frame())
    with pytest.raises(TypeError, match="Every reindex"):
        commodplot.reindex_year_line_facets([pd.Series(dtype=float)])
    with pytest.raises(ValueError, match="at least one"):
        commodplot.seas_line_facets(pd.DataFrame())
    with pytest.raises(ValueError, match="positive integer"):
        commodplot.seas_line_facets(history, facet_col_wrap=0)
    with pytest.raises(ValueError, match="one title per panel"):
        commodplot.seas_line_facets(history, subplot_titles=["only one"])

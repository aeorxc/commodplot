import json
from collections import OrderedDict

import pandas as pd
import plotly.graph_objects as go
import pytest
from commodutil import dates, transforms
from plotly.utils import PlotlyJSONEncoder

from commodplot import commodplot
from commodplot import commodplottrace


def _normalise_plotly(value):
    return json.loads(json.dumps(value.to_plotly_json(), cls=PlotlyJSONEncoder))


def _seasonal_inputs(columns=("A", "B", "C")):
    history_index = pd.date_range(
        f"{dates.curyear - 3}-01-01",
        f"{dates.curyear - 1}-12-31",
        freq="B",
    )
    history = pd.DataFrame(
        {
            column: range(offset, offset + len(history_index))
            for offset, column in enumerate(columns)
        },
        index=history_index,
    )
    forward_index = pd.date_range(f"{dates.curyear}-01-01", periods=4, freq="MS")
    forward = pd.DataFrame(
        {
            column: range(offset + 100, offset + 100 + len(forward_index))
            for offset, column in enumerate(columns)
        },
        index=forward_index,
    )
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


def _traces_for_axis(fig, axis_name):
    return [trace for trace in fig.data if trace.xaxis == axis_name]


def test_bar_chart_delegates_to_px_and_preserves_legacy_contract(mocker):
    index = pd.date_range("2026-01-01", periods=3, name="Date")
    frame = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}, index=index)
    px_bar = mocker.spy(commodplot.px, "bar")

    with pytest.warns(FutureWarning, match="plotly.express.bar") as caught:
        actual = commodplot.bar_chart(
            frame, title="Bars", barmode="stack", yaxis_title="ignored"
        )

    legacy = go.Figure()
    for column in frame.columns:
        legacy.add_trace(go.Bar(x=frame.index, y=frame[column], name=column))
    legacy.update_layout(
        title="Bars",
        hovermode="x",
        margin=commodplot.preset_margins,
        barmode="stack",
    )
    assert _normalise_plotly(actual) == _normalise_plotly(legacy)
    assert px_bar.call_count == len(frame.columns)
    assert caught[0].filename == __file__


def test_horizontal_bar_delegates_to_px_and_preserves_legacy_contract(mocker):
    index = pd.Index(["one", "two"], name="Bucket")
    frame = pd.DataFrame({"Value": [1, 2], "ignored": [3, 4]}, index=index)
    px_bar = mocker.spy(commodplot.px, "bar")

    with pytest.warns(FutureWarning, match="orientation='h'") as caught:
        actual = commodplot.horizontal_bar_plot(
            frame, title="Horizontal", bargap=0.4, width=500, height=300
        )

    legacy = go.Figure(
        data=[go.Bar(x=frame.iloc[:, 0], y=frame.index, orientation="h")]
    )
    legacy.update_layout(
        title="Horizontal",
        xaxis_title="Value",
        yaxis_title="Bucket",
        bargap=0.4,
        width=500,
        height=300,
    )
    assert _normalise_plotly(actual) == _normalise_plotly(legacy)
    assert px_bar.call_count == 1
    assert caught[0].filename == __file__


def test_stacked_area_delegates_to_px_and_preserves_legacy_contract(mocker):
    index = pd.date_range("2026-01-01", periods=3)
    frame = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}, index=index)
    px_area = mocker.spy(commodplot.px, "area")

    with pytest.warns(FutureWarning, match="plotly.express.area") as caught:
        actual = commodplot.stacked_area_chart(
            frame,
            title="Area",
            stackgroup="desk",
            showlegend=False,
            hovermode="ignored",
        )

    legacy = go.Figure()
    for column in frame.columns:
        legacy.add_trace(
            go.Scatter(
                x=frame.index,
                y=frame[column],
                name=column,
                stackgroup="desk",
                showlegend=False,
            )
        )
    legacy.update_layout(
        title="Area", showlegend=False, margin=commodplot.preset_margins
    )
    assert _normalise_plotly(actual) == _normalise_plotly(legacy)
    assert px_area.call_count == len(frame.columns)
    assert caught[0].filename == __file__


def test_generic_wrappers_preserve_zero_row_legacy_contract(mocker):
    empty = pd.DataFrame(columns=["A", "B"], index=pd.DatetimeIndex([], name="Date"))
    px_bar = mocker.spy(commodplot.px, "bar")
    px_area = mocker.spy(commodplot.px, "area")

    with pytest.warns(FutureWarning):
        bars = commodplot.bar_chart(empty, title="Empty", barmode="stack")
    legacy_bars = go.Figure()
    for column in empty.columns:
        legacy_bars.add_trace(go.Bar(x=empty.index, y=empty[column], name=column))
    legacy_bars.update_layout(
        title="Empty",
        hovermode="x",
        margin=commodplot.preset_margins,
        barmode="stack",
    )

    with pytest.warns(FutureWarning):
        horizontal = commodplot.horizontal_bar_plot(empty, title="Empty")
    legacy_horizontal = go.Figure(
        data=[go.Bar(x=empty.iloc[:, 0], y=empty.index, orientation="h")]
    )
    legacy_horizontal.update_layout(
        title="Empty",
        xaxis_title="A",
        yaxis_title="Date",
        bargap=0.25,
        width=None,
        height=None,
    )

    with pytest.warns(FutureWarning):
        area = commodplot.stacked_area_chart(
            empty, title="Empty", stackgroup="desk", showlegend=False
        )
    legacy_area = go.Figure()
    for column in empty.columns:
        legacy_area.add_trace(
            go.Scatter(
                x=empty.index,
                y=empty[column],
                name=column,
                stackgroup="desk",
                showlegend=False,
            )
        )
    legacy_area.update_layout(
        title="Empty", showlegend=False, margin=commodplot.preset_margins
    )

    assert _normalise_plotly(bars) == _normalise_plotly(legacy_bars)
    assert _normalise_plotly(horizontal) == _normalise_plotly(legacy_horizontal)
    assert _normalise_plotly(area) == _normalise_plotly(legacy_area)
    assert px_bar.call_count == 0
    assert px_area.call_count == 0


def test_px_normalisation_uses_only_stable_serialised_xy(mocker):
    class FutureTrace:
        def __init__(self, x, y):
            self._properties = {
                "x": x,
                "y": y,
                "future_schema_property": "must not leak",
                "fillpattern": {"shape": "/"},
                "alignmentgroup": "px-version-specific",
            }

        def to_plotly_json(self):
            return self._properties

    class FutureFigure:
        def __init__(self, x, y):
            self.data = [FutureTrace(x, y)]

    frame = pd.DataFrame({"A": [1, 2]}, index=pd.date_range("2026-01-01", periods=2))
    mocker.patch.object(
        commodplot.px,
        "bar",
        side_effect=lambda x, y, orientation=None: FutureFigure(x, y),
    )
    mocker.patch.object(
        commodplot.px,
        "area",
        side_effect=lambda x, y: FutureFigure(x, y),
    )

    with pytest.warns(FutureWarning):
        bar = commodplot.bar_chart(frame)
    with pytest.warns(FutureWarning):
        area = commodplot.stacked_area_chart(frame, showlegend=False)

    assert set(bar.data[0].to_plotly_json()) == {"name", "x", "y", "type"}
    assert set(area.data[0].to_plotly_json()) == {
        "name",
        "showlegend",
        "stackgroup",
        "x",
        "y",
        "type",
    }


def test_timeseries_trace_uses_px_without_changing_trace_contract(mocker):
    series = pd.Series(
        [1.0, None, 3.0],
        index=pd.date_range("2026-01-01", periods=3),
        name="A",
    )
    px_line = mocker.spy(commodplottrace.px, "line")

    actual = commodplottrace.timeseries_trace(
        series, legendgroup="A", visible=True, color="red"
    )
    clean = series.dropna()
    legacy = go.Scatter(
        x=clean.index,
        y=clean.values,
        hoverinfo="y",
        name="A",
        hovertemplate=commodplottrace.hovertemplate_default,
        text=clean.index.strftime("%d-%b-%y"),
        visible=True,
        line=dict(width=None, color="red", dash=None),
        legendgroup="A",
        showlegend=None,
    )
    assert _normalise_plotly(actual) == _normalise_plotly(legacy)
    assert px_line.call_count == 1


def test_timeseries_trace_retains_empty_go_fallback(mocker):
    empty = pd.Series([], dtype=float, index=pd.DatetimeIndex([]), name="empty")
    px_line = mocker.spy(commodplottrace.px, "line")

    trace = commodplottrace.timeseries_trace(empty)

    assert isinstance(trace, go.Scatter)
    assert len(trace.x) == 0
    assert px_line.call_count == 0


def test_line_plot_preserves_history_forward_interleaving_and_styles():
    index = pd.date_range("2026-01-01", periods=10, freq="D")
    history = pd.DataFrame({"A": range(10), "B": range(10, 20)}, index=index)
    forward_index = pd.date_range("2026-02-01", periods=3, freq="MS")
    forward = pd.DataFrame({"A": [11, 12, 13], "B": [21, 22, 23]}, index=forward_index)

    figure = commodplot.line_plot(
        history, fwd=forward, visible_lines=["A"], title="Desk"
    )

    assert [trace.name for trace in figure.data] == ["A", "A", "B", "B"]
    assert [trace.legendgroup for trace in figure.data] == ["A", "A", "B", "B"]
    assert [trace.line.dash for trace in figure.data] == [None, "dash", None, "dash"]
    assert [trace.showlegend for trace in figure.data] == [None, False, None, False]
    assert [trace.visible for trace in figure.data] == [
        True,
        True,
        "legendonly",
        "legendonly",
    ]
    assert figure.data[0].line.color == figure.data[1].line.color
    assert figure.data[2].line.color == figure.data[3].line.color


def test_timeseries_scatter_uses_px_for_base_layer_and_keeps_custom_layers(mocker):
    index = pd.date_range("2026-01-01", periods=8, freq="D")
    frame = pd.DataFrame({"x": range(8), "y": [1, 2, 4, 3, 5, 7, 6, 8]}, index=index)
    px_scatter = mocker.spy(commodplot.px, "scatter")

    figure = commodplot.timeseries_scatter_plot(frame, line_last_n=3, fit_line=True)

    assert px_scatter.call_count == 1
    assert [trace.mode for trace in figure.data] == [
        "lines",
        "markers",
        "lines+markers",
    ]
    assert figure.data[0].name == "Line of Best Fit"
    assert figure.data[1].text[0] == "2026-01-01"
    assert "symbol" not in figure.data[1].marker.to_plotly_json()
    assert list(figure.data[2].x) == list(frame.iloc[-3:, 0])


def test_seasonal_facets_wide_order_trace_order_axes_and_shared_legend():
    history, forward = _seasonal_inputs()

    figure = commodplot.seas_line_facets(
        history,
        fwd=forward,
        facet_col_wrap=2,
        shaded_range=2,
        average_line=2,
        facet_titles={"A": "Alpha", "C": "Charlie"},
        yaxis_title="$/bbl",
    )

    assert [annotation.text for annotation in figure.layout.annotations] == [
        "Alpha",
        "B",
        "Charlie",
    ]
    for axis_name in ("xaxis", "xaxis2", "xaxis3"):
        axis = getattr(figure.layout, axis_name)
        assert axis.type == "date"
        assert pd.Timestamp(axis.tick0) == pd.Timestamp(dates.curyear, 1, 1)
        assert axis.dtick == "M1"
        assert axis.tickformat == "%b"
    for axis_name in ("yaxis", "yaxis2", "yaxis3"):
        assert getattr(figure.layout, axis_name).title.text == "$/bbl"

    first_panel = _traces_for_axis(figure, "x")
    assert first_panel[0].name.endswith("Max")
    assert first_panel[1].name.endswith("Min")
    assert first_panel[1].fill == "tonexty"
    assert first_panel[2].name.endswith("Avg")
    assert first_panel[-1].line.dash == "dot"
    assert all(trace.showlegend is True for trace in first_panel)
    assert all(
        trace.showlegend is False
        for trace in _traces_for_axis(figure, "x2") + _traces_for_axis(figure, "x3")
    )


def test_seasonal_facets_mapping_order_and_forward_key_matching():
    history, forward = _seasonal_inputs(("A", "B"))
    panels = OrderedDict([("second", history["B"]), ("first", history["A"])])
    forwards = {"first": forward["A"]}

    figure = commodplot.seas_line_facets(
        panels, fwd=forwards, facet_titles={"first": "First override"}
    )

    assert [annotation.text for annotation in figure.layout.annotations] == [
        "second",
        "First override",
    ]
    assert not any(trace.line.dash == "dot" for trace in _traces_for_axis(figure, "x"))
    assert any(trace.line.dash == "dot" for trace in _traces_for_axis(figure, "x2"))

    with pytest.raises(ValueError, match="unknown panel keys"):
        commodplot.seas_line_facets(panels, fwd={"extra": forward["A"]})


@pytest.mark.parametrize(
    ("legend_mode", "expected_first", "expected_second", "layout_showlegend"),
    [
        ("shared", True, False, True),
        ("each", True, True, True),
        ("none", False, False, False),
    ],
)
def test_seasonal_facet_legend_modes(
    legend_mode, expected_first, expected_second, layout_showlegend
):
    history, _ = _seasonal_inputs(("A", "B"))

    figure = commodplot.seas_line_facets(history, legend_mode=legend_mode)

    assert all(
        trace.showlegend is expected_first for trace in _traces_for_axis(figure, "x")
    )
    assert all(
        trace.showlegend is expected_second for trace in _traces_for_axis(figure, "x2")
    )
    assert figure.layout.showlegend is layout_showlegend


def test_seasonal_facets_honour_shared_axes():
    history, _ = _seasonal_inputs()

    figure = commodplot.seas_line_facets(
        history,
        facet_col_wrap=2,
        shared_xaxes=True,
        shared_yaxes=True,
    )

    assert figure.layout.xaxis.matches == "x3"
    assert figure.layout.yaxis2.matches == "y"


def test_reindex_facets_accept_mapping_and_sequence_in_order():
    panels = OrderedDict([("later", _reindex_frame(10)), ("earlier", _reindex_frame())])

    mapped = commodplot.reindex_year_line_facets(
        panels,
        shaded_range=2,
        facet_titles={"later": "Later panel"},
    )
    sequenced = commodplot.reindex_year_line_facets(
        list(panels.values()), facet_col_wrap=1
    )

    assert [annotation.text for annotation in mapped.layout.annotations] == [
        "Later panel",
        "earlier",
    ]
    assert [annotation.text for annotation in sequenced.layout.annotations] == [
        "0",
        "1",
    ]
    first_panel = _traces_for_axis(mapped, "x")
    assert first_panel[0].name.endswith("Max")
    assert first_panel[1].name.endswith("Min")
    assert first_panel[1].fill == "tonexty"
    assert mapped.layout.xaxis.type == "date"
    assert mapped.layout.xaxis2.tickformat == "%b-%y"


def _expected_reindex_range(frame, max_results=None):
    transformed = transforms.reindex_year(frame)
    if max_results is not None:
        transformed = transformed.tail(max_results)
    end = transformed.index[-1]
    start = max(transformed.index[0], end - pd.DateOffset(years=3))
    return [pd.Timestamp(start), pd.Timestamp(end)]


def test_reindex_facets_apply_panel_local_max_results_and_ranges():
    long_panel = _reindex_frame()
    short_panel = _reindex_frame(10).head(60)
    panels = OrderedDict([("long", long_panel), ("short", short_panel)])

    figure = commodplot.reindex_year_line_facets(
        panels,
        max_results=40,
        yaxis_title="$/bbl",
        shared_xaxes=False,
    )

    assert [pd.Timestamp(value) for value in figure.layout.xaxis.range] == (
        _expected_reindex_range(long_panel, max_results=40)
    )
    assert [pd.Timestamp(value) for value in figure.layout.xaxis2.range] == (
        _expected_reindex_range(short_panel, max_results=40)
    )
    assert figure.layout.xaxis.range != figure.layout.xaxis2.range
    assert figure.layout.yaxis.title.text == "$/bbl"
    assert figure.layout.yaxis2.title.text == "$/bbl"
    for axis_name in ("x", "x2"):
        panel_traces = _traces_for_axis(figure, axis_name)
        assert panel_traces
        assert all(len(trace.x) <= 40 for trace in panel_traces)


def test_reindex_facets_shared_axes_use_common_union_range():
    long_panel = _reindex_frame()
    short_panel = _reindex_frame(10).head(60)
    local_ranges = [
        _expected_reindex_range(long_panel),
        _expected_reindex_range(short_panel),
    ]
    expected_union = [
        min(panel_range[0] for panel_range in local_ranges),
        max(panel_range[1] for panel_range in local_ranges),
    ]

    figure = commodplot.reindex_year_line_facets(
        {"long": long_panel, "short": short_panel}, shared_xaxes=True
    )

    assert [
        pd.Timestamp(value) for value in figure.layout.xaxis.range
    ] == expected_union
    assert [
        pd.Timestamp(value) for value in figure.layout.xaxis2.range
    ] == expected_union


@pytest.mark.parametrize(
    ("call", "error", "message"),
    [
        (
            lambda: commodplot.seas_line_facets(pd.DataFrame()),
            ValueError,
            "at least one",
        ),
        (
            lambda: commodplot.seas_line_facets(
                pd.DataFrame({"A": [1, 2]}, index=[0, 1])
            ),
            TypeError,
            "DatetimeIndex",
        ),
        (
            lambda: commodplot.seas_line_facets(
                {
                    "A": pd.DataFrame(
                        {"x": [1], "y": [2]},
                        index=pd.date_range("2026-01-01", periods=1),
                    )
                }
            ),
            ValueError,
            "exactly one",
        ),
        (
            lambda: commodplot.seas_line_facets(
                _seasonal_inputs(("A",))[0], facet_col_wrap=0
            ),
            ValueError,
            "positive integer",
        ),
        (
            lambda: commodplot.seas_line_facets(
                _seasonal_inputs(("A",))[0], legend_mode="auto"
            ),
            ValueError,
            "legend_mode",
        ),
        (
            lambda: commodplot.reindex_year_line_facets([]),
            ValueError,
            "must not be empty",
        ),
        (
            lambda: commodplot.reindex_year_line_facets([pd.Series(dtype=float)]),
            TypeError,
            "DataFrame",
        ),
        (
            lambda: commodplot.reindex_year_line_facets(
                [_reindex_frame()], max_results=0
            ),
            ValueError,
            "max_results",
        ),
    ],
)
def test_facet_validation(call, error, message):
    with pytest.raises(error, match=message):
        call()


def test_reindex_facet_year_validation_has_panel_context():
    index = pd.date_range("2026-01-01", periods=3)
    duplicate_labels = pd.DataFrame([[1, 2], [3, 4], [5, 6]], index=index)
    duplicate_labels.columns = ["Q1 2025", "Q1 2025"]
    duplicate_years = pd.DataFrame(
        {"Q1 2025": [1, 2, 3], "Q2 2025": [4, 5, 6]}, index=index
    )
    unparseable = pd.DataFrame({"prompt": [1, 2, 3]}, index=index)

    with pytest.raises(ValueError, match="Panel 'labels'.*duplicate column"):
        commodplot.reindex_year_line_facets({"labels": duplicate_labels})
    with pytest.raises(ValueError, match="Panel 'years'.*duplicate reindex years"):
        commodplot.reindex_year_line_facets({"years": duplicate_years})
    with pytest.raises(ValueError, match="Panel 'parse'.*four-digit year"):
        commodplot.reindex_year_line_facets({"parse": unparseable})


def test_legacy_subplot_warnings_and_seasonal_average_omission():
    history, forward = _seasonal_inputs(("A",))

    with pytest.warns(FutureWarning, match="seas_line_facets") as seasonal_warning:
        seasonal = commodplot.seas_line_subplot(
            1,
            1,
            history,
            fwd=forward,
            average_line=2,
            subplot_titles=["Legacy"],
        )
    with pytest.warns(
        FutureWarning, match="reindex_year_line_facets"
    ) as reindex_warning:
        commodplot.reindex_year_line_subplot(1, 1, [_reindex_frame()])

    assert not any(trace.name.endswith("Avg") for trace in seasonal.data)
    assert seasonal_warning[0].filename == __file__
    assert reindex_warning[0].filename == __file__


def test_legacy_seasonal_subplot_ignores_yaxis_title():
    history, _ = _seasonal_inputs(("A", "B"))

    with pytest.warns(FutureWarning, match="seas_line_facets"):
        figure = commodplot.seas_line_subplot(
            1, 2, history, yaxis_title="ignored by the legacy adapter"
        )

    assert figure.layout.yaxis.title.text is None
    assert figure.layout.yaxis2.title.text is None


def test_legacy_reindex_subplot_ignores_max_results_ranges_and_titles_first_axis():
    frames = [_reindex_frame(), _reindex_frame(10)]

    with pytest.warns(FutureWarning, match="reindex_year_line_facets"):
        limited = commodplot.reindex_year_line_subplot(
            1,
            2,
            frames,
            max_results=5,
            yaxis_title="$/bbl",
        )
    with pytest.warns(FutureWarning, match="reindex_year_line_facets"):
        unlimited = commodplot.reindex_year_line_subplot(1, 2, frames)

    assert [list(trace.x) for trace in limited.data] == [
        list(trace.x) for trace in unlimited.data
    ]
    assert limited.layout.xaxis.range is None
    assert limited.layout.xaxis2.range is None
    assert limited.layout.yaxis.title.text == "$/bbl"
    assert limited.layout.yaxis2.title.text is None

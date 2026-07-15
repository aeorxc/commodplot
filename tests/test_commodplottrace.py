# python
import pandas as pd
import plotly.graph_objects as go
import pytest
from commodutil import dates, transforms
from commodplot import commodplottrace as cptr

def test_min_max_range(df_datetime):
    dft = transforms.seasonailse(df_datetime)
    res = cptr.min_max_mean_range(dft, shaded_range=5)
    assert isinstance(res[0], pd.DataFrame)
    assert isinstance(res[1], int)

def test_timeseries_trace(df_datetime):
    t = cptr.timeseries_trace(df_datetime['A'])
    assert isinstance(t, go.Scatter)
    assert t.name == "A"
    assert t.hovertemplate == cptr.hovertemplate_default

def test_timeseries_trace_by_year(df_datetime):
    df = transforms.seasonailse(df_datetime)
    colyear = df.columns[-1]
    t = cptr.timeseries_trace_by_year(df[colyear], colyear=colyear)
    assert isinstance(t, go.Scatter)
    assert t.name == str(colyear)
    assert t.visible == cptr.line_visible(colyear)
    assert t.line.color == cptr.get_year_line_col(colyear)


def test_timeseries_to_seas_trace_preserves_legacy_trace_contract():
    index = pd.date_range(f"{dates.curyear}-01-01", periods=3, freq="D")
    seas = pd.DataFrame(
        {
            dates.curyear - 1: [1.0, 2.0, 3.0],
            dates.curyear: [4.0, 5.0, 6.0],
        },
        index=index,
    )
    text = index.strftime("%d-%b")

    traces = cptr.timeseries_to_seas_trace(
        seas,
        text,
        showlegend=False,
        visible_line_years=1,
    )

    assert [trace.name for trace in traces] == [
        str(dates.curyear - 1),
        str(dates.curyear),
    ]
    for col, trace in zip(seas.columns, traces):
        trace_json = trace.to_plotly_json()
        assert isinstance(trace, go.Scatter)
        assert pd.DatetimeIndex(trace.x).equals(index)
        assert list(trace.y) == list(seas[col])
        assert list(trace.text) == list(text)
        assert trace.hoverinfo == "y"
        assert trace.hovertemplate == cptr.hovertemplate_default
        assert trace.legendgroup == str(col)
        assert trace.showlegend is False
        assert trace.visible == cptr.line_visible(col, visible_line_years=1)
        assert trace.line.color == cptr.get_year_line_col(col)
        assert trace.line.width == cptr.get_year_line_width(col)
        assert trace.line.dash is None

        # Plotly Express metadata must not leak into the legacy trace contract.
        for field in ("mode", "marker", "orientation", "xaxis", "yaxis"):
            assert field not in trace_json


def test_timeseries_to_seas_trace_preserves_requested_mode_and_dash():
    index = pd.date_range(f"{dates.curyear}-01-01", periods=3, freq="D")
    seas = pd.DataFrame({dates.curyear: [1.0, 2.0, 3.0]}, index=index)

    trace = cptr.timeseries_to_seas_trace(
        seas,
        index.strftime("%d-%b"),
        dash="dot",
        line_mode="lines+markers",
    )[0]

    assert trace.mode == "lines+markers"
    assert trace.line.dash == "dot"


def test_timeseries_to_seas_trace_ignores_falsy_line_mode():
    index = pd.date_range(f"{dates.curyear}-01-01", periods=3, freq="D")
    seas = pd.DataFrame({dates.curyear: [1.0, 2.0, 3.0]}, index=index)

    for line_mode in ("", False):
        trace = cptr.timeseries_to_seas_trace(
            seas,
            index.strftime("%d-%b"),
            line_mode=line_mode,
        )[0]
        assert trace.mode is None
        assert "mode" not in trace.to_plotly_json()


def test_timeseries_to_seas_trace_returns_empty_for_zero_columns():
    index = pd.date_range(f"{dates.curyear}-01-01", periods=3, freq="D")
    all_nan = pd.DataFrame(
        {dates.curyear: [float("nan")] * len(index)},
        index=index,
    )
    seas = all_nan.dropna(how="all", axis=1)

    assert seas.shape[1] == 0
    assert cptr.timeseries_to_seas_trace(seas, index.strftime("%d-%b")) == []


def test_seas_plot_traces_handles_all_nan_history():
    index = pd.date_range(f"{dates.curyear}-01-01", periods=3, freq="D")
    history = pd.Series(float("nan"), index=index, name="Price")

    traces = cptr.seas_plot_traces(history, histfreq="D")

    assert traces["hist"] == []


def test_timeseries_to_seas_trace_rejects_px_trace_count_mismatch(monkeypatch):
    index = pd.date_range(f"{dates.curyear}-01-01", periods=3, freq="D")
    seas = pd.DataFrame(
        {
            dates.curyear - 1: [1.0, 2.0, 3.0],
            dates.curyear: [4.0, 5.0, 6.0],
        },
        index=index,
    )
    monkeypatch.setattr(cptr.px, "line", lambda *args, **kwargs: go.Figure())

    with pytest.raises(RuntimeError, match="0 seasonal traces for 2 columns"):
        cptr.timeseries_to_seas_trace(seas, index.strftime("%d-%b"))

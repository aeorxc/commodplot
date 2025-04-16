# python
import os
import pandas as pd
import plotly.graph_objects as go

from commodutil import forwards
from commodutil.forward.util import convert_contract_to_date
from commodplot import commodplot

def test_seas_line_plot(cl_data):
    cl = cl_data.dropna(how="all", axis=1)
    fwd = pd.DataFrame(
        [50 for _ in range(12)],
        index=pd.date_range("2025-01-01", periods=12, freq="MS")
    )
    res = commodplot.seas_line_plot(
        cl[cl.columns[-1]],
        fwd=fwd,
        shaded_range=5,
        visible_line_years=3,
        average_line=5,
    )
    assert isinstance(res, go.Figure)

    shaded_range_max = [x for x in res.data if "Max" in x["name"]]
    assert len(shaded_range_max) == 1
    shaded_range_min = [x for x in res.data if "Min" in x["name"]]
    assert len(shaded_range_min) == 1

    solid_line = [x for x in res.data if x["name"] == "2024"]
    solid_line_dict = solid_line[0].to_plotly_json()
    assert solid_line_dict.get("hoverinfo") == "y"

    dot_line = [x for x in res.data if x["name"] == "2025"]
    dot_line_dict = dot_line[0].to_plotly_json()
    assert dot_line_dict.get("hoverinfo") == "y"


def test_seas_line_subplot():
    dr = pd.date_range(start="2015", end="2027-12-31", freq="B")
    data = {"A": [10 for _ in dr], "B": [20 for _ in dr], "C": [30 for _ in dr], "D": [10 for _ in dr]}
    df = pd.DataFrame(data, index=dr)
    dr = pd.date_range("2025-01-01", periods=12, freq="MS")
    data = {"A": [10 for _ in dr], "B": [20 for _ in dr], "C": [30 for _ in dr], "D": [10 for _ in dr]}
    fwd = pd.DataFrame(data, index=dr)

    res = commodplot.seas_line_subplot(
        2, 2, df, fwd=fwd, subplot_titles=["1", "2", "3", "4"], shaded_range=5
    )
    assert isinstance(res, go.Figure)
    assert [x.name for x in res.data].count("2020") == 4


def test_reindex_year_line_plot(cl_data):
    cl = cl_data.dropna(how="all", axis=1)
    cl = cl.rename(
        columns={x: pd.to_datetime(convert_contract_to_date(x)) for x in cl.columns}
    )
    sp = forwards.time_spreads(cl, 12, 12)
    res = commodplot.reindex_year_line_plot(sp, max_results=360, visible_line_years=7)
    assert isinstance(res, go.Figure)


def test_fwd_hist_plot():
    dirname = os.path.dirname(os.path.abspath(__file__))
    cl = pd.read_csv(
        os.path.join(dirname, "test_cl_fwd.csv"),
        index_col=0,
        parse_dates=True,
        dayfirst=True,
    )
    res = commodplot.forward_history_plot(cl)
    assert isinstance(res, go.Figure)


def test_candle_chart():
    dirname = os.path.dirname(os.path.abspath(__file__))
    cl = pd.read_csv(
        os.path.join(dirname, "test_cl_chlo.csv"),
        index_col=0,
        parse_dates=True,
        dayfirst=True,
    )
    res = commodplot.candle_chart(cl)
    assert isinstance(res, go.Figure)


def test_stack_area_chart():
    dirname = os.path.dirname(os.path.abspath(__file__))
    cl = pd.read_csv(
        os.path.join(dirname, "test_cl_chlo.csv"),
        index_col=0,
        parse_dates=True,
        dayfirst=True,
    )
    res = commodplot.stacked_area_chart(cl)
    assert isinstance(res, go.Figure)


def test_stack_area_chart_negative_cols():
    dirname = os.path.dirname(os.path.abspath(__file__))
    cl = pd.read_csv(
        os.path.join(dirname, "test_cl_chlo.csv"),
        index_col=0,
        parse_dates=True,
        dayfirst=True,
    )
    res = commodplot.stacked_area_chart_negative_cols(cl)
    assert isinstance(res, go.Figure)


def test_stack_bar_chart(cl_data):
    cl = cl_data.dropna(how="all", axis=1)
    res = commodplot.bar_chart(cl, barmode="stack")
    assert isinstance(res, go.Figure)


def test_reindex_year_line_subplot():
    dr = pd.date_range(start="2015", end="2020-12-31", freq="B")
    data = {"Q1 2019": [10 for _ in dr], 2020: [20 for _ in dr], 2021: [30 for _ in dr], 2022: [10 for _ in dr]}
    df = pd.DataFrame(data, index=dr)
    dfs = [df for _ in range(4)]
    res = commodplot.reindex_year_line_subplot(
        2, 2, dfs, subplot_titles=["1", "2", "3", "4"]
    )
    assert isinstance(res, go.Figure)


def test_seas_box_plot(cl_data):
    cl = cl_data.dropna(how="all", axis=1)
    fwd = cl[cl.columns[-1]].resample("MS").mean()
    res = commodplot.seas_box_plot(cl[cl.columns[-1]], fwd)
    assert isinstance(res, go.Figure)


def test_table_plot(cl_data):
    cl = cl_data.dropna(how="all", axis=1)
    res = commodplot.table_plot(cl, formatted_cols=["CL_2020F"])
    assert isinstance(res, go.Figure)


def test_seas_table(cl_data):
    cl = cl_data.dropna(how="all", axis=1)
    fwd = cl[cl.columns[-1]].resample("MS").mean()
    res = commodplot.seas_table_plot(cl[cl.columns[-1]], fwd)
    assert isinstance(res, go.Figure)


def test_diff_plot(cl_data):
    cl = cl_data.dropna(how="all", axis=1)[["CL_2020F", "CL_2020G"]]
    res = commodplot.diff_plot(cl, title="Test")
    assert isinstance(res, go.Figure)


def test_line_plot(cl_data):
    cl = cl_data.dropna(how="all", axis=1)[["CL_2019F", "CL_2020G"]]
    fwd = pd.DataFrame(
        [[50 for _ in range(2)]],
        index=pd.date_range("2021-01-01", periods=12, freq="MS"),
        columns=["CL_2019F", "CL_2020G"],
    )
    res = commodplot.line_plot(cl, fwd=fwd, title="Test")
    assert isinstance(res, go.Figure)


def test_line_plot2(cl_data):
    cl = cl_data.dropna(how="all", axis=1)[["CL_2020F", "CL_2020G"]]
    cl = cl.rename(columns={"CL_2020F": "A", "CL_2020G": "B"})
    fwd = pd.DataFrame(
        [[50 for _ in range(2)]],
        index=pd.date_range("2021-01-01", periods=12, freq="MS"),
        columns=["A", "B"],
    )
    res = commodplot.line_plot(cl, fwd=fwd, title="Test")
    assert isinstance(res, go.Figure)


def test_stacked_grouped_bar_chart():
    level1 = ["A", "A", "B", "B"]
    level2 = ["X", "Y", "X", "Y"]
    multi_index = pd.MultiIndex.from_arrays([level1, level2])
    df = pd.DataFrame(
        data={"col1": [1, 2, 3, 4], "col2": [5, 6, 7, 8]}, index=multi_index
    ).T
    res = commodplot.stacked_grouped_bar_chart(df)
    assert isinstance(res, go.Figure)


def test_bar_line_plot(cl_data):
    cl = cl_data.dropna(how="all", axis=1)[["CL_2020F", "CL_2020G"]]
    cl = cl.rename(columns={"CL_2020F": "A", "CL_2020G": "B"})
    res = commodplot.bar_line_plot(cl, title="Test")
    assert isinstance(res, go.Figure)


def test_horizontal_bar_plot(cl_data):
    res = commodplot.horizontal_bar_plot(cl_data, title="Test")
    assert isinstance(res, go.Figure)


def test_timeseries_scatter_plot(cl_data):
    cl = cl_data.dropna(how="all", axis=1)
    cl = cl[cl.columns[:2]].dropna()
    res = commodplot.timeseries_scatter_plot(cl, line_last_n=12, fit_line=True)
    assert isinstance(res, go.Figure)
# python
import pandas as pd
import plotly.graph_objects as go
from commodutil import transforms
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
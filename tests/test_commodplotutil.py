# python
import pandas as pd
from commodplot import commodplotutil as cpu

def test_delta_summary_str():
    df = pd.DataFrame({'value': [1.0, 2.0]})
    m1 = df.iloc[-1, 0]
    m2 = df.iloc[-2, 0]
    diff = m1 - m2
    res = cpu.delta_summary_str(df)
    assert str(round(m1, 2)) in res
    assert str(round(diff, 2)) in res

def test_gen_title_without_title():
    df = pd.DataFrame([1, 2, 3], columns=["Test"])
    res = cpu.gen_title(df, title=None)
    assert res.startswith("3")

def test_gen_title_with_title():
    df = pd.DataFrame([1, 2, 3], columns=["Test"])
    res = cpu.gen_title(df, title="TTitle")
    assert res.startswith("TTitle")
    assert res.endswith("+1")

def test_gen_title_with_title_and_postfix():
    df = pd.DataFrame([1, 2, 3], columns=["Test"])
    res = cpu.gen_title(df, title="TTitle", title_postfix="post")
    assert res.startswith("TTitle  post:")
    assert res.endswith("+1")
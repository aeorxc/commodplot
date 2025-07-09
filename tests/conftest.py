# python
import os
import pandas as pd
import pytest

@pytest.fixture(scope="module")
def cl_data():
    dirname = os.path.dirname(os.path.abspath(__file__))
    cl = pd.read_csv(
        os.path.join(dirname, "test_cl.csv"),
        index_col=0,
        parse_dates=True,
        dayfirst=True,
        date_format='%Y-%m-%d'
    )
    return cl



@pytest.fixture
def df_datetime():
    return pd.DataFrame(
        {'A': range(1, 5001)},
        index=pd.date_range(start="2020-01-01", periods=5000, freq="D")
    )
import pandas as pd
from commodutil import transforms


def seasonalise(df, histfreq):
    """
    Given a dataframe, seasonalise the data, returning seasonalised dataframe
    :param df:
    :return:
    """
    # Backwards compatible wrapper: core seasonalization lives in commodutil.transforms.
    return transforms.seasonalize(df, histfreq=histfreq)

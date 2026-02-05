import pandas as pd
from commodutil import transforms


def seasonalise(df, histfreq):
    """
    Given a dataframe, seasonalise the data, returning seasonalised dataframe
    :param df:
    :return:
    """
    # Prefer core seasonalization in commodutil (newer versions).
    if hasattr(transforms, "seasonalize"):
        return transforms.seasonalize(df, histfreq=histfreq)

    # Backwards compatibility for older commodutil versions.
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)

    if histfreq is None:
        histfreq = pd.infer_freq(df.index)
        if histfreq is None:
            histfreq = "D"  # sometimes infer_freq returns null - assume mostly will be a daily series

    if histfreq.startswith("W"):
        seas = transforms.seasonalise_weekly(df)
    else:
        seas = transforms.seasonailse(df)

    seas = seas.dropna(how="all", axis=1)  # dont plot empty years
    return seas

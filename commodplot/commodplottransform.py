from commodutil import transforms


def seasonalise(df, histfreq):
    """
    Given a dataframe, seasonalise the data, returning seasonalised dataframe
    :param df:
    :return:
    """
    return transforms.seasonalize(df, histfreq=histfreq)

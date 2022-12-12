import pandas as pd
import typing as t

table_style = [
    dict(selector="tr:hover", props=[("background", "#D6EEEE")]),
    dict(
        selector="th.col_heading",
        props=[
            ("color", "#fff"),
            ("border", "1px solid #eee"),
            ("padding", "12px 35px"),
            ("border-collapse", "collapse"),
            ("background", "#1D4477"),
            ("font-size", "18px"),
        ],
    ),
    dict(
        selector="th.row_heading",
        props=[
            ("border", "1px solid #eee"),
            ("padding", "12px 35px"),
            ("border-collapse", "collapse"),
            ("font-size", "12px"),
            ("text-align", "left"),
        ],
    ),
    dict(
        selector="td",
        props=[
            ("border", "1px solid #eee"),
            ("padding", "10px 20px"),
            ("border-collapse", "collapse"),
            ("font-size", "15px"),
        ],
    ),
    dict(
        selector="table",
        props=[
            ("font-family", "Helvetica"),
            ("margin", "25px auto"),
            ("border-collapse", "collapse"),
            ("border", "1px solid #eee"),
            ("border-bottom", "2px solid #00cccc"),
        ],
    ),
    dict(selector="caption", props=[("caption-side", "bottom")]),
    dict(
        selector="tr:nth-child(even)",
        props=[
            ("background-color", "#f2f2f2"),
        ],
    ),
]


def color_accounting(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, green otherwise.
    """
    if isinstance(val, (float, int)):
        color = "red" if val < 0 else "green"
    else:
        color = "red" if float(val.replace(",", "")) < 0 else "green"
    return "color: %s" % color


def generate_table(
    df: pd.DataFrame,
    precision: t.Tuple[int, dict] = None,
    accounting_col_columns: list = None,
):

    if precision:
        if isinstance(precision, int):
            format_var = "{:.%sf}" % precision
            df = df.applymap(lambda x: format_var.format(x))
        elif isinstance(precision, dict):
            for col, col_precision in precision.items():
                format_var = "{:,.%sf}" % col_precision
                df[col] = df[col].map(format_var.format)

    if accounting_col_columns:
        res = df.style.applymap(
            color_accounting, subset=accounting_col_columns
        ).set_table_styles(table_style)
    else:
        res = df.style.set_table_styles(table_style)

    return res.to_html()

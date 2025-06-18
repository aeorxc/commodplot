# python
import os
import plotly.express as px
import plotly.graph_objects as go
from commodplot import jinjautils

def test_convert_dict_plotly_fig_html_div():
    df = px.data.gapminder().query("country=='Canada'")
    fig = px.line(df, x="year", y="lifeExp", title="Life expectancy in Canada")
    data = {
        "ch1": fig,
        "el": 1,
        "innerd": {"ch2": fig},
    }
    res = jinjautils.convert_dict_plotly_fig_html_div(data)
    assert isinstance(res["ch1"], str)
    assert isinstance(res["innerd"]["ch2"], str)

def test_render_html_to_file(tmp_path):
    test_out_loc = tmp_path / "test.html"
    if test_out_loc.exists():
        test_out_loc.unlink()

    import plotly.graph_objects as go
    fig = go.Figure(
        data=[go.Bar(x=[1, 2, 3], y=[1, 3, 2])],
        layout=go.Layout(
            title=go.layout.Title(text="A Figure Specified By A Graph Object")
        ),
    )
    data = {"name": "test", "fig1": fig}

    jinjautils.render_html(
        data,
        template="test_report.html",
        filename=str(test_out_loc),
        package_loader_name="commodplot",
    )

    assert test_out_loc.exists()
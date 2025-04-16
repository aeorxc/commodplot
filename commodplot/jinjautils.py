import base64
import logging
import os
from datetime import datetime

import plotly as pl
from jinja2 import PackageLoader, FileSystemLoader, Environment
from plotly import graph_objects as go

# margin to use in HTML charts - make charts bigger but leave space for title
narrow_margin = {"l": 2, "r": 2, "t": 30, "b": 10}


def convert_dict_plotly_fig_png(d):
    """
    Given a dict (that might be passed to jinja), convert all plotly figures png
    """
    for k, v in d.items():
        if isinstance(d[k], go.Figure):
            d[k] = plpng(d[k])
        if isinstance(d[k], dict):
            convert_dict_plotly_fig_png(d[k])
        if isinstance(d[k], list):
            for count, item in enumerate(d[k]):
                if isinstance(item, go.Figure):
                    d[k][count] = plpng(item)

    return d


def plpng(fig):
    """
    Given a plotly figure, return it as a png embedded in an img tag.
    Uses Plotly's export function with the Kaleido engine.
    """
    image = fig.to_image(format="png", engine="kaleido")
    # The output is already bytes, so encode to base64 only if necessary.
    # Here we use Plotly's built-in conversion to image.
    import base64
    image_b64 = base64.b64encode(image).decode("ascii")
    return f'<img src="data:image/png;base64,{image_b64}">'


def convert_dict_plotly_fig_html_div(d, interactive=True):
    """
    Given a dict (that might be passed to jinja), convert all plotly figures to html divs
    or png images depending on the interactive flag.
    """
    for k, v in d.items():
        if isinstance(d[k], go.Figure):
            d[k] = plhtml(d[k], interactive=interactive)
        if isinstance(d[k], dict):
            convert_dict_plotly_fig_html_div(d[k], interactive=interactive)
        if isinstance(d[k], list):
            for count, item in enumerate(d[k]):
                if isinstance(item, go.Figure):
                    d[k][count] = plhtml(item, interactive=interactive)
                    d[k][count] = plhtml(item, interactive=interactive)
    return d


def plhtml(fig, interactive=True, margin=narrow_margin, **kwargs):
    """
    Given a plotly figure, return it as a div if interactive is True,
    or as a static png image if interactive is False.
    """
    if fig is None:
        return ""
    fig.update_layout(margin=margin)
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    if interactive:
        return pl.offline.plot(fig, include_plotlyjs=False, output_type="div")
    else:
        # Render as a static image
        return plpng(fig)


def render_html(
    data,
    template,
    package_loader_name=None,
    template_globals=None,
    plotly_image_conv_func=convert_dict_plotly_fig_html_div,
    filename: str = None,
):
    """
    Using a Jinja2 template, render html file and return as string
    :param data: dict of jinja parameters to include in rendered html
    :param template: absolute location of template file
    :param package_loader_name: if using PackageLoader instead of FileLoader specify package name
    :return:
    """
    data = plotly_image_conv_func(data)

    tdirname, tfilename = os.path.split(os.path.abspath(template))
    if package_loader_name:
        loader = PackageLoader(package_loader_name, "templates")
    else:
        loader = FileSystemLoader(tdirname)
    env = Environment(loader=loader)
    env.finalize = jinja_finalize
    template = env.get_template(tfilename)
    if template_globals:
        for template_global in template_globals:
            template.globals[template_global] = template_globals[template_global]

    output = template.render(
        pagetitle=data["name"], last_gen_time=datetime.now(), data=data
    )

    if filename:
        render_html_to_file(filename, output)

    return output


def render_html_to_file(filename: str, output: str):
    """
    Using a Jinja2 template, render a html file and save to disk
    :param data: dict of jinja parameters to include in rendered html
    :param template: absolute location of template file
    :param filename: location of where rendered html file should be output
    :param package_loader_name: if using PackageLoader instead of FileLoader specify package name
    :return:
    """
    logging.info("Writing html to {}".format(filename))

    with open(filename, "w", encoding="utf8") as fh:
        fh.write(output)

    return filename


def jinja_finalize(value):
    """
    Finalize for jinja which makes empty entries show as blank rather than none
    and converts plotly charts to html divs
    :param value:
    :return:
    """
    if value is None:
        return ""
    if isinstance(value, go.Figure):
        return plhtml(value)
    return value

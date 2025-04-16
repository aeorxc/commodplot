# python
import os
import pytest
import plotly.graph_objects as go
from unittest.mock import patch

from commodplot import messaging

def create_figure():
    fig = go.Figure(
        data=[go.Bar(x=[1, 2, 3], y=[1, 3, 2])],
        layout=go.Layout(
            title=go.layout.Title(text="A Figure Specified By A Graph Object")
        ),
    )
    return fig

@pytest.mark.skip()
@patch("commodplot.messaging.SMTP")
def test_compose_and_send_report(mock_smtp):
    sender = "testcommodplot@mailinator.com"
    receiver = sender
    os.environ["SMTP_HOST"] = "smtp.example.com"
    os.environ["SMTP_PORT"] = "587"
    os.environ["SMTP_TIMEOUT"] = "60"
    os.environ["SENDER_EMAIL"] = sender
    os.environ["RECEIVER_EMAIL"] = receiver

    instance = mock_smtp.return_value.__enter__.return_value
    fig = create_figure()
    subject = "test_email"
    content = (
        "<html>"
        "<body>"
        "<h1 style=\"text-align: center;\">Simple Data Report</h1>"
        "<p>Here could be a short description of the data.</p>"
        "<p><img src=\"cid:0\"></p>"
        "</body>"
        "</html>"
    )
    img = fig.to_image(width=1200, height=350)
    images = {"0": img}

    messaging.compose_and_send_report(
        subject=subject,
        content=content,
        images=images,
        sender_email=sender,
        receiver_email=receiver,
    )

    instance.sendmail.assert_called_once()
    sendmail_args = instance.sendmail.call_args[0]
    assert sendmail_args[0] == sender
    assert sendmail_args[1] == receiver
    assert subject in sendmail_args[2]

@pytest.mark.skip()
@patch("commodplot.messaging.SMTP")
def test_compose_jinja_report(mock_smtp):
    sender = "testcommodplot@mailinator.com"
    receiver = sender
    os.environ["SMTP_HOST"] = "smtp.example.com"
    os.environ["SMTP_PORT"] = "587"
    os.environ["SMTP_TIMEOUT"] = "60"
    os.environ["SENDER_EMAIL"] = sender
    os.environ["RECEIVER_EMAIL"] = receiver

    instance = mock_smtp.return_value.__enter__.return_value
    fig = create_figure()
    data = {"name": "test", "fig1": fig}
    subject = "test_email"

    messaging.compose_and_send_jinja_report(
        subject=subject,
        data=data,
        template="test_report.html",
        package_loader_name="commodplot",
        sender_email=sender,
        receiver_email=receiver,
    )

    instance.sendmail.assert_called_once()
    sendmail_args = instance.sendmail.call_args[0]
    assert sendmail_args[0] == sender
    assert sendmail_args[1] == receiver
    assert subject in sendmail_args[2]
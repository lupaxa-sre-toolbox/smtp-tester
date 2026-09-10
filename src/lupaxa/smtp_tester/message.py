"""Build the MIME test message."""

from __future__ import annotations

from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid

DEFAULT_SUBJECT = "Simple test message"
DEFAULT_BODY = "This is the body of the message."


def build_test_message(
    from_address: str,
    to_address: str,
    *,
    subject: str = DEFAULT_SUBJECT,
    body: str = DEFAULT_BODY,
) -> EmailMessage:
    """Assemble a plain-text test message.

    Parameters
    ----------
    from_address
        Envelope and header From address.
    to_address
        Envelope and header To address.
    subject
        Message subject.
    body
        Plain-text body.

    Returns
    -------
    EmailMessage
        Ready-to-send MIME message with Date and Message-ID.
    """
    message = EmailMessage()
    message["From"] = formataddr(("", from_address))
    message["To"] = formataddr(("", to_address))
    message["Subject"] = subject
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid()
    message.set_content(body)
    return message

"""SMTP send path for a single test message."""

from __future__ import annotations

import logging
import math
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage

from .message import DEFAULT_BODY, DEFAULT_SUBJECT, build_test_message

DEFAULT_PORT = 25
DEFAULT_TIMEOUT = 10.0
LOGGER = logging.getLogger(__name__)


class _StarttlsRequired(Exception):
    """STARTTLS was required but the server did not advertise it."""


@dataclass(frozen=True)
class SmtpTestResult:
    """Outcome of one SMTP test send."""

    ok: bool
    to_address: str
    detail: str
    smtp_code: int | None = None


def send_test_message(
    host: str,
    port: int,
    username: str | None,
    password: str | None,
    from_address: str,
    to_address: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    use_tls: bool = False,
    starttls: bool = True,
    subject: str = DEFAULT_SUBJECT,
    body: str = DEFAULT_BODY,
    debug: bool = False,
) -> SmtpTestResult:
    """Connect, optionally authenticate, and send one test message.

    Parameters
    ----------
    host
        SMTP hostname.
    port
        SMTP port (``1``–``65535``).
    username
        AUTH username, or ``None`` / empty to skip login.
    password
        AUTH password, or ``None`` / empty to skip login. Never logged.
    from_address
        Envelope MAIL FROM and header From.
    to_address
        Envelope RCPT TO and header To.
    timeout
        Socket timeout in seconds. Must be greater than ``0``.
    use_tls
        Use implicit TLS (``SMTP_SSL``), typically port 465.
    starttls
        Require STARTTLS before AUTH or DATA. Fail if the server does
        not advertise it. Ignored when ``use_tls`` is true.
    subject
        Message subject.
    body
        Plain-text body.
    debug
        Log SMTP steps (connect, EHLO, STARTTLS, AUTH, send) without
        protocol payloads.

    Returns
    -------
    SmtpTestResult
        Success or a credential-safe failure reason.

    Raises
    ------
    ValueError
        If ``port`` or ``timeout`` is invalid, or only one of
        username/password is set.
    """
    _validate_port(port)
    _validate_timeout(timeout)
    user, secret = _auth_pair(username, password)
    message = build_test_message(
        from_address,
        to_address,
        subject=subject,
        body=body,
    )
    try:
        _trace(debug, "connecting to %s:%s", host, port)
        server = _connect(host, port, timeout, use_tls)
        try:
            _deliver(
                server,
                user,
                secret,
                message,
                starttls=starttls and not use_tls,
                debug=debug,
            )
        finally:
            _close(server)
    except _StarttlsRequired:
        return SmtpTestResult(
            False,
            to_address,
            "STARTTLS is required but the server did not advertise it",
        )
    except smtplib.SMTPAuthenticationError as exc:
        return _failure(to_address, f"authentication failed: {_smtp_text(exc)}", exc)
    except smtplib.SMTPRecipientsRefused as exc:
        return SmtpTestResult(
            False,
            to_address,
            "all recipient addresses refused",
            smtp_code=_refused_code(exc),
        )
    except smtplib.SMTPSenderRefused as exc:
        return _failure(to_address, f"sender refused: {_smtp_text(exc)}", exc)
    except smtplib.SMTPDataError as exc:
        return _failure(to_address, f"server refused message data: {_smtp_text(exc)}", exc)
    except smtplib.SMTPConnectError as exc:
        return _failure(to_address, f"connection failed: {_smtp_text(exc)}", exc)
    except smtplib.SMTPHeloError as exc:
        return _failure(to_address, f"HELO refused: {_smtp_text(exc)}", exc)
    except smtplib.SMTPServerDisconnected:
        return SmtpTestResult(False, to_address, "server unexpectedly disconnected")
    except smtplib.SMTPResponseException as exc:
        return _failure(to_address, _smtp_text(exc), exc)
    except smtplib.SMTPException as exc:
        return SmtpTestResult(False, to_address, str(exc) or exc.__class__.__name__)
    except ssl.SSLError as exc:
        return SmtpTestResult(False, to_address, f"TLS handshake failed: {exc}")
    except TimeoutError:
        return SmtpTestResult(False, to_address, "connection timed out")
    except OSError as exc:
        return SmtpTestResult(False, to_address, f"socket error: {exc}")
    return SmtpTestResult(True, to_address, f"email sent to {to_address}")


def _validate_port(port: int) -> None:
    if port < 1 or port > 65535:
        raise ValueError("port must be between 1 and 65535")


def _validate_timeout(timeout: float) -> None:
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be greater than 0")


def _optional_text(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    return value


def _auth_pair(username: str | None, password: str | None) -> tuple[str | None, str | None]:
    user = _optional_text(username)
    secret = _optional_text(password)
    if (user is None) ^ (secret is None):
        raise ValueError("username and password must both be set, or both omitted")
    return user, secret


def _connect(host: str, port: int, timeout: float, use_tls: bool) -> smtplib.SMTP:
    if use_tls:
        return smtplib.SMTP_SSL(host=host, port=port, timeout=timeout)
    return smtplib.SMTP(host=host, port=port, timeout=timeout)


def _deliver(
    server: smtplib.SMTP,
    username: str | None,
    password: str | None,
    message: EmailMessage,
    *,
    starttls: bool,
    debug: bool,
) -> None:
    _trace(debug, "EHLO")
    server.ehlo()
    if starttls:
        if not server.has_extn("STARTTLS"):
            raise _StarttlsRequired
        _trace(debug, "STARTTLS")
        server.starttls()
        server.ehlo()
    if username is not None and password is not None:
        _trace(debug, "AUTH user=%s", username)
        server.login(username, password)
    else:
        _trace(debug, "AUTH skipped")
    _trace(debug, "sending message")
    server.send_message(message)


def _trace(debug: bool, message: str, *args: object) -> None:
    if debug:
        LOGGER.debug(message, *args)


def _close(server: smtplib.SMTP) -> None:
    try:
        server.quit()
    except smtplib.SMTPException:
        server.close()


def _failure(
    to_address: str,
    detail: str,
    exc: smtplib.SMTPResponseException,
) -> SmtpTestResult:
    return SmtpTestResult(False, to_address, detail, smtp_code=exc.smtp_code)


def _refused_code(exc: smtplib.SMTPRecipientsRefused) -> int | None:
    for item in exc.recipients.values():
        if item:
            return int(item[0])
    return None


def _smtp_text(exc: smtplib.SMTPResponseException) -> str:
    error = exc.smtp_error
    if isinstance(error, bytes):
        return error.decode("utf-8", errors="replace")
    return str(error)

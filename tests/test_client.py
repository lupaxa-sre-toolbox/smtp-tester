"""SMTP client send path."""

from __future__ import annotations

import smtplib
import ssl
from unittest.mock import MagicMock, patch

import pytest

from lupaxa.smtp_tester.client import send_test_message


def _server(*, starttls: bool = True) -> MagicMock:
    server = MagicMock()
    server.has_extn.return_value = starttls
    return server


def test_send_success_uses_starttls_and_login() -> None:
    server = _server()
    with patch("lupaxa.smtp_tester.client.smtplib.SMTP", return_value=server):
        result = send_test_message(
            "smtp.example.com",
            587,
            "user",
            "secret",
            "from@example.com",
            "to@example.com",
        )
    assert result.ok is True
    assert result.to_address == "to@example.com"
    assert result.smtp_code is None
    assert "to@example.com" in result.detail
    server.ehlo.assert_called()
    server.starttls.assert_called_once()
    server.login.assert_called_once_with("user", "secret")
    server.send_message.assert_called_once()
    server.sendmail.assert_not_called()
    server.quit.assert_called_once()


def test_send_skips_starttls_when_disabled() -> None:
    server = _server()
    with patch("lupaxa.smtp_tester.client.smtplib.SMTP", return_value=server):
        result = send_test_message(
            "smtp.example.com",
            25,
            "user",
            "secret",
            "from@example.com",
            "to@example.com",
            starttls=False,
        )
    assert result.ok is True
    server.starttls.assert_not_called()


def test_fails_when_starttls_required_but_not_advertised() -> None:
    server = _server(starttls=False)
    with patch("lupaxa.smtp_tester.client.smtplib.SMTP", return_value=server):
        result = send_test_message(
            "smtp.example.com",
            587,
            "user",
            "secret",
            "from@example.com",
            "to@example.com",
        )
    assert result.ok is False
    assert "STARTTLS" in result.detail
    assert result.smtp_code is None
    server.login.assert_not_called()
    server.send_message.assert_not_called()


def test_send_implicit_tls_uses_smtp_ssl() -> None:
    server = _server()
    with (
        patch("lupaxa.smtp_tester.client.smtplib.SMTP_SSL", return_value=server) as ssl_ctor,
        patch("lupaxa.smtp_tester.client.smtplib.SMTP") as plain,
    ):
        result = send_test_message(
            "smtp.example.com",
            465,
            "user",
            "secret",
            "from@example.com",
            "to@example.com",
            use_tls=True,
        )
    assert result.ok is True
    ssl_ctor.assert_called_once()
    plain.assert_not_called()
    server.starttls.assert_not_called()


def test_authentication_failure_includes_smtp_code() -> None:
    server = _server()
    server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"bad credentials")
    with patch("lupaxa.smtp_tester.client.smtplib.SMTP", return_value=server):
        result = send_test_message(
            "smtp.example.com",
            587,
            "user",
            "secret",
            "from@example.com",
            "to@example.com",
        )
    assert result.ok is False
    assert result.smtp_code == 535
    assert "authentication failed" in result.detail
    assert "secret" not in result.detail


def test_recipients_refused_includes_smtp_code() -> None:
    server = _server()
    server.send_message.side_effect = smtplib.SMTPRecipientsRefused(
        {"to@example.com": (550, b"no")},
    )
    with patch("lupaxa.smtp_tester.client.smtplib.SMTP", return_value=server):
        result = send_test_message(
            "smtp.example.com",
            25,
            "user",
            "secret",
            "from@example.com",
            "to@example.com",
            starttls=False,
        )
    assert result.ok is False
    assert result.detail == "all recipient addresses refused"
    assert result.smtp_code == 550


def test_smtp_not_supported() -> None:
    server = _server()
    server.login.side_effect = smtplib.SMTPNotSupportedError("SMTP AUTH extension not supported")
    with patch("lupaxa.smtp_tester.client.smtplib.SMTP", return_value=server):
        result = send_test_message(
            "smtp.example.com",
            587,
            "user",
            "secret",
            "from@example.com",
            "to@example.com",
        )
    assert result.ok is False
    assert "not supported" in result.detail.lower() or "AUTH" in result.detail


def test_tls_handshake_failure() -> None:
    with patch(
        "lupaxa.smtp_tester.client.smtplib.SMTP_SSL",
        side_effect=ssl.SSLError("certificate verify failed"),
    ):
        result = send_test_message(
            "smtp.example.com",
            465,
            "user",
            "secret",
            "from@example.com",
            "to@example.com",
            use_tls=True,
        )
    assert result.ok is False
    assert "TLS" in result.detail
    assert "secret" not in result.detail


def test_socket_error() -> None:
    with patch(
        "lupaxa.smtp_tester.client.smtplib.SMTP",
        side_effect=OSError("connection refused"),
    ):
        result = send_test_message(
            "smtp.example.com",
            25,
            "user",
            "secret",
            "from@example.com",
            "to@example.com",
            starttls=False,
        )
    assert result.ok is False
    assert "socket error" in result.detail


def test_timeout() -> None:
    with patch("lupaxa.smtp_tester.client.smtplib.SMTP", side_effect=TimeoutError):
        result = send_test_message(
            "smtp.example.com",
            25,
            "user",
            "secret",
            "from@example.com",
            "to@example.com",
            starttls=False,
        )
    assert result.ok is False
    assert result.detail == "connection timed out"


def test_skips_login_when_auth_omitted() -> None:
    server = _server()
    with patch("lupaxa.smtp_tester.client.smtplib.SMTP", return_value=server):
        result = send_test_message(
            "smtp.example.com",
            25,
            None,
            None,
            "from@example.com",
            "to@example.com",
            starttls=False,
        )
    assert result.ok is True
    server.login.assert_not_called()
    server.send_message.assert_called_once()


def test_rejects_username_without_password() -> None:
    with pytest.raises(ValueError, match="both"):
        send_test_message(
            "smtp.example.com",
            25,
            "user",
            None,
            "from@example.com",
            "to@example.com",
        )


def test_rejects_out_of_range_port() -> None:
    with pytest.raises(ValueError, match="port"):
        send_test_message(
            "smtp.example.com",
            0,
            "user",
            "secret",
            "from@example.com",
            "to@example.com",
        )


def test_rejects_non_positive_timeout() -> None:
    with pytest.raises(ValueError, match="timeout"):
        send_test_message(
            "smtp.example.com",
            25,
            "user",
            "secret",
            "from@example.com",
            "to@example.com",
            timeout=0,
        )


def test_verbose_does_not_enable_smtplib_debug() -> None:
    server = _server()
    with patch("lupaxa.smtp_tester.client.smtplib.SMTP", return_value=server):
        send_test_message(
            "smtp.example.com",
            587,
            "user",
            "secret",
            "from@example.com",
            "to@example.com",
            debug=True,
        )
    server.set_debuglevel.assert_not_called()

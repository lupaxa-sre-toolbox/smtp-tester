"""CLI entrypoint."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from lupaxa.smtp_tester.cli import build_parser, main, resolve_auth
from lupaxa.smtp_tester.client import SmtpTestResult
from lupaxa.smtp_tester.version import get_version

_CONNECT = [
    "--from-address",
    "from@example.com",
    "--to-address",
    "to@example.com",
    "--smtp-server",
    "smtp.example.com",
]
_BASE = [
    *_CONNECT,
    "--smtp-username",
    "user",
]


def test_help_exits_zero() -> None:
    assert main(["--help"]) == 0


def test_version_flag(capsys) -> None:
    assert main(["--version"]) == 0
    assert get_version() in capsys.readouterr().out


def test_parser_defaults() -> None:
    args = build_parser().parse_args([*_BASE, "--smtp-password", "secret"])
    assert args.from_address == "from@example.com"
    assert args.to_address == "to@example.com"
    assert args.smtp_username == "user"
    assert args.smtp_password == "secret"
    assert args.smtp_server == "smtp.example.com"
    assert args.smtp_port == 25
    assert args.timeout == 10.0
    assert args.tls is False
    assert args.no_starttls is False
    assert args.verbose is False


def test_parser_auth_optional() -> None:
    args = build_parser().parse_args(_CONNECT)
    assert args.smtp_username is None
    assert args.smtp_password is None


def test_parser_overrides() -> None:
    args = build_parser().parse_args(
        [
            *_BASE,
            "--smtp-password",
            "secret",
            "--smtp-port",
            "587",
            "--timeout",
            "2.5",
            "--tls",
            "--no-starttls",
            "--subject",
            "Probe",
            "--body",
            "ping",
            "--verbose",
        ],
    )
    assert args.smtp_port == 587
    assert args.timeout == 2.5
    assert args.tls is True
    assert args.no_starttls is True
    assert args.subject == "Probe"
    assert args.body == "ping"
    assert args.verbose is True


def test_parser_rejects_non_positive_timeout() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([*_CONNECT, "--timeout", "0"])


def test_parser_rejects_out_of_range_port() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([*_CONNECT, "--smtp-port", "70000"])


def test_resolve_auth_from_flags() -> None:
    assert resolve_auth("user", "secret", {}) == ("user", "secret")


def test_resolve_auth_from_env() -> None:
    assert resolve_auth(
        None,
        None,
        {"SMTP_USERNAME": "from-env", "SMTP_PASSWORD": "from-env-pass"},
    ) == ("from-env", "from-env-pass")


def test_resolve_auth_omitted() -> None:
    assert resolve_auth(None, None, {}) == (None, None)


def test_resolve_auth_username_without_password() -> None:
    with pytest.raises(ValueError, match="both"):
        resolve_auth("user", None, {})


def test_main_requires_password_when_username_set(capsys) -> None:
    with patch("lupaxa.smtp_tester.cli.os.environ", {}):
        assert main(_BASE) == 1
    err = capsys.readouterr().err
    assert "both" in err


def test_main_success(capsys) -> None:
    result = SmtpTestResult(True, "to@example.com", "email sent to to@example.com")
    with patch("lupaxa.smtp_tester.cli.send_test_message", return_value=result) as send:
        assert main([*_BASE, "--smtp-password", "secret"]) == 0
    send.assert_called_once()
    kwargs = send.call_args.kwargs
    assert kwargs["use_tls"] is False
    assert kwargs["starttls"] is True
    assert "email sent" in capsys.readouterr().out


def test_main_skips_auth(capsys) -> None:
    result = SmtpTestResult(True, "to@example.com", "email sent to to@example.com")
    with (
        patch("lupaxa.smtp_tester.cli.send_test_message", return_value=result) as send,
        patch("lupaxa.smtp_tester.cli.os.environ", {}),
    ):
        assert main(_CONNECT) == 0
    assert send.call_args.args[2] is None
    assert send.call_args.args[3] is None
    assert "email sent" in capsys.readouterr().out


def test_main_failure_uses_stderr(capsys) -> None:
    result = SmtpTestResult(False, "to@example.com", "authentication failed", smtp_code=535)
    with patch("lupaxa.smtp_tester.cli.send_test_message", return_value=result):
        assert main([*_BASE, "--smtp-password", "secret", "--tls"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "authentication failed" in captured.err

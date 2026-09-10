"""Command-line interface for SMTP Tester."""

from __future__ import annotations

import argparse
import logging
import math
import os
import sys
from collections.abc import Mapping

from .client import DEFAULT_PORT, DEFAULT_TIMEOUT, send_test_message
from .message import DEFAULT_BODY, DEFAULT_SUBJECT
from .version import get_version

_SMTP_USER_ENV = "SMTP_USERNAME"
_SMTP_AUTH_ENV = "SMTP_PASSWORD"


def _positive_timeout(value: str) -> float:
    try:
        timeout = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be a number") from exc
    if not math.isfinite(timeout) or timeout <= 0:
        raise argparse.ArgumentTypeError("timeout must be greater than 0")
    return timeout


def _tcp_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be an integer") from exc
    if port < 1 or port > 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def build_parser() -> argparse.ArgumentParser:
    """Build the ``smtp-tester`` argument parser."""
    parser = argparse.ArgumentParser(
        description="Send a test email through an SMTP server.",
    )
    parser.add_argument(
        "-f",
        "--from-address",
        required=True,
        metavar="ADDR",
        help="From address",
    )
    parser.add_argument(
        "-t",
        "--to-address",
        required=True,
        metavar="ADDR",
        help="To address",
    )
    parser.add_argument(
        "-u",
        "--smtp-username",
        default=None,
        metavar="USER",
        help=f"SMTP username (or set {_SMTP_USER_ENV}; omit with password to skip AUTH)",
    )
    parser.add_argument(
        "-p",
        "--smtp-password",
        default=None,
        metavar="PASS",
        help=f"SMTP password (or set {_SMTP_AUTH_ENV}; omit with username to skip AUTH)",
    )
    parser.add_argument(
        "-s",
        "--smtp-server",
        required=True,
        metavar="HOST",
        help="SMTP server hostname",
    )
    parser.add_argument(
        "-P",
        "--smtp-port",
        type=_tcp_port,
        default=DEFAULT_PORT,
        metavar="PORT",
        help=f"SMTP port (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "-T",
        "--timeout",
        type=_positive_timeout,
        default=DEFAULT_TIMEOUT,
        metavar="SECONDS",
        help=f"Socket timeout in seconds (default: {DEFAULT_TIMEOUT:g})",
    )
    parser.add_argument(
        "--tls",
        action="store_true",
        help="Use implicit TLS (SMTP_SSL), typically port 465",
    )
    parser.add_argument(
        "--no-starttls",
        action="store_true",
        help="Do not require STARTTLS (credentials go in the clear if AUTH is used)",
    )
    parser.add_argument(
        "--subject",
        default=DEFAULT_SUBJECT,
        help=f"Message subject (default: {DEFAULT_SUBJECT})",
    )
    parser.add_argument(
        "--body",
        default=DEFAULT_BODY,
        help="Plain-text body",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Log SMTP steps without protocol payloads",
    )
    parser.add_argument("--version", action="version", version=get_version())
    return parser


def resolve_auth(
    cli_username: str | None,
    cli_password: str | None,
    environ: Mapping[str, str] | None = None,
) -> tuple[str | None, str | None]:
    """Resolve username and password from flags or the environment.

    Parameters
    ----------
    cli_username
        Value from ``--smtp-username``, if any.
    cli_password
        Value from ``--smtp-password``, if any.
    environ
        Environment mapping. Defaults to ``os.environ``.

    Returns
    -------
    tuple[str | None, str | None]
        ``(username, password)``, or ``(None, None)`` to skip AUTH.

    Raises
    ------
    ValueError
        If only one of username or password is set.
    """
    env = os.environ if environ is None else environ
    username = cli_username if cli_username is not None else env.get(_SMTP_USER_ENV)
    password = cli_password if cli_password is not None else env.get(_SMTP_AUTH_ENV)
    if username == "":
        username = None
    if password == "":
        password = None
    if (username is None) ^ (password is None):
        raise ValueError(
            "username and password must both be set, or both omitted "
            f"(flags or {_SMTP_USER_ENV} / {_SMTP_AUTH_ENV})",
        )
    return username, password


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        format="%(message)s",
    )


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        return code if isinstance(code, int) else 1

    try:
        username, password = resolve_auth(args.smtp_username, args.smtp_password)
    except ValueError as exc:
        print(f"smtp-tester: {exc}", file=sys.stderr)
        return 1

    _configure_logging(args.verbose)
    try:
        result = send_test_message(
            args.smtp_server,
            args.smtp_port,
            username,
            password,
            args.from_address,
            args.to_address,
            timeout=args.timeout,
            use_tls=args.tls,
            starttls=not args.no_starttls,
            subject=args.subject,
            body=args.body,
            debug=args.verbose,
        )
    except ValueError as exc:
        print(f"smtp-tester: {exc}", file=sys.stderr)
        return 1
    stream = sys.stdout if result.ok else sys.stderr
    print(result.detail, file=stream)
    return 0 if result.ok else 1

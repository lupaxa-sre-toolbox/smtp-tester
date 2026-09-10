"""lupaxa.smtp_tester — send a test email through an SMTP server."""

from __future__ import annotations

from .client import DEFAULT_PORT, DEFAULT_TIMEOUT, SmtpTestResult, send_test_message
from .message import DEFAULT_BODY, DEFAULT_SUBJECT, build_test_message
from .version import __version__, get_version

__all__ = [
    "DEFAULT_BODY",
    "DEFAULT_PORT",
    "DEFAULT_SUBJECT",
    "DEFAULT_TIMEOUT",
    "SmtpTestResult",
    "__version__",
    "build_test_message",
    "get_version",
    "send_test_message",
]

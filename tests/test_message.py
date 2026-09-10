"""Test message assembly."""

from __future__ import annotations

from lupaxa.smtp_tester.message import DEFAULT_BODY, DEFAULT_SUBJECT, build_test_message


def test_build_test_message_headers_and_body() -> None:
    message = build_test_message("from@example.com", "to@example.com")
    assert "from@example.com" in message["From"]
    assert "to@example.com" in message["To"]
    assert message["Subject"] == DEFAULT_SUBJECT
    assert DEFAULT_BODY in message.get_content()
    assert message["Date"]
    assert message["Message-ID"]


def test_build_test_message_custom_subject_and_body() -> None:
    message = build_test_message(
        "from@example.com",
        "to@example.com",
        subject="Probe",
        body="ping",
    )
    assert message["Subject"] == "Probe"
    assert "ping" in message.get_content()

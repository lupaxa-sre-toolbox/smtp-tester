# Getting started

## Requirements

- Python 3.13 or newer
- An SMTP server you are allowed to test
- No runtime dependencies beyond the standard library

## Install

```bash
pip install lupaxa-smtp-tester
smtp-tester --help
```

Library import:

```python
from lupaxa.smtp_tester import send_test_message

result = send_test_message(
    "smtp.example.com",
    587,
    "USER",
    "PASS",
    "from@example.com",
    "to@example.com",
)
print(result.ok, result.detail, result.smtp_code)
```

Module entry point:

```bash
python -m lupaxa.smtp_tester --version
```

### From source (development)

```bash
make init
make python-install-dev
smtp-tester --version
```

## First run

Pass From, To, and the SMTP host. Add username and password when the
server requires AUTH:

```bash
smtp-tester --from-address from@example.com --to-address to@example.com \
  --smtp-username USER --smtp-password PASS \
  --smtp-server smtp.example.com --smtp-port 587
```

Prefer `SMTP_USERNAME` and `SMTP_PASSWORD` instead of putting
credentials on the command line. STARTTLS is required on this path; the
send fails if the server does not advertise it. Use `--tls` with port
`465` for implicit TLS. Use `--no-starttls` only for a plaintext
internal relay. `--verbose` logs steps without protocol payloads. A
successful send prints `email sent to …` and exits `0`. Failures go to
stderr and exit `1`.

## Makefile helpers

```bash
make init                 # clone makefile-skills into .makefiles/
make python-install-dev   # editable install with [dev]
make python-check         # lint + type + test
make mkdocs-serve         # local docs site
```

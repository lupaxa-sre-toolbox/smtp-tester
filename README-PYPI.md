<!-- markdownlint-disable -->
<p align="center">
  <a href="https://github.com/lupaxa-sre-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/sre-toolbox/readme-logo.png" alt="Project Logo" width="256"/><br/>
  </a>
</p>
<h3 align="center">
  The Lupaxa SRE Toolbox<br />
  Part of The Lupaxa Project
</h3>

<br />

# lupaxa-smtp-tester

Send a test email through an SMTP server to verify delivery.

## Features

- Open one SMTP session and send a short plain-text test message
- Add `Date` and `Message-ID` headers automatically
- Require STARTTLS before AUTH or DATA (fail if it is not advertised)
- `--tls` for implicit TLS (`SMTP_SSL`, typically port 465)
- `--no-starttls` to send without the upgrade (plaintext AUTH if used)
- Optional AUTH: username and password together, or omit both
- Credentials from flags or `SMTP_USERNAME` / `SMTP_PASSWORD`
- `--timeout` to bound the socket
- `--verbose` logs steps without protocol payloads or the password
- Library API (`send_test_message`, `SmtpTestResult` with `smtp_code`)
- Fully typed, linted, formatted, and tested
- No runtime dependencies beyond the standard library

## Installation

### From PyPI

```bash
pip install lupaxa-smtp-tester
```

### From source (development mode)

```bash
pip install -e ".[dev]"
```

Requires Python 3.13+. No runtime dependencies.

## Library quick start

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

## CLI quick start

```bash
smtp-tester --help
smtp-tester --from-address from@example.com --to-address to@example.com \
  --smtp-username USER --smtp-password PASS \
  --smtp-server smtp.example.com --smtp-port 587
smtp-tester -f from@example.com -t to@example.com \
  -s smtp.internal.example.com --no-starttls
smtp-tester -f from@example.com -t to@example.com -u USER \
  -s smtp.example.com --tls -P 465
```

You can also run the CLI as a module:

```bash
python -m lupaxa.smtp_tester --help
python -m lupaxa.smtp_tester --version
```

## Documentation

Online documentation:

[Documentation](https://smtp-tester.thelupaxaproject.org/)

Source repository:

[GitHub](https://github.com/lupaxa-sre-toolbox/smtp-tester)

### Serve docs locally

From a clone of the repository:

```bash
make mkdocs-serve
```

Then open the local URL printed by MkDocs in your browser.

## Development

Clone the repository and install with Make:

```bash
make init                # first-time makefile-skills checkout
make python-install-dev  # editable install with [dev]
make python-check        # lint, type-check, and test
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>

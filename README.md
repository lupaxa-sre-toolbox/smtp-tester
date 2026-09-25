<p align="center">
  <a href="https://github.com/lupaxa-sre-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/sre-toolbox/readme-logo.png" alt="SRE Toolbox" />
  </a>
</p>

<h1 align="center">SMTP Tester</h1>

Send a test email through an SMTP server to verify delivery.

## Install

```bash
pip install lupaxa-smtp-tester
smtp-tester --help
```

## CLI

```bash
smtp-tester --from-address from@example.com --to-address to@example.com \
  --smtp-username USER --smtp-password PASS \
  --smtp-server email-smtp.eu-west-1.amazonaws.com --smtp-port 587
smtp-tester -f from@example.com -t to@example.com -u USER -s smtp.example.com -P 587
smtp-tester -f from@example.com -t to@example.com -s smtp.internal.example.com --no-starttls
smtp-tester -f from@example.com -t to@example.com -u USER -s smtp.example.com --tls -P 465
python -m lupaxa.smtp_tester --version
```

The tool opens one SMTP session and sends a short plain-text message
with `Date` and `Message-ID`. STARTTLS is required unless you pass
`--tls` (implicit TLS, typically port 465) or `--no-starttls`. AUTH is
optional: pass username and password together, or omit both for an
internal relay. Credentials may come from `--smtp-username` /
`--smtp-password` or `SMTP_USERNAME` / `SMTP_PASSWORD`. `--timeout`
bounds the socket. `--verbose` logs steps (connect, EHLO, STARTTLS,
AUTH, send) without protocol payloads.

## Library

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

## Development

```bash
make init
make python-install-dev
make python-check
make mkdocs-serve
```

## Documentation

The published guide is at
<https://smtp-tester.thelupaxaproject.org/>.

Site Markdown lives in `mkdocs/`.

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>

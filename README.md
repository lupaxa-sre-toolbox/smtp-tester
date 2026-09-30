<p align="center">
  <a href="https://github.com/lupaxa-sre-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/sre-toolbox/readme-logo.png" alt="SRE Toolbox" />
  </a>
</p>

<h1 align="center">SMTP Tester</h1>

Send a test email through an SMTP server to verify delivery.

Requires Python 3.13 or newer. The runtime is the standard library
only.

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
`--smtp-password` or `SMTP_USERNAME` / `SMTP_PASSWORD`. Flags override
the environment. `--timeout` bounds the socket. `--verbose` logs steps
(connect, EHLO, STARTTLS, AUTH, send) without protocol payloads.

A successful send prints `email sent to <to-address>` and exits `0`.
Failures go to stderr and exit `1`. The password is never included in
that output or in `--verbose` logs. `--no-starttls` sends in the
clear; do not use it with credentials on an untrusted network.

### Flags

| Flag              | Default               | Description                                           |
| :---------------- | :-------------------- | :---------------------------------------------------- |
| `--from-address`  | required              | From address (`-f`)                                   |
| `--to-address`    | required              | To address (`-t`)                                     |
| `--smtp-username` | `SMTP_USERNAME`       | SMTP username; omit with password to skip AUTH (`-u`) |
| `--smtp-password` | `SMTP_PASSWORD`       | SMTP password; omit with username to skip AUTH (`-p`) |
| `--smtp-server`   | required              | SMTP hostname (`-s`)                                  |
| `--smtp-port`     | `25`                  | SMTP port (`1`–`65535`, `-P`)                         |
| `--timeout`       | `10`                  | Socket timeout in seconds (`-T`)                      |
| `--tls`           | off                   | Implicit TLS (`SMTP_SSL`, typically port 465)         |
| `--no-starttls`   | off                   | Do not require STARTTLS                               |
| `--subject`       | `Simple test message` | Message subject                                       |
| `--body`          | built-in body         | Plain-text body                                       |
| `--verbose`       | off                   | Log SMTP steps without protocol payloads (`-v`)       |
| `--version`       | —                     | Print the package version and exit                    |

`--timeout` must be greater than `0`. Username and password must both
be set or both omitted.

### Exit codes

| Code | When                                                          |
| :--- | :------------------------------------------------------------ |
| `0`  | Help, version, or the test message was accepted               |
| `1`  | Invalid arguments, mismatched credentials, or the send failed |

### Examples

Prefer environment credentials over the command line:

```bash
export SMTP_USERNAME='USER'
export SMTP_PASSWORD='your-smtp-password'
smtp-tester --from-address from@example.com --to-address to@example.com \
  --smtp-server smtp.example.com --smtp-port 587
```

Amazon SES needs an SES SMTP credential, not the AWS access key.
The From address must be a verified identity in that SES region:

```bash
smtp-tester --from-address from@example.com --to-address to@example.com \
  --smtp-username AKIAexample --smtp-password SES_SMTP_PASSWORD \
  --smtp-server email-smtp.eu-west-1.amazonaws.com --smtp-port 587
```

Custom subject, body, timeout, and step logs:

```bash
smtp-tester --from-address from@example.com --to-address to@example.com \
  --smtp-username USER --smtp-password PASS \
  --smtp-server smtp.example.com --smtp-port 587 \
  --subject "SMTP probe" --body "ping" --verbose --timeout 15
```

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

`send_test_message` returns an `SmtpTestResult` with `ok`,
`to_address`, `detail`, and `smtp_code`. Pass `use_tls=True` for
implicit TLS, or `starttls=False` to skip STARTTLS. Pass `None` for
both username and password to skip AUTH. Invalid `port` or `timeout`,
or only one credential, raises `ValueError`. Socket, TLS,
authentication, and SMTP reply failures return `ok=False` instead of
raising.

## Development

```bash
make init
make python-install-dev
make python-check
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>

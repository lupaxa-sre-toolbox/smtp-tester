# Usage

The CLI opens one SMTP session and sends a short plain-text message.
Short flags match the original script: `-f`, `-t`, `-u`, `-p`, `-s`,
`-P`, `-T`, and `-v`.

## CLI Flags

| Flag              | Default               | Description                                           |
| :---------------- | :-------------------- | :---------------------------------------------------- |
| `--from-address`  | required              | From address                                          |
| `--to-address`    | required              | To address                                            |
| `--smtp-username` | `SMTP_USERNAME`       | SMTP username; omit with password to skip AUTH        |
| `--smtp-password` | `SMTP_PASSWORD`       | SMTP password; omit with username to skip AUTH        |
| `--smtp-server`   | required              | SMTP hostname                                         |
| `--smtp-port`     | `25`                  | SMTP port                                             |
| `--timeout`       | `10`                  | Socket timeout in seconds                             |
| `--tls`           | off                   | Implicit TLS (`SMTP_SSL`, typically port 465)         |
| `--no-starttls`   | off                   | Do not require STARTTLS                               |
| `--subject`       | `Simple test message` | Message subject                                       |
| `--body`          | built-in body         | Plain-text body                                       |
| `--verbose`       | off                   | Log SMTP steps without protocol payloads              |
| `--version`       | —                     | Print the package version and exit                    |

`--timeout` must be greater than `0`. `--smtp-port` must be an integer
from `1` to `65535`. Username and password must both be set or both
omitted. Flags override `SMTP_USERNAME` and `SMTP_PASSWORD`.

STARTTLS is required unless `--tls` or `--no-starttls` is set. If
STARTTLS is required and the server does not advertise it, the send
fails before AUTH. `--no-starttls` sends in the clear; do not use it
with credentials on an untrusted network.

```bash
smtp-tester --from-address from@example.com --to-address to@example.com \
  --smtp-username USER --smtp-password PASS \
  --smtp-server smtp.example.com --smtp-port 587
smtp-tester -f from@example.com -t to@example.com \
  -s smtp.internal.example.com --no-starttls
smtp-tester -f from@example.com -t to@example.com -u USER \
  -s smtp.example.com --tls -P 465
smtp-tester --version
```

A successful send prints `email sent to <to-address>` and exits `0`.
A failed send prints a reason on stderr and exits `1`. The password is
never included in that output or in `--verbose` logs.

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
    timeout=10.0,
)
if not result.ok:
    raise SystemExit(f"{result.detail} ({result.smtp_code})")
```

`send_test_message` returns an `SmtpTestResult` with `ok`,
`to_address`, `detail`, and `smtp_code`. Pass `use_tls=True` for
implicit TLS, or `starttls=False` to skip STARTTLS. Pass `None` for
both username and password to skip AUTH. Invalid `port` or `timeout`,
or only one credential, raises `ValueError`.

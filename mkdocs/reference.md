# Reference

## CLI arguments

| Flag              | Default               | Description                                   |
| :---------------- | :-------------------- | :-------------------------------------------- |
| `--from-address`  | required              | From address                                  |
| `--to-address`    | required              | To address                                    |
| `--smtp-username` | `SMTP_USERNAME`       | SMTP username; omit both to skip AUTH         |
| `--smtp-password` | `SMTP_PASSWORD`       | SMTP password; omit both to skip AUTH         |
| `--smtp-server`   | required              | SMTP hostname                                 |
| `--smtp-port`     | `25`                  | SMTP port (`1`–`65535`)                       |
| `--timeout`       | `10`                  | Socket timeout in seconds                     |
| `--tls`           | off                   | Implicit TLS (`SMTP_SSL`)                     |
| `--no-starttls`   | off                   | Do not require STARTTLS                       |
| `--subject`       | `Simple test message` | Message subject                               |
| `--body`          | built-in body         | Plain-text body                               |
| `--verbose`       | off                   | Log SMTP steps without protocol payloads      |
| `--version`       | —                     | Print the package version and exit            |

`--timeout` must be greater than `0` when set. `--tls` never issues
STARTTLS. Without `--tls` or `--no-starttls`, STARTTLS is required.

## Exit codes

| Code | When                                                              |
| :--- | :---------------------------------------------------------------- |
| `0`  | Help, version, or the test message was accepted                   |
| `1`  | Invalid arguments, mismatched credentials, or the send failed     |

## Library

| Name                 | Meaning                                                     |
| :------------------- | :---------------------------------------------------------- |
| `send_test_message`  | Connect, optionally authenticate, and send one test message |
| `SmtpTestResult`     | Frozen result: `ok`, `to_address`, `detail`, `smtp_code`    |
| `smtp_code`          | SMTP status code on failure, or `None`                      |
| `build_test_message` | Build the MIME `EmailMessage` with Date and Message-ID      |
| `DEFAULT_PORT`       | Default SMTP port (`25`)                                    |
| `DEFAULT_TIMEOUT`    | Default socket timeout (`10`)                               |
| `DEFAULT_SUBJECT`    | Default message subject                                     |
| `DEFAULT_BODY`       | Default plain-text body                                     |
| `get_version()`      | Return the package version string                           |

`send_test_message` never puts the password into `detail` or debug
logs. Socket, timeout, TLS, authentication, and SMTP reply failures
return `ok=False` instead of raising. `ValueError` is raised for a
bad port, a non-positive timeout, or a username without a password
(or the reverse). `SMTPNotSupportedError` and other
`SMTPException` subclasses are returned as failures.

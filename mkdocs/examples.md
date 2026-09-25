# Examples

## Submission on Port 587

```bash
smtp-tester --from-address from@example.com --to-address to@example.com \
  --smtp-username USER --smtp-password PASS \
  --smtp-server smtp.example.com --smtp-port 587
```

STARTTLS is required. The send fails if the server does not advertise
it.

## Implicit TLS on Port 465

```bash
smtp-tester --from-address from@example.com --to-address to@example.com \
  --smtp-username USER --smtp-password PASS \
  --smtp-server smtp.example.com --smtp-port 465 --tls
```

## Internal Relay without AUTH

```bash
smtp-tester --from-address from@example.com --to-address to@example.com \
  --smtp-server smtp.internal.example.com --no-starttls
```

Omit both username and password. `--no-starttls` is for a plaintext
lab or internal relay you already trust.

## Credentials from the Environment

```bash
export SMTP_USERNAME='USER'
export SMTP_PASSWORD='your-smtp-password'
smtp-tester --from-address from@example.com --to-address to@example.com \
  --smtp-server smtp.example.com --smtp-port 587
```

## Amazon SES

```bash
smtp-tester --from-address from@example.com --to-address to@example.com \
  --smtp-username AKIAexample --smtp-password SES_SMTP_PASSWORD \
  --smtp-server email-smtp.eu-west-1.amazonaws.com --smtp-port 587
```

Use an SES SMTP credential, not the AWS access key itself. The From
address must be a verified identity in that SES region.

## Custom Subject and Step Logs

```bash
smtp-tester --from-address from@example.com --to-address to@example.com \
  --smtp-username USER --smtp-password PASS \
  --smtp-server smtp.example.com --smtp-port 587 \
  --subject "SMTP probe" --body "ping" --verbose --timeout 15
```

`--verbose` prints connect, EHLO, STARTTLS, AUTH, and send. It does
not print the password or raw SMTP lines.

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
    subject="SMTP probe",
    body="ping",
)
print(result.ok, result.detail, result.smtp_code)
```

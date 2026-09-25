# SMTP Tester

`lupaxa-smtp-tester` sends one test email through an SMTP server so
you can confirm the gateway accepts mail.

Install the package for the library API and the `smtp-tester`
console command:

```bash
pip install lupaxa-smtp-tester
smtp-tester --from-address from@example.com --to-address to@example.com \
  --smtp-username USER --smtp-password PASS \
  --smtp-server smtp.example.com --smtp-port 587
```

You can also run `python -m lupaxa.smtp_tester`.

## What it Does

- Opens one SMTP session to the host and port you name
- Requires STARTTLS unless you use implicit TLS or `--no-starttls`
- Authenticates when you pass a username and password, or skips AUTH
- Sends a short plain-text message with `Date` and `Message-ID`
- Returns a success or failure reason and optional SMTP status code
- Never echoes the password, including under `--verbose`
- Exposes `send_test_message` as a library function

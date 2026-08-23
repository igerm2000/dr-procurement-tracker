"""
Sends email via Gmail SMTP using an app password.
Credentials come from environment variables, which the GitHub Actions
workflow populates from repo secrets -- they are never written to any
file in the repo.
"""
import os
import smtplib
from email.mime.text import MIMEText


def send_email(subject, html_body):
    gmail_address = os.environ["GMAIL_ADDRESS"]
    gmail_app_password = os.environ["GMAIL_APP_PASSWORD"]
    to_address = os.environ["ALERT_TO_EMAIL"]

    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = gmail_address
    msg["To"] = to_address

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, gmail_app_password)
        server.sendmail(gmail_address, [to_address], msg.as_string())

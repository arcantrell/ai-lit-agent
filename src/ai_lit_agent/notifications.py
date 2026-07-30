from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


def email_enabled() -> bool:
    required = ("AI_LIT_AGENT_SMTP_HOST", "AI_LIT_AGENT_EMAIL_TO", "AI_LIT_AGENT_EMAIL_FROM")
    return all(os.environ.get(name) for name in required)


def send_briefing_email(subject: str, body: str) -> bool:
    if not email_enabled():
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = os.environ["AI_LIT_AGENT_EMAIL_FROM"]
    message["To"] = os.environ["AI_LIT_AGENT_EMAIL_TO"]
    message.set_content(body)

    host = os.environ["AI_LIT_AGENT_SMTP_HOST"]
    port = int(os.environ.get("AI_LIT_AGENT_SMTP_PORT", "587"))
    username = os.environ.get("AI_LIT_AGENT_SMTP_USERNAME")
    password = os.environ.get("AI_LIT_AGENT_SMTP_PASSWORD")
    use_tls = os.environ.get("AI_LIT_AGENT_SMTP_TLS", "true").lower() not in {"0", "false", "no"}

    with smtplib.SMTP(host, port, timeout=30) as smtp:
        if use_tls:
            smtp.starttls()
        if username and password:
            smtp.login(username, password)
        smtp.send_message(message)
    return True

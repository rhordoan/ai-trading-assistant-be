import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from jose import jwt
from datetime import datetime, timedelta

from app.core.config import settings

SENDGRID_API_KEY = settings.SENDGRID_API_KEY
EMAIL_SENDER = settings.EMAIL_SENDER
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

def create_magic_token(email: str) -> str:
    """
    Create a JWT token for the magic link.
    """
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def send_email_link(recipient: str, token: str):
    """
    Send a magic link to the user's email for login.
    """
    login_url = f"http://localhost:8000/auth/verify-token?token={token}"
    message = Mail(
        from_email=EMAIL_SENDER,
        to_emails=recipient,
        subject="Your Magic Login Link",
        html_content=f"""
            <p>Click the link below to log in:</p>
            <p><a href="{login_url}">Log in</a></p>
            <p>This link will expire in 15 minutes.</p>
        """
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        print(f"SendGrid Error: {e}")

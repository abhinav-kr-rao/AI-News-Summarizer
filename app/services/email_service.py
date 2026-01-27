import smtplib
import os
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, html_content: str):
    """
    Sends an HTML email using Gmail's SMTP server.
    Requires GOOGLE_APP_PASSWORD and GMAIL_ID environment variables.
    """
    gmail_user = os.getenv("GMAIL_ID")
    gmail_password = os.getenv("GOOGLE_APP_PASSWORD")

    if not gmail_user or not gmail_password:
        logger.error("GMAIL_ID or GOOGLE_APP_PASSWORD not set. Cannot send email.")
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = gmail_user
    message["To"] = to_email

    # Turn these into plain/html MIMEText objects
    # We will only provide HTML for now, or a simple fallback for plain text
    text = "Please view this email in a client that supports HTML."
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html_content, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(
                gmail_user, to_email, message.as_string()
            )
        logger.info(f"Email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

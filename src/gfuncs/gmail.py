import base64
from email.message import EmailMessage

from gfuncs import auth


def send_email(to="", subject="", body="") -> None:
    service = auth.service("gmail")

    if not to:
        to = auth.username()
    if not subject:
        subject = f"Message from {__file__}"

    message = EmailMessage()
    message.set_content(body)
    message["To"] = auth.username()
    message["Subject"] = subject

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"raw": encoded_message}
    service.users().messages().send(userId="me", body=create_message).execute()

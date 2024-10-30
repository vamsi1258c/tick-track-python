import os
import json
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from email.message import EmailMessage


def convert_to_enum(enum_class, value):
    # Normalize the value to lowercase
    normalized_value = value.lower()
    for enum_member in enum_class:
        if enum_member.value == normalized_value:
            return enum_member
    # Raise an error if no match found
    raise ValueError(f"Invalid value: {value}")

def create_message(sender_email, to_email, subject, message_text):
    """Create an email message."""
    message = EmailMessage()
    message.set_content(message_text)
    message['To'] = to_email
    message['From'] = sender_email
    message['Subject'] = subject

    # Encode the message to base64
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_email(sender_email, to_email, subject, message_text):
    """Send an email using Gmail API and OAuth 2.0."""
    # Create the email message
    email_message = create_message(sender_email, to_email, subject, message_text)
    print(to_email)
    # Load credentials from the service account file
    creds = service_account.Credentials.from_service_account_file(
        'config/service_account.json',
        scopes=['https://www.googleapis.com/auth/gmail.send']
    )

    delegated_creds = creds.with_subject(sender_email)

    # Build the Gmail service
    service = build('gmail', 'v1', credentials=delegated_creds)

    try:
        # Send the email
        service.users().messages().send(userId='me', body=email_message).execute()
        print("Email sent successfully.")
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")
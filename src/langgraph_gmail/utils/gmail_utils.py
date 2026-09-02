from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import base64
import datetime
from ..state import Email
from .html_utils import html_to_text

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def _decode_body(data: str) -> str:
    if not data:
        return ''
    try:
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
    except Exception:
        return ''


def _iter_parts(payload):
    """Yield every part of the MIME tree, including nested multiparts."""
    yield payload
    for part in payload.get('parts', []) or []:
        yield from _iter_parts(part)


def extract_body(payload) -> str:
    """Return the email body as plain text, preferring text/plain over text/html."""
    plain, html = '', ''
    for part in _iter_parts(payload):
        mime = part.get('mimeType', '')
        # Skip attachments; they carry attachmentId instead of inline data.
        if part.get('body', {}).get('attachmentId'):
            continue
        data = part.get('body', {}).get('data', '')
        if not data:
            continue
        if mime == 'text/plain' and not plain:
            plain = _decode_body(data)
        elif mime == 'text/html' and not html:
            html = _decode_body(data)

    if plain.strip():
        return plain.strip()
    if html.strip():
        return html_to_text(html)
    return ''


def parse_email_message(message) -> Email:
    headers_list = message.get('payload', {}).get('headers', [])
    headers = {header['name'].lower(): header['value'] for header in headers_list}

    subject = headers.get('subject', 'No Subject')
    from_email = headers.get('from', 'No Sender')
    date = headers.get('date', 'No Date')
    message_id = headers.get('message-id', '')
    references = headers.get('references', '')

    body = extract_body(message.get('payload', {}))

    return Email(
        id=message.get('id', ''),
        subject=subject,
        sender=from_email,
        date=date,
        body=body,
        message_id=message_id,
        references=references,
        thread_id=message.get('threadId', ''),
    )

def get_most_recent_email(user_id='me') -> Email | None:
    service = get_gmail_service()
    today = datetime.datetime.now().date()
    query = f'after:{today.strftime("%Y/%m/%d")}'
    try:
        results = service.users().messages().list(userId=user_id, q=query, maxResults=1).execute()
        messages = results.get('messages', [])
        if not messages:
            return None
        message_id = messages[0]['id'] # Get the ID of the most recent message
        message = service.users().messages().get(userId=user_id, id=message_id).execute()
        return parse_email_message(message)
    except Exception as e:
        print(f"An error occurred while fetching the most recent email: {e}")
        return None

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from ..state import Email
from .html_utils import html_to_text
import os
import base64
import datetime
import uuid

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Paths can point at Secret Manager files mounted by Cloud Run's --set-secrets.
_CREDENTIALS_FILE = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
_TOKEN_FILE = os.getenv('GMAIL_TOKEN_FILE', 'token.json')
# On servers set this to "false" so we never try to open a browser.
_ALLOW_INTERACTIVE_AUTH = os.getenv(
    'GMAIL_ALLOW_INTERACTIVE_AUTH', 'true'
).lower() not in ('0', 'false', 'no')


def _persist_token(creds) -> None:
    """Best-effort cache of the (refreshed) token; a no-op on a read-only FS."""
    try:
        with open(_TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    except OSError:
        pass


def get_gmail_service():
    creds = None
    if os.path.exists(_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(_TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            _persist_token(creds)
        elif _ALLOW_INTERACTIVE_AUTH:
            flow = InstalledAppFlow.from_client_secrets_file(_CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            _persist_token(creds)
        else:
            raise RuntimeError(
                'No valid Gmail credentials and interactive auth is disabled. '
                f'Provide a pre-authorized token at {_TOKEN_FILE!r} (must contain a '
                'refresh token).'
            )

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
    # Restrict to the Primary inbox tab so promotions/social/updates are ignored.
    query = f'category:primary after:{today.strftime("%Y/%m/%d")}'
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

def send_reply_email(original_email: Email, reply_email: Email) -> bool:
    try:
        service = get_gmail_service()

        sender_email = original_email.sender
        if '<' in sender_email and '>' in sender_email:
            sender_email = sender_email.split('<')[1].split('>')[0]

        print(f"Reply will be sent to: {sender_email}")

        reply_subject = reply_email.subject
        original_subject = original_email.subject
        if original_subject.startswith('Re:'):
            reply_subject = original_subject
        else:
            reply_subject = f"Re: {original_subject}"

        message_id = original_email.message_id
        references = original_email.references
        thread_id = original_email.thread_id

        if not message_id:
            message_id = f"<{original_email.id}@gmail.com>"

        message = _create_reply_message_with_thread(
            to=sender_email,
            subject=reply_subject,
            message_text=reply_email.body,
            original_message_id=message_id,
            original_references=references,
            thread_id=thread_id
        )

        sent_message = service.users().messages().send(userId='me', body=message).execute()

        print(f"Threaded reply email sent successfully. Message ID: {sent_message['id']}")
        return True

    except Exception as error:
        print(f'An error occurred while sending reply email: {error}')
        return False

def _create_reply_message_with_thread(to: str, subject: str, message_text: str, original_message_id: str, original_references: str, thread_id: str) -> dict:
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject

    if original_message_id:
        message['In-Reply-To'] = original_message_id
        if original_references:
            references = f"{original_references} {original_message_id}".strip()
        else:
            references = original_message_id
        message['References'] = references

        message['Message-ID'] = f"<{uuid.uuid4()}@gmail.com>"

    body = {
        'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    }

    if thread_id:
        body['threadId'] = thread_id
    return body
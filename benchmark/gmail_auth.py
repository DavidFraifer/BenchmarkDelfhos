"""Shared Gmail OAuth helper.

Tries delfhos's cached token first (~/.config/oauth_gmail.json) so only
one browser authorisation is needed for the whole benchmark.
"""

from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .config import OAUTH_CREDS_PATH, BENCHMARK_TOKEN_PATH, DELFHOS_TOKEN_PATH, GMAIL_SCOPES


def get_gmail_credentials() -> Credentials:
    creds = None

    # 1. Prefer delfhos cached token (already authorised by user)
    for token_path in [DELFHOS_TOKEN_PATH, BENCHMARK_TOKEN_PATH]:
        if Path(token_path).exists():
            try:
                creds = Credentials.from_authorized_user_file(token_path, GMAIL_SCOPES)
                if creds and creds.valid:
                    return creds
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    _save_token(creds)
                    return creds
            except Exception:
                creds = None

    # 2. Full OAuth flow (opens browser once)
    flow = InstalledAppFlow.from_client_secrets_file(OAUTH_CREDS_PATH, GMAIL_SCOPES)
    creds = flow.run_local_server(port=0)
    _save_token(creds)
    return creds


def _save_token(creds: Credentials) -> None:
    Path(BENCHMARK_TOKEN_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(BENCHMARK_TOKEN_PATH).write_text(creds.to_json())


def get_gmail_service():
    """Return an authenticated Gmail API service object."""
    creds = get_gmail_credentials()
    return build("gmail", "v1", credentials=creds)


def read_recent_emails_raw(count: int = 5) -> list[dict]:
    """Read `count` most recent emails. Returns list of dicts."""
    service = get_gmail_service()
    resp = service.users().messages().list(userId="me", maxResults=count, labelIds=["INBOX"]).execute()
    messages = resp.get("messages", [])

    emails = []
    for m in messages:
        msg = service.users().messages().get(userId="me", id=m["id"], format="metadata").execute()
        headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
        emails.append(
            {
                "from": headers.get("From", "Unknown"),
                "subject": headers.get("Subject", "(no subject)"),
                "date": headers.get("Date", "Unknown"),
                "snippet": msg.get("snippet", ""),
            }
        )
    return emails

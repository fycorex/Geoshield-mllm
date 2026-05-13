from __future__ import annotations

from pathlib import Path
from typing import Any

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def build_drive_service_oauth(client_secrets: Path, token_path: Path) -> Any:
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError("Google Drive OAuth dependencies are not installed.") from exc

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json(), encoding="utf-8")
    return build("drive", "v3", credentials=creds)


def build_drive_service_service_account(credentials_path: Path) -> Any:
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError("Google Drive service account dependencies are not installed.") from exc

    creds = service_account.Credentials.from_service_account_file(str(credentials_path), scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_drive(file_path: str, mime_type: str, folder_id: str = None) -> str:
    """
    Uploads a file to Google Drive using OAuth 2.0 User Credentials (via environment secrets).
    Uses your personal Google account's storage quota rather than a Service Account.
    """
    print(f"Uploading {os.path.basename(file_path)} to Google Drive...")

    # Fetch OAuth credentials and target folder directly from Environment Variables
    client_id = os.environ.get("GDRIVE_CLIENT_ID")
    client_secret = os.environ.get("GDRIVE_CLIENT_SECRET")
    refresh_token = os.environ.get("GDRIVE_REFRESH_TOKEN")
    target_folder_id = folder_id or os.environ.get("GDRIVE_FOLDER_ID")

    # Validate that all required secrets exist
    if not all([client_id, client_secret, refresh_token]):
        raise ValueError(
            "Missing Google Drive OAuth secrets. "
            "Ensure GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET, and GDRIVE_REFRESH_TOKEN are set in environment."
        )

    # Initialize Credentials using Refresh Token (automatically generates a fresh access token)
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )

    drive_service = build('drive', 'v3', credentials=creds)

    # Build file metadata
    file_metadata = {'name': os.path.basename(file_path)}
    if target_folder_id:
        file_metadata['parents'] = [target_folder_id]

    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

    # Perform the upload
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    file_id = file.get('id')
    web_view_link = file.get('webViewLink')

    # Set 'anyone with link can read' permissions
    try:
        drive_service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
    except Exception as e:
        print(f"Warning: Could not set public permissions for file {file_id}: {e}")

    print(f"Successfully uploaded: {web_view_link}")
    return web_view_link
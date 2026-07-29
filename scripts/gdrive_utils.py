import json
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_drive(file_path: str, mime_type: str, service_account_json: str, folder_id: str = None) -> str:
    print("Uploading to Google Drive...")
    creds_dict = json.loads(service_account_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=['https://www.googleapis.com/auth/drive'])
    drive_service = build('drive', 'v3', credentials=creds)

    # Get target folder ID from argument or environment variable
    target_folder_id = folder_id or os.environ.get("GDRIVE_FOLDER_ID")

    file_metadata = {'name': os.path.basename(file_path)}

    # Target the shared folder so it uses your personal quota instead of the service account's 0B quota
    if target_folder_id:
        file_metadata['parents'] = [target_folder_id]

    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    # Make link readable for anyone
    drive_service.permissions().create(
        fileId=file.get('id'),
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    return file.get('webViewLink')
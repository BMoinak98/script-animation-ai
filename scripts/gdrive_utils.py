import json
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_drive(file_path: str, mime_type: str, service_account_json: str) -> str:
    print("Uploading to Google Drive...")
    creds_dict = json.loads(service_account_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=['https://www.googleapis.com/auth/drive'])
    drive_service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()

    # Make link readable for anyone
    drive_service.permissions().create(
        fileId=file.get('id'),
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    return file.get('webViewLink')
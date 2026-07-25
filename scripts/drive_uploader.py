import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_folder_contents(local_folder, parent_drive_id):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_file('service_account.json', scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    for root, _, files in os.walk(local_folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_metadata = {
                'name': file,
                'parents': [parent_drive_id]
            }
            media = MediaFileUpload(file_path, resumable=True)
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
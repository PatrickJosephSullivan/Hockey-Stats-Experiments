import os
from googleapiclient.discovery import build
import google.oauth2.credentials
import google_auth_oauthlib.flow


# Build the Google Drive API client
creds = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    os.path.expanduser("C:/Users/Patrick/Downloads/client_secret_656120656245-ic0cjv3gom480autn3mf2ghe8jbd753o.apps.googleusercontent.com.json"),
    scopes=["https://www.googleapis.com/auth/drive"]
)
service = build("drive", "v3", credentials=creds)

# Define the folder metadata
folder_metadata = {
    'name': 'example_folder',
    'mimeType': 'application/vnd.google-apps.folder'
}

# Create the folder in Google Drive
folder = service.files().create(body=folder_metadata, fields='id').execute()
print(F'Folder ID: {folder.get("id")}')

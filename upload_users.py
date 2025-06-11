import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === CONFIG ===
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
FOLDER_ID = "1tBpyY1VFi-hTxTWWlow4dE0PXrvV7Pvs"
USERS_FILE = "users.csv"

def get_drive_service():
    if os.path.exists("token_drive.pkl"):
        creds = Credentials.from_authorized_user_file("token_drive.pkl", SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token_drive.pkl", "w") as token:
            token.write(creds.to_json())
    return build("drive", "v3", credentials=creds)

def upload_users_file():
    service = get_drive_service()
    # Cerca se già esiste
    query = f"'{FOLDER_ID}' in parents and name='{USERS_FILE}' and trashed=false"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get("files", [])

    for f in files:
        service.files().delete(fileId=f["id"]).execute()

    file_metadata = {
        "name": USERS_FILE,
        "parents": [FOLDER_ID]
    }
    media = MediaFileUpload(USERS_FILE, mimetype="text/csv")
    service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"✅ File '{USERS_FILE}' caricato su Google Drive nella cartella condivisa.")

if __name__ == "__main__":
    if os.path.exists(USERS_FILE):
        upload_users_file()
    else:
        print(f"❌ File '{USERS_FILE}' non trovato nella cartella corrente.")

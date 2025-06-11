import gdown
import os

# === CONFIGURAZIONE TOKEN ===
TOKEN_FILENAME = "token_drive.pkl"
TOKEN_DRIVE_FILE_ID = "INSERISCI_QUI_ID_DEL_TOKEN_SUL_DRIVE"  # <-- Inserisci dopo il primo upload

def scarica_token_da_drive():
    """Scarica token_drive.pkl da Drive se non esiste in locale"""
    if not os.path.exists(TOKEN_FILENAME):
        try:
            print("🔄 Scarico token da Google Drive...")
            url = f"https://drive.google.com/uc?id={TOKEN_DRIVE_FILE_ID}"
            gdown.download(url, TOKEN_FILENAME, quiet=False)
            print("✅ Token scaricato correttamente.")
        except Exception as e:
            print(f"❌ Errore durante il download del token: {e}")

def carica_token_su_drive(service):
    """Carica il token_drive.pkl su Drive (solo una volta, manualmente)"""
    from googleapiclient.http import MediaFileUpload

    file_metadata = {
        "name": TOKEN_FILENAME,
        "parents": [FOLDER_ID],  # La tua cartella condivisa
    }
    media = MediaFileUpload(TOKEN_FILENAME, resumable=True)
    try:
        file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        print(f"✅ Token caricato. File ID: {file['id']}")
    except Exception as e:
        print(f"❌ Errore durante l'upload del token: {e}")

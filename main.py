#!/usr/bin/python3.7
import os
import io
import pickle
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Variables
SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]
CLIENT_SECRET_FILE = "/home/qleon/GIT/google_photos_downloader/client_secret.json"
TOKEN_PICKLE_FILE = "/home/qleon/GIT/google_photos_downloader/token.pickle"
DESTINATION_FOLDER = "/mnt/hdd4TB/OPEN/Photo/Photo_years/"
MAX_FILES = 120


def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server()
    with open(TOKEN_PICKLE_FILE, "wb") as token:
        pickle.dump(credentials, token)


def load_credentials():
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, "rb") as token:
            credentials = pickle.load(token)
            return credentials
    else:
        return None


def download_media(media_url, destination_path):
    if os.path.exists(destination_path):
        pass
    else:
        print(f"Downloading {destination_path}")
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        response = requests.get(media_url, stream=True)
        if response.status_code == 200:
            with open(destination_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)


def main():
    credentials = load_credentials()
    if not credentials:
        authenticate()
        credentials = load_credentials()

    service = build("photoslibrary", "v1", credentials=credentials, static_discovery=False)

    next_page_token = None
    downloaded_files = 0
    while downloaded_files < MAX_FILES:
        media_list = service.mediaItems().list(pageSize=100, pageToken=next_page_token).execute()
        media_items = media_list.get("mediaItems", [])
        for media_item in media_items:
            type = media_item["mimeType"]
            filename = media_item["filename"]
            filecreated = media_item["mediaMetadata"]["creationTime"]
            media_url = media_item["baseUrl"]
            if 'image' in type:
                media_url = "{}=d".format(media_url)
            elif 'video' in type:
                media_url = "{}=dv".format(media_url)
            destination_path = os.path.join(DESTINATION_FOLDER, filecreated[slice(4)], filecreated[slice(5,7)], f"{filename}")
            print(f"Check {filename}")
            download_media(media_url, destination_path)
            downloaded_files += 1
            if downloaded_files >= MAX_FILES:
                break
        next_page_token = media_list.get("nextPageToken")
        if not next_page_token:
            break


if __name__ == "__main__":
    main()

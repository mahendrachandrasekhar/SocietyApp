from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient import discovery
from httplib2 import Http
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client.service_account import ServiceAccountCredentials
from tabulate import tabulate
from mimetypes import MimeTypes
import pandas as pd
import io
import time
import pickle
import os

#https://medium.com/nerd-for-tech/request-get-files-from-google-api-with-python-f6dab75681ae

##################
### TO DO
##################
### Refer URL below.. Use token.pickle file for everything instead of service account.
#https://www.thepythoncode.com/article/using-google-drive--api-in-python#Upload_Files

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive']

def get_gdrive_service_oauth():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('.config/gspread/token.pickle'):
        with open('.config/gspread/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '.config/gspread/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('.config/gspread/token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # return Google Drive API service
    return build('drive', 'v3', credentials=creds)

def get_gdrive_service():
    credentials = ServiceAccountCredentials.from_json_keyfile_name('.config/gspread/service_account.json',scopes=SCOPES)
    # return Google Drive API service
    return build('drive', 'v3', credentials=credentials)

def get_folder_id(foldername):
    service = get_gdrive_service()

    results = service.files().list(pageSize=1000, orderBy='name', fields="nextPageToken, files(id, name, parents)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        for item in items:
            if item['name'] == foldername:
               parentId = item['id']

    return (parentId)

def list_files(foldername):
    d = {'FileName': [], 'Action':[]}

    service = get_gdrive_service()
    results = service.files().list(pageSize=1000, orderBy='name', fields="nextPageToken, files(id, name, parents)").execute()
    items = results.get('files', [])
    parentId = None

    if not items:
        print('No files found.')
    else:
        for item in items:
            if item['name'] == foldername:
               parentId = item['id']

        for item in items:
            try:
                if item['parents'][0] == parentId:
                    d['FileName'].append(item['name'])
                    d['Action'].append(item['id'])
                    #print(u'{0} {1} ({2})'.format(item['name'], item['name'], 'https://drive.google.com/file/d/'+item['id']))
            except (KeyError):
                a = None
    return (pd.DataFrame(data=d))
def get_file(fileId):
    service = get_gdrive_service()

    request = service.files().get_media(fileId=fileId)
    #fh = io.FileIO('download', 'wb')
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
        time.sleep(2)
    #file_name = os.path.join(name)

    return fh

def upload_file(folderName,fileName,flatNumber):
    folder_id = get_folder_id(folderName)
    # authenticate account
    service = get_gdrive_service_oauth()

    # upload a file text file
    # first, define file metadata, such as the name and the parent folder ID
    file_metadata = {
        "name": flatNumber+'-'+fileName,
        "parents": [folder_id]
    }
    # upload
    media = MediaFileUpload(fileName, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print("File created, id:", file.get("id"))
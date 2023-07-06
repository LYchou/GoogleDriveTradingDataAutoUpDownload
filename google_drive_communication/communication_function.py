import os 
from google.auth.transport.requests import Request
from  google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload


def get_api_service(SCOPES=['https://www.googleapis.com/auth/drive'], creds_and_tokem_path='./'):


    # SCOPES = ['https://www.googleapis.com/auth/drive']

    token_file =  os.path.join(creds_and_tokem_path, 'token.json')
    creds_file = os.path.join(creds_and_tokem_path, 'credentials.json')

    creds = None

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_file, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
    service = build('drive', 'v3', credentials=creds)

    return service


def get_metadata(service, fileId):
    '''
    function
        透過 id 取得資料元的基本資訊
    input
        :service: 跟雲端溝通的物件，可以從 get_api_service() 獲得
        :fileId: str, 設定要取得資料的屬性 ex:'id, name, mimeType, parents, createdTime, modifiedTime'
        
    output
        :file: dict, file基本資訊
    '''
    file = service.files().get(fileId=fileId).execute()
    return file



def query_metadata(service, query='', fields='id, name'):
    '''
    function
        取得雲端上檔案
    input
        :service: 跟雲端溝通的物件，可以從 get_api_service() 獲得
        :fields: str, 設定要取得資料的屬性 ex:'id, name, mimeType, parents, createdTime, modifiedTime' (https://developers.google.com/drive/api/v3/reference/files)
        :query: str, 篩選回傳資料的方式。(https://developers.google.com/drive/api/guides/search-files)
    output
        :files: list, 
            ex:
                [
                    {'id': '18UIQCxaPg9YQY01KsNWb4oa3rvEcTzi2',
                    'name': '2010-01-04.csv',
                    'mimeType': 'text/csv',
                    'parents': ['1VGU7TpbHxcp5AqmZAva9twtl80rJNV9Z'],
                    'createdTime': '2022-11-11T08:40:56.891Z',
                    'modifiedTime': '2022-11-10T08:53:18.000Z'
                    },
                    {

                    },
                    ...
                ]
    '''
    files = []
    page_token = None
    while True:
        # pylint: disable=maybe-no-member
        response = service.files().list(q=query,
                                        spaces='drive',
                                        fields=f'nextPageToken, files({fields})',
                                        pageToken=page_token).execute()
        # for file in response.get('files', []):
        #     # Process change
        #     print(F'Found file: {file.get("name")}, {file.get("id")}')
        files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    return files

def create_folder(service, folder_name, parent_id):
    '''
    function
        在雲端創建資料夾，位置為 parent_id 目錄下
    input
        :service: 跟雲端溝通的物件，可以從 get_api_service() 獲得
        :folder_name: str
        :parent_id: str 
    output
        :file: dict, 創建資料的訊息
    '''
    file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
    file = service.files().create(body=file_metadata).execute() 
    return file


def delete_metadata(service, fileId):
    '''
    function
        刪除雲端的資料(雲端上所有元素都可以，如資料夾或檔案)
    input
        :service: 跟雲端溝通的物件，可以從 get_api_service() 獲得
        :fileId: str
    output
        None
    '''
    service.files().delete(fileId=fileId).execute()

def upload_file(service, fileName, parent_id, loacl_file):
    '''
    function
        上傳本地資料到雲端
    input
        :service: 跟雲端溝通的物件，可以從 get_api_service() 獲得
        :fileName: str, 雲端檔案的名稱(須包含附檔名)
        :parent_id: str,  
        :loacl_file: str, 要上傳的檔案 ex: './price.csv'
    output
        :file: dict, 上傳檔案的訊息
    '''

    # 設定儲存雲端位置
    file_metadta = {
        "name":fileName,
        "parents":[parent_id]
    }
    # 取得本地端的檔案
    media = MediaFileUpload(loacl_file)
    file = service.files().create(
                    body=file_metadta,
                    media_body=media
                ).execute()
    return file

def download_metadata(service, fileId, save_file):
    '''
    function
        下載雲端資料至本地
    input
        :service: 跟雲端溝通的物件，可以從 get_api_service() 獲得
        :fileId: str, 
        :save_file: str, 下載的檔案與位置(須包含副檔名) ex: './price.csv'
    output
        None
    '''

    request = service.files().get_media(fileId=fileId)

    with open(save_file, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # print("Download %d%%." % int(status.progress() * 100))


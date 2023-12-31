import os
from . import communication_function
from . import utils

class Download:

    def __init__(self) -> None:

        # 權限設定
        self.creds_and_tokem_path = './'
        self.scopes = ['https://www.googleapis.com/auth/drive']

        # 初始設定
        self.service = None

    def get_service(self):
        '''
        取得 google drive api 最基礎的物件
        '''
        self.service = communication_function.get_api_service(
            SCOPES=self.scopes,
            creds_and_tokem_path=self.creds_and_tokem_path
        )

    def download_file(self, cloud_file_id:str, save_file:str) -> None:
        '''
        功能:
            儲存單一檔案
        輸入:
            :cloud_file_id: 雲端檔案 id
            :save_file: 儲存檔案的路徑名稱

        '''

        print(f'-- 下載 save_file={save_file} , cloud_file_id={cloud_file_id}')
        if not os.path.isfile(save_file):
            communication_function.download_metadata(self.service, fileId=cloud_file_id, save_file=save_file)
            print('-- (成功)')
        else:
            print('-- (失敗) 檔案已經存在')

    def download_files(self, files:list, save_folder:str) -> None:
        '''
        功能:
            下載多個檔案
        輸入:
            :files: 雲端檔案 id 
                files = [
                    {'id':'XXXX', 'name':'filename.extension'},
                    {'id':'XXXX', 'name':'filename.extension'},
                    ....
                ]
            :save_folder: 儲存檔案的資料夾路徑

        '''
        for file in files:
            basename, fileId = file['name'], file['id']
            save_file = os.path.join(save_folder, basename)
            self.download_file(fileId, save_file)

    def listdir_cloud_folder(self, cloud_folder_id:str) -> list:
        '''
        功能:
            列出雲端資料夾內所有的檔案名稱
        輸入:
            :cloud_folder_id: 雲端資料夾
        輸出:
            :files: 雲端檔案 id 
            
                files = [
                    {'id':'XXXX', 'name':'filename.extension'},
                    {'id':'XXXX', 'name':'filename.extension'},
                    ....
                ]
        '''

        query = f"'{cloud_folder_id}' in parents"
        files = communication_function.query_metadata(service=self.service, fields='id, name', query=query)

        return files
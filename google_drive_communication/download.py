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


    def search_files_that_are_in_cloud_folder_but_notin_local_folder(self, local_folder_path:str, cloud_folder_id:str) -> list:
        '''
        功能:
            為了不要重複下載內容所需要的功能，尋找本地沒有但雲端有的檔案
        輸入:
            :local_folder_path: 下載資料夾路徑
            :cloud_folder_id: 對應雲端資料夾 id

        輸出:
            files = [
                {'id':'XXXX', 'name':'filename.extension'},
                {'id':'XXXX', 'name':'filename.extension'},
                ....
            ]
        '''

        # 判斷是否有資料夾，沒有的話就創建
        utils.create_folder(local_folder_path)

        # 取得本地已經有哪些檔案
        print(f'-- 開始搜尋 {local_folder_path} 本地檔案')
        existing_file_names = os.listdir(local_folder_path)
        print(f'-- 完成，共有 {len(existing_file_names)} 個檔案')
        # 搜尋端檔案
        print(f'-- 開始搜尋 {local_folder_path} 對應雲端檔案, id={cloud_folder_id}')
        query = f"'{cloud_folder_id}' in parents"
        cloud_files = communication_function.query_metadata(service=self.service, fields='id, name', query=query)
        # 篩選檔案
        # 找到在雲端不在本地檔案
        files = [file for file in cloud_files if file['name'] not in existing_file_names]

        return files

    def download_file(cloud_file_id:str, save_file:str) -> None:
        '''
        功能:
            儲存單一檔案
        輸入:
            :cloud_file_id: 雲端檔案 id
            :save_file: 儲存檔案的路徑名稱

        '''

        print(f'-- 下載 save_file={save_file} , cloud_file_id={cloud_file_id}')
        if os.path.exists(save_file):
            print('-- (成功)')
            communication_function.download_metadata(self.service, fileId=file_id, save_file=save_file)
        else:
            print('-- (失敗) 檔案已經存在')


    def download_files(files:list, save_folder:str) -> None:
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





    # def search_and_download_files_in_folder(self, download_folder_path, cloud_folder_id, start, end) -> None:
    #     '''
    #     功能:
    #         對於每個資料夾跟雲端比對與下載(每一類的資料再資料夾的格式都為:日期.csv)
    #     輸入:
    #         :download_folder_path: str, 下載資料夾路徑
    #         :cloud_folder_id: str, 對應雲端資料夾 id
    #         :start: str, 日期 ex: 2020-01-01
    #         :end: str, 日期 ex: 2020-01-01

    #     '''

    #     # 判斷是否有資料夾，沒有的話就創建
    #     utils.create_folder(download_folder_path)

    #     # 取得本地已經有哪些檔案
    #     print(f'-- 開始搜尋 {download_folder_path} 本地檔案')
    #     existing_file_names = os.listdir(download_folder_path)
    #     print(f'-- 完成，共有 {len(existing_file_names)} 個檔案')
    #     # 搜尋端檔案
    #     print(f'-- 開始搜尋 {download_folder_path} 對應雲端檔案, id={cloud_folder_id}')
    #     query = f"'{cloud_folder_id}' in parents"
    #     cloud_files = communication_function.query_metadata(service=self.service, fields='id, name', query=query)
    #     # 篩選檔案
    #     # 找到在雲端不在本地檔案，並下載
    #     download_files = [file for file in cloud_files if file['name'] not in existing_file_names]
    #     # 找到限度內的日期
    #     download_files = [file for file in download_files if file['name'].split('.')[0]>=start]
    #     download_files = [file for file in download_files if file['name'].split('.')[0]<=end]

    #     download_file_names = [file['name'] for file in download_files]
    #     max_date = max(download_file_names, key=lambda file:file.split('.')[0]) if len(download_file_names)>0 else None
    #     min_date = min(download_file_names, key=lambda file:file.split('.')[0]) if len(download_file_names)>0 else None

    #     print(f'-- 完成，雲端共有 {len(cloud_files)} 個檔案，滿足日期規範檔案且需要額外下載共有 {len(download_files)} 個檔案 ({min_date}~{max_date})')

    #     print(f'-- 開始下載 {download_folder_path}')
    #     download_files = sorted(download_files, key= lambda file:file['name'].split('.')[0])
    #     for file in download_files:
    #         file_id = file['id']
    #         fileName = file['name']
    #         save_file = os.path.join(download_folder_path,fileName)
    #         print(f'-- 下載 {download_folder_path} - {fileName}')
    #         ###
    #         ### 2023-02-12
    #         ### 好像有時候跟google drive連結斷的時候，
    #         ### 檔案會被先被創建在資料夾中，size=0，資料還沒被下載
    #         ### 之後 refresh_token 後，會以為這個檔案存在，不會更新
    #         communication_function.download_metadata(self.service, fileId=file_id, save_file=save_file)
    #     print(f'-- 完成')



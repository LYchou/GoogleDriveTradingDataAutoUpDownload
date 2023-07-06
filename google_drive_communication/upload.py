import enum
import os
from . import communication_function


class Upload:

    def __init__(self) -> None:

        # 模式設定，決定可以執行的權限
        self.mode = Mode.read

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

    def update_file(self, fileName, loacl_file, parent_folder_id):
        '''
        上傳特定檔案(必須雲端沒有相同的檔案)
        '''

        if self.mode not in [Mode.update, Mode.override]:
            print('-- update_file ({loacl_file}) 失敗，需要把 brain.mode 設定為 Mode.update or Mode.override')
            return None


        # 取得該folder下有哪些檔案名稱
        query = f"'{parent_folder_id}' in parents"
        cloud_files = communication_function.query_metadata(
            service=self.service, 
            fields='id, name, mimeType, parents, createdTime, modifiedTime', 
            query=query
        )
        cloud_file_names = [Dict['name'] for Dict in cloud_files['files']]

        if self.mode==Mode.update:
        
            # 先確定雲端上沒有相同檔案
            if fileName in cloud_file_names:
                print(f'-- update_file ({loacl_file}) 完成，雲端已有檔案不另外上傳')
                return None
            else:
                # 如果沒有 -> 上傳
                upload_file_respond_dict = communication_function.upload_file(
                        service=self.service, fileName=fileName, parent_id=parent_folder_id, loacl_file=loacl_file
                    )
                print(f'-- update_file ({loacl_file}) 完成')
                return upload_file_respond_dict

        elif self.mode==Mode.override:

            # 移除
            if fileName in cloud_file_names:
                file = [file for file in cloud_files if file==fileName][0]
                fileId = file['id']
                self.delete_file(fileId)

            # 上傳
            upload_file_respond_dict = communication_function.upload_file(
                        service=self.service, fileName=fileName, parent_id=parent_folder_id, loacl_file=loacl_file
                    )
            print(f'-- update_file ({loacl_file}) 完成')
            return upload_file_respond_dict

    def delete_file(self, fileId):
        if self.mode in [Mode.delete, Mode.override]:
            communication_function.delete_metadata(self.service, fileId)

    def upload_files_in_folder(self, local_folder_path, cloud_folder_id):
        '''
        上傳資料夾中所有雲端沒有的檔案
        '''

        if self.mode!=Mode.update:
            print('-- update_all_files 失敗，需要把 brain.mode 設定為 Mode.update')
            return

        if self.mode==Mode.update:
            # 搜尋端檔案
            print(f'-- 開始搜尋 {local_folder_path} 對應雲端檔案, id={cloud_folder_id}')
            query = f"'{cloud_folder_id}' in parents"
            cloud_files = communication_function.query_metadata(service=self.service, fields='id, name', query=query)
            cloud_file_names = [Dict['name'] for Dict in cloud_files]
            print(f'-- 完成，雲端共有 {len(cloud_file_names)} 個檔案')
            # 尋找本地端的檔案
            print(f'-- 開始搜尋 {local_folder_path} 本地檔案')
            local_file_names = sorted(os.listdir(local_folder_path))
            print(f'-- 完成，本地共有 {len(local_file_names)} 個檔案')
            # 對比出雲端沒有本地有的檔案
            upload_file_names = list(set(local_file_names)-set(cloud_file_names))
            # 確保檔案都是 csv
            upload_file_names = [file_name for file_name in upload_file_names if 'csv' in file_name] 
            max_date = max(upload_file_names, key=lambda file:file.split('.')[0]) if len(upload_file_names)>0 else None
            min_date = min(upload_file_names, key=lambda file:file.split('.')[0]) if len(upload_file_names)>0 else None
            print(f'-- 經過對比，需要上傳的檔案有 {len(upload_file_names)} 個檔案 ({min_date}~{max_date})')
            print('-- 開始上傳')
            for fileName in sorted(upload_file_names):
                file = os.path.join(local_folder_path,fileName)
                # 上傳檔案
                print(f'-- 上傳 {local_folder_path} - {fileName}')
                upload_file_respond_dict = communication_function.upload_file(
                    service=self.service, fileName=fileName, parent_id=cloud_folder_id, loacl_file=file
                )
                print('-- 成功')



class Mode(enum.Enum):
    '''
    權限:小->大

    read - update - delete - override
    '''
    read = 0
    update = 1
    override = 2 # 先把相同名稱的檔案刪除，在上傳檔案。
    delete = 3


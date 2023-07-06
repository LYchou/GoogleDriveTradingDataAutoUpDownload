import os


def create_folder(folder_path):
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
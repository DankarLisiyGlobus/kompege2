import os
import shutil


def copy(path1: str, path2: str):
    if os.path.isdir(path1):
        shutil.copytree(path1, path2, dirs_exist_ok=True)
    else:
        shutil.copy2(path1, path2)

def delete_temp():
    temp_path = "temp"
    if os.path.isdir(temp_path):
        shutil.rmtree(temp_path)
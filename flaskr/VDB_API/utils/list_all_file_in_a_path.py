import os


def list_all_files(
    path="/home/n66104571/AutoReply-LineBotAssistant/flaskr/VDB_API/docs",
):
    """
    列出指定路徑下的所有文件和資料夾
    """
    files_names = [path + "/" + i for i in os.listdir(path)]
    print(files_names)

    return files_names


if __name__ == "__main__":
    list_all_files()

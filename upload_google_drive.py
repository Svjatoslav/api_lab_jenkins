from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def gogle_auth():
    gauth = GoogleAuth()

    #пробуем загрузить сохраненные данные о пользователе, чтобы не проходить ручную аутентификацию
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # входим, если не вошли по сохраненным данным
        gauth.GetFlow()
        gauth.flow.params.update({'access_type': 'offline'})
        gauth.flow.params.update({'approval_prompt': 'force'})

        gauth.LocalWebserverAuth()

    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    # сохраняем пользовательские данных для последующих автоматических аутентификаций
    gauth.SaveCredentialsFile("mycreds.txt")
    return gauth

def another_way(folderName, folderName_create):
    gauth = gogle_auth()
    upload_file_in_specific_folder(folderName,folderName_create, gauth=gauth)


#итерируемся по каталогам и ищем нужный
def upload_file_on_drive(user_id, project_name,file_name):

    gauth  = gogle_auth()
    drive = GoogleDrive(gauth)
    fileID = ''
    fileList = drive.ListFile({'q': f"'root' in parents and trashed=false"}).GetList()
    for file in fileList:
        if (file['title'] == f"test_api_bot"):
            fileID = file['id']
            break
    str = "\'" + fileID + "\'" + " in parents and trashed=false"

    file_list = drive.ListFile({'q': str}).GetList()
    for file in file_list:
        if (file['title'] == f"{user_id}"):
            fileID = file['id']
            break
    str = "\'" + fileID + "\'" + " in parents and trashed=false"

    file_list = drive.ListFile({'q': str}).GetList()
    for file in file_list:
        if (file['title'] == f"{project_name}"):
            print(file['title'])
            fileID = file['id']
            file1 = drive.CreateFile({'parents': [{'id': fileID}]})
            file1.SetContentFile(file_name)
            file1.Upload()

            print('УРАААА!!!!')
            break

#создаем папку
def upload_file_in_specific_folder(folderName,folderName_create, gauth):
    drive = GoogleDrive(gauth)
    folders = drive.ListFile(
        {
            'q': "title='" + folderName + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
    for folder in folders:
        if folder['title'] == folderName:
            create_folder(folder['id'], folderName_create, drive)


def create_folder(folder_id, folderName,drive):
    file_metadata = {
        'title': folderName,
        'parents': [{'id': folder_id}], #parent folder
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive.CreateFile(file_metadata)
    folder.Upload()


#список файлов в текущем проекте
def get_list_of_current_project_files(user_id, project_name):
    gauth = gogle_auth()
    drive = GoogleDrive(gauth)
    fileID = ''
    fileList = drive.ListFile({'q': f"'root' in parents and trashed=false"}).GetList()
    for file in fileList:
        if (file['title'] == f"test_api_bot"):
            fileID = file['id']
            break
    str = "\'" + fileID + "\'" + " in parents and trashed=false"

    file_list = drive.ListFile({'q': str}).GetList()
    for file in file_list:
        if (file['title'] == f"{user_id}"):
            fileID = file['id']
            break
    str = "\'" + fileID + "\'" + " in parents and trashed=false"

    file_list = drive.ListFile({'q': str}).GetList()
    for file in file_list:
        if (file['title'] == f"{project_name}"):
            fileID = file['id']
            break
    str = "\'" + fileID + "\'" + " in parents and trashed=false"

    file_list = drive.ListFile({'q': str}).GetList()
    return file_list





def delete_files_from_google_disk(file_id):
    gauth = gogle_auth()
    drive = GoogleDrive(gauth)
    file1 = drive.CreateFile({'id': file_id})
    file1.Trash()  # убираем файл в карзину


def main():
    pass


if __name__ == '__main__':
    gogle_auth()
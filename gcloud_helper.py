import os


def upload_file(file_name, blob_name, bucket):
    try:
        blob = bucket.blob(blob_name)
        [print(item) for item in dir(blob)]
        blob.upload_from_filename(file_name)
    except Exception as e:
        print(e)
        return False


def download_file(file_name, blob_name, bucket):
    try:
        blob = bucket.blob(blob_name)
        blob.download_to_filename(file_name)
    except Exception as e:
        print(e)
        return False


def delete_file(blob_name, bucket):
    try:
        blob = bucket.blob(blob_name)
        blob.delete()
    except Exception as e:
        print(e)
        return False


def download_all(bucket):
    all_files = bucket.list_blobs()
    for file in all_files:
        create_missing_directory(file.name, prefix="../")
        download_file("../" + file.name, file.name, bucket)


def create_missing_directory(filepath, prefix=""):
    directory_from_index = filepath.find("/")
    if directory_from_index == -1:
        return

    directory_name = filepath[:directory_from_index]
    filepath = filepath[directory_from_index + 1:]

    if filepath == "":
        return
    if not os.path.exists(prefix + directory_name):
        os.mkdir(prefix + directory_name)

    create_missing_directory(filepath, prefix=prefix + directory_name + "/")

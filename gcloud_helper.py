import os
import crcmod
import base64


def upload_file(file_name, blob_name, bucket):
    try:
        blob = bucket.blob(blob_name)
        [print(item) for item in dir(blob)]
        blob.upload_from_filename(file_name)
    except Exception as e:
        print(f"following error occurred when uploading {file_name} as {blob_name} in {bucket.name} bucket")
        print(e)
        return False


def download_file(file_name, blob_name, bucket):
    try:
        blob = bucket.blob(blob_name)
        blob.download_to_filename(file_name)
    except Exception as e:
        print(f"following error occurred when downloading {blob_name} in {bucket.name} bucket as {file_name} ")
        print(e)
        return False


def delete_file(blob_name, bucket):
    try:
        blob = bucket.blob(blob_name)
        blob.delete()
    except Exception as e:
        print(f"following error occurred when deleting {blob_name} in {bucket.name}")
        print(e)
        return False


def download_all(bucket):
    all_files = bucket.list_blobs()
    for file in all_files:
        create_missing_directory(file.name, prefix="../")
        download_file("../" + file.name, file.name, bucket)


def create_missing_directory(filepath, prefix=""):
    """
    Do not use this method unless you fully understand it.
    It is meant as a helper method, not to be used in other code.
    :param filepath:
    :param prefix:
    :return:
    """
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


def is_file_different(file_name, blob_name, bucket):
    blob = bucket.get_bucket(blob_name)
    with open(file_name) as file:
        file_bytes = file.read()
        crc32c = crcmod.predefined.Crc('crc-32c')
        crc32c.update(file_bytes)

        return blob.crc32c == base64.b64encode(crc32c.digest()).decode('utf-8')

import filemanaging
import os


def upload_file(file_name, blob_name, bucket):
    try:
        blob = bucket.blob(blob_name)
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


def download_all(bucket, working_dir):
    all_files = bucket.list_blobs()
    for file in all_files:
        filemanaging.create_missing_directory(file.name, prefix=working_dir)
        download_file(working_dir + file.name, file.name, bucket)


def is_file_different(file_name, blob_name, bucket):
    blob = bucket.get_blob(blob_name)
    return blob.crc32c != filemanaging.get_crc32c(file_name)


def find_new_and_updated_cloud_files(working_directory_path, bucket, ignores=[]):
    pulled_files = []
    blobs = bucket.list_blobs()
    for blob in blobs:
        if blob.name in ignores:
            continue
        if not os.path.exists(working_directory_path + filemanaging.convert_to_windows_path(blob.name)) or is_file_different(
                working_directory_path + filemanaging.convert_to_windows_path(blob.name),
                blob.name, bucket):
            pulled_files.append(blob.name)
    return pulled_files


def find_deleted_cloud_files(working_directory_path, bucket, ignores=[]):
    items = os.listdir(working_directory_path)
    deleted_items = []
    for item in items:
        if item in ignores:
            continue
        if os.path.isdir(working_directory_path + "\\" + item):
            deleted_items += find_deleted_cloud_files_recursive(working_directory_path, item, bucket, ignores=ignores)
            continue
        if not bucket.blob(item).exists():
            deleted_items.append(item)
    return deleted_items


def find_deleted_cloud_files_recursive(working_directory_path, pre, bucket, ignores):
    items = os.listdir(working_directory_path + "\\" + filemanaging.convert_to_windows_path(pre))
    deleted_items = []
    for item in items:
        if filemanaging.convert_to_windows_path(pre) + "\\" + item in ignores:
            continue
        if os.path.isdir(working_directory_path + "\\" + filemanaging.convert_to_windows_path(pre) + "\\" + item):
            deleted_items += find_deleted_cloud_files_recursive(working_directory_path, pre + "/" + item, bucket, ignores=ignores)
            continue
        if not bucket.blob(pre + "/" + item).exists():
            deleted_items.append(pre + "/" + item)
    return deleted_items

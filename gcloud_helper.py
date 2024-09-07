import filemanaging
import os

import module_helper


def upload_file(file_name, blob_name, bucket):
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_name)
        return True


def upload_from_string(data, blob_name, bucket):
    try:
        blob = bucket.blob(blob_name)
        blob.upload_from_string(data)
        return True
    except Exception as e:
        module_helper.log(f"following error occurred when backing up {blob_name} into {bucket}")
        module_helper.log(e)
        return False


def download_file(file_name, blob_name, bucket):
    try:
        blob = bucket.blob(blob_name)
        blob.download_to_filename(file_name)
        return True
    except Exception as e:
        module_helper.log(f"following error occurred when downloading {blob_name} in {bucket.name} bucket as {file_name} ")
        module_helper.log(e)
        return False


def delete_file(blob_name, bucket):
    try:
        blob = bucket.blob(blob_name)
        blob.delete()
        return True
    except Exception as e:
        module_helper.log(f"following error occurred when deleting {blob_name} in {bucket.name}")
        module_helper.log(e)
        return False


def download_all(bucket, working_dir):
    all_files = bucket.list_blobs()
    for file in all_files:
        filemanaging.create_missing_directory(file.name, prefix=working_dir)
        download_file(working_dir + file.name, file.name, bucket)


def is_file_different(file_name, blob_name, bucket):
    blob = bucket.get_blob(blob_name)
    return blob.crc32c != filemanaging.get_crc32c(file_name)


def are_blobs_different(blob1, blob2):
    return blob1.crc32c != blob2.crc32c


def find_new_and_updated_cloud_files(working_directory_path, bucket, ignores=[]):
    pulled_files = []
    blobs = bucket.list_blobs()
    for blob in blobs:
        if blob.name in ignores:
            continue
        if not os.path.exists(working_directory_path + blob.name) or is_file_different(
                working_directory_path + blob.name,
                blob.name, bucket):
            pulled_files.append(blob.name)
    return pulled_files


def find_deleted_cloud_files(working_directory_path, bucket, ignores=[]):
    items = os.listdir(working_directory_path)
    deleted_items = []
    for item in items:
        if item in ignores:
            continue
        if os.path.isdir(working_directory_path + "/" + item):
            deleted_items += find_deleted_cloud_files_recursive(working_directory_path, item, bucket, ignores=ignores)
            continue
        if not bucket.blob(item).exists():
            deleted_items.append(item)
    return deleted_items


def find_deleted_cloud_files_recursive(working_directory_path, pre, bucket, ignores):
    items = os.listdir(working_directory_path + "/" + pre)
    deleted_items = []
    for item in items:
        if pre + "/" + item in ignores:
            continue
        if os.path.isdir(working_directory_path + "/" + pre + "/" + item):
            deleted_items += find_deleted_cloud_files_recursive(working_directory_path, pre + "/" + item, bucket, ignores=ignores)
            continue
        if not bucket.blob(pre + "/" + item).exists():
            deleted_items.append(pre + "/" + item)
    return deleted_items


def backup(bucket, backup_bucket, ignores):
    pulled_blobs = find_new_and_updated_backup_files(bucket, backup_bucket, ignores)
    deleted_blobs = find_deleted_backup_files(bucket, backup_bucket, ignores)

    for pulled_blob in pulled_blobs:
        data = pulled_blob.download_as_string()
        upload_from_string(data, pulled_blob.name, backup_bucket)

    for deleted_blob in deleted_blobs:
        delete_file(deleted_blob.name, backup_bucket)


def find_new_and_updated_backup_files(bucket, backup_bucket, ignores):
    pulled_blobs = []
    blobs = bucket.list_blobs()
    for blob in blobs:
        if blob.name in ignores:
            continue
        backup_blob = backup_bucket.blob(blob.name)
        if not backup_blob or are_blobs_different(backup_blob, blob):
            pulled_blobs.append(blob)
    return pulled_blobs


def find_deleted_backup_files(bucket, backup_bucket, ignores):
    deleted_blobs = []
    backup_blobs = backup_bucket.list_blobs()
    for backup_blob in backup_blobs:
        if backup_blob.name in ignores:
            continue
        blob = bucket.blob(backup_blob.name)
        if not blob.exists():
            deleted_blobs.append(backup_blob)
            continue
    return deleted_blobs

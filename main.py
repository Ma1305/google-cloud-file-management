import os
import sys
import filemanaging
import gcloud_helper as cloud

from google.cloud import storage
from filemanaging import ChangeScanner
from config import CREDENTIAL_FILENAME, BUCKET_NAME, IGNORES, USERNAME, OLD_VERSION_DIR_PATH, WORKING_DIR_PATH
from module_helper import Option


def setup():
    pass


def push():
    global change_scanner, my_bucket

    confirmation("push")

    new_files = change_scanner.scan_for_new_files()
    deleted_files = change_scanner.scan_for_deleted_files()
    updated_files = change_scanner.scan_for_updated_files()

    print("New files are: ")
    for item in new_files:
        print(item)
        if item[-1] != "/":
            cloud.upload_file(WORKING_DIR_PATH + item, item, my_bucket)
            filemanaging.copy_file_to(WORKING_DIR_PATH + item, OLD_VERSION_DIR_PATH + item)

    print("Deleted files are: ")
    for item in deleted_files:
        print(item)
        if item[-1] != "/":
            cloud.delete_file(item, my_bucket)
            filemanaging.delete_file(OLD_VERSION_DIR_PATH + item)

    print("Modified files are: ")
    for item in updated_files:
        print(item)
        if item[-1] != "/":
            cloud.upload_file(WORKING_DIR_PATH + item, item, my_bucket)
            filemanaging.copy_file_to(WORKING_DIR_PATH + item, OLD_VERSION_DIR_PATH + item)


def pull():
    global my_bucket

    confirmation("pull")

    pulled_files = cloud.find_new_and_updated_cloud_files(WORKING_DIR_PATH, my_bucket)
    for item in pulled_files:
        filemanaging.create_missing_directory(WORKING_DIR_PATH + "/" + item)
        cloud.download_file(WORKING_DIR_PATH + "/" + item, item, my_bucket)
        pulled_files.append(item)

    deleted_files = cloud.find_deleted_cloud_files(WORKING_DIR_PATH, my_bucket, ignores=IGNORES)
    for item in deleted_files:
        filemanaging.delete_file(WORKING_DIR_PATH + "/" + item)

    # update old version folder
    new_files = change_scanner.scan_for_new_files()
    deleted_files = change_scanner.scan_for_deleted_files()
    updated_files = change_scanner.scan_for_updated_files()

    print("New files are: ")
    for item in new_files:
        print(item)
        if item[-1] != "/":
            filemanaging.copy_file_to(WORKING_DIR_PATH + item, OLD_VERSION_DIR_PATH + item)

    print("Deleted files are: ")
    for item in deleted_files:
        print(item)
        if item[-1] != "/":
            filemanaging.delete_file(OLD_VERSION_DIR_PATH + item)

    print("Modified files are: ")
    for item in updated_files:
        print(item)
        if item[-1] != "/":
            filemanaging.copy_file_to(WORKING_DIR_PATH + item, OLD_VERSION_DIR_PATH + item)


def confirmation(action):
    """
    :return: bool
    """
    response = input(f"Enter yes to confirm that you want to {action}: ")
    if response.lower().strip() == "yes":
        print(f"starting the {action} process\n")
        return
    print(f"canceling the {action} process\n")
    quit()


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIAL_FILENAME
storage_client = storage.Client()
my_bucket = storage_client.get_bucket(BUCKET_NAME)

change_scanner = ChangeScanner(OLD_VERSION_DIR_PATH, WORKING_DIR_PATH, skip_files=IGNORES)

options = [
    Option("setup", "sets up all the important files for tracking the changes", setup,
           warning="DO NOT CALL THIS METHOD UNLESS YOU ARE SETTING UP THE STORAGE AND SCRIPT"),
    Option("push", "uploads only the modified files (new, deleted, and updated files)",
           push,
           warning="RECOMMENDED TO USE WHEN ALL CHANGES ARE DONE, POSSIBILITY OF CONFLICT"),
    Option("pull",
           "download only the files updated since the last download (new, deleted, updates files)",
           pull,
           warning="IF YOU HAVE MADE ANY CHANGES, YOUR CHANGES WILL BE OVERWRITTEN (POSSIBILITY OF CONFLICT)")
]

if len(sys.argv) < 1:
    print("One argument must be passed!")
    print("Available arguments:")
    [print(option.name) for option in options]

if sys.argv[1] not in [option.name for option in options]:
    print("Invalid argument")
    print("Available arguments:")
    [print(option.name) for option in options]

for option in options:
    if option.name == sys.argv[1].lower():
        option.action()

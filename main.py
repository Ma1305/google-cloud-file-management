import datetime
import os
import sys
import filemanaging
import gcloud_helper as cloud

from google.cloud import storage
from filemanaging import ChangeScanner
from config import CREDENTIAL_FILENAME, BUCKET_NAME, IGNORES, USERNAME, OLD_VERSION_DIR_PATH, WORKING_DIR_PATH, LOGS_FOLDER
from module_helper import Option, log


def setup():
    global my_bucket
    fields = [
        "Username",
        "Time",
        "Action",
        "Items",
        "Special Log Message",
    ]
    filemanaging.create_csv("logs.csv", fields)
    filemanaging.append_row_to_csv("logs.csv", [
        USERNAME,
        str(datetime.datetime.now()),
        "Setup",
        "None",
        "Setting up the log information"
    ])
    cloud.upload_file("logs.csv", "logs.csv", my_bucket)
    filemanaging.delete_file("logs.csv")


def push():
    global change_scanner, my_bucket

    log_file_path = LOGS_FOLDER + "/logs-" + datetime.datetime.now()
    confirmation("push", log_file_path)

    new_files = change_scanner.scan_for_new_files()
    deleted_files = change_scanner.scan_for_deleted_files()
    updated_files = change_scanner.scan_for_updated_files()

    cloud.download_file("logs.csv", "logs.csv", my_bucket)

    log("New files are: ", log_file_path)
    new_files_string = ""
    for item in new_files:
        log(item, log_file_path)
        new_files_string += item + "\n"
        if item[-1] != "/":
            if cloud.upload_file(WORKING_DIR_PATH + item, item, my_bucket):
                filemanaging.copy_file_to(WORKING_DIR_PATH + item, OLD_VERSION_DIR_PATH + item)

    if new_files_string != "":
        log("some new files", log_file_path)
        filemanaging.append_row_to_csv("logs.csv", [
            USERNAME,
            str(datetime.datetime.now()),
            "New Files",
            new_files_string,
            "None"
        ])

    log("Deleted files are: ", log_file_path)
    deleted_files_string = ""
    for item in deleted_files:
        log(item, log_file_path)
        deleted_files_string += item + "\n"
        if item[-1] != "/":
            if cloud.delete_file(item, my_bucket):
                filemanaging.delete_file(OLD_VERSION_DIR_PATH + item)

    if deleted_files_string != "":
        log("some deleted files", log_file_path)
        filemanaging.append_row_to_csv("logs.csv", [
            USERNAME,
            str(datetime.datetime.now()),
            "Deleted Files",
            deleted_files_string,
            "None"
        ])

    log("Modified files are: ", log_file_path)
    updated_files_string = ""
    for item in updated_files:
        log(item, log_file_path)
        updated_files_string += item + "\n"
        if item[-1] != "/":
            if cloud.upload_file(WORKING_DIR_PATH + item, item, my_bucket):
                filemanaging.copy_file_to(WORKING_DIR_PATH + item, OLD_VERSION_DIR_PATH + item)

    if updated_files_string != "":
        log("some updated files", log_file_path)
        filemanaging.append_row_to_csv("logs.csv", [
            USERNAME,
            str(datetime.datetime.now()),
            "Updated Files",
            updated_files_string,
            "None"
        ])

    if cloud.is_file_different("logs.csv", "logs.csv", my_bucket):
        log("uploading", log_file_path)
        cloud.upload_file("logs.csv", "logs.csv", my_bucket)

    filemanaging.delete_file("logs.csv")


def pull():
    global my_bucket

    log_file_path = LOGS_FOLDER + "/logs-" + datetime.datetime.now()
    confirmation("pull", log_file_path)

    pulled_files = cloud.find_new_and_updated_cloud_files(WORKING_DIR_PATH, my_bucket, ignores=IGNORES)
    for item in pulled_files:
        log(item, log)
        filemanaging.create_missing_directory(WORKING_DIR_PATH + "/" + item)
        cloud.download_file(WORKING_DIR_PATH + "/" + item, item, my_bucket)

    deleted_files = cloud.find_deleted_cloud_files(WORKING_DIR_PATH, my_bucket, ignores=IGNORES)
    for item in deleted_files:
        filemanaging.delete_file(WORKING_DIR_PATH + "/" + item)

    # update old version folder
    new_files = change_scanner.scan_for_new_files()
    deleted_files = change_scanner.scan_for_deleted_files()
    updated_files = change_scanner.scan_for_updated_files()

    log("New files are: ", log_file_path)
    for item in new_files:
        log(item, log_file_path)
        if item[-1] != "/":
            filemanaging.copy_file_to(WORKING_DIR_PATH + item, OLD_VERSION_DIR_PATH + item)

    log("Deleted files are: ", log_file_path)
    for item in deleted_files:
        log(item, log_file_path)
        if item[-1] != "/":
            filemanaging.delete_file(OLD_VERSION_DIR_PATH + item)

    log("Modified files are: ", log_file_path)
    for item in updated_files:
        log(item, log_file_path)
        if item[-1] != "/":
            filemanaging.copy_file_to(WORKING_DIR_PATH + item, OLD_VERSION_DIR_PATH + item)


def confirmation(action, log_file_path):
    """
    :return: bool
    """
    response = input(f"Enter yes to confirm that you want to {action}: ")
    if response.lower().strip() == "yes":
        log(f"starting the {action} process\n", log_file_path)
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

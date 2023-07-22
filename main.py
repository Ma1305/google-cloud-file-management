import os
import sys

from google.cloud import storage
from gcloud_helper import upload_file, delete_file, download_file, download_all
from filemanaging import ChangeScanner
from config import CREDENTIAL_FILENAME, BUCKET_NAME, IGNORES, USERNAME
from module_helper import Option


def setup():
    pass


def upload_all():
    pass


def download_all():
    pass


def upload_efficient():
    pass


def download_efficient():
    pass


def confirmation():
    """
    :return: bool
    """
    pass


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIAL_FILENAME

storage_client = storage.Client()

my_bucket = storage_client.get_bucket(BUCKET_NAME)

options = [
    Option("setup", "sets up all the important files for tracking the changes", setup,
           warning="DO NOT CALL THIS METHOD UNLESS YOU ARE SETTING UP THE STORAGE AND SCRIPT"),
    Option("upload-all", "uploading all the files from your computer to storage. Overwriting the cloud storage files.",
           upload_all,
           warning="SHOULD BE AVOIDED, UNLESS SETTING UP THE STORAGE"),
    Option("download-all", "downloads all the files from the storage. Overwriting the files on your computer",
           download_all,
           warning="SHOULD BE AVOIDED, UNLESS SETTING UP THE STORAGE ON YOUR COMPUTER"),
    Option("upload-efficient", "uploads only the modified files (new, deleted, and updated files)",
           upload_efficient,
           warning="RECOMMENDED TO USE WHEN ALL CHANGES ARE DONE, POSSIBILITY OF CONFLICT"),
    Option("download-efficient",
           "download only the files updated since the last download (new, deleted, updates files)",
           download_efficient,
           warning="IF YOU HAVE MADE ANY CHANGES, YOUR CHANGES WILL BE OVERWRITTEN (POSSIBILITY OF CONFLICT)")
]

if len(sys.argv) < 1:
    print("One argument must be passed!")
    print("Available arguments:")
    [print(option.name) for option in options]

if sys.argv[0] not in [option.name for option in options]:
    print("Invalid argument")
    print("Available arguments:")
    [print(option.name) for option in options]

for option in options:
    if option.name == sys.argv[0].lower():
        option.action()

import os
from google.cloud import storage
from gcloud_helper import upload_file, delete_file, download_file, download_all
from filemanaging import ChangeScanner
from config import CREDENTIAL_FILENAME, BUCKET_NAME

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIAL_FILENAME

storage_client = storage.Client()

my_bucket = storage_client.get_bucket(BUCKET_NAME)

ignores = [
    "scripts",
    "prev_version",
    "venv",
    ".idea"
]

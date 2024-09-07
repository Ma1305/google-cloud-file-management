import sys
import unittest
import os
from mock import patch

os.chdir("../")
import config
import test_config

config.CREDENTIAL_FILENAME = test_config.CREDENTIAL_FILENAME
config.BUCKET_NAME = test_config.BUCKET_NAME
config.BACKUP_BUCKET_NAME = test_config.BACKUP_BUCKET_NAME
config.USERNAME = test_config.USERNAME
config.WORKING_DIR_PATH = test_config.WORKING_DIR_PATH
config.OLD_VERSION_DIR_PATH = test_config.OLD_VERSION_DIR_PATH
config.IGNORES = test_config.IGNORES
config.LOGS_FOLDER = test_config.LOGS_FOLDER
config.AUTO_BACKUP = test_config.AUTO_BACKUP

sys.argv.append("")
from main import my_bucket, my_backup_bucket, push, pull, backup, setup
import main


class TestFileManagement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup()

    @patch("main.confirmation", return_value=True)
    def test_upload_when_not_found_in_prev(self, confirmation):
        try:
            os.remove(config.OLD_VERSION_DIR_PATH + "/test_upload.txt")
        except FileNotFoundError:
            pass

        with open(config.WORKING_DIR_PATH + "/test_upload.txt", "w") as file:
            file.write("Hello World!")
        push()

        test_file_blob = my_bucket.blob("test_upload.txt")
        self.assertTrue(test_file_blob.exists())
        self.assertEquals(str(test_file_blob.download_as_text()), "Hello World!")

    @patch("main.confirmation", return_value=True)
    def test_delete_on_cloud_when_only_found_in_prev(self, confirmation):
        try:
            os.remove(config.OLD_VERSION_DIR_PATH + "/test_upload.txt")
        except FileNotFoundError:
            pass

        with open(config.WORKING_DIR_PATH + "/test_upload.txt", "w") as file:
            file.write("Hello World!")
        push()

        try:
            os.remove(config.WORKING_DIR_PATH + "/test_upload.txt")
        except FileNotFoundError:
            pass
        push()

        test_file_blob = my_bucket.blob("test_upload.txt")
        self.assertFalse(test_file_blob.exists())

    @patch("main.confirmation", return_value=True)
    def test_delete_locally_when_found_in_prev(self, confirmation):
        try:
            os.remove(config.OLD_VERSION_DIR_PATH + "/test_upload.txt")
        except FileNotFoundError:
            pass

        with open(config.WORKING_DIR_PATH + "/test_upload.txt", "w") as file:
            file.write("Hello World!")

        with open(config.OLD_VERSION_DIR_PATH + "/test_upload.txt", "w") as file:
            file.write("Hello World!")

        pull()

        file_exists = os.path.exists(config.WORKING_DIR_PATH + "/test_upload.txt")
        self.assertFalse(file_exists)

    @patch("main.confirmation", return_value=True)
    def test_should_not_delete_locally_when_found_not_found_in_prev(self, confirmation):
        try:
            os.remove(config.OLD_VERSION_DIR_PATH + "/test_upload.txt")
        except FileNotFoundError:
            pass

        with open(config.WORKING_DIR_PATH + "/test_upload.txt", "w") as file:
            file.write("Hello World!")

        pull()

        file_exists = os.path.exists(config.WORKING_DIR_PATH + "/test_upload.txt")
        self.assertTrue(file_exists)

    @patch("main.confirmation", return_value=True)
    def test_update_on_cloud(self, confirmation):
        try:
            os.remove(config.OLD_VERSION_DIR_PATH + "/test_upload.txt")
        except FileNotFoundError:
            pass

        with open(config.WORKING_DIR_PATH + "/test_upload.txt", "w") as file:
            file.write("Hello World!")

        push()

        with open(config.WORKING_DIR_PATH + "/test_upload.txt", "a") as file:
            file.write("\nUpdating the file")

        push()

        test_file_blob = my_bucket.blob("test_upload.txt")
        self.assertTrue(test_file_blob.exists())
        self.assertEquals(str(test_file_blob.download_as_text()), "Hello World!\r\nUpdating the file")

    @patch("main.confirmation", return_value=True)
    def test_update_locally(self, confirmation):
        try:
            os.remove(config.OLD_VERSION_DIR_PATH + "/test_upload.txt")
        except FileNotFoundError:
            pass

        with open(config.WORKING_DIR_PATH + "/test_upload.txt", "w") as file:
            file.write("Hello World!")

        push()

        with open(config.WORKING_DIR_PATH + "/test_upload.txt", "w") as file:
            file.write("Old version of the file")

        pull()

        test_file_blob = my_bucket.blob("test_upload.txt")
        self.assertTrue(test_file_blob.exists())
        self.assertEquals(str(test_file_blob.download_as_text()), "Hello World!")

    @patch("main.confirmation", return_value=True)
    def test_download_locally(self, confirmation):
        try:
            os.remove(config.OLD_VERSION_DIR_PATH + "/test_upload.txt")
        except FileNotFoundError:
            pass

        with open(config.WORKING_DIR_PATH + "/test_upload.txt", "w") as file:
            file.write("Hello World!")

        push()

        os.remove(config.WORKING_DIR_PATH + "/test_upload.txt")

        pull()

        file_exists = os.path.exists(config.WORKING_DIR_PATH + "/test_upload.txt")
        self.assertFalse(file_exists)

    @patch("main.confirmation", return_value=True)
    def test_upload_backup(self, confirmation):
        main.AUTO_BACKUP = True
        try:
            os.remove(config.OLD_VERSION_DIR_PATH + "/test_upload.txt")
        except FileNotFoundError:
            pass

        with open(config.WORKING_DIR_PATH + "/test_upload.txt", "w") as file:
            file.write("Hello World!")
        push()

        with open(config.WORKING_DIR_PATH + "/test_upload.txt", "w") as file:
            file.write("Should only be in the original storage")
        push()

        test_file_blob = my_bucket.blob("test_upload.txt")
        self.assertTrue(test_file_blob.exists())
        self.assertEquals(str(test_file_blob.download_as_text()), "Should only be in the original storage")

        test_file_blob = my_backup_bucket.blob("test_upload.txt")
        self.assertTrue(test_file_blob.exists())
        self.assertEquals(str(test_file_blob.download_as_text()), "Hello World!")

    @patch("main.confirmation", return_value=True)
    def test_update_backup(self, confirmation):
        main.AUTO_BACKUP = True
        try:
            os.remove(config.OLD_VERSION_DIR_PATH + "/test_upload.txt")
        except FileNotFoundError:
            pass

        with open(config.WORKING_DIR_PATH + "/test_upload.txt", "w") as file:
            file.write("Hello World!")
        push()

        with open(config.WORKING_DIR_PATH + "/test_upload.txt", "w") as file:
            file.write("Updated!")
        push()

        with open(config.WORKING_DIR_PATH + "/test_upload.txt", "w") as file:
            file.write("Should only be in the original storage")
        push()

        test_file_blob = my_bucket.blob("test_upload.txt")
        self.assertTrue(test_file_blob.exists())
        self.assertEquals(str(test_file_blob.download_as_text()), "Should only be in the original storage")

        test_file_blob = my_backup_bucket.blob("test_upload.txt")
        self.assertTrue(test_file_blob.exists())
        self.assertEquals(str(test_file_blob.download_as_text()), "Updated!")

    @patch("main.confirmation", return_value=True)
    def test_delete_backup(self, confirmation):
        main.AUTO_BACKUP = True
        try:
            os.remove(config.OLD_VERSION_DIR_PATH + "/test_upload.txt")
        except FileNotFoundError:
            pass

        with open(config.WORKING_DIR_PATH + "/test_upload.txt", "w") as file:
            file.write("Hello World!")
        push()

        os.remove(config.WORKING_DIR_PATH + "/test_upload.txt")
        push()

        with open(config.WORKING_DIR_PATH + "/test_upload.txt", "w") as file:
            file.write("Should only be in the original storage")
        push()

        test_file_blob = my_bucket.blob("test_upload.txt")
        self.assertTrue(test_file_blob.exists())
        self.assertEquals(str(test_file_blob.download_as_text()), "Should only be in the original storage")

        test_file_blob = my_backup_bucket.blob("test_upload.txt")
        self.assertFalse(test_file_blob.exists())

    def tearDown(self):
        blobs = my_bucket.list_blobs()
        for blob in blobs:
            if blob.name not in config.IGNORES:
                blob.delete()

        blobs = my_backup_bucket.list_blobs()
        for blob in blobs:
            if blob.name not in config.IGNORES:
                blob.delete()

    def setUp(self):
        blobs = my_bucket.list_blobs()
        for blob in blobs:
            if blob.name not in config.IGNORES:
                blob.delete()

        blobs = my_backup_bucket.list_blobs()
        for blob in blobs:
            if blob.name not in config.IGNORES:
                blob.delete()


if __name__ == '__main__':
    unittest.main()

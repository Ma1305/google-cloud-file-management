import os
import crcmod
import base64
import shutil
import csv


class ChangeScanner:
    def __init__(self, old_version_path, new_version_path, skip_files=[]):
        if skip_files is None:
            skip_files = []
        self.old_version_path = old_version_path
        self.new_version_path = new_version_path
        self.skip_files = skip_files

    def scan_for_new_files(self):
        items = os.listdir(self.create_new_path_names())
        new_items = []
        for item in items:
            if item in self.skip_files:
                continue
            if not os.path.exists(self.create_old_path_names() + "/" + item):
                add_on = ""
                if os.path.isdir(self.create_new_path_names() + "/" + item):
                    add_on = "/"
                new_items.append(item + add_on)
            if os.path.isdir(self.create_new_path_names() + "/" + item):
                new_items += self.scan_for_new_files_recursive(item)
        return new_items

    def scan_for_new_files_recursive(self, pre):
        items = os.listdir(self.create_new_path_names() + "/" + pre)
        new_items = []
        for item in items:
            if pre + "/" + item in self.skip_files:
                continue
            if not os.path.exists(self.create_old_path_names() + "/" + pre + "/" + item):
                add_on = ""
                if os.path.isdir(self.create_new_path_names() + "/" + pre + "/" + item):
                    add_on = "/"
                new_items.append(pre + "/" + item + add_on)
            if os.path.isdir(self.create_new_path_names() + "/" + pre + "/" + item):
                new_items += self.scan_for_new_files_recursive(pre + "/" + item)

        return new_items

    def scan_for_deleted_files(self):
        items = os.listdir(self.create_old_path_names())
        deleted_items = []
        for item in items:
            if not os.path.exists(self.create_new_path_names() + "/" + item):
                add_on = ""
                if os.path.isdir(self.create_old_path_names() + "/" + item):
                    add_on = "/"
                deleted_items.append(item + add_on)
            if os.path.isdir(self.create_old_path_names() + "/" + item):
                deleted_items += self.scan_for_deleted_files_recursive(item)
        return deleted_items

    def scan_for_deleted_files_recursive(self, pre):
        items = os.listdir(self.create_old_path_names() + "/" + pre)
        deleted_items = []
        for item in items:
            if not os.path.exists(self.create_new_path_names() + "/" + pre + "/" + item):
                add_on = ""
                if os.path.isdir(self.create_old_path_names() + "/" + item):
                    add_on = "/"
                deleted_items.append(pre + "/" + item + add_on)
            if os.path.isdir(self.create_old_path_names() + "/" + pre + "/" + item):
                deleted_items += self.scan_for_deleted_files_recursive(pre + "/" + item)
        return deleted_items

    def scan_for_updated_files(self):
        items = os.listdir(self.create_old_path_names())
        update_items = []
        for item in items:
            if not os.path.exists(self.create_new_path_names() + "/" + item):
                continue
            if item in self.skip_files:
                continue
            if os.path.isdir(self.create_old_path_names() + "/" + item):
                update_items += self.scan_for_updated_files_recursive(item)
                continue
            if get_crc32c(self.create_old_path_names() + "/" + item) != \
                    get_crc32c(self.create_new_path_names() + "/" + item):
                update_items.append(item)
        return update_items

    def scan_for_updated_files_recursive(self, pre):
        items = os.listdir(self.create_old_path_names() + "/" + pre)
        update_items = []
        for item in items:
            if not os.path.exists(self.create_new_path_names() + "/" + pre + "/" + item):
                continue
            if pre + "/" + item in self.skip_files:
                continue
            if os.path.isdir(self.create_old_path_names() + "/" + pre + "/" + item):
                update_items += self.scan_for_updated_files_recursive(pre + "/" + item)
                continue
            if get_crc32c(self.create_old_path_names() + "/" + pre + "/" + item) != \
                    get_crc32c(self.create_new_path_names() + "/" + pre + "/" + item):
                update_items.append(pre + "/" + item)
        return update_items

    def create_new_path_names(self):
        return self.new_version_path

    def create_old_path_names(self):
        return self.old_version_path


def get_crc32c(filename):
    with open(filename, "rb") as file:
        file_bytes = file.read()
        crc32c = crcmod.predefined.Crc('crc-32c')
        crc32c.update(file_bytes)

        return base64.b64encode(crc32c.digest()).decode('utf-8')


def copy_file_to(original_file_path, new_file_path):
    create_missing_directory(new_file_path)
    shutil.copy2(original_file_path, new_file_path)


def delete_file(file_path):
    os.remove(file_path)


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
    if not os.path.exists(prefix + directory_name) and directory_name != "":
        os.mkdir(prefix + directory_name)

    create_missing_directory(filepath, prefix=prefix + directory_name + "/")


def create_csv(filename, fields):
    append_row_to_csv(filename, fields)


def append_row_to_csv(filename, row):
    with open(filename, 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(row)

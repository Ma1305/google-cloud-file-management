import os


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
                deleted_items += self.scan_for_deleted_files_recursive(item)
        return deleted_items

    def scan_for_updated_files(self):
        return []

    def scan_for_updated_files_recursive(self, pre):
        return []

    def create_new_path_names(self):
        return os.path.dirname(__file__) + "/" + self.new_version_path

    def create_old_path_names(self):
        return os.path.dirname(__file__) + "/" + self.old_version_path

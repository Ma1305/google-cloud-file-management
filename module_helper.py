class Option:
    def __init__(self, name, description, action, warning=""):
        self.name = name
        self.description = description
        self.warning = warning
        self.action = action


def log(message, log_file_path):
    with open(log_file_path, "a") as log_file:
        log_file.write(message)
    print(message)

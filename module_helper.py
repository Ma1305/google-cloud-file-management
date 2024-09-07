class Option:
    def __init__(self, name, description, action, warning=""):
        self.name = name
        self.description = description
        self.warning = warning
        self.action = action


def log(message):
    global log_file_path
    create_file = False
    try:
        with open(log_file_path, "a") as log_file:
            log_file.write(message + "\n")
    except OSError:
        create_file = True
    if create_file:
        with open(log_file_path, "w") as log_file:
            log_file.write(message + "\n")
    print(message)


log_file_path = ""

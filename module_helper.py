class Option:
    def __init__(self, name, description, action, warning=""):
        self.name = name
        self.description = description
        self.warning = warning
        self.action = action

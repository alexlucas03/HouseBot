class Admin:
    def __init__(self, name, password):
        self.name = name
        self.password = password

    def to_dict(self):
        return {
            'name': self.name,
            'password': self.password
        }

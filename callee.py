class Callee:
    def __init__(self, name, num, tag):
        self.name = name
        self.num = num
        self.tag = tag

    def to_dict(self):
        return {
            'name': self.name,
            'num': self.num,
            'tag': self.tag
        }
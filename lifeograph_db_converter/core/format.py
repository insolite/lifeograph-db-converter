

class Format:

    def decode(self, data):
        raise NotImplementedError

    def encode(self, diary):
        raise NotImplementedError

    def parse(self, data):
        return data

    def dump(self, data):
        return data

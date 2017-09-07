import json

from lifeograph_db_converter import Diary, Format


class JsonFormat(Format):

    def decode(self, data):
        # TODO: deep copy
        return Diary(**data)

    def encode(self, diary):
        # TODO: deep copy
        return diary.__dict__.copy()

    def parse(self, data):
        return json.loads(data)

    def dump(self, data):
        return json.dumps(data)

import os
import json

from flask import current_app


class Resource:

    @staticmethod
    def path(name):
        return os.path.join(current_app.root_path, 'storage/resources', name)

    @staticmethod
    def load(name):
        path = Resource.path(name)
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        content = open('{}'.format(path), 'r', encoding='UTF-8').read()
        return str(content)

    @staticmethod
    def load_json(filename):
        if os.path.isfile(filename):
            path = filename
        else:
            path = Resource.path(filename)
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        with open(path, 'r', encoding='utf-8') as f:
            contents = json.load(f)
        return contents

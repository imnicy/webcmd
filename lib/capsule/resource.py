import os
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

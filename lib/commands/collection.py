from lib.capsule.resource import Resource


def layouts():
    return Resource.load_json('collections/layouts.json')

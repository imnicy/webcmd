import json
from ..capsule.resource import Resource


def layouts():
    contents = Resource.load('collections/layouts.json')
    return json.loads(contents)

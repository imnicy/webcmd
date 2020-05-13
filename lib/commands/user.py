from flask import request
from . import validate


def login(command=None):
    document = validate(request, {
        'email_or_username': {
            'required': True,
            'type': 'string',
            'regex': '[\w_\-@\.]+',
            'min': 3, 'max': 32
        },
        'password': {'required': True, 'type': 'string', 'min': 6, 'max': 32}
    }, {
        'email_or_username.required': 'username required.',
        'email_or_username.regex': 'username error.'
    })

    # print(document)

    return {'status': True}


def logout(command=None):
    pass


def register(command=None):
    pass


def resend(command=None, email=None):
    pass


def recover(command=None, credential=None):
    pass


def show(command=None, username=None):
    pass


def update(command=None):
    pass

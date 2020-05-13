from flask import request, g
from . import validate
from ..models.auth import User

"""
globals Query object in local proxy
use: g.query.get_app(), g.query.get_command(), g.query.get_arguments()
"""
query = g.get('query', None)


def login():
    document = validate(request, {
        'email_or_username': {
            'required': True,
            'type': 'string',
            'regex': '[\w_\-@\.]+',
            'min': 3, 'max': 32
        },
        'password': {'required': True, 'type': 'string', 'min': 6, 'max': 32}
    }, {
        'email_or_username.regex': 'username error.'
    })

    username = document.get('email_or_username')
    password = document.get('password')

    found_user = User.query.filter_by(username=username).first()

    if found_user is not None:
        if not found_user.verify_password(password):
            return {'status': False, 'error_text': 'password verify failed!'}
        if not found_user.available_user():
            return {'status': False, 'error_text': 'user not available!'}
    else:
        return {'status': False, 'error_text': 'user not found!'}

    return {'status': True}


def logout():
    pass


def register():
    pass


def resend(email=None):
    pass


def recover(credential=None):
    pass


def show(command=None, username=None):
    pass


def update(command=None):
    pass

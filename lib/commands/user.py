from flask import request
from . import validate, get_query
from ..models.auth import User

"""
get query arguments from local proxy globals
arguments is a dict
"""
arguments = get_query().get_arguments()


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


def resend():
    email = arguments.get('email', None)
    pass


def recover():
    credential = arguments.get('credential', None)
    pass


def show():
    username = arguments.get('username', None)
    pass


def update():
    pass

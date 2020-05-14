from flask import request, make_response
from . import validate, get_query
from ..models.auth import User
from ..capsule.exceptions import TokenDiscarded
from flask_jwt_extended import (
    create_access_token, get_jwt_identity, jwt_required, jwt_refresh_token_required
)

"""
get query arguments from local proxy globals
arguments is a dict
"""
arguments = get_query().get_arguments()


def login():
    document = validate(request, scheme={
        'email_or_username': {
            'required': True,
            'type': 'string',
            'regex': '[\w_\-@\.]+',
            'min': 3, 'max': 32
        },
        'password': {'required': True, 'type': 'string', 'min': 6, 'max': 32}
    }, messages={
        'email_or_username.regex': 'username error.'
    })

    username = document.get('email_or_username')
    password = document.get('password')

    user = User.authenticate(username, password)

    if user is None:
        return {'status': False, 'error_text': 'authenticate failed.'}

    response = make_response({'status': True})
    response.headers['Authorization'] = create_access_token(user.id)

    return response


def logout():
    """
    log out
    :return: dict
    """
    return {'status': True}


def register():
    pass


def resend():
    email = arguments.get('email', None)
    pass


def recover():
    credential = arguments.get('credential', None)
    pass


@jwt_required
def show():
    document = validate(request,scheme={
            'username': {
                'required': True,
                'type': 'string',
                'regex': '[\w_\-@\.]+',
                'min': 3, 'max': 32
            }
        },messages={
            'username.regex': 'username error.'
        }, extra=arguments
    )

    username = document.get('username', None)

    if username is None or not isinstance(username, str):
        return {'status': False}

    if username == 'me':
        print(get_jwt_identity())
        user = User.identify(get_jwt_identity())
    else:
        user = User.query.filter_by(username=username).first()

    if user is None:
        return {'status': False, 'error_text': 'user not found.'}

    return {'status': True, 'user_data': user.to_dict()}


def update():
    pass


@jwt_refresh_token_required
def token():
    document = validate(request, {
        'operation': {
            'type': 'string',
            'in': ['refresh', 'remove']
        }
    })

    operation = document.get('operation')

    if operation == 'refresh':
        response = make_response({'status': True})
        response.headers['Authorization'] = create_access_token(get_jwt_identity())

        return response
    elif operation == 'remove':
        raise TokenDiscarded('token has removed.')

    return {'status': True}

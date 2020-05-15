from flask import request, make_response, g
from . import validate, get_query
from ..models.auth import User, auth_required
from flask_jwt_extended import create_access_token

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

    email_or_username = document.get('email_or_username')
    password = document.get('password')

    user = User.authenticate(email_or_username, password)

    if user is None:
        return {'status': False, 'error_text': 'authenticate failed.'}

    response = make_response({'status': True})
    response.headers['Authorization'] = create_access_token(user.id)

    return response


@auth_required
def logout():
    """
    log out
    :return: dict
    """
    return {'status': True}


def register():
    scheme = {
        'email': {
            'required': True, 'type': 'string', 'max': 32,
            'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        },
        'username': {
            'required': True, 'type': 'string', 'max': 32, 'min': 6, 'regex': '[\w_\-\.]+',
        },
        'fullname': {'required': True, 'type': 'string', 'max': 32, 'min': 6},
        'password': {'required': True, 'type': 'string', 'max': 32, 'min': 6}
    }

    document = validate(request, scheme=scheme)

    if not User.check_email(document.get('email')):
        return {'status': False, 'error_text': 'email exists.'}

    if not User.check_username(document.get('username')):
        return {'status': False, 'error_text': 'username exists.'}

    user = User.create(username=document.get('username'), email=document.get('email'),
                       fullname=document.get('fullname'), password_source=document.get('password'))

    response = make_response({'status': True})
    response.headers['Authorization'] = create_access_token(user.id)

    return response


def resend():
    email = arguments.get('email', None)
    pass


def recover():
    credential = arguments.get('credential', None)
    pass


@auth_required
def show():
    document = validate(request, scheme={
            'username': {
                'required': True, 'type': 'string', 'regex': '[\w_\-@\.]+', 'min': 3, 'max': 32
            }
        }, messages={
            'username.regex': 'username error.'
        }, extra=arguments
    )

    username = document.get('username', None)
    if username is None or not isinstance(username, str):
        return {'status': False}

    if username == 'me':
        user = g.get('user')
    else:
        user = User.query.filter_by(username=username).first()

    if user is None:
        return {'status': False, 'error_text': 'user not found.'}

    return {'status': True, 'user_data': user.to_dict()}


@auth_required
def update():
    document = validate(request, scheme={
        'fullname': {'nullable': True, 'type': 'string', 'max': 32, 'min': 6},
        'avatar': {'nullable': True, 'type': 'string',
                   'regex': 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'},
        'gender': {'nullable': True, 'type': 'string', 'forbidden': ['f', 'm', '*']},
        'webpage': {'nullable': True, 'type': 'string',
                    'regex': 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'},
        'github_username': {'nullable': True, 'type': 'string', 'regex': '[\w_\-@\.]+'},
        'tags': {'nullable': True, 'type': 'string', 'max': 256},
        'password': {'nullable': True, 'type': 'string', 'max': 32, 'min': 6}
    })

    print(document)
    updates = {k.lower(): v.lower() for k, v in document.items() if v is not None and k in [
        'fullname', 'avatar', 'gender', 'webpage', 'github_username', 'tags', 'password'
    ]}
    print(updates)

    user = g.get('user')
    user.update_profile(updates)

    response = make_response({'status': True})

    if 'password' in updates:
        response.headers['Authorization'] = create_access_token(user.id)

    return response

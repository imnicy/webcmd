import helper

from flask import Blueprint, g, json
from flask_jwt_extended import create_access_token
from providers.jwt import jwt
from lib.capsule.exceptions import TokenDiscarded, TokenExpired, AppNotFound

errors_blue = Blueprint('errors', __name__)


@errors_blue.errorhandler(404)
def page_not_found():
    return AppNotFound('app not found from errorhandle 404.').to_response()


# @errors_blue.errorhandler(500)
# def system_error():
#     pass


@jwt.unauthorized_loader
def handle_auth_error(e):
    return TokenDiscarded(str(e)).to_response()


@jwt.expired_token_loader
def handle_expired_error(e):
    try:
        identify = e.get(helper.config('JWT_IDENTITY_CLAIM', 'identify'), None)
        claims = e.get(helper.config('JWT_USER_CLAIMS', {}))

        response = TokenExpired('Access token expired.').to_response()
        response.headers['Authorization'] = create_access_token(identify, additional_claims=claims)

        query = g.get('query', None)

        if query is not None:
            expired_data = json.loads(response.get_data())

            pre_script = expired_data.get('script', '')
            sub_script = '$scope.term.retry(\'%s\', \'%s\', %s)' \
                         % (query.app, query.command, '[\'' + '\',\''.join(query.arguments) + '\']')

            expired_data['script'] = pre_script + sub_script

            response.set_data(json.dumps(expired_data))

        return response
    except Exception as be:
        return TokenDiscarded(str(be)).to_response()


@jwt.invalid_token_loader
def handle_invalid_header_error(e):
    return TokenDiscarded(str(e)).to_response()

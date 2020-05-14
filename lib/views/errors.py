from flask import Blueprint, current_app
from flask_jwt_extended import create_access_token
from providers.jwt import jwt
from ..capsule.exceptions import TokenDiscarded, TokenExpired, AppNotFound

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
        identify = e.get(current_app.config.get('JWT_IDENTITY_CLAIM', 'identify'), None)
        response = TokenExpired('access token expired.').to_response()
        response.headers['Authorization'] = create_access_token(identify)

        return response
    except Exception as be:
        return TokenDiscarded(str(be)).to_response()


@jwt.invalid_token_loader
def handle_invalid_header_error(e):
    return TokenDiscarded(str(e)).to_response()

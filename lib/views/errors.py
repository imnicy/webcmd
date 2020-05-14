from flask import Blueprint
from providers.jwt import jwt
from ..capsule.exceptions import TokenDiscarded, TokenExpired, TerminalException

errors_blue = Blueprint('errors', __name__)


@jwt.unauthorized_loader
def handle_auth_error(e):
    try:
        raise TokenDiscarded(str(e))
    except TerminalException as te:
        return te.to_response()


@jwt.expired_token_loader
def handle_expired_error(e):
    try:
        raise TokenExpired(str(e))
    except TerminalException as te:
        return te.to_response()


@jwt.invalid_token_loader
def handle_invalid_header_error(e):
    try:
        raise TokenDiscarded(str(e))
    except TerminalException as te:
        return te.to_response()

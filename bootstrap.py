import os
from flask import Flask
from flask_wtf import CSRFProtect
from flask_jwt_extended import JWTManager
from setting import Config
from providers.db import database
from providers.redis import store as redis_store
from providers.logger import register as logger_register
from providers.jwt import jwt as jwt_manager
from lib.views import views_blue
from lib import foundation


def create_app():
    """
    create flask web manager
    from environ
    :return: Flask
    """
    # environ bootstrap
    Config.bootstrap()

    # register app logger
    logger_register(os.path.dirname(__file__), Config.LOGGER)

    # make flask manager
    app = Flask(__name__)
    app.config.from_object(Config)

    database.init_app(app)  # init database use SQLAlchmy
    redis_store.init_app(app)   # init redis store database use flask-redis
    jwt_manager.init_app(app)  # init json web token manager
    CSRFProtect(app)    # init CSRF protect

    return load_blueprints(load_blinker(app))


def load_blinker(app):
    """
    register app linkers
    :param app: Flask
    :return: Flask
    """
    @app.before_request
    def boot_library_foundation():
        foundation.boot()

    return app


def load_blueprints(app):
    """
    load blueprints
    :param app:
    :return: Flask
    """
    app.register_blueprint(views_blue)

    return app

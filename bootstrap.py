from flask import Flask
from setting import configs
from lib.views import views_blue
from lib.models import database
from lib.capsule.app import application as cmd_app_capsule


def create_app(environ=None):
    """
    create flask web manager
    from environ
    :param environ: development, production, default
    :return: Flask
    """
    if environ is None or environ not in configs:
        environ = 'default'

    # environ bootstrap
    config = configs.get(environ)
    config.bootstrap()

    # make flask manager
    app = Flask(__name__)
    app.config.from_object(config)

    # init database use SQLAlchmy
    database.init_app(app)

    return load_blueprints(load_blinker(app))


def load_blinker(app):
    """
    register app linkers
    :param app: Flask
    :return: Flask
    """
    @app.before_request
    def load_command_apps():
        cmd_app_capsule.register()

    return app


def load_blueprints(app):
    """
    load blueprints
    :param app:
    :return: Flask
    """
    app.register_blueprint(views_blue)

    return app

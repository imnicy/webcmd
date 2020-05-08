from flask import Flask, _app_ctx_stack
from flask_script import Manager
from setting import configs
from lib.views import views_blue
from lib.models import database
from lib.capsule.app import App


def create_manager(environ=None):
    """
    create flask web manager
    from environ
    :param environ: development, production, default
    :return:
    """
    if environ is None or environ not in configs:
        environ = 'default'

    # environ bootstrap
    config = configs.get(environ)
    config.bootstrap()

    # make flask manager
    fls = Flask(__name__)
    fls.config.from_object(config)

    # init database use SQLAlchmy
    database.init_app(fls)

    return Manager(load_blueprints(fls))


def load_blueprints(fls):
    """
    load blueprints
    :param fls:
    :return:
    """
    fls.register_blueprint(views_blue)

    return fls

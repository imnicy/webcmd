import os
from dotenv import find_dotenv, load_dotenv


def env(name, default=None, force_default=False):
    """
    get env config value from environ
    :param force_default: bool
    :param name: string
    :param default: string
    :return: str
    """
    value = os.getenv(name, default)

    if force_default and (not value or value == '' or value is None):
        return default

    return value


class Config:
    ENV_LOADED = False

    SECRET_KEY = env('SECRET_KEY', 'secret key')

    TERMINAL_CONFIGS = {
        'apps': [
            'lib.apps.help.Help',
            'lib.apps.cmd.Cmd',
            'lib.apps.system.System',
            'lib.apps.user.User'
        ],

        'auth': []
    }

    LOGGER = {
        'version': 1,
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }

    @staticmethod
    def bootstrap():
        load_dotenv(find_dotenv('.env'))


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%s/%s' % (
        env('DEV_DB_USER', 'user'),
        env('DEV_DB_PASSWORD', 'password'),
        env('DEV_DB_HOST', 'localhost'),
        int(env('DEV_DB_PORT', 3306, True)),
        env('DEV_DB_NAME', 'database')
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%s/%s' % (
        env('PRO_DB_USER', 'user'),
        env('PRO_DB_PASSWORD', 'password'),
        env('PRO_DB_HOST', 'localhost'),
        int(env('PRO_DB_PORT', 3306, True)),
        env('PRO_DB_NAME', 'database')
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}

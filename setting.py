import os
from dotenv import find_dotenv, load_dotenv


def env(name, default=None):
    """
    get env config value from environ
    :param name: string
    :param default: string
    :return: str
    """
    return os.getenv(name, default)


class Config:
    ENV_LOADED = False

    SECRET_KEY = env('SECRET_KEY', 'secret key')

    TERMINAL_CONFIGS = {
        'apps': [
            'lib.apps.help.Help',
            'lib.apps.cmd.Cmd',
            'lib.apps.system.System'
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
        env('DEV_DB_PORT', 3306),
        env('DEV_DB_NAME', 'database')
    ),
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%s/%s' % (
        env('PRO_DB_USER', 'user'),
        env('PRO_DB_PASSWORD', 'password'),
        env('PRO_DB_HOST', 'localhost'),
        env('PRO_DB_PORT', 3306),
        env('PRO_DB_NAME', 'database')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}

import os


def env(name, default=None, force_default=False):
    value = os.getenv(name, default)

    if force_default and (not value or value == '' or value is None):
        return default

    return value


class Config:

    def __init__(self):
        pass

    SECRET_KEY = env('SECRET_KEY', 'secret key')

    REDIS_URL = 'redis://:%s@%s:%d/%d' % (
        env('REDIS_PASSWORD', ''),
        env('REDIS_HOST', 'localhost'),
        int(env('REDIS_PORT', 6379, True)),
        int(env('REDIS_DATABASE', 0, True))
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%d/%s' % (
        env('DB_USER', 'user'),
        env('DB_PASSWORD', 'password'),
        env('DB_HOST', 'localhost'),
        int(env('DB_PORT', 3306, True)),
        env('DB_NAME', 'database')
    )

    TERMINAL_CONFIGS = {
        'apps': [
            'lib.apps.help.Help',
            'lib.apps.cmd.Cmd',
            'lib.apps.system.System',
            'lib.apps.user.User'
        ],
        'auth': [
        ]
    }

    LOGGER = {
        'version': 1,
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }

    JWT_SECRET_KEY = env('JWT_SECRET_KEY', '')
    JWT_ACCESS_TOKEN_EXPIRES = 20
    JWT_REFRESH_TOKEN_EXPIRES = 86400
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_IDENTITY_CLAIM = 'identify'
    JWT_USER_CLAIMS = 'user_claims'

    @staticmethod
    def bootstrap():
        pass


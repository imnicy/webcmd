import os
from dotenv import find_dotenv, load_dotenv


class Config:
    ENV_LOADED = False

    SECRET_KEY = '8XYn85BSfbyeS716i45ev93Nm9tj4j46DceYZtpFccrFnFMqvQWBXf4SMJy5DS3A'
    TERMINAL_CONFIGS = {
        'apps': [
            'lib.apps.help.Help',
            'lib.apps.cmd.Cmd',
            'lib.apps.system.System'
        ],

        'auth': {}
    }

    @staticmethod
    def env(name, default):
        """
        get env config value from environ
        :param name: string
        :param default: string
        :return: str
        """
        if not Config.ENV_LOADED:
            load_dotenv(find_dotenv('.env'))
            Config.ENV_LOADED = True
        return os.getenv(name, default)

    @staticmethod
    def bootstrap():
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%s/%s' % (
        Config.env('DEV_DB_USER', 'user'),
        Config.env('DEV_DB_PASSWORD', 'password'),
        Config.env('DEV_DB_HOST', 'localhost'),
        Config.env('DEV_DB_PORT', 3306),
        Config.env('DEV_DB_NAME', 'database')
    ),
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%s/%s' % (
        Config.env('PRO_DB_USER', 'user'),
        Config.env('PRO_DB_PASSWORD', 'password'),
        Config.env('PRO_DB_HOST', 'localhost'),
        Config.env('PRO_DB_PORT', 3306),
        Config.env('PRO_DB_NAME', 'database')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}

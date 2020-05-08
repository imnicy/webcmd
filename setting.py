class Config:
    SECRET_KEY = '8XYn85BSfbyeS716i45ev93Nm9tj4j46DceYZtpFccrFnFMqvQWBXf4SMJy5DS3A'
    TERMINAL_CONFIGS = {
        'apps': [
            'lib.apps.help.Help'
        ],

        'command': {},

        'auth': {}
    }

    @staticmethod
    def bootstrap():
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:abcdEF122....@192.168.254.220:3306/terminal_api',
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:abcdEF122....@192.168.254.220:3306/terminal_api'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}

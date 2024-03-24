import os

from logging.config import dictConfig


def register(root_path, config: dict | None):
    if config is None:
        config = {}

    dictConfig({
        'version': config.get('version', 1),
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(root_path, 'storage/logs/app.log'),
                'maxBytes': 1024 * 1024 * 5,
                'formatter': 'default',
                'backupCount': 5
            }
        },
        'root': {
            'level': config.get('level', 'INFO'),
            'handlers': config.get('handlers', ['wsgi'])
        }
    })

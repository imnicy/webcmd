from flask import current_app
from importlib import import_module
from setting import env as setting_env


def import_module_from_string(string, package=__name__):
    cls, module = string.rsplit('.', maxsplit=1)
    if cls.startswith('.'):
        loaded = import_module(cls, package=package)
    else:
        loaded = import_module(cls)
    return getattr(loaded, module)


def env(name, default=None, force_default=False):
    return setting_env(name, default=default, force_default=force_default)


def log(level, msg, *args, **kwargs):
    current_app.logger.log(level, msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    log(20, msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
    log(10, msg, *args, **kwargs)

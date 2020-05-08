from flask import current_app
from .query import Query
from importlib import import_module


class App:

    REGISTERED = False

    def __init__(self):
        self.APPS = []
        self.HIDDEN = {}
        self.APPS_ALIASES = {}

    def register(self):
        if self.REGISTERED:
            return

        config = current_app.config.get('TERMINAL_CONFIGS', {})
        apps = config.get('apps', [])

        for app in apps:
            cls, mod = app.rsplit('.', maxsplit=1)
            imported = import_module(cls)
            instance = getattr(imported, mod)

            if getattr(instance, 'NAME', None) is None:
                continue

            if getattr(instance, 'HIDDEN', False):
                self.HIDDEN[getattr(instance, 'NAME')] = instance
            else:
                self.APPS.append(instance())

            self.__set_apps_aliases(getattr(instance, 'NAME'), getattr(instance, 'ALIASES'))

        self.REGISTERED = True

    def __set_apps_aliases(self, name, aliases):
        self.APPS_ALIASES[name] = name

        for alias in aliases:
            self.APPS_ALIASES[alias] = name

    def __find_apps_aliases(self, name):
        return self.APPS_ALIASES.get(name, None)

    def apps(self):
        return self.APPS

    def __apps_to_array(self):
        apps = self.apps()
        data = []
        for app in apps:
            data.append(app.to_array())
        return data

    def __is_hidden(self, name):
        return True if name in self.HIDDEN else False

    def get(self, name=None, from_command=False):
        found_app = self.__find_apps_aliases(name)
        if name is not None and found_app is not None:
            if self.__is_hidden(found_app):
                return self.HIDDEN.get(found_app)
            return self.APPS[found_app]
        found_app = self.__get_from_command_or_app(name)
        if from_command and found_app:
            return found_app
        raise ModuleNotFoundError('app %s not found' % name)

    def __get_from_command_or_app(self, name):
        apps = self.apps()
        for app in apps:
            enable_commands = app.get_enable_commands()
            for command in enable_commands:
                if getattr(command, 'NAME', None) == name or name in getattr(command, 'ALIASES'):
                    return app
        return False

    def pull(self):
        apps = self.__apps_to_array()
        return {
            'status': True,
            'apps': list(apps)
        }

    def run(self, queries):
        query = Query.f(queries)
        app = self.get(query.app(), True)
        command = query.command() if getattr(app, 'NAME') == query.app() else query.app()

        app.set_active_commands([command])

        if not app.get_command(command):
            raise ModuleNotFoundError('app founded, bud command %s not found.' % query.command())

        return {
            'status': True,
            'app': app.to_array(),
            'script': app.script(),
            'queries': queries
        }

from flask import current_app
from .query import Query
from importlib import import_module
from ..capsule.exceptions import AppNotFound, CommandNotFound, InvalidArgument


class App:

    registered = False

    def __init__(self):
        self.apps = {}
        self.hidden = {}
        self.apps_aliases = {}

    def register(self):
        if self.registered:
            return

        config = current_app.config.get('TERMINAL_CONFIGS', {})
        apps = config.get('apps', [])

        for app in apps:
            cls, mod = app.rsplit('.', maxsplit=1)
            imported = import_module(cls)
            instance = getattr(imported, mod)()

            if getattr(instance, 'name', None) is None:
                continue

            if getattr(instance, 'hidden', False):
                self.hidden[getattr(instance, 'name')] = instance
            else:
                self.apps[getattr(instance, 'name')] = instance

            self.__set_apps_aliases(getattr(instance, 'name'), getattr(instance, 'aliases'))

        self.registered = True

    def __set_apps_aliases(self, name, aliases):
        self.apps_aliases[name] = name

        for alias in aliases:
            self.apps_aliases[alias] = name

    def __find_apps_aliases(self, name):
        return self.apps_aliases.get(name, None)

    def get_apps(self):
        return self.apps

    def __apps_to_array(self):
        apps = self.get_apps()
        data = []
        for app_name, app in apps.items():
            data.append(app.to_array())
        return data

    def __is_hidden(self, name):
        return True if name in self.hidden else False

    def get(self, name=None, from_command=False):
        found_app = self.__find_apps_aliases(name)
        if name is not None and found_app is not None:
            if self.__is_hidden(found_app):
                return self.hidden.get(found_app)
            return self.apps.get(found_app)

        found_app = self.__get_from_command_or_app(name)
        if from_command and found_app:
            return found_app
        raise AppNotFound('app %s not found' % name)

    def __get_from_command_or_app(self, name):
        apps = self.get_apps()
        for app_name, app in apps.items():
            enable_commands = app.get_enable_commands()
            for command in enable_commands:
                if getattr(command, 'name', None) == name or name in getattr(command, 'aliases'):
                    return app
        return False

    def pull(self):
        apps = self.__apps_to_array()
        return {
            'status': True,
            'apps': list(apps)
        }

    def run(self, queries):
        if not queries or queries is None:
            raise InvalidArgument('Invalid arguments: query field is required.')

        query = Query.f(queries)
        app = self.get(query.get_app(), True)
        command = query.get_command() if getattr(app, 'name') == query.get_app() else query.get_app()

        app.set_active_commands([command])
        enable = False if getattr(app, 'hidden') else True

        if not app.get_command(command, enable):
            raise CommandNotFound('app founded, bud command %s not found.' % query.get_command())

        return {
            'status': True,
            'app': app.to_array(),
            'script': app.get_script(),
            'queries': queries
        }


application = App()

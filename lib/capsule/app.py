from flask import current_app
from importlib import import_module


class App:

    """
    command apps register status
    """
    registered = False

    def __init__(self):
        self.apps = {}
        self.hidden = {}
        self.apps_aliases = {}

    def register(self):
        """
        register command apps before request
        :return: None
        """
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
        """
        enable command apps list
        :return: list
        """
        return self.apps

    def __apps_to_dict(self):
        apps = self.get_apps()
        data = []
        for app_name, app in apps.items():
            data.append(app.to_dict())
        return data

    def __is_hidden(self, name):
        return True if name in self.hidden else False

    def get(self, name=None, from_command=False):
        """
        get Command app from name
        :param name: str
        :param from_command: bool
        :return: App
        """
        found_app = self.__find_apps_aliases(name)
        if name is not None and found_app is not None:
            if self.__is_hidden(found_app):
                return self.hidden.get(found_app)
            return self.apps.get(found_app)

        found_app = self.__get_from_command_or_app(name)
        if from_command and found_app:
            return found_app

        return False

    def __get_from_command_or_app(self, name):
        apps = self.get_apps()
        for app_name, app in apps.items():
            enable_commands = app.get_enable_commands()
            for command in enable_commands:
                if getattr(command, 'name', None) == name or name in getattr(command, 'aliases'):
                    return app
        return False

    def pull(self):
        apps = self.__apps_to_dict()
        return {
            'status': True,
            'apps': list(apps)
        }

    def transform(self, app, command, queries):
        """
        get query object from queries string
        :param queries: str
        :param command: Command
        :param app: App
        :return: dict
        """
        return {
            'status': True,
            'app': app.to_dict(),
            'script': app.get_script(),
            'queries': queries,
            'command': command.name
        }


"""
single object for App
"""
application = App()

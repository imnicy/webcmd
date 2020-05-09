import json
from ..capsule.exceptions import CommandNotFound


class Base:

    NAME = None
    INFO = None
    SCRIPT = None

    AUTHOR = 'ly'
    HIDDEN = False
    SHOW_ON_HELP = False

    ALIASES = {}

    def __init__(self):
        self.COMMANDS = []
        self.ENABLE_COMMANDS = []
        self.ACTIVE_COMMANDS = []

    def hidden(self, status):
        self.AUTHOR = status

    def set_active_commands(self, commands):
        self.ACTIVE_COMMANDS = commands
        return self

    def get_command(self, name, enable=True):
        commands = self.get_enable_commands() if enable else self.get_commands(True)

        for found in commands:
            if found.NAME == name or name in found.ALIASES:
                return found

        return False

    def get_commands(self, refresh=False):
        if len(self.COMMANDS) == 0 or refresh:
            self.COMMANDS = self.commands()
            self.ENABLE_COMMANDS = self.COMMANDS

            if self.HIDDEN:
                active_commands = []
                for command in self.ENABLE_COMMANDS:
                    if getattr(command, 'NAME') in self.ACTIVE_COMMANDS:
                        active_commands.append(command)
                self.ENABLE_COMMANDS = active_commands

            certified_commands = []
            for command in self.ENABLE_COMMANDS:
                if getattr(command, 'AUTH', 0) == 0:
                    certified_commands.append(command)
            self.ENABLE_COMMANDS = certified_commands

        return self.ENABLE_COMMANDS

    def get_enable_commands(self):
        if len(self.ENABLE_COMMANDS) == 0:
            self.get_commands()

        return self.ENABLE_COMMANDS

    def run_command(self, name=None):
        if name is not None:
            self.set_active_commands([name])
            command = self.get_command(name)

            if command:
                return command.run()
        raise CommandNotFound('command %s not found.' % name)

    def __load_command_scripts(self):
        scripts = []
        commands = self.get_enable_commands()

        for command in commands:
            script = ''
            command.with_init(True)
            data = command.to_array()
            script += '%s:{' % data.get('name')

            for name, item in data.items():
                if name == 'init':
                    parameter_in_callback = ''
                    parameters = data.get('parameters', None)
                    if parameters is not None:
                        valid_parameters = []
                        for parameter in parameters:
                            if parameter is not None:
                                valid_parameters.append(parameter)

                        parameter_in_callback = ','.join(valid_parameters)
                    parsed_data = 'function(%s){%s}' % (parameter_in_callback, item)
                elif isinstance(item, str):
                    parsed_data = "'%s'" % item
                elif isinstance(item, list) or isinstance(item, dict):
                    parsed_data = json.dumps(item, ensure_ascii=False).replace('"', '\'')
                elif isinstance(item, bool):
                    parsed_data = 'true' if item else 'false'
                elif isinstance(item, int):
                    parsed_data = item
                else:
                    continue

                script += "%s:%s," % (name, parsed_data)
            script += '}'
            scripts.append(script)

        return '{'+','.join(scripts)+'}'

    def __build_script(self):
        if self.SCRIPT is not None:
            return self.SCRIPT

        sst = ''
        aliases = '[\''+','.join(self.ALIASES)+'\']'
        show_help_bool = 'true' if self.SHOW_ON_HELP else 'false'
        caching = 'false' if self.HIDDEN else 'true'

        sst += 'caching:%s,name:\'%s\',author:\'%s\',info:\'%s\',aliases:%s,show_on_help:%s,' \
               'controller:function(){%s},commands:%s' % \
               (caching, self.NAME, self.AUTHOR, self.INFO, aliases, show_help_bool, self.controller(),
                self.__load_command_scripts())

        script = '$scope.apps.%s={%s}' % (self.NAME, sst)
        return script

    def script(self):
        return self.__build_script()

    def __commands_to_array(self):
        to_array = []
        commands = self.get_enable_commands()

        for command in commands:
            to_array.append(command.to_array())
        return to_array

    def __get_commands_structure(self, commands):
        structure = {}

        for command in commands:
            item = {}
            if command.get('parameters', None) is not None:
                item['parameters'] = command.get('parameters')

            if command.get('aliases', None) is not None:
                item['aliases'] = command.get('aliases')

            structure[command.get('name')] = item

        return structure

    def to_array(self):
        commands = self.__commands_to_array()

        return {
            'aliases': self.ALIASES,
            'author': self.AUTHOR,
            'name': self.NAME,
            'info': self.INFO,
            'show_on_help': self.SHOW_ON_HELP,
            'commands': commands,
            'commands_array': [command.get('name', 'None') for command in commands],
            'commands_structure': self.__get_commands_structure(commands),
            'script': self.script()
        }

    def commands(self):
        raise NotImplementedError('commands function not implement.')

    def controller(self):
        raise NotImplementedError('controller function not implement.')

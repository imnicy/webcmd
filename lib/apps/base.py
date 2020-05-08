import json


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
        commands = self.get_enable_commands() if enable else self.get_commands()
        for found in commands:
            if found.NAME == name or name in found.__ALIASES__:
                return found

        return False

    def get_commands(self):
        if len(self.COMMANDS) == 0:
            self.COMMANDS = self.commands()
            self.ENABLE_COMMANDS = self.COMMANDS

            if self.AUTHOR is not None:
                for command in self.ENABLE_COMMANDS:
                    if getattr(command, 'NAME') in self.ACTIVE_COMMANDS:
                        self.ENABLE_COMMANDS.append(command)

            filtered_commands = []
            for command in self.ENABLE_COMMANDS:
                if getattr(command, 'AUTH', 0) == 0:
                    filtered_commands.append(command)

            self.ENABLE_COMMANDS = filtered_commands

        return self.COMMANDS

    def get_enable_commands(self):
        if len(self.ENABLE_COMMANDS) == 0:
            self.get_commands()

        return self.ENABLE_COMMANDS

    def run_command(self, name):
        self.set_active_commands([name])
        command = self.get_command(name)
        if command:
            return command.run()
        raise ModuleNotFoundError('command %s not found.' % name)

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
                    data = 'function(%s){%s}' % (parameter_in_callback, item)
                elif isinstance(item, str):
                    data = "'%s'" % item
                elif isinstance(item, list) or isinstance(item, dict):
                    data = json.dumps(item).replace('"', '\'')
                elif isinstance(item, bool):
                    data = 'true' if item else 'false'
                elif isinstance(item, int):
                    data = item
                else:
                    continue

                script += "%s:%s," % (name, data)
            script += '}'
            scripts.append(script)

        return '{'+','.join(scripts)+'}'

    def __build_script(self):
        if self.SCRIPT is not None:
            return self.SCRIPT
        sst = ''
        aliases = '[\''+','.join(self.ALIASES)+'\']'
        show_help_bool = 'true' if self.SHOW_ON_HELP else 'false'
        caching = 'false' if self.HIDDEN else 'false'

        sst += 'caching:%s,name:\'%s\',author:\'%s\',info:\'%s\',aliases:%s,show_on_help:%s,' \
               'controller:function(){%s},commands:%s' % \
               (caching, self.NAME, self.AUTHOR, self.INFO, aliases, show_help_bool, self.controller(),
                self.__load_command_scripts())

    def script(self):
        return self.__build_script()

    def __commands_to_array(self):
        to_array = []
        commands = self.get_enable_commands()
        for command in commands:
            to_array.append(dict(command))
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
            'commands_array': '',
            'commands_structure': self.__get_commands_structure(commands),
            'script': self.script()
        }

    def commands(self):
        raise NotImplementedError('commands function not implement.')

    def controller(self):
        raise NotImplementedError('controller function not implement.')

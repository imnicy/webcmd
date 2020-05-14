import re

from jsmin import jsmin
from flask import json


class Base:

    name = None
    info = None

    script = None
    author = 'ly'
    hidden = False
    show_on_help = False
    aliases = []

    def __init__(self):
        self.all_commands = []
        self.enable_commands = []
        self.active_commands = []

    def set_hidden(self, status):
        self.hidden = status

    def set_active_commands(self, commands):
        self.active_commands = commands
        return self

    def get_command(self, name=None, enable=True):
        commands = self.get_enable_commands() if enable else self.get_commands(True)
        for found in commands:
            if name is not None and (found.name == name or name in found.aliases):
                return found

        return None

    def get_commands(self, refresh=False):
        if len(self.all_commands) == 0 or refresh:
            self.all_commands = self.commands()
            self.enable_commands = self.all_commands

            if self.hidden:
                active_commands = []
                for command in self.enable_commands:
                    if getattr(command, 'name') in self.active_commands:
                        active_commands.append(command)
                self.enable_commands = active_commands

            certified_commands = []
            for command in self.enable_commands:
                if getattr(command, 'auth_level', 0) == 0:
                    certified_commands.append(command)
            self.enable_commands = certified_commands

        return self.all_commands

    def get_enable_commands(self):
        if len(self.enable_commands) == 0:
            self.get_commands()

        return self.enable_commands

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
                    arguments = data.get('arguments', [])
                    valid_arguments = []
                    for argument in arguments:
                        if isinstance(argument, str) and re.match(r"^[a-zA-Z_]\w+\??$", argument):
                            valid_arguments.append(argument.replace('?', ''))
                    arguments_in_callback = ','.join(valid_arguments)
                    parsed_data = 'function(%s){%s}' % (arguments_in_callback, item)
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
        if self.script is not None:
            return self.script

        sst = ''
        aliases = '[\''+','.join(self.aliases)+'\']'
        show_help_bool = 'true' if self.show_on_help else 'false'
        caching = 'false' if self.hidden else 'true'

        sst += 'caching:%s,name:\'%s\',author:\'%s\',info:\'%s\',aliases:%s,show_on_help:%s,' \
               'controller:function(){%s},commands:%s' % \
               (caching, self.name, self.author, self.info, aliases, show_help_bool, self.controller(),
                self.__load_command_scripts())

        script = jsmin('$scope.apps.%s={%s}' % (self.name, sst))
        return script

    def get_script(self):
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
            'aliases': self.aliases,
            'author': self.author,
            'name': self.name,
            'info': self.info,
            'show_on_help': self.show_on_help,
            'commands': commands,
            'commands_array': [command.get('name', None) for command in commands],
            'commands_structure': self.__get_commands_structure(commands),
            'script': self.get_script()
        }

    def commands(self):
        raise NotImplementedError('commands function not implement.')

    def controller(self):
        raise NotImplementedError('controller function not implement.')

    def __repr__(self):
        return '<App %s: %s>' % (self.name, self.info)

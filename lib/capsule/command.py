from importlib import import_module


class Command:

    arguments = []
    _with_init = False

    def __init__(
            self,
            name,
            auth_level=0,
            caching=False,
            help_string=None,
            arguments=None,
            aliases=None,
            pro=False,
            example=None,
            init=None,
            command=None
    ):
        self.name = name
        self.help_string = help_string
        self.auth_level = auth_level

        self.__parse_arguments(arguments)
        self.__set_aliases(aliases)

        self.caching = caching
        self.pro = pro
        self.example = example

        self.__bind_command(command)
        self.__init_script(init)

    def __init_script(self, script):
        if isinstance(script, str):
            self.init = script
        elif hasattr(script, '__call__'):
            self.init = script()
        if not isinstance(self.init, str):
            self.init = None

    def __bind_command(self, command):
        if isinstance(command, str):
            if command in locals().keys() or command in dir():
                self.callable = command
            elif '.' in command:
                cls, cmd = command.rsplit('.', maxsplit=1)
                module = import_module(cls)
                self.callable = getattr(module, cmd)
        elif hasattr(command, '__call__'):
            self.callable = command

    def __parse_arguments(self, arguments):
        self.arguments = []
        if isinstance(arguments, list):
            for argument in arguments:
                self.__argument_parser(argument)

    def __argument_parser(self, argument):
        if isinstance(argument, str) and ' ' not in argument:
            self.arguments.append(argument)

    def __set_aliases(self, aliases):
        if isinstance(aliases, str) or isinstance(aliases, list):
            self.aliases = aliases if isinstance(aliases, list) else [aliases]
        else:
            self.aliases = []

    def with_init(self, status=True):
        self._with_init = status

    def run(self):
        the_callable = self.callable
        if the_callable is not None and hasattr(the_callable, '__call__'):
            return the_callable()
        return None

    def allow_cache(self):
        if len(self.arguments):
            return False
        if self.caching:
            return True
        return True

    def to_array(self):
        arguments = self.arguments if self.arguments is not None else []

        data = {
            'pro': self.pro,
            'help': self.help_string,
            'name': self.name,
            'auth': self.auth_level,
            'example': self.example,
            'aliases': self.aliases,
            'arguments': arguments,
            'caching': self.allow_cache()
        }

        if self._with_init:
            data['init'] = self.init

        return data

    def to_string(self):
        return '<Command %s: %s>' % (self.name, self.help_string)

    def __repr__(self):
        return self.to_string()

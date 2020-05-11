from importlib import import_module


class Command:

    arguments = []
    options = []

    _with_init = False

    def __init__(
            self,
            name,
            auth_level=0,
            caching=False,
            help_string=None,
            arguments=None,
            options=None,
            aliases=None,
            pro=False,
            example=None,
            init=None,
            command=None
    ):
        self.name = name
        self.help_string = help_string
        self.auth_level = auth_level

        self.__parse_arguments_and_options(arguments=arguments, options=options)
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

    def __parse_arguments_and_options(self, arguments, options):
        self.arguments = []
        self.options = []
        if isinstance(arguments, list):
            for argument in arguments:
                self.__argument_parser(argument)
        if isinstance(options, list):
            for option in options:
                self.__option_parser(option)

    def __argument_parser(self, argument):
        if isinstance(argument, str) and ' ' not in argument:
            self.arguments.append(argument)

    def __option_parser(self, option):
        if isinstance(option, str) and ' ' not in option:
            self.options.append(option)

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
            return the_callable(self)
        return None

    def allow_cache(self):
        if len(self.arguments) or len(self.options):
            return False
        if self.caching:
            return True
        return True

    def to_array(self):
        arguments = self.arguments if self.arguments is not None else []
        options = self.options if self.options is not None else []

        data = {
            'pro': self.pro,
            'help': self.help_string,
            'name': self.name,
            'auth': self.auth_level,
            'example': self.example,
            'aliases': self.aliases,
            'options': options,
            'arguments': arguments,
            'caching': self.allow_cache()
        }

        if self._with_init:
            data['init'] = self.init

        return data

    def to_string(self):
        return 'Command <%s>' % self.name

from importlib import import_module


class Command:

    PRO = False
    INIT = None
    HELP = None
    EXAMPLE = None

    WITH_INIT = False
    CALLABLE = None
    NO_CACHING = False
    FORCE_CACHING = False

    ALIASES = []
    PARAMETERS = []

    AUTH = 0

    def __init__(self, name):
        self.NAME = name

    @staticmethod
    def build(name):
        return Command(name)

    def need_auth(self, level):
        self.AUTH = level
        return self

    def no_caching(self):
        self.NO_CACHING = True
        return self

    def force_caching(self):
        self.FORCE_CACHING = True
        return self

    def name(self, name):
        self.NAME = name
        return self

    def help(self, message):
        self.HELP = message
        return self

    def parameters(self, parameters):
        self.PARAMETERS = parameters if isinstance(parameters, list) else [parameters]
        return self

    def aliases(self, aliases):
        self.ALIASES = aliases
        return self

    def pro(self, status):
        self.PRO = status
        return self

    def example(self, example):
        self.EXAMPLE = example
        return self

    def init(self, called):
        if isinstance(called, str):
            self.INIT = called
        elif hasattr(called, '__call__'):
            self.INIT = called()
        if not isinstance(self.INIT, str):
            self.INIT = None
        return self

    def with_init(self, status):
        self.WITH_INIT = status
        return self

    def command(self, called):
        self.CALLABLE = called
        return self

    def run(self):
        the_callable = self.CALLABLE
        if the_callable is not None and isinstance(the_callable, str):
            cls, cmd = the_callable.rsplit('.', maxsplit=1)
            module = import_module(cls)
            command = getattr(module, cmd)
            if command is not None and hasattr(command, '__call__'):
                return command(self)
        return None

    def allow_cache(self):
        if self.FORCE_CACHING:
            return True
        if self.NO_CACHING:
            return False
        if self.PARAMETERS:
            return False
        return True

    def to_array(self):
        parameters = self.PARAMETERS if self.PARAMETERS is not None else ['']
        data = {
            'pro': self.PRO,
            'help': self.HELP,
            'name': self.NAME,
            'auth': self.AUTH,
            'example': self.EXAMPLE,
            'aliases': self.ALIASES,
            'parameter': ','.join(parameters),
            'parameters': parameters,
            'caching': self.allow_cache()
        }
        if self.WITH_INIT is not None:
            data['init'] = self.INIT
        return data

    def to_string(self):
        return self.NAME + '__' + '_'.join(self.PARAMETERS)

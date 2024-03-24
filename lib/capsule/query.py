import helper

from flask import g
from .exceptions import InvalidQueries
from .app import application
from .exceptions import AppNotFound, CommandNotFound, InvalidArgument


class Query:

    def __init__(self, queries):

        self.app = None
        self.command = None
        self.arguments = []
        self.queries = queries

        """
        cache found items
        """
        self.found = {
            'app': None,
            'command': None,
            'arguments': {}
        }

        """
        parse queries string
        get app,command,arguments from it
        and push this to local proxy
        """
        self.parse(queries)

        """
        logging query run records
        """
        helper.debug('run command with queries: %s' % queries)

    def to_dict(self):
        return {
            'app': self.app,
            'command': self.command,
            'arguments': self.arguments
        }

    def parse(self, queries):
        joined = [] if queries is None else queries.strip().split(' ')
        valid = list(map(lambda q: q.strip(), joined))

        if len(valid) == 0:
            raise InvalidQueries('invalid queries %s' % queries)

        self.app = valid[0]
        self.command = 'index' if len(valid) < 2 else valid[1]
        self.arguments = valid[2:]

        """
        current query context
        push on local proxy globals
        """
        g.query = self

        return True

    def get_app(self):
        found_app = self.found.get('app')
        if found_app is not None:
            return found_app

        app = application.get(self.app, True)

        if not app:
            raise AppNotFound('app not found from queries %s' % self.queries)

        self.found['app'] = app

        return app

    def get_command(self):
        found_command = self.found.get('command')
        if found_command is not None:
            return found_command

        app = self.get_app()
        command = self.command

        app.set_active_commands([command])
        enable = False if getattr(app, 'hidden') else True
        command = app.get_command(command, enable)

        if not command:
            raise CommandNotFound('command not found from queries %s' % self.queries)

        self.found['command'] = command

        return command

    def get_arguments(self):
        found_arguments = self.found.get('arguments')
        if found_arguments is not None:
            return found_arguments

        arguments = {}
        command = self.get_command()
        command_arguments = command.arguments

        try:
            for _k, _v in enumerate(command_arguments):
                if _v.endswith('?'):
                    arguments[_v[0:-1]] = None if _k > len(self.arguments) else self.arguments[_k]
                else:
                    if len(self.arguments) <= _k:
                        raise InvalidArgument('invalid argument or argument not found: %s.' % _v)
                    arguments[_v] = self.arguments[_k]
        except TypeError:
            return arguments

        self.found['arguments'] = arguments

        return arguments

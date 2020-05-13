from flask import g
from .exceptions import InvalidQueries
from .app import application
from .exceptions import AppNotFound, CommandNotFound


class Query:

    app = None
    command = None
    queries = None

    def __init__(self, queries):
        self.arguments = []
        self.queries = queries
        """
        parse queries string
        get app,command,arguments from it
        and push this to local proxy
        """
        self.parse(queries)

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
        """
        get command app object
        :return: App
        """
        app = application.get(self.app, True)

        if not app:
            raise AppNotFound('app not found from queries %s' % self.queries)

        return app

    def get_command(self):
        """
        get command object
        :return: Command
        """
        app = self.get_app()
        command = self.command

        app.set_active_commands([command])
        enable = False if getattr(app, 'hidden') else True
        command = app.get_command(command, enable)

        if not command:
            raise CommandNotFound('command not found from queries %s' % self.queries)

        return command

    def get_arguments(self):
        return self.arguments

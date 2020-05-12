class Query:

    app = None
    command = None

    def __init__(self, queries):
        self.arguments = []
        self.parse(queries)

    @staticmethod
    def f(queries):
        return Query(queries)

    def parse(self, queries):
        joined = [] if queries is None else queries.strip().split(' ')
        valid = list(map(lambda q: q.strip(), joined))

        if len(valid) == 0:
            return False

        self.app = valid[0]
        self.command = 'index' if len(valid) < 2 else valid[1]
        self.arguments = valid[2:]

        return True

    def get_app(self):
        return self.app

    def get_command(self):
        return self.command

    def get_arguments(self):
        return self.arguments

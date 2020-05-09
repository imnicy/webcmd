class Query:

    APP = None
    COMMAND = None

    def __init__(self, queries):
        self.PARAMETERS = []
        self.parse(queries)

    @staticmethod
    def f(queries):
        return Query(queries)

    def parse(self, queries):
        joined = [] if queries is None else queries.strip().split(' ')
        valid = list(map(lambda q: q.strip(), joined))

        if len(valid) == 0:
            return False

        self.APP = valid[0]
        self.COMMAND = 'index' if len(valid) < 2 else valid[1]
        self.PARAMETERS = valid[2:]

        return True

    def app(self):
        return self.APP

    def command(self):
        return self.COMMAND

    def parameters(self):
        return self.PARAMETERS

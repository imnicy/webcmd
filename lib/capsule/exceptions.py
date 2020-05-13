from flask import make_response, request


class TerminalException(Exception):

    SCRIPT = None

    def to_response(self):
        query = request.values.get('query', None)
        if query is None and request.json is not None:
            query = request.json.get('query', '')
        content = {
            'app': '',
            'queries': query,
            'status': False,
            'errorText': str(self)
        }

        if self.SCRIPT is not None:
            content['script'] = self.SCRIPT

        response = make_response(content)
        return response


class AppNotFound(TerminalException):
    SCRIPT = '$scope.term.returnError(5404);'


class CommandNotFound(TerminalException):
    SCRIPT = '$scope.term.returnError(4404);'


class ValidationError(TerminalException):
    SCRIPT = '$scope.term.returnError(302);'


class InvalidArgument(TerminalException):
    pass

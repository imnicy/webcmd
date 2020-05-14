from flask import make_response


class TerminalException(Exception):

    SCRIPT = '$scope.term.returnError(\'System error\');'

    def to_response(self):
        content = {
            'status': False,
            'error_text': str(self)
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
    SCRIPT = '$scope.term.returnError(5403);'


class InvalidQueries(TerminalException):
    SCRIPT = '$scope.term.returnError(4403);'


class NotFound(TerminalException):
    SCRIPT = '$scope.term.returnError(3404);'


class TokenExpired(TerminalException):
    SCRIPT = '$scope.term.returnError(3403);'


class TokenDiscarded(TerminalException):
    SCRIPT = '$scope.term.returnError(2403);'

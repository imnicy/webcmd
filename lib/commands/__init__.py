from flask import g
from werkzeug.local import LocalProxy
from providers.validate import Validator
from ..capsule.exceptions import ValidationError, TerminalException
from ..capsule.mark import get_mark


def validate(document, scheme=None, messages=None):
    if isinstance(document, LocalProxy):
        document = {**document.values.to_dict(), **document.json}

    result, document_or_error = Validator(scheme).validate(document, to_bool=False, messages=messages)

    def build_error_msg(path, error):
        error = error[0] if isinstance(error, list) else error
        return 'document %s: %s' % (path, error)

    if not result:
        messages = [build_error_msg(k, m) for k, m in document_or_error.items()]
        raise ValidationError(messages[0])

    return document_or_error


def get_query():
    """
    globals Query object in local proxy
    use: g.query().get_app(), g.query().get_command(), g.query().get_arguments()
    :return Query
    """
    query = g.get('query', None)

    if get_mark('process') == 'run':
        if query is None:
            raise TerminalException('query is invalid on local proxy.')

    return query

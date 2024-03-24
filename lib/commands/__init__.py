from flask import g
from werkzeug.local import LocalProxy
from providers.validate import Validator
from lib.capsule.exceptions import ValidationError, TerminalException
from lib.capsule.mark import get_mark


def validate(document, scheme=None, messages=None, extra=None):
    if document is not None and isinstance(document, LocalProxy):
        document = {**(document.values.to_dict() or {}), **(document.json or {})}

    if extra is not None and isinstance(extra, dict):
        document.update(extra)

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

    if query is None and get_mark('process') == 'run':
        raise TerminalException('query is invalid on local proxy.')

    return query

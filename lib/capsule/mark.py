from flask import g
from helper import import_module_from_string


def process_run():
    print('process run')


"""
command signals
example:
{'process.command_run': callback}
"""
listeners = {
    # 'process.run': process_run
}


def mark(node, tag):
    """
    mark node tag and make signals on make event
    :param node: str
    :param tag: str
    :return: void
    """
    if node is None or not isinstance(node, str) or tag is None or not isinstance(tag, str):
        """ invalid mark event """
        return

    def push_on_globals(k, v):
        _m = g.get('mark', {})
        _m.update({k: v})

    listener = '%s.%s' % (node, tag)    # listener name

    if listener in listeners:
        """
        check mark signal in listeners
        is signal listener is exists then call it
        listener should be a callback or module
        """
        _callback = listeners[listener]
        _final = None
        if hasattr(_callback, '__call__'):
            _final = _callback
        elif isinstance(_callback, str) and _callback in globals().keys():
            _final = globals().get(_callback)
        elif '.' in _callback:
            _final = import_module_from_string(_callback, package=__name__)

        if _final is not None and hasattr(_final, '__call__'):
            """
            call signal listener callback
            """
            _final()

    """
    push mark status on local proxy globals
    """
    push_on_globals(node, tag)


def get_mark(node):
    """
    get mark status on local proxy globals
    :param node: str
    :return: str
    """
    _mark = g.get('mark', {})

    return _mark.get(node, None)

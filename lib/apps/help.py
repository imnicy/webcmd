from .base import Base
from ..capsule.command import Command


class Help(Base):

    NAME = 'help'
    INFO = 'Need help with this shit?'
    SHOW_ON_HELP = True
    ALIASES = ['wtf', 'info', 'information']

    def commands(self):
        def index_called():
            return '' \
                   '$scope.apps.help.header(false, function() {' \
                   '    $scope.apps.help.list(false)' \
                   '})'

        def pro_called():
            return '' \
                   '$scope.apps.help.header(true, function() {' \
                   '    $scope.apps.help.list(true)' \
                   '})'

        return [
            Command.build('index').help('This is the help module of imnicy.com OS.').init(index_called),
            Command.build('pro').help('Advanced commands for pro users.').aliases(['all']).init(pro_called)
        ]

    def controller(self):
        pass

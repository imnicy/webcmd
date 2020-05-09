from .base import Base
from ..capsule.command import Command
from ..capsule.resource import Resource


class Help(Base):

    NAME = 'help'
    INFO = 'Need help with this shit?'
    SHOW_ON_HELP = True
    ALIASES = ['wtf', 'info', 'information']

    def commands(self):
        return [
            Command.build('index').help('This is the help module of imnicy.com OS.').init(
                '$scope.apps.help.header(false, function() {$scope.apps.help.list(false)})'
            ),

            Command.build('pro').help('Advanced commands for pro users.').aliases(['all']).init(
                '$scope.apps.help.header(true, function() {$scope.apps.help.list(true)})'
            ),

            Command.build('app').help('Get help for an app.').parameters(['app_name', 'flag']).example('help app cmd')
            .init(
                'var pro = flag === \'pro\' ? true : false; $scope.apps.help.list(pro, app_name)'
            )
        ]

    def controller(self):
        return Resource.load('scripts/apps/help.js')

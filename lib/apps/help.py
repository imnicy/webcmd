from .base import Base
from lib.capsule.command import Command
from lib.capsule.resource import Resource


class Help(Base):

    name = 'help'
    info = 'Need help with this shit?'

    show_on_help = True
    aliases = ['wtf', 'info', 'information']

    def commands(self):
        return [
            Command(name='index', help_string='This is the help module of imnicy.com OS.',
                    init='$scope.apps.help.header(false, function() {$scope.apps.help.list(false)})'),

            Command(name='pro', help_string='Advanced commands for pro users.', aliases=['all'],
                    init='$scope.apps.help.header(true, function() {$scope.apps.help.list(true)});'),

            Command(name='app', help_string='Get help for an app.', arguments=['app_name', 'cmd_name?'],
                    example='help app cmd',
                    init='var pro = cmd_name ? true : false; $scope.apps.help.list(pro, app_name, cmd_name)'),
        ]

    def controller(self):
        return Resource.load('scripts/apps/help.js')

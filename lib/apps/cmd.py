from .base import Base
from lib.capsule.command import Command
from lib.capsule.resource import Resource


class Cmd(Base):

    name = 'cmd'
    info = 'Etc module of cmd platform'

    show_on_help = True
    aliases = ['etc']

    def commands(self):
        return [
            Command(name='index', help_string='cmd is toolkit of ly.com', caching=True,
                    init='$scope.ui.addWarning(\'You can enter cmd <cmd>help app cmd</cmd> for more help.\');'),

            Command(name='layouts', help_string='Show all available layouts', caching=True, example='cmd layouts',
                    init='$scope.apps.cmd.layouts();', command='lib.commands.collection.layouts'),

            Command(name='layout', help_string='Set layout from available layouts.', example='cmd layout default',
                    arguments=['name'], pro=True, init='$scope.apps.cmd.layout(name);'),

            Command(name='about', help_string='hello web cmd!', pro=True, example='cmd about',
                    init='$scope.apps.cmd.about();'),

            Command(name='search', help_string='Search in ly.com', arguments=['query'],
                    example='cmd search Paris Hilton | cmd s -a Paris Hilton',
                    init='$scope.apps.cmd.search(query);'),

            Command(name='go', arguments=['url'], help_string='Go to url',
                    example='cmd go google.com | cmd go https://example.com',
                    init='$scope.apps.cmd.go(url);')
        ]

    def controller(self):
        return Resource.load('scripts/apps/cmd.js')

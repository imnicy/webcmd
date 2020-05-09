from .base import Base
from ..capsule.command import Command
from ..capsule.resource import Resource


class Cmd(Base):
    NAME = 'cmd'
    INFO = 'Etc module of cmd platform'
    SHOW_ON_HELP = True
    ALIASES = ['etc']

    def commands(self):
        return [
            Command.build('index').help('cmd is toolkit of imnicy.com').force_caching().init(
                '$scope.ui.addWarning(\'You can enter cmd <cmd>help app cmd<cmd> for more help.\');'
            ),

            Command.build('layouts').help('Show all available layouts').force_caching().example('cmd layouts').init(
                '$scope.apps.cmd.layouts();'
            ).command('lib.commands.collection.layouts'),

            Command.build('layout').help('Set layout from available layouts.').example('cmd layout default')
            .parameters(['name']).pro(True).init(
                '$scope.apps.cmd.layout(name);'
            ),

            Command.build('about').help('hello web cmd!').pro(True).example('cmd about').init(
                '$scope.apps.cmd.about();'
            ),

            Command.build('search').help('Search in imnicy.com').parameters(['query']).example(
                'cmd search Paris Hilton | cmd s -a Paris Hilton'
            ).init(
                '$scope.apps.cmd.search(query);'
            ),

            Command.build('go').parameters('url').help('Go to url').example(
                'cmd go google.com | cmd go https://example.com'
            ).init(
                '$scope.apps.cmd.go(url);'
            )
        ]

    def controller(self):
        return Resource.load('scripts/apps/cmd.js')

from .base import Base
from ..capsule.command import Command
from ..capsule.resource import Resource


class System(Base):

    NAME = 'system'
    INFO = 'Hidden system operating instruction group'
    SHOW_ON_HELP = False
    ALIASES = ['sys']
    HIDDEN = True

    def commands(self):
        return [
            Command.build('cache').parameters('type').no_caching().init(
                '$scope.ui.add([\'You found something hidden\']);$scope.http.api();'
            ).command('lib.commands.system.flush_all_cache'),

            Command.build('welcome').no_caching().init(
                '$scope.ui.add([\'Welcome system\'])'
            )
        ]

    def controller(self):
        return Resource.load('scripts/apps/system.js')

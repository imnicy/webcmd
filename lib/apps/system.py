from .base import Base
from ..capsule.command import Command
from ..capsule.resource import Resource


class System(Base):

    name = 'system'
    info = 'Hidden system operating instruction group'

    show_on_help = False
    aliases = ['sys']
    hidden = True

    def commands(self):
        return [
            Command(name='cache', arguments=['type'], caching=False,
                    init='$scope.ui.add([\'You found something hidden\']);$scope.http.api();',
                    command='lib.commands.system.flush_all_cache'),

            Command(name='welcome', caching=False, init='$scope.ui.add([\'Welcome system\'])')
        ]

    def controller(self):
        return Resource.load('scripts/apps/system.js')

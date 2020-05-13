from flask import Blueprint
from helper import import_module_from_string


loaded_views = [
    '.api.api_blue',
    '.terminal.terminal_blue'
]


class NestableBlueprint(Blueprint):
    def register_blueprint(self, blueprint, **options):
        def deferred(state):
            url_prefix = (state.url_prefix or u"") + (options.get('url_prefix', blueprint.url_prefix) or u"")
            if 'url_prefix' in options:
                del options['url_prefix']
            state.app.register_blueprint(blueprint, url_prefix=url_prefix, **options)
        self.record(deferred)


views_blue = NestableBlueprint('views', __name__)


for view_cls in loaded_views:
    blue = import_module_from_string(view_cls, package=__name__)
    views_blue.register_blueprint(blue)

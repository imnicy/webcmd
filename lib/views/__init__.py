from flask import Blueprint
from importlib import import_module


loaded_views = {
    'api_blue': '.api',
    'terminal_blue': '.terminal'
}


class NestableBlueprint(Blueprint):
    def register_blueprint(self, blueprint, **options):
        def deferred(state):
            url_prefix = (state.url_prefix or u"") + (options.get('url_prefix', blueprint.url_prefix) or u"")
            if 'url_prefix' in options:
                del options['url_prefix']
            state.app.register_blueprint(blueprint, url_prefix=url_prefix, **options)
        self.record(deferred)


views_blue = NestableBlueprint('views', __name__)


for name, cls in loaded_views.items():
    loaded = import_module(cls, package=__name__)
    blue = getattr(loaded, name)
    views_blue.register_blueprint(blue)

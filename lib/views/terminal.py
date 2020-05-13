from flask import Blueprint, render_template
from ..capsule.app import application as cmd_app_capsule
from ..capsule.resource import Resource
import json


terminal_blue = Blueprint('terminal', __name__)


class Terminal:

    @staticmethod
    def get_app_commands():
        explain = {}
        apps = cmd_app_capsule.get_apps()

        for app_name, app in apps.items():
            command_explain = {}
            commands = app.get_enable_commands()
            for command in commands:
                command_explain[getattr(command, 'name')] = {
                    'arguments': getattr(command, 'arguments'),
                    'aliases': getattr(command, 'aliases')
                }

            explain[getattr(app, 'name')] = {
                'aliases': getattr(app, 'aliases'),
                'commands': command_explain
            }

        return json.dumps(explain)

    @staticmethod
    def get_terminal_data():
        data = {
            'news': Terminal.__get_news(),
            'tips': Terminal.__get_tips(),
            'info': {
                'version': 'v0.9.3',
                'codename': 'beta'
            },
            'token': ''
        }
        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def __get_news():
        return json.loads(Resource.load('collections/news.json'))

    @staticmethod
    def __get_tips():
        return json.loads(Resource.load('collections/tips.json'))


@terminal_blue.route('/')
@terminal_blue.route('/<action>')
@terminal_blue.route('/<action>/<inner_action>')
@terminal_blue.route('/<action>/<inner_action>/<run_cmd>')
def default(action=None, inner_action=None, run_cmd=None):
    return render_template('terminal/default.htm',
                           app_commands=Terminal.get_app_commands(),
                           terminal_data=Terminal.get_terminal_data())


@terminal_blue.route('/templates/<name>')
def template(name=None):
    if name in ['terminal', 'terminals-window']:
        return render_template('terminal/partials/%s.htm' % name)
    return 'template not found', 404

from flask import Blueprint, render_template
from ..capsule.app import App
import json


terminal_blue = Blueprint('terminal', __name__)


class Terminal:

    NEWS = ["Github: <a href='https://github.com/imnicy'>https://github.com/imnicy</a>"]
    TIPS = ["0.9.2 - Fixed some bugs for smoother use."]

    @staticmethod
    def get_app_commands():
        explain = {}
        application = App()
        application.register()
        apps = application.apps()

        for app in apps:
            command_explain = {}
            commands = app.get_enable_commands()
            for command in commands:
                command_explain[getattr(command, 'NAME')] = {
                    'parameters': getattr(command, 'PARAMETERS'),
                    'aliases': getattr(command, 'ALIASES')
                }

            explain[getattr(app, 'NAME')] = {
                'aliases': getattr(app, 'ALIASES'),
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
        return json.dumps(data)

    @staticmethod
    def __get_news():
        return Terminal.NEWS

    @staticmethod
    def __get_tips():
        return Terminal.TIPS


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

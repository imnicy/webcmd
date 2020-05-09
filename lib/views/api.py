import json
from flask import Blueprint, request
from ..capsule.app import application as cmd_app_capsule
from ..capsule.exceptions import TerminalException


api_blue = Blueprint('api', __name__, url_prefix='/api/v1')


@api_blue.route('/apps', methods=['GET', 'POST'])
@api_blue.route('/apps/<app>', methods=['GET', 'POST'])
@api_blue.route('/apps/<app>/<command>', methods=['GET', 'POST'])
def handle(app=None, command=None):
    handler = cmd_app_capsule
    response = 'None'
    try:
        if app is not None:
            if app == 'run':
                query = request.values.get('query', None)
                if query is None and request.json is not None:
                    query = request.json.get('query', None)
                response = handler.run(query)
            else:
                found = handler.get(app)
                if found and found is not None:
                    response = found.run_command(command)
        else:
            response = handler.pull()
    except TerminalException as e:
        return e.to_response()

    return json.dumps(response, ensure_ascii=False)


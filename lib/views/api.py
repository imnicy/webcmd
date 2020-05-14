from flask import Blueprint, request, json
from flask.wrappers import Response
from ..capsule.app import application as cmd_app_capsule
from ..capsule.query import Query
from ..capsule.exceptions import TerminalException
from ..capsule.mark import mark


api_blue = Blueprint('api', __name__, url_prefix='/api/v1')


@api_blue.route('/apps', methods=['GET', 'POST'])
@api_blue.route('/apps/<app>', methods=['GET', 'POST'])
@api_blue.route('/apps/<app>/<queries>', methods=['GET', 'POST'])
def handle(app=None, queries=None):
    """
    api request handle
    execute command or pull app commands detail to json
    :param app: str
    :param queries: str
    :return: Response|str
    """
    handler = cmd_app_capsule
    app_capsule_transform = False

    try:
        if app is not None:
            if app == 'run':
                app_capsule_transform = True
                queries = request.values.get('queries', None)
                if queries is None and request.json is not None:
                    queries = request.json.get('queries', None)

                mark('process', 'transform') # mark process status to transform
            else:
                queries = '%s %s' % (app, queries)
                mark('process', 'run')  # mark process status to run

            query = Query(queries)  # get Query object from queries string
            app = query.get_app()
            command = query.get_command()

            response = handler.transform(app, command, queries) if app_capsule_transform else command.run()
        else:
            response = handler.pull()
            mark('process', 'pull')     # mark process status to pull

    except TerminalException as e:
        return e.to_response()

    return response if isinstance(response, Response) else json.dumps(response, ensure_ascii=False)


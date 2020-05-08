from flask import Blueprint


api_blue = Blueprint('api', __name__, url_prefix='/api/v1')


@api_blue.route('/apps/<app>', methods=['GET', 'POST'])
@api_blue.route('/apps/<app>/<command>', methods=['GET', 'POST'])
def handle(app=None, command=None):
    return None

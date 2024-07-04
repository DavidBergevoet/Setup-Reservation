from routes.api.version import version
from routes.api.reservations import update_reserved, update_current, update_queue, cancel_request
from routes.api import setups
from entities import application


def init():
    application.app.add_url_rule(
        '/api/version', 'version', version, methods=['GET'])
    application.app.add_url_rule(
        '/api/update_reserved', 'update_reserved', update_reserved, methods=['GET'])
    application.app.add_url_rule(
        '/api/update_current', 'update_current', update_current, methods=['GET'])
    application.app.add_url_rule(
        '/api/update_queue', 'update_queue', update_queue, methods=['GET'])
    application.app.add_url_rule(
        '/api/cancel_request', 'cancel_request', cancel_request, methods=['DELETE'])
    application.app.add_url_rule(
        '/api/setups', 'setups.get', setups.get, methods=['GET'])

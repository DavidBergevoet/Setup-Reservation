from routes import index, static
from entities import application


def init():
    application.app.add_url_rule(
        '/', 'index', index.index, methods=['GET', 'POST'])
    application.app.add_url_rule(
        '/static/<path:path>', 'static_file', static.static_file, methods=['GET'])

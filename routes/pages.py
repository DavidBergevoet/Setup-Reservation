from routes.index import index
from routes.static import static_file
from entities import application

def init():
    application.app.add_url_rule('/', 'index', index, methods=['GET', 'POST'])
    application.app.add_url_rule('/static/<path:path>', 'static_file', static_file, methods=['GET'])

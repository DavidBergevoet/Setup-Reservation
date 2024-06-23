from routes.index import index
from entities import application

def init():
    application.app.add_url_rule('/', 'index', index, methods=['GET', 'POST'])

from flask import Flask

app = None


def init(root_path, secret_key):
    global app
    template_folder_path = root_path + '/templates'
    static_folder_path = root_path + '/static'
    app = Flask(__name__, template_folder=template_folder_path,
                static_folder=static_folder_path)
    app.secret_key = secret_key


def run():
    app.run(host='0.0.0.0', use_reloader=True)

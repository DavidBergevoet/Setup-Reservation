

def static_file(path):
    return send_from_directory(application.app.static_folder, path)
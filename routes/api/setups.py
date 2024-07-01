from handlers import config_handler


def get():
    return config_handler.configuration_handler.to_json()

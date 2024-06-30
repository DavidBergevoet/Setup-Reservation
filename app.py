from handlers import version_handler, config_handler, reservation_handler
from entities import application
from os import path
from routes import content
from routes.api import api
from atexit import register
from apscheduler.schedulers.background import BackgroundScheduler

absolute_path = path.abspath('./')

# Configuration
config_path = absolute_path + "/config.json"
config_handler.configuration_handler.load(config_path)

# Initialize application
application.init(path.abspath(absolute_path))

# Initialize routes
content.init()
api.init()

if __name__ == '__main__':
    reservation_handler.reservation_handler.from_file(config_handler.configuration_handler.queue_file_path())
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=reservation_handler.reservation_handler.update_time, trigger="interval", seconds=1)
    scheduler.add_job(func=version_handler.update, trigger="interval", minutes=10)
    scheduler.start()
    register(lambda: scheduler.shutdown())
    application.run()

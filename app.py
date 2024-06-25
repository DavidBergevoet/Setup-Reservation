from entities import application
from os import path
from handlers.reservation_handler import reservation_handler
from handlers import version_handler
from routes import pages
from routes.api import api
from atexit import register
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize application
absolute_path = path.abspath('./')
application.init(path.abspath(absolute_path))

# Initialize routes
pages.init()
api.init()

if __name__ == '__main__':
    reservation_handler.from_file()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=reservation_handler.update_time, trigger="interval", seconds=1)
    scheduler.add_job(func=version_handler.update, trigger="interval", seconds=600)
    scheduler.start()
    register(lambda: scheduler.shutdown())
    application.run()

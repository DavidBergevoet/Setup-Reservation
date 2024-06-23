from flask import Flask, redirect, render_template, jsonify, request
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap5
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp, ValidationError
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import csv
import os
import uuid
import subprocess
from datetime import datetime, timedelta

# new imports
from entities import application, defines
from entities.reservation import Reservation
from os import path
from handlers.reservation_handler import reservation_handler
from handlers import version_handler
from routes import pages
from routes.api import api

# Initialize application
absolute_path = os.path.abspath('./')
application.init(os.path.abspath(absolute_path))

# Initialize routes
pages.init()
api.init()

@application.app.route('/static/<path:path>')
def static_file(path):
    return send_from_directory(application.app.static_folder, path)

if __name__ == '__main__':
    reservation_handler.from_file()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=reservation_handler.update_time, trigger="interval", seconds=1)
    scheduler.add_job(func=version_handler.update, trigger="interval", seconds=600)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    application.run()

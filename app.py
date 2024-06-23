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

# Initialize application
absolute_path = os.path.abspath('./')
application.init(os.path.abspath(absolute_path))

# Initialize routes
pages.init()

@application.app.route('/update_reserved', methods=['GET'])
def update_reserved():
    reserved = reservation_handler.current is not None
    return jsonify(reserved=reserved)

@application.app.route('/update_current', methods=['GET'])
def update_current():
    if reservation_handler.current is None:
        return jsonify(None)
    else:
        return jsonify(reservation_handler.current.jsonify(request.remote_addr))

@application.app.route('/update_queue', methods=['GET'])
def update_queue():
    jsonQueue = [item.jsonify(request.remote_addr) for item in reservation_handler.queue]
    return jsonify(jsonQueue)

@application.app.route('/cancel_request', methods=['DELETE'])
def cancel_request():
    requestId = request.form.get('id')
    requestIpAddress = request.remote_addr
    requestExists = False

    # Check if the current reservation is canceled
    if reservation_handler.current != None and \
    reservation_handler.current.ip_address == requestIpAddress and \
    reservation_handler.current.id == requestId:
        requestExists = True
        reservation_handler.current = None
    else: # Check the queue for requests
        for i in range(len(reservation_handler.queue)):
            if reservation_handler.queue[i].ip_address == requestIpAddress and reservation_handler.queue[i].id == requestId:
                requestExists = True
                del reservation_handler.queue[i]
                break

    if requestExists:
        reservation_handler.update()
        reservation_handler.to_file()
        return jsonify("Success"), 200
    else:
        return jsonify("Could not find reservation"), 404

@application.app.route('/static/<path:path>')
def static_file(path):
    return send_from_directory(application.app.static_folder, path)

@application.app.route('/version', methods=['GET'])
def version_request():
    gitHash = version_handler.retrieve_hash()
    return jsonify({"version": gitHash})

if __name__ == '__main__':
    reservation_handler.from_file()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=reservation_handler.update_time, trigger="interval", seconds=1)
    scheduler.add_job(func=version_handler.update, trigger="interval", seconds=600)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    application.run()

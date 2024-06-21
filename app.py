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
from handlers.reservation_handler import ReservationHandler

absolute_path = os.path.abspath('./')
application.init(os.path.abspath(absolute_path))


class ReservationForm(FlaskForm):
    name = StringField("Name", 
            validators=[DataRequired(), Length(2, 40), Regexp("^[a-zA-Z0-9 ]*$", message="Name includes invalid characters. Only use alphanumeric characters and spaces")],
            description="Only alphanumeric characters and spaces allowed")
    minutes = IntegerField("Number of minutes", 
            validators=[DataRequired(), NumberRange(min=1, max=defines.MAX_RESERVATION_TIME)], 
            description=f"All reservations combined can be a maximum of {defines.MAX_RESERVATION_TIME} minute{'s' if defines.MAX_RESERVATION_TIME != 1 else ''}")
    submit = SubmitField("Reserve")
    
    def validate_minutes(form, field):
        reserved_minutes = reservation_handler.get_reserved_minutes(request.remote_addr)
        if reserved_minutes + int(field.data) > defines.MAX_RESERVATION_TIME:
            raise ValidationError(f"You are only able to reserve a combined amount of {defines.MAX_RESERVATION_TIME} minute{'s' if defines.MAX_RESERVATION_TIME != 1 else ''}.\n \
                You are able to reserve {defines.MAX_RESERVATION_TIME - reserved_minutes} more minute{'s' if defines.MAX_RESERVATION_TIME - reserved_minutes != 1 else ''}")

queue_file = "queue.csv"
reservation_handler = ReservationHandler(queue_file)

def RetrieveGitRevisionHash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

def GitPull():
    subprocess.check_output(['git', 'pull'])

@application.app.route('/', methods=['GET', 'POST'])
def index():
    form = ReservationForm()
    if form.validate_on_submit():
        name = form.name.data
        ipAddress = request.remote_addr
        dateTimeNow = floorDateTime(datetime.now())
        minutes = timedelta(minutes = form.minutes.data)
        # If there are no reservations
        if reservation_handler.current is None and len(reservation_handler.queue) == 0:
            startTime = dateTimeNow
        # If there is a current reservation, but none in the queue
        elif len(reservation_handler.queue) == 0:
            startTime = reservation_handler.current.end_time
        # If there is no current reservation, and the new reservation will end before the first next reservation starts
        elif reservation_handler.current is None and dateTimeNow + minutes <= reservation_handler.queue[0].start_time:
            startTime = dateTimeNow
        # If there is no current reservation, and there is only one reservation in the queue
        elif reservation_handler.current is None and len(reservation_handler.queue) == 1:
            startTime = queue[0].end_time
        # If the new reservation would not fit between the current and the first reservation
        else:
            if reservation_handler.current is None:   
                currentItem = reservation_handler.queue[1]
                nextIndex = 1
            else:
                currentItem = reservation_handler.current
                nextIndex = 0

            slotFound = False
            queueLength = len(reservation_handler.queue)

            while nextIndex < queueLength and not slotFound:
                # If the new reservation would fit between the currently selected reservation and the next reservation
                if currentItem.end_time + minutes <= reservation_handler.queue[nextIndex].start_time:
                    startTime = currentItem.end_time
                    slotFound = True
                else:
                    currentItem = reservation_handler.queue[nextIndex]
                    nextIndex += 1

            if not slotFound:
                startTime = reservation_handler.queue[-1].end_time

        endTime = startTime + timedelta(minutes = form.minutes.data)
        reservation_handler.queue.append(Reservation(name, ipAddress, startTime, endTime))
        reservation_handler.queue.sort(key=lambda x: x.start_time)
        if reservation_handler.current is None:
            reservation_handler.update()
        reservation_handler.to_file()
        return redirect("/")
    else:
        return render_template('index.html', form=form)

def floorDateTime(dateTime):
    return dateTime - timedelta(seconds = dateTime.second, microseconds = dateTime.microsecond)

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
    gitHash = RetrieveGitRevisionHash()
    return jsonify({"version": gitHash})

if __name__ == '__main__':
    reservation_handler.from_file()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=reservation_handler.update_time, trigger="interval", seconds=1)
    scheduler.add_job(func=GitPull, trigger="interval", seconds=600)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    application.run()

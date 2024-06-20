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

app = Flask(__name__)
app.secret_key = 'tO$&!|0wkamvVia0?n$NqIRVWOG'
bootstrap = Bootstrap5(app)
dateTimeFormat = '%Y-%m-%d %H:%M'

MAX_RESERVATION_MINUTES = 60

class Reservation:
    def __init__(self, name, ipAddress, startTime, endTime, requestId = None):
        if requestId == None:
            self.id = str(uuid.uuid4())
        else:
            self.id = requestId
        self.name = name
        self.ipAddress = ipAddress
        self.startTime = startTime
        self.endTime = endTime
    def isActive(self):
        dateTimeNow = datetime.now()
        return self.startTime <= dateTimeNow and self.endTime > dateTimeNow
    def hasPassed(self):
        return self.endTime <= datetime.now()
    def jsonify(self, requestIpAddress):
        timeDelta = self.endTime - datetime.now()
        minutes = timeDelta.days * 24 * 60 * 60 + timeDelta.seconds // 60
        startTime = self.startTime.strftime(dateTimeFormat)
        endTime = self.endTime.strftime(dateTimeFormat)
        return {"name": self.name,
            "address": self.ipAddress, 
            "canCancel": self.ipAddress == requestIpAddress,
            "startTime": startTime,
            "endTime": endTime,
            "minutes": minutes,
            "id": self.id}
    def csvify(self):
        return f"{self.name};{self.ipAddress};{self.startTime.strftime(dateTimeFormat)};{self.endTime.strftime(dateTimeFormat)};{self.id}\n"
    def getMinutesReserved(self):
        beginTime = self.startTime if datetime.now() < self.startTime else datetime.now()
        timeDelta = self.endTime - beginTime
        return timeDelta.days * 24 * 60 * 60 + timeDelta.seconds // 60

class ReservationForm(FlaskForm):
    name = StringField("Name", 
            validators=[DataRequired(), Length(2, 40), Regexp("^[a-zA-Z0-9 ]*$")],
            description="Only alphanumeric characters allowed")
    minutes = IntegerField("Number of minutes", 
            validators=[DataRequired(), NumberRange(min=1, max=MAX_RESERVATION_MINUTES)], 
            description=f"All reservations combined can be a maximum of {MAX_RESERVATION_MINUTES} minutes")
    submit = SubmitField("Reserve")
    
    def validate_minutes(form, field):
        reserved_minutes = GetReservedMinutes(request.remote_addr)
        if reserved_minutes + int(field.data) > MAX_RESERVATION_MINUTES:
            raise ValidationError(f"You are only able to reserve a maximum amount of time of {MAX_RESERVATION_MINUTES} minutes.\n \
                You are able to reserve {MAX_RESERVATION_MINUTES - reserved_minutes} minutes")


current = None
queue = []
queueFile = "queue.csv"

def UpdateQueueFromFile():
    if os.path.exists(queueFile):
        with open(queueFile, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            queue.clear()
            for row in reader:
                if len(row) == 5:
                    name = row[0]
                    ipAddress = row[1]
                    startTime = datetime.strptime(row[2], dateTimeFormat)
                    endTime = datetime.strptime(row[3], dateTimeFormat)
                    requestId = row[4]

                    reservation = Reservation(name, ipAddress, startTime, endTime, requestId)
                    queue.append(reservation)
            queue.sort(key=lambda x: x.startTime)
            UpdateCurrentFromQueue()

def UpdateFileFromQueue():
    global current, queue
    file = open(queueFile, 'w')
    if current != None:
        file.write(current.csvify())
    for reservation in queue:
        file.write(reservation.csvify())

def UpdateCurrentFromQueue(updateFileFromQueue = True):
    global current, queue
    if current is None and len(queue) != 0:
        queue.sort(key=lambda x: x.startTime)
        potentialCurrent = queue[0]

        shouldUpdateFile = False

        while potentialCurrent is not None and potentialCurrent.hasPassed():
            queue = queue[1:]
            shouldUpdateFile = True
            if len(queue) != 0:
                potentialCurrent = queue[0]
            else:
                potentialCurrent = None

        if potentialCurrent is not None and potentialCurrent.isActive():
            current = queue.pop(0)
            shouldUpdateFile = True
            
        if shouldUpdateFile and updateFileFromQueue:
            UpdateFileFromQueue()

def UpdateCurrentTimer():
    global current
    if current is not None:
        if not current.isActive():
            current = None
            UpdateCurrentFromQueue(False)
            UpdateFileFromQueue()

def GetReservedMinutes(address):
    global current, queue
    reserved_minutes = 0
    if current != None and current.ipAddress == address:
        reserved_minutes = current.getMinutesReserved()
    for reservation in queue:
        if reservation.ipAddress == address:
            reserved_minutes += reservation.getMinutesReserved()
    return reserved_minutes

def RetrieveGitRevisionHash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

def GitPull():
    subprocess.check_output(['git', 'pull'])

@app.route('/', methods=['GET', 'POST'])
def index():
    global current, queue
    form = ReservationForm()
    if form.validate_on_submit():
        name = form.name.data
        ipAddress = request.remote_addr
        dateTimeNow = floorDateTime(datetime.now())
        minutes = timedelta(minutes = form.minutes.data)
        # If there are no reservations
        if current is None and len(queue) == 0:
            startTime = dateTimeNow
        # If there is a current reservation, but none in the queue
        elif len(queue) == 0:
            startTime = current.endTime
        # If there is no current reservation, and the new reservation will end before the first next reservation starts
        elif current is None and dateTimeNow + minutes <= queue[0].startTime:
            startTime = dateTimeNow
        # If there is no current reservation, and there is only one reservation in the queue
        elif current is None and len(queue) == 1:
            startTime = queue[0].endTime
        # If the new reservation would not fit between the current and the first reservation
        else:
            if current is None:   
                currentItem = queue[1]
                nextIndex = 1
            else:
                currentItem = current
                nextIndex = 0

            slotFound = False
            queueLength = len(queue)

            while nextIndex < queueLength and not slotFound:
                # If the new reservation would fit between the currently selected reservation and the next reservation
                if currentItem.endTime + minutes <= queue[nextIndex].startTime:
                    startTime = currentItem.endTime
                    slotFound = True
                else:
                    currentItem = queue[nextIndex]
                    nextIndex += 1

            if not slotFound:
                startTime = queue[-1].endTime

        endTime = startTime + timedelta(minutes = form.minutes.data)
        queue.append(Reservation(name, ipAddress, startTime, endTime))
        queue.sort(key=lambda x: x.startTime)
        if current is None:
            UpdateCurrentFromQueue(False)
        UpdateFileFromQueue()
        return redirect("/")
    else:
        return render_template('index.html', form=form)

def floorDateTime(dateTime):
    return dateTime - timedelta(seconds = dateTime.second, microseconds = dateTime.microsecond)

@app.route('/update_reserved', methods=['GET'])
def update_reserved():
    global current
    reserved = current is not None
    return jsonify(reserved=reserved)

@app.route('/update_current', methods=['GET'])
def update_current():
    global current
    if current is None:
        return jsonify(None)
    else:
        return jsonify(current.jsonify(request.remote_addr))

@app.route('/update_queue', methods=['GET'])
def update_queue():
    global queue
    jsonQueue = [item.jsonify(request.remote_addr) for item in queue]
    return jsonify(jsonQueue)

@app.route('/cancel_request', methods=['DELETE'])
def cancel_request():
    global current, queue
    requestId = request.form.get('id')
    requestIpAddress = request.remote_addr
    requestExists = False

    # Check if the current reservation is canceled
    if current != None and current.ipAddress == requestIpAddress and current.id == requestId:
        requestExists = True
        current = None
    else: # Check the queue for requests
        for i in range(len(queue)):
            if queue[i].ipAddress == requestIpAddress and queue[i].id == requestId:
                requestExists = True
                del queue[i]
                break

    if requestExists:
        UpdateCurrentFromQueue(False)
        UpdateFileFromQueue()
        return jsonify("Success"), 200
    else:
        return jsonify("Could not find reservation"), 404

@app.route('/static/<path:path>')
def static_file(path):
    return send_from_directory('static', path)

@app.route('/version', methods=['GET'])
def version_request():
    gitHash = RetrieveGitRevisionHash()
    return jsonify({"version": gitHash})

if __name__ == '__main__':
    UpdateQueueFromFile()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=UpdateCurrentTimer, trigger="interval", seconds=1)
    scheduler.add_job(func=GitPull, trigger="interval", seconds=600)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    app.run(host='0.0.0.0',use_reloader=True)

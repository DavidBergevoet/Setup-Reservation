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

app = Flask(__name__)
app.secret_key = 'tO$&!|0wkamvVia0?n$NqIRVWOG'
bootstrap = Bootstrap5(app)

MAX_RESERVATION_MINUTES = 60

class Reservation:
    def __init__(self, name, minutes, ipAddress, requestId = None):
        if requestId == None:
            self.id = str(uuid.uuid4())
        else:
            self.id = requestId
        self.name = name
        self.minutes = int(minutes)
        self.ipAddress = ipAddress
    def decreaseMinutes(self):
        self.minutes -= 1
    def jsonify(self, requestIpAddress):
        return {"name": self.name, 
            "minutes": self.minutes, 
            "address": self.ipAddress, 
            "canCancel": self.ipAddress == requestIpAddress,
            "id": self.id}
    def csvify(self):
        return f"{self.name};{self.minutes};{self.ipAddress};{self.id}\n"
    def duration(self):
        return self.minutes

class ReservationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(2, 40), Regexp("^[a-zA-Z0-9 ]*$")])
    minutes = IntegerField("Number of minutes", validators=[DataRequired(), NumberRange(min=1, max=MAX_RESERVATION_MINUTES)])
    submit = SubmitField("Reserve")
    def validate_minutes(form, field):
        global current, queue
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
                if len(row) == 4:
                    reservation = Reservation(row[0], row[1], row[2], row[3])
                    queue.append(reservation)
            UpdateCurrentFromQueue()

def UpdateFileFromQueue():
    global current, queue
    file = open(queueFile, 'w')
    if current != None:
        file.write(current.csvify())
    for reservation in queue:
        file.write(reservation.csvify())

def UpdateCurrentFromQueue():
    global current, queue
    if current is None and len(queue) != 0:
        current = queue.pop(0)
        UpdateFileFromQueue()

def UpdateCurrentTimer():
    global current
    if current is not None:
        current.decreaseMinutes()
        if current.minutes == 0:
            current = None
            UpdateCurrentFromQueue()
        UpdateFileFromQueue()

def GetReservedMinutes(address):
    global current, queue
    reserved_minutes = 0
    if current != None and current.ipAddress == address:
        reserved_minutes = current.minutes
    for reservation in queue:
        if reservation.ipAddress == address:
            reserved_minutes += reservation.minutes
    return reserved_minutes

def RetrieveGitRevisionHash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

def GitPull():
    subprocess.check_output(['git', 'pull'])

@app.route('/', methods=['GET', 'POST'])
def index():
    global current
    form = ReservationForm()
    if form.validate_on_submit():
        name = form.name.data
        minutes = form.minutes.data
        ipAddress = request.remote_addr
        queue.append(Reservation(name, minutes, ipAddress))
        if current is None:
            UpdateCurrentFromQueue()
        UpdateFileFromQueue()
        return redirect("/")
    else:
        return render_template('index.html', form=form)

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
        UpdateCurrentFromQueue()
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
    scheduler.add_job(func=UpdateCurrentTimer, trigger="interval", seconds=60)
    scheduler.add_job(func=GitPull, trigger="interval", seconds=600)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    app.run(host='0.0.0.0',use_reloader=True)

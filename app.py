from flask import Flask, render_template, jsonify, request
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap5
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import csv
import os

app = Flask(__name__)
app.secret_key = 'tO$&!|0wkamvVia0?n$NqIRVWOG'
bootstrap = Bootstrap5(app)

class Reservation:
    def __init__(self, name, minutes, ipAddress):
        self.name = name
        self.minutes = int(minutes)
        self.ipAddress = ipAddress
    def decreaseMinutes(self):
        self.minutes -= 1
    def jsonify(self):
        return {"name": self.name, "minutes": self.minutes, "address": self.ipAddress}
    def csvify(self):
        return f"{self.name};{self.minutes};{self.ipAddress}\n"

class ReservationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(2, 40), Regexp("^[a-zA-Z0-9 ]*$")])
    minutes = IntegerField("Number of minutes", validators=[DataRequired(), NumberRange(min=1, max=120)])
    submit = SubmitField("Reserve")

current = None
queue = []
queueFile = "queue.csv"

def UpdateQueueFromFile():
    if os.path.exists(queueFile):
        with open(queueFile, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            queue.clear()
            for row in reader:
                if len(row) == 3:
                    reservation = Reservation(row[0], row[1], row[2])
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
        return jsonify(current.jsonify())

@app.route('/update_queue', methods=['GET'])
def update_queue():
    global queue
    jsonQueue = [item.jsonify() for item in queue]
    return jsonify(jsonQueue)

if __name__ == '__main__':
    UpdateQueueFromFile()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=UpdateCurrentTimer, trigger="interval", seconds=60)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    app.run(host='0.0.0.0',debug=True)

from uuid import uuid4
from datetime import datetime, timedelta
from entities import defines


class Reservation:
    def __init__(self, name, ip_address, start_time, end_time, request_id=None):
        if request_id == None:
            self.id = str(uuid4())
        else:
            self.id = request_id
        self.name = name
        self.ip_address = ip_address
        self.start_time = start_time
        self.end_time = end_time

    def is_active(self):
        datetime_now = datetime.now()
        return self.start_time <= datetime_now and self.end_time > datetime_now

    def has_passed(self):
        return self.end_time <= datetime.now()

    def jsonify(self, request_ip_address):
        time_delta = self.end_time - datetime.now()
        minutes = time_delta.days * 24 * 60 * 60 + time_delta.seconds // 60
        start_time = self.start_time.strftime(defines.DATETIME_FORMAT)
        end_time = self.end_time.strftime(defines.DATETIME_FORMAT)
        return {"name": self.name,
                "address": self.ip_address,
                "can_cancel": self.ip_address == request_ip_address,
                "start_time": start_time,
                "end_time": end_time,
                "minutes": minutes,
                "id": self.id}

    def csvify(self):
        return f"{self.name};{self.ip_address};{self.start_time.strftime(defines.DATETIME_FORMAT)};{self.end_time.strftime(defines.DATETIME_FORMAT)};{self.id}\n"

    def get_minutes_reserved(self):
        begin_time = self.start_time if datetime.now() < self.start_time else datetime.now()
        time_delta = self.end_time - begin_time
        return time_delta.days * 24 * 60 * 60 + time_delta.seconds // 60

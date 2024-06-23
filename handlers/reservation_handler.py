from entities.reservation import Reservation
from os import path
from csv import reader
from datetime import datetime, timedelta
from entities import defines

class ReservationHandler:
	def __init__(self, queue_file_path):
		self.queue_file_path = queue_file_path
		self.queue = []
		self.current = None

	def from_file(self):
		if path.exists(self.queue_file_path):
			with open(self.queue_file_path, newline='') as csv_file:
				csv_reader = reader(csv_file, delimiter=';')
				self.queue.clear()
				for row in csv_reader:
					if len(row) == 5:
						name = row[0]
						ip_address = row[1]
						start_time = datetime.strptime(row[2], defines.DATETIME_FORMAT)
						end_time = datetime.strptime(row[3], defines.DATETIME_FORMAT)
						request_id = row[4]

						reservation = Reservation(name, ip_address, start_time, end_time, request_id)
						self.queue.append(reservation)
				self.queue.sort(key=lambda x: x.start_time)
				self.update()
		else:
			print(f"File '{self.queue_file_path}' cannot be opened")

	def to_file(self):
		file = open(self.queue_file_path, 'w')
		if self.current != None:
			file.write(self.current.csvify())
		for reservation in self.queue:
			file.write(reservation.csvify())

	def update(self):
		if self.current is None and len(self.queue) != 0:
			self.queue.sort(key=lambda x: x.start_time)
			potential_current = self.queue[0]

			should_update_file = False

			while potential_current is not None and potential_current.has_passed():
				self.queue = queue[1:]
				should_update_file = True
				if len(self.queue) != 0:
					potential_current = self.queue[0]
				else:
					potential_current = None

			if potential_current is not None and potential_current.is_active():
				self.current = self.queue.pop(0)
				should_update_file = True
			    
			if should_update_file:
				self.to_file()

	def update_time(self):
		if self.current is not None:
			if not self.current.is_active():
				self.current = None
				self.update()
				self.to_file()

	def get_reserved_minutes(self, address):
		reserved_minutes = 0
		if self.current != None and self.current.ip_address == address:
			reserved_minutes = self.current.get_minutes_reserved()
		for reservation in self.queue:
			if reservation.ip_address == address:
				reserved_minutes += reservation.get_minutes_reserved()
		return reserved_minutes

reservation_handler = ReservationHandler('queue.csv')

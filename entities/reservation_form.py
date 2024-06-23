from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp, ValidationError
from entities.reservation import Reservation
from entities import defines
from handlers.reservation_handler import reservation_handler

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

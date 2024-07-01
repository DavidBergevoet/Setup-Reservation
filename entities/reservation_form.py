from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp, ValidationError
from entities.reservation import Reservation
from entities import defines
from handlers.reservation_handler import reservation_handler
from handlers.config_handler import configuration_handler


class ReservationForm(FlaskForm):
    name = StringField("Name",
                       validators=[DataRequired(), Length(2, 40), Regexp(
                           "^[a-zA-Z0-9 ]*$", message="Name includes invalid characters. Only use alphanumeric characters and spaces")],
                       description="Only alphanumeric characters and spaces allowed")
    minutes = IntegerField("Number of minutes", description="")
    submit = SubmitField("Reserve")

    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        max_minutes = configuration_handler.maximum_minutes()
        self.minutes.description = f"All reservations combined can be a maximum of {max_minutes} minute{'s' if max_minutes != 1 else ''}"
        self.minutes.validators = [
            DataRequired(), NumberRange(min=1, max=max_minutes)]

    def validate_minutes(form, field):
        reserved_minutes = reservation_handler.get_reserved_minutes(
            request.remote_addr)
        max_minutes = configuration_handler.maximum_minutes()
        if reserved_minutes + int(field.data) > max_minutes:
            raise ValidationError(f"You are only able to reserve a combined amount of {max_minutes} minute{'s' if max_minutes != 1 else ''}.\n \
            You are able to reserve {max_minutes - reserved_minutes} more minute{'s' if max_minutes - reserved_minutes != 1 else ''}")

from datetime import datetime, timedelta
from flask import render_template, request, redirect
from entities import defines
from entities.reservation import Reservation
from entities.reservation_form import ReservationForm
from handlers.reservation_handler import reservation_handler
from handlers.config_handler import configuration_handler


def index():
    form = ReservationForm()
    if form.validate_on_submit():
        name = form.name.data
        ip_address = request.remote_addr
        datetime_now = defines.floor_datetime(datetime.now())
        minutes = timedelta(minutes=form.minutes.data)
        # If there are no reservations
        if reservation_handler.current is None and len(reservation_handler.queue) == 0:
            start_time = datetime_now
        # If there is a current reservation, but none in the queue
        elif len(reservation_handler.queue) == 0:
            start_time = reservation_handler.current.end_time
        # If there is no current reservation, and the new reservation will end before the first next reservation starts
        elif reservation_handler.current is None and datetime_now + minutes <= reservation_handler.queue[0].start_time:
            start_time = datetime_now
        # If there is no current reservation, and there is only one reservation in the queue
        elif reservation_handler.current is None and len(reservation_handler.queue) == 1:
            start_time = reservation_handler.queue[0].end_time
        # If the new reservation would not fit between the current and the first reservation
        else:
            if reservation_handler.current is None:
                current_item = reservation_handler.queue[1]
                next_index = 1
            else:
                current_item = reservation_handler.current
                next_index = 0

            slot_found = False
            queue_length = len(reservation_handler.queue)

            while next_index < queue_length and not slot_found:
                # If the new reservation would fit between the currently selected reservation and the next reservation
                if current_item.end_time + minutes <= reservation_handler.queue[next_index].start_time:
                    start_time = current_item.end_time
                    slot_found = True
                else:
                    current_item = reservation_handler.queue[next_index]
                    next_index += 1

            if not slot_found:
                start_time = reservation_handler.queue[-1].end_time

        end_time = start_time + timedelta(minutes=form.minutes.data)
        reservation_handler.queue.append(Reservation(
            name, ip_address, start_time, end_time))
        reservation_handler.queue.sort(key=lambda x: x.start_time)
        if reservation_handler.current is None:
            reservation_handler.update()
        reservation_handler.to_file()
        return redirect("/")
    else:
        return render_template('index.html',
                               form=form,
                               title=configuration_handler.title(),
                               setup_name=configuration_handler.name(),
                               setup_image=configuration_handler.title_image())

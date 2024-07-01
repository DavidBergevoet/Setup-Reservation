from flask import jsonify, request
from handlers.reservation_handler import reservation_handler


def update_reserved():
    reserved = reservation_handler.current is not None
    return jsonify(reserved=reserved)


def update_current():
    if reservation_handler.current is None:
        return jsonify(None)
    else:
        return jsonify(reservation_handler.current.jsonify(request.remote_addr))


def update_queue():
    json_queue = [item.jsonify(request.remote_addr)
                  for item in reservation_handler.queue]
    return jsonify(json_queue)


def cancel_request():
    request_id = request.form.get('id')
    request_ip_address = request.remote_addr
    request_exists = False

    # Check if the current reservation is canceled
    if reservation_handler.current != None and \
            reservation_handler.current.ip_address == request_ip_address and \
            reservation_handler.current.id == request_id:
        request_exists = True
        reservation_handler.current = None
    else:  # Check the queue for requests
        for i in range(len(reservation_handler.queue)):
            if reservation_handler.queue[i].ip_address == request_ip_address and reservation_handler.queue[i].id == request_id:
                request_exists = True
                del reservation_handler.queue[i]
                break

    if request_exists:
        reservation_handler.update()
        reservation_handler.to_file()
        return ('', 204)
    else:
        return jsonify("Could not find reservation"), 404

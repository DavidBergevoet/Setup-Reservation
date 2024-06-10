$(() => {
    const roomStatus = $("#room-status");
    const cancelReservationBtn = $("#cancel-reservation-btn");
    const reservationInfo = $("#reservation-info");
    const reservations = $(".reservations");
    const reservationsBody = reservations.find('tbody');
    const noReservationsMessage = $("#no-reservations-message");

    cancelReservationBtn.on('click', () => {
        if (cancelReservationBtn.hasClass("hidden") || !cancelReservationBtn.data('request-id')) {
            return;
        }
        if (confirm("Are you sure you want to cancel the active reservation?")) {
            cancelRequest(cancelReservationBtn.data('request-id'));
        }
    })

    function updateCurrent() {
        $.get('/update_current', function (data) {
            roomStatus.removeClass("not-available");
            roomStatus.removeClass("available");
            cancelReservationBtn.addClass("hidden");
            cancelReservationBtn.data('request-id', null);
            reservationInfo.addClass("hidden");

            if (data != null) {
                roomStatus.addClass("not-available");
                roomStatus.text("Setup is not available");
                reservationInfo.removeClass("hidden");
                reservationInfo.find('.name').text(data.name);
                reservationInfo.find('.time-left').text(data.minutes);
                cancelReservationBtn.data('request-id', data.id);

                if (data.canCancel) {
                    cancelReservationBtn.removeClass("hidden");
                }
            }
            else {
                roomStatus.addClass("available");
                roomStatus.text("Setup is available");
            }
        });
    }

    function updateQueue() {
        $.get('/update_queue', function (data) {
            reservationsBody.empty();
            reservations.addClass("hidden");
            noReservationsMessage.addClass("hidden");

            if (data.length == 0) {
                noReservationsMessage.text("There are no upcoming reservations")
                noReservationsMessage.removeClass("hidden");
                return;
            }

            reservations.removeClass("hidden");

            for (var i = 0; i < data.length; i++) {
                var reservation = data[i];

                var tableRow = $("<tr>");

                var nameColumn = $("<td>");
                nameColumn.data('label', "Name");
                nameColumn.text(reservation.name);
                tableRow.append(nameColumn);

                var minutesColumn = $("<td>");
                minutesColumn.data('label', "Minutes left");
                minutesColumn.text(reservation.minutes);
                tableRow.append(minutesColumn);

                if (reservation.canCancel) {
                    var cancelColumn = $("<td>");
                    cancelColumn.data('label', "Action");
                    var cancelButton = $("<button>Cancel</button>");
                    cancelButton.addClass("cancel-btn");
                    (function (reservation) {
                        cancelButton.on('click', () => {
                            if (confirm("Are you sure you want to cancel this reservation?")) {
                                cancelRequest(reservation.id);
                            }
                        })
                    })(reservation)
                    cancelColumn.append(cancelButton);
                    tableRow.append(cancelColumn);
                }

                reservationsBody.append(tableRow);
            }
        });
    }

    function cancelRequest(identifier) {
        $.ajax({
            url: '/cancel_request',
            type: 'DELETE',
            data: { id: identifier },
            success: function (response) {
                update()
            },
            error: function (error) {
                console.error('Error cancelling request:', error);
            }
        });
    }

    function update() {
        updateCurrent();
        updateQueue();
    }

    update();
    setInterval(update, 10000);
})
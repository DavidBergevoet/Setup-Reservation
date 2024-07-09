$(() => {
    const roomStatus = $("#room-status");
    const cancelReservationBtn = $("#cancel-reservation-btn");
    const reservationInfo = $("#reservation-info");
    const reservations = $(".reservations");
    const reservationsBody = reservations.find('tbody');
    const noReservationsMessage = $("#no-reservations-message");
    var serverVersion = undefined;

    cancelReservationBtn.on('click', () => {
        if (cancelReservationBtn.hasClass("hidden") || !cancelReservationBtn.data('request-id')) {
            return;
        }
        if (confirm("Are you sure you want to cancel the active reservation?")) {
            cancelRequest(cancelReservationBtn.data('request-id'));
        }
    })

    function updateCurrent() {
        $.get('/api/update_current', function (data) {
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
                reservationInfo.find('.start-time').text(convertTimeString(data.start_time));
                reservationInfo.find('.end-time').text(convertTimeString(data.end_time));
                if (data.minutes == 0) {
                    reservationInfo.find('.remaining-minutes').text('Less than 1 minute')
                }
                else {
                    reservationInfo.find('.remaining-minutes').text(data.minutes);
                }
                cancelReservationBtn.data('request-id', data.id);

                if (data.can_cancel) {
                    cancelReservationBtn.removeClass("hidden");
                }
            }
            else {
                roomStatus.addClass("available");
                roomStatus.text("Setup is available");
            }
        });
    }
    
    function convertTimeString(timeString) {
        const date = new Date(timeString);
        const locale = navigator.language;
        const formattedTime = new Intl.DateTimeFormat(locale, {
            timeStyle: "short"
        }).format(date);

        return formattedTime;
    }

    function updateQueue() {
        $.get('/api/update_queue', function (data) {
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
                
                var startTimeColumn = $("<td>");
                startTimeColumn.data('label', "Start time");
                startTimeColumn.text(convertTimeString(reservation.start_time));
                tableRow.append(startTimeColumn);

                
                var endTimeColumn = $("<td>");
                endTimeColumn.data('label', "End time");
                endTimeColumn.text(convertTimeString(reservation.end_time));
                tableRow.append(endTimeColumn);

                if (reservation.can_cancel) {
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

    function updateVersion() {
        $.get('/api/version', function (data) {
            if (serverVersion) {
                if (serverVersion != data.version) {
                    location.reload(true);
                }
            } else {
                serverVersion = data.version;
            }
        });
    }

    function cancelRequest(identifier) {
        $.ajax({
            url: '/api/cancel_request',
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
        updateVersion();
    }
    update();
    setInterval(update, 10000);
})
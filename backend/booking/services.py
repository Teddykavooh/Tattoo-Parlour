from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import (
    Artist,
    Service,
    Customer,
    WorkingHours,
    BlockedTime,
    Appointment,
)


@transaction.atomic
def create_booking(
    *,
    artist_id,
    customer_id,
    service_id,
    start_time,
    tattoo_description=""
):
    # Validate timezone-aware datetime
    if timezone.is_naive(start_time):
        raise ValidationError(
            "Appointment time must include a timezone."
        )

    if start_time <= timezone.now():
        raise ValidationError(
            "Please select a future appointment time."
        )

    # Lock the artist to prevent concurrent bookings.
    artist = (
        Artist.objects
        .select_for_update()
        .get(pk=artist_id, is_active=True)
    )

    service = Service.objects.get(
        pk=service_id,
        is_active=True
    )

    customer = Customer.objects.get(pk=customer_id)

    # Calculate actual appointment duration.
    appointment_duration = timedelta(
        minutes=service.duration_minutes
    )

    buffer_duration = timedelta(
        minutes=service.buffer_minutes
    )

    # Calculate appointment boundaries.
    end_time = start_time + appointment_duration

    reserved_until = end_time + buffer_duration

    local_start = timezone.localtime(start_time)
    local_end = timezone.localtime(end_time)
    local_reserved_until = timezone.localtime(reserved_until)

    # Ensure the reservation fits within one working day.
    if (
        local_start.date() != local_end.date()
        or local_start.date() != local_reserved_until.date()
    ):
        raise ValidationError(
            "Appointments cannot extend beyond working hours."
        )

    # Retrieve artist working hours.
    working_hours = WorkingHours.objects.filter(
        artist=artist,
        weekday=local_start.weekday()
    ).first()

    if not working_hours:
        raise ValidationError(
            "The artist does not work on this day."
        )

    # Validate the entire reserved period, including buffer.
    if not (
        working_hours.start_time <= local_start.time()
        and local_reserved_until.time() <= working_hours.end_time
    ):
        raise ValidationError(
            "The selected time is outside working hours."
        )

    # Check blocked periods, including the buffer.
    if BlockedTime.objects.filter(
        artist=artist,
        start_time__lt=reserved_until,
        end_time__gt=start_time
    ).exists():
        raise ValidationError(
            "The artist is unavailable during this period."
        )

    active_statuses = [
        Appointment.Status.PENDING,
        Appointment.Status.CONFIRMED,
    ]

    # Check overlapping appointments.
    if Appointment.objects.filter(
        artist=artist,
        status__in=active_statuses,
        start_time__lt=reserved_until,
        reserved_until__gt=start_time
    ).exists():
        raise ValidationError(
            "This appointment slot is already occupied."
        )

    # Create pending appointment.
    return Appointment.objects.create(
        artist=artist,
        customer=customer,
        service=service,
        start_time=start_time,
        end_time=end_time,
        reserved_until=reserved_until,
        quoted_price=service.price,
        tattoo_description=tattoo_description,
        status=Appointment.Status.PENDING
    )

from django.db import models
from django.db.models import Q, F

# Create your models here.

class Artist(models.Model):
    name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(
        upload_to="artists/",
        blank=True,
        null=True
    )
    specialties = models.CharField(
        max_length=255,
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    duration_minutes = models.PositiveIntegerField(
        help_text="Estimated appointment duration in minutes"
    )

    buffer_minutes = models.PositiveIntegerField(
        default=15,
        help_text="Preparation and cleaning time after appointment"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class WorkingHours(models.Model):
    WEEKDAYS = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="working_hours"
    )

    weekday = models.PositiveSmallIntegerField(
        choices=WEEKDAYS
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["artist", "weekday"],
                name="unique_artist_workday"
            ),
            models.CheckConstraint(
                condition=Q(end_time__gt=F("start_time")),
                name="valid_working_hours"
            )
        ]

    def __str__(self):
        return f"{self.artist} - {self.get_weekday_display()}"


class BlockedTime(models.Model):
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="blocked_times"
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    reason = models.CharField(
        max_length=255,
        blank=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(end_time__gt=F("start_time")),
                name="valid_blocked_time"
            )
        ]


class Appointment(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"

    artist = models.ForeignKey(
        Artist,
        on_delete=models.PROTECT,
        related_name="appointments"
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="appointments"
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="appointments"
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # Preserve the quoted price even if service pricing changes.
    quoted_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    tattoo_description = models.TextField(blank=True)

    reference_image = models.ImageField(
        upload_to="appointment_references/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    reserved_until = models.DateTimeField()

    admin_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]
        indexes = [
            models.Index(
                fields=["artist", "start_time", "end_time"]
            ),
            models.Index(fields=["status", "start_time"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_time__gt=F("start_time")),
                name="valid_appointment_duration"
            )
        ]

    def __str__(self):
        return f"{self.customer} - {self.start_time}"

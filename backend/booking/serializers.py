from rest_framework import serializers

from .models import (
    Artist,
    Service,
    Customer,
    Appointment,
)


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = [
            "id",
            "name",
            "bio",
            "profile_image",
            "specialties",
        ]


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "description",
            "duration_minutes",
            "buffer_minutes",
            "price",
        ]


class BookingCreateSerializer(serializers.Serializer):
    # Optional while there is only one active artist.
    # When multiple artists are active, the customer can select one.
    artist = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.filter(is_active=True),
        required=False
    )

    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.filter(is_active=True)
    )

    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=30)

    start_time = serializers.DateTimeField()

    tattoo_description = serializers.CharField(
        required=False,
        allow_blank=True
    )

    reference_image = serializers.ImageField(
        required=False,
        allow_null=True
    )

    def validate_start_time(self, value):
        from django.utils import timezone

        if value <= timezone.now():
            raise serializers.ValidationError(
                "Please select a future appointment time."
            )

        return value

    def validate(self, attrs):
        active_artists = Artist.objects.filter(is_active=True)

        if not active_artists.exists():
            raise serializers.ValidationError(
                "There are currently no artists available for bookings."
            )

        if not attrs.get("artist"):
            if active_artists.count() > 1:
                raise serializers.ValidationError({
                    "artist": "Please select an artist."
                })

        return attrs


class AppointmentSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)

    customer_name = serializers.CharField(
        source="customer.full_name",
        read_only=True
    )

    customer_email = serializers.EmailField(
        source="customer.email",
        read_only=True
    )

    customer_phone = serializers.CharField(
        source="customer.phone",
        read_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            "id",
            "artist",
            "service",
            "customer_name",
            "customer_email",
            "customer_phone",
            "start_time",
            "end_time",
            "reserved_until",
            "quoted_price",
            "tattoo_description",
            "reference_image",
            "status",
            "admin_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import (
    Artist,
    Service,
    Customer,
    WorkingHours,
    BlockedTime,
    Appointment,
)

class WorkingHoursInline(admin.TabularInline):
    model = WorkingHours
    extra = 1


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "specialities",
        "is_active",
        "created_at",
    )

    list_filter = ("is_active",)
    search_fields = ("name", "specialities")
    list_editable = ("is_active",)
    inlines = [WorkingHoursInline]

    # Prefer deactivation to deletion because appointments
    # may reference this artist.
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "duration_minutes",
        "buffer_minutes",
        "price",
        "is_active",
    )

    list_filter = ("is_active",)
    search_fields = ("name", "description")
    list_editable = ("is_active",)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BlockedTime)
class BlockedTimeAdmin(admin.ModelAdmin):
    list_display = (
        "artist",
        "start_time",
        "end_time",
        "reason",
    )

    list_filter = ("artist",)
    search_fields = ("artist__name", "reason")
    date_hierarchy = "start_time"


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "phone",
        "created_at",
    )

    search_fields = ("full_name", "email", "phone")
    readonly_fields = ("created_at",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "artist",
        "service",
        "start_time",
        "status",
    )

    list_filter = (
        "status",
        "artist",
        "service",
    )

    search_fields = (
        "customer__full_name",
        "customer__phone",
        "customer__email",
    )

    date_hierarchy = "start_time"

    readonly_fields = (
        "artist",
        "customer",
        "service",
        "start_time",
        "end_time",
        "reserved_until",
        "quoted_price",
        "tattoo_description",
        "reference_image",
        "status",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

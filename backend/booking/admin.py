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

admin.site.register(Artist)
admin.site.register(Service)
admin.site.register(Customer)
admin.site.register(WorkingHours)
admin.site.register(BlockedTime)
admin.site.register(Appointment)
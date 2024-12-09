from django.contrib import admin
from .models import Booking, UserProfile


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "car_plate",
        "date",
        "start_time",
        "end_time",
        "amount",
        "paid",
    )
    list_filter = ("paid", "date")
    search_fields = ("car_plate",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "car_plate")
    search_fields = ("user__username", "car_plate")

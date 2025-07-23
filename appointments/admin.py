from django.contrib import admin
from .models import Appointment, AvailableSlot

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'patient', 'date', 'time', 'status', 'is_paid')
    list_filter = ('status', 'date', 'doctor')
    search_fields = ('doctor__user__full_name', 'patient__user__full_name', 'notes')
    ordering = ('-date', 'time')

@admin.register(AvailableSlot)
class AvailableSlotAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'date', 'start_time', 'end_time')
    list_filter = ('doctor', 'date')
    search_fields = ('doctor__user__full_name',)
    ordering = ('-date', 'start_time')

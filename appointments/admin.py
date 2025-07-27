from django.contrib import admin
from .models import Appointment, AvailableSlot, Insurance

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

@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ('provider', 'patient', 'policy_number', 'coverage_percent', 'valid_until')
    list_filter = ('provider', 'valid_until')
    search_fields = ('provider', 'policy_number', 'patient__first_name', 'patient__last_name')
    date_hierarchy = 'valid_until'
    raw_id_fields = ('patient',)
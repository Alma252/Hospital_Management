from rest_framework import serializers
from .models import Appointment, AvailableSlot


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['status', 'created_at', 'updated_at', 'patient']


class AvailableSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableSlot
        fields = ['id', 'doctor', 'date', 'start_time', 'end_time']
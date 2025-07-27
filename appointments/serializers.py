from rest_framework import serializers
from .models import Appointment, AvailableSlot, Insurance
from users.serializers import DoctorSerializer, PatientSerializer  # ایمپورت کن

class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insurance
        fields = ['id', 'provider', 'policy_number', 'coverage_percent', 'valid_until']


class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    patient = PatientSerializer(read_only=True)
    insurance_used = InsuranceSerializer(read_only=True)
    insurance_used_id = serializers.PrimaryKeyRelatedField(
        queryset=Insurance.objects.all(), write_only=True, source='insurance_used'
    )

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['status', 'created_at', 'updated_at', 'patient', 'insurance_used', 'insurance_used_id']


class AvailableSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableSlot
        fields = ['id', 'doctor', 'date', 'start_time', 'end_time']




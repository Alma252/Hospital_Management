from django.db import models
from users.models import Doctor, Patient


class Insurance(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurances')
    provider = models.CharField(max_length=255)  # نام شرکت بیمه
    policy_number = models.CharField(max_length=100, unique=True)  # شماره بیمه‌نامه
    coverage_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # درصد پوشش بیمه
    valid_until = models.DateField(null=True, blank=True)  # تاریخ اعتبار بیمه

    def __str__(self):
        return f"{self.provider} - {self.policy_number}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    fee = models.DecimalField(max_digits=10, decimal_places=0, default=500000)  # به تومان یا ریال
    is_paid = models.BooleanField(default=False)
    insurance_used = models.ForeignKey(Insurance, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('doctor', 'date', 'time')

    def __str__(self):
        return f"{self.patient.user.full_name} - {self.doctor.user.full_name} ({self.date} {self.time})"


class AvailableSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='available_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()




from django.db import models
from users.models import Doctor, Patient

# Create your models here.
class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('approved', 'Approved'), ('cancelled', 'Cancelled')), default='pending')

    def __str__(self):
        return f"{self.patient.user.full_name} - {self.doctor.user.full_name} ({self.date} {self.time})"

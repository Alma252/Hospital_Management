# Generated by Django 5.2.3 on 2025-07-27 05:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0003_appointment_fee_appointment_is_paid'),
        ('users', '0004_doctor_description_doctor_medical_license_number_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Insurance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(max_length=255)),
                ('policy_number', models.CharField(max_length=100, unique=True)),
                ('coverage_percent', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('valid_until', models.DateField(blank=True, null=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='insurances', to='users.patient')),
            ],
        ),
        migrations.AddField(
            model_name='appointment',
            name='insurance_used',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='appointments.insurance'),
        ),
    ]

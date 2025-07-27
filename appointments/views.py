from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from yaml import serialize
from .models import Appointment, AvailableSlot
from .serializers import AppointmentSerializer, AvailableSlotSerializer
from django.utils import timezone
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from users.models import Doctor
from decimal import Decimal
from reportlab.lib.pagesizes import A4


class CreateAppointmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        doctor_id = request.data.get('doctor')
        date = request.data.get('date')
        time = request.data.get('time')

        try:
            patient = request.user.patient_profile
        except Patient.DoesNotExist:
            return Response({'detail': 'Only patients can create appointments'}, status=403)

        patient = request.user.patient_profile
        doctor = get_object_or_404(Doctor, id=doctor_id)

        # بررسی اینکه زمان در بازه قابل قبول باشه
        is_valid_time = AvailableSlot.objects.filter(
            doctor=doctor,
            date=date,
            start_time__lte=time,
            end_time__gt=time
        ).exists()

        if not is_valid_time:
            return Response(
                {"detail": "This time is not available for the selected doctor."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ایجاد نوبت
        Appointment.objects.create(
            doctor=doctor,
            patient=patient,
            date=date,
            time=time
        )

        return Response({"detail": "Appointment created successfully!"}, status=status.HTTP_201_CREATED)


# لیست نوبت‌ها بر اساس نقش کاربر
class ListAppointmentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == 'doctor':
            appointments = Appointment.objects.filter(doctor__user=user)

        elif user.role == 'patient':
            appointments = Appointment.objects.filter(patient__user=user)

        elif user.role == 'admin':
            appointments = Appointment.objects.all()

        else:
            return Response({'detail': 'Access Denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

# برای تغییر وضعیت نوبت‌ها (فقط دکتر یا ادمین)
class UpdateAppointmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, appointment_id):

        try:
            appointment = Appointment.objects.get(id=appointment_id)

        except Appointment.DoesNotExist:
            return Response({'detail': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if user.role not in ['doctor', 'admin']:
            return Response({'detail': 'You do not have permission to update appointments.'}, status=status.HTTP_403_FORBIDDEN)

        if user.role == 'doctor' and appointment.doctor.user != user:
            return Response({'detail': 'You can only update your own appointments.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# لغو نوبت توسط بیمار
class CancelAppointmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({'detail': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if user.role != 'patient' or appointment.patient.user != user:
            return Response({'detail': 'You can only cancel your own appointments'}, status=status.HTTP_403_FORBIDDEN)

        appointment.status = 'cancelled'
        appointment.save()
        return Response({'detail': 'Appointment cancelled successfully'})

# ویوی تغییر زمان نوبت توسط بیمار
class ChangeAppointmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, appointment_id):

        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({'detail': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role != 'patient' or appointment.patient.user != request.user:
            return Response({'detail': 'You can only modify your own appointments.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()

        doctor_id = data.get('doctor', appointment.doctor.id)
        date = data.get('date', appointment.date)
        time = data.get('time', appointment.time)

        slot_exists = AvailableSlot.objects.filter(
            doctor_id=doctor_id,
            date=date,
            start_time__lte=time,
            end_time__gt=time
        ).exists()

        if not slot_exists:
            return Response({'detail': 'The new time is not available for the selected doctor.'}, status=400)

        serializer = AppointmentSerializer(appointment, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


#  نوبت‌های آینده
class UpcomingAppointmentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()

        if user.role == 'doctor':
            appointments = Appointment.objects.filter(doctor=user.doctor_profile, date__gte=today)

        elif user.role == 'patient':
            appointments = Appointment.objects.filter(patient=user.patient_profile, date__gte=today)

        else:
            return Response({"detail": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


# زمان‌های آزاد یک پزشک
class DoctorAvailableSlotsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, doctor_id):
        slots = AvailableSlot.objects.filter(doctor_id=doctor_id).order_by('date', 'start_time')
        serializer = AvailableSlotSerializer(slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


#ویوی ثبت زمان آزاد توسط دکتر :)
class CreateAvailableSlotView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role != 'doctor':
            return Response({'detail': 'Only doctors can create available slots.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        doctor = get_object_or_404(Doctor, user=user)
        data['doctor'] = doctor.id

        serializer = AvailableSlotSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#تکمیل نوبت توسط دکتر
class CompleteAppointmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({'detail': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

            # فقط پزشک اختصاص یافته می‌تواند نوبت رو تکمیل کنه
        if request.user.role != 'doctor' or appointment.doctor.user != request.user:
            return Response({'detail': 'Only the assigned doctor can complete this appointment.'},
                            status=status.HTTP_403_FORBIDDEN)

        # علامت‌گذاری نوبت به عنوان تکمیل شده
        appointment.status = 'completed'
        appointment.updated_at = timezone.now()
        appointment.save()

        return Response({'detail': 'Appointment marked as completed successfully.'}, status=status.HTTP_200_OK)

class AppointmentInvoicePDFView(APIView):
    def get(self, request, appointment_id):
        appointment = get_object_or_404(
            Appointment.objects.select_related('doctor__user', 'patient__user', 'insurance'),
            pk=appointment_id
        )

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="invoice_{appointment.id}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        y = height - 50

        # عنوان
        p.setFont("Helvetica-Bold", 18)
        p.drawString(220, y, "Invoice")
        y -= 40

        # اطلاعات نوبت
        p.setFont("Helvetica", 12)
        p.drawString(50, y, f"Patient Name: {appointment.patient.user.full_name}")
        y -= 20
        p.drawString(50, y, f"Doctor Name: Dr. {appointment.doctor.user.full_name}")
        y -= 20
        p.drawString(50, y, f"Appointment Date: {appointment.date.strftime('%Y-%m-%d')} at {appointment.time}")
        y -= 30

        # محاسبه هزینه و تخفیف بیمه
        visit_fee = appointment.fee or 0
        insurance = appointment.insurance

        if insurance and insurance.coverage_percent:
            discount = (visit_fee * insurance.coverage_percent) / 100
            insurance_provider = insurance.provider
        else:
            discount = 0
            insurance_provider = "None"

        total_cost = visit_fee - discount

        # رسم هزینه‌ها
        p.drawString(50, y, f"Visit Fee: ${visit_fee:.2f}")
        y -= 20
        p.drawString(50, y, f"Insurance Provider: {insurance_provider}")
        y -= 20
        p.drawString(50, y, f"Insurance Discount: ${discount:.2f}")
        y -= 20
        p.drawString(50, y, f"Total Cost: ${total_cost:.2f}")

        p.showPage()
        p.save()

        return response
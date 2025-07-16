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


# رزرو نوبت فقط توسط بیماران
class CreateAppointmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.role != 'patient':
            return Response({'detail': 'Only patients can create appointments'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        doctor_id = data.get('doctor')
        date = data.get('date')
        time = data.get('time')

        # بررسی اینکه آیا این اسلات در AvailableSlot وجود دارد
        slot_exists = AvailableSlot.objects.filter(
            doctor_id=doctor_id,
            date=date,
            start_time__lte=time,
            end_time__gt=time  # time باید در بازه‌ی زمان آزاد باشه
        ).exists()

        if not slot_exists:
            return Response({'detail': 'This time is not available for the selected doctor.'}, status=status.HTTP_400_BAD_REQUEST)

        data['patient'] = request.user.patient_profile.id
        serializer = AppointmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        data['doctor'] = user.doctor_profile.id

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


# ویوی Invoice یا گزارش و فاکتور
class AppointmentInvoicePDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({'detail': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        if user.role == 'admin':
            pass  # مجاز است
        elif user.role == 'doctor' and hasattr(user, 'doctor_profile') and appointment.doctor == user.doctor_profile:
            pass
        elif user.role == 'patient' and hasattr(user, 'patient_profile') and appointment.patient == user.patient_profile:
            pass
        else:
            return Response({'detail': 'Access denied'}, status=403)

        # تولید فایل PDF در حافظه
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="invoice_{appointment.id}.pdf"'

        p = canvas.Canvas(response)
        p.setFont("Helvetica", 14)
        p.drawString(100, 800, " فاکتور نوبت پزشکی")

        p.setFont("Helvetica", 12)
        p.drawString(100, 770, f"بیمار: {appointment.patient.user.full_name}")
        p.drawString(100, 750, f"پزشک: {appointment.doctor.user.full_name}")
        p.drawString(100, 730, f"تاریخ نوبت: {appointment.date}")
        p.drawString(100, 710, f"ساعت: {appointment.time}")
        p.drawString(100, 690, f"وضعیت نوبت: {appointment.status}")

        p.drawString(100, 660, f"مبلغ پایه: {appointment.fee} تومان")
        tax = int(appointment.fee * 0.09)
        total = appointment.fee + tax
        p.drawString(100, 640, f"مالیات (۹٪): {tax} تومان")
        p.drawString(100, 620, f"جمع کل: {total} تومان")

        p.drawString(100, 590, f"وضعیت پرداخت: {'پرداخت شده' if appointment.is_paid else 'پرداخت نشده'}")

        p.showPage()
        p.save()

        return response

















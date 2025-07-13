from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from yaml import serialize

from .models import Appointment, AvailableSlot
from .serializers import AppointmentSerializer, AvailableSlotSerializer
from django.utils import timezone


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


















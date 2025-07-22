from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from yaml import serialize

from .models import User, Doctor, Patient
from .serializers import RegisterSerializer, UserSerializer, DoctorSerializer, PatientSerializer
from django.db.models import Q

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {'user': UserSerializer(user).data}

        if user.role == 'doctor' and hasattr(user, 'doctor_profile'):
            data['profile'] = DoctorSerializer(user.doctor_profile).data
        elif user.role == 'patient' and hasattr(user, 'patient_profile'):
            data['profile'] = PatientSerializer(user.patient_profile).data

        return Response(data)


class DoctorListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        doctors = Doctor.objects.select_related('user')

        if query:
            doctors = doctors.filter(
                Q(user__full_name__icontains=query) |
                Q(specialty__icontains=query) |
                Q(hospital__icontains=query)
            )

        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)

# ویوی تأیید پزشک
class ApproveDoctorView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, doctor_id):
        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response({'detail': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)

        approved = request.data.get('approved')
        reason = request.data.get('rejection_reason', '')

        if approved is True:
            doctor.approved = True
            doctor.approval_date = timezone.now()
            doctor.rejection_reason = ''
        else:
            doctor.approved = False
            doctor.approval_date = None
            doctor.rejection_reason = reason

        doctor.save()
        return Response({'detail': 'Doctor approval status updated'})

# ثبت بیمار توسط ادمین
class CreatePatientByAdminView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=201)
        return Response(serializer.errors, status=400)

# پذیرش بیمار (Check-In)
class PatientCheckInView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, patient_id):
        if request.user.role != 'admin':
            return Response({'detail': 'Only admins can check in patients.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            patient = Patient.objects.get(id=patient_id)

        except Patient.DoesNotExist:
            return Response({'detail': 'Patient not found.'}, status=status.HTTP_404_NOT_FOUND)

        if patient.is_checked_in:
            return Response({'detail': 'Patient is already checked in.'}, status=status.HTTP_400_BAD_REQUEST)

        patient.is_checked_in = True
        patient.check_in_time = timezone.now()
        patient.check_out_time = None
        patient.save()

        return Response({'detail': f'{patient.user.full_name} checked in successfully.'})

# خروج بیمار (Check-Out)
class PatientCheckOutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, patient_id):
        if request.user.role != 'admin':
            return Response({'detail': 'Only admins can check out patients.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response({'detail': 'Patient not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not patient.is_checked_in:
            return Response({'detail': 'Patient is not currently checked in.'}, status=status.HTTP_400_BAD_REQUEST)

        patient.is_checked_in = False
        patient.check_out_time = timezone.now()
        patient.save()

        return Response({'detail': f'{patient.user.full_name} checked out successfully.'})

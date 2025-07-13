from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
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

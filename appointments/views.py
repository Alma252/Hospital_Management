from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentListCreateView(APIView):
    permissions_classes = [permissions.IsAuthenticated]

    def get(self, request):

        if request.user.role == 'doctor':
            appointments = Appointment.objects.filter(doctor__user=request.user)
        elif request.user.role == 'patient':
            appointments = Appointment.objects.filter(patient__user=request.user)
        elif request.user.role == 'admin':
            appointments = Appointment.objects.all()
        else:
            return Response({'detail': 'Access Denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'patient':
            return Response({'detail': 'Only patients can create appointments'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data['patient'] = request.user.patient_profile.id

        serializer = AppointmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

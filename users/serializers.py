from rest_framework import serializers
from .models import User, Doctor, Patient

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role']

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id',
            'user',
            'specialty',
            'hospital',
            'approved',
            'approval_date',
            'rejection_reason',
        ]
        read_only_fields = ['approved', 'approval_date', 'rejection_reason']

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'user', 'age', 'gender', 'phone_number']


class RegisterSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(required=False)
    gender = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    description = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'role', 'age', 'gender', 'phone_number', 'description']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        role = validated_data.pop('role', None)
        password = validated_data.pop('password')

        if role not in ['patient', 'doctor']:
            raise serializers.ValidationError({'role': 'Role must be either "patient" or "doctor"'})

        age = validated_data.pop('age', None)
        gender = validated_data.pop('gender', None)
        phone_number = validated_data.pop('phone_number', None)
        description = validated_data.pop('description', None)

        user = User.objects.create(**validated_data, role=role)
        user.set_password(password)
        user.save()

        if role == 'patient':
            Patient.objects.create(user=user, age=age, gender=gender, phone_number=phone_number)
        elif role == 'doctor':
            Doctor.objects.create(user=user, description=description)

        return user


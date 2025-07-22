from rest_framework import serializers
from .models import User, Doctor, Patient


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role']


class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    description = serializers.CharField(required=False)
    medical_system_number = serializers.CharField(required=False)
    photo = serializers.ImageField(required=False)

    class Meta:
        model = Doctor
        fields = [
            'id',
            'user',
            'specialty',
            'hospital',
            'description',
            'medical_system_number',
            'photo',
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
    rejection_reason = serializers.CharField(required=False)
    medical_license_number = serializers.CharField(required=False)
    photo = serializers.ImageField(required=False)
    specialty = serializers.CharField(required=False)
    hospital = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'full_name', 'role',
            'age', 'gender', 'phone_number',
            'description', 'rejection_reason',
            'medical_license_number', 'photo',
            'specialty', 'hospital'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        role = validated_data.pop('role', None)
        password = validated_data.pop('password')

        if role not in ['patient', 'doctor']:
            raise serializers.ValidationError({'role': 'Role must be either "patient" or "doctor"'})

        # اطلاعات عمومی برای هر دو نقش
        age = validated_data.pop('age', None)
        gender = validated_data.pop('gender', None)
        phone_number = validated_data.pop('phone_number', None)

        # اطلاعات خاص دکتر
        doctor_data = {
            'description': validated_data.pop('description', None),
            'rejection_reason': validated_data.pop('rejection_reason', None),
            'medical_license_number': validated_data.pop('medical_license_number', None),
            'photo': validated_data.pop('photo', None),
            'specialty': validated_data.pop('specialty', None),
            'hospital': validated_data.pop('hospital', None),
        }

        # ایجاد کاربر
        user = User.objects.create(**validated_data, role=role)
        user.set_password(password)
        user.save()

        if role == 'patient':
            Patient.objects.create(user=user, age=age, gender=gender, phone_number=phone_number)
        elif role == 'doctor':
            Doctor.objects.create(user=user, **doctor_data)

        return user

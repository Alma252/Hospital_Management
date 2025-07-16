from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserProfileView, DoctorListView, ApproveDoctorView, CreatePatientByAdminView, PatientCheckInView, PatientCheckOutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('doctors/<int:doctor_id>/approve/', ApproveDoctorView.as_view(), name='approve-doctor'),
    path('admin/create-patient/', CreatePatientByAdminView.as_view(), name='admin-create-patient'),
    path('patients/<int:patient_id>/check-in/', PatientCheckInView.as_view(), name='patient-check-in'),
    path('patients/<int:patient_id>/check-out/', PatientCheckOutView.as_view(), name='patient-check-out'),
]




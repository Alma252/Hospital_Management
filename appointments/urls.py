from django.urls import path
from .views import (
    CreateAppointmentView,
    ListAppointmentsView,
    UpdateAppointmentView,
    CancelAppointmentView,
    UpcomingAppointmentsView,
    DoctorAvailableSlotsView,
    CreateAvailableSlotView,
    ChangeAppointmentView,
    CompleteAppointmentView,
    AppointmentInvoicePDFView
)

urlpatterns = [
    path('create/', CreateAppointmentView.as_view(), name='create_appointment'),
    path('list/', ListAppointmentsView.as_view(), name='list_appointments'),
    path('<int:appointment_id>/update/', UpdateAppointmentView.as_view(), name='update_appointment'),
    path('<int:appointment_id>/cancel/', CancelAppointmentView.as_view(), name='cancel_appointment'),
    path('<int:appointment_id>/change/', ChangeAppointmentView.as_view(), name='change_appointment'),
    path('<int:appointment_id>/complete/', CompleteAppointmentView.as_view(), name='complete_appointment'),

    path('upcoming/', UpcomingAppointmentsView.as_view(), name='upcoming_appointments'),
    path('doctors/<int:doctor_id>/available-slots/', DoctorAvailableSlotsView.as_view(), name='doctor_available_slots'),
    path('slots/create/', CreateAvailableSlotView.as_view(), name='create_available_slot'),
    path('<int:appointment_id>/invoice/', AppointmentInvoicePDFView.as_view(), name='appointment-invoice'),
]

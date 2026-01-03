from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Role-based login URLs
    path('login/', views.home),  # Redirect generic login to home
    path('login/<str:role>/', views.role_login_view, name='role_login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Registration
    path('register/', views.register_view, name='register'),
    
    # Role-based dashboards
    path('hospital-admin/dashboard/', views.admin_dashboard, name='hospital_admin_dashboard'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),
    path('profile/security/', views.profile_security, name='profile_security'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/profile/', views.staff_profile, name='staff_profile'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    
    # Appointments
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/complete/<int:appt_id>/', views.complete_appointment, name='complete_appointment'),
    path('book-appointment/', views.book_appointment_view, name='book_appointment_view'),
    
    # Patient Management
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/create-guest/', views.create_guest_patient, name='create_guest_patient'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    
    # Medical Records
    path('patient/<int:patient_id>/add-record/', views.add_medical_record, name='add_medical_record'),
    path('prescription/<int:record_id>/add/', views.add_prescription, name='add_prescription'),
    
    # Doctor Management
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('delete-doctor/<int:doctor_id>/', views.delete_doctor, name='delete_doctor'),
    
    # Triage
    path('triage/', views.triage_form, name='triage_form'),
    path('triage/<int:patient_id>/', views.triage_form, name='triage_form_patient'),
    
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    
    # Reports
    path('reports/', views.reports_view, name='reports'),

    # Admin User Management
    path('admin/add-doctor/', views.admin_add_doctor, name='admin_add_doctor'),
    path('admin/add-staff/', views.admin_add_staff, name='admin_add_staff'),
    path('admin/add-patient/', views.admin_add_patient, name='admin_add_patient'),

    # Email verification
]
from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Role-based login URLs
    path('login/<str:role>/', views.role_login_view, name='role_login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Registration
    path('register/', views.register_view, name='register'),
    
    # Role-based dashboards
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    
    # Appointments
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('book-appointment/', views.book_appointment_view, name='book_appointment_view'),
    
    # Patient Management
    path('patients/', views.patient_list, name='patient_list'),
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
]
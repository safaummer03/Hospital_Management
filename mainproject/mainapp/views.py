from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, date, timedelta
from .models import *
from .forms import *
from .decorators import role_required

def home(request):
    return render(request, 'home.html')

def role_login_view(request, role):
    role = role.upper()
    role_names = {'ADMIN': 'Administrator', 'DOCTOR': 'Doctor', 'STAFF': 'Staff', 'PATIENT': 'Patient'}
    
    if role not in role_names:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['emai']
        password = request.POST['password']
        
        user = authenticate(request, username=email, password=password)
        if user and user.is_active_user:
            if user.role != role:
                messages.error(request, f'Invalid credentials for {role_names[role]} role')
                return render(request, 'role_login.html', {'role': role, 'role_name': role_names[role]})
            
            login(request, user)
            return redirect(f'{role.lower()}_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'role_login.html', {'role': role, 'role_name': role_names[role]})

def login_view(request):
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        name = request.POST.get('name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'register.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            name=name,
            role=role
        )
        
        messages.success(request, f'{role.title()} registered successfully! Please login.')
        return redirect('home')
    
    departments = Department.objects.all()
    return render(request, 'register.html', {'departments': departments})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@role_required(['ADMIN'])
def admin_dashboard(request):
    total_patients = PatientProfile.objects.count()
    total_doctors = DoctorProfile.objects.count()
    total_staff = StaffProfile.objects.count()
    total_appointments = Appointment.objects.count()
    
    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_staff': total_staff,
        'total_users': User.objects.count(),
        'total_appointments': total_appointments,
        'revenue': 0,
        'doctors': User.objects.filter(role='DOCTOR'),
        'departments': Department.objects.all(),
    }
    return render(request, 'admin_dashboard.html', context)

@role_required(['DOCTOR'])
def doctor_dashboard(request):
    today = date.today()
    appointments = Appointment.objects.filter(doctor=request.user, appointment_date=today)
    
    context = {
        'appointments': appointments,
        'today_appointments': appointments,
        'notifications': Notification.objects.filter(user=request.user, is_read=False)[:5],
    }
    return render(request, 'doctor_dashboard.html', context)

@role_required(['STAFF'])
def staff_dashboard(request):
    context = {
        'triage_queue': TriageQueue.objects.filter(is_processed=False),
        'today_appointments': Appointment.objects.filter(appointment_date=date.today()),
        'notifications': Notification.objects.filter(user=request.user, is_read=False)[:5],
    }
    return render(request, 'staff_dashboard.html', context)

@role_required(['PATIENT'])
def patient_dashboard(request):
    context = {
        'appointments': Appointment.objects.filter(patient=request.user)[:5],
        'medical_history': MedicalHistory.objects.filter(patient=request.user)[:5],
        'notifications': Notification.objects.filter(user=request.user, is_read=False)[:5],
    }
    return render(request, 'patient_dashboard.html', context)

@role_required(['PATIENT'])
def book_appointment_view(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')
        
        doctor = get_object_or_404(User, id=doctor_id, role='DOCTOR')
        
        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason
        )
        
        messages.success(request, 'Appointment booked successfully!')
        return redirect('patient_dashboard')
    
    doctors = User.objects.filter(role='DOCTOR', is_active_user=True)
    return render(request, 'book_appointment.html', {'doctors': doctors})

@role_required(['ADMIN', 'DOCTOR', 'STAFF'])
def patient_list(request):
    patients = User.objects.filter(role='PATIENT')
    return render(request, 'patient_list.html', {'patients': patients})

@role_required(['ADMIN', 'DOCTOR', 'STAFF'])
def patient_detail(request, patient_id):
    patient = get_object_or_404(User, id=patient_id, role='PATIENT')
    return render(request, 'patient_detail.html', {'patient': patient})

@role_required(['ADMIN'])
def reports_view(request):
    context = {'message': 'Reports coming soon'}
    return render(request, 'reports.html', context)

@role_required(['DOCTOR'])
def add_medical_record(request, patient_id):
    return redirect('patient_detail', patient_id=patient_id)

@role_required(['DOCTOR'])
def add_prescription(request, record_id):
    return redirect('patient_list')

@role_required(['ADMIN'])
def doctor_list(request):
    doctors = User.objects.filter(role='DOCTOR')
    return render(request, 'doctor_list.html', {'doctors': doctors})

@role_required(['ADMIN'])
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(User, id=doctor_id, role='DOCTOR')
    doctor.delete()
    messages.success(request, 'Doctor deleted successfully')
    return redirect('admin_dashboard')

@role_required(['STAFF'])
def triage_form(request, patient_id=None):
    return render(request, 'triage_form.html')

@login_required
def appointment_list(request):
    appointments = Appointment.objects.all()
    return render(request, 'appointment_list.html', {'appointments': appointments})

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'notifications.html', {'notifications': notifications})
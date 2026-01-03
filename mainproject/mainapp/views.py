from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, date, timedelta
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import *
from .forms import *
from .decorators import role_required


def home(request):
    return render(request, 'home.html')


def role_login_view(request, role):
    # Normalize role and provide user-friendly names
    role = role.upper()
    role_names = {
        'ADMIN': 'Administrator',
        'DOCTOR': 'Doctor',
        'STAFF': 'Staff',
        'PATIENT': 'Patient',
    }

    if role not in role_names:
        messages.error(request, 'Invalid role specified.')
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Username and password are required')
            return render(request, 'role_login.html', {'role': role, 'role_name': role_names[role]})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, 'Your account is disabled. Please contact the administrator.')
                return render(request, 'role_login.html', {'role': role, 'role_name': role_names[role]})

            if not getattr(user, 'is_active_user', True):
                messages.error(request, 'Your account has been deactivated. Please contact the administrator.')
                return render(request, 'role_login.html', {'role': role, 'role_name': role_names[role]})

            # Admin may also be a superuser
            if role == 'ADMIN':
                if getattr(user, 'role', None) == 'ADMIN' or user.is_superuser:
                    login(request, user)
                    if user.is_superuser:
                        return redirect('/admin/')
                    return redirect('hospital_admin_dashboard')
                else:
                    messages.error(request, f'Access Denied: You are registered as a {user.role.title() if getattr(user, "role", None) else "User"}.')
                    return render(request, 'role_login.html', {'role': role, 'role_name': role_names[role]})

            # Other roles must match exactly
            if getattr(user, 'role', None) == role:
                login(request, user)
                if getattr(user, 'first_login', False) and role == 'DOCTOR':
                    messages.info(request, "Welcome! For security, please update your password first.")
                    return redirect('doctor_profile')
                return redirect(f'{role.lower()}_dashboard')

            messages.error(request, f'Incorrect Portal: You are a {user.role.title() if getattr(user, "role", None) else "User"}. Please use the correct login page.')
            return render(request, 'role_login.html', {'role': role, 'role_name': role_names[role]})

        else:
            # Authentication failed; provide a generic helpful message
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'role_login.html', {'role': role, 'role_name': role_names[role]})


def register_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        name = request.POST.get('name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Only allow PATIENT role registration
        if role != 'PATIENT':
            messages.error(request, 'Only patients can register themselves. Admins, doctors, and staff must be added by hospital administrators.')
            return render(request, 'register.html')

        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            name=name,
            role=role,
            is_active=True,  # Account is active immediately
            email_verified=True  # Mark as verified immediately
        )

        messages.success(request, 'Registration successful! You can now login with your credentials.')
        return redirect('home')

    departments = Department.objects.all()
    return render(request, 'register.html', {'departments': departments})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@role_required(['ADMIN'])
def admin_dashboard(request):
    from django.db.models import Sum
    total_patients = PatientProfile.objects.count()
    total_doctors = DoctorProfile.objects.count()
    total_staff = StaffProfile.objects.count()
    total_appointments = Appointment.objects.count()
    
    # Calculate revenue from completed appointments
    revenue = Appointment.objects.filter(status='COMPLETED').aggregate(
        total=Sum('doctor__doctorprofile__consultation_fee')
    )['total'] or 0
    
    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_staff': total_staff,
        'total_users': User.objects.count(),
        'total_appointments': total_appointments,
        'revenue': revenue,
        'doctors': User.objects.filter(role='DOCTOR'),
        'departments': Department.objects.all(),
    }
    return render(request, 'admin_dashboard.html', context)

@role_required(['DOCTOR'])
def doctor_dashboard(request):
    today = date.today()
    appointments = Appointment.objects.filter(doctor=request.user, appointment_date=today)
    doctor_profile = DoctorProfile.objects.filter(user=request.user).first()
    
    # Do not force redirect from dashboard; initial login already handles first-login flow.

    # Calculate statistics
    total_patients_count = User.objects.filter(role='PATIENT', patient_appointments__doctor=request.user).distinct().count()
    pending_requests_count = Appointment.objects.filter(doctor=request.user, status='PENDING').count()

    context = {
        'appointments': appointments,
        'today_appointments': appointments,
        'doctor_profile': doctor_profile,
        'total_patients': total_patients_count,
        'pending_requests': pending_requests_count,
        'notifications': Notification.objects.filter(user=request.user, is_read=False)[:5],
    }
    return render(request, 'doctor_dashboard.html', context)

@role_required(['DOCTOR'])
def doctor_profile(request):
    doctor_profile = DoctorProfile.objects.filter(user=request.user).first()
    password_form = ChangePasswordForm()

    if request.method == 'POST':
        if 'update_password' in request.POST:
            password_form = ChangePasswordForm(request.POST)
            if password_form.is_valid():
                old_password = password_form.cleaned_data['old_password']
                new_password1 = password_form.cleaned_data['new_password1']
                new_password2 = password_form.cleaned_data['new_password2']

                if not request.user.check_password(old_password):
                    messages.error(request, 'Old password is incorrect.')
                elif new_password1 != new_password2:
                    messages.error(request, 'New passwords do not match.')
                else:
                    request.user.set_password(new_password1)
                    request.user.first_login = False
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    messages.success(request, 'Password updated successfully!')
                    return redirect('doctor_profile')
        
        elif 'update_profile' in request.POST:
            # Update User Model
            request.user.name = request.POST.get('name')
            request.user.email = request.POST.get('email')
            request.user.phone = request.POST.get('phone')
            request.user.save()

            # Update Doctor Profile Model
            if doctor_profile:
                doctor_profile.specialty = request.POST.get('specialty')
                doctor_profile.qualification = request.POST.get('qualification')
                doctor_profile.experience_years = int(request.POST.get('experience_years', 0))
                doctor_profile.consultation_fee = float(request.POST.get('consultation_fee', 0))
                
                # Handle time fields
                avail_from = request.POST.get('available_from')
                avail_to = request.POST.get('available_to')
                if avail_from:
                    doctor_profile.available_from = avail_from
                if avail_to:
                    doctor_profile.available_to = avail_to
                    
                doctor_profile.save()

            messages.success(request, 'Profile updated successfully!')
            return redirect('doctor_profile')

    context = {
        'doctor_profile': doctor_profile,
        'password_form': password_form,
    }
    return render(request, 'doctor_profile.html', context)

@login_required
def profile_security(request):
    password_form = ChangePasswordForm()
    if request.method == 'POST':
        password_form = ChangePasswordForm(request.POST)
        if password_form.is_valid():
            old_password = password_form.cleaned_data['old_password']
            new_password1 = password_form.cleaned_data['new_password1']
            new_password2 = password_form.cleaned_data['new_password2']

            if not request.user.check_password(old_password):
                messages.error(request, 'Old password is incorrect.')
            elif new_password1 != new_password2:
                messages.error(request, 'New passwords do not match.')
            else:
                request.user.set_password(new_password1)
                request.user.first_login = False
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, f'Welcome {request.user.name}! Your password has been updated.')
                
                # Role based dashboard redirection
                dashboard_map = {
                    'ADMIN': 'hospital_admin_dashboard',
                    'DOCTOR': 'doctor_dashboard',
                    'STAFF': 'staff_dashboard',
                    'PATIENT': 'patient_dashboard'
                }
                return redirect(dashboard_map.get(request.user.role, 'home'))
    
    if request.user.role == 'DOCTOR':
        base_template = 'base_doctor.html'
    elif request.user.role == 'STAFF':
        base_template = 'base_staff.html'
    elif request.user.role == 'PATIENT':
        base_template = 'base_patient.html'
    else:
        base_template = 'base.html'

    return render(request, 'profile_security.html', {
        'password_form': password_form,
        'base_template': base_template
    })

@role_required(['STAFF'])
def staff_dashboard(request):
    today = date.today()
    staff_profile = StaffProfile.objects.filter(user=request.user).first()
    today_appointments = Appointment.objects.filter(appointment_date=today).order_by('appointment_time')
    
    context = {
        'today_appointments': today_appointments,
        'appointments_today_count': today_appointments.count(),
        'patients_waiting_count': TriageQueue.objects.filter(is_processed=False).count(),
        'doctors_on_duty_count': DoctorProfile.objects.filter(is_available=True).count(),
        'pending_requests_count': Appointment.objects.filter(status='PENDING').count(),
        'current_date': today.strftime("%Y-%m-%d"),
        'staff_profile': staff_profile,
        'notifications': Notification.objects.filter(user=request.user, is_read=False)[:5],
    }
    return render(request, 'staff_dashboard.html', context)

@role_required(['STAFF'])
def staff_profile(request):
    staff_profile = StaffProfile.objects.filter(user=request.user).first()
    password_form = ChangePasswordForm()

    if request.method == 'POST':
        if 'update_password' in request.POST:
            password_form = ChangePasswordForm(request.POST)
            if password_form.is_valid():
                old_password = password_form.cleaned_data['old_password']
                new_password1 = password_form.cleaned_data['new_password1']
                new_password2 = password_form.cleaned_data['new_password2']

                if not request.user.check_password(old_password):
                    messages.error(request, 'Old password is incorrect.')
                elif new_password1 != new_password2:
                    messages.error(request, 'New passwords do not match.')
                else:
                    request.user.set_password(new_password1)
                    request.user.first_login = False
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    messages.success(request, 'Password updated successfully!')
                    return redirect('staff_profile')
        
        elif 'update_profile' in request.POST:
            request.user.name = request.POST.get('name')
            request.user.email = request.POST.get('email')
            request.user.phone = request.POST.get('phone')
            request.user.save()

            if staff_profile:
                department_id = request.POST.get('department')
                if department_id:
                    department = Department.objects.get(id=department_id)
                    staff_profile.department = department
                staff_profile.position = request.POST.get('position', '')
                staff_profile.save()

            messages.success(request, 'Profile updated successfully!')
            return redirect('staff_profile')

    context = {
        'staff_profile': staff_profile,
        'password_form': password_form,
        'departments': Department.objects.all(),
    }
    return render(request, 'staff_profile.html', context)

@role_required(['PATIENT'])
def patient_dashboard(request):
    from datetime import date
    patient_profile = PatientProfile.objects.filter(user=request.user).first()
    appointments = Appointment.objects.filter(patient=request.user).order_by('-appointment_date')
    medical_history = MedicalHistory.objects.filter(patient=request.user).order_by('-date')
    
    # Calculate health status metrics
    last_visit = medical_history.first()
    next_appointment = appointments.filter(
        appointment_date__gte=date.today()
    ).order_by('appointment_date').first()
    active_prescriptions_count = medical_history.filter(
        prescription__isnull=False
    ).count()
    
    context = {
        'appointments': appointments[:5],
        'medical_history': medical_history[:5],
        'patient_profile': patient_profile,
        'last_visit_date': last_visit.date if last_visit else None,
        'next_appointment': next_appointment,
        'active_prescriptions_count': active_prescriptions_count,
        'notifications': Notification.objects.filter(user=request.user, is_read=False)[:5],
    }
    return render(request, 'patient_dashboard.html', context)

@login_required
def dashboard(request):
    # Redirect user to their role-specific dashboard
    role = getattr(request.user, 'role', '').upper()
    if role == 'ADMIN':
        return redirect('hospital_admin_dashboard')
    if role == 'DOCTOR':
        return redirect('doctor_dashboard')
    if role == 'STAFF':
        return redirect('staff_dashboard')
    if role == 'PATIENT':
        return redirect('patient_dashboard')
    return redirect('home')
@role_required(['PATIENT', 'STAFF'])
def book_appointment_view(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        patient_id = request.POST.get('patient') # Staff can select patient
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')
        
        doctor = get_object_or_404(User, id=doctor_id, role='DOCTOR')
        
        if request.user.role == 'STAFF':
            patient = get_object_or_404(User, id=patient_id, role='PATIENT')
        else:
            patient = request.user

        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason
        )
        
        messages.success(request, 'Appointment booked successfully!')
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'appointment_id': appointment.id, 'status': appointment.status})

        if request.user.role == 'STAFF':
            return redirect('staff_dashboard')
        return redirect('patient_dashboard')
    
    doctors = User.objects.filter(role='DOCTOR', is_active_user=True)
    patients = User.objects.filter(role='PATIENT') if request.user.role == 'STAFF' else None
    
    if request.user.role == 'STAFF':
        base_template = 'base_staff.html'
    elif request.user.role == 'PATIENT':
        base_template = 'base_patient.html'
    else:
        base_template = 'base.html'

    return render(request, 'book_appointment.html', {
        'doctors': doctors, 
        'patients': patients,
        'base_template': base_template
    })

@role_required(['ADMIN', 'DOCTOR', 'STAFF'])
def patient_list(request):
    if request.user.role == 'DOCTOR':
        patients = User.objects.filter(role='PATIENT', patient_appointments__doctor=request.user).distinct()
    else:
        patients = User.objects.filter(role='PATIENT')
    selected_patient_id = request.GET.get('p')
    selected_patient = None
    medical_history = []
    
    if selected_patient_id:
        selected_patient = get_object_or_404(User, id=selected_patient_id, role='PATIENT')
    elif patients.exists():
        selected_patient = patients.first()

    if selected_patient:
        medical_history = MedicalHistory.objects.filter(patient=selected_patient).order_by('-date')

    if request.user.role == 'DOCTOR':
        base_template = 'base_doctor.html'
    elif request.user.role == 'STAFF':
        base_template = 'base_staff.html'
    else:
        base_template = 'base.html'

    return render(request, 'patient_list.html', {
        'patients': patients, 
        'selected_patient': selected_patient,
        'medical_history': medical_history,
        'base_template': base_template
    })

@role_required(['ADMIN', 'DOCTOR', 'STAFF'])
def patient_detail(request, patient_id):
    return redirect(f"/patients/?p={patient_id}")

@role_required(['ADMIN', 'DOCTOR'])
def reports_view(request):
    if request.user.role == 'DOCTOR':
        # Get count for each weekday (1=Sunday, 2=Monday, ..., 6=Friday, 7=Saturday)
        # We focus on work days: Mon-Fri (2-6)
        density_data = []
        weekdays = [
            (2, 'Mon'), (3, 'Tue'), (4, 'Wed'), (5, 'Thu'), (6, 'Fri')
        ]
        
        max_count = 0
        counts = []
        for day_num, day_name in weekdays:
            count = Appointment.objects.filter(doctor=request.user, appointment_date__week_day=day_num).count()
            counts.append({'day': day_name, 'count': count})
            if count > max_count:
                max_count = count
        
        # Scale to percentage for bar height
        for item in counts:
            height = (item['count'] / max_count * 100) if max_count > 0 else 0
            density_data.append({'label': item['day'], 'height': height, 'count': item['count']})

        # Basic patient stats
        total_patients_count = User.objects.filter(patient_appointments__doctor=request.user).distinct().count()
    else:
        density_data = []
        total_patients_count = 0

    if request.user.role == 'DOCTOR':
        base_template = 'base_doctor.html'
    elif request.user.role == 'STAFF':
        base_template = 'base_staff.html'
    else:
        base_template = 'base.html'

    context = {
        'density_data': density_data,
        'total_patients': total_patients_count,
        'base_template': base_template
    }
    return render(request, 'reports.html', context)

@role_required(['DOCTOR'])
def add_medical_record(request, patient_id):
    if request.method == 'POST':
        patient = get_object_or_404(User, id=patient_id, role='PATIENT')
        diagnosis = request.POST.get('diagnosis')
        treatment = request.POST.get('treatment')
        notes = request.POST.get('notes')
        
        MedicalHistory.objects.create(
            patient=patient,
            doctor=request.user,
            diagnosis=diagnosis,
            treatment=treatment,
            symptoms=notes
        )
        messages.success(request, f"Medical record for {patient.name} has been saved successfully.")
        return redirect(f"/patients/?p={patient_id}")
    return redirect('patient_list')

@role_required(['DOCTOR'])
def complete_appointment(request, appt_id):
    appt = get_object_or_404(Appointment, id=appt_id)
    # Only the doctor assigned to the appointment may mark it completed
    if appt.doctor != request.user:
        messages.error(request, "You can only complete your own appointments.")
        return redirect('appointment_list')

    appt.status = 'COMPLETED'
    appt.save()
    messages.success(request, f"Appointment for {appt.patient.name} marked as completed.")
    return redirect('appointment_list')

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
    return redirect('hospital_admin_dashboard')

@role_required(['STAFF'])
def triage_form(request, patient_id=None):
    patient = None
    appointment = None
    if patient_id:
        patient = get_object_or_404(User, id=patient_id, role='PATIENT')
        appointment = Appointment.objects.filter(patient=patient, appointment_date=date.today()).first()

    if request.method == 'POST':
        # Defensive checks: ensure a patient was provided
        if not patient:
            messages.error(request, 'Patient not specified for triage.')
            return redirect('staff_dashboard')

        # Associate triage with today's appointment for this patient if present
        # Create triage record and ensure numeric fields converted where appropriate
        temp = request.POST.get('temperature')
        pulse = request.POST.get('pulse_rate')
        weight = request.POST.get('weight')

        try:
            temp_val = float(temp) if temp else None
        except Exception:
            temp_val = None

        try:
            pulse_val = int(pulse) if pulse else None
        except Exception:
            pulse_val = None

        try:
            weight_val = float(weight) if weight else None
        except Exception:
            weight_val = None

        TriageQueue.objects.create(
            patient=patient,
            appointment=appointment,
            blood_pressure=request.POST.get('bp', ''),
            temperature=temp_val,
            pulse_rate=pulse_val,
            weight=weight_val,
            priority_level=request.POST.get('priority', 'MEDIUM'),
            chief_complaint=request.POST.get('chief_complaint', ''),
            is_processed=False
        )
        messages.success(request, f"Vitals recorded for {patient.name}!")
        return redirect('staff_dashboard')

    context = {
        'patient': patient,
        'appointment': appointment,
        'base_template': 'base_staff.html'
    }
    return render(request, 'triage_form.html', context)

@login_required
def appointment_list(request):
    # Retrieve filters
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    
    if request.user.role == 'DOCTOR':
        appointments = Appointment.objects.filter(doctor=request.user)
    elif request.user.role == 'PATIENT':
        appointments = Appointment.objects.filter(patient=request.user)
    else:
        appointments = Appointment.objects.all()

    # Apply search filter
    if query:
        appointments = appointments.filter(patient__name__icontains=query)
    
    # Apply status filter
    if status_filter:
        appointments = appointments.filter(status=status_filter)
        
    appointments = appointments.order_by('-appointment_date', '-appointment_time')
        
    # Provide doctors and patients lists for staff modal booking
    doctors = User.objects.filter(role='DOCTOR', is_active_user=True)
    patients = User.objects.filter(role='PATIENT') if request.user.role == 'STAFF' else None

    if request.user.role == 'DOCTOR':
        base_template = 'base_doctor.html'
    elif request.user.role == 'STAFF':
        base_template = 'base_staff.html'
    elif request.user.role == 'PATIENT':
        base_template = 'base_patient.html'
    else:
        base_template = 'base.html'

    return render(request, 'appointment_list.html', {
        'appointments': appointments, 
        'base_template': base_template,
        'query': query,
        'status_filter': status_filter,
        'doctors': doctors,
        'patients': patients,
    })

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'notifications.html', {'notifications': notifications})

@role_required(['ADMIN'])
def admin_add_doctor(request):
    if request.method == 'POST':
        form = AdminAddDoctorForm(request.POST)
        if form.is_valid():
            # Check if email already exists
            if User.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, 'Email already exists. Please use a different email.')
                return render(request, 'admin_add_doctor.html', {'form': form})

            # Auto-generate unique username
            base_username = form.cleaned_data['name'].lower().replace(' ', '_')
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            # Generate temporary password
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits
            temp_password = ''.join(secrets.choice(alphabet) for i in range(12))

            # Create user account with auto-generated credentials
            user = User.objects.create_user(
                username=username,
                email=form.cleaned_data['email'],
                password=temp_password,
                name=form.cleaned_data['name'],
                role='DOCTOR',
                email_verified=True,  # Admin-added users are verified by default
                is_active=True,
                is_staff=True,  # Staff-level access
                is_superuser=False,  # Not superuser
                first_login=True  # Require password change on first login
            )

            # Create doctor profile
            doctor_profile = form.save(commit=False)
            doctor_profile.user = user
            doctor_profile.save()

            messages.success(request, f'Doctor added successfully! Username: {username}, Temporary Password: {temp_password}. Please share these credentials securely with the doctor.')
            return redirect('hospital_admin_dashboard')
    else:
        form = AdminAddDoctorForm()

    return render(request, 'admin_add_doctor.html', {'form': form})

@role_required(['ADMIN'])
def admin_add_staff(request):
    if request.method == 'POST':
        form = AdminAddStaffForm(request.POST)
        if form.is_valid():
            # Check if email already exists
            if User.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, 'Email already exists. Please use a different email.')
                return render(request, 'admin_add_staff.html', {'form': form})

            # Auto-generate unique username
            base_username = form.cleaned_data['name'].lower().replace(' ', '_')
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            # Generate temporary password
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits
            temp_password = ''.join(secrets.choice(alphabet) for i in range(12))

            # Create user account with auto-generated credentials
            user = User.objects.create_user(
                username=username,
                email=form.cleaned_data['email'],
                password=temp_password,
                name=form.cleaned_data['name'],
                role='STAFF',
                email_verified=True,  # Admin-added users are verified by default
                is_active=True,
                is_staff=True,  # Staff-level access
                is_superuser=False,  # Not superuser
                first_login=True  # Require password change on first login
            )

            # Create staff profile
            staff_profile = form.save(commit=False)
            staff_profile.user = user
            staff_profile.save()

            messages.success(request, f'Staff member added successfully! Username: {username}, Temporary Password: {temp_password}. Please share these credentials securely with the staff member.')
            return redirect('hospital_admin_dashboard')
    else:
        form = AdminAddStaffForm()

    return render(request, 'admin_add_staff.html', {'form': form})

@role_required(['ADMIN'])
def admin_add_patient(request):
    if request.method == 'POST':
        form = AdminAddPatientForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            name = form.cleaned_data['name']
            
            # Check if user already exists by email
            user = User.objects.filter(email=email).first()
            
            if user:
                # Update existing user
                user.set_password(password)
                user.is_active = True
                user.email_verified = True
                user.is_active_user = True
                user.name = name
                
                # Handle username update if different
                old_username = user.username
                if username != old_username:
                    if User.objects.filter(username=username).exists():
                        messages.warning(request, f'Patient updated, BUT username "{username}" is taken. Kept old username: "{old_username}". Password has been reset.')
                    else:
                        user.username = username
                        messages.success(request, f'Patient updated! Username changed from "{old_username}" to "{username}". Password reset.')
                else:
                    messages.success(request, f'Patient updated! Username: {user.username}. Password reset.')
                
                user.save()
            else:
                # Check if username is taken (by someone else)
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Username already taken. Please choose another.')
                    return render(request, 'admin_add_patient.html', {'form': form})

                # Create new user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    name=name,
                    role='PATIENT',
                    is_active=True,
                    email_verified=True,
                    is_active_user=True
                )
                messages.success(request, f'Patient added successfully! Username: {username}')

            # Create or update patient profile
            # We use update_or_create to handle both cases safely
            PatientProfile.objects.update_or_create(
                user=user,
                defaults={
                    'age': form.cleaned_data['age'],
                    'gender': form.cleaned_data['gender'],
                    'contact_number': form.cleaned_data['contact_number'],
                    'blood_group': form.cleaned_data['blood_group'],
                    'emergency_contact': form.cleaned_data['emergency_contact'],
                    'address': form.cleaned_data['address'],
                    'allergies': form.cleaned_data['allergies'],
                    'medical_history': form.cleaned_data['medical_history'],
                    'current_medications': form.cleaned_data['current_medications'],
                    'insurance_number': form.cleaned_data['insurance_number']
                }
            )

            return redirect('hospital_admin_dashboard')
    else:
        form = AdminAddPatientForm()

    return render(request, 'admin_add_patient.html', {'form': form})


@role_required(['STAFF', 'ADMIN'])
def create_guest_patient(request):
    """Create a patient record without login credentials (for in-person registration).

    Expects POST with: name, age, gender, contact_number
    Returns JSON {success: True, patient_user_id, name}
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=400)

    name = request.POST.get('name', '').strip()
    age = request.POST.get('age', '').strip()
    gender = request.POST.get('gender', '').strip()
    contact = request.POST.get('contact_number', '').strip()

    if not name or not age or not gender:
        return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)

    try:
        age_val = int(age)
        if age_val < 0:
            raise ValueError()
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid age'}, status=400)

    # Generate a unique placeholder username and create a user with unusable password
    import uuid
    base = f"guest_{uuid.uuid4().hex[:8]}"
    username = base
    # Ensure uniqueness (very unlikely collision)
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base}_{counter}"
        counter += 1

    # Provide a unique placeholder email to satisfy the User.email unique constraint
    placeholder_email = f"{username}@guests.local"
    user = User.objects.create(
        username=username,
        name=name,
        role='PATIENT',
        email=placeholder_email,
        is_active=True,        # allow linking in workflows (no usable password)
        is_active_user=True,
        email_verified=False,
    )
    user.set_unusable_password()
    user.save()

    PatientProfile.objects.create(
        user=user,
        age=age_val,
        gender=gender,
        contact_number=contact,
    )

    return JsonResponse({'success': True, 'patient_user_id': user.id, 'name': user.name})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password1 = form.cleaned_data['new_password1']
            new_password2 = form.cleaned_data['new_password2']

            if not request.user.check_password(old_password):
                messages.error(request, 'Old password is incorrect.')
            elif new_password1 != new_password2:
                messages.error(request, 'New passwords do not match.')
            else:
                request.user.set_password(new_password1)
                request.user.first_login = False  # Mark as not first login
                request.user.save()
                messages.success(request, 'Password changed successfully! Please login again.')
                return redirect('login')
    else:
        form = ChangePasswordForm()

    return render(request, 'change_password.html', {'form': form})

@login_required
def change_username(request):
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST)
        if form.is_valid():
            new_username = form.cleaned_data['new_username']
            password = form.cleaned_data['password']

            if not request.user.check_password(password):
                messages.error(request, 'Password is incorrect.')
            elif User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
                messages.error(request, 'Username already exists.')
            else:
                request.user.username = new_username
                request.user.save()
                messages.success(request, 'Username changed successfully!')
                # Special handling for ADMIN role
                if request.user.role == 'ADMIN':
                    return redirect('hospital_admin_dashboard')
                else:
                    return redirect(f'{request.user.role.lower()}_dashboard')
    else:
        form = ChangeUsernameForm()

    return render(request, 'change_username.html', {'form': form})


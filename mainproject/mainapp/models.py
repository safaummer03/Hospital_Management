from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime, time, date
import uuid

class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('DOCTOR', 'Doctor'),
        ('STAFF', 'Staff'),
        ('PATIENT', 'Patient'),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PATIENT')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    is_active_user = models.BooleanField(default=True)
    
    def get_full_name(self):
        return self.name or self.username

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    head_doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'DOCTOR'})
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class PatientProfile(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    BLOOD_GROUP_CHOICES = [('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'PATIENT'})
    patient_id = models.CharField(max_length=20, unique=True, blank=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    contact_number = models.CharField(max_length=15)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    insurance_number = models.CharField(max_length=50, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.patient_id:
            self.patient_id = f"PAT{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.name} - {self.patient_id}"

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'DOCTOR'})
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200)
    experience_years = models.IntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_from = models.TimeField(default=time(9, 0))
    available_to = models.TimeField(default=time(17, 0))
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Dr. {self.user.name} - {self.specialty}"

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'STAFF'})
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.name} - Staff ({self.department.name})"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'PATIENT'}, related_name='patient_appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'DOCTOR'}, related_name='doctor_appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    reason = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.patient.name} - {self.doctor.name} on {self.appointment_date}"

class MedicalHistory(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'PATIENT'}, related_name='patient_medical_history')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'DOCTOR'}, related_name='doctor_medical_history')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    diagnosis = models.TextField()
    treatment = models.TextField()
    symptoms = models.TextField(blank=True)
    vital_signs = models.JSONField(default=dict, blank=True)
    lab_results = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.patient.name} - {self.date.date()}"

class Prescription(models.Model):
    medical_history = models.ForeignKey(MedicalHistory, on_delete=models.CASCADE)
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.medication_name} for {self.medical_history.patient.name}"

class TriageQueue(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'PATIENT'})
    blood_pressure = models.CharField(max_length=20, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    pulse_rate = models.IntegerField(null=True, blank=True)
    chief_complaint = models.TextField(blank=True)
    priority_level = models.CharField(max_length=10, choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('URGENT', 'Urgent')], default='MEDIUM')
    checked_in_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.patient.name} - Triage ({self.priority_level})"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('APPOINTMENT', 'Appointment'),
        ('PRESCRIPTION', 'Prescription'),
        ('TEST_RESULT', 'Test Result'),
        ('FOLLOW_UP', 'Follow Up'),
        ('GENERAL', 'General'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='GENERAL')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.name}"
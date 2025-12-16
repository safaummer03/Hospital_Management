from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'name', 'email', 'role', 'is_active_user', 'is_staff')
    list_filter = ('role', 'is_active_user', 'is_staff', 'is_superuser')
    search_fields = ('username', 'name', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Info', {'fields': ('name', 'role', 'phone', 'avatar', 'is_active_user')}),
    )

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'head_doctor', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'patient_id', 'age', 'gender', 'blood_group', 'registered_at')
    search_fields = ('user__name', 'patient_id', 'contact_number')
    list_filter = ('gender', 'blood_group', 'registered_at')
    readonly_fields = ('patient_id', 'registered_at')

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'specialty', 'experience_years', 'is_available')
    search_fields = ('user__name', 'specialty', 'qualification')
    list_filter = ('department', 'is_available', 'experience_years')

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'position')
    search_fields = ('user__name', 'position')
    list_filter = ('department',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'appointment_time', 'status', 'created_at')
    list_filter = ('status', 'appointment_date', 'created_at')
    search_fields = ('patient__name', 'doctor__name')
    date_hierarchy = 'appointment_date'

@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'diagnosis')
    list_filter = ('date', 'doctor__doctorprofile__department')
    search_fields = ('patient__name', 'doctor__name', 'diagnosis')
    date_hierarchy = 'date'

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('medical_history', 'medication_name', 'dosage', 'frequency', 'created_at')
    search_fields = ('medication_name', 'medical_history__patient__name')
    list_filter = ('created_at',)

@admin.register(TriageQueue)
class TriageQueueAdmin(admin.ModelAdmin):
    list_display = ('patient', 'priority_level', 'checked_in_at', 'is_processed')
    list_filter = ('priority_level', 'is_processed', 'checked_in_at')
    search_fields = ('patient__name', 'chief_complaint')
    date_hierarchy = 'checked_in_at'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__name', 'title', 'message')

admin.site.register(User, CustomUserAdmin)
admin.site.site_header = "Hospital Management System Admin"
admin.site.site_title = "HMS Admin"
admin.site.index_title = "Welcome to HMS Administration"
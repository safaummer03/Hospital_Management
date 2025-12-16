from django import forms
from django.contrib.auth.forms import UserCreationForm
from datetime import date, time
from .models import *

class CustomUserCreationForm(UserCreationForm):
    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'name', 'email', 'phone', 'role', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ('age', 'gender', 'contact_number', 'blood_group', 'emergency_contact', 'address', 'allergies', 'medical_history', 'current_medications', 'insurance_number')
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 120}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'current_medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'insurance_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ('department', 'specialty', 'qualification', 'experience_years', 'consultation_fee', 'available_from', 'available_to')
        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
            'specialty': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'available_from': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'available_to': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('doctor', 'appointment_date', 'appointment_time', 'reason')
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': date.today()}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = User.objects.filter(role='DOCTOR', is_active_user=True)
        self.fields['doctor'].empty_label = "Select a Doctor"

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data['appointment_date']
        if appointment_date < date.today():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        return appointment_date

class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = MedicalHistory
        fields = ('diagnosis', 'treatment', 'symptoms', 'lab_results', 'follow_up_date')
        widgets = {
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'treatment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'lab_results': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ('medication_name', 'dosage', 'frequency', 'duration', 'instructions')
        widgets = {
            'medication_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 500mg'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Twice daily'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 7 days'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class TriageForm(forms.ModelForm):
    class Meta:
        model = TriageQueue
        fields = ('blood_pressure', 'temperature', 'weight', 'height', 'pulse_rate', 'chief_complaint', 'priority_level')
        widgets = {
            'blood_pressure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 120/80'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Temperature in °F', 'step': '0.1'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Weight in kg', 'step': '0.1'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Height in cm', 'step': '0.1'}),
            'pulse_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Beats per minute'}),
            'chief_complaint': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Primary reason for visit'}),
            'priority_level': forms.Select(attrs={'class': 'form-control'}),
        }

class SearchForm(forms.Form):
    search = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search patients...'
        })
    )
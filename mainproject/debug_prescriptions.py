import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainproject.settings')
django.setup()

from mainapp.models import MedicalHistory, Prescription, User

# Find the patient by name "ADHIL CK" or similar from screenshot, or just verify the medical history mentioned
records = MedicalHistory.objects.filter(diagnosis__icontains="Acute Viral Fever")
print(f"Found {records.count()} records matching 'Acute Viral Fever'")

for record in records:
    print(f"Record ID: {record.id}, Diagnosis: {record.diagnosis}, Date: {record.date}")
    print(f"  Treatment (Text): {record.treatment}")
    prescriptions = record.prescription_set.all()
    print(f"  Prescription count: {prescriptions.count()}")
    for p in prescriptions:
        print(f"    - {p.medication_name}")

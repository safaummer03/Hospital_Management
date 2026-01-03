import os
import sys

# Add project to path
sys.path.insert(0, r'C:\Users\HP\OneDrive\Desktop\HMS\Hospital_Management\mainproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainproject.settings')

import django
django.setup()

from django.template.loader import get_template

try:
    # Test appointment_list.html
    t1 = get_template('appointment_list.html')
    print("SUCCESS: appointment_list.html syntax is valid")
    
    # Test staff_profile.html
    t2 = get_template('staff_profile.html')
    print("SUCCESS: staff_profile.html syntax is valid")
    
    print("\nAll template syntax errors have been fixed!")
    print("The appointments page should now load without crashing.")
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

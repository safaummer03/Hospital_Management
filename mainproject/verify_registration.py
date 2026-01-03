import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainproject.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from mainapp.views import register_view
from mainapp.models import User

def verify_registration_msg():
    print("--- Registration Message Verification ---")
    
    # Setup
    username = "new_reg_user"
    email = "new_reg@example.com"
    if User.objects.filter(username=username).exists():
        User.objects.get(username=username).delete()
        
    factory = RequestFactory()
    data = {
        'role': 'PATIENT',
        'username': username,
        'name': 'New User',
        'email': email,
        'password1': 'password123',
        'password2': 'password123'
    }
    
    request = factory.post('/register/', data)
    
    # Add session and messages support
    from django.contrib.sessions.middleware import SessionMiddleware
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    
    response = register_view(request)
    
    print(f"Response Status: {response.status_code}")
    if response.status_code == 302 and getattr(response, 'url', '') == '/': # Home URL reversed is usually '/'
         print("Redirects to Home: YES")
    else:
         print(f"Redirects to Home: NO (Url={getattr(response, 'url', '')})")

    # Check messages
    msgs = [str(m) for m in messages]
    print(f"Messages generated: {msgs}")
    
    if any("Registration successful" in m for m in msgs):
        print("PASS: Success message found.")
    else:
        print("FAIL: No success message found.")

if __name__ == "__main__":
    verify_registration_msg()

import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from api.models import User

# Let's find specific users
emails = ['adminburhan@gmail.com', 'sradmin@tmrtools.com']
try:
    for email in emails:
        user = User.objects.filter(email=email).first()
        if user:
            print(f"Found: {user.email}, Role: {user.role}, Active: {user.is_active}, Verified: {user.is_verified}, SU: {user.is_superuser}, Staff: {user.is_staff}, Has Pass: {user.has_usable_password()}")
            
            # test login
            print(f"Password Check 'password123': {user.check_password('password123')}")
            print(f"Password Check 'admin123': {user.check_password('admin123')}")
            
        else:
            print(f"Not found: {email}")
except Exception as e:
    print(f"Error: {e}")

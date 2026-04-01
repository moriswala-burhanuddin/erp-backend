import os
import django
import sys
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

# Set environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storeflow_backend.settings")
django.setup()

User = get_user_model()

email = 'burhanuddinmoris52@gmail.com'
password = 'tmr@5253'
username = 'burhan_admin'

def restore_admin():
    print(f"Checking user: {email}")
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': username,
            'is_superuser': True,
            'is_staff': True,
            'is_active': True,
            'role': 'super_admin'
        }
    )

    if created:
        user.set_password(password)
        user.save()
        print(f"✅ Created new superuser: {email}")
    else:
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.role = 'super_admin'
        user.set_password(password)
        user.save()
        print(f"✅ Restored existing user: {email} and updated permissions.")

if __name__ == "__main__":
    restore_admin()

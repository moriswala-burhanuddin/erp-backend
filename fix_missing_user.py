import os
import django
import sys
from django.contrib.auth.hashers import make_password

sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from api.models import User

email = 'aiwork449@gmail.com'
password = 'Password123!' # Temporary

user, created = User.objects.get_or_create(
    email=email,
    defaults={
        'username': email.split('@')[0],
        'is_verified': True,
        'is_active': True,
        'role': 'user',
        'password': make_password(password)
    }
)

if created:
    print(f"User {email} re-created successfully.")
else:
    print(f"User {email} already existed.")

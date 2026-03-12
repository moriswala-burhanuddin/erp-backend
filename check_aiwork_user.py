import os
import django
import sys

sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from api.models import User

email = 'aiwork449@gmail.com'
user = User.objects.filter(email=email).first()

if user:
    print(f"USER FOUND: {user.email}")
    print(f"ID: {user.id}")
    print(f"ACTIVE: {user.is_active}")
    print(f"VERIFIED: {user.is_verified}")
    print(f"ROLE: {user.role}")
    print(f"PASSWORD HASH: {user.password[:20]}...")
else:
    print(f"USER {email} NOT FOUND")

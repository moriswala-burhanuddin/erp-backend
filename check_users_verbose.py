import os
import django
import sys
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from api.models import User

# Try to find by email
email = 'aiwork449@gmail.com'
user_by_email = User.objects.filter(email=email).first()

if user_by_email:
    print(f"FOUND BY EMAIL: {user_by_email.email}, ID: {user_by_email.id}, ACTIVE: {user_by_email.is_active}")
else:
    print(f"NOT FOUND BY EMAIL: {email}")

# Let's list ALL users again, but more verbose
print("\n--- ALL USERS IN DB ---")
for u in User.objects.all():
    print(f"ID: {u.id} | EMAIL: {u.email} | ACTIVE: {u.is_active} | VERIFIED: {getattr(u, 'is_verified', 'N/A')}")

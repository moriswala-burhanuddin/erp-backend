import os
import django
import sys

# Set up Django environment
sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from api.models import User

print("--- USER DIAGNOSTIC ---")
users = User.objects.all().order_by('-id')
print(f"Total Users: {users.count()}")

for user in users[:10]:
    print(f"ID: {user.id} | Email: {user.email} | Active: {user.is_active} | Role: {user.role} | Joined: {user.date_joined}")

print("--- END DIAGNOSTIC ---")

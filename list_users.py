import os
import django
import sys

# Set up Django environment
sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from api.models import User
from django.utils import timezone

print("--- FULL USER LIST ---")
for u in User.objects.all().order_by('-date_joined'):
    print(f"EMAIL: {u.email} | ROLE: {u.role} | ACTIVE: {u.is_active} | JOINED: {u.date_joined}")

print("--- END ---")

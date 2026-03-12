import os
import django
import sys

sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from api.models import User

print("--- PASSWORD HASH DIAGNOSTIC ---")
for u in User.objects.all():
    prefix = u.password[:15] if u.password else "EMPTY"
    print(f"User: {u.email} | Hash Prefix: {prefix}...")

print("--- END ---")

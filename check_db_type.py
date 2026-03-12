import os
import django
import sys

# Set up Django environment
sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from django.db import connection
print(f"DATABASE ENGINE: {connection.settings_dict['ENGINE']}")
print(f"DATABASE NAME: {connection.settings_dict['NAME']}")

from api.models import User
print(f"User Count: {User.objects.count()}")
for u in User.objects.all()[:5]:
    print(f"User: {u.email} | Active: {u.is_active}")

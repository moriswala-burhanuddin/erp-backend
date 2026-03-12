import os
import django
import sys

sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from api.models import User

users = User.objects.all()
print(f"TOTAL USERS: {users.count()}")
for u in users:
    print(f"EMAIL: {u.email} | ID: {u.id} | ACTIVE: {u.is_active} | VERIFIED: {getattr(u, 'is_verified', 'N/A')}")

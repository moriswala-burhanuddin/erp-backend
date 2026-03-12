import os
import django
import sys

sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from api.models import User

# List all users sorted by date_joined descending
users = User.objects.all().order_by('-date_joined')
print(f"TOTAL USERS: {users.count()}")
for u in users:
    print(f"JOINED: {u.date_joined} | EMAIL: {u.email} | ID: {u.id} | ACTIVE: {u.is_active}")

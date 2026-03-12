import os
import django
import sys

sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from api.models import User

users = User.objects.all()
with open('d:/NEW-ERP/storeflow-erp/backend/full_user_list.txt', 'w') as f:
    f.write(f"TOTAL USERS: {users.count()}\n")
    for u in users:
        f.write(f"EMAIL: {u.email} | ID: {u.id} | ACTIVE: {u.is_active} | VERIFIED: {getattr(u, 'is_verified', 'N/A')} | JOINED: {u.date_joined}\n")
print("Done writing full_user_list.txt")

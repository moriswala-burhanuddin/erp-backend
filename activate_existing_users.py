import os
import django
import sys

sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from api.models import User

# Mark all current users as verified and active so they can login immediately
users = User.objects.all()
count = 0
for user in users:
    needs_save = False
    if not user.is_verified:
        user.is_verified = True
        needs_save = True
    if not user.is_active:
        user.is_active = True
        needs_save = True
    
    if needs_save:
        user.save()
        count += 1

print(f"Successfully activated/verified {count} existing users.")

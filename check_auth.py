import os
import django
import sys

sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from django.contrib.auth import authenticate
from api.models import User

user_email = 'burhanuddinmoris52@gmail.com'
password = 'ChangeMe123!'

print(f"Direct authenticate test for: {user_email}")
user = authenticate(username=user_email, password=password)

if user:
    print(f"AUTHENTICATED! User ID: {user.id} | Active: {user.is_active}")
else:
    print("Direct authenticate FAILED.")
    # Check if user exists but password mismatch or deactivated
    db_user = User.objects.filter(email=user_email).first()
    if db_user:
        print(f"User exists in DB. ID: {db_user.id} | Active: {db_user.is_active} | Has Password: {bool(db_user.password)}")
        if not db_user.check_password(password):
            print("Password check FAILED.")
        else:
            print("Password check PASSED. Issues might be is_active or custom Auth Backend.")
    else:
        print("User NOT found in DB.")

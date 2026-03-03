import os
import django
import sys

# Setup Django Environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storeflow_backend.settings")
django.setup()

from api.models import User

def fix_admin(email, password):
    try:
        user = User.objects.get(email=email)
        print(f"Found user: {user.email}")
        
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.role = 'super_admin'
        user.set_password(password) # DEFINITELY hash and set the password
        user.save()
        
        print(f"✅ SUCCESS: {email} is now a Superuser/Admin with password reset.")
        print("You can now login at https://erp.decentinstitute.in/admin/")
    except User.DoesNotExist:
        print(f"❌ ERROR: User with email {email} not found in database.")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    target_email = "burhanuddinmoris52@gmail.com"
    target_pass = "b5253" # The password you provided
    fix_admin(target_email, target_pass)

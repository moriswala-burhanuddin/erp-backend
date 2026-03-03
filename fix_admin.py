import os
import django
import sys

# Setup Django Environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storeflow_backend.settings")
django.setup()

from api.models import User

def fix_admin(email):
    try:
        user = User.objects.get(email=email)
        print(f"Found user: {user.email}")
        
        user.is_staff = True
        user.is_superuser = True
        user.role = 'super_admin'
        user.save()
        
        print(f"✅ SUCCESS: {email} is now a Superuser/Admin.")
        print("You can now login at https://erp.decentinstitute.in/admin/")
    except User.DoesNotExist:
        print(f"❌ ERROR: User with email {email} not found in database.")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    target_email = "burhanuddinmoris52@gmail.com"
    fix_admin(target_email)

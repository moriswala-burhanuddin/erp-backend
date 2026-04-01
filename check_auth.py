import os
import django
import sys
from pathlib import Path

# Auto-detect BASE_DIR
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from django.contrib.auth import authenticate
from api.models import User

# --- INPUT YOUR TEST CREDENTIALS HERE ---
user_email = 'admin@tmrtools.com' # Try your email
password = 'ChangeMe123!'        # Try your password
# ----------------------------------------

print(f"\n--- [DIAGNOSTIC] Checking Authentication for: {user_email} ---")
db_user = User.objects.filter(email=user_email).first()

if not db_user:
    print(f"[ERROR] User '{user_email}' NOT found in the database.")
    sys.exit(1)

print(f"[INFO] User exists: ID={db_user.id}, Active={db_user.is_active}, Verified={db_user.is_verified}, Role={db_user.role}")

# Test direct password check
if db_user.check_password(password):
    print("[SUCCESS] Password check (check_password) PASSED.")
else:
    print("[FAIL] Password check (check_password) FAILED.")

# Test full Django authentication (includes backend/active checks)
user = authenticate(username=user_email, password=password)

if user:
    print(f"[SUCCESS] authenticate() PASSED. User is valid and ready for Login.")
else:
    print(f"[FAIL] authenticate() FAILED. This usually means the user is inactive or the AUTH_BACKEND is blocking it.")
    if not db_user.is_active:
        print("[TIP] User is marked as INACTIVE (is_active=False).")
    
print("-" * 50)

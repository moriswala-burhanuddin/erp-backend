import os
import django
import sys

sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from api.models import User, Customer, Store

# Cleanup
test_email = 'auto_user_test@gmail.com'
User.objects.filter(email=test_email).delete()
Customer.objects.filter(email=test_email).delete()

print(f"--- TESTING AUTO-USER CREATION FOR {test_email} ---")

store = Store.objects.first()
if not store:
    print("No store found!")
    sys.exit(1)

# Create a customer manually (like in the ERP admin)
customer = Customer.objects.create(
    name='Auto User Test',
    email=test_email,
    phone='1234567890',
    type='retail',
    status='active',
    source='POS',
    store=store
)

print(f"Customer created ID: {customer.id}")

# Verification: User should have been created by signal
user = User.objects.filter(email=test_email).first()

if user:
    print(f"SUCCESS: User auto-created for customer!")
    print(f"USER EMAIL: {user.email}")
    print(f"USER ROLE: {user.role}")
    print(f"USER ACTIVE: {user.is_active}")
    print(f"USER VERIFIED: {user.is_verified}")
else:
    print("FAILURE: User was NOT auto-created.")

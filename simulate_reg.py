from rest_framework.test import APIClient
import os
import django
import sys

sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from api.models import User, Customer

client = APIClient()

test_email = 'test_reg_unique@gmail.com'
User.objects.filter(email=test_email).delete()
Customer.objects.filter(email=test_email).delete()

data = {
    'email': test_email,
    'password': 'Password123!',
    'full_name': 'Test Registration User',
    'username': 'testreg'
}

print(f"--- SIMULATING REGISTRATION FOR {test_email} ---")
response = client.post('/api/auth/register', data, format='json')

print(f"STATUS: {response.status_code}")
print(f"DATA: {response.data}")

# Check if User exists in DB
user_exists = User.objects.filter(email=test_email).exists()
customer_exists = Customer.objects.filter(email=test_email).exists()

print(f"USER CREATED IN DB: {user_exists}")
print(f"CUSTOMER CREATED IN DB: {customer_exists}")

if user_exists:
    user = User.objects.get(email=test_email)
    print(f"USER ID: {user.id} | ACTIVE: {user.is_active} | VERIFIED: {user.is_verified}")

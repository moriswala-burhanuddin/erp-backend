import os
import django
import sys
from django.db import connection

sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

with connection.cursor() as cursor:
    cursor.execute("SELECT id, email, is_active FROM api_user")
    rows = cursor.fetchall()
    print(f"--- RAW USER TABLE (api_user) ---")
    print(f"TOTAL ROWS: {len(rows)}")
    for row in rows:
        print(row)

    cursor.execute("SELECT id, name, email FROM api_customer WHERE email = 'aiwork449@gmail.com'")
    rows = cursor.fetchall()
    print(f"\n--- SEARCHING CUSTOMER TABLE ---")
    for row in rows:
        print(row)

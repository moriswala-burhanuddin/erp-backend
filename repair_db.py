import os
import sys
import django
from django.db import connection

# Add current directory to path so it can find storeflow_backend
sys.path.append(os.getcwd())

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

def repair():
    cursor = connection.cursor()
    
    # 1. Fix Product table
    print("Checking api_product...")
    try:
        cursor.execute("ALTER TABLE api_product ADD COLUMN IF NOT EXISTS discount_percentage INTEGER DEFAULT 0")
        print("Added discount_percentage to api_product")
    except Exception as e: print(f"Product discount_percentage note: {e}")

    try:
        cursor.execute("ALTER TABLE api_product ADD COLUMN IF NOT EXISTS price_inr NUMERIC(12, 2)")
        print("Added price_inr to api_product")
    except Exception as e: print(f"Product price_inr note: {e}")

    try:
        cursor.execute("ALTER TABLE api_product ADD COLUMN IF NOT EXISTS price_usd NUMERIC(12, 2)")
        print("Added price_usd to api_product")
    except Exception as e: print(f"Product price_usd note: {e}")

    try:
        cursor.execute("ALTER TABLE api_product ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE")
        cursor.execute("UPDATE api_product SET is_deleted = FALSE WHERE is_deleted IS NULL")
        print("Fixed is_deleted column in api_product")
    except Exception as e: print(f"Product is_deleted note: {e}")

    # Ensure store_id has a default if missing in some rows
    try:
        from .models import Store
        store = Store.objects.first()
        if store:
            cursor.execute(f"UPDATE api_product SET store_id = '{store.id}' WHERE store_id IS NULL")
            print(f"Fixed store_id in api_product (using {store.id})")
    except Exception as e: print(f"Product store_id repair note: {e}")

    # 2. Fix Customer table (just in case status/type are missing)
    print("Checking api_customer...")
    try:
        cursor.execute("ALTER TABLE api_customer ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active'")
        cursor.execute("UPDATE api_customer SET status = 'active' WHERE status IS NULL")
        print("Added status to api_customer")
    except Exception as e: print(f"Customer status note: {e}")

    try:
        cursor.execute("ALTER TABLE api_customer ADD COLUMN IF NOT EXISTS type VARCHAR(50) DEFAULT 'retail'")
        cursor.execute("UPDATE api_customer SET type = 'retail' WHERE type IS NULL")
        print("Added type to api_customer")
    except Exception as e: print(f"Customer type note: {e}")

    print("\nDatabase repair attempts finished.")

if __name__ == "__main__":
    repair()

import os
import django
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings') # Adjust 'backend' if your project renamed it
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

    # 2. Fix Customer table (just in case status/type are missing)
    print("Checking api_customer...")
    try:
        cursor.execute("ALTER TABLE api_customer ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active'")
        print("Added status to api_customer")
    except Exception as e: print(f"Customer status note: {e}")

    try:
        cursor.execute("ALTER TABLE api_customer ADD COLUMN IF NOT EXISTS type VARCHAR(50) DEFAULT 'retail'")
        print("Added type to api_customer")
    except Exception as e: print(f"Customer type note: {e}")

    print("\nDatabase repair attempts finished.")

if __name__ == "__main__":
    repair()

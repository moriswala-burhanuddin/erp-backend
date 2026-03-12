import os
import django
import sys
from decimal import Decimal

sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from api.models import User, Product, Sale, SaleReturn, Notification
from api.serializers import CustomTokenObtainPairSerializer

def test_returns_and_notifications():
    print("--- TESTING RETURNS & NOTIFICATIONS ---")
    
    # 1. Test Low Stock Notification trigger
    product = Product.objects.first()
    if product:
        print(f"Testing stock notification for: {product.name}")
        old_stock = product.quantity
        old_min = product.min_stock
        
        product.quantity = product.min_stock - 1
        product.save()
        
        # Give it a moment or just fresh query
        notif = Notification.objects.filter(title__contains=product.name).last()
        if notif:
            print(f"SUCCESS: Stock notification created: {notif.title}")
            print(f"Message: {notif.message}")
        else:
            print("FAILURE: Stock notification NOT created.")
            
        # Restore stock
        product.quantity = old_stock
        product.save()

    # 2. Test SaleReturn stock increase
    sale = Sale.objects.first()
    if sale and product:
        print(f"\nTesting sale return for product: {product.name}")
        initial_stock = product.quantity
        
        ret = SaleReturn.objects.create(
            sale=sale,
            product=product,
            quantity=Decimal('2.00'),
            reason="Defective",
            refund_amount=Decimal('100.00'),
            status='approved'
        )
        
        product.refresh_from_db()
        print(f"Initial Stock: {initial_stock}")
        print(f"Returned Qty: 2")
        print(f"Final Stock: {product.quantity}")
        if product.quantity == initial_stock + 2:
            print(f"SUCCESS: Stock increased after return.")
        else:
            print(f"FAILURE: Stock NOT increased correctly. Final: {product.quantity}, Expected: {initial_stock + 2}")

    print("\n--- VERIFICATION END ---")

if __name__ == "__main__":
    test_returns_and_notifications()

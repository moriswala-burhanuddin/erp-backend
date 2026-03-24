from django.core.management.base import BaseCommand
from api.models import (
    Sale, Purchase, Product, Customer, Supplier, Invoice, 
    Quotation, Attendance, Leave, Payroll, Transaction, 
    StockLog, StockTransfer, Receiving
)

class Command(BaseCommand):
    help = 'Clears old ERP data but keeps Stores, Users, Employees, and 3 test Products/Sales'

    def handle(self, *args, **options):
        self.stdout.write("Starting ERP data cleanup...")
        
        # 1. Keep 3 Products
        recent_product_ids = Product.objects.order_by('-created_at')[:3].values_list('id', flat=True)
        products_deleted, _ = Product.objects.exclude(id__in=recent_product_ids).delete()
        self.stdout.write(f"Cleared {products_deleted} products (kept 3).")

        # 2. Keep 3 Sales
        recent_sale_ids = Sale.objects.order_by('-date')[:3].values_list('id', flat=True)
        sales_deleted, _ = Sale.objects.exclude(id__in=recent_sale_ids).delete()
        self.stdout.write(f"Cleared {sales_deleted} sales (kept 3).")
        
        # 3. Clear other transactional/partner data completely
        partners_deleted = Customer.objects.all().delete()[0] + Supplier.objects.all().delete()[0]
        self.stdout.write(f"Cleared {partners_deleted} customers and suppliers.")
        
        docs_deleted = Invoice.objects.all().delete()[0] + Quotation.objects.all().delete()[0] + Purchase.objects.all().delete()[0]
        self.stdout.write(f"Cleared {docs_deleted} invoices, quotations, and purchases.")
        
        inv_deleted = StockLog.objects.all().delete()[0] + StockTransfer.objects.all().delete()[0] + Receiving.objects.all().delete()[0]
        self.stdout.write(f"Cleared {inv_deleted} stock logs, transfers, and receivings.")
        
        finance_deleted = Transaction.objects.all().delete()[0]
        self.stdout.write(f"Cleared {finance_deleted} transactions.")
        
        # 4. HR Data (Keeping Employees)
        hr_deleted = Attendance.objects.all().delete()[0] + Leave.objects.all().delete()[0] + Payroll.objects.all().delete()[0]
        self.stdout.write(f"Cleared {hr_deleted} HR records (attendance, leaves, payroll).")
        
        self.stdout.write(self.style.SUCCESS('ERP data reset complete. Stores, Users, and Employees preserved.'))

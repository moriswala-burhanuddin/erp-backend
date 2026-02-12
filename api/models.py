import random
import string
from django.db import models
from django.contrib.auth.models import AbstractUser

def generate_id(prefix='id'):
    """Generate a random ID similar to the frontend format: prefix-randomString"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    return f"{prefix}-{random_str}"

def generate_store_id(): return generate_id('store')
def generate_user_id(): return generate_id('user')
def generate_acc_id(): return generate_id('acc')
def generate_prod_id(): return generate_id('prod')
def generate_cust_id(): return generate_id('cust')
def generate_sale_id(): return generate_id('sale')
def generate_pur_id(): return generate_id('pur')
def generate_log_id(): return generate_id('log')
def generate_qtn_id(): return generate_id('qtn')
def generate_trans_id(): return generate_id('tr')
def generate_exp_id(): return generate_id('exp')
def generate_tax_id(): return generate_id('tax')
def generate_st_id(): return generate_id('st')
def generate_po_id(): return generate_id('po')
def generate_lp_id(): return generate_id('lp')
def generate_com_id(): return generate_id('com')

class Store(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_store_id)
    name = models.CharField(max_length=255)
    branch = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class User(AbstractUser):
    id = models.CharField(max_length=50, primary_key=True, default=generate_user_id)
    role = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('staff', 'Staff')], default='staff')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # We use email as login instead of username for better UX
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # username is still required by AbstractUser unless we override more

    def __str__(self):
        return f"{self.email} ({self.role})"

class Account(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_acc_id)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='accounts')
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class Product(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_prod_id)
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    category = models.CharField(max_length=100, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    unit = models.CharField(max_length=50, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    barcode = models.CharField(max_length=100, null=True, blank=True)
    tax_slab = models.ForeignKey('TaxSlab', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    last_used = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class Customer(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_cust_id)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    email = models.EmailField(null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    credit_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_purchases = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='customers')
    joined_at = models.DateTimeField(null=True, blank=True)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class Sale(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_sale_id)
    invoice_number = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=50)
    items = models.TextField() # JSON string
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    profit = models.DecimalField(max_digits=12, decimal_places=2)
    payment_mode = models.CharField(max_length=50)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='sales')
    date = models.DateTimeField()
    quotation_id = models.CharField(max_length=50, null=True, blank=True)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class Purchase(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_pur_id)
    invoice_number = models.CharField(max_length=100, unique=True)
    supplier = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    items = models.TextField() # JSON string
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='purchases')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateTimeField()
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class StockLog(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_log_id)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    quantity_change = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=100)
    reference_id = models.CharField(max_length=100, null=True, blank=True)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Quotation(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_qtn_id)
    quotation_number = models.CharField(max_length=100, unique=True)
    items = models.TextField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    customer_id = models.CharField(max_length=50, null=True, blank=True) # Loose link
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_phone = models.CharField(max_length=50, null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    date = models.DateTimeField()
    expiry_date = models.DateTimeField()
    status = models.CharField(max_length=50)
    notes = models.TextField(null=True, blank=True)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class Transaction(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_trans_id)
    type = models.CharField(max_length=50, choices=[
        ('cash_in', 'Cash In'), 
        ('cash_out', 'Cash Out'), 
        ('expense', 'Expense'), 
        ('sale_return', 'Sale Return')
    ])
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateTimeField()
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class ExpenseCategory(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_exp_id)
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    updated_at = models.DateTimeField(auto_now=True)

class TaxSlab(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_tax_id)
    name = models.CharField(max_length=255)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

class StockTransfer(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_st_id)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    from_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='transfers_sent')
    to_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='transfers_received')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending')
    transferred_at = models.DateTimeField(null=True, blank=True)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class PurchaseOrder(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_po_id)
    supplier = models.CharField(max_length=255)
    items = models.TextField() # JSON string
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('draft', 'Draft'), ('sent', 'Sent'), ('received', 'Received'), ('cancelled', 'Cancelled')], default='draft')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='purchase_orders')
    date = models.DateTimeField()
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class LoyaltyPoint(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_lp_id)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loyalty_points')
    points = models.IntegerField()
    reason = models.CharField(max_length=255, null=True, blank=True)
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Commission(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_com_id)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commissions')
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='commissions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


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
def generate_sup_id(): return generate_id('sup')
def generate_scf_id(): return generate_id('scf')
def generate_scfv_id(): return generate_id('scfv')
def generate_stx_id(): return generate_id('stx')
def generate_pt_id(): return generate_id('pt')
def generate_recv_id(): return generate_id('recv')
def generate_ri_id(): return generate_id('ri')
def generate_doc_id(): return generate_id('doc')
def generate_sp_id(): return generate_id('sp')
def generate_gc_id(): return generate_id('gc')
def generate_wo_id(): return generate_id('wo')
def generate_del_id(): return generate_id('del')
def generate_inv_id(): return generate_id('inv')
def generate_invitem_id(): return generate_id('ivi')
def generate_chq_id(): return generate_id('chq')
def generate_cat_id(): return generate_id('cat')
def generate_pimg_id(): return generate_id('pimg')
def generate_feat_id(): return generate_id('feat')
def generate_cart_id(): return generate_id('cart')
def generate_ci_id(): return generate_id('ci')
def generate_rev_id(): return generate_id('rev')
def generate_fb_id(): return generate_id('fb')



class Store(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_store_id)
    name = models.CharField(max_length=255)
    branch = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.branch})" if self.branch else self.name

class User(AbstractUser):
    id = models.CharField(max_length=50, primary_key=True, default=generate_user_id)
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Admin'), 
        ('staff', 'Staff'),
        ('hr_manager', 'HR Manager'),
        ('sales_manager', 'Sales Manager'),
        ('inventory_manager', 'Inventory Manager'),
        ('accountant', 'Accountant'),
        ('employee', 'Employee'),
        ('user', 'User'),
        ('super_admin', 'Super Admin')
    ], default='user')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    is_driver = models.BooleanField(default=False)
    
    # Elegance Profile Fields
    phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # We use email as login instead of username for better UX
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # username is still required by AbstractUser unless we override more

    def __str__(self):
        return f"{self.email} ({self.role})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

class Account(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_acc_id)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='accounts')
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class Category(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_cat_id)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='categories')
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_prod_id)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.TextField(null=True, blank=True) # URL or Base64
    sku = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    unit = models.CharField(max_length=50, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    barcode = models.CharField(max_length=100, null=True, blank=True)
    
    # Elegance Frontend Compatibility
    discount_percentage = models.IntegerField(default=0)
    price_inr = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_usd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    tax_slab = models.ForeignKey('TaxSlab', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    last_used = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_kit = models.BooleanField(default=False)
    limited_qty = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class Customer(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_cust_id)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    email = models.EmailField(null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=50, choices=[('retail', 'Retail'), ('wholesale', 'Wholesale')], default='retail')
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')
    source = models.CharField(max_length=50, default='POS') # POS, Online, etc.
    credit_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_purchases = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='customers')
    joined_at = models.DateTimeField(null=True, blank=True)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

def generate_gc_id(): return generate_id('gc')
def generate_wo_id(): return generate_id('wo')
def generate_del_id(): return generate_id('del')
def generate_sp_id(): return generate_id('sp')

class Sale(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('suspended', 'Suspended'),
        ('work_order', 'Work Order'),
        ('delivery', 'Delivery'),
        ('returned', 'Returned'),
    ]
    id = models.CharField(max_length=50, primary_key=True, default=generate_sale_id)
    invoice_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='completed')
    type = models.CharField(max_length=50) # retail, wholesale, etc.
    items = models.TextField() # JSON string
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    profit = models.DecimalField(max_digits=12, decimal_places=2)
    payment_mode = models.CharField(max_length=50) # Legacy single mode
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='sales')
    source = models.CharField(max_length=50, default='POS') # POS, Online, etc.
    date = models.DateTimeField()
    quotation_id = models.CharField(max_length=50, null=True, blank=True)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class SalePayment(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_sp_id)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments')
    payment_mode = models.CharField(max_length=50) # cash, card, upi, store_credit
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

class GiftCard(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_gc_id)
    card_number = models.CharField(max_length=100, unique=True)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

class WorkOrder(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_wo_id)
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name='work_order')
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], default='pending')
    notes = models.TextField(null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

class Delivery(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_del_id)
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name='delivery')
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField()
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_cod = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('dispatched', 'Dispatched'),
        ('delivered', 'Delivered')
    ], default='pending')
    delivery_date = models.DateTimeField(null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

class Supplier(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_sup_id)
    company_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    website = models.URLField(max_length=255, null=True, blank=True)
    
    # Address Information
    address_line1 = models.TextField(null=True, blank=True)
    address_line2 = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    
    # Financial Information
    supplier_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    account_number = models.CharField(max_length=100, null=True, blank=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_terms = models.ForeignKey('PaymentTerm', on_delete=models.SET_NULL, null=True, blank=True, related_name='suppliers')
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_number = models.CharField(max_length=100, null=True, blank=True)
    currency = models.CharField(max_length=10, default='USD')
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Internal & Meta
    internal_notes = models.TextField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    logo = models.TextField(null=True, blank=True) # URL or Base64
    documents = models.TextField(null=True, blank=True) # JSON list
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('disabled', 'Disabled')], default='active')
    rating = models.IntegerField(default=5)
    is_preferred = models.BooleanField(default=False)
    is_blacklisted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='suppliers')
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

class SupplierCustomField(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_scf_id)
    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=50, choices=[
        ('text', 'Text'), ('number', 'Number'), ('date', 'Date'), ('dropdown', 'Dropdown')
    ])
    is_required = models.BooleanField(default=False)
    show_on_receipt = models.BooleanField(default=False)
    hide_label = models.BooleanField(default=False)
    options = models.TextField(null=True, blank=True) # JSON for dropdown
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='supplier_custom_fields')
    updated_at = models.DateTimeField(auto_now=True)

class SupplierCustomFieldValue(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_scfv_id)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='custom_values')
    field = models.ForeignKey(SupplierCustomField, on_delete=models.CASCADE)
    value = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class PaymentTerm(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_pt_id)
    name = models.CharField(max_length=100)
    days = models.IntegerField(default=0)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='payment_terms')
    updated_at = models.DateTimeField(auto_now=True)

class DeliveryZone(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_del_id)
    name = models.CharField(max_length=255)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='delivery_zones')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (${self.fee})"

class SupplierDocument(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_doc_id)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_documents')
    name = models.CharField(max_length=255)
    file_path = models.TextField() # Local or S3 path
    file_type = models.CharField(max_length=50, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

class SupplierTransaction(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_stx_id)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=50, choices=[
        ('purchase', 'Purchase'), ('payment', 'Payment'), ('credit_note', 'Credit Note'), ('opening_balance', 'Opening Balance')
    ])
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField()
    reference_id = models.CharField(max_length=100, null=True, blank=True) # Invoice # or Receipt #
    description = models.TextField(null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


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


def generate_emp_id(): return generate_id('emp')
def generate_att_id(): return generate_id('att')
def generate_leave_id(): return generate_id('leave')
def generate_payroll_id(): return generate_id('pay')
def generate_perf_id(): return generate_id('perf')

class Employee(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_emp_id)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    joining_date = models.DateField()
    documents = models.TextField(null=True, blank=True) # JSON list of document URLs
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='employees')
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class Attendance(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_att_id)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('present', 'Present'), ('absent', 'Absent'), ('late', 'Late'), ('half_day', 'Half Day')])
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class Leave(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_leave_id)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    type = models.CharField(max_length=50, choices=[('sick', 'Sick Leave'), ('casual', 'Casual Leave'), ('earned', 'Earned Leave')])
    reason = models.TextField()
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class Payroll(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_payroll_id)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    month = models.DateField() # Store as first day of month
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('generated', 'Generated'), ('paid', 'Paid')], default='generated')
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class PerformanceReview(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_perf_id)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_reviews')
    month = models.DateField()
    kpi_score = models.DecimalField(max_digits=5, decimal_places=2) # 0-100
    rating = models.IntegerField() # 1-5
    comments = models.TextField(null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


# ─────────────────────────────────────────────────────────────
# RECEIVING MODULE
# ─────────────────────────────────────────────────────────────

class Receiving(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('suspended', 'Suspended'),
        ('completed', 'Completed'),
        ('returned', 'Returned'),
    ]
    id               = models.CharField(max_length=50, primary_key=True, default=generate_recv_id)
    receiving_number = models.CharField(max_length=100, unique=True)
    supplier         = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='receivings')
    purchase_order   = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='receivings')
    total_amount     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_due       = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    account          = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='receivings')
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes            = models.TextField(null=True, blank=True)
    custom_fields    = models.JSONField(null=True, blank=True)  # extra fields dict
    store            = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='receivings')
    device_id        = models.CharField(max_length=50, null=True, blank=True)
    completed_at     = models.DateTimeField(null=True, blank=True)
    updated_at       = models.DateTimeField(auto_now=True)

    def __str__(self):
        supplier_name = self.supplier.company_name if self.supplier else "No Supplier"
        return f"{self.receiving_number} — {supplier_name}"


class ReceivingItem(models.Model):
    id            = models.CharField(max_length=50, primary_key=True, default=generate_ri_id)
    receiving     = models.ForeignKey(Receiving, on_delete=models.CASCADE, related_name='items')
    product       = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='receiving_items')
    product_name  = models.CharField(max_length=255)
    cost          = models.DecimalField(max_digits=10, decimal_places=2)
    quantity      = models.DecimalField(max_digits=10, decimal_places=3)
    discount_pct  = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total         = models.DecimalField(max_digits=12, decimal_places=2)
    batch_number  = models.CharField(max_length=100, null=True, blank=True)
    expiry_date   = models.DateField(null=True, blank=True)
    serial_number = models.CharField(max_length=100, null=True, blank=True)
    location      = models.CharField(max_length=100, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    upc           = models.CharField(max_length=100, null=True, blank=True)
    description   = models.TextField(null=True, blank=True)
    store         = models.ForeignKey(Store, on_delete=models.CASCADE)
    updated_at    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"


# ─────────────────────────────────────────────────────────────
# INVOICE MODULE (Standalone Accounts Receivable/Payable)
# ─────────────────────────────────────────────────────────────

class Invoice(models.Model):
    TYPE_CHOICES = [
        ('customer', 'Customer Invoice (AR)'),
        ('supplier', 'Supplier Bill (AP)'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    id = models.CharField(max_length=50, primary_key=True, default=generate_inv_id)
    invoice_number = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Links
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    
    # Totals
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Dates
    date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    # Extra Meta
    notes = models.TextField(null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='invoices')
    device_id = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        party = self.customer.name if self.type == 'customer' and self.customer else (self.supplier.company_name if self.supplier else 'Unknown')
        return f"{self.invoice_number} — {party} ({self.total_amount})"

class InvoiceItem(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_invitem_id)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='invoice_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255) # Snapshot
    description = models.TextField(null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_name} x {self.quantity} (Inv: {self.invoice.invoice_number})"



class Cheque(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_chq_id)
    party_type = models.CharField(max_length=20, choices=[('supplier', 'Supplier'), ('customer', 'Customer')])
    party_id = models.CharField(max_length=50) # Reference to Customer/Supplier ID
    party_name = models.CharField(max_length=255)
    cheque_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    issue_date = models.DateField()
    clearing_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('cleared', 'Cleared'),
        ('bounced', 'Bounced'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='cheques')
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cheque {self.cheque_number} - {self.party_name} ({self.status})"

# ──────────────────────────────────────────────────────────────
# E-COMMERCE MODELS (Elegance Website Integration)
# ──────────────────────────────────────────────────────────────

class Review(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_rev_id)
    user_name = models.CharField(max_length=255)
    user_email = models.EmailField(null=True, blank=True)
    product_id = models.CharField(max_length=50, null=True, blank=True) 
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user_name} ({self.rating} stars)"

class ProductImage(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_pimg_id)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.TextField(null=True, blank=True) # URL or Base64
    is_thumbnail = models.BooleanField(default=False)

class KeyFeature(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_feat_id)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='features')
    title = models.CharField(max_length=200)
    description = models.TextField()

class Cart(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_cart_id)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts', null=True, blank=True) # For logged-in users
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True) # For anonymous users
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id} (User: {self.user.username if self.user else 'Anonymous'})"

class CartItem(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_ci_id)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    price_at_time = models.DecimalField(max_digits=12, decimal_places=2) # Snapshot of price when added to cart
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.id}"

class Feedback(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_fb_id)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    rating = models.IntegerField(default=5) # For general satisfaction
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name}: {self.subject}"


class OnlineOrder(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Failed', 'Failed'),
    )
    user_email = models.EmailField()
    order_id = models.CharField(max_length=100, unique=True) # Razorpay Order ID
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    sale = models.OneToOneField('Sale', on_delete=models.SET_NULL, null=True, blank=True, related_name='online_order')
    
    # Snapshot info
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Shipping & Delivery
    shipping_method = models.CharField(max_length=100, blank=True, null=True)
    courier_name = models.CharField(max_length=100, blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery_date = models.DateField(blank=True, null=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.user_email} ({self.status})"

class OnlineOrderItem(models.Model):
    order = models.ForeignKey(OnlineOrder, on_delete=models.CASCADE, related_name='web_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255) # Snapshot
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

class OnlineReturn(models.Model):
    STATUS_CHOICES = (
        ('Requested', 'Requested'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Picked Up', 'Picked Up'),
        ('Refunded', 'Refunded'),
        ('Completed', 'Completed'),
    )
    order = models.ForeignKey(OnlineOrder, on_delete=models.CASCADE, related_name='returns')
    items = models.TextField() # JSON list of items being returned
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Requested')
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Return for Order {self.order.order_id} - {self.status}"

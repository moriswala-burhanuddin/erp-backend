from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Store, User, Account, Product, Customer, Sale, Purchase, 
    StockLog, Quotation, Transaction, ExpenseCategory, TaxSlab, 
    StockTransfer, PurchaseOrder, LoyaltyPoint, Commission,
    Supplier, PaymentTerm, SupplierDocument,
    Receiving, ReceivingItem, SaleReturn, Notification,
    OnlineOrder, OnlineOrderItem, OnlineReturn,
    Client, Device, Feature, ClientFeature,
    Employee, Attendance, Leave, Payroll, PerformanceReview, Shift
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'store', 'is_staff')
    list_filter = ('role', 'store', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'role', 'store', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'phone', 'id')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'quantity', 'selling_price', 'store', 'is_deleted')
    list_filter = ('store', 'category', 'is_deleted')
    search_fields = ('name', 'barcode', 'sku')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'total_amount', 'date', 'type', 'store')
    list_filter = ('store', 'type', 'payment_mode')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'total_purchases', 'store', 'joined_at')

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'balance', 'store')

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'supplier', 'total_amount', 'store')

@admin.register(StockLog)
class StockLogAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'quantity_change', 'reason', 'created_at')

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ('quotation_number', 'customer_name', 'total_amount', 'status')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'amount', 'store', 'date')
    list_filter = ('type', 'store')

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'updated_at')

@admin.register(TaxSlab)
class TaxSlabAdmin(admin.ModelAdmin):
    list_display = ('name', 'percentage', 'updated_at')

@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ('product', 'from_store', 'to_store', 'quantity', 'status')

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'total_amount', 'status', 'date')

@admin.register(LoyaltyPoint)
class LoyaltyPointAdmin(admin.ModelAdmin):
    list_display = ('customer', 'points', 'reason', 'created_at')

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'sale', 'amount', 'percentage', 'status')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'supplier_code', 'email', 'phone', 'status', 'current_balance', 'store')
    list_filter = ('store', 'status', 'is_preferred', 'is_blacklisted', 'is_deleted')
    search_fields = ('company_name', 'email', 'phone', 'supplier_code', 'tax_number')
    ordering = ('company_name',)

@admin.register(PaymentTerm)
class PaymentTermAdmin(admin.ModelAdmin):
    list_display = ('name', 'days', 'store')
    list_filter = ('store',)
    search_fields = ('name',)

@admin.register(SupplierDocument)
class SupplierDocumentAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'name', 'file_type', 'uploaded_at')
    list_filter = ('file_type',)
    search_fields = ('name', 'supplier__company_name')


class ReceivingItemInline(admin.TabularInline):
    model = ReceivingItem
    extra = 0
    fields = ('product', 'product_name', 'quantity', 'cost', 'discount_pct', 'total', 'batch_number', 'expiry_date')
    readonly_fields = ('total',)

@admin.register(Receiving)
class ReceivingAdmin(admin.ModelAdmin):
    list_display = ('id', 'receiving_number', 'status', 'updated_at')
    ordering = ('-updated_at',)

@admin.register(ReceivingItem)
class ReceivingItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'quantity', 'cost', 'total')

@admin.register(SaleReturn)
class SaleReturnAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale', 'customer', 'product', 'quantity', 'refund_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('reason', 'customer__name')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('title', 'message')

class OnlineOrderItemInline(admin.TabularInline):
    model = OnlineOrderItem
    extra = 0

@admin.register(OnlineOrder)
class OnlineOrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user_email', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'user_email', 'full_name')
    inlines = [OnlineOrderItemInline]

@admin.register(OnlineOrderItem)
class OnlineOrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'price')

@admin.register(OnlineReturn)
class OnlineReturnAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'refund_amount', 'created_at')
    list_filter = ('status', 'created_at')

# ──────────────────────────────────────────────────────────────
# LICENSE & FEATURE FLAG ADMIN
# ──────────────────────────────────────────────────────────────

class DeviceInline(admin.TabularInline):
    model = Device
    extra = 0
    readonly_fields = ('registered_at', 'last_active')

class ClientFeatureInline(admin.TabularInline):
    model = ClientFeature
    extra = 0

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'license_key', 'id', 'created_at')
    search_fields = ('name', 'license_key', 'id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [DeviceInline, ClientFeatureInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Provisions any features that weren't added/edited via the inline
        form.instance.provision_default_features()

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'client', 'id', 'registered_at', 'last_active')
    search_fields = ('device_id', 'client__name', 'id')
    readonly_fields = ('id', 'registered_at', 'last_active')
    list_filter = ('client',)

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'created_at')
    search_fields = ('name', 'id')
    readonly_fields = ('id', 'created_at')

@admin.register(ClientFeature)
class ClientFeatureAdmin(admin.ModelAdmin):
    list_display = ('client', 'feature', 'enabled', 'id', 'updated_at')
    list_filter = ('enabled', 'feature', 'client')
    readonly_fields = ('id', 'updated_at')
    search_fields = ('client__name', 'feature__name', 'id')
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'department', 'designation', 'store', 'is_deleted')
    search_fields = ('id', 'user__email', 'department', 'designation')
    list_filter = ('department', 'store', 'is_deleted')

    def user_email(self, obj):
        return obj.user.email if obj.user else "N/A"

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'check_in', 'check_out')
    list_filter = ('status', 'date')

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('employee', 'type', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'type')

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'year', 'net_salary', 'status')
    list_filter = ('status', 'year', 'month')

@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ('employee', 'reviewer', 'date', 'rating')
    list_filter = ('rating', 'date')

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('employee', 'type', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'type')

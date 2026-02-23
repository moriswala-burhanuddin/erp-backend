from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Store, User, Account, Product, Customer, Sale, Purchase, 
    StockLog, Quotation, Transaction, ExpenseCategory, TaxSlab, 
    StockTransfer, PurchaseOrder, LoyaltyPoint, Commission,
    Supplier, PaymentTerm, SupplierDocument,
    Receiving, ReceivingItem
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
    list_display = ('receiving_number', 'supplier', 'status', 'total_amount', 'amount_paid', 'amount_due', 'store', 'updated_at')
    list_filter = ('store', 'status')
    search_fields = ('receiving_number', 'supplier__company_name')
    ordering = ('-updated_at',)
    inlines = [ReceivingItemInline]
    readonly_fields = ('completed_at',)

@admin.register(ReceivingItem)
class ReceivingItemAdmin(admin.ModelAdmin):
    list_display = ('receiving', 'product_name', 'quantity', 'cost', 'total', 'batch_number')
    search_fields = ('product_name', 'receiving__receiving_number')

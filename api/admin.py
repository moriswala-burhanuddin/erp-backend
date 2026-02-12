from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Store, User, Account, Product, Customer, Sale, Purchase, 
    StockLog, Quotation, Transaction, ExpenseCategory, TaxSlab, 
    StockTransfer, PurchaseOrder, LoyaltyPoint, Commission
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

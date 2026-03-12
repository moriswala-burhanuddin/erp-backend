from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from datetime import datetime, date
from django.utils import timezone
from django.db import transaction
import json
from .models import (
    Store, Account, Product, Customer, Sale, Purchase, StockLog, User, 
    Quotation, Transaction, ExpenseCategory, TaxSlab, StockTransfer, 
    PurchaseOrder, LoyaltyPoint, Commission,
    Employee, Attendance, Leave, Payroll, PerformanceReview,
    Supplier, SupplierCustomField, SupplierCustomFieldValue, SupplierTransaction,
    PaymentTerm, SupplierDocument,
    Receiving, ReceivingItem,
    GiftCard, SalePayment, WorkOrder, Delivery, DeliveryZone,
    Invoice, InvoiceItem, Cheque, Category,
    OnlineOrder, OnlineOrderItem, OnlineReturn,
    SaleReturn, Notification
)
from django.db.models import Sum, Count, F, Q


from .serializers import (
    EmployeeSerializer, AttendanceSerializer, LeaveSerializer, 
    PayrollSerializer, PerformanceReviewSerializer,
    SupplierSerializer, SupplierCustomFieldSerializer, 
    SupplierCustomFieldValueSerializer, SupplierTransactionSerializer,
    PaymentTermSerializer, SupplierDocumentSerializer,
    ReceivingSerializer, ReceivingItemSerializer,
    InvoiceSerializer, InvoiceItemSerializer, ChequeSerializer,
    ProductSerializer, CustomerSerializer, SaleSerializer,
    UserRegistrationSerializer, CategorySerializer,
    ProductImageSerializer, KeyFeatureSerializer, CartSerializer, CartItemSerializer,
    ReviewSerializer, FeedbackSerializer,
    OnlineOrderSerializer, OnlineOrderItemSerializer, OnlineReturnSerializer,
    SaleReturnSerializer, NotificationSerializer
)


from rest_framework import viewsets

from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
import decimal
from decimal import Decimal
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        "status": "online",
        "version": "1.0.7",
        "roles": [c[0] for c in User._meta.get_field('role').choices]
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def db_diagnostic(request):
    from django.db import connection
    cursor = connection.cursor()
    tables = connection.introspection.table_names()
    
    diagnostic = {
        "tables": tables,
        "database": connection.settings_dict['NAME'],
        "columns": {}
    }
    
    # Check specific critical tables for new columns
    check_tables = {
        "api_product": ["discount_percentage", "price_inr", "price_usd"],
        "api_customer": ["source", "joined_at"],
        "api_user": ["address_line1", "phone", "role"]
    }
    
    for table, cols in check_tables.items():
        if table in tables:
            actual_cols = [c[0] for c in connection.introspection.get_table_description(cursor, table)]
            diagnostic["columns"][table] = {
                "missing": [c for c in cols if c not in actual_cols],
                "present": [c for c in cols if c in actual_cols]
            }
        else:
            diagnostic["columns"][table] = "TABLE MISSING"
            
    # Check migrations
    from django.db.migrations.recorder import MigrationRecorder
    applied_migrations = MigrationRecorder.Migration.objects.filter(app='api').values_list('name', flat=True)
    diagnostic["migrations"] = list(applied_migrations)
            
    return Response(diagnostic)

class PushEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        payload = data.get('payload', {})
        print(f"SYNC PUSH RECEIVED: Payload keys: {list(payload.keys())}")
        if 'products' in payload:
            print(f"SYNC PUSH PRODUCTS: {payload['products']}")
        
        device_id = data.get('deviceId')
        
        # Order matters for Foreign Keys
        ORDER = [
            'stores', 
            'users', 
            'accounts', 
            'categories',
            'expense_categories',
            'tax_slabs',
            'customers', 
            'payment_terms',
            'suppliers',
            'supplier_custom_fields',
            'supplier_custom_values',
            'products', 
            'quotations',
            'sales', 
            'purchases', 
            'supplier_transactions',
            'supplier_documents',
            'purchase_orders',
            'stock_transfers',
            'transactions', 
            'stock_logs',
            'loyalty_points',
            'commissions',
            'receivings',
            'receiving_items',
            'invoices',
            'invoice_items',
            'cheques',
            'attendance',
            'leaves',
            'employees',
            'payroll',
            'performance_reviews',
            'product_images',
            'key_features',
        ]


        synced_ids = {table: [] for table in ORDER}

        try:
            with transaction.atomic():
                for table in ORDER:
                    if table not in payload:
                        continue
                    
                    rows = payload[table]
                    model = self.get_model(table)
                    if not model:
                        continue

                    for row in rows:
                        # 1. Convert camelCase to snake_case for all keys
                        row_data = {}
                        for k, v in row.items():
                            if k == 'sync_status': continue
                            # Convert camelCase to snake_case
                            snake_key = ''.join(['_' + c.lower() if c.isupper() else c for c in k]).lstrip('_')
                            row_data[snake_key] = v
                        
                        # Debug logging
                        if table == 'users':
                            print(f"SYNCING USER: {row_data.get('email')} | Role: {row_data.get('role')} | Active: {row_data.get('is_active')}")
                        
                        # Prepare data for update_or_create
                        
                        # Ensure password is hashed if provided as plain text
                        if table == 'users':
                            # NEVER let password be null or empty string
                            if not row_data.get('password'):
                                from django.contrib.auth.hashers import make_password
                                row_data['password'] = make_password('ChangeMe123!')
                                print(f"DEBUG: Setting default password for {row_data.get('email')}")
                            elif not row_data['password'].startswith(('pbkdf2_', 'bcrypt', '$2b$', '$2a$', 'argon2')):
                                from django.contrib.auth.hashers import make_password
                                row_data['password'] = make_password(row_data['password'])
                                print(f"DEBUG: Hashing plain-text password for {row_data.get('email')}")
                                
                            if 'email' in row_data and not row_data.get('username'):
                                row_data['username'] = row_data['email']

                            # Normalize roles: default to staff if invalid
                            valid_roles = [c[0] for c in model._meta.get_field('role').choices]
                            if row_data.get('role') not in valid_roles:
                                print(f"DEBUG: Normalizing role '{row_data.get('role')}' to 'staff' for {row_data.get('email')}")
                                row_data['role'] = 'staff'

                            # Ensure is_active is True for synced users
                            if 'is_active' not in row_data:
                                row_data['is_active'] = True
                            
                            # Admin-created users in ERP are pre-verified
                            row_data['is_verified'] = True

                            # [PROMOTION LOGIC] Grant Django admin access for admin roles
                            if row_data.get('role') in ['admin', 'super_admin']:
                                row_data['is_staff'] = True
                                row_data['is_superuser'] = True
                                print(f"DEBUG: Promoting {row_data.get('email')} to STAFF/SUPERUSER")

                            # Split name into first and last name
                            if 'name' in row_data:
                                name_parts = row_data['name'].split(' ', 1)
                                row_data['first_name'] = name_parts[0]
                                row_data['last_name'] = name_parts[1] if len(name_parts) > 1 else ''

                        # Filter out any fields that don't exist in the Django model
                        valid_fields = {f.name for f in model._meta.get_fields() if not (f.is_relation and not f.concrete)}
                        # Also allow attnames (like store_id)
                        valid_fields.update({getattr(f, 'attname', None) for f in model._meta.get_fields()})
                        
                        # Normalize data: filter non-existent fields and treat empty strings/None appropriately
                        cleaned_data = {}
                        for k, v in row_data.items():
                            if k not in valid_fields:
                                continue
                            
                            # Determine if the field allows NULL
                            field_obj = next((f for f in model._meta.get_fields() if f.name == k or getattr(f, 'attname', None) == k), None)
                            is_nullable = getattr(field_obj, 'null', False)
                            internal_type = field_obj.get_internal_type() if field_obj else ""

                            if v == "" or v is None:
                                if is_nullable:
                                    cleaned_data[k] = None
                                elif internal_type in ['CharField', 'TextField']:
                                    cleaned_data[k] = ""
                                else:
                                    cleaned_data[k] = v
                            else:
                                # Format conversion for Date/Time fields from ISO strings
                                if internal_type == 'TimeField' and 'T' in str(v):
                                    try:
                                        cleaned_data[k] = str(v).split('T')[1].split('.')[0]
                                    except Exception:
                                        cleaned_data[k] = v
                                elif internal_type == 'DateField' and 'T' in str(v):
                                    cleaned_data[k] = str(v).split('T')[0]
                                else:
                                    cleaned_data[k] = v
                        
                        # Defensively ensure first/last name are never None for Users
                        if table == 'users':
                            if cleaned_data.get('first_name') is None: cleaned_data['first_name'] = ""
                            if cleaned_data.get('last_name') is None: cleaned_data['last_name'] = ""
                        
                        # Debug: Print what we are about to save for users specifically
                        if table == 'users':
                            print(f"DEBUG: Cleaned User Data for {cleaned_data.get('email')}: {list(cleaned_data.keys())}")
                            if 'password' not in cleaned_data or cleaned_data.get('password') is None:
                                print(f"CRITICAL: PASSWORD STILL MISSING FOR {cleaned_data.get('email')}!")
                                # One last fallback to avoid 400
                                from django.contrib.auth.hashers import make_password
                                cleaned_data['password'] = make_password('ChangeMe123!')

                        obj_id = cleaned_data.pop('id')
                        try:
                            # Pre-check: validate required FK fields are present before saving
                            required_fk_fields = [
                                f.attname for f in model._meta.get_fields()
                                if hasattr(f, 'attname') and f.is_relation
                                and not getattr(f, 'null', True)
                                and f.concrete
                            ]
                            missing_fks = [fk for fk in required_fk_fields if cleaned_data.get(fk) is None]
                            if missing_fks:
                                print(f"SKIPPING {table} row {obj_id}: Missing required FK fields: {missing_fks}")
                                continue

                            # Special handling for users: Reconcile by email if ID doesn't match
                            if table == 'users' and 'email' in cleaned_data:
                                email = cleaned_data.get('email')
                                existing_user = User.objects.filter(email=email).first()
                                if existing_user:
                                    print(f"DEBUG: Found existing user by email: {email}. Updating record (protecting password)...")
                                    # Protect existing password if the incoming one is the placeholder
                                    incoming_password = cleaned_data.get('password')
                                    from django.contrib.auth.hashers import check_password
                                    
                                    is_placeholder = False
                                    if incoming_password:
                                        try:
                                            # If incoming matches placeholder, it's definitely a placeholder
                                            is_placeholder = check_password('ChangeMe123!', incoming_password)
                                        except: pass

                                    for key, value in cleaned_data.items():
                                        if key == 'password' and is_placeholder:
                                            continue # Keep existing password
                                        setattr(existing_user, key, value)
                                    existing_user.save()
                                    obj, created = existing_user, False
                                else:
                                    obj, created = model.objects.update_or_create(id=obj_id, defaults=cleaned_data)
                            else:
                                obj, created = model.objects.update_or_create(id=obj_id, defaults=cleaned_data)
                            
                            print(f"SAVED {table} {obj_id}: Created={created}, is_deleted={getattr(obj, 'is_deleted', 'N/A')}")
                            synced_ids[table].append(obj_id)
                        except Exception as row_error:
                            print(f"SKIPPING {table} row {obj_id} due to error: {str(row_error)}")
                            print(f"Row Data: {cleaned_data}")
                            # Skip this row (don't abort the whole sync for bad seed data)
                            continue
                    
                for table in ORDER:
                    if table not in payload: continue
                    
                    # If we reach here, we processed rows. We should mark them as synced in the response even if one table failed?
                    # No, transaction.atomic() handles the rollback.

            return Response({
                "status": "success",
                "synced_ids": synced_ids
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = str(e)
            print(f"SYNC ERROR: {error_msg}")
            # If it's a migration error, let the user know
            if "no such table" in error_msg.lower():
                error_msg = f"Database out of sync: {error_msg}. Please run migrations on the server."
            
            return Response({
                "status": "error",
                "message": error_msg
            }, status=status.HTTP_400_BAD_REQUEST)

    def get_model(self, table_name):
        model_mapping = {
            'stores': Store,
            'users': User,
            'accounts': Account,
            'expense_categories': ExpenseCategory,
            'tax_slabs': TaxSlab,
            'products': Product,
            'customers': Customer,
            'sales': Sale,
            'quotations': Quotation,
            'purchases': Purchase,
            'purchase_orders': PurchaseOrder,
            'stock_transfers': StockTransfer,
            'stock_logs': StockLog,
            'transactions': Transaction,
            'loyalty_points': LoyaltyPoint,
            'commissions': Commission,
            'suppliers': Supplier,
            'supplier_custom_fields': SupplierCustomField,
            'supplier_custom_values': SupplierCustomFieldValue,
            'supplier_transactions': SupplierTransaction,
            'payment_terms': PaymentTerm,
            'supplier_documents': SupplierDocument,
            'receivings': Receiving,
            'receiving_items': ReceivingItem,
            'invoices': Invoice,
            'invoice_items': InvoiceItem,
            'gift_cards': GiftCard,
            'sale_payments': SalePayment,
            'work_orders': WorkOrder,
            'deliveries': Delivery,
            'delivery_zones': DeliveryZone,
            'attendance': Attendance,
            'leaves': Leave,
            'employees': Employee,
            'payroll': Payroll,
            'performance_reviews': PerformanceReview,
            'cheques': Cheque,
            'categories': Category,
        }

        return model_mapping.get(table_name)

class PullEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            store_id = data.get('store_id')
            last_sync = data.get('last_sync') # ISO timestamp string

            if not store_id:
                return Response({"status": "error", "message": "store_id is required"}, status=status.HTTP_400_BAD_REQUEST)

             # Order for pulling usually doesn't matter as much, but we'll follow same order
            ORDER = [
                'stores', 
                'users', 
                'accounts', 
                'categories',
                'expense_categories',
                'tax_slabs',
                'customers', 
                'payment_terms',
                'suppliers',
                'supplier_custom_fields',
                'supplier_custom_values',
                'products', 
                'quotations',
                'sales', 
                'purchases',
                'supplier_transactions',
                'supplier_documents', 
                'transactions', 
                'stock_logs',
                'receivings',
                'receiving_items',
                'gift_cards',
                'sale_payments',
                'work_orders',
                'deliveries',
                'delivery_zones',
                'invoices',
                'invoice_items',
                'cheques',
                'attendance',
                'leaves',
                'employees',
                'payroll',
                'performance_reviews',
            ]

            updates = {}
            
            # We can use the mapping from a helper or just define it here to be cleaner
            model_mapping = {
                'stores': Store,
                'users': User,
                'accounts': Account,
                'expense_categories': ExpenseCategory,
                'tax_slabs': TaxSlab,
                'products': Product,
                'customers': Customer,
                'sales': Sale,
                'quotations': Quotation,
                'purchases': Purchase,
                'purchase_orders': PurchaseOrder,
                'stock_transfers': StockTransfer,
                'stock_logs': StockLog,
                'transactions': Transaction,
                'loyalty_points': LoyaltyPoint,
                'commissions': Commission,
                'suppliers': Supplier,
                'supplier_custom_fields': SupplierCustomField,
                'supplier_custom_values': SupplierCustomFieldValue,
                'supplier_transactions': SupplierTransaction,
                'payment_terms': PaymentTerm,
                'supplier_documents': SupplierDocument,
                'gift_cards': GiftCard,
                'sale_payments': SalePayment,
                'work_orders': WorkOrder,
                'deliveries': Delivery,
                'delivery_zones': DeliveryZone,
                'invoice_items': InvoiceItem,
                'invoices': Invoice,
                'receivings': Receiving,
                'receiving_items': ReceivingItem,
                'attendance': Attendance,
                'leaves': Leave,
                'employees': Employee,
                'cheques': Cheque,
                'categories': Category,
            }


            for table in ORDER:
                print(f"[SYNC] Pulling table: {table}")
                model = model_mapping.get(table)
                if not model:
                    continue
                
                # 1. Class-based overrides (Most reliable)
                if model == Store: 
                     queryset = model.objects.all() # Fetch ALL stores so manager's store appears
                elif model == User:
                     queryset = model.objects.all() # Fetch ALL users for cross-store staff/admins
                elif model == SalePayment:
                     queryset = model.objects.filter(sale__store_id=store_id)
                elif model == SupplierCustomFieldValue:
                     queryset = model.objects.filter(supplier__store_id=store_id)
                elif model in [LoyaltyPoint, Commission]:
                     queryset = model.objects.filter(sale__store_id=store_id)
                elif model in [WorkOrder, Delivery]:
                     queryset = model.objects.filter(sale__store_id=store_id)
                elif model in [ReceivingItem]:
                     queryset = model.objects.filter(receiving__store_id=store_id)
                elif model in [InvoiceItem]:
                     queryset = model.objects.filter(invoice__store_id=store_id)
                elif model in [ExpenseCategory, TaxSlab]:
                     queryset = model.objects.all()
                
                # 2. Field-based filtering
                elif 'store' in [f.name for f in model._meta.fields] or 'store_id' in [getattr(f, 'attname', None) for f in model._meta.fields]:
                     queryset = model.objects.filter(store_id=store_id)
                
                # 3. Fallback
                else:
                     queryset = model.objects.all()

                if last_sync and model not in [Store, User, ExpenseCategory, TaxSlab]:
                    # Generic filter field is updated_at, but some tables might use created_at or uploaded_at
                    if table in ['stock_logs', 'loyalty_points', 'commissions', 'supplier_transactions', 'cheques']:
                        filter_field = 'created_at'
                    elif table == 'supplier_documents':
                        filter_field = 'uploaded_at'
                    else:
                        filter_field = 'updated_at'
                        
                    queryset = queryset.filter(**{f"{filter_field}__gt": last_sync})
                
                try:
                    rows = []
                    for obj in queryset:
                        row_data = {}
                        for field in obj._meta.fields:
                            if field.name in [
                                'password', 'is_superuser', 'is_staff', 'is_active', 
                                'date_joined', 'groups', 'user_permissions', 'last_login', 
                                'username', 'first_name', 'last_name'
                            ]:
                                continue
                            
                            val = getattr(obj, field.name)
                            
                            # Determine key_name (Local SQLite expects 'field_id' for Foreign Keys)
                            key_name = field.name
                            if field.is_relation and not key_name.endswith('_id'):
                                key_name = f"{key_name}_id"

                            if isinstance(val, (datetime, date)):
                                row_data[key_name] = val.isoformat()
                            elif isinstance(val, bool):
                                row_data[key_name] = 1 if val else 0
                            elif field.is_relation and val:
                                row_data[key_name] = str(val.pk) if hasattr(val, 'pk') else str(val)
                            elif val is not None:
                                if isinstance(val, (int, float)):
                                    row_data[key_name] = val
                                else:
                                    row_data[key_name] = str(val)
                            else:
                                row_data[key_name] = None
                        
                        # SPECIAL HANDLING FOR ACCOUNTS & PAYMENT TYPES
                        if table in ['accounts', 'sales', 'purchases', 'transactions']:
                            if row_data.get('type') not in ['cash', 'card', 'wallet']:
                                row_data['type'] = 'card'
                        
                        # SPECIAL HANDLING FOR SALES
                        if table == 'sales':
                            if row_data.get('type') not in ['retail', 'cash', 'credit']:
                                 row_data['type'] = 'cash'
                            if row_data.get('payment_mode') not in ['cash', 'card', 'wallet']:
                                 row_data['payment_mode'] = 'card'
                        
                        # SPECIAL HANDLING FOR PURCHASES
                        if table == 'purchases':
                            if row_data.get('type') not in ['cash', 'credit']:
                                 row_data['type'] = 'cash'

                        # SPECIAL HANDLING FOR USERS
                        if table == 'users' and isinstance(obj, User):
                            row_data['name'] = f"{obj.first_name} {obj.last_name}".strip()
                            if not row_data['name']:
                                 row_data['name'] = obj.username
                            if row_data.get('role') == 'staff':
                                row_data['role'] = 'user'

                        rows.append(row_data)
                    
                    if rows:
                        updates[table] = rows
                except Exception as table_err:
                    print(f"[PULL] SKIPPING table '{table}': {str(table_err)}")
                    # Don't abort the whole sync — skip this table and continue
                    continue

            return Response({
                "status": "success",
                "updates": updates,
                "server_time": datetime.now().isoformat()
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = str(e)
            if 'table' in locals():
                error_msg = f"Error in table {table}: {error_msg}"
            return Response({
                "status": "error",
                "message": error_msg
            }, status=status.HTTP_400_BAD_REQUEST)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer

class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer

class PerformanceReviewViewSet(viewsets.ModelViewSet):
    queryset = PerformanceReview.objects.all()
    serializer_class = PerformanceReviewSerializer

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class SupplierCustomFieldViewSet(viewsets.ModelViewSet):
    queryset = SupplierCustomField.objects.all()
    serializer_class = SupplierCustomFieldSerializer

class SupplierCustomFieldValueViewSet(viewsets.ModelViewSet):
    queryset = SupplierCustomFieldValue.objects.all()
    serializer_class = SupplierCustomFieldValueSerializer

class SupplierTransactionViewSet(viewsets.ModelViewSet):
    queryset = SupplierTransaction.objects.all()
    serializer_class = SupplierTransactionSerializer

class PaymentTermViewSet(viewsets.ModelViewSet):
    queryset = PaymentTerm.objects.all()
    serializer_class = PaymentTermSerializer

class SupplierDocumentViewSet(viewsets.ModelViewSet):
    queryset = SupplierDocument.objects.all()
    serializer_class = SupplierDocumentSerializer


# ──────────────────────────────────────────────────────────────
# RECEIVING VIEWSETS
# ──────────────────────────────────────────────────────────────

from rest_framework.decorators import action
from django.utils import timezone
from decimal import Decimal

class ReceivingViewSet(viewsets.ModelViewSet):
    serializer_class = ReceivingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        store_id = self.request.query_params.get('store_id')
        qs = Receiving.objects.prefetch_related('items').select_related('supplier', 'account')
        if store_id:
            qs = qs.filter(store_id=store_id)
        return qs.order_by('-updated_at')

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Finalize a receiving: update inventory, create ledger entry, update PO."""
        receiving = self.get_object()
        if receiving.status == 'completed':
            return Response({'error': 'Already completed'}, status=400)

        amount_paid = Decimal(str(request.data.get('amount_paid', 0)))
        account_id  = request.data.get('account_id')

        try:
            with transaction.atomic():
                for item in receiving.items.all():
                    # 1. Increase product quantity
                    product = item.product
                    product.quantity += int(item.quantity)
                    # Update purchase price to latest cost
                    product.purchase_price = item.cost
                    product.save()

                    # 2. Create stock log
                    StockLog.objects.create(
                        product=product,
                        product_name=product.name,
                        store=receiving.store,
                        quantity_change=item.quantity,
                        reason='receiving',
                        reference_id=receiving.id,
                    )

                # 3. Create supplier transaction (purchase)
                SupplierTransaction.objects.create(
                    supplier=receiving.supplier,
                    type='purchase',
                    amount=receiving.total_amount,
                    balance_after=receiving.supplier.current_balance + receiving.total_amount,
                    date=timezone.now(),
                    reference_id=receiving.receiving_number,
                    description=f'Receiving #{receiving.receiving_number}',
                    store=receiving.store,
                )

                # 4. Update supplier balance
                receiving.supplier.current_balance += receiving.total_amount
                receiving.supplier.save()

                # 5. Update PO status if linked and fully received
                if receiving.purchase_order:
                    po = receiving.purchase_order
                    if not po.receivings.filter(status__in=['draft', 'suspended']).exists():
                        po.status = 'received'
                        po.save()

                # 6. Mark receiving as completed
                receiving.amount_paid = amount_paid
                receiving.amount_due = receiving.total_amount - amount_paid
                receiving.status = 'completed'
                receiving.completed_at = timezone.now()
                if account_id:
                    receiving.account_id = account_id
                receiving.save()

            return Response(ReceivingSerializer(receiving).data)

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Save receiving as suspended — inventory NOT updated yet."""
        receiving = self.get_object()
        receiving.status = 'suspended'
        receiving.save()
        return Response(ReceivingSerializer(receiving).data)

    @action(detail=True, methods=['post'])
    def add_payment(self, request, pk=None):
        """Record a partial payment against a completed/suspended receiving."""
        receiving = self.get_object()
        amount = Decimal(str(request.data.get('amount', 0)))
        account_id = request.data.get('account_id')

        if amount <= 0:
            return Response({'error': 'Invalid amount'}, status=400)

        with transaction.atomic():
            # Create supplier payment transaction
            SupplierTransaction.objects.create(
                supplier=receiving.supplier,
                type='payment',
                amount=amount,
                balance_after=receiving.supplier.current_balance - amount,
                date=timezone.now(),
                reference_id=receiving.receiving_number,
                description=f'Payment for #{receiving.receiving_number}',
                store=receiving.store,
            )
            receiving.supplier.current_balance -= amount
            receiving.supplier.save()

            receiving.amount_paid += amount
            receiving.amount_due = max(receiving.total_amount - receiving.amount_paid, Decimal('0'))
            if account_id:
                receiving.account_id = account_id
            receiving.save()

        return Response(ReceivingSerializer(receiving).data)


class ReceivingItemViewSet(viewsets.ModelViewSet):
    serializer_class = ReceivingItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        receiving_id = self.request.query_params.get('receiving_id')
        qs = ReceivingItem.objects.all()
        if receiving_id:
            qs = qs.filter(receiving_id=receiving_id)
        return qs

class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        store_id = self.request.query_params.get('store_id')
        qs = Invoice.objects.prefetch_related('invoice_items').select_related('customer', 'supplier')
        if store_id:
            qs = qs.filter(store_id=store_id)
        return qs.order_by('-date')

class InvoiceItemViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        invoice_id = self.request.query_params.get('invoice_id')
        qs = InvoiceItem.objects.all()
        if invoice_id:
            qs = qs.filter(invoice_id=invoice_id)
        return qs



class ChequeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChequeSerializer

    def get_queryset(self):
        store_id = self.request.query_params.get('store_id')
        if store_id:
            return Cheque.objects.filter(store_id=store_id)
        return Cheque.objects.all()

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny] # Allow website to fetch products

    def get_queryset(self):
        from django.db.models import Q
        # Filter is_deleted=False but also handle NULLs just in case repair_db hasn't run
        qs = Product.objects.filter(Q(is_deleted=False) | Q(is_deleted__isnull=True)).select_related('category', 'store').prefetch_related('images', 'features')
        
        store_id = self.request.query_params.get('store_id')
        sku = self.request.query_params.get('sku')
        category_slug = self.request.query_params.get('category__slug')
        search = self.request.query_params.get('search')
        
        if store_id:
            qs = qs.filter(store_id=store_id)
        if sku:
            if sku.startswith('prod-'):
                qs = qs.filter(id=sku.replace('prod-', ''))
            else:
                qs = qs.filter(sku=sku)
        if category_slug:
            qs = qs.filter(Q(category__name__iexact=category_slug.replace('-', ' ')) | Q(category__id=category_slug))
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(sku__icontains=search) | Q(description__icontains=search) | Q(brand__icontains=search))
            
        return qs.order_by('-updated_at')

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        store_id = self.request.query_params.get('store_id')
        
        if not user.is_authenticated:
            return Sale.objects.none()

        # Super Admins and Admins can see everything
        if user.role in ['super_admin', 'admin'] or user.is_staff:
            qs = Sale.objects.all()
        # Managers etc see their store's sales
        elif user.role in ['hr_manager', 'sales_manager', 'inventory_manager', 'accountant'] and user.store:
            qs = Sale.objects.filter(store=user.store)
        # Regular users (Web Customers) see only their own orders by email
        else:
            qs = Sale.objects.filter(customer__email=user.email)
            
        if store_id:
            qs = qs.filter(store_id=store_id)
            
        return qs.order_by('-date')

    def perform_create(self, serializer):
        # Automated inventory deduction logic for direct API sales (Web Orders)
        with transaction.atomic():
            sale = serializer.save()
            
            # Parse items from the TextField (JSON string)
            import json
            try:
                items = json.loads(sale.items) if isinstance(sale.items, str) else sale.items
                if isinstance(items, list):
                    for item in items:
                        product_id = item.get('productId') or item.get('product_id') or item.get('id')
                        qty = int(float(item.get('quantity', 0)))
                        print(f"DEBUG: Stock deduction for {item.get('id')}, qty={qty}")
                        if product_id and qty > 0:
                            product = Product.objects.filter(id=product_id).first()
                            if product:
                                product.quantity -= qty
                                product.save()
                                
                                # Log stock change
                                StockLog.objects.create(
                                    product=product,
                                    product_name=product.name,
                                    store=sale.store,
                                    quantity_change=-qty,
                                    reason='sale',
                                    reference_id=sale.id
                                )
            except Exception as e:
                print(f"ERROR: Failed to deduct stock for sale {sale.id}: {str(e)}")

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_razorpay_order(self, request):
        amount_val = request.data.get('amount', 0)
        try:
            # Convert to float then to paise (integer)
            amount = int(float(amount_val) * 100)
        except (TypeError, ValueError):
            amount = 0

        # Note: We are NOT generating a server-side order_id here 
        # because the 'razorpay' python package is not installed.
        # Removing order_id from response allows standard checkout.
        
        from django.conf import settings
        return Response({
            "amount": amount,
            "key_id": settings.RAZORPAY_KEY_ID,
            "currency": "INR",
            "description": "Elegance Store Order",
            "user_name": request.user.get_full_name() if request.user.is_authenticated else "Guest",
            "user_email": request.user.email if request.user.is_authenticated else "guest@example.com",
            "user_contact": ""
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def verify_payment(self, request):
        """Verify Razorpay payment and create Sale record in ERP."""
        print("\n=== VERIFY PAYMENT START ===")
        print(f"User: {request.user.email}")
        try:
            data = request.data
            print(f"Payload: {json.dumps(data, indent=2)}")
            
            order_id = data.get('razorpay_order_id')
            payment_id = data.get('razorpay_payment_id')
            signature = data.get('razorpay_signature')
            shipping_address = data.get('shipping_address', {})
            cart_items = data.get('cart_items', [])
            amount_input = data.get('amount', 0)
            print(f"DEBUG: amount_input='{amount_input}' (type: {type(amount_input)})")
            
            # 1. Basic Validation
            if not cart_items:
                print("[ERROR] Cart items missing")
                return Response({"error": "Cart items missing"}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Create Sale in ERP
            with transaction.atomic():
                print("Transaction started...")
                # 3. Check if OnlineOrder already exists (Prevent duplicate creation on retries)
                if order_id and OnlineOrder.objects.filter(order_id=order_id).exists():
                    print(f"[INFO] Order {order_id} already exists. Returning success.")
                    oo = OnlineOrder.objects.get(order_id=order_id)
                    return Response({
                        "status": "success",
                        "sale_id": oo.sale.id if oo.sale else None,
                        "invoice_number": oo.sale.invoice_number if oo.sale else None,
                        "message": "Order already processed"
                    }, status=status.HTTP_200_OK)

                # Find or Create Customer
                cust_email = shipping_address.get('email') or request.user.email
                customer = Customer.objects.filter(email=cust_email).first()
                print(f"Customer Found: {customer.id if customer else 'None'}")
                
                # Fetch or Create fallback Store/Account
                # Intelligent Store Selection for Logistics
                first_store = Store.objects.filter(name__icontains='Main').first() or Store.objects.first()
                if not first_store:
                    print("Creating fallback store...")
                    first_store = Store.objects.create(name="Hardware Central [Main Branch]", branch="Main")
                
                first_account = Account.objects.first()
                if not first_account:
                    print("Creating fallback account...")
                    first_account = Account.objects.create(
                        name="Main Cash", 
                        type='cash', 
                        balance=0,
                        store=first_store
                    )
                
                if not customer:
                    print(f"Creating new customer for {cust_email}...")
                    customer = Customer.objects.create(
                        name=shipping_address.get('name', getattr(request.user, 'full_name', 'Web Customer')),
                        email=cust_email,
                        phone=shipping_address.get('phone', ''),
                        store=first_store,
                        source='Online'
                    )
                
                # Calculate Profit on Backend for accuracy
                total_profit = Decimal('0.00')
                for item in cart_items:
                    p_id = item.get('id')
                    try:
                        p_obj = Product.objects.filter(id=p_id).first()
                        if p_obj:
                            item_price = Decimal(str(item.get('price', 0)))
                            item_cost = p_obj.purchase_price or Decimal('0.00')
                            item_qty = Decimal(str(item.get('quantity', 1)))
                            total_profit += (item_price - item_cost) * item_qty
                    except:
                        pass

                # Create Sale Record
                print("Creating Sale record...")
                sale = Sale.objects.create(
                    invoice_number=f"WEB-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                    status='completed',
                    type='retail',
                    source='Online',
                    items=json.dumps(cart_items),
                    subtotal=amount_input,
                    total_amount=amount_input,
                    profit=total_profit,
                    payment_mode='card',
                    account=first_account,
                    customer=customer,
                    store=first_store,
                    date=timezone.now()
                )
                print(f"Sale created: {sale.id}")
                
                # Create SalePayment Record
                SalePayment.objects.create(
                    sale=sale,
                    payment_mode='card',
                    amount=amount_input,
                    account=first_account
                )

                # Create OnlineOrder record
                print("Creating OnlineOrder record...")
                oo = OnlineOrder.objects.create(
                    user_email=cust_email,
                    order_id=order_id or f"WEB-{sale.id}",
                    payment_id=payment_id,
                    amount=amount_input,
                    sale=sale,
                    status='Processing',
                    full_name=shipping_address.get('name', getattr(request.user, 'full_name', 'Web Customer')),
                    phone=shipping_address.get('phone', ''),
                    address=shipping_address.get('address', shipping_address.get('address_line1', '')),
                    city=shipping_address.get('city', ''),
                    state=shipping_address.get('state', ''),
                    pincode=shipping_address.get('pincode', '')
                )
                
                # Create Delivery record for Logistics module
                print("Creating Delivery record...")
                Delivery.objects.create(
                    sale=sale,
                    address=f"{oo.address}, {oo.city}, {oo.state} - {oo.pincode}",
                    is_cod=False,
                    status='pending',
                    store=first_store,
                    notes=f"Online Order ID: {oo.order_id}"
                )
                
                # Create OnlineOrderItems with robust name selection
                print("Creating OnlineOrderItems...")
                for item in cart_items:
                    raw_qty = item.get('quantity', 1)
                    parsed_qty = int(float(raw_qty))
                    # Use provided names to avoid "Unknown Product" - checking camelCase productName too
                    p_name = item.get('productName') or item.get('product_name') or item.get('project_title') or item.get('name') or item.get('title', 'Unknown Product')
                    print(f"DEBUG: item={item.get('id')}, name={p_name}, qty={parsed_qty}")
                    OnlineOrderItem.objects.create(
                        order=oo,
                        product_id=item.get('id'),
                        product_name=p_name,
                        price=Decimal(str(item.get('price', 0))),
                        quantity=parsed_qty
                    )
                
                # Deduct Stock
                print("Updating stock...")
                for item in cart_items:
                    product_id = item.get('id')
                    raw_qty_stock = item.get('quantity', 0)
                    qty = int(float(raw_qty_stock))
                    print(f"DEBUG: stock deduc item={product_id}, raw_qty='{raw_qty_stock}', parsed_qty={qty}")
                    if product_id and qty > 0:
                        product = Product.objects.filter(id=product_id).first()
                        if product:
                            product.quantity -= qty
                            product.save()
                            
                            StockLog.objects.create(
                                product=product,
                                product_name=product.name,
                                store=sale.store,
                                quantity_change=-qty,
                                reason='sale',
                                reference_id=sale.id
                            )
                
            print(f"=== VERIFY PAYMENT SUCCESS: {sale.invoice_number} ===")
            return Response({
                "status": "success",
                "sale_id": sale.id,
                "invoice_number": sale.invoice_number
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = f"Verification failed: {str(e)}"
            print(f"=== VERIFY PAYMENT ERROR: {error_msg} ===")
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = f"Verification failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    from .serializers import UserProfileSerializer
    if request.method == 'PUT':
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.is_active = False # Deactivate until verified
        user.save()
        
        # Email Verification Logic
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # The frontend URL for verification
        verify_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}"
        
        subject = "Verify your Elegance account"
        message = f"Hi {user.first_name or user.username},\n\nPlease verify your email by clicking the link below:\n\n{verify_url}\n\nIf you did not register, please ignore this email."
        
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            print(f"Verification email sent to {user.email}")
        except Exception as e:
            print(f"Failed to send verification email: {e}")
        
        # Create a Customer record for this new user so they appear in the ERP
        from .models import Customer, Store
        customer_created = False
        try:
            store = Store.objects.first()
            if store:
                # Map Elegance data to ERP Customer
                from django.utils import timezone
                Customer.objects.create(
                    name=request.data.get('full_name') or user.get_full_name() or user.username,
                    email=user.email,
                    phone=request.data.get('phone', ''),
                    type='retail',
                    status='active',
                    source='Online',
                    store=store,
                    joined_at=timezone.now()
                )
                customer_created = True
        except Exception as e:
            print(f"Failed to create Customer record for new user: {e}")

        return Response({
            "status": "success",
            "customer_created": customer_created,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, uidb64, token):
    if not uidb64 or not token:
        return Response({"error": "UID and token are required"}, status=400)
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.is_verified = True
        user.save()
        return Response({"status": "success", "message": "Email verified successfully"})
    else:
        return Response({"error": "Invalid verification link"}, status=400)

from .models import Review, Feedback
from .serializers import ReviewSerializer, FeedbackSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny] # Allow reading reviews publicly, creating publicly?
    # TODO: May want to restrict creating to authenticated or specific conditions

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().order_by('-created_at')
    serializer_class = FeedbackSerializer
    permission_classes = [AllowAny] # Allow website visitors to submit feedback

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def _get_cart(self, request):
        session_key = request.headers.get('X-Cart-Session') or request.headers.get('x-cart-session')
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            return cart
        if session_key:
            cart, _ = Cart.objects.get_or_create(session_key=session_key)
            return cart
        return None

    def list(self, request):
        cart = self._get_cart(request)
        if not cart:
            return Response({"items": [], "total_price": 0})
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def add(self, request):
        cart = self._get_cart(request)
        if not cart:
            return Response({"error": "No session provided"}, status=400)
            
        # Support both 'product_id' (internal) and 'project_id' (Elegance frontend name)
        product_id = request.data.get('product_id') or request.data.get('project_id')
        try:
            qty_val = request.data.get('quantity', 1)
            if qty_val == "" or qty_val is None: qty_val = 1
            quantity = Decimal(str(qty_val))
        except (ValueError, TypeError, decimal.InvalidOperation):
            quantity = Decimal('1')
            
        if not product_id:
            return Response({"error": "Product ID is required"}, status=400)
            
        # Try to find product by ID, then by SKU (as the frontend often uses SKU as ID)
        product = Product.objects.filter(id=product_id).first()
        if not product:
            product = Product.objects.filter(sku=product_id).first()
            
        if not product:
            return Response({"error": f"Product not found with ID or SKU: {product_id}"}, status=404)
            
        item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            defaults={'price_at_time': product.selling_price or 0, 'quantity': 0}
        )
        item.quantity += quantity
        item.price_at_time = product.selling_price or 0 # Update to current price
        item.save()
        
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['POST'])
    def remove_item(self, request):
        cart = self._get_cart(request)
        if not cart: return Response(status=400)
        
        product_id = request.data.get('product_id')
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['POST'])
    def clear(self, request):
        cart = self._get_cart(request)
        if cart:
            cart.items.all().delete()
        return Response({"status": "cleared"})

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [AllowAny]

    def _get_cart(self, request):
        session_id = request.headers.get('X-Cart-Session') or request.headers.get('x-cart-session')
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            return cart
        if session_id:
            cart, _ = Cart.objects.get_or_create(session_key=session_id)
            return cart
        return None

    def get_queryset(self):
        user = self.request.user
        session_id = self.request.headers.get('X-Cart-Session') or self.request.headers.get('x-cart-session')
        
        q_filter = Q()
        if user.is_authenticated:
            q_filter |= Q(cart__user=user)
        if session_id:
            q_filter |= Q(cart__session_key=session_id)
            
        if not (user.is_authenticated or session_id):
            return CartItem.objects.none()
            
        return CartItem.objects.filter(q_filter).distinct()

    def perform_create(self, serializer):
        cart = self._get_cart(self.request)
        if not cart:
            raise serializers.ValidationError("No cart session found")
        
        # Ensure price_at_time is set from the product
        product_id = self.request.data.get('product_id')
        if not product_id:
             raise serializers.ValidationError({"product_id": "This field is required for item creation."})
             
        product = get_object_or_404(Product, id=product_id)
        serializer.save(cart=cart, product=product, price_at_time=product.selling_price or 0)

    def perform_update(self, serializer):
        # Prevent 400 errors during quantity updates if product_id is missing
        instance = self.get_object()
        product_id = self.request.data.get('product_id')
        
        if product_id:
            product = get_object_or_404(Product, id=product_id)
            serializer.save(product=product)
        else:
            # If no product_id provided, just save with existing product to avoid validation issues
            serializer.save(product=instance.product)

class OnlineOrderViewSet(viewsets.ModelViewSet):
    serializer_class = OnlineOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role in ['admin', 'super_admin']:
            return OnlineOrder.objects.all().order_by('-created_at')
        return OnlineOrder.objects.filter(user_email=user.email).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        status_val = request.data.get('status')
        if status_val:
            order.status = status_val
            order.save()
            return Response({'status': 'updated'})
        return Response({'error': 'status required'}, status=400)

    @action(detail=True, methods=['post'])
    def add_tracking(self, request, pk=None):
        order = self.get_object()
        order.courier_name = request.data.get('courier_name', order.courier_name)
        order.tracking_number = request.data.get('tracking_number', order.tracking_number)
        order.shipping_method = request.data.get('shipping_method', order.shipping_method)
        if request.data.get('estimated_delivery_date'):
            order.estimated_delivery_date = request.data.get('estimated_delivery_date')
        order.status = 'Shipped'
        order.save()
        return Response({'status': 'tracking added'})

class OnlineReturnViewSet(viewsets.ModelViewSet):
    queryset = OnlineReturn.objects.all()
    serializer_class = OnlineReturnSerializer
    permission_classes = [IsAuthenticated]

class OnlineReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        # Revenue and Top Selling Products (Online only)
        total_revenue = OnlineOrder.objects.filter(status='Delivered').aggregate(total=Sum('amount'))['total'] or 0
        total_orders = OnlineOrder.objects.count()
        
        top_products = OnlineOrderItem.objects.values('product_name')\
            .annotate(total_qty=Sum('quantity'))\
            .order_by('-total_qty')[:5]
            
        return Response({
            'revenue': total_revenue,
            'orders': total_orders,
            'top_products': top_products
        })

class SaleReturnViewSet(viewsets.ModelViewSet):
    queryset = SaleReturn.objects.all().order_by('-created_at')
    serializer_class = SaleReturnSerializer
    permission_classes = [IsAuthenticated]

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(Q(user=self.request.user) | Q(user=None)).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'read'})

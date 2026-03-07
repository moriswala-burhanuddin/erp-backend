from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, date
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
    Invoice, InvoiceItem, Cheque, Category
)


from .serializers import (
    EmployeeSerializer, AttendanceSerializer, LeaveSerializer, 
    PayrollSerializer, PerformanceReviewSerializer,
    SupplierSerializer, SupplierCustomFieldSerializer, 
    SupplierCustomFieldValueSerializer, SupplierTransactionSerializer,
    PaymentTermSerializer, SupplierDocumentSerializer,
    ReceivingSerializer, ReceivingItemSerializer,
    InvoiceSerializer, InvoiceItemSerializer, ChequeSerializer,
    ProductSerializer, CustomerSerializer, SaleSerializer,
    UserRegistrationSerializer, CategorySerializer
)


from rest_framework import viewsets

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

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
    tables = connection.introspection.table_names()
    return Response({
        "tables": tables,
        "has_receiving": "api_receiving" in tables,
        "has_receivingitem": "api_receivingitem" in tables,
    })

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
                            elif not row_data['password'].startswith(('pbkdf2_', 'bcrypt', 'argon2')):
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
                                    print(f"DEBUG: Found existing user by email: {email}. Updating record with id={obj_id}")
                                    for key, value in cleaned_data.items():
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
        qs = Product.objects.filter(is_deleted=False).select_related('category', 'store').prefetch_related('images', 'features')
        
        store_id = self.request.query_params.get('store_id')
        sku = self.request.query_params.get('sku')
        category_slug = self.request.query_params.get('category__slug')
        search = self.request.query_params.get('search')
        
        if store_id:
            qs = qs.filter(store_id=store_id)
        if sku:
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
        store_id = self.request.query_params.get('store_id')
        if store_id:
            return Sale.objects.filter(store_id=store_id)
        return Sale.objects.all()

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
                        qty = int(item.get('quantity', 0))
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
        amount = request.data.get('amount', 0)
        # Note: integration with razorpay package
        # Since we might not have razorpay installed in the ERP backend, 
        # we generate a stub or mockup for now that the frontend expects.
        import time
        order_id = f"order_{int(time.time())}"
        
        return Response({
            "order_id": order_id,
            "amount": amount,
            "key_id": "rzp_test_stub_key",
            "currency": "INR",
            "description": "Elegance Store Order",
            "user_name": request.user.first_name,
            "user_email": request.user.email,
            "user_contact": ""
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def verify_payment(self, request):
        """Verify Razorpay payment and create Sale record in ERP."""
        try:
            data = request.data
            order_id = data.get('razorpay_order_id')
            payment_id = data.get('razorpay_payment_id')
            signature = data.get('razorpay_signature')
            shipping_address = data.get('shipping_address', {})
            cart_items = data.get('cart_items', [])
            
            # 1. Verify Signature (simplified if key is missing)
            # In a real environment, you'd use settings.RAZORPAY_KEY_SECRET
            
            # 2. Create Sale in ERP
            with transaction.atomic():
                # Find or Create Customer
                cust_email = shipping_address.get('email')
                customer = Customer.objects.filter(email=cust_email).first() if cust_email else None
                if not customer:
                    customer = Customer.objects.create(
                        name=shipping_address.get('name', 'Web Customer'),
                        email=cust_email,
                        phone=shipping_address.get('phone', ''),
                        store_id=data.get('store_id', Store.objects.first().id)
                    )
                
                # Create Sale Record
                sale = Sale.objects.create(
                    invoice_number=f"WEB-{timezone.now().strftime('%Y%m%d%04d')}",
                    status='completed',
                    type='retail',
                    source='Online',
                    items=json.dumps(cart_items),
                    total_amount=data.get('amount', 0),
                    profit=data.get('profit', 0),
                    payment_mode='card',
                    account_id=data.get('account_id', Account.objects.first().id),
                    customer=customer,
                    store_id=data.get('store_id', Store.objects.first().id),
                    date=timezone.now()
                )
                
                for item in cart_items:
                    product_id = item.get('id')
                    qty = int(item.get('quantity', 0))
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

            return Response({
                "status": "success",
                "sale_id": sale.id,
                "invoice_number": sale.invoice_number
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    from .serializers import UserProfileSerializer
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Create a Customer record for this new user so they appear in the ERP
        from .models import Customer, Store
        try:
            store = Store.objects.first()
            if store:
                # Map Elegance data to ERP Customer
                Customer.objects.create(
                    name=request.data.get('full_name') or user.get_full_name() or user.username,
                    email=user.email,
                    phone=request.data.get('phone', ''),
                    type='retail',
                    status='active',
                    source='Online',
                    store=store
                )
        except Exception as e:
            print(f"Failed to create Customer record for new user: {e}")

        return Response({
            "status": "success",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            return cart
        else:
            session_key = request.headers.get('x-cart-session')
            if not session_key:
                return None
            cart, _ = Cart.objects.get_or_create(session_key=session_key)
            return cart

    def list(self, request):
        cart = self._get_cart(request)
        if not cart:
            return Response({"items": [], "total_price": 0})
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def add_item(self, request):
        cart = self._get_cart(request)
        if not cart:
            return Response({"error": "No session provided"}, status=400)
            
        product_id = request.data.get('product_id')
        quantity = Decimal(str(request.data.get('quantity', 1)))
        
        product = get_object_or_404(Product, id=product_id)
        
        item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            defaults={'price_at_time': product.selling_price, 'quantity': 0}
        )
        item.quantity += quantity
        item.price_at_time = product.selling_price # Update to current price
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

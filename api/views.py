from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, date
from django.db import transaction
from .models import (
    Store, Account, Product, Customer, Sale, Purchase, StockLog, User, 
    Quotation, Transaction, ExpenseCategory, TaxSlab, StockTransfer, 
    PurchaseOrder, LoyaltyPoint, Commission
)

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
            'expense_categories',
            'tax_slabs',
            'customers', 
            'products', 
            'quotations',
            'sales', 
            'purchases', 
            'purchase_orders',
            'stock_transfers',
            'transactions', 
            'stock_logs',
            'loyalty_points',
            'commissions'
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
                        # Prepare data for update_or_create
                        row_data = {k: v for k, v in row.items() if k != 'sync_status'}
                        
                        # COMPATIBILITY: Map 'user' back to 'staff' for Django
                        if table == 'users':
                            if row_data.get('role') == 'user':
                                row_data['role'] = 'staff'
                            if 'email' in row_data and not row_data.get('username'):
                                row_data['username'] = row_data['email']
                            
                            # Split name into first and last name
                            if 'name' in row_data:
                                name_parts = row_data['name'].split(' ', 1)
                                row_data['first_name'] = name_parts[0]
                                if len(name_parts) > 1:
                                    row_data['last_name'] = name_parts[1]
                                else:
                                    row_data['last_name'] = ''
                            
                            # Set default password for users created in Electron
                            # Django User model requires a password field
                            if 'password' not in row_data or not row_data.get('password'):
                                from django.contrib.auth.hashers import make_password
                                row_data['password'] = make_password('ChangeMe123!')
                        
                        # Filter out any fields that don't exist in the Django model
                        # Use _meta.fields to only get forward fields (avoiding reverse relation crashes)
                        valid_fields = {f.name for f in model._meta.fields}
                        # Also allow _id fields for ForeignKeys
                        valid_fields.update({f.attname for f in model._meta.fields})
                        
                        cleaned_data = {k: v for k, v in row_data.items() if k in valid_fields}
                        
                        if not cleaned_data:
                            print(f"SKIPPING {table} row {row.get('id')} - No valid fields! Row keys: {list(row.items())}")
                            continue
                        
                        # Debug: Print what we are about to save
                        # print(f"SAVING {table}: {cleaned_data.keys()}")

                        obj_id = cleaned_data.pop('id')
                        try:
                            obj, created = model.objects.update_or_create(
                                id=obj_id,
                                defaults=cleaned_data
                            )
                            print(f"SAVED {table} {obj_id}: Created={created}, is_deleted={getattr(obj, 'is_deleted', 'N/A')}")
                            synced_ids[table].append(obj_id)
                        except Exception as row_error:
                            print(f"FAILED TO SAVE {table} row {obj_id}: {str(row_error)}")
                            print(f"Row Data: {cleaned_data}")
                            raise row_error # Re-raise to trigger atomic rollback

            return Response({
                "status": "success",
                "synced_ids": synced_ids
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"SYNC ERROR: {str(e)}")
            return Response({
                "status": "error",
                "message": str(e)
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
            'commissions': Commission
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
                'customers', 
                'products', 
                'quotations',
                'sales', 
                'purchases', 
                'transactions', 
                'stock_logs'
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
                'commissions': Commission
            }

            for table in ORDER:
                model = model_mapping.get(table)
                if not model:
                    continue
                
                if table == 'stores': 
                     queryset = model.objects.filter(id=store_id)
                else:
                     queryset = model.objects.filter(store_id=store_id)

                if last_sync:
                    # Generic filter field is updated_at, but some tables might use created_at
                    filter_field = 'created_at' if table in ['stock_logs', 'loyalty_points', 'commissions'] else 'updated_at'
                    queryset = queryset.filter(**{f"{filter_field}__gt": last_sync})
                
                # Serialize
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
                            # SQLite doesn't have a native BOOLEAN, usually uses 0/1
                            row_data[key_name] = 1 if val else 0
                        elif field.is_relation and val:
                            # For JSON serialization, we just want the ID of the related object
                            row_data[key_name] = str(val.pk) if hasattr(val, 'pk') else str(val)
                        elif val is not None:
                            # Convert Decimals and other objects to strings to avoid binding errors
                            # but keep numbers as numbers if possible
                            if isinstance(val, (int, float)):
                                row_data[key_name] = val
                            else:
                                row_data[key_name] = str(val)
                        else:
                            row_data[key_name] = None
                    
                    # SPECIAL HANDLING FOR ACCOUNTS & PAYMENT TYPES
                    if table in ['accounts', 'sales', 'purchases', 'transactions']:
                        if row_data.get('type') not in ['cash', 'card', 'wallet']:
                            row_data['type'] = 'card' # Map bank/other to card for local DB
                    
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
                        # Construct 'name' from first_name + last_name
                        row_data['name'] = f"{obj.first_name} {obj.last_name}".strip()
                        if not row_data['name']:
                             row_data['name'] = obj.username # Fallback
                        
                        # COMPATIBILITY: Map 'staff' to 'user' for local DB constraint
                        if row_data.get('role') == 'staff':
                            row_data['role'] = 'user'

                    rows.append(row_data)
                
                if rows:
                    updates[table] = rows

            return Response({
                "status": "success",
                "updates": updates,
                "server_time": datetime.now().isoformat()
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"PULL ERROR: {str(e)}")
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

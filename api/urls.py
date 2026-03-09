from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    PushEndpoint, PullEndpoint, EmployeeViewSet, AttendanceViewSet, 
    LeaveViewSet, PayrollViewSet, PerformanceReviewViewSet, health_check, db_diagnostic,
    SupplierViewSet, SupplierCustomFieldViewSet, 
    SupplierCustomFieldValueViewSet, SupplierTransactionViewSet,
    PaymentTermViewSet, SupplierDocumentViewSet,
    ReceivingViewSet, ReceivingItemViewSet,
    InvoiceViewSet, InvoiceItemViewSet, ChequeViewSet,
    ProductViewSet, SaleViewSet, CustomerViewSet, register, CategoryViewSet,
    ReviewViewSet, FeedbackViewSet, CartViewSet, get_profile, CartItemViewSet,
    OnlineOrderViewSet
)

from .serializers import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'leaves', LeaveViewSet)
router.register(r'payroll', PayrollViewSet)
router.register(r'performance', PerformanceReviewViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'supplier-custom-fields', SupplierCustomFieldViewSet)
router.register(r'supplier-custom-values', SupplierCustomFieldValueViewSet)
router.register(r'supplier-transactions', SupplierTransactionViewSet)
router.register(r'payment-terms', PaymentTermViewSet)
router.register(r'supplier-documents', SupplierDocumentViewSet)
router.register(r'receivings', ReceivingViewSet, basename='receiving')
router.register(r'receiving-items', ReceivingItemViewSet, basename='receiving-item')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'invoice-items', InvoiceItemViewSet, basename='invoice-item')
router.register(r'cheques', ChequeViewSet, basename='cheque')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'orders', SaleViewSet, basename='order')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'online-orders', OnlineOrderViewSet, basename='online_order')
router.register(r'store/cart/items', CartItemViewSet, basename='cart-item')
router.register(r'store/cart', CartViewSet, basename='cart')


urlpatterns = [
    path('sync/push', PushEndpoint.as_view(), name='sync-push'),
    path('sync/pull', PullEndpoint.as_view(), name='sync-pull'),
    path('health', health_check, name='health'),
    path('db-diagnostic', db_diagnostic, name='db-diagnostic'),
    
    # Auth
    path('auth/login', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/register', register, name='register'),
    path('auth/profile/', get_profile, name='get_profile'),
    path('auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),
] + router.urls

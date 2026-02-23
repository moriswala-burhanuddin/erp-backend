from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    PushEndpoint, PullEndpoint, EmployeeViewSet, AttendanceViewSet, 
    LeaveViewSet, PayrollViewSet, PerformanceReviewViewSet, health_check,
    SupplierViewSet, SupplierCustomFieldViewSet, 
    SupplierCustomFieldValueViewSet, SupplierTransactionViewSet,
    PaymentTermViewSet, SupplierDocumentViewSet
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

urlpatterns = [
    path('sync/push', PushEndpoint.as_view(), name='sync-push'),
    path('sync/pull', PullEndpoint.as_view(), name='sync-pull'),
    path('health', health_check, name='health'),
    
    # Auth
    path('auth/login', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),
] + router.urls

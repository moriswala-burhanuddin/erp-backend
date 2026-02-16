from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    PushEndpoint, PullEndpoint, EmployeeViewSet, AttendanceViewSet, 
    LeaveViewSet, PayrollViewSet, PerformanceReviewViewSet
)
from .serializers import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'leaves', LeaveViewSet)
router.register(r'payroll', PayrollViewSet)
router.register(r'performance', PerformanceReviewViewSet)

urlpatterns = [
    path('sync/push', PushEndpoint.as_view(), name='sync-push'),
    path('sync/pull', PullEndpoint.as_view(), name='sync-pull'),
    path('health', lambda r: Response({
        "status": "online", 
        "version": "1.0.5",
        "roles": [c[0] for c in User._meta.get_field('role').choices]
    }), name='health'),
    
    # Auth
    path('auth/login', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),
] + router.urls

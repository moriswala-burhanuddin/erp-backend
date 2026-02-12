from django.urls import path
from .views import PushEndpoint, PullEndpoint
from .serializers import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('sync/push', PushEndpoint.as_view(), name='sync-push'),
    path('sync/pull', PullEndpoint.as_view(), name='sync-pull'),
    
    # Auth
    path('auth/login', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]

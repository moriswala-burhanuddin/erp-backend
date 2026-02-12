from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

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

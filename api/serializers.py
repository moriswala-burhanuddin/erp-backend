from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['role'] = user.role
        token['name'] = f"{user.first_name} {user.last_name}".strip()
        token['email'] = user.email
        if user.store:
            token['store_id'] = user.store.id
            token['store_name'] = user.store.name
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra response data
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'name': f"{self.user.first_name} {self.user.last_name}".strip(),
            'role': self.user.role,
            'store_id': self.user.store.id if self.user.store else None
        }
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

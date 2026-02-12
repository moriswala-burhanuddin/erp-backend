
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storeflow_backend.settings")
django.setup()

User = get_user_model()

def create_admin():
    email = 'admin@storeflow.com'
    password = 'admin'
    
    if not User.objects.filter(email=email).exists():
        print(f"Creating superuser: {email}")
        User.objects.create_superuser(email=email, username='admin', password=password)
        print("Superuser created successfully!")
    else:
        print("Superuser already exists.")

if __name__ == "__main__":
    create_admin()

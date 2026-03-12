import os
import django
import sys
from django.conf import settings

sys.path.append('d:/NEW-ERP/storeflow-erp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

print(f"DATABASE ENGINE: {settings.DATABASES['default']['ENGINE']}")
print(f"DATABASE NAME: {settings.DATABASES['default']['NAME']}")

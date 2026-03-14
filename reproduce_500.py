import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeflow_backend.settings')
django.setup()

from api.models import Client, Feature, ClientFeature

def test_add_client():
    print("Testing adding a client...")
    try:
        # Create a dummy client
        client = Client.objects.create(
            name="Test Client",
            license_key="TEST-123-456"
        )
        print(f"Client created: {client.id}")
        
        # Check if features were linked
        features_count = ClientFeature.objects.filter(client=client).count()
        print(f"Features linked: {features_count}")
        
        # Clean up
        client.delete()
        print("Test client deleted.")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_add_client()

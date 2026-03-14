from django.core.management.base import BaseCommand
from api.models import Feature, Client, ClientFeature

class Command(BaseCommand):
    help = 'Seeds initial AI features and ensures existing clients have them'

    def handle(self, *args, **options):
        ai_features = [
            ("Business Analyst", "Chat with your ERP data for insights."),
            ("Inventory Forecast", "Predicts stockouts based on sales velocity."),
            ("Invoice OCR", "Automatically scans and populates purchase orders from receipt images."),
            ("Reorder Optimization", "Recommends optimal minStock and reorder quantities."),
            ("HR & Performance AI", "Analyzes attendance patterns, employee risk, and shift scheduling."),
            ("Recruitment AI", "Parses and scores resumes automatically."),
            ("HR Assistant", "A dedicated policy-aware chatbot for staff."),
        ]
        
        created_count = 0
        for name, desc in ai_features:
            feature, created = Feature.objects.get_or_create(
                name=name, 
                defaults={'description': desc}
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created feature: {name}'))
            else:
                self.stdout.write(f'Feature already exists: {name}')

        # Also ensure all current clients have these features (Signal handles new ones, but just in case)
        self.stdout.write("Checking client feature assignments...")
        all_features = Feature.objects.all()
        for client in Client.objects.all():
            for feature in all_features:
                ClientFeature.objects.get_or_create(
                    client=client,
                    feature=feature,
                    defaults={'enabled': False}
                )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created_count} new features.'))

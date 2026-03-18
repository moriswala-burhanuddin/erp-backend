from django.core.management.base import BaseCommand
from api.models import Feature, Client, ClientFeature

class Command(BaseCommand):
    help = 'Seeds AI features and configures TMR International client'

    def handle(self, *args, **options):
        # 1. Define AI Features
        ai_features = [
            ("Business Analyst", "AI-powered business insights chat."),
            ("Inventory Forecast", "AI stock prediction."),
            ("Invoice OCR", "AI receipt scanning."),
            ("Reorder Optimization", "AI reorder recommendations."),
            ("HR Assistant", "AI HR Policy chatbot."),
            ("HR & Performance AI", "AI Performance and Risk analysis."),
            ("Recruitment AI", "AI Resume parsing and scoring.")
        ]

        # 2. Create Features
        feature_objs = []
        for name, desc in ai_features:
            feature, created = Feature.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created feature: {name}'))
            feature_objs.append(feature)

        # 3. Configure TMR International
        client, created = Client.objects.get_or_create(
            license_key='tmr-international',
            defaults={'name': 'TMR International'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created client: {client.name}'))

        # 4. Ensure TMR doesn't have AI features enabled
        for feature in feature_objs:
            cf, created = ClientFeature.objects.get_or_create(
                client=client,
                feature=feature,
                defaults={'enabled': False}
            )
            if not created and cf.enabled:
                cf.enabled = False
                cf.save()
                self.stdout.write(self.style.WARNING(f'Disabled {feature.name} for {client.name}'))
            elif created:
                self.stdout.write(self.style.SUCCESS(f'Added {feature.name} to {client.name} (Disabled)'))

        self.stdout.write(self.style.SUCCESS('Seeding completed successfully.'))

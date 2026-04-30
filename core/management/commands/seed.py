from django.core.management.base import BaseCommand
from django.core.management import call_command
from core.models import PersonModel
from pathlib import Path
from django.conf import settings
import json

class Command(BaseCommand):
    help = "Seed profiles into db"

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write("Seeding profile into database .... 🚀😎⌛")
            populate_profiles(self)
            self.stdout.write("Success seeding profile into database .... ✅✅")
        except Exception as e:
            self.stdout.write("An error occured while seeding into DB ... ❌❌")
            raise e
        
def populate_profiles(self):
    file_path = Path(settings.BASE_DIR) / "seed_profiles.json"
    with open(file_path, 'r', encoding='utf-8') as file:        
        data = json.load(file)
    for profile in data["profiles"]:
        person, created = PersonModel.objects.get_or_create(name=profile['name'], defaults={
            "gender": profile['gender'],
            "gender_probability": profile['gender_probability'],
            "age": profile['age'],
            "age_group": profile['age_group'],
            "country_id": profile['country_id'],
            "country_name": profile['country_name'],
            "country_probability": profile['country_probability']
        })
        if created: 
            self.stdout.write(f"Successfully created profile: {person.name}.")
        else:
            self.stdout.write(f"{person.name} profile already exists.")

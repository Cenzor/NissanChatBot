from django.core.management.base import BaseCommand
from app.models import TGAccount, VKAccount, FBAccount
import json


class Command(BaseCommand):
    def handle(self, *args, **options):
        counter = 0
        with open('dump.json', 'r') as file:
            json_data = json.loads(file.read())
            for user_dump in json_data:
                if user_dump['provider'] == 'telegram':
                    class_ = TGAccount
                elif user_dump['provider'] == 'vk':
                    class_ = VKAccount
                elif user_dump['provider'] == 'facebook':
                    class_ = FBAccount
                if class_.objects.filter(id=user_dump['id']).count() == 0:
                    counter += 1
                    class_.objects.create(id=user_dump['id'], first_name=user_dump['first_name'], vin=user_dump['vin'])
        print('Imported:', counter)

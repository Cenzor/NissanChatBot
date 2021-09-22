from django.core.management.base import BaseCommand
from app.models import Service


class Command(BaseCommand):
    def handle(self, *args, **options):
        Service.objects.create(name='Регулярное техническое обслуживание', api_id=13)
        Service.objects.create(name='Запасные части «Преимущество 3+» включая замену для а/м старше 3-х лет', api_id=40)
        Service.objects.create(name='«Преимущество 3+» : Запасные части для а/м старше 3х лет', api_id=40)
        Service.objects.create(name='Комплексная проверка автомобиля', api_id=14)
        Service.objects.create(name='Ультразвуковая очистка кондиционера', api_id=14)
        Service.objects.create(name='Масляный сервис для а/м старше 3-х лет', api_id=16)
        Service.objects.create(name='Другие услуги', api_id=17)

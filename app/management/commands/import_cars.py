from django.core.management.base import BaseCommand
from django.conf import settings
from app.models import Car
from copy import copy
from constance import config
import requests, ujson


def call_nissanvd(method: str):
    return requests.get(config.NISSAN_VD_API + method, headers={
            'Authorization': 'Basic ' + config.NISSAN_VD_API_SECRET
          })


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Loading cars list...')
        cars_request = call_nissanvd('model')
        if cars_request.status_code == 200:
            print('Loading prices list...')
            prices_request = call_nissanvd('priceList')
            print('Loading make list...')
            make_request = call_nissanvd('make')
            if prices_request.status_code == 200 and make_request.status_code == 200:
                prices_json = prices_request.json()
                make_json = make_request.json()
                for car_data in cars_request.json():
                    price_info = (list(x for x in prices_json if x['modelId'] == car_data['id']) or [None])[0]
                    if price_info is not None:
                        prices = price_info['prices'][0]
                        price = prices['msRwVAT'] - prices['tradeInOffer'] - prices['loyalTradeIn'] - prices['discount']
                        versions_list = []
                        for version in list(x for x in make_json if x['modelId'] == car_data['id']):
                            version_ = copy(version)
                            del version_['modelId']
                            del version_['techSpecs']
                            versions_list.append(version)
                        versions = ujson.dumps(versions_list)

                        car = Car.objects.filter(id=car_data['id']).first()
                        if car is None:
                            car = Car(id=car_data['id'])
                            print('New car:', car_data['name'])
                        car.brand = car_data['brand']
                        car.name = car_data['name']
                        car.model_group_id = car_data['modelGroupId']
                        car.model_code = car_data['modelCode']
                        car.year = car_data['year']
                        car.min_price = price
                        car.disabled = car_data['disabled']
                        car.photo = car_data['modelImages'][0]['filename'] if len(car_data['modelImages']) > 0 else None
                        if car.versions in ['[]', ''] or len(car.versions) > 0:
                            car.versions = versions
                        car.save()
        print('Import cars complete.')

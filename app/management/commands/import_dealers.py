from django.core.management.base import BaseCommand
from app.models import Dealer
from app.bot.assets import yandex_geo
from constance import config
import requests, xmltodict, json, re


class Command(BaseCommand):
    def handle(self, *args, **options):
        response = requests.post(config.NISSAN_AFTER_API + 'Services/Public/InfoService.asmx/GetDealers')
        if response.status_code == 200:
            json_data = json.dumps(xmltodict.parse(response.text))
            data = json.loads(json_data)
            for dealer_obj in data['ArrayOfDealerInfoDto']['DealerInfoDto']:
                if not dealer_obj.get('Address') or not dealer_obj.get('CityRu') or not dealer_obj.get('HeliosCode'):
                    continue
                dealer = Dealer.objects.filter(helios_code=dealer_obj['HeliosCode']).first()
                if dealer is None:
                    dealer = Dealer()
                print('Parse: ', dealer_obj['HeliosCode'])
                dealer.name = dealer_obj['DealerNameRu']
                dealer.street = dealer_obj['Address']
                dealer.zip = re.sub(r'[^\d]+', '', dealer_obj.get('PostIndex') or '0')
                dealer.city = dealer_obj['CityRu']
                dealer.phone = re.sub(r'[^\d]+', '', dealer_obj.get('Phone') or dealer_obj.get('PhoneForCarMaintenance'))
                if dealer.phone == '':
                    dealer.phone = None
                dealer.helios_code = dealer_obj['HeliosCode']
                longitude, latitude = yandex_geo.get_coords(dealer.full_address)
                dealer.latitude = latitude or 0
                dealer.longitude = longitude or 0
                dealer.save()
        else:
          print('Couldn\'t load Nissan dealers list. Response status:', response.status_code)

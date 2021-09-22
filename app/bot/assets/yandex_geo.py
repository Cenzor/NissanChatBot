from django.conf import settings
from yandex_geocoder import Client


client = Client(settings.YANDEX_GEO_API_KEY)


def get_address(*args):
    return client.address(*args)


def get_coords(*args):
    try:
        return client.coordinates(*args)
    except Exception as ex:
        return (None, None,)

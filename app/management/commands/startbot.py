from django.core.management.base import BaseCommand
from django.conf import settings
from app.bot import NissanBot


class Command(BaseCommand):
    help = 'Start Telegram bot'

    def add_arguments(self, parser):
        parser.add_argument('sc', type=str)
    
    def handle(self, *args, **options):
        if options['sc'] == 'vk':
            current_bot = NissanBot(vk_token=settings.VK_TOKEN)
        elif options['sc'] == 'tg':
            current_bot = NissanBot(tg_token=settings.TG_TOKEN)
        else:
            return print('"sc" parameter is not set or such a social network is not found')
        current_bot.create_longpoll_listeners()

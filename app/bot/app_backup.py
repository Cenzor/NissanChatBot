from django.db.models import Q
from app.bot.assets import TGMessage, VKMessage, TGCallback, VKCallback, fake_callback #, FBMessage
from app.models import Account, TGAccount, VKAccount, FaqList
from app.bot import handler
from app.bot.assets import Bot as FBBot
from threading import Thread
from vkbottle import GroupEventType, GroupTypes
# from pymessenger.bot import Bot as FBBot
import os, importlib, re, uvloop, asyncio, aiogram, vkbottle, ujson
from django.db import close_old_connections #new


class NissanBot:
    def __init__(self, **kwargs):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        uvloop.install()
        self.read_handlers()
        self._tg_token = kwargs.get('tg_token')
        self._vk_token = kwargs.get('vk_token')
        self._fb_token = kwargs.get('fb_token')

    def create_longpoll_listeners(self):
        if not self._tg_token and not self._vk_token:
            raise Exception("Not enough arguments for start bot")
        if self._tg_token is not None:
            self._create_listeners_tg(self._tg_token)
        elif self._vk_token is not None:
            self._create_listeners_vk(self._vk_token)

    def create_callback_instances(self):
        if not self._fb_token:
            raise Exception("Not enough arguments for start bot")
        self.__fb_bot = FBBot(self._fb_token)

    def _create_listeners_tg(self, token):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.__tgbot = aiogram.Bot(token=token)
        self.__tgdp = aiogram.Dispatcher(self.__tgbot)
        TGAccount.TempData.bot = self.__tgbot

        def load_or_create(user_data):
            return TGAccount.objects.get_or_create(id=user_data.id,
                                            defaults={'first_name': user_data.first_name, 'last_name': user_data.last_name, 'username': user_data.username})[0]

        @self.__tgdp.message_handler(content_types=[aiogram.types.ContentType.ANY])
        async def _(message: aiogram.types.Message):
            new_message = TGMessage(text=message.text or '', chat_id=message['from'].id, source=message)
            user = load_or_create(message['from'])
            asyncio.ensure_future(self.handle_message(new_message, user, self.__tgbot))

        @self.__tgdp.callback_query_handler()
        async def _(call: aiogram.types.CallbackQuery):
            callback = TGCallback(name=call.data, chat_id=call.from_user.id, source=call, bot=self.__tgbot)
            user = load_or_create(call.from_user)
            asyncio.ensure_future(self.handle_callback(callback, user, self.__tgbot))

        aiogram.executor.start_polling(self.__tgdp, skip_updates=True)

    def _create_listeners_vk(self, token):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.__vkbot = vkbottle.Bot(token)
        VKAccount.TempData.bot = self.__vkbot

        async def load_or_create(from_id):
            close_old_connections()
            print('Load user VK:', from_id)
            account = VKAccount.objects.filter(id=from_id).first()
            if account is None:
                user = (await self.__vkbot.api.users.get(from_id))[0]
                return VKAccount.objects.create(id=from_id, first_name=user.first_name, last_name=user.last_name)
            else:
                return account

        @self.__vkbot.on.message()
        async def _(message):
            user = await load_or_create(message.from_id)
            if message.payload is not None:
                callback = VKCallback(name=ujson.loads(message.payload)['cmd'], chat_id=message.from_id, source=None, bot=self.__vkbot)
                asyncio.ensure_future(self.handle_callback(callback, user, self.__vkbot))
            else:
                new_message = VKMessage(text=message.text, chat_id=message.from_id, source=message)
                asyncio.ensure_future(self.handle_message(new_message, user, self.__vkbot))

        @self.__vkbot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=GroupTypes.MessageEvent)
        async def _(event: GroupTypes.MessageEvent):
            callback = VKCallback(name=event.object.payload['cmd'], chat_id=event.object.user_id, source=event, bot=self.__vkbot)
            user = await load_or_create(event.object.user_id)
            asyncio.ensure_future(self.handle_callback(callback, user, self.__vkbot))

        async def init():
            await self.__vkbot.run_polling()
        loop.run_until_complete(asyncio.wait([loop.create_task(init())]))

    async def handle_message(self, message, user, bot_object):
        processed_name = message.text.lower().strip()
        path_args = re.split(r'\s+', processed_name)
        if ('меню' in processed_name or '/start' in processed_name) and user.dialog != Account.Dialog.START:
            await user.return_menu()
        else:
            for command in handler.commands:
                if (command.only_to is None or message.class_name in command.only_to) and ((not command.with_args and command.name in ['', processed_name]) or (command.with_args and command.name in ['', path_args[0]])) and command.dialog == user.dialog:
                    if not await command.handle(message, path_args, bot_object, user):
                        await message.reply('❌ Произошла <b>системная</b> ошибка. Выйдите в меню и попробуйте <b>ещё раз</b>.')
                    break
            else:
                faq = FaqList.objects.filter(question__icontains=processed_name).first()
                if faq is None:
                    query = Q()
                    for arg in [processed_name] + path_args:
                        query |= Q(keywords__istartswith=f'{arg},')
                        query |= Q(keywords__icontains=f' {arg},')
                        query |= Q(keywords__iendswith=f', {arg}')
                    faq = FaqList.objects.filter(query).first()
                    if faq is not None:
                        if faq.link != '':
                            path_args = re.split(r'\s+', faq.link)
                            for callback_ in handler.callbacks:
                                if callback_.name == path_args[0]:
                                    return await callback_.handle(fake_callback(message, bot_object), path_args, bot_object, user)
                        elif faq.answer != '':
                            return await message.reply(faq.answer)
                else:
                    return await message.reply(faq.answer)
                await message.reply('⚠️ Неизвестная команда. Напишите мне <b>«Меню»</b> и воспользуйтесь кнопками')

    async def handle_callback(self, callback, user, bot_object):
        print(callback)
        path_args = re.split(r'\s+', callback.name)
        for callback_ in handler.callbacks:
            if (callback_.only_to is None or callback.class_name in callback_.only_to) and callback_.name == path_args[0]:
                await callback_.handle(callback, path_args, bot_object, user)
                break

    def read_handlers(self):
        for root, dirs, files in os.walk('app/bot/commands'):
            check_extension = filter(lambda x: x.endswith('.py'), files)
            for command in check_extension:
                path = os.path.join(root, command)
                spec = importlib.util.spec_from_file_location(command, os.path.abspath(path))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

    @property
    def fb_bot(self):
        return self.__fb_bot
    

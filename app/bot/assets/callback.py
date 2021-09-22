from aiogram.types import ReplyKeyboardMarkup as RKM, KeyboardButton as KB, ReplyKeyboardRemove as RKR, InlineKeyboardMarkup as IKM, InlineKeyboardButton as IKB
from vkbottle import Keyboard as VKM, Text as VKB, Callback as VKC, Location as VKL, OpenLink as VKO
from typing import Optional
import re, random


class CallbackEvent:
    name: str
    chat_id: int

    def __init__(self, name: str, chat_id: int, source, bot):
        self.name = name 
        self.chat_id = chat_id
        self.source = source
        self._bot = bot

    def reply_keyboard(self, type_: str, kb_args: dict) -> bool:
        if 'only_to' in kb_args:
            only_to = kb_args['only_to']
            del kb_args['only_to']
            if isinstance(only_to, list):
                return type_ in only_to
        return True

    def hide_reply_keyboard(self, type_: str, only_to: Optional[list]):
        return type_ in only_to if only_to else True

    def inline_keyboard(self, type_: str, only_to: Optional[list]):
        return type_ in only_to if only_to else True


class TGCallback(CallbackEvent):
    class_name = 'telegram'

    def reply_keyboard(self, k_list: list, **kwargs) -> Optional[RKM]:
        return super().reply_keyboard(self.class_name, kwargs) and RKM(k_list, resize_keyboard=True, **kwargs)

    def reply_keyboard_button(self, text: str, **kwargs) -> KB:
        return KB(text, **kwargs)

    def hide_reply_keyboard(self, only_to=None) -> RKR:
        return super().hide_reply_keyboard(self.class_name, only_to) and RKR()

    def inline_keyboard(self, k_list: list, only_to=None) -> Optional[IKM]:
        return super().inline_keyboard(self.class_name, only_to) and IKM(inline_keyboard=k_list)

    def inline_keyboard_button(self, text: str, **kwargs) -> IKB:
        return IKB(text, **kwargs)

    async def delete(self):
        self.source is not None and await self.source.message.delete()

    async def edit_text(self, text: str, **kwargs):
        if self.source is not None:
            await self.source.message.edit_text(text, parse_mode='HTML', **kwargs)
        else:
            await self._bot.send_message(chat_id=self.chat_id, text=text, parse_mode='HTML', **kwargs)


class VKCallback(CallbackEvent):
    class_name = 'vk'

    async def reply(self, text, keyboard=None):
        text = re.sub(r'<\/?[A-z](\shref=\".+\")?>', '', text)
        await self.source.answer(text, keyboard=keyboard)

    def reply_keyboard(self, k_list: list, **kwargs) -> Optional[VKM]:
        if super().reply_keyboard(self.class_name, kwargs):
            kb = VKM(**kwargs)
            for i, row in enumerate(k_list):
                for btn in row:
                    kb.add(btn if not isinstance(btn, str) else self.reply_keyboard_button(btn))
                if len(k_list) > 10:
                    if (i + 1) % 2 == 0 and i + 1 != len(k_list):
                        kb.row()
                elif i + 1 < len(k_list):
                    kb.row()
            return kb
        else:
            return None

    def reply_keyboard_button(self, text: str, **kwargs) -> Optional[VKB]:
        if 'request_contact' in kwargs:
            return None
        if len(text) > 40:
            text = text[:40]
        if 'request_location' in kwargs:
            del kwargs['request_location']
            return VKL(**kwargs)
        else:
            return VKB(text, **kwargs)

    def hide_reply_keyboard(self, only_to=None) -> []:
        return None

    def inline_keyboard(self, k_list: list, only_to=None) -> Optional[VKB]:
        if super().inline_keyboard(self.class_name, only_to):
            kb = VKM(inline=True)
            buttons_count = 0
            for i, row in enumerate(k_list):
                for btn in row:
                    kb.add(btn)
                    buttons_count += 1
                if len(k_list) > 6:
                    if (i + 1) % 2 == 0 and i + 1 != len(k_list):
                        kb.row()
                elif i + 1 < len(k_list):
                    kb.row()
            if buttons_count <= 10:
                return kb
            else:
                k_list = self.convert_inline_to_reply_keyboard(k_list)
                return self.reply_keyboard(k_list)
        else:
            return None

    def convert_inline_to_reply_keyboard(self, k_list: list):
        new_list = []
        for row in k_list:
            new_list.append([])
            for btn in row:
                new_list[-1].append(VKB(btn.label, payload=btn.payload))
        return new_list

    def inline_keyboard_button(self, text: str, **kwargs) -> VKC:
        if len(text) > 40:
            text = text[:40]
        if 'callback_data' in kwargs:
            return VKC(text, payload={"cmd": kwargs['callback_data']})
        elif 'url' in kwargs:
            return VKO(label=text, link=kwargs['url'])
        else:
            return None

    async def delete(self):
        pass

    async def edit_text(self, text: str, **kwargs):
        text = re.sub(r'<\/?[A-z](\shref=\".+\")?>', '', text)
        if 'reply_markup' in kwargs:
            kwargs['keyboard'] = kwargs['reply_markup']
            del kwargs['reply_markup']
        if self.source is not None:
            await self._bot.api.messages.edit(peer_id=self.source.object.peer_id, conversation_message_id=self.source.object.conversation_message_id, message=text, **kwargs)
        else:
            await self._bot.api.messages.send(peer_id=self.chat_id, message=text, random_id=random.randint(1, 999999999), **kwargs)


class FBCallback(CallbackEvent):
    class_name = 'facebook'

    def reply_keyboard(self, k_list: list, **kwargs):
        if super().reply_keyboard(self.class_name, kwargs):
            result = []
            for x in k_list:
                result += x
            return result
        else:
            return None

    def reply_keyboard_button(self, text: str, **kwargs):
        return {'content_type': 'text', 'title': text, 'payload': 'plane_text'}

    def hide_reply_keyboard(self, only_to=None):
        pass

    def inline_keyboard(self, k_list: list, only_to=None):
        if super().inline_keyboard(self.class_name, only_to):
            result = []
            for x in k_list:
                result += x
            return result
        else:
            return None

    def inline_keyboard_button(self, text: str, **kwargs):
        return {'content_type': 'text', 'title': text, 'payload': kwargs['callback_data'] if 'callback_data' in kwargs else f'view_url {kwargs["url"]}'}

    async def delete(self):
        pass

    async def edit_text(self, text: str, **kwargs):
        processed_text = re.sub(r'<\/?[A-z](\shref=\".+\")?>', '', text)
        payload = {}
        payload['message'] = {'text': processed_text}
        if kwargs['reply_markup'] is not None:
            payload['message']['quick_replies'] = kwargs['reply_markup']
        return self._bot.send_recipient(recipient_id=self.chat_id, payload=payload)


def fake_callback(message, bot):
    if message.class_name == 'telegram':
        return TGCallback('', message.chat_id, None, bot)
    elif message.class_name == 'vk':
        return VKCallback('', message.chat_id, None, bot)

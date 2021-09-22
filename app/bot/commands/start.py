from aiogram.types import InlineKeyboardMarkup as IKM, InlineKeyboardButton as IKB
from django.conf import settings
from app.bot import handler, parse_vin_image
from app.models import Account
import re, os


@handler.message(name='', dialog=Account.Dialog.START)
async def _(message, path_args, bot, user):
    user.dialog = Account.Dialog.START_PHONE
    user.save()
    await user.reply('Здравствуйте, я Nissy – чат-бот Nissan и Ваш личный помощник. Возможно мы уже знакомы, могу я попросить Вас поделиться со мной Вашим номером телефона?', keyboard=message.reply_keyboard([
            [message.reply_keyboard_button('Телефон', request_contact=True)]
        ], one_time_keyboard=True, only_to=['telegram']))


@handler.message(dialog=Account.Dialog.START_PHONE)
async def _(message, path_args, bot, user):
    phone = message.source.contact.phone_number if hasattr(message.source, 'contact') and message.source.contact is not None else re.sub(r'[\s\-\(\)]', '', message.text)
    if re.match(r'^(8|(\+?7))?\d{10}$', phone) is not None:
        user.phone = phone
        user.dialog = Account.Dialog.START_NAME
        user.save()
        await user.reply('К сожалению, мы еще не знакомы, как я могу к Вам обращаться?', keyboard=message.hide_reply_keyboard(only_to=['telegram']))
    else:
        await user.reply('Для предоставления наиболее качественного сервиса хочу попросить Вас поделиться со мной Вашим номером телефона.', keyboard=message.reply_keyboard([
            [message.reply_keyboard_button('Телефон', request_contact=True)]
        ], one_time_keyboard=True, only_to=['telegram']))


@handler.message(name='', dialog=Account.Dialog.START_NAME)
async def _(message, path_args, bot, user):
    user.first_name = message.text
    user.dialog = Account.Dialog.START_INFO
    user.save()
    await user.reply(f'{user.first_name}, приятно познакомиться! <i>(Если Вы захотите сменить имя, по которому я к Вам обращаюсь, это можно сделать в настройках.)</i>')
    await user.reply('Не могу не поинтересоваться: Вы являетесь владельцем автомобиля Nissan?', keyboard=message.inline_keyboard([
            [message.inline_keyboard_button('Да', callback_data='is_auto_owner 1'), message.inline_keyboard_button('Нет', callback_data='is_auto_owner 2')]
        ]))


@handler.message(name='да', dialog=Account.Dialog.START_INFO, only_to=['vk', 'facebook'])
async def _(message, path_args, bot, user):
    user.dialog = Account.Dialog.START_VIN
    user.save()
    await user.reply(f'{user.first_name}, я могу предложить Вам считать VIN с документов на автомобиль (СТС или ПТС) с помощью камеры Вашего смартфона, либо ввести 17 символов VIN вручную.\n\nДля считывания VIN с помощью камеры Вашего смартфона:\n1) Откройте меню для отправки файлов\n2) Включите камеру\n3) Разместите документ в кадре целиком\n4) Отправьте фото\n\nЛибо введите 17 символов VIN вручную и отправьте сообщение.\n\n<i>(При нажатии на кнопку “Отмена”, вы завершите регистрацию. Если Вы захотите зарегистрировать VIN, это можно будет сделать в настройках.)</i>', keyboard=message.reply_keyboard([
            [message.reply_keyboard_button('Отмена')]
        ]))


@handler.message(name='нет', dialog=Account.Dialog.START_INFO, only_to=['vk', 'facebook'])
async def _(message, path_args, bot, user):
    await complete_registration(user)


@handler.callback(name='is_auto_owner')
async def _(callback, path_args, bot, user):
    if len(path_args) == 2 and path_args[1].isdigit():
        status = int(path_args[1]) == 1
        if status:
            user.dialog = Account.Dialog.START_VIN
            user.save()
            await callback.edit_text(f'{user.first_name}, я могу предложить Вам считать VIN с документов на автомобиль (СТС или ПТС) с помощью камеры Вашего смартфона, либо ввести 17 символов VIN вручную.\n\nДля считывания VIN с помощью камеры Вашего смартфона:\n1) Откройте меню для отправки файлов\n2) Включите камеру\n3) Разместите документ в кадре целиком\n4) Отправьте фото\n\nЛибо введите 17 символов VIN вручную и отправьте сообщение.\n\n<i>(При нажатии на кнопку “Отмена”, вы завершите регистрацию. Если Вы захотите зарегистрировать VIN, это можно будет сделать в настройках.)</i>', reply_markup=callback.inline_keyboard([
                    [callback.inline_keyboard_button('Отмена', callback_data='is_auto_owner 2')]
                ]))
        else:
            await callback.delete()
            await complete_registration(user)


@handler.message(name='', dialog=Account.Dialog.START_VIN)
async def _(message, path_args, bot, user):
    if message.text.lower() == 'отмена':
        await complete_registration(user)
    else:
        photo = await message.get_photo()
        if photo is not None:
            photo_name = str(user.id) + '_vin.jpg'
            photo_full_path = os.path.join('media', 'vin', photo_name)
            await photo.download(photo_full_path)
            await user.reply('Скан получен. Считывание VIN\nПодождите...')
            result = await parse_vin_image(open(photo_full_path, 'rb'))
            if result is not None:
                return await user.reply(f'Распознанный VIN: <code>{result}</code>. Если VIN неправильный, попробуйте отправить другое фото или написать его вручную.', keyboard=message.inline_keyboard([
                        [message.inline_keyboard_button('✅ Подтвердить', callback_data=f'start_set_vin {result}')]
                    ]))
        else:
            if re.match(settings.VIN_REGEXP, message.text):
                return await user.reply(f'Заданный VIN: <code>{message.text.upper()}</code>. Проверьте VIN номер и, если всё хорошо, подтвердите действие.', keyboard=message.inline_keyboard([
                        [message.inline_keyboard_button('✅ Подтвердить', callback_data=f'start_set_vin {message.text}')]
                    ]))
        await user.reply('К сожалению, я не могу распознать Ваш VIN.\nПожалуйста, введите 17 символов VIN, используя только цифры и латинские буквы.')


@handler.callback(name='start_set_vin')
async def _(callback, path_args, bot, user):
    if len(path_args) == 2:
        await callback.delete()
        await complete_registration(user, vin=path_args[1])


async def complete_registration(user, vin=None):
    user.vin = vin
    await user.reply('Превосходно! Теперь я готов ответить на Ваши вопросы.\n<i>(Если Вы захотите зарегистрировать VIN, это можно сделать в настройках.)</i>\n\nХочу отметить, что мы обещаем быть ВСЕГДА НА СВЯЗИ 24/7\nОтвет на любой вопрос по телефону 8 800 200 59 90 или пообщавшись со мной.')
    await user.return_menu()

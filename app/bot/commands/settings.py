from django.conf import settings
from app.models import Account
from app.bot import handler, parse_vin_image
import os, re


@handler.message(name='настройки', dialog=Account.Dialog.DEFAULT)
async def _(message, path_args, bot, user):
    await user.reply(f'{user.first_name}, вы попали в раздел настроек профиля:', keyboard=message.inline_keyboard([
            [message.inline_keyboard_button('Отписаться от новостей и событий' if user.mailing else 'Подписаться на новости и события', callback_data='toggle_mailing')],
            [message.inline_keyboard_button('Указать VIN' if user.vin is None else 'Сменить VIN', callback_data='change_vin')],
            [message.inline_keyboard_button('Сменить имя', callback_data='change_first_name')],
            [message.inline_keyboard_button('⬅️ Главное меню', callback_data='menu')],
        ]))


@handler.callback(name='settings')
async def _(callback, path_args, bot, user):
    await callback.edit_text(f'{user.first_name}, вы попали в раздел настроек профиля:', reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('Отписаться от новостей и событий' if user.mailing else 'Подписаться на новости и события', callback_data='toggle_mailing')],
            [callback.inline_keyboard_button('Указать VIN' if user.vin is None else 'Сменить VIN', callback_data='change_vin')],
            [callback.inline_keyboard_button('Сменить имя', callback_data='change_first_name')],
            [callback.inline_keyboard_button('⬅️ Главное меню', callback_data='menu')],
        ]))


@handler.callback(name='toggle_mailing')
async def _(callback, path_args, bot, user):
    user.mailing = not user.mailing
    user.save()
    await callback.edit_text('✅ Вы успешно ' + ('подписались на новости и события!' if user.mailing else 'отписались от новостей и событий.'), reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('⬅️ Назад', callback_data='settings')]
        ]))


@handler.callback(name='change_vin')
async def _(callback, path_args, bot, user):
    await callback.delete()
    user.dialog = Account.Dialog.CHANGE_VIN
    user.save()
    await user.reply(f'{user.first_name}, я могу предложить Вам считать VIN с документов на автомобиль (СТС или ПТС) с помощью камеры Вашего смартфона, либо ввести 17 символов VIN вручную.\n\nДля считывания VIN с помощью камеры Вашего смартфона:\n1) Отройте меню для отправки файлов\n2) Включите камеру\n3) Разместите документ в кадре целиком\n4) Отправьте фото\n\nЛибо введите 17 символов VIN вручную и отправьте сообщение.')


@handler.message(name='', dialog=Account.Dialog.CHANGE_VIN)
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
                        [message.inline_keyboard_button('✅ Подтвердить', callback_data=f'change_vin_confirm {result}')]
                    ]))
        else:
            if re.match(settings.VIN_REGEXP, message.text):
                return await user.reply(f'Заданный VIN: <code>{message.text.upper()}</code>. Проверьте VIN номер и, если всё хорошо, подтвердите действие.', keyboard=message.inline_keyboard([
                        [message.inline_keyboard_button('✅ Подтвердить', callback_data=f'change_vin_confirm {message.text}')]
                    ]))
        await user.reply('К сожалению, я не могу распознать Ваш VIN.\nПожалуйста, введите 17 символов VIN, используя только цифры и латинские буквы.')


@handler.callback(name='change_vin_confirm')
async def _(callback, path_args, bot, user):
    if len(path_args) == 2:
        user.vin = path_args[1]
        await callback.edit_text('Ваш VIN номер успешно сохранён.')
        await user.return_menu()


@handler.callback(name='change_first_name')
async def _(callback, path_args, bot, user):
    user.dialog = Account.Dialog.CHANGE_FIRST_NAME
    user.save()
    await callback.delete()
    await user.reply('Как я могу к Вам обращаться?')


@handler.message(name='', dialog=Account.Dialog.CHANGE_FIRST_NAME)
async def _(message, path_args, bot, user):
    user.first_name = message.text
    await user.reply('Имя сохранено.')
    await user.return_menu()

from app.bot import handler
from app.bot.assets import yandex_geo
from app.models import Account, SpecialCategory, SpecialItem, Parking
from constance import config


@handler.message(name='сервисы', dialog=Account.Dialog.DEFAULT)
async def _(message, path_args, bot, user):
    await user.reply('Сервисное меню:', disable_web_page_preview=True, keyboard=message.inline_keyboard([
            [message.inline_keyboard_button('Спец. программы', callback_data='special_programs')],
            [message.inline_keyboard_button('Где я припарковался?', callback_data='parking')],
            [message.inline_keyboard_button('Заявка на кредит он-лайн', url=config.CREDIT_ONLINE_URL)],
            [message.inline_keyboard_button('⬅️ Главное меню', callback_data='menu')],
        ]))


@handler.callback(name='go_services')
async def _(callback, path_args, bot, user):
    await callback.edit_text('Сервисное меню:', disable_web_page_preview=True, reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('Спец. программы', callback_data='special_programs')],
            [callback.inline_keyboard_button('Где я припарковался?', callback_data='parking')],
            [callback.inline_keyboard_button('Заявка на кредит он-лайн', url=config.CREDIT_ONLINE_URL)],
            [callback.inline_keyboard_button('⬅️ Главное меню', callback_data='menu')],
        ]))


@handler.callback(name='special_programs')
async def _(callback, path_args, bot, user):
    await callback.edit_text('Меню:', disable_web_page_preview=True, reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button(x.name, callback_data=f'get_special {x.id}')] for x in SpecialCategory.objects.filter(is_disabled=False).all()
        ] + [
            [callback.inline_keyboard_button('⬅️ Назад', callback_data='go_services')]
        ]))


@handler.callback(name='get_special')
async def _(callback, path_args, bot, user):
    if len(path_args) >= 2:
        special = SpecialCategory.objects.filter(id=path_args[1]).first()
        if special is not None:
            back_btn = 'special_programs' if len(path_args) == 2 else ' '.join(path_args[2:])
            await callback.edit_text(special.text, disable_web_page_preview=True, reply_markup=callback.inline_keyboard([
                    [callback.inline_keyboard_button(x.name, callback_data=f'more_special {x.id}')] for x in special.items.all()
                ] + [
                    [callback.inline_keyboard_button('◀️ Назад', callback_data=back_btn)],
                    [callback.inline_keyboard_button('⬅️ Главное меню', callback_data='menu')]
                ]))


@handler.callback(name='more_special')
async def _(callback, path_args, bot, user):
    if len(path_args) == 2:
        special = SpecialItem.objects.filter(id=path_args[1]).first()
        if special is not None:
            await callback.edit_text(special.text, disable_web_page_preview=True, reply_markup=callback.inline_keyboard([
                    [callback.inline_keyboard_button('◀️ Назад', callback_data=f'get_special {special.category.id}')],
                    [callback.inline_keyboard_button('⬅️ Главное меню', callback_data='menu')]
                ]))


@handler.callback(name='parking')
async def _(callback, path_args, bot, user):
    if user.parking is None:
        keyboard = [
                [callback.inline_keyboard_button('Запомнить место парковки', callback_data='parking_remember')],
                [callback.inline_keyboard_button('⬅️ Главное меню', callback_data='menu')]
            ]
    else:
        keyboard = [
                [callback.inline_keyboard_button('Запомнить место парковки', callback_data='parking_remember')],
                [callback.inline_keyboard_button('Показать место парковки', callback_data='parking_show')],
                [callback.inline_keyboard_button('⬅️ Главное меню', callback_data='menu')]
            ]
    await callback.edit_text('Меню:', reply_markup=callback.inline_keyboard(keyboard))


@handler.callback(name='parking_remember', only_to=['vk', 'telegram'])
async def _(callback, path_args, bot, user):
    await callback.delete()
    user.dialog = Account.Dialog.PARKING_REMEMBER_LOCATION
    user.save()
    await user.reply('Чтобы сохранить место парковки Вашего автомобиля, <b>поделитесь текушим местоположением или введите Ваш адрес.</b>', keyboard=callback.reply_keyboard([
            [callback.reply_keyboard_button('Текущее положение', request_location=True), 'Задать самостоятельно'],
            ['Отмена']
        ]))


@handler.callback(name='parking_remember', only_to=['facebook'])
async def _(callback, path_args, bot, user):
    user.dialog = Account.Dialog.PARKING_INPUT_LOCATION
    user.save()
    await user.reply('Введите адрес вашего местоположения (Например: <i>"Москва, улица Волочаевская, дом 3"</i>)', keyboard=message.hide_reply_keyboard())


@handler.message(name='', dialog=Account.Dialog.PARKING_REMEMBER_LOCATION)
async def _(message, path_args, bot, user):
    if message.text == 'Задать самостоятельно':
        user.dialog = Account.Dialog.PARKING_INPUT_LOCATION
        user.save()
        await user.reply('Введите адрес вашего местоположения (Например: <i>"Москва, улица Волочаевская, дом 3"</i>)', keyboard=message.hide_reply_keyboard())
    elif message.text == 'Отмена':
        await user.return_menu()
    else:
        if message.location is not None:
            address = yandex_geo.get_address(message.location.longitude, message.location.latitude)
            user.temp = f'{message.location.longitude},{message.location.latitude}'
            user.dialog = Account.Dialog.PARKING_ADD_COMMENT
            user.save()
            await user.reply(f'Ваш адрес: <b>{address}</b>\n\nПо желанию Вы можете дополнить комментарием место парковки, указав номер парковки или другую информацию, которая облегчит Вам поиск автобомиля', keyboard=message.reply_keyboard([
                    [message.reply_keyboard_button('Без комментария')]
                ]))


@handler.message(name='', dialog=Account.Dialog.PARKING_INPUT_LOCATION)
async def _(message, path_args, bot, user):
    longitude, latitude = yandex_geo.get_coords(message.text)
    if longitude and latitude:
        address = yandex_geo.get_address(longitude, latitude)
        user.temp = f'{longitude},{latitude}'
        user.dialog = Account.Dialog.PARKING_ADD_COMMENT
        user.save()
        await user.reply(f'Ваш адрес: <b>{address}</b>\n\nПо желанию Вы можете дополнить комментарием место парковки, указав номер парковки или другую информацию, которая облегчит Вам поиск автобомиля', keyboard=message.reply_keyboard([
                [message.reply_keyboard_button('Без комментария')]
            ]))
    else:
        await user.reply('Не удалось определить местоположение. Попробуйте изменить запрос.')


@handler.message(name='', dialog=Account.Dialog.PARKING_ADD_COMMENT, only_to=['telegram'])
async def _(message, path_args, bot, user):
    if user.parking is not None:
        user.parking.delete()
    longitude, latitude = user.temp.split(',')
    parking = Parking.objects.create(longitude=longitude, latitude=latitude, comment=message.text)
    user.parking = parking
    user.dialog = Account.Dialog.DEFAULT
    user.save()
    address = yandex_geo.get_address(longitude, latitude)
    await user.reply(f'Сохранено\n{address}\n<a href="https://static-maps.yandex.ru/1.x/?ll={longitude},{latitude}&size=450,450&z=18&l=map&pt={longitude},{latitude}">Показать на карте</a> {longitude}, {latitude}\n{parking.comment}', keyboard=message.inline_keyboard([
            [message.inline_keyboard_button('Удалить место парковки', callback_data='parking_remove')],
            [message.inline_keyboard_button('Обновить место парковки', callback_data='parking_remember')],
            [message.inline_keyboard_button('⬅️ Главное меню', callback_data='menu')],
        ]))


@handler.message(name='', dialog=Account.Dialog.PARKING_ADD_COMMENT, only_to=['vk'])
async def _(message, path_args, bot, user):
    if user.parking is not None:
        user.parking.delete()
    longitude, latitude = user.temp.split(',')
    parking = Parking.objects.create(longitude=longitude, latitude=latitude, comment=message.text)
    user.parking = parking
    user.dialog = Account.Dialog.DEFAULT
    user.save()
    address = yandex_geo.get_address(longitude, latitude)
    await user.reply(f'Сохранено\n{address}\nНа карте: https://static-maps.yandex.ru/1.x/?ll={longitude},{latitude}&size=450,450&z=18&l=map&pt={longitude},{latitude}\n{parking.comment}', keyboard=message.inline_keyboard([
            [message.inline_keyboard_button('Удалить место парковки', callback_data='parking_remove')],
            [message.inline_keyboard_button('Обновить место парковки', callback_data='parking_remember')],
            [message.inline_keyboard_button('⬅️ Главное меню', callback_data='menu')],
        ]))


@handler.callback(name='parking_show', only_to=['telegram'])
async def _(callback, path_args, bot, user):
    if user.parking is not None:
        address = yandex_geo.get_address(user.parking.longitude, user.parking.latitude)
        await callback.edit_text(f'{address}\n<a href="https://static-maps.yandex.ru/1.x/?ll={user.parking.longitude},{user.parking.latitude}&size=450,450&z=18&l=map&pt={user.parking.longitude},{user.parking.latitude}">Показать на карте</a> {user.parking.longitude}, {user.parking.latitude}\n{user.parking.comment}', reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('Удалить место парковки', callback_data='parking_remove')],
            [callback.inline_keyboard_button('Обновить место парковки', callback_data='parking_remember')],
            [callback.inline_keyboard_button('⬅️ Главное меню', callback_data='menu')],
        ]))


@handler.callback(name='parking_show', only_to=['vk', 'facebook'])
async def _(callback, path_args, bot, user):
    if user.parking is not None:
        address = yandex_geo.get_address(user.parking.longitude, user.parking.latitude)
        await callback.edit_text(f'{address}\nНа карте: https://static-maps.yandex.ru/1.x/?ll={user.parking.longitude},{user.parking.latitude}&size=450,450&z=18&l=map&pt={user.parking.longitude},{user.parking.latitude}\n{user.parking.comment}', reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('Удалить место парковки', callback_data='parking_remove')],
            [callback.inline_keyboard_button('Обновить место парковки', callback_data='parking_remember')],
            [callback.inline_keyboard_button('⬅️ Главное меню', callback_data='menu')],
        ]))


@handler.callback(name='parking_remove')
async def _(callback, path_args, bot, user):
    if user.parking is not None:
        user.parking.delete()
    user.dialog = Account.Dialog.DEFAULT
    user.save()
    await callback.edit_text('Удалено', reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('⬅️ Главное меню', callback_data='menu')]
        ]))


from app.bot import handler
from app.models import Account, Car, Dealer, TestDrive
from app.bot.assets import yandex_geo
import ujson, math


@handler.message(name='заказать тест-драйв', dialog=Account.Dialog.DEFAULT)
async def _(message, path_args, bot, user):
    keyboard = [[]]
    for car in Car.objects.filter(disabled=False).all():
        if len(keyboard[-1]) == 2:
            keyboard.append([])
        keyboard[-1].append(message.inline_keyboard_button(car.name, callback_data=f'test_drive {car.id}'))
    await user.reply('Выберите модель:', keyboard=message.inline_keyboard(keyboard))


@handler.callback(name='test_drive_start')
async def _(callback, path_args, bot, user):
    keyboard = [[]]
    for car in Car.objects.filter(disabled=False).all():
        if len(keyboard[-1]) == 2:
            keyboard.append([])
        keyboard[-1].append(callback.inline_keyboard_button(car.name, callback_data=f'test_drive {car.id}'))
    await callback.edit_text('Выберите модель:', reply_markup=callback.inline_keyboard(keyboard))


@handler.callback(name='test_drive', only_to=['telegram', 'vk'])
async def _(callback, path_args, bot, user):
    if len(path_args) == 2 and path_args[1].isdigit():
        car = Car.objects.filter(id=path_args[1]).first()
        if car is not None:
            await callback.delete()
            user.temp = car.id
            user.dialog = Account.Dialog.TEST_DRIVE_PLACE
            user.save()
            await user.reply('Для удобства выбора дилерского центра предлагаю Вам <b>поделиться местоположением</b>', keyboard=callback.reply_keyboard([
                    [callback.reply_keyboard_button('Текущее положение', request_location=True), callback.reply_keyboard_button('Задать самостоятельно')]
                ]))


@handler.callback(name='test_drive', only_to=['facebook'])
async def _(callback, path_args, bot, user):
    if len(path_args) == 2 and path_args[1].isdigit():
        car = Car.objects.filter(id=path_args[1]).first()
        if car is not None:
            await callback.delete()
            user.temp = car.id
            await user.return_menu('Введите адрес вашего местоположения (Например: <i>"Москва, улица Волочаевская"</i>)')
            user.dialog = Account.Dialog.TEST_DRIVE_ENTER_PLACE
            user.save()


@handler.message(name='', dialog=Account.Dialog.TEST_DRIVE_PLACE)
async def _(message, path_args, bot, user):
    if message.text.lower() == 'задать самостоятельно':
        await user.return_menu('Введите адрес вашего местоположения (Например: <i>"Москва, улица Волочаевская"</i>)')
        user.dialog = Account.Dialog.TEST_DRIVE_ENTER_PLACE
        user.save()
    else:
        if message.location is not None:
            place = yandex_geo.get_address(message.location.longitude, message.location.latitude)
            user.temp = ujson.dumps({'car': user.temp, 'place': place})
            user.save()
            await user.reply(f'Давайте уточним ваше местоположение: <b>{place}</b>. Всё правильно?', keyboard=message.inline_keyboard([
                    [message.inline_keyboard_button('Да', callback_data='test_drive_place 1'), message.inline_keyboard_button('Нет', callback_data='test_drive_place 2')]
                ]))


@handler.message(name='', dialog=Account.Dialog.TEST_DRIVE_ENTER_PLACE)
async def _(message, path_args, bot, user):
    longitude, latitude = yandex_geo.get_coords(message.text)
    if latitude and longitude:
        place = yandex_geo.get_address(longitude, latitude) 
        user.temp = ujson.dumps({'car': user.temp, 'place': place})
        user.save()
        await user.reply(f'Давайте уточним ваше местоположение: <b>{place}</b>. Всё правильно?', keyboard=message.inline_keyboard([
                [message.inline_keyboard_button('Да', callback_data='test_drive_place 1'), message.inline_keyboard_button('Нет', callback_data='test_drive_place 2')]
            ]))
    else:
        await user.reply('Не удалось определить местоположение. Попробуйте изменить запрос.')


@handler.callback(name='test_drive_place')
async def _(callback, path_args, bot, user):
    if len(path_args) == 2 and path_args[1].isdigit():
        user.dialog = Account.Dialog.DEFAULT
        user.save()
        data = ujson.loads(user.temp)
        place = data['place']
        longitude, latitude = yandex_geo.get_coords(place)
        dealers = Dealer.objects.raw('SELECT *, SQRT(POW(111 * (latitude - %s), 2) + POW(111 * (%s - longitude) * COS(latitude / 57.3), 2)) AS distance FROM app_dealer HAVING distance < 25 ORDER BY distance LIMIT 5' % (latitude, longitude))
        await callback.edit_text('Ближайшие к Вам официальные дилерские центры Nissan:', reply_markup=callback.inline_keyboard([
                [callback.inline_keyboard_button(f'{x.name} (~{math.ceil(x.distance)}км)', callback_data=f'test_drive_select {x.id}')] for x in dealers
            ] + [[callback.inline_keyboard_button('⬅️ Главное меню', callback_data='menu'), callback.inline_keyboard_button('Изменить адрес', callback_data=f'test_drive {data["car"]}')]]))


@handler.callback(name='test_drive_select')
async def _(callback, path_args, bot, user):
    if len(path_args) == 2 and path_args[1].isdigit():
        dealer = Dealer.objects.filter(id=path_args[1]).first()
        if dealer is not None:
            data = ujson.loads(user.temp)
            data['dealer'] = dealer.id
            user.temp = ujson.dumps(data)
            user.save()
            car = Car.objects.filter(id=data['car']).first()
            await callback.delete()
            await user.reply('Давайте подтвердим запись на тест-драйв:')
            await user.reply(f'Модель для тест-драйва: <b>{car.name}</b>\nДилер: <b>{dealer.name}</b>\n{dealer.full_address}', keyboard=callback.inline_keyboard([
                    [callback.inline_keyboard_button('Подтвердить заявку', callback_data='test_drive_confirm')],
                    [callback.inline_keyboard_button('Сменить модель', callback_data='test_drive_start'), callback.inline_keyboard_button('Сменить дилера', callback_data=f'test_drive {car.id}')],
                    [callback.inline_keyboard_button('Отмена', callback_data='menu')],
                ]))


@handler.callback(name='test_drive_confirm')
async def _(callback, path_args, bot, user):
    data = ujson.loads(user.temp)
    dealer = Dealer.objects.filter(id=data['dealer']).first()
    car = Car.objects.filter(id=data['car']).first()
    TestDrive.objects.create(user_tg=user, dealer=dealer, car=car)
    user.temp = ''
    await user.reply(user.first_name + ', большое спасибо! Ваша заявка на тест-драйв отправлена.')
    await user.return_menu('Скоро мы свяжемся с Вами для уточнения времени визита.')

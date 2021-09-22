from app.bot import handler
from app.models import Account, Dealer
from app.bot.assets import yandex_geo
import json, math


async def select_place(callback, user):
    await callback.edit_text(f'Поиск дилеров будет производиться вблизи указанного адреса: <b>{user.temp}</b>', reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('Официальные Дилеры', callback_data='find_dealer_select 1')],
            [callback.inline_keyboard_button('Nissan Бизнес Центры', callback_data='find_dealer_select 2')],
            [callback.inline_keyboard_button('Продажа и обслуживание Nissan GT-R', callback_data='find_dealer_select 3')],
            [callback.inline_keyboard_button('Автомобили с пробегом', callback_data='find_dealer_select 4')],
            [callback.inline_keyboard_button('⬅️ Главное меню', callback_data='menu'), callback.inline_keyboard_button('Изменить адрес', callback_data='find_dealer_place 2')]
        ]))


@handler.message(name=['найти дилера', 'найди дилера', 'дилеры', 'дилер', 'ближайший дилер', 'официальные дилеры ниссан', 'дилер-локатор', 'сервис nissan', 'сервис ниссан', 'официальные сервисы ниссан'], dialog=Account.Dialog.DEFAULT, only_to=['vk', 'telegram'])
async def _(message, path_args, bot, user):
    user.dialog = Account.Dialog.FIND_DEALER_PLACE
    user.save()
    await user.reply('Для удобства выбора дилерского центра предлагаю Вам <b>поделиться местоположением</b>', keyboard=message.reply_keyboard([
            [message.reply_keyboard_button('Текущее положение', request_location=True), message.reply_keyboard_button('Задать самостоятельно')],
            [message.reply_keyboard_button('⬅️ Назад')]
        ]))


@handler.message(name=['найти дилера', 'найди дилера', 'дилеры', 'дилер', 'ближайший дилер', 'официальные дилеры ниссан', 'дилер-локатор', 'сервис nissan', 'сервис ниссан', 'официальные сервисы ниссан'], dialog=Account.Dialog.DEFAULT, only_to=['facebook'])
async def _(message, path_args, bot, user):
    user.dialog = Account.Dialog.FIND_DEALER_ENTER_PLACE
    user.save()
    await user.reply('Введите адрес вашего местоположения (Например: <i>"Москва, улица Волочаевская"</i>)')


@handler.message(name='', dialog=Account.Dialog.FIND_DEALER_PLACE)
async def _(message, path_args, bot, user):
    text = message.text.lower()
    if text == 'задать самостоятельно':
        user.dialog = Account.Dialog.FIND_DEALER_ENTER_PLACE
        user.save()
        await user.reply('Введите адрес вашего местоположения (Например: <i>"Москва, улица Волочаевская"</i>)')
    elif 'назад' in text:
        await user.return_menu()
    else:
        if message.location is not None:
            place = yandex_geo.get_address(message.location.longitude, message.location.latitude)
            print(place)
            user.temp = place
            user.save()
            await user.reply(f'Давайте уточним ваше местоположение: <b>{place}</b>. Всё правильно?', keyboard=message.inline_keyboard([
                    [message.inline_keyboard_button('Да', callback_data='find_dealer_place 1'), message.inline_keyboard_button('Нет', callback_data='find_dealer_place 2')]
                ]))


@handler.callback(name='find_dealer_place')
async def _(callback, path_args, bot, user):
    if len(path_args) == 2:
        if path_args[1] == '1':
            await select_place(callback, user)
        elif path_args[1] == '2':
            await callback.delete()
            user.dialog = Account.Dialog.FIND_DEALER_ENTER_PLACE
            user.temp = ''
            user.save()
            await user.reply('Введите адрес вашего местоположения (Например: <i>"Москва, улица Волочаевская"</i>)')


@handler.message(name='', dialog=Account.Dialog.FIND_DEALER_ENTER_PLACE)
async def _(message, path_args, bot, user):
    longitude, latitude = yandex_geo.get_coords(message.text)
    if latitude and longitude:
        place = yandex_geo.get_address(longitude, latitude) 
        user.temp = place
        user.save()
        await user.reply(f'Давайте уточним ваше местоположение: <b>{place}</b>. Всё правильно?', keyboard=message.inline_keyboard([
                [message.inline_keyboard_button('Да', callback_data='find_dealer_place 1'), message.inline_keyboard_button('Нет', callback_data='find_dealer_place 2')]
            ]))
    else:
        await user.reply('Не удалось определить местоположение. Попробуйте изменить запрос.')


@handler.callback(name='find_dealer_select')
async def _(callback, path_args, bot, user):
    if len(path_args) == 2 and path_args[1].isdigit():
        # action = int(path_args[1])
        # if action == 1:     # Find dealers
        user.dialog = Account.Dialog.DEFAULT
        user.save()
        longitude, latitude = yandex_geo.get_coords(user.temp)
        dealers = Dealer.objects.raw('SELECT *, SQRT(POW(111 * (latitude - %s), 2) + POW(111 * (%s - longitude) * COS(latitude / 57.3), 2)) AS distance FROM app_dealer HAVING distance < 25 ORDER BY distance LIMIT 5' % (latitude, longitude))
        await callback.edit_text('Ближайшие к Вам официальные дилерские центры Nissan:', reply_markup=callback.inline_keyboard([
                [callback.inline_keyboard_button(f'{x.name} (~{math.ceil(x.distance)}км)', callback_data=f'show_find_dealer {x.id}')] for x in dealers
            ] + [[callback.inline_keyboard_button('⬅️ Главное меню', callback_data='menu'), callback.inline_keyboard_button('Изменить адрес', callback_data='find_dealer_place 2')]]))


@handler.callback(name='show_find_dealer')
async def _(callback, path_args, bot, user):
    if len(path_args) == 2 and path_args[1].isdigit():
        dealer = Dealer.objects.filter(id=path_args[1]).first()
        if dealer is not None:
            await callback.edit_text(f'{dealer.name}\n\n+{dealer.phone}\n<a href="https://maps.yandex.ru/?ll={dealer.longitude},{dealer.latitude}&z=15&pt={dealer.longitude},{dealer.latitude}">{dealer.full_address}</a>')

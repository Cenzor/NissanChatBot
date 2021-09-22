from app.models import Account, CarData, Car, Dealer, Service
from app.bot import handler
from app.bot.assets import yandex_geo
from datetime import datetime
import ujson, math, re


@handler.message(name=['сервис', 'запись на сервис', 'запись на то', 'ремонт авто', 'ремонт автомобиля', 'замена масла', 'слесарный ремонт', 'то', 'сервисные акции', 'кузовной ремонт', 'замена шин', 'установка дополнительного оборудования', 'ремонт', 'запасные части', 
'запасные части для негарантийного автомобиля', 'преимущество 3+'], dialog=Account.Dialog.DEFAULT)
async def _(message, path_args, bot, user):
    text = 'Вы выбрали «Записаться на сервисное обслуживание».\nЧтобы узнать о сервисах именно для вас, введите порядковый номер модели из списка:\n'
    for i, car in enumerate(CarData.objects.all()):
        text += f'\n{i + 1}) {car.name}'
    await user.reply(text)
    user.dialog = Account.Dialog.SERVICE_SIGNUP
    user.save()


@handler.callback(name='service_signup_start')
async def _(callback, path_args, bot, user):
    await callback.delete()
    text = 'Вы выбрали «Записаться на сервисное обслуживание».\nЧтобы узнать о сервисах именно для вас, введите порядковый номер модели из списка:\n'
    for i, car in enumerate(CarData.objects.all()):
        text += f'\n{i + 1}) {car.name}'
    await user.reply(text)
    user.dialog = Account.Dialog.SERVICE_SIGNUP
    user.save()


@handler.message(name='', dialog=Account.Dialog.SERVICE_SIGNUP)
async def _(message, path_args, bot, user):
    if message.text.isdigit():
        car_offset = int(message.text)
        cars = CarData.objects.all()
        if car_offset > 0 and car_offset <= cars.count():
            car = cars[car_offset - 1]
            await user.reply(f'Вы выбрали {car.name}. Укажите, пожалуйста, год первичной продажи автомобиля в формате ГГГГ. Например: 2019')
            user.dialog = Account.Dialog.SERVICE_SIGNUP_YEAR
            user.temp = ujson.dumps({'car': car.id})
            user.save()
        else:
            await user.reply('Не удалось распознать ваше сообщение. Ничего страшного! Проверьте все данные и попробуйте еще раз.')


@handler.message(name='', dialog=Account.Dialog.SERVICE_SIGNUP_YEAR)
async def _(message, path_args, bot, user):
    if message.text.isdigit():
        year = int(message.text)
        if year >= 1900 and year <= int(datetime.now().strftime('%Y')):
            data = ujson.loads(user.temp)
            car = CarData.objects.filter(id=data['car']).first()
            user.dialog = Account.Dialog.DEFAULT
            user.save()
            await user.reply(f'По моим данным, у вас {car.name}, год первичной продажи – {year}. Все верно?', keyboard=message.inline_keyboard([
                    [message.inline_keyboard_button('Да', callback_data=f'signup_service_year {car.id} {year}'), message.inline_keyboard_button('Нет', callback_data='service_signup_start')]
                ]))
        else:
            await user.reply('Не удалось распознать год первичной продажи. Ничего страшного! Проверьте все данные и попробуйте еще раз: введите дату первичной продажи вашего автомобиля в таком формате: ГГГГ')


@handler.callback(name='signup_service_year')
async def _(callback, path_args, bot, user):
    if len(path_args) == 3 and path_args[1].isdigit() and path_args[2].isdigit():
        car_id = int(path_args[1])
        year = int(path_args[2])
        user.temp = ujson.dumps({'car': car_id, 'year': year})
        user.save()
        car = CarData.objects.filter(id=car_id).first()
        await callback.edit_text('Отлично! Теперь выберите, пожалуйста, модификацию вашего автомобиля.', reply_markup=callback.inline_keyboard([
                [callback.inline_keyboard_button(key, callback_data=f'signup_service_version {key}')] for key in ujson.loads(car.versions).keys()
            ]))


@handler.callback(name='signup_service_version')
async def _(callback, path_args, bot, user):
    if len(path_args) >= 2:
        data = ujson.loads(user.temp)
        key = ' '.join(path_args[1:])
        data['version'] = key
        user.temp = ujson.dumps(data)
        user.dialog = Account.Dialog.SERVICE_SIGNUP_MILEAGE
        user.save()
        await callback.delete()
        await user.reply('Все ясно! Теперь необходимо ввести пробег вашего автомобиля Nissan в км в следующем формате: 50000')


@handler.message(name='', dialog=Account.Dialog.SERVICE_SIGNUP_MILEAGE)
async def _(message, path_args, bot, user):
    if message.text.isdigit():
        data = ujson.loads(user.temp)
        data['mileage'] = int(message.text)
        user.temp = ujson.dumps(data)
        user.dialog = Account.Dialog.DEFAULT
        user.save()
        await user.reply('Я уже собрал доступные для вас предложения, а еще — очень много обязательной юридической информации.\n\nНет, серьезно. Очень. Много. Информации. Смотрим?', keyboard=message.inline_keyboard([
                [message.inline_keyboard_button('Да', callback_data='signup_service_legal_info')]
            ]))


@handler.callback(name='signup_service_legal_info')
async def _(callback, path_args, bot, user):
    data = ujson.loads(user.temp)
    car = CarData.objects.filter(id=data['car']).first()
    modify = ujson.loads(car.versions)[data['version']]

    full_text = 'Спасибо, что согласились. Будь я живым человеком, мне было бы приятно!\nДля вас действуют следующие акции и предложения:\n'
    if int(datetime.now().strftime('%Y')) - data['year'] >= 3:
        if modify[0][0] != '-':
            full_text += f'\n• Запасные части «Преимущество 3+» включая замену для а/м старше 3-х лет (от {modify[0][0]} руб.)¹'
        full_text += f'\n• Комплексная проверка автомобиля - 999,00 руб.³\n• Ультразвуковая очистка кондиционера - {modify[2]} руб.⁴'
        if modify[2] != '-':
            full_text += f'\n• Масляный сервис для а/м старше 3-х лет - от {modify[2]} руб.⁵'
        full_text += f'\n\n¹ Цена предложения указана для автомобиля {car.name} (с двигателем {data["version"]}) {modify[0][1]} ({modify[0][2]}) {modify[0][0]} руб. (включая замену). Цена предложения зависит от устанавливаемой запасной части «Преимущество 3+», модели вашего автомобиля, мощности и объема двигателя и других технических параметров. Акция для владельцев постгарантийных автомобилей. Предложение действует с 01.07.2020 г. по 31.07.2020 г. Предложение ограничено. Не является публичной офертой. Подробную информацию об акции, дилерах-участниках узнавайте у вашего дилера или на сайте www.nissan.ru. Дилер имеет право устанавливать стоимость предложения ниже указанной рекомендованной максимальной цены. Итоговая стоимость предложения и все цены на запасные части, указанные в настоящем разделе, носят информационный характер, рекомендуются ООО «Ниссан Мэнуфэкчуринг Рус» как максимальная рекомендованная цена предложения и могут отличаться от действительных цен уполномоченных дилеров Nissan.\n\n² Цена предложения зависит от модели вашего автомобиля. Подробную информацию об акции, дилерах-участниках, стоимости предложения для других моделей автомобилей Nissan узнавайте у вашего дилера или на сайте www.nissan.ru. Не является публичной офертой. Акция для владельцев постгарантийных автомобилей. Предложение действует с 01.07.2020 г. по 31.07.2020 г. Предложение ограничено. Цены, указанные в настоящем разделе, носят информационный характер и могут отличаться от действительных цен уполномоченных дилеров Nissan. Указанные рекомендованные розничные цены являются максимальными. Дилер имеет право устанавливать стоимость предложения ниже указанной рекомендованной максимальной цены.\n\n³ В кампанию входит: проверка АКБ, проверка тормозной системы, проверка уровня технических жидкостей (моторное, трансмиссионное масло, тормозная жидкость, жидкость гидроусилителя руля), проверка плотности антифриза, диагностика ходовой части (не включает проверку углов установки колес), проверка ламп (фары, фонари и салонное освещение), проверка воздушного и салонного фильтров, техническая мойка. При прохождении кампании выдается cертификат программы помощи на дорогах Nissan Assistance (Ниссан Ассистанс) сроком на 1 год! Указана максимальная рекомендованная цена предложения, не зависит от модели, не включает стоимость расходных материалов. Дилер имеет право устанавливать стоимость предложения ниже указанной рекомендованной максимальной цены. Итоговая стоимость предложения и все цены на запасные части, указанные в настоящем разделе, носят информационный характер, рекомендуются ООО «Ниссан Мэнуфэкчуринг Рус» как максимальная рекомендованная цена предложения и могут отличаться от действительных цен уполномоченных дилеров Nissan. Подробную информацию об акции, дилерах-участниках узнавайте у вашего дилера или на сайте www.nissan.ru. Не является публичной офертой. Акция для владельцев постгарантийных автомобилей Nissan. Предложение действует с 06.04.2020 г. по 31.03.2021 г. Предложение ограничено.\n\n⁴ Указана максимальная рекомендованная цена предложения при ультразвуковой очистке при использовании запасных частей «Преимущество 3+» в рублях (вкл. НДС 20%) для постгарантийного автомобиля {car.name}. Цена предложения зависит от модели вашего автомобиля, гарантийный или постгарантийный ваш автомобиль, от выбранного комплекта: «Стандартная» или «Ультразвуковая» очистка. Дилер имеет право устанавливать стоимость предложения ниже указанной рекомендованной максимальной цены. Подробную информацию об акции, дилерах-участниках, стоимости предложения для других моделей автомобилей Nissan узнавайте у вашего дилера или на сайте www.nissan.ru. Не является публичной офертой. Предложение действует с 01.07.2020 по 31.07.2020. Предложение ограничено.\n\n⁵ Указана рекомендованная максимальная цена предложения для автомобиля {car.name} (с двигателем {data["version"]} при использовании запасных частей Преимущество 3+ и масла Преимущество 3+ . Цена зависит от точной модели вашего автомобиля, а также от выбранных запасных частей: оригинальные запасные части или оригинальные запасные части «Преимущество 3+». Подробную информацию об акции, дилерах-участниках, стоимости предложения для других моделей автомобилей Nissan узнавайте у вашего дилера или на сайте www.nissan.ru. Не является публичной офертой. Акция для владельцев постгарантийных автомобилей. Предложение действует с 01.07.2020 г. по 31.07.2020 г. Предложение ограничено. Дилер имеет право устанавливать стоимость предложения ниже указанной рекомендованной максимальной цены. Итоговая стоимость предложения и все цены на запасные части, указанные в настоящем разделе, носят информационный характер, рекомендуются ООО «Ниссан Мэнуфэкчуринг Рус» как максимальная рекомендованная цена предложения и могут отличаться от действительных цен уполномоченных дилеров Nissan.\n\n⁶ Детальную информацию вы можете уточнить у вашего официального дилера.'
    else:
        full_text += f'\n• Регулярное техническое обслуживание¹\n• Ультразвуковая очистка кондиционера - {modify[2]} руб.²'
        full_text += f'\n\n¹ Детальную информацию вы можете уточнить у вашего официального дилера.\n² Указана максимальная рекомендованная цена предложения при ультразвуковой очистке в рублях (вкл. НДС 20%) для автомобиля {car.name}. Цена предложения зависит от модели вашего автомобиля, гарантийный или постгарантийный ваш автомобиль, от выбранного комплекта: «Стандартная» или «Ультразвуковая» очистка. Дилер имеет право устанавливать стоимость предложения ниже указанной рекомендованной максимальной цены. Подробную информацию об акции, дилерах-участниках, стоимости предложения для других моделей автомобилей Nissan узнавайте у вашего дилера или на сайте www.nissan.ru. Не является публичной офертой. Предложение действует с 01.07.2020 по 31.07.2020. Предложение ограничено.'
  
    await callback.delete()

    if len(full_text) > 4000:
        for i, char in enumerate(full_text[4000:]):
            if char == ' ':
                await user.reply(full_text[:4000 + i])
                await user.reply(full_text[4000 + i:], keyboard=callback.inline_keyboard([[callback.inline_keyboard_button('Записаться', callback_data='signup_service_legal_go')]]))
                break
    else:
        await user.reply(full_text, keyboard=callback.inline_keyboard([[callback.inline_keyboard_button('Записаться', callback_data='signup_service_legal_go')]]))


@handler.callback(name='signup_service_legal_go')
async def _(callback, path_args, bot, user):
    await callback.delete()
    user.dialog = Account.Dialog.SERVICE_SIGNUP_ENTER_LOCATION
    user.save()
    await user.reply('Напоминаю, что все подробности об акциях и дилерах-участниках можно уточнить на nissan.ru и в салонах официальных дилеров.\n\nТеперь начнем запись! Напишите, пожалуйста, название города России, в котором вы хотите посетить дилера, или поделитесь своим местоположением.', keyboard=callback.reply_keyboard([
            [callback.reply_keyboard_button('Поделиться', request_location=True)]
        ]))


@handler.message(name='', dialog=Account.Dialog.SERVICE_SIGNUP_ENTER_LOCATION)
async def _(message, path_args, bot, user):
    if len(message.text) > 0:
        longitude, latitude = yandex_geo.get_coords(message.text)
        if latitude and longitude:
            place = yandex_geo.get_address(longitude, latitude) 
            data = ujson.loads(user.temp)
            data['place'] = place
            user.temp = ujson.dumps(data)
            user.save()
            await user.reply(f'Давайте уточним ваше местоположение: <b>{place}</b>. Всё правильно?', keyboard=message.inline_keyboard([
                    [message.inline_keyboard_button('Да', callback_data='signup_service_place 1'), message.inline_keyboard_button('Нет', callback_data='signup_service_place 2')]
                ]))
        else:
            await user.reply('Не удалось определить местоположение. Попробуйте изменить запрос.')
    else:
        if message.location is not None:
            place = yandex_geo.get_address(message.location.longitude, message.location.latitude)
            data = ujson.loads(user.temp)
            data['place'] = place
            user.temp = ujson.dumps(data)
            user.save()
            await user.reply(f'Давайте уточним ваше местоположение: <b>{place}</b>. Всё правильно?', keyboard=message.inline_keyboard([
                    [message.inline_keyboard_button('Да', callback_data='signup_service_place 1'), message.inline_keyboard_button('Нет', callback_data='signup_service_place 2')]
                ]))


@handler.callback(name='signup_service_place')
async def _(callback, path_args, bot, user):
    if len(path_args) == 2:
        if path_args[1] == '1':
            data = ujson.loads(user.temp)
            longitude, latitude = yandex_geo.get_coords(data['place'])
            dealers = Dealer.objects.raw('SELECT *, SQRT(POW(111 * (latitude - %s), 2) + POW(111 * (%s - longitude) * COS(latitude / 57.3), 2)) AS distance FROM app_dealer HAVING distance < 25 ORDER BY distance LIMIT 5' % (latitude, longitude))
            await callback.edit_text(f'Вы выбрали {data["place"]}. С помощью кнопок выберите дилерский центр, который хотите посетить.', reply_markup=callback.inline_keyboard([
                    [callback.inline_keyboard_button(f'{x.name} (~{math.ceil(x.distance)}км)', callback_data=f'signup_dealer_select {x.id}')] for x in dealers
                ]))
        elif path_args[1] == '2':
            await callback.delete()
            user.dialog = Account.Dialog.SERVICE_SIGNUP_ENTER_LOCATION
            user.save()
            await user.reply('Напишите, пожалуйста, название города России, в котором вы хотите посетить дилера, или поделитесь своим местоположением.', keyboard=callback.reply_keyboard([
                    [callback.reply_keyboard_button('Поделиться', request_location=True)]
                ]))


@handler.callback(name='signup_dealer_select')
async def _(callback, path_args, bot, user):
    if len(path_args) == 2 and path_args[1].isdigit():
        dealer = Dealer.objects.filter(id=path_args[1]).first()
        if dealer is not None:
            data = ujson.loads(user.temp)
            data['dealer'] = path_args[1]
            user.temp = ujson.dumps(data)
            user.dialog = Account.Dialog.DEFAULT
            user.save()
            await callback.edit_text(f'Отлично! Вы выбрали ДЦ «{dealer.name}». С помощью кнопок выберите интересующие вас услуги.', reply_markup=callback.inline_keyboard([
                    [callback.inline_keyboard_button(x.name, callback_data=f'signup_dealer_services {x.id}')] for x in Service.objects.all()
                ]))


@handler.callback(name='signup_dealer_services')
async def _(callback, path_args, bot, user):
    if len(path_args) == 2 and path_args[1].isdigit():
        service =  Service.objects.filter(id=path_args[1]).first()
        if service is not None:
            data = ujson.loads(user.temp)
            dealer = Dealer.objects.filter(id=data['dealer']).first()
            if 'services' not in data:
                data['services'] = []
            if service.id not in data['services']:
                data['services'].append(service.id)
            else:
                data['services'].remove(service.id)
            user.temp = ujson.dumps(data)
            user.save()

            keyboard = [
                    [callback.inline_keyboard_button(('✅ ' if x.id in data['services'] else '') + x.name, callback_data=f'signup_dealer_services {x.id}')] for x in Service.objects.all()
                ]
            if len(data['services']) > 0:
                keyboard.append([callback.inline_keyboard_button('Выход', callback_data='menu'), callback.inline_keyboard_button('Далее', callback_data='signup_dealer_complete')])

            await callback.edit_text(f'Отлично! Вы выбрали ДЦ «{dealer.name}». С помощью кнопок выберите интересующие вас услуги.', reply_markup=callback.inline_keyboard(keyboard))


@handler.callback(name='signup_dealer_complete')
async def _(callback, path_args, bot, user):
    data = ujson.loads(user.temp)
    await callback.edit_text('Отлично! С помощью кнопок выберите интересующие вас услуги.\n' + '\n'.join(['✅ ' + x.name for x in Service.objects.all() if x.id in data['services']]))
    if 7 in data['services']:
        user.dialog = Account.Dialog.SERVICE_SIGNUP_OTHER_SERVICES
        user.save()
        await user.reply('Вы выбрали пункт «Другие услуги». Пожалуйста, уточните сообщением, какие именно услуги вас интересуют.')
    else:
        user.dialog = Account.Dialog.SERVICE_SIGNUP_NAME
        user.save()
        await user.reply('Отлично, осталось несколько простых шагов. Напишите, пожалуйста, ваши реальные имя и фамилию. Например, так: Иван Иванов.')


@handler.message(name='', dialog=Account.Dialog.SERVICE_SIGNUP_OTHER_SERVICES)
async def _(message, path_args, bot, user):
    data = ujson.loads(user.temp)
    data['other_services'] = message.text
    user.temp = ujson.dumps(data)
    user.dialog = Account.Dialog.SERVICE_SIGNUP_NAME
    user.save()
    await user.reply('Отлично, осталось несколько простых шагов. Напишите, пожалуйста, ваши реальные имя и фамилию. Например, так: Иван Иванов.')


@handler.message(name='', dialog=Account.Dialog.SERVICE_SIGNUP_NAME)
async def _(message, path_args, bot, user):
    data = ujson.loads(user.temp)
    data['full_name'] = message.text
    user.temp = ujson.dumps(data)
    user.dialog = Account.Dialog.SERVICE_SIGNUP_VIN
    user.save()
    await user.reply('Отлично! Укажите, пожалуйста, Ваш VIN-номер или пришлите его фотографию.')


@handler.message(name='', dialog=Account.Dialog.SERVICE_SIGNUP_VIN)
async def _(message, path_args, bot, user):
    if re.search(r'^(\w{17})$', message.text):
        data = ujson.loads(user.temp)
        data['vin'] = message.text
        user.temp = ujson.dumps(data)
        user.dialog = Account.Dialog.SERVICE_SIGNUP_PHONE
        user.save()
        await user.reply(f'Вы указали VIN – {message.text}, спасибо! Теперь сообщите номер своего телефона в таком формате: 79991234567')
    else:
        await user.reply('Не удалось определить ваш VIN номер. Попробуйте указать его ещё раз.')


@handler.message(name='', dialog=Account.Dialog.SERVICE_SIGNUP_PHONE)
async def _(message, path_args, bot, user):
    if re.search(r'^7\d{10}$', message.text):
        data = ujson.loads(user.temp)
        data['phone'] = message.text
        user.temp = ujson.dumps(data)
        user.dialog = Account.Dialog.SERVICE_SIGNUP_EMAIL
        user.save()
        await user.reply('Еще немного! Поделитесь своей электронной почтой? Так мы сможем выслать письмо с подтверждением вашей записи.')
    else:
        await user.reply('Извините, не могу распознать ваш номер телефона. Убедитесь, что написали его в правильном формате и попробуйте еще раз.')


@handler.message(name='', dialog=Account.Dialog.SERVICE_SIGNUP_EMAIL)
async def _(message, path_args, bot, user):
    if re.search(r'^.+@.+\..+$', message.text):
        data = ujson.loads(user.temp)
        data['email'] = message.text
        user.temp = ujson.dumps(data)
        user.dialog = Account.Dialog.SERVICE_SIGNUP_VISIT_DATE
        user.save()
        await user.reply('Записали ваш e-mail, спасибо! Осталось совсем немного! Сообщите удобную дату визита в таком формате:\nДД.ММ.ГГГГ\n\nНапример, так:\n08.09.2019')
    else:
        await user.reply('Извините, не могу распознать ваш E-mail. Убедитесь, что написали его в правильном формате и попробуйте еще раз.')


@handler.message(name='', dialog=Account.Dialog.SERVICE_SIGNUP_VISIT_DATE)
async def _(message, path_args, bot, user):
    try:
        visit_date = datetime.strptime(message.text, '%d.%m.%Y')
    except:
        return await user.reply('У меня не получилось распознать удобную для вас дату. Попробуйте сообщить еще раз в таком формате:\nДД.ММ.ГГГГ\n\nНапример, так:\n08.09.2019')
    
    days_offset = (visit_date - datetime.now()).days
    if days_offset >= 1:
        if days_offset <= 90:
            data = ujson.loads(user.temp)
            data['visit_date'] = message.text
            user.temp = ujson.dumps(data)
            user.dialog = Account.Dialog.SERVICE_SIGNUP_VISIT_TIME
            user.save()
            await user.reply('Отлично! Осталось совсем немного! Сообщите удобное время визита в таком формате:\nЧЧ:ММ\n\nНапример, так:\n14:30')
        else:
            await user.reply('Планируемая дата визита не может быть позже, чем на 3 месяца вперёд. Попробуйте сообщить еще раз в таком формате:\nДД.ММ.ГГГГ\n\nНапример, так:\n08.09.2019')
    else:
        await user.reply('Планируемая дата визита должна быть не ранее завтрашнего дня. Попробуйте сообщить еще раз в таком формате:\nДД.ММ.ГГГГ\n\nНапример, так:\n08.09.2019')


@handler.message(name='', dialog=Account.Dialog.SERVICE_SIGNUP_VISIT_TIME)
async def _(message, path_args, bot, user):
    try:
        visit_time = datetime.strptime(message.text, '%H:%M')
    except:
        return await user.reply('У меня не получилось распознать удобное для вас время.\nПопробуйте сообщить его еще раз в таком формате:\nЧЧ:ММ\n\nНапример, так:\n14:30')
    
    data = ujson.loads(user.temp)
    data['visit_time'] = message.text
    user.temp = ujson.dumps(data)
    user.dialog = Account.Dialog.SERVICE_SIGNUP_COMMENT
    user.save()
    await user.reply('Если у вас есть дополнительные комментарии, пожелания или просьбы к дилеру, пожалуйста, напишите их в сообщении, либо нажмите на кнопку «Без комментария».', keyboard=message.reply_keyboard([
            [message.reply_keyboard_button('Без комментария')]
        ]))


@handler.message(name='', dialog=Account.Dialog.SERVICE_SIGNUP_COMMENT)
async def _(message, path_args, bot, user):
    data = ujson.loads(user.temp)
    data['comment'] = message.text if message.text.lower() != 'без комментария' else None
    car = CarData.objects.filter(id=data['car']).first()
    dealer = Dealer.objects.filter(id=data['dealer']).first()

    ticket_text = f'\n• Автомобиль: {car.name} ({data["version"]})'
    ticket_text += f'\n• Год первичной продажи: {data["year"]}'
    ticket_text += f'\n• VIN: {data["vin"]}'
    ticket_text += f'\n• Пробег: {data["mileage"]} км.'
    ticket_text += f'\n• Город: {dealer.city}'
    ticket_text += f'\n• Дилерский центр: {dealer.name}'
    ticket_text += f'\n• Услуги:' + ('\n'.join([f'⠀⠀{x.name}' for x in Service.objects.all() if x.id in data['services']]))
    ticket_text += f'\n• Имя и фамилия: {data["full_name"]}'
    ticket_text += f'\n• Телефон: {data["phone"]}'
    ticket_text += f'\n• E-Mail: {data["email"]}'
    ticket_text += f'\n• Дата и время визита: {data["visit_date"]} {data["visit_time"]}'
    ticket_text += f'\n• Ваш комментарий: {data["comment"] or "отсутствует"}'
    if 'other_services' in data:
        ticket_text += f'\nДругие услуги: {data["other_services"]}'

    await user.reply('Готово! Предлагаю еще раз проверить детали вашего визита.\n' + ticket_text, keyboard=message.inline_keyboard([
            [message.inline_keyboard_button('Отправить', callback_data='service_signup_send')],
            [message.inline_keyboard_button('Заново', callback_data='service_signup_start')],
            [message.inline_keyboard_button('В главное меню', callback_data='menu')],
        ]))


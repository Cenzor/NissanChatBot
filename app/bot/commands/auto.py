from datetime import datetime
import calendar
from vkbottle.tools import PhotoMessageUploader
from app.models import Account, Car
from app.bot import handler
from constance import config
import ujson, requests, base64


def end_of_month():
	date = datetime.now()
	rg = calendar.monthrange(date.year, date.month)
	return f'{rg[1]}.{date.strftime("%m.%Y")}'


@handler.message(name='автомобили', dialog=Account.Dialog.DEFAULT)
async def _(message, path_args, bot, user):
	keyboard = [[]]
	for car in Car.objects.filter(disabled=False).all():
		if len(keyboard[-1]) == 2:
			keyboard.append([])
		keyboard[-1].append(message.inline_keyboard_button(car.name, callback_data=f'show_car {car.id}'))
	keyboard.append([message.inline_keyboard_button('⬅️ Вернуться в главное меню', callback_data='menu')])
	await user.reply(f'{user.first_name}, я выведу список моделей, а Вы, выбрав желаемую, сможете получить о ней детальную информацию.')
	await user.reply('Список моделей:', keyboard=message.inline_keyboard(keyboard))


@handler.callback(name='show_car', only_to=['telegram', 'vk'])
async def _(callback, path_args, bot, user):
	print(type(callback))
	if len(path_args) == 2 and path_args[1].isdigit():
		car = Car.objects.filter(id=path_args[1]).first()
		if car is not None:
			versions = ujson.loads(car.versions)
			# await callback.delete()
			await user.reply(f'Вы выбрали: <b>{car.name}</b>\n\nЦена от* {car.min_price} руб.', keyboard=callback.inline_keyboard([
					[callback.inline_keyboard_button(v['name'], callback_data=f'show_car_version {car.id} {i}')] for i, v in enumerate(versions)
				]))
			await user.reply('Узнать больше:', keyboard=callback.inline_keyboard([
					[callback.inline_keyboard_button('Заказать тест-драйв', callback_data=f'test_drive {car.id}')],
					[callback.inline_keyboard_button('Заявка на кредит он-лайн', url=config.CREDIT_ONLINE_URL)],
				]))
			await user.reply(f'<i>*Рекомендованная розничная цена на автомобили {car.brand} {car.name} с учетом всех действующих специальных предложений, включая специальные предложения для клиентов-участников «В кругу Nissan». Подробнее на сайте www.nissan.ru и у официальных дилеров. Предложение ограничено и действует до {end_of_month()}. Не является офертой.</i>', keyboard=callback.inline_keyboard([
					[callback.inline_keyboard_button('⬅️ Вернуться в главное меню', callback_data='menu')]
				]))


@handler.callback(name='show_car', only_to=['facebook'])
async def _(callback, path_args, bot, user):
	if len(path_args) == 2 and path_args[1].isdigit():
		car = Car.objects.filter(id=path_args[1]).first()
		if car is not None:
			versions = ujson.loads(car.versions)
			# await callback.delete()
			await user.reply(f'Вы выбрали: <b>{car.name}</b>\n\nЦена от* {car.min_price} руб.')
			await user.reply('Узнать больше:')
			await user.reply(f'<i>*Рекомендованная розничная цена на автомобили {car.brand} {car.name} с учетом всех действующих специальных предложений, включая специальные предложения для клиентов-участников «В кругу Nissan». Подробнее на сайте www.nissan.ru и у официальных дилеров. Предложение ограничено и действует до {end_of_month()}. Не является офертой.</i>', keyboard=callback.inline_keyboard([
					[callback.inline_keyboard_button(v['name'], callback_data=f'show_car_version {car.id} {i}')] for i, v in enumerate(versions)
				] + [
					[callback.inline_keyboard_button('Заказать тест-драйв', callback_data=f'test_drive {car.id}')],
					[callback.inline_keyboard_button('Заявка на кредит он-лайн', url=config.CREDIT_ONLINE_URL)],
					[callback.inline_keyboard_button('⬅️ Вернуться в главное меню', callback_data='menu')]
				]))


@handler.callback(name='show_car_version', only_to=['telegram'])
async def _(callback, path_args, bot, user):
	if len(path_args) == 3 and path_args[1].isdigit() and path_args[2].isdigit():
		car = Car.objects.filter(id=path_args[1]).first()
		if car is not None:
			v_id = int(path_args[2])
			versions = ujson.loads(car.versions)
			version = versions[v_id] if v_id >= 0 and v_id < len(versions) else None
			if version is not None:
				# await callback.delete()
				await user.reply(f'Вы выбрали: <b>{car.name}</b>\n\nЦена от* {car.min_price} руб.')
				await user.reply(f'<i>*Рекомендованная розничная цена на автомобили {car.brand} {car.name} с учетом всех действующих специальных предложений, включая специальные предложения для клиентов-участников «В кругу Nissan». Подробнее на сайте www.nissan.ru и у официальных дилеров. Предложение ограничено и действует до {end_of_month()}. Не является офертой.</i>\n\n<a href="https://nissanvd.ru/images/model/{car.photo}">Фото</a>', keyboard=callback.inline_keyboard([
					[callback.inline_keyboard_button('Заказать тест-драйв', callback_data=f'test_drive {car.id}')],
					[callback.inline_keyboard_button('⬅️ Вернуться в главное меню', callback_data='menu')]
				]))


@handler.callback(name='show_car_version', only_to=['vk'])
async def _(callback, path_args, bot, user):
	if len(path_args) == 3 and path_args[1].isdigit() and path_args[2].isdigit():
		car = Car.objects.filter(id=path_args[1]).first()
		if car is not None:
			v_id = int(path_args[2])
			versions = ujson.loads(car.versions)
			version = versions[v_id] if v_id >= 0 and v_id < len(versions) else None
			if version is not None:
				photo_data = requests.get(f'https://nissanvd.ru/images/model/{car.photo}')
				# photo_base64 = base64.b64encode(photo_data.content)
				photo = await PhotoMessageUploader(bot.api).upload(photo_data.content) # base64.decodestring(photo_base64))
				await user.reply(text='Фото', attachment=photo)
				await user.reply(f'Вы выбрали: <b>{car.name}</b>\n\nЦена от* {car.min_price} руб.')
				await user.reply(f'<i>*Рекомендованная розничная цена на автомобили {car.brand} {car.name} с учетом всех действующих специальных предложений, включая специальные предложения для клиентов-участников «В кругу Nissan». Подробнее на сайте www.nissan.ru и у официальных дилеров. Предложение ограничено и действует до {end_of_month()}. Не является офертой.</i>', keyboard=callback.inline_keyboard([
					[callback.inline_keyboard_button('Заказать тест-драйв', callback_data=f'test_drive {car.id}')],
					[callback.inline_keyboard_button('⬅️ Вернуться в главное меню', callback_data='menu')]
				]))


@handler.callback(name='show_car_version', only_to=['facebook'])
async def _(callback, path_args, bot, user):
	if len(path_args) == 3 and path_args[1].isdigit() and path_args[2].isdigit():
		car = Car.objects.filter(id=path_args[1]).first()
		if car is not None:
			v_id = int(path_args[2])
			versions = ujson.loads(car.versions)
			version = versions[v_id] if v_id >= 0 and v_id < len(versions) else None
			if version is not None:
				# photo_data = requests.get(f'https://nissanvd.ru/images/model/{car.photo}')
				# photo_base64 = base64.b64encode(photo_data.content)
				# photo = await PhotoMessageUploader(bot.api).upload(photo_data.content) # base64.decodestring(photo_base64))
				# await user.reply(text='Фото', attachment=photo)
				bot.send_image_url(recipient_id=user.id, image_url=f'https://nissanvd.ru/images/model/{car.photo}')
				await user.reply(f'Вы выбрали: <b>{car.name}</b>\n\nЦена от* {car.min_price} руб.')
				await user.reply(f'<i>*Рекомендованная розничная цена на автомобили {car.brand} {car.name} с учетом всех действующих специальных предложений, включая специальные предложения для клиентов-участников «В кругу Nissan». Подробнее на сайте www.nissan.ru и у официальных дилеров. Предложение ограничено и действует до {end_of_month()}. Не является офертой.</i>', keyboard=callback.inline_keyboard([
					[callback.inline_keyboard_button('Заказать тест-драйв', callback_data=f'test_drive {car.id}')],
					[callback.inline_keyboard_button('⬅️ Вернуться в главное меню', callback_data='menu')]
				]))

from app.bot import handler
from app.models import Account
from constance import config


@handler.message(name='вместе с nissan', dialog=Account.Dialog.DEFAULT)
async def _(message, path_args, bot, user):
    await user.reply('На протяжении многих лет мы совершенствуем свои автомобили и сервисы, чтобы владение Nissan оставалось простым, удобным и выгодным. Чтобы Вам было проще ориентироваться во всем многообразии услуг и сервисов, которыми Вы можете воспользоваться, мы объединили их в три главных преимущества: Выгодно, Надежно и Интересно.', keyboard=message.inline_keyboard([
            [message.inline_keyboard_button('Вместе Надежно', callback_data='with_nissan 1')],
            [message.inline_keyboard_button('Вместе Выгодно', callback_data='with_nissan 2')],
            [message.inline_keyboard_button('Вместе Интересно', callback_data='with_nissan 3')],
            [message.inline_keyboard_button('⬆️ Главное Меню', callback_data='menu')]
        ]))


@handler.callback(name='with_nissan_start')
async def _(callback, path_args, bot, user):
    await callback.edit_text('На протяжении многих лет мы совершенствуем свои автомобили и сервисы, чтобы владение Nissan оставалось простым, удобным и выгодным. Чтобы Вам было проще ориентироваться во всем многообразии услуг и сервисов, которыми Вы можете воспользоваться, мы объединили их в три главных преимущества: Выгодно, Надежно и Интересно.', reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('Вместе Надежно', callback_data='with_nissan 1')],
            [callback.inline_keyboard_button('Вместе Выгодно', callback_data='with_nissan 2')],
            [callback.inline_keyboard_button('Вместе Интересно', callback_data='with_nissan 3')],
            [callback.inline_keyboard_button('⬆️ Главное Меню', callback_data='menu')]
        ]))


@handler.callback(name='with_nissan')
async def _(callback, path_args, bot, user):
    if len(path_args) == 2 and path_args[1].isdigit():
        advantage = int(path_args[1])
        if advantage == 1:
            await callback.edit_text('Мы заботимся о наших клиентах и нам важно, чтобы владение автомобилем было для Вас необременительным и приятным. \nВ разделе "Вместе Надежно" Вы сможете узнать больше о:\n- программе постгарантийного обслуживания Nissan Service 3+, \n- службе помощи на дорогах Nissan Assistance.\nА так же:\n- найти информацию об аксессуарах для Вашего автомобиля,\n- записаться на сервис онлайн,\n- запомнить место, где Вы припарковали Ваш автомобиль.', reply_markup=callback.inline_keyboard([
                    [callback.inline_keyboard_button('Nissan Service 3+', callback_data='get_special 1 with_nissan 1')],
                    [callback.inline_keyboard_button('Nissan Assistance', callback_data='get_special 3 with_nissan 1')],
                    [callback.inline_keyboard_button('Запись на сервис', callback_data='service_signup_start')],
                    [callback.inline_keyboard_button('Где я припарковался?', callback_data='parking')],
                    [callback.inline_keyboard_button('⬅️ Назад', callback_data='with_nissan_start')],
                    [callback.inline_keyboard_button('⬆️ Главное меню', callback_data='menu')]
                ]))
        elif advantage == 2:
            await callback.edit_text('Финансовые услуги и специальные сервисы помогут Вам сократить расходы на эксплуатацию автомобиля, сохраняя при этом неизменно высокое качество сервиса. \nВ разделе "Вместе выгодно" Вы можете:\n- узнать цены на Сервисный Контракт , \n- получить информацию о кредитных программах,\n- ознакомиться с программами страхования.\nВыбор за Вами!', reply_markup=callback.inline_keyboard([
                    [callback.inline_keyboard_button('Сервисный контракт', callback_data='get_special 2')],
                    # [callback.inline_keyboard_button('В кругу Nissan', callback_data='nissan_square')],
                    [callback.inline_keyboard_button('Nissan Finance', callback_data='nissan_finance')],
                    [callback.inline_keyboard_button('⬅️ Назад', callback_data='with_nissan_start')],
                    [callback.inline_keyboard_button('⬆️ Главное меню', callback_data='menu')]
                ]))
        elif advantage == 3:
            await callback.edit_text('Nissan – это не только надежные и комфортные автомобили, но и пропуск в мир захватывающих эмоций. Не верите?\nЗдесь Вы можете:\n- записаться на тест-драйв, \n- зарядиться от партнерства Nissan с футбольными клубами,\n- погрузиться в принципы и правила Nissan,\n- ознакомиться с концепцией Nissan Intelligent Mobility,\n- быть в курсе последних событий и достижений Nissan.', reply_markup=callback.inline_keyboard([
                    [callback.inline_keyboard_button('Заказать тест-драйв', callback_data='test_drive_start')],
                    [callback.inline_keyboard_button('Nissan и футбол', callback_data='nissan_football')],
                    [callback.inline_keyboard_button('Правила Nissan', callback_data='nissan_rules')],
                    [callback.inline_keyboard_button('Nissan Intelligent Mobility', callback_data='nissan_intelligent_mobility')],
                    [callback.inline_keyboard_button('События', callback_data='nissan_events')],
                    [callback.inline_keyboard_button('Достижения', callback_data='nissan_achievements')],
                    [callback.inline_keyboard_button('Концепт кары', callback_data='nissan_concept')],
                    [callback.inline_keyboard_button('Nissan в соцсетях', callback_data='nissan_social')],
                    [callback.inline_keyboard_button('⬅️ Назад', callback_data='with_nissan_start')],
                    [callback.inline_keyboard_button('⬆️ Главное меню', callback_data='menu')]
                ]))


@handler.callback(name='nissan_football')
async def _(callback, path_args, bot, user):
    await callback.edit_text('Nissan – официальный партнер лиги чемпионов УЕФА и легендарных футбольных российских клубов «Зенит» и «Спартак-Москва».\n\nИ мы знаем, что именно болельщики делают игру незабываемой.\n\nУзнайте больше об амбассадорах Nissan и детской академии футбола.', reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('Узнать больше на сайте', url=config.FOOTBALL_URL)],
            [callback.inline_keyboard_button('⬅️ Назад', callback_data='with_nissan 3')],
            [callback.inline_keyboard_button('⬆️ Главное меню', callback_data='menu')]
        ]))


@handler.callback(name='nissan_rules')
async def _(callback, path_args, bot, user):
    await callback.edit_text('Вот уже более 80 лет Nissan стремится быть эталоном качества и профессионализма в производстве и обслуживании автомобилей, предлагая инновационные технологии, высокие стандарты сервиса и стараясь, чтобы мир Nissan стал неотъемлемой и приятной частью Вашей жизни.\n\nДля достижения этих задач Nissan неукоснительно соблюдает ряд принципов и правил, позволивших изменить сам подход к созданию автомобилей и выработать философию, в центре которой – человек и его потребности.', reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('Узнать больше на сайте', url=config.RULES_URL)],
            [callback.inline_keyboard_button('⬅️ Назад', callback_data='with_nissan 3')],
            [callback.inline_keyboard_button('⬆️ Главное меню', callback_data='menu')]
        ]))


@handler.callback(name='nissan_intelligent_mobility')
async def _(callback, path_args, bot, user):
    await callback.edit_text('Концепция Intelligent Mobility, принятая в Nissan, ставит своей целью раскрыть максимальный потенциал каждого из нас и охватывает три области инноваций: \n- систему питания автомобиля, позволяющую минимизировать выбросы и использовать только чистую энергию; \n- повышение уровня безопасности автомобилей через использование технологий «умного» автономного вождения; \n- интеграцию систем автомобиля в общество. \nТолько подумайте: Ваш автомобиль, высадив водителя и пассажиров, паркуется самостоятельно, а дорожное полотно заряжает Ваш электромобиль, пока вы в пути — и это лишь простейший пример того, как улучшится наша жизнь в ближайшем будущем. Двигайтесь вперед и достигайте большего вместе с Nissan!', reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('Узнать больше на сайте', url=config.INTELLIGENT_MOBILITY_URL)],
            [callback.inline_keyboard_button('⬅️ Назад', callback_data='with_nissan 3')],
            [callback.inline_keyboard_button('⬆️ Главное меню', callback_data='menu')]
        ]))


@handler.callback(name='nissan_events')
async def _(callback, path_args, bot, user):
    await callback.edit_text('Узнайте больше о последних событиях в мире Nissan, вступайте в наши сообщества в социальных сетях и будьте на связи.', reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('Узнать больше на сайте', url=config.EVENTS_URL)],
            [callback.inline_keyboard_button('Nissan в соцсетях', callback_data='nissan_social')],
            [callback.inline_keyboard_button('⬅️ Назад', callback_data='with_nissan 3')],
            [callback.inline_keyboard_button('⬆️ Главное меню', callback_data='menu')]
        ]))


@handler.callback(name='nissan_social')
async def _(callback, path_args, bot, user):
    await callback.edit_text('Вместе с Nissan.', reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('Facebook', url=config.FACEBOOK_URL)],
            [callback.inline_keyboard_button('Twitter', url=config.TWITTER_URL)],
            [callback.inline_keyboard_button('Youtube', url=config.YOUTUBE_URL)],
            [callback.inline_keyboard_button('VK', url=config.VK_URL)],
            [callback.inline_keyboard_button('Одноклассники', url=config.OK_URL)],
            [callback.inline_keyboard_button('Instagram', url=config.INSTAGRAM_URL)],
            [callback.inline_keyboard_button('⬅️ Назад', callback_data='with_nissan 3')],
            [callback.inline_keyboard_button('⬆️ Главное меню', callback_data='menu')]
        ]))


@handler.callback(name='nissan_achievements')
async def _(callback, path_args, bot, user):
    await callback.edit_text('Стремление компании Nissan постоянно совершенствовать характеристики своих автомобилей сполна отражается в нашем увлечении автоспортом.\n\nГоночные автомобили Nismo автоспортивного подразделения Nissan заслужили одобрение своих водителей и уважение соперников во всем мире.', reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('Узнать больше на сайте', url=config.PERF_URL)],
            [callback.inline_keyboard_button('⬅️ Назад', callback_data='with_nissan 3')],
            [callback.inline_keyboard_button('⬆️ Главное меню', callback_data='menu')]
        ]))


@handler.callback(name='nissan_concept')
async def _(callback, path_args, bot, user):
    await callback.edit_text('Технологии Nissan созданы совершенствовать взаимодействие между водителем и автомобилем, в котором последний выступает в качестве близкого и надежного партнера, способного обеспечить более безопасное, удобное и приятное передвижение.', reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('Узнать больше на сайте', url=config.CONCEPT_CARS_URL)],
            [callback.inline_keyboard_button('⬅️ Назад', callback_data='with_nissan 3')],
            [callback.inline_keyboard_button('⬆️ Главное меню', callback_data='menu')]
        ]))


@handler.callback(name='nissan_square')
async def _(callback, path_args, bot, user):
    await callback.edit_text('Я не знаю ответ на этот вопрос', reply_markup=callback.inline_keyboard([[callback.inline_keyboard_button('Назад', callback_data='with_nissan 2')]]))


@handler.callback(name='nissan_finance')
async def _(callback, path_args, bot, user):
    await callback.edit_text('Nissan Finance:', reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('Заявка на кредит он-лайн', url=config.CREDIT_ONLINE_URL)],
            [callback.inline_keyboard_button('⬅️ Назад', callback_data='with_nissan 2')],
            [callback.inline_keyboard_button('⬆️ Главное меню', callback_data='menu')]
        ]))

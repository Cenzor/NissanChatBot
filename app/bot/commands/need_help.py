from app.bot import handler
from app.models import Account


@handler.message(name='мне нужна помощь', dialog=Account.Dialog.DEFAULT)
async def _(message, path_args, bot, user):
    await user.reply('Мы всегда готовы помочь. Обратитесь в центр обслуживания клиентов Nissan. Наши специалисты ответят на все Ваши вопросы и окажут необходимую помощь.\n+7-800-200-59-90 (звонок бесплатный)\nили 8-495-587-99-11 для связи со Службой помощи на дорогах Nissan Assistance из-за рубежа', keyboard=message.inline_keyboard([[message.inline_keyboard_button('Перейти в основное меню', callback_data='menu')]]))

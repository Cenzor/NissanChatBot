from app.models import Account, Feedback
from app.bot import handler


@handler.message(name='обратная связь')
async def _(message, path_args, bot, user):
    await user.reply(f'{user.first_name}, Вы можете связаться с нашими специалистами.')
    await user.reply('Что Вы хотите сообщить?', keyboard=message.inline_keyboard([
            [message.inline_keyboard_button('Проблемы в работе Бота', callback_data='feedback bug')],
            [message.inline_keyboard_button('Пожелания к работе Бота', callback_data='feedback wish')],
            [message.inline_keyboard_button('⬅️ Вернуться в главное меню', callback_data='menu')],
        ]))


@handler.callback(name='feedback')
async def _(callback, path_args, bot, user):
    if len(path_args) == 2:
        keyboard = callback.inline_keyboard([[callback.inline_keyboard_button('⬅️ Вернуться в главное меню', callback_data='menu')]])
        await callback.delete()
        if path_args[1] == 'bug':
            user.dialog = Account.Dialog.USER_FEEDBACK_BUG
            await user.reply(f'{user.first_name}, нашли ошибку? Опишите ее здесь!', keyboard=keyboard)
        elif path_args[1] == 'wish':
            user.dialog = Account.Dialog.USER_FEEDBACK_WISH
            await user.reply(f'{user.first_name}, здесь вы можете оставить свои впечатления и предложения по работе Бота.', keyboard=keyboard)
        user.save()


@handler.message(name='', dialog=Account.Dialog.USER_FEEDBACK_BUG)
async def _(message, path_args, bot, user):
    feedback = Feedback(text=message.text, type=Feedback.Type.BUG)
    if message.class_name == 'tg':
        feedback.user_tg = user
    elif message.class_name == 'vk':
        feedback.user_vk = user
    elif message.class_name == 'fb':
        feedback.user_fb = user
    feedback.save()
    user.dialog = Account.Dialog.DEFAULT
    user.save()
    await user.reply(f'Спасибо, {user.first_name}! В ближайшее время мы изучим ошибку и устраним её.', keyboard=message.inline_keyboard([[message.inline_keyboard_button('⬅️ Вернуться в главное меню', callback_data='menu')]]))


@handler.message(name='', dialog=Account.Dialog.USER_FEEDBACK_WISH)
async def _(message, path_args, bot, user):
    feedback = Feedback(text=message.text, type=Feedback.Type.WISH)
    if message.class_name == 'tg':
        feedback.user_tg = user
    elif message.class_name == 'vk':
        feedback.user_vk = user
    elif message.class_name == 'fb':
        feedback.user_fb = user
    feedback.save()
    user.dialog = Account.Dialog.DEFAULT
    user.save()
    await user.reply(f'Спасибо за обратную связь! Ваши отзывы помогают нам постоянно совершенствовать нашего Бота и делать его умнее и удобнее.', keyboard=message.inline_keyboard([[message.inline_keyboard_button('⬅️ Вернуться в главное меню', callback_data='menu')]]))

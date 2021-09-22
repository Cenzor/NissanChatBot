import logging
from app.bot import handler
from constance import config
from app.models import Account


logger = logging.getLogger('main_logger')


@handler.message(name='wizzard', dialog=Account.Dialog.DEFAULT)
async def _(message, path_args, bot, user):
    logger.debug(f"callback wizzard, path_args: {path_args}")
    await user.reply('ыы:', disable_web_page_preview=True, keyboard=message.inline_keyboard([
            [message.inline_keyboard_button('Ы', callback_data='xyz')],
            [message.inline_keyboard_button('branch_url', url=config.BRANCH_URL)],
            [message.inline_keyboard_button('⬅️ Главное меню', callback_data='menu')],
        ]))


@handler.callback(name='xyz')
async def _(callback, path_args, bot, user):
    await callback.edit_text('XYZ:', disable_web_page_preview=True, reply_markup=callback.inline_keyboard([
            [callback.inline_keyboard_button('⬅️ Главное меню', callback_data='menu')]
        ]))
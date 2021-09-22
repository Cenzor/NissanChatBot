from app.bot import handler


@handler.callback(name='menu')
async def _(callback, path_args, bot, user):
    await callback.delete()
    await user.return_menu()

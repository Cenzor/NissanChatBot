from app.bot import handler


@handler.callback(name='view_url')
async def _(callback, path_args, bot, user):
    if len(path_args) == 2:
        await user.reply(path_args[1])

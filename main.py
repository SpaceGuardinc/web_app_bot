import asyncio
import logging
import os
from middlewares.database import DataBaseSession
from handlers.admin_private import admin_private_router
from dotenv import (find_dotenv,
                    load_dotenv)
from aiogram import (Bot,
                     Dispatcher)
#
# from database.engine import (drop_db,
#                              session_maker,
#                              create_db)
from database.engine import Database

# раскомитить на сервере когда опишем все хендлеры, чтобы не нагружать сервак
# ALLOWED_UPDATES = ["message, "
#                   "edited_message",
#                   "callback_query"]

bot = Bot(token=os.getenv("API_TOKEN"))
dp = Dispatcher()  # fsm_strategy=FSMStrategy.USER_IN_CHAT
database = Database()
load_dotenv(find_dotenv())


# async def on_startup(bot):
#     run_param = False
#     if run_param:
#         await database.drop_db()
#
#     await database.create_db()
#
#
# async def on_shutdown(bot):
#     print('бот лег')


async def main():
    #  await bot.delete_webhook(drop_pending_updates=True)  # раскомитить на серве чтобы не нагружать его
    dp.update.middleware(DataBaseSession(session_pool=database.session_maker))
    # dp.startup.register(on_startup)
    # dp.shutdown.register(on_shutdown)
    dp.include_router(admin_private_router)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

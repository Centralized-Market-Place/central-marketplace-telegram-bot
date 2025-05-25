import asyncio
import logging

import httpx
from aiogram import Bot, Dispatcher, types
from config import settings

# --- Import your routers ---
from handlers.categories import router as categories_router
from handlers.channels   import router as channels_router
from handlers.products   import router as products_router
from handlers.comments   import router as comments_router
from handlers.bookmarks  import router as bookmarks_router
from handlers.misc       import router as misc_router
import state_store

state_store.init_db()


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s:%(lineno)d – %(message)s"
)

async def global_error_handler(update: types.Update, **kwargs) -> bool:
    exception = kwargs.get("exception")
    if isinstance(exception, (httpx.ConnectError, httpx.ReadTimeout)):
        if update.message:
            chat_id = update.message.chat.id
            bot = update.message.bot
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id
            bot = update.callback_query.bot
        else:
            return False

        await bot.send_message(
            chat_id,
            "⚠️ Sorry, I can’t reach the server right now. Please try again soon."
        )
        return True

    return False

async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp  = Dispatcher()

    dp.include_router(categories_router)
    dp.include_router(channels_router)
    dp.include_router(products_router)
    dp.include_router(comments_router)
    dp.include_router(bookmarks_router)
    dp.include_router(misc_router)

    dp.errors.register(global_error_handler)

    print(f"Starting bot @{settings.BOT_USERNAME}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

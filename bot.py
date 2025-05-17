import asyncio
from aiogram import Bot, Dispatcher
from config import settings
from handlers.categories import router as categories_router
from handlers.channels import router as channels_router
from handlers.products import router as products_router
from handlers.comments import router as comments_router
from handlers.misc import router as misc_router
from handlers.paginations import router as filter_router    
from handlers.bookmarks import router as bookmarks_router
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s:%(lineno)d – %(message)s"
)

async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Include all routers
    dp.include_router(categories_router)
    dp.include_router(channels_router)
    dp.include_router(products_router)
    dp.include_router(comments_router)
    dp.include_router(bookmarks_router)
    dp.include_router(misc_router)
    dp.include_router(filter_router)

    print(f"Starting bot @{settings.BOT_USERNAME}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
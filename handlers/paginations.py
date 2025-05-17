from aiogram import Router, types
from aiogram.filters.command import Command, CommandObject
from client import ApiClient
from aiogram.types import CallbackQuery
from handlers.callback_data import ProductsPage
from aiogram import Bot
from handlers.categories import send_products_page

router = Router()

@router.callback_query(ProductsPage.filter())
async def on_page(query: CallbackQuery, callback_data: ProductsPage, bot: Bot):
    """Move to the requested page."""
    await query.answer()
    await send_products_page(
        bot, query.message,
        callback_data.category,
        callback_data.page
    )

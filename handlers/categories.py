from aiogram import Router, types
from aiogram.filters.command import Command
from handlers.callback_data import FilterCategory
from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helpers import send_products_page

router = Router()
CATEGORIES = ["technology", "mobile", "fashion"]

@router.message(Command("filter"))
async def cmd_filter(message: types.Message):
    """Start filtering by showing category buttons."""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=cat.title(),
                    callback_data=FilterCategory(category=cat).pack()
                )
            ] for cat in CATEGORIES
        ]
    )
    await message.reply("Select a category:", reply_markup=kb)

@router.callback_query(FilterCategory.filter())
async def on_filter(query: CallbackQuery, callback_data: FilterCategory, bot: Bot):
    """
    Fired when a category button is tapped.
    Starts at page=1.
    """
    await query.answer()  # removes loading spinner
    # Send page 1 of the chosen category
    await send_products_page(bot, query.message, callback_data.category, page=1)

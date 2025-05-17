from aiogram import Router, types
from aiogram.filters.command import Command, CommandObject
from client import ApiClient
from aiogram.types import CallbackQuery
from handlers.callback_data import ProductsPage
from aiogram import Bot

# Supported categories
CATEGORIES = ["technology", "mobile", "fashion"]

router = Router()

@router.message(Command("products"))
async def cmd_products(
    message: types.Message,
    command: CommandObject,
):
    # parse arguments as before…
    raw_args = command.args or ""
    parts   = raw_args.split()
    page    = 1
    category = None
    query    = None

    # (your existing arg-parsing logic here) …
    api  = ApiClient(message.from_user.id)
    data = await api.list_products(page=page, category=category, query=query)
    items = data.get("items", [])

    if not items:
        return await message.reply(f"No products found on page {page}.")

    # send each product separately
    for p in items:
        # pick image or placeholder
        imgs = p.get("images") or []
        img_url = imgs[0] if imgs else "https://via.placeholder.com/300x200?text=No+Image"

        name  = p.get("name") or "<no name>"
        price = p.get("price")
        price_str = f"${price}" if price is not None else "N/A"

        desc = (p.get("description") or "").strip()
        caption = (
            f"*{name}*\n"
            f"Price: {price_str}\n"
            f"{desc}"
        )
        await message.answer_photo(photo=img_url, caption=caption, parse_mode="Markdown")
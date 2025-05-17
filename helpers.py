from aiogram.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from client import ApiClient
from aiogram import types, Bot
from handlers.callback_data import ProductsPage

async def send_products_page(
    bot: Bot,
    message: types.Message,
    category: str,
    page: int
):
    api = ApiClient(message.from_user.id)
    data = await api.list_products(page=page, category=category)
    items = data.get("items", [])

    if not items:
        return await message.reply(f"No products in {category} page {page}.")

    # Send each product as its own photo+caption
    for p in items:
        img = (p.get("images") or ["https://via.placeholder.com/300"])[0]
        name  = p.get("name") or "<no name>"
        price = p.get("price")
        price_str = f"${price}" if price is not None else "N/A"
        desc = (p.get("description") or "").strip()

        caption = (
            f"*{name}*\n"
            f"Price: {price_str}\n"
            f"{desc}"
        )
        await message.answer_photo(img, caption=caption, parse_mode="Markdown")

    # Build Prev/Next buttons
    kb = InlineKeyboardMarkup(row_width=3)
    if page > 1:
        kb.insert(InlineKeyboardButton(
            text="⬅ Prev",
            callback_data=ProductsPage(category=category, page=page-1).pack()
        ))
    kb.insert(InlineKeyboardButton(
        text=f"Page {page}",
        callback_data="noop"  # dummy, does nothing
    ))
    # Assume page size of 10
    if len(items) >= 10:
        kb.insert(InlineKeyboardButton(
            text="Next ➡",
            callback_data=ProductsPage(category=category, page=page+1).pack()
        ))

    await message.reply("Navigate:", reply_markup=kb)

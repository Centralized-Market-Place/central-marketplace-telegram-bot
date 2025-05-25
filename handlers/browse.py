# handlers/browse.py
from aiogram import Router, types
from aiogram.filters.callback_data import CallbackQueryFilter
# from handlers.callback_data import CategorySelect, PageAction
from client import ApiClient
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram import Bot

router = Router()

async def send_page(bot: Bot, msg: types.Message, what: str, category: str, page: int):
    """Fetch & send one page of items, then show Prev/Next buttons."""
    # api = ApiClient(msg.from_user.id)
    async with ApiClient(msg.from_user.id) as api:

        if what == "products":
            data = await api.list_products(page=page, category=category)
        else:
            data = await api.list_channels(page=page, category=category)

        items = data.get("items", [])
        if not items:
            return await msg.answer(f"No {what} in {category} page {page}.")

        # send each item as photo + caption
        for p in items:
            if what == "products":
                img = (p.get("images") or ["https://via.placeholder.com/300"])[0]
                title = p.get("name") or "<no name>"
                subtitle = f"Price: ${p.get('price','N/A')}"
                desc = p.get("description","")
            else:
                img = p.get("thumbnail_url") or "https://via.placeholder.com/300"
                title = p.get("title") or "<no title>"
                subtitle = f"{p.get('participants',0)} members"
                desc = p.get("description","")
            caption = f"*{title}*\n{subtitle}\n{desc}"
            await msg.answer_photo(img, caption=caption, parse_mode="Markdown")

        # pagination buttons
        kb = InlineKeyboardMarkup(row_width=3)
        if page > 1:
            kb.insert(InlineKeyboardButton("⬅ Prev",
                callback_data=PageAction(what=what, category=category, page=page-1).pack()
            ))
        kb.insert(InlineKeyboardButton(f"Page {page}", callback_data="noop"))
        if len(items) >= data.get("page_size",10):
            kb.insert(InlineKeyboardButton("Next ➡",
                callback_data=PageAction(what=what, category=category, page=page+1).pack()
            ))
        await msg.answer("Navigate:", reply_markup=kb)

# 4) Category taps
@router.callback_query(CategorySelect.filter())
async def on_category(query: types.CallbackQuery, data: CategorySelect, bot: Bot):
    await query.answer()
    await send_page(bot, query.message, data.what, data.category, page=1)

# 5) Pagination taps
@router.callback_query(PageAction.filter())
async def on_page(query: types.CallbackQuery, data: PageAction, bot: Bot):
    await query.answer()
    await send_page(bot, query.message, data.what, data.category, data.page)

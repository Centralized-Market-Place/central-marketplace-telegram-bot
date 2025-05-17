from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from client import ApiClient

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    main_menu = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Products"), KeyboardButton(text="📺 Channels")],
            [KeyboardButton(text="⭐ My Bookmarks"), KeyboardButton(text="💬 Help")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await message.answer(
        "Welcome! Choose an action:",
        reply_markup=main_menu
    )

@router.message(lambda m: m.text in ["🛍 Products", "📺 Channels"])
async def cmd_show_categories(message: types.Message):
    key = "products" if message.text.startswith("🛍") else "channels"
    title = "product" if key == "products" else "channel"
    cats = ["technology", "mobile", "fashion"]

    # **Here we include the `keyboard=` field**
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=cat.title())] for cat in cats
        ] + [
            [KeyboardButton(text=f"🔎 Search {title.title()}")],
            [KeyboardButton(text="◀️ Back to Main Menu")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(f"Select a {title} category:", reply_markup=kb)

@router.message(lambda m: m.text and m.text.lower() in ["technology","mobile","fashion"])
async def cmd_category_selected(message: types.Message):
    category = message.text.lower()
    await _send_page(message, what="products", category=category, page=1)

@router.message(lambda m: m.text and m.text.startswith("🔎"))
async def cmd_search_prompt(message: types.Message):
    # e.g. “🔎 Search Product”
    what = "products" if "Product" in message.text else "channels"
    # send a plain keyboard remove so they can type
    await message.answer("Type your search query:", reply_markup=ReplyKeyboardRemove())
    # And set up FSM/state to capture next message as search term...
async def _send_page(message: types.Message, what: str, category: str, page: int):
    api   = ApiClient(message.from_user.id)
    data  = await (api.list_products if what=="products" else api.list_channels)(
                page=page, category=category
            )
    items = data.get("items", [])

    # Render each item (swap to answer_photo + caption if you like)
    for p in items:
        title = p.get("name") or p.get("title") or "<no name>"
        await message.answer(f"{title} (ID: {p['id']})")

    # Build pagination + back keyboard
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    row = []
    if page > 1:
        row.append( KeyboardButton(text="⬅ Prev") )
    row.append( KeyboardButton(text=str(page)) )
    if len(items) >= data.get("page_size",10):
        row.append( KeyboardButton(text="Next ➡") )
    kb.row(*row)
    kb.add( KeyboardButton(text="◀️ Back to Categories") )
    await message.answer(
        f"{what.title()} in {category.title()} — page {page}",
        reply_markup=kb
    )

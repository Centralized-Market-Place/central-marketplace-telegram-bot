from aiogram import Router, types
from aiogram.filters.command import Command, CommandObject
from client import ApiClient
from handlers.channels import cmd_channels
from constants import PRICE_RANGES
from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from client import ApiClient
import logging
import re
# from aiogram.utils.markdown import quote
logger = logging.getLogger(__name__)
from aiogram.types import ReplyKeyboardRemove
from state_store import save_state, load_state, clear_state

router = Router()




def nav_kb(kind: str) -> ReplyKeyboardMarkup:
    cats = ["technology", "accessories", "shoes", "clothes"]
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=cat.title())] for cat in cats
        ] + [
            [KeyboardButton(text="⬅️ Prev"), KeyboardButton(text="Next ➡️")],
            [KeyboardButton(text=f"🔎 Search {kind.title()}")],
            [KeyboardButton(text="◀️ Back to Main Menu")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return kb

@router.message(lambda m: m.text in ["🛍 Products", "📺 Channels"])
async def cmd_show_categories(message: types.Message):
    key = "products" if message.text.startswith("🛍") else "channels"
    save_state(message.from_user.id, {
        "what": key,
        "category": None,
        "page": 1,
        "query": None,
        "searching": False,
        "min_price": None,
        "max_price": None
    })
    cats = ["technology", "accessories", "shoes", "clothes"]
    kb = types.ReplyKeyboardMarkup(
        keyboard=
            [[types.KeyboardButton(text=cat.title())] for cat in cats]
          + [[types.KeyboardButton(text="⬅️ Prev"), types.KeyboardButton(text="Next ➡️")]]
          + [[types.KeyboardButton(text=f"🔎 Search {key.title()}")]]
          + [[types.KeyboardButton(text=f"💰 Filter by Price")]]
          + [[types.KeyboardButton(text="◀️ Back to Main Menu")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(f"Select a {key[:-1]} category:", reply_markup=kb)

@router.message(lambda m: m.text == "💰 Filter by Price")
async def cmd_show_price_ranges(message: types.Message):
    state = load_state(message.from_user.id)
    state["searching"] = False
    # state["query"] = None
    save_state(message.from_user.id, state)
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=price["label"])] for price in PRICE_RANGES
        ] + [[types.KeyboardButton(text="⬅️ Prev"), types.KeyboardButton(text="Next ➡️")]]
        + [[types.KeyboardButton(text="◀️ Back to Main Menu")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Filter by price range:", reply_markup=kb)

@router.message(lambda m: m.text == "📺 Channels")
async def launch_channels_via_button(message: types.Message):
    cmd = CommandObject(command="channels", args="")
    await cmd_channels(message, cmd)

@router.message(lambda m: m.text in ["⬅️ Prev", "Next ➡️"])
async def cmd_paginate(message: types.Message):
    state = load_state(message.from_user.id)
    if not state:
        return await message.answer("Choose Products or Channels first with 🛍 / 📺.")
    if message.text == "⬅️ Prev":
        state["page"] = max(1, state["page"] - 1)
    else:
        state["page"] += 1
    save_state(message.from_user.id, state)
    return await _list_products_or_channels(message, state["what"], state["page"], state["category"])

async def _list_products_or_channels(message: types.Message, kind: str, page: int, category: str = None, price_range:  dict = None):
    api = ApiClient(message.from_user.id)
    async with api:
        data = None
        try:
            if kind == "products":
                data = await api.list_products(page=page, category=category, price_range=price_range)
            else:
                data = await api.list_channels(page=page, category=category)
        except Exception as exc:
            logger.error("❌ Error while fetching %s: %s", kind, repr(exc))
            return await message.answer(f"An error occurred while fetching {kind}. Please try again later.")
    items = data.get("items", [])
    if not items:
        return await message.answer(f"No {kind} found on page {page}.")

    await _send_page(message, kind, category, page)

    cats = ["technology", "accessories", "shoes", "clothes"]
    kb = types.ReplyKeyboardMarkup(
        keyboard=
            [[types.KeyboardButton(text=cat.title())] for cat in cats]
          + [[types.KeyboardButton(text="⬅️ Prev"), types.KeyboardButton(text="Next ➡️")]]
          + [[types.KeyboardButton(text=f"🔎 Search {kind.title()}")]]
          + [[types.KeyboardButton(text="◀️ Back to Main Menu")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    clear_state(message.from_user.id)
    main_menu = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Products"), KeyboardButton(text="📺 Channels")],
            [ KeyboardButton(text="💬 Help")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await message.answer(
        "Welcome! Choose an action:",
        reply_markup=main_menu
    )

@router.message(lambda msg: msg.text == "💬 Help")
async def handle_help(message: types.Message):
    await message.answer(
        "For more information, please check our website: [Centralized Marketplace](https://www.centeralmarketplace.systems)",
        parse_mode="Markdown"
    )

@router.message(lambda m: m.text == "◀️ Back to Main Menu")
async def cmd_back_to_main(message: types.Message):
    await cmd_start(message)

@router.message(lambda m: m.text and m.text.lower() in ["technology", "accessories", "shoes", "clothes"])
async def cmd_category_selected(message: types.Message):
    category = message.text.lower()
    state = load_state(message.from_user.id)
    state["category"] = category
    state["page"]     = 1
    state["searching"] = False
    state["query"] = None
    save_state(message.from_user.id, state)

    await _list_products_or_channels(
      message,
      kind=state["what"], 
      page=1,
      category=category
    )

@router.message(lambda m: m.text and m.text.startswith("🔎"))
async def cmd_search_trigger(message: types.Message):
    state = load_state(message.from_user.id)
    if not state:
        await message.answer("Please select 🛍 or 📺 first.")
        return
    state["searching"] = True
    save_state(message.from_user.id, state)
    await message.answer("Please type your search keyword:")

@router.message(lambda m: load_state(m.from_user.id,).get("searching", False))
async def cmd_search_input(message: types.Message):
    state = load_state(message.from_user.id)
    state["query"] = message.text.strip()
    state["page"] = 1
    # state["searching"] = False
    save_state(message.from_user.id, state)
    await _send_page(message, what=state["what"], category=state.get("category"), page=state["page"])
    
@router.message(lambda m: m.text and any(p["label"] == m.text for p in PRICE_RANGES))
async def cmd_price_filter_selected(message: types.Message):
    selected = next(p for p in PRICE_RANGES if p["label"] == message.text)
    state = load_state(message.from_user.id)
    state["min_price"] = selected["min"]
    state["max_price"] = selected["max"]
    state["page"] = 1
    save_state(message.from_user.id, state)
    # await _list_products_or_channels(
    #     message,
    #     kind=state["what"],
    #     page=1,
    #     category=state["category"],
    #     price_range={"min_price": selected["min"], "max_price": selected["max"]}
    # )
    await _send_page(
        message,
        what=state["what"],
        category=state["category"],
        page=1,
        price_range={"min_price": selected["min"], "max_price": selected["max"]}
    )

async def _send_page(message: types.Message, what: str, category: str, page: int, price_range: dict = None):
    state = load_state(message.from_user.id)
    api = ApiClient(message.from_user.id)
    logger.debug
    got_one = False
    item_vals = 0
    try:
        async with api:
            data = None
            if what == "products":
                if price_range is None:
                    price_range = {"min_price": state.get("min_price"), "max_price": state.get("max_price")}
                data = await api.list_products(
                    page=page,
                    category=category,
                    query=state.get("query"),
                    price_range=price_range
                )
            else:
                data = await api.list_channels(
                    page=page,
                    category=category,
                    query=state.get("query")
                )
            items = data.get("items", [])
            if not items:
                text = f"No {what} found"
                if state.get("query"):
                    text += f" for '{state['query']}'"
                text += f" on page {state['page']}."
                await message.answer(text)
                return
            got_one = True
            item_vals = len(items)
            for item in items:
                if what == "products":
                    channel_name = item.get("channel", {}).get("username", "")
                    link = f"https://t.me/{channel_name}/{item.get('message_id')}" if channel_name else ""
                    images = item.get("images", [])
                    url = images[0] if images else "https://res.cloudinary.com/dpfl0ikdj/image/upload/v1750256371/cart_cnftt3.jpg"
                    description = (item.get("description") or "").strip()
                    if len(description) > 800:
                        description = description[:800] + "..."
                    price = item.get("price")
                    if price is None:
                        price = "Not Described"
                    else :
                        price = f"${price} BIRR"
                    raw = f"*{item.get('title','<no name>')}*\n\nPrice: {price}\n{description}"
                    if link:
                        raw += f"\n\n[🔗 View Product]({link})"
                    
                    caption = escape_md_v2(raw)
                    await message.answer_photo(photo=url, caption=caption, parse_mode="MarkdownV2")
                else:
                    url = item.get("thumbnail_url") or "https://via.placeholder.com/300x200"
                    username = item.get("username")
                    link = f"https://t.me/{username}" if username else "N/A"
                    raw = f"*{item.get('title', '<no title>')}*\n{(item.get('description') or '')[:100]}...\n[🔗 Join Channel]({link})"
                    caption = escape_md_v2(raw)
                    await message.answer_photo(photo=url, caption=raw, parse_mode="MarkdownV2")
            save_state(message.from_user.id, state)
            total_pages = (data.get("total", 100) + 9) // 10 
            await message.answer(f"{what} – page {page}/{total_pages}")

    except Exception as exc:
        logger.error("❌ Error while sending page: %s", item_vals)
        logger.exception("Error while sending page: %s", repr(exc))
        if not item_vals:
            await message.answer("An error occurred while getting data. Please try again later.")

def escape_md_v2(text: str) -> str:
    return re.sub(r'([_\*\[\]\(\)~`>#+\-=\|{}.!])', r"\\\1", text)

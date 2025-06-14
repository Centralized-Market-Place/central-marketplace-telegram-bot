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
logger = logging.getLogger(__name__)
from aiogram.types import ReplyKeyboardRemove
from state_store import save_state, load_state, clear_state

router = Router()




def nav_kb(kind: str) -> ReplyKeyboardMarkup:
    cats = ["technology", "mobile", "fashion"]
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    for cat in cats:
        kb.add(KeyboardButton(cat.title()))
    kb.row(KeyboardButton("⬅️ Prev"), KeyboardButton("Next ➡️"))
    kb.add(KeyboardButton(f"🔎 Search {kind.title()}"))
    kb.add(KeyboardButton("◀️ Back to Main Menu"))
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
    cats = ["technology", "mobile", "fashion"]
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
        if kind == "products":
            data = await api.list_products(page=page, category=category, price_range=price_range)
        else:
            data = await api.list_channels(page=page, category=category)

    items = data.get("items", [])
    if not items:
        return await message.answer(f"No {kind} found on page {page}.")

    await _send_page(message, kind, category, page)

    cats = ["technology", "mobile", "fashion"]
    kb = types.ReplyKeyboardMarkup(
        keyboard=
            [[types.KeyboardButton(text=cat.title())] for cat in cats]
          + [[types.KeyboardButton(text="⬅️ Prev"), types.KeyboardButton(text="Next ➡️")]]
          + [[types.KeyboardButton(text=f"🔎 Search {kind.title()}")]]
          + [[types.KeyboardButton(text="◀️ Back to Main Menu")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(f"{kind.title()} – page {page}/{data.get('total_pages', '?')}", reply_markup=kb)

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    clear_state(message.from_user.id)
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

@router.message(lambda m: m.text == "◀️ Back to Main Menu")
async def cmd_back_to_main(message: types.Message):
    await cmd_start(message)

@router.message(lambda m: m.text and m.text.lower() in ["technology","mobile","fashion"])
async def cmd_category_selected(message: types.Message):
    category = message.text.lower()
    state = load_state(message.from_user.id)
    state["category"] = category
    state["page"]     = 1
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
    state["searching"] = False
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
    async with api:
        data = None
        if what == "products":
            if price_range is None:
                price_range = {"min_price": state.get("min_price"), "max_price": state.get("max_price")}
                # print("dddddddddddddddddddddddddddddddddddddddddddddddddddd", price_range)
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
        for item in items:
            if what == "products":
                url = item.get("images", [None])[0] or "https://via.placeholder.com/300x200"
                raw = f"*{item.get('name','<no name>')}*\nPrice: ${item.get('price') or 'N/A'}\n{(item.get('description') or '').strip()}"
                caption = escape_md_v2(raw)
                await message.answer_photo(photo=url, caption=caption, parse_mode="MarkdownV2")
            else:
                url = item.get("thumbnail_url") or "https://via.placeholder.com/300x200"
                raw = f"*{item.get('title','<no title>')}*\n{(item.get('description') or '')[:100]}...\n[🔗 Join Channel]({item.get('username') and f'https://t.me/{item['username']}' or 'N/A'})"
                # caption = escape_md_v2(raw)
                await message.answer_photo(photo=url, caption=raw, parse_mode="Markdown")
        save_state(message.from_user.id, state)

        await message.answer(f"{what.title()} – page {state['page']}/{data.get('total_pages','?')}", reply_markup=nav_kb(what))

def escape_md_v2(text: str) -> str:
    return re.sub(r'([_\*\[\]\(\)~`>#+\-=\|{}.!])', r"\\\1", text)

from aiogram import Router, types
from aiogram.filters.command import Command, CommandObject
from client import ApiClient
from aiogram.types import CallbackQuery
from handlers.callback_data import ProductsPage
import logging
import re

logger = logging.getLogger(__name__)

# Supported categories
CATEGORIES = ["technology", "mobile", "fashion"]

router = Router()

def escape_md_v2(text: str) -> str:
    return re.sub(r'([_\*\[\]\(\)~`>#+\-=\|{}.!])', r"\\\1", text)

@router.message(Command("products"))
async def cmd_products(
    message: types.Message,
    command: CommandObject,
):
    raw_args = command.args or ""
    parts = raw_args.split()
    page = 1
    category = None
    query = None

    # (your existing arg-parsing logic here)...

    api = ApiClient(message.from_user.id)
    async with api:
        try:
            data = await api.list_products(page=page, category=category, query=query)
            items = data.get("items", [])

            if not items:
                return await message.reply(f"No products found on page {page}.")

            for p in items:
                imgs = p.get("images") or []
                img_url = imgs[0] if imgs else "https://via.placeholder.com/300x200?text=No+Image"

                logger.debug(
                    "Product %s: %s, price: %s",
                    p.get("id"), p.get("name"), p.get("price")
                )
                name = p.get("name") or "<no name>"
                price = p.get("price")
                price_str = f"${price}" if price is not None else "N/A"

                desc = (p.get("description") or "").strip()
                raw_caption = f"*{name}*\nPrice: {price_str}\n{desc}"
                caption = escape_md_v2(raw_caption)

                await message.answer_photo(
                    photo=img_url,
                    caption=caption,
                    parse_mode="MarkdownV2"
                )
        except Exception as e:
            logger.error(
                "Failed to load products", exc_info=e
            )
            await message.answer("⚠️ Failed to load products: please try again later.")
            return

from aiogram import Router, types
from aiogram.filters.command import Command, CommandObject
from client import ApiClient

router = Router()

@router.message(Command("channels"))
async def cmd_channels(
    message: types.Message,
    command: CommandObject,    # injected parsed command
):
    raw_args = command.args or ""
    parts   = raw_args.split()
    page    = 1
    category = None

    # parse arguments: /channels [category|page] [page]
    if len(parts) == 1:
        if parts[0].isdigit():
            page = int(parts[0])
        else:
            category = parts[0]
    elif len(parts) >= 2:
        first, second = parts[0], parts[1]
        if first.isdigit():
            page = int(first)
            category = second
        else:
            category = first
            if second.isdigit():
                page = int(second)

    api  = ApiClient(message.from_user.id)
    data = await api.list_channels(page=page, category=category)
    items = data.get("items", [])

    if not items:
        return await message.reply(f"No channels found on page {page}.")

    for c in items:
        # Title
        title = c.get("title") or "<no title>"

        # Truncated description
        full_desc = (c.get("description") or "").strip()
        if len(full_desc) > 100:
            desc = full_desc[:97] + "..."
        else:
            desc = full_desc

        # Thumbnail URL (or placeholder)
        thumb = c.get("thumbnail_url") or \
                "https://via.placeholder.com/300x200?text=No+Image"

        # Telegram link
        username = c.get("username")
        link = f"https://t.me/{username}" if username else "N/A"

        # Build caption with Markdown
        caption = (
            f"*{title}*\n"
            f"{desc}\n\n"
            f"[🔗 Join Channel]({link})"
        )

        # Send one message per channel
        await message.answer_photo(
            photo=thumb,
            caption=caption,
            parse_mode="Markdown"
        )

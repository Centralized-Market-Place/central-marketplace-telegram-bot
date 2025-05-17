from aiogram import Router, types
from aiogram.filters import Command
from client import ApiClient

router = Router()

@router.message(Command("comment"))
async def cmd_comment(message: types.Message):
    parts = message.get_args().split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply("Usage: /comment <product_id> <text>")
    pid, text = parts
    api = ApiClient(message.from_user.id)
    comment = await api.post_comment(pid, text)
    await message.reply(f"Comment posted: {comment.get('id')}")
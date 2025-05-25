from aiogram import Router, types
from aiogram.filters import Command
from client import ApiClient

router = Router()

@router.message(Command("bookmark"))
async def cmd_bookmark(message: types.Message):
    pid = message.get_args().strip()
    async with ApiClient(message.from_user.id) as api:
        bm = await api.add_bookmark(pid)
        await message.reply(f"Bookmarked product {bm.get('product_id')}")

@router.message(Command("unbookmark"))
async def cmd_unbookmark(message: types.Message):
    pid = message.get_args().strip()
    # api = ApiClient(message.from_user.id)
    async with ApiClient(message.from_user.id) as api:
        await api.remove_bookmark(pid)
    await message.reply(f"Removed bookmark for {pid}")

@router.message(Command("mybookmarks"))
async def cmd_mybookmarks(message: types.Message):
    page = 1
    if message.get_args().isdigit():
        page = int(message.get_args())
    # api = ApiClient(message.from_user.id)
    async with ApiClient(message.from_user.id) as api:
        data = await api.list_bookmarks(page=page)
        items = data.get("items", [])
        text = "Your bookmarks:\n" + "\n".join(
            f"{b['product']['id']}: {b['product']['name']}" for b in items
        )
        await message.reply(text)
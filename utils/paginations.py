from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from handlers.callback_data import page_cb

def build_pagination(current: int, total: int) -> InlineKeyboardMarkup:
    """
    Builds ◀️ current/total ▶️ inline keyboard.
    action="goto" for real buttons, "noop" for disabled.
    """
    kb = InlineKeyboardMarkup(row_width=3)

    if current > 1:
        kb.insert(InlineKeyboardButton("⬅️", callback_data=page_cb.new(page=current-1, action="goto")))
    else:
        kb.insert(InlineKeyboardButton("⬅️", callback_data=page_cb.new(page=1, action="noop")))

    kb.insert(InlineKeyboardButton(f"{current}/{total}", callback_data=page_cb.new(page=current, action="noop")))

    if current < total:
        kb.insert(InlineKeyboardButton("➡️", callback_data=page_cb.new(page=current+1, action="goto")))
    else:
        kb.insert(InlineKeyboardButton("➡️", callback_data=page_cb.new(page=total, action="noop")))

    return kb

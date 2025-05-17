# handlers/callbacks.py
from aiogram.filters.callback_data import CallbackData

class MainMenu(CallbackData, prefix="main"):
    key: str  # "products", "channels", "bookmarks", "help"

class CategorySelect(CallbackData, prefix="cat"):
    what: str    # "products" or "channels"
    category: str

class SearchAction(CallbackData, prefix="search"):
    what: str   # "products" or "channels"

class PageAction(CallbackData, prefix="page"):
    what: str   # "products" or "channels"
    category: str
    page: int

class FilterCategory(CallbackData, prefix="filter"):
    """Emitted when a user picks a category."""
    category: str

class ProductsPage(CallbackData, prefix="page"):
    """Handles pagination for a given category."""
    category: str
    page: int

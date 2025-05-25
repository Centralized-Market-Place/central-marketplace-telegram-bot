# state_store.py
import sqlite3
import threading
from typing import Optional, Dict, Any

_DB_PATH = "user_state.sqlite3"
_LOCK = threading.Lock()

def _get_connection():
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create the user_state table if it doesn’t exist."""
    with _LOCK:
        conn = _get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_state (
                user_id     INTEGER PRIMARY KEY,
                what        TEXT,
                category    TEXT,
                page        INTEGER,
                query       TEXT,
                searching   INTEGER    -- 0 or 1
            )
        """)
        conn.commit()
        conn.close()

def save_state(user_id: int, state: Dict[str, Any]) -> None:
    """
    Insert or update the state for a given user.
    `state` keys: what, category, page, query, searching.
    """
    with _LOCK:
        conn = _get_connection()
        conn.execute("""
            INSERT INTO user_state(user_id, what, category, page, query, searching)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                what      = excluded.what,
                category  = excluded.category,
                page      = excluded.page,
                query     = excluded.query,
                searching = excluded.searching
        """, (
            user_id,
            state.get("what"),
            state.get("category"),
            state.get("page"),
            state.get("query"),
            1 if state.get("searching") else 0
        ))
        conn.commit()
        conn.close()

def load_state(user_id: int) -> Optional[Dict[str, Any]]:
    """Return the saved state for a user, or None if not found."""
    with _LOCK:
        conn = _get_connection()
        cur = conn.execute("SELECT * FROM user_state WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
    if not row:
        return None
    return {
        "what":       row["what"],
        "category":   row["category"],
        "page":       row["page"],
        "query":      row["query"],
        "searching":  bool(row["searching"]),
    }

def clear_state(user_id: int) -> None:
    """Delete a user’s saved state (e.g. on /start)."""
    with _LOCK:
        conn = _get_connection()
        conn.execute("DELETE FROM user_state WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

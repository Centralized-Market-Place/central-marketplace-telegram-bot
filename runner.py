import asyncio
import signal
import sys
from watchgod import awatch

async def watch_and_run():
    proc = None

    async def start_bot():
        nonlocal proc
        await asyncio.sleep(0.2)
        proc = await asyncio.create_subprocess_exec(sys.executable, "bot.py")
        print(f"Bot started (pid={proc.pid})")

    async def restart_bot():
        nonlocal proc
        if proc:
            proc.send_signal(signal.SIGINT)
            await proc.wait()
            print(f"Bot (pid={proc.pid}) exited, code={proc.returncode}")
            await asyncio.sleep(1)
        await start_bot()

    await start_bot()

    async for changes in awatch(".", debounce=0.5):
        paths = [path for change, path in changes]
        if any(p.endswith((".sqlite3", ".db", ".sqlite3-wal", ".sqlite3-shm", ".sqlite3-journal")) for p in paths):
            continue
        if any("__pycache__" in p for p in paths):
            continue
        print("Detected code change, restarting bot…")
        try:
            await restart_bot()
        except:
            await asyncio.sleep(1)
            await restart_bot()

if __name__ == "__main__":
    try:
        asyncio.run(watch_and_run())
    except KeyboardInterrupt:
        pass

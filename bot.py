# ╔══════════════════════════════════════════════╗
# ║         BotifyX_Pro_Botz — Linkshare Bot     ║
# ║   Telegram: https://t.me/BotifyX_Pro_Botz    ║
# ╚══════════════════════════════════════════════╝

import asyncio
from datetime import datetime

from aiohttp import web
from pyrogram import Client
from pyrogram.enums import ParseMode

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, PORT, OWNER_ID
from plugins import web_server
import pyrogram.utils

pyrogram.utils.MIN_CHANNEL_ID = -1009147483647

# Global broadcast cancel controls
is_canceled = False
cancel_lock = asyncio.Lock()


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="BOTIFYX-LINKSHARE",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN,
        )
        self.LOGGER = LOGGER

    async def start(self, *args, **kwargs):
        await super().start()
        me = await self.get_me()
        self.uptime = datetime.now()
        self.username = me.username

        # Notify owner on (re)start
        try:
            await self.send_message(
                chat_id=OWNER_ID,
                text="<b><blockquote>☘️ Sᴇɴᴘᴀɪ I'ᴍ ᴀʟɪᴠᴇ</blockquote></b>",
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            self.LOGGER(__name__).warning(f"Could not notify owner on start: {e}")

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info("Linkshare Bot is running...")
        self.LOGGER(__name__).info(f"Logged in as @{self.username}")

        # Spin up the health-check web server
        try:
            runner = web.AppRunner(await web_server())
            await runner.setup()
            await web.TCPSite(runner, "0.0.0.0", PORT).start()
            self.LOGGER(__name__).info(f"Web server listening on port {PORT}")
        except Exception as e:
            self.LOGGER(__name__).error(f"Web server failed to start: {e}")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped cleanly.")


if __name__ == "__main__":
    Bot().run()
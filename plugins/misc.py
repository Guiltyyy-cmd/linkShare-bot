# ╔══════════════════════════════════════════════╗
# ║         BotifyX_Pro_Botz — Linkshare Bot     ║
# ╚══════════════════════════════════════════════╝

from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

from bot import Bot
from config import OWNER_ID, BOT_STATS_TEXT
from helpers import get_readable_time


@Bot.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def cmd_stats(client: Bot, message: Message):
    delta  = datetime.now() - client.uptime
    uptime = get_readable_time(delta.seconds)
    await message.reply(BOT_STATS_TEXT.format(uptime=uptime))
# ╔══════════════════════════════════════════════╗
# ║         BotifyX_Pro_Botz — LinkShare Bot     ║
# ║   Telegram: https://t.me/HypoFlix_Network    ║
# ╚══════════════════════════════════════════════╝

import os
import re
import logging
from logging.handlers import RotatingFileHandler
from os import environ

# ── Required ──────────────────────────────────────────────────────────────────
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8907536916:AAEwbWh0gw4B0JmncDD9GI80qLOVhrQkTuE")
APP_ID       = int(os.environ.get("APP_ID", "31761013"))
API_HASH     = os.environ.get("API_HASH", "3d55d62014467b2a922c6c0d6d95deae")

# ── Ownership ─────────────────────────────────────────────────────────────────
OWNER_ID = int(os.environ.get("OWNER_ID", "7537243058"))
PORT     = os.environ.get("PORT", "8080")

# ── Database ──────────────────────────────────────────────────────────────────
DB_URI  = os.environ.get("DB_URI", "mongodb+srv://dubbingroup29_db_user:itsyashjha@immortaldata.ojaeaxj.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = os.environ.get("DB_NAME", "Yae_Probot")

# ── Database channel (where /genlink stores links) ────────────────────────────
DATABASE_CHANNEL = int(os.environ.get("DATABASE_CHANNEL", "-1003628073027"))

# ── Auto-approve ──────────────────────────────────────────────────────────────
id_pattern = re.compile(r"^-?\d+$")
CHAT_ID = [
    int(cid) if id_pattern.search(cid) else cid
    for cid in environ.get("CHAT_ID", "").split()
    if cid
]
APPROVED         = environ.get("APPROVED_WELCOME", "on").lower()
TEXT             = environ.get(
    "APPROVED_WELCOME_TEXT",
    "<b>{mention},\n\nʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ {title} ɪs ᴀᴘᴘʀᴏᴠᴇᴅ.\n\n"
    "‣ ᴘᴏᴡᴇʀᴇᴅ ʙʏ @HypoFlix_Network</b>",
)

# ── Force-Subscribe ───────────────────────────────────────────────────────────
# FSUB_CHANNELS  : space-separated channel IDs that users MUST join before use
FSUB_CHANNELS    = [
    int(cid) for cid in environ.get("FSUB_CHANNELS", "-1003819872917").split() if cid
]
FSUB_LINK_EXPIRY = int(os.environ.get("FSUB_LINK_EXPIRY", "10"))   # seconds; 0 = no expiry

FORCE_PIC = os.environ.get(
    "FORCE_PIC",
    "https://i.pinimg.com/736x/3d/45/cb/3d45cbb976ed3fb5dc7265afd9dfbf82.jpg",
)
FORCE_MSG = os.environ.get(
    "FORCE_MSG",
    "<b>Hᴇʏ!!! {mention} Sᴇɴᴘᴀɪ,\n"
    "ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ ᴄʜᴀɴɴᴇʟ(s) ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ.\n\n"
    "ᴀғᴛᴇʀ ᴊᴏɪɴɪɴɢ, ᴄʟɪᴄᴋ <b>♻️ Tʀʏ Aɢᴀɪɴ</b></b>",
)

# ── Bot images ────────────────────────────────────────────────────────────────
START_PIC = os.environ.get(
    "START_PIC",
    "https://i.pinimg.com/736x/ba/ec/36/baec367a261437e9eb620d1da2247ee4.jpg",
)
START_IMG = START_PIC  # alias

# ── Start & help messages ──────────────────────────────────────────────────────
START_MSG = os.environ.get(
    "START_MESSAGE",
    "<b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <a href='https://t.me/HypoFlix_Network'>LinkShare Bot</a>.\n"
    "sʜᴀʀᴇ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋs sᴇᴄᴜʀᴇʟʏ ᴡɪᴛʜ ᴛᴇᴍᴘᴏʀᴀʀʏ ɪɴᴠɪᴛᴇs\n"
    "ᴀɴᴅ ᴋᴇᴇᴘ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟs sᴀғᴇ ғʀᴏᴍ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs.\n\n"
    "<blockquote>‣ ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ : <a href='https://t.me/BlurpleOg'>BlurpleOg</a></blockquote></b>",
)

HELP = os.environ.get(
    "HELP_MESSAGE",
    "<b><blockquote expandable>"
    "» Uᴘᴅᴀᴛᴇs: <a href='https://t.me/HypoFlix_Network'>HypoFlix Network</a>\n"
    "» sᴜᴘᴘᴏʀᴛ: <a href='https://t.me/BlurpleOg'>BlurpleOg</a>\n"
    "» ᴅᴇᴠ: <a href='https://t.me/BlurpleOg'>彡 乃ㄥㄩ尺卩ㄥ乇 ㄖ厶 彡</a>"
    "</blockquote></b>",
)

ABOUT = os.environ.get(
    "ABOUT_MESSAGE",
    "<b><blockquote expandable>"
    "LɪɴᴋSʜᴀʀᴇ Bᴏᴛ sᴇᴄᴜʀᴇʟʏ sʜᴀʀᴇs Tᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋs ᴜsɪɴɢ ᴛᴇᴍᴘᴏʀᴀʀʏ ɪɴᴠɪᴛᴇ ʟɪɴᴋs,"
    "ᴘʀᴏᴛᴇᴄᴛɪɴɢ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟs ғʀᴏᴍ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs ᴀɴᴅ ʟɪɴᴋ ᴛʜᴇғᴛ.\n\n"
    "‣ Mᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ : <a href='https://t.me/BlurpleOg'>乃ㄥㄩ尺卩ㄥ乇 ㄖ厶</a>"
    "</blockquote></b>",
)

ABOUT_TXT = (
    "<b>›› ᴄᴏᴍᴍᴜɴɪᴛʏ: <a href='https://t.me/HypoFlix_Network'>HypoFlix Network</a>\n"
    "<blockquote expandable>"
    "›› ᴜᴘᴅᴀᴛᴇs: <a href='https://t.me/HypoFlix_Network'>Cʟɪᴄᴋ ʜᴇʀᴇ</a>\n"
    "›› sᴜᴘᴘᴏʀᴛ: <a href='https://t.me/BlurpleOg'>乃ㄥㄩ尺卩ㄥ乇 ㄖ厶</a>\n"
    "›› ʟᴀɴɢᴜᴀɢᴇ: <a href='https://docs.python.org/3/'>Pʏᴛʜᴏɴ 3</a>\n"
    "›› ʟɪʙʀᴀʀʏ: <a href='https://docs.pyrogram.org/'>Pʏʀᴏɢʀᴀᴍ ᴠ2</a>\n"
    "›› ᴅᴀᴛᴀʙᴀsᴇ: <a href='https://www.mongodb.com/docs/'>MᴏɴɢᴏDB</a>\n"
    "›› ᴅᴇᴠᴇʟᴏᴘᴇʀ: @BlurpleOg"
    "</blockquote></b>"
)

CHANNELS_TXT = (
    "<b>›› Uᴘᴅᴀᴛᴇs: <a href='https://t.me/BotifyX_Pro_Botz'>BᴏᴛɪғʏX-Bᴏᴛᴢ</a>\n"
    "<blockquote expandable>"
    "›› sᴜᴘᴘᴏʀᴛ: <a href='https://t.me/BlurpleOg'>乃ㄥㄩ尺卩ㄥ乇 ㄖ厶</a>\n"
    "›› ᴅᴇᴠᴇʟᴏᴘᴇʀ: <a href='https://t.me/BlurpleOg'>乃ㄥㄩ尺卩ㄥ乇 ㄖ厶</a>"
    "</blockquote></b>"
)

# ── Default / misc ─────────────────────────────────────────────────────────────
TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "40"))
BOT_STATS_TEXT = "<b>⚡Bᴏᴛ Uᴘᴛɪᴍᴇ</b>\n{uptime}"
USER_REPLY_TEXT = "ɪ ᴏɴʟʏ ʀᴇsᴘᴏɴᴅ ᴛᴏ Mʏ Mᴀsᴛᴇʀ @Blurpleog"

# ── Logging ────────────────────────────────────────────────────────────────────
LOG_FILE_NAME = "linkshare-bot.log"

try:
    ADMINS: list[int] = []
    for _uid in os.environ.get("ADMINS", str(OWNER_ID)).split():
        ADMINS.append(int(_uid))
except ValueError:
    raise Exception("ADMINS env var must contain space-separated integers.")

if OWNER_ID not in ADMINS:
    ADMINS.append(OWNER_ID)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(LOG_FILE_NAME, maxBytes=50_000_000, backupCount=10),
        logging.StreamHandler(),
    ],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)

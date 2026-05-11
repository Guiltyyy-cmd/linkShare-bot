# ╔══════════════════════════════════════════════╗
# ║         BotifyX_Pro_Botz — LinkVault Bot     ║
# ║   Telegram: https://t.me/BotifyX_Pro_Botz    ║
# ╚══════════════════════════════════════════════╝

import base64
from pyrogram.filters import Filter
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from config import OWNER_ID
from database.db import is_admin


# ── Custom filters ─────────────────────────────────────────────────────────────

class IsAdmin(Filter):
    """True if the sender is a bot admin (stored in DB)."""
    async def __call__(self, client, message):
        return await is_admin(message.from_user.id)


class IsOwnerOrAdmin(Filter):
    """True if the sender is the owner or a DB admin."""
    async def __call__(self, client, message):
        uid = message.from_user.id
        return uid == OWNER_ID or await is_admin(uid)


is_admin_filter   = IsAdmin()
is_owner_or_admin = IsOwnerOrAdmin()


# ── Encoding helpers ───────────────────────────────────────────────────────────

async def encode(string: str) -> str:
    """URL-safe base64 encode (no padding)."""
    return base64.urlsafe_b64encode(string.encode("ascii")).decode("ascii").strip("=")


async def decode(base64_string: str) -> str:
    """URL-safe base64 decode (no-padding tolerant)."""
    base64_string = base64_string.strip("=")
    padded = base64_string + "=" * (-len(base64_string) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii")).decode("ascii")


# ── Uptime helper ──────────────────────────────────────────────────────────────

def get_readable_time(seconds: int) -> str:
    """Convert a duration in seconds to a human-readable string."""
    count = 0
    up_time = ""
    time_list: list[int] = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = (
            divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        )
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]

    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "

    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time
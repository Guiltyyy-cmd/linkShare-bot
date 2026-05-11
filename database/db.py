# ╔══════════════════════════════════════════════╗
# ║         BotifyX_Pro_Botz — LinkVault Bot     ║
# ║   Telegram: https://t.me/BotifyX_Pro_Botz    ║
# ╚══════════════════════════════════════════════╝

import base64
from datetime import datetime
from typing import List, Optional

import motor.motor_asyncio

from config import DB_URI, DB_NAME

# ── Motor client & collections ─────────────────────────────────────────────────
_client             = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
_database           = _client[DB_NAME]

user_data              = _database["users"]
channels_collection    = _database["channels"]
fsub_channels_collection = _database["fsub_channels"]
admins_collection      = _database["admins"]


# ── Users ──────────────────────────────────────────────────────────────────────

async def add_user(user_id: int) -> bool:
    """Insert user if not present. Returns True if inserted."""
    if not isinstance(user_id, int) or user_id <= 0:
        return False
    try:
        if await user_data.find_one({"_id": user_id}):
            return False
        await user_data.insert_one({"_id": user_id, "created_at": datetime.utcnow()})
        return True
    except Exception as e:
        print(f"[DB] add_user({user_id}): {e}")
        return False


async def present_user(user_id: int) -> bool:
    return bool(await user_data.find_one({"_id": user_id}))


async def full_userbase() -> List[int]:
    try:
        return [doc["_id"] async for doc in user_data.find()]
    except Exception as e:
        print(f"[DB] full_userbase: {e}")
        return []


async def del_user(user_id: int) -> bool:
    try:
        result = await user_data.delete_one({"_id": user_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"[DB] del_user({user_id}): {e}")
        return False


# ── Admins ─────────────────────────────────────────────────────────────────────

async def is_admin(user_id: int) -> bool:
    try:
        return bool(await admins_collection.find_one({"_id": int(user_id)}))
    except Exception as e:
        print(f"[DB] is_admin({user_id}): {e}")
        return False


async def add_admin(user_id: int) -> bool:
    try:
        await admins_collection.update_one(
            {"_id": int(user_id)}, {"$set": {"_id": int(user_id)}}, upsert=True
        )
        return True
    except Exception as e:
        print(f"[DB] add_admin({user_id}): {e}")
        return False


async def remove_admin(user_id: int) -> bool:
    try:
        result = await admins_collection.delete_one({"_id": int(user_id)})
        return result.deleted_count > 0
    except Exception as e:
        print(f"[DB] remove_admin({user_id}): {e}")
        return False


async def list_admins() -> List[int]:
    try:
        return [doc["_id"] async for doc in admins_collection.find()]
    except Exception as e:
        print(f"[DB] list_admins: {e}")
        return []


# ── Link-share channels ────────────────────────────────────────────────────────

async def save_channel(channel_id: int) -> bool:
    try:
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "channel_id": channel_id,
                    "invite_link_expiry": None,
                    "created_at": datetime.utcnow(),
                    "status": "active",
                }
            },
            upsert=True,
        )
        return True
    except Exception as e:
        print(f"[DB] save_channel({channel_id}): {e}")
        return False


async def get_channels() -> List[int]:
    try:
        docs = await channels_collection.find({"status": "active"}).to_list(None)
        return [d["channel_id"] for d in docs if "channel_id" in d]
    except Exception as e:
        print(f"[DB] get_channels: {e}")
        return []


async def delete_channel(channel_id: int) -> bool:
    try:
        result = await channels_collection.delete_one({"channel_id": channel_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"[DB] delete_channel({channel_id}): {e}")
        return False


async def save_encoded_link(channel_id: int) -> Optional[str]:
    try:
        encoded = base64.urlsafe_b64encode(str(channel_id).encode()).decode()
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "encoded_link": encoded,
                    "status": "active",
                    "updated_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )
        return encoded
    except Exception as e:
        print(f"[DB] save_encoded_link({channel_id}): {e}")
        return None


async def get_channel_by_encoded_link(encoded_link: str) -> Optional[int]:
    try:
        doc = await channels_collection.find_one(
            {"encoded_link": encoded_link, "status": "active"}
        )
        return doc["channel_id"] if doc and "channel_id" in doc else None
    except Exception as e:
        print(f"[DB] get_channel_by_encoded_link: {e}")
        return None


async def save_encoded_link2(channel_id: int, encoded_link: str) -> Optional[str]:
    try:
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "req_encoded_link": encoded_link,
                    "status": "active",
                    "updated_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )
        return encoded_link
    except Exception as e:
        print(f"[DB] save_encoded_link2({channel_id}): {e}")
        return None


async def get_channel_by_encoded_link2(encoded_link: str) -> Optional[int]:
    try:
        doc = await channels_collection.find_one(
            {"req_encoded_link": encoded_link, "status": "active"}
        )
        return doc["channel_id"] if doc and "channel_id" in doc else None
    except Exception as e:
        print(f"[DB] get_channel_by_encoded_link2: {e}")
        return None


async def save_invite_link(channel_id: int, invite_link: str, is_request: bool) -> bool:
    try:
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "current_invite_link": invite_link,
                    "is_request_link": is_request,
                    "invite_link_created_at": datetime.utcnow(),
                    "status": "active",
                }
            },
            upsert=True,
        )
        return True
    except Exception as e:
        print(f"[DB] save_invite_link({channel_id}): {e}")
        return False


async def get_current_invite_link(channel_id: int) -> Optional[dict]:
    try:
        doc = await channels_collection.find_one(
            {"channel_id": channel_id, "status": "active"}
        )
        if doc and "current_invite_link" in doc:
            return {
                "invite_link": doc["current_invite_link"],
                "is_request": doc.get("is_request_link", False),
            }
        return None
    except Exception as e:
        print(f"[DB] get_current_invite_link({channel_id}): {e}")
        return None


async def get_link_creation_time(channel_id: int):
    try:
        doc = await channels_collection.find_one(
            {"channel_id": channel_id, "status": "active"}
        )
        return doc.get("invite_link_created_at") if doc else None
    except Exception as e:
        print(f"[DB] get_link_creation_time({channel_id}): {e}")
        return None


async def get_original_link(channel_id: int) -> Optional[str]:
    try:
        doc = await channels_collection.find_one(
            {"channel_id": channel_id, "status": "active"}
        )
        return doc.get("original_link") if doc else None
    except Exception as e:
        print(f"[DB] get_original_link({channel_id}): {e}")
        return None


# ── Auto-approve flags ─────────────────────────────────────────────────────────

async def set_approval_off(channel_id: int, off: bool = True) -> bool:
    try:
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {"$set": {"approval_off": off}},
            upsert=True,
        )
        return True
    except Exception as e:
        print(f"[DB] set_approval_off({channel_id}): {e}")
        return False


async def is_approval_off(channel_id: int) -> bool:
    try:
        doc = await channels_collection.find_one({"channel_id": channel_id})
        return bool(doc and doc.get("approval_off", False))
    except Exception as e:
        print(f"[DB] is_approval_off({channel_id}): {e}")
        return False


# ── FSub channels ──────────────────────────────────────────────────────────────

async def add_fsub_channel(channel_id: int) -> bool:
    """Add a channel to the force-subscribe list."""
    try:
        await fsub_channels_collection.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "channel_id": channel_id,
                    "mode": "off",        # "on" = join-request mode, "off" = direct invite
                    "status": "active",
                    "added_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )
        return True
    except Exception as e:
        print(f"[DB] add_fsub_channel({channel_id}): {e}")
        return False


async def remove_fsub_channel(channel_id: int) -> bool:
    try:
        result = await fsub_channels_collection.delete_one({"channel_id": channel_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"[DB] remove_fsub_channel({channel_id}): {e}")
        return False


async def get_fsub_channels() -> List[int]:
    try:
        docs = await fsub_channels_collection.find({"status": "active"}).to_list(None)
        return [d["channel_id"] for d in docs if "channel_id" in d]
    except Exception as e:
        print(f"[DB] get_fsub_channels: {e}")
        return []


async def get_fsub_channel_mode(channel_id: int) -> str:
    """Return the mode ('on' = request, 'off' = invite) for a FSub channel."""
    try:
        doc = await fsub_channels_collection.find_one({"channel_id": channel_id})
        return doc.get("mode", "off") if doc else "off"
    except Exception as e:
        print(f"[DB] get_fsub_channel_mode({channel_id}): {e}")
        return "off"


async def set_fsub_channel_mode(channel_id: int, mode: str) -> bool:
    """Set mode for a FSub channel ('on' or 'off')."""
    try:
        await fsub_channels_collection.update_one(
            {"channel_id": channel_id},
            {"$set": {"mode": mode}},
            upsert=True,
        )
        return True
    except Exception as e:
        print(f"[DB] set_fsub_channel_mode({channel_id}, {mode}): {e}")
        return False


# ── DataBase wrapper (used as `db` in start.py) ────────────────────────────────

class BotifyXDataBase:
    """Thin OO wrapper used as `db` for FSub channel queries in start.py."""

    async def show_channels(self) -> List[int]:
        return await get_fsub_channels()

    async def get_channel_mode(self, channel_id: int) -> str:
        return await get_fsub_channel_mode(channel_id)

    async def set_channel_mode(self, channel_id: int, mode: str) -> bool:
        return await set_fsub_channel_mode(channel_id, mode)


shun = BotifyXDataBase()
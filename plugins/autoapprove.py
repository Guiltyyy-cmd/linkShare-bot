# ╔══════════════════════════════════════════════╗
# ║         BotifyX_Pro_Botz — LinkVault Bot     ║
# ║     Auto-Approve Module (autoapprove.py)     ║
# ╚══════════════════════════════════════════════╝

import asyncio

from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant, FloodWait, ChatAdminRequired, RPCError
from pyrogram.types import (
    ChatJoinRequest,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import APPROVED, CHAT_ID, APP_ID, API_HASH, START_PIC
from database.db import set_approval_off, is_approval_off
from helpers import is_owner_or_admin

# ── Settings (runtime-adjustable via commands) ─────────────────────────────────
APPROVAL_WAIT_TIME   = 5    # seconds to wait before approving
AUTO_APPROVE_ENABLED = True


# ── Auto-approve handler ───────────────────────────────────────────────────────

@Client.on_chat_join_request(
    (filters.group | filters.channel) & filters.chat(CHAT_ID)
    if CHAT_ID
    else (filters.group | filters.channel)
)
async def auto_approve(client: Client, request: ChatJoinRequest):
    global AUTO_APPROVE_ENABLED

    if not AUTO_APPROVE_ENABLED:
        return

    chat = request.chat
    user = request.from_user

    # Per-channel override
    if await is_approval_off(chat.id):
        return

    print(f"[AutoApprove] {user.first_name} requested to join {chat.title}")
    await asyncio.sleep(APPROVAL_WAIT_TIME)

    # Skip if already a member
    try:
        member = await client.get_chat_member(chat.id, user.id)
        if member.status.name in ("MEMBER", "ADMINISTRATOR", "OWNER", "CREATOR"):
            return
    except UserNotParticipant:
        pass
    except Exception as e:
        print(f"[AutoApprove] get_chat_member error: {e}")

    try:
        await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
    except Exception as e:
        print(f"[AutoApprove] approve error: {e}")
        return

    if APPROVED == "on":
        try:
            invite_link = await client.export_chat_invite_link(chat.id)
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("• ᴜᴘᴅᴀᴛᴇs •", url="https://t.me/BotifyX_Pro_Botz")],
                [InlineKeyboardButton(f"• ᴊᴏɪɴ {chat.title} •", url=invite_link)],
            ])
            caption = (
                f"<b>ʜᴇʏ {user.mention()},\n\n"
                f"<blockquote>✅ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ <b>{chat.title}</b> ʜᴀs ʙᴇᴇɴ ᴀᴘᴘʀᴏᴠᴇᴅ.</blockquote></b>"
            )
            await client.send_photo(
                chat_id=user.id,
                photo=START_PIC,
                caption=caption,
                reply_markup=markup,
            )
        except Exception as e:
            print(f"[AutoApprove] welcome message error: {e}")


# ── Admin commands ─────────────────────────────────────────────────────────────

@Client.on_message(filters.command("reqtime") & is_owner_or_admin)
async def cmd_reqtime(client: Client, message: Message):
    """Set the delay (in seconds) before a join request is approved."""
    global APPROVAL_WAIT_TIME
    if len(message.command) != 2 or not message.command[1].isdigit():
        return await message.reply_text("ᴜsᴀɢᴇ: <code>/reqtime &lt;seconds&gt;</code>")
    APPROVAL_WAIT_TIME = int(message.command[1])
    await message.reply_text(
        f"✅ Aᴘᴘʀᴏᴠᴀʟ ᴅᴇʟᴀʏ sᴇᴛ ᴛᴏ <b>{APPROVAL_WAIT_TIME}s</b>."
    )


@Client.on_message(filters.command("reqmode") & is_owner_or_admin)
async def cmd_reqmode(client: Client, message: Message):
    """Enable or disable auto-approve globally."""
    global AUTO_APPROVE_ENABLED
    if len(message.command) != 2 or message.command[1].lower() not in ("on", "off"):
        return await message.reply_text("ᴜsᴀɢᴇ: <code>/reqmode on</code> or <code>/reqmode off</code>")
    AUTO_APPROVE_ENABLED = message.command[1].lower() == "on"
    status = "✅ ᴇɴᴀʙʟᴇᴅ" if AUTO_APPROVE_ENABLED else "❌ ᴅɪsᴀʙʟᴇᴅ"
    await message.reply_text(f"Aᴜᴛᴏ-ᴀᴘᴘʀᴏᴠᴇ: {status}")


@Client.on_message(filters.command("approveoff") & is_owner_or_admin)
async def cmd_approve_off(client: Client, message: Message):
    """Disable auto-approve for a specific channel."""
    if len(message.command) != 2 or not message.command[1].lstrip("-").isdigit():
        return await message.reply_text("ᴜsᴀɢᴇ: <code>/approveoff &lt;channel_id&gt;</code>")
    cid = int(message.command[1])
    if await set_approval_off(cid, True):
        await message.reply_text(f"✅ Aᴜᴛᴏ-ᴀᴘᴘʀᴏᴠᴇ <b>OFF</b> ғᴏʀ <code>{cid}</code>.")
    else:
        await message.reply_text(f"❌ Fᴀɪʟᴇᴅ ᴛᴏ ᴜᴘᴅᴀᴛᴇ <code>{cid}</code>.")


@Client.on_message(filters.command("approveon") & is_owner_or_admin)
async def cmd_approve_on(client: Client, message: Message):
    """Re-enable auto-approve for a specific channel."""
    if len(message.command) != 2 or not message.command[1].lstrip("-").isdigit():
        return await message.reply_text("ᴜsᴀɢᴇ: <code>/approveon &lt;channel_id&gt;</code>")
    cid = int(message.command[1])
    if await set_approval_off(cid, False):
        await message.reply_text(f"✅ Aᴜᴛᴏ-ᴀᴘᴘʀᴏᴠᴇ <b>ON</b> ғᴏʀ <code>{cid}</code>.")
    else:
        await message.reply_text(f"❌ Fᴀɪʟᴇᴅ ᴛᴏ ᴜᴘᴅᴀᴛᴇ <code>{cid}</code>.")
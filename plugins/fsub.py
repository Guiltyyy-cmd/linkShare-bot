# ╔══════════════════════════════════════════════╗
# ║         BotifyX_Pro_Botz — LinkVault Bot     ║
# ║     Force-Subscribe Module  (fsub.py)        ║
# ╚══════════════════════════════════════════════╝
#
# This module handles everything related to force-subscription (FSub):
#   • Checking whether a user has joined all required channels
#   • Admin commands to add / remove / list FSub channels
#   • Per-channel "request mode" toggle (join request vs. direct invite)
#   • Callback handler for the "♻️ Try Again" button

import asyncio
from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant, FloodWait, ChatAdminRequired
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot import Bot
from config import ADMINS, FSUB_LINK_EXPIRY, FORCE_PIC, FORCE_MSG, OWNER_ID
from database.db import (
    add_fsub_channel,
    remove_fsub_channel,
    get_fsub_channels,
    get_fsub_channel_mode,
    set_fsub_channel_mode,
    shun, 
)
from helpers import is_owner_or_admin


# ═══════════════════════════════════════════════
#  Core helpers — used by start.py
# ═══════════════════════════════════════════════

async def is_sub(client: Client, user_id: int, chat_id: int) -> bool:
    """
    Return True if *user_id* is an active member of *chat_id*.
    Treats LEFT / BANNED / KICKED as not-subscribed.
    """
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status.name in (
            "OWNER",
            "ADMINISTRATOR",
            "MEMBER",
            "RESTRICTED"
       )
    except UserNotParticipant:
        return False
    except Exception as e:
        print(f"[FSub] is_sub({user_id}, {chat_id}): {e}")
        return False


async def check_subscription_status(
    client: Client,
    user_id: int,
    channels: list[int],
) -> tuple[bool, str | None, InlineKeyboardMarkup | None]:
    """
    Check if *user_id* is subscribed to every channel in *channels*.

    Returns:
        (True, None, None)                   – all channels joined
        (False, prompt_text, reply_markup)   – one or more not joined
    """
    unjoined: list[int] = []

    for cid in channels:
        if not await is_sub(client, user_id, cid):
            unjoined.append(cid)

    if not unjoined:
        return True, None, None

    buttons: list[list[InlineKeyboardButton]] = []

    for cid in unjoined:
        try:
            chat = await client.get_chat(cid)
            mode = await get_fsub_channel_mode(cid)

            if chat.username:
                link = f"https://t.me/{chat.username}"
            elif mode == "on":
                # join-request invite link
                expire = (
                    datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY)
                    if FSUB_LINK_EXPIRY
                    else None
                )
                invite = await client.create_chat_invite_link(
                    cid, creates_join_request=True, expire_date=expire
                )
                link = invite.invite_link
            else:
                # standard invite link
                expire = (
                    datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY)
                    if FSUB_LINK_EXPIRY
                    else None
                )
                invite = await client.create_chat_invite_link(
                    cid, expire_date=expire
                )
                link = invite.invite_link

            label = "📩 ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ" if mode == "on" else "• ᴊᴏɪɴ"
            buttons.append(
                [InlineKeyboardButton(f"{label} {chat.title}", url=link)]
            )
        except ChatAdminRequired:
            print(f"[FSub] Bot is not admin in {cid} — skipping invite link.")
        except Exception as e:
            print(f"[FSub] check_subscription_status channel {cid}: {e}")

    buttons.append(
        [InlineKeyboardButton("♻️ Tʀʏ Aɢᴀɪɴ", callback_data="check_sub")]
    )

    msg = (
        "<b><blockquote expandable>"
        "⚠️ ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ(s) ʟɪsᴛᴇᴅ ʙᴇʟᴏᴡ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ.\n\n"
        "ᴀғᴛᴇʀ ᴊᴏɪɴɪɴɢ, ᴘʀᴇss <b>♻️ Tʀʏ Aɢᴀɪɴ</b>."
        "</blockquote></b>"
    )
    return False, msg, InlineKeyboardMarkup(buttons)


# ═══════════════════════════════════════════════
#  Admin commands
# ═══════════════════════════════════════════════

@Bot.on_message(filters.command("addfsub") & is_owner_or_admin)
async def cmd_add_fsub(client: Bot, message: Message):
    """
    /addfsub <channel_id>
    Add a channel to the force-subscribe list.
    Bot must be admin in that channel.
    """
    if len(message.command) != 2 or not message.command[1].lstrip("-").isdigit():
        return await message.reply_text(
            "ᴜsᴀɢᴇ: <code>/addfsub &lt;channel_id&gt;</code>\n\n"
            "<i>Make sure the bot is an admin in that channel first.</i>"
        )

    cid = int(message.command[1])

    try:
        chat = await client.get_chat(cid)
    except Exception as e:
        return await message.reply_text(
            f"❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ғᴇᴛᴄʜ ᴄʜᴀᴛ: <code>{e}</code>"
        )

    success = await add_fsub_channel(cid)
    if success:
        await message.reply_text(
            f"✅ <b>{chat.title}</b> (<code>{cid}</code>) ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ ғsᴜʙ ʟɪsᴛ.\n\n"
            f"<i>Use /fsubmode {cid} on  to enable join-request mode.</i>"
        )
    else:
        await message.reply_text(
            f"⚠️ <b>{chat.title}</b> ᴍᴀʏ ᴀʟʀᴇᴀᴅʏ ʙᴇ ɪɴ ᴛʜᴇ ʟɪsᴛ."
        )


@Bot.on_message(filters.command("delfsub") & is_owner_or_admin)
async def cmd_del_fsub(client: Bot, message: Message):
    """
    /delfsub <channel_id>
    Remove a channel from the force-subscribe list.
    """
    if len(message.command) != 2 or not message.command[1].lstrip("-").isdigit():
        return await message.reply_text(
            "ᴜsᴀɢᴇ: <code>/delfsub &lt;channel_id&gt;</code>"
        )

    cid = int(message.command[1])
    success = await remove_fsub_channel(cid)

    if success:
        await message.reply_text(
            f"✅ ᴄʜᴀɴɴᴇʟ <code>{cid}</code> ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ғsᴜʙ ʟɪsᴛ."
        )
    else:
        await message.reply_text(
            f"❌ ᴄʜᴀɴɴᴇʟ <code>{cid}</code> ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴛʜᴇ ʟɪsᴛ."
        )


@Bot.on_message(filters.command("listfsub") & is_owner_or_admin)
async def cmd_list_fsub(client: Bot, message: Message):
    """
    /listfsub
    List all force-subscribe channels with their current mode.
    """
    channels = await get_fsub_channels()
    if not channels:
        return await message.reply_text(
            "ɴᴏ ғsᴜʙ ᴄʜᴀɴɴᴇʟs ᴄᴏɴғɪɢᴜʀᴇᴅ.\n"
            "ᴜsᴇ <code>/addfsub &lt;channel_id&gt;</code> ᴛᴏ ᴀᴅᴅ ᴏɴᴇ."
        )

    lines = ["<b>📋 Fᴏʀᴄᴇ-Sᴜʙsᴄʀɪʙᴇ Cʜᴀɴɴᴇʟs:</b>\n"]
    for idx, cid in enumerate(channels, 1):
        mode = await get_fsub_channel_mode(cid)
        mode_label = "🟢 ʀᴇǫᴜᴇsᴛ" if mode == "on" else "🔵 ɪɴᴠɪᴛᴇ"
        try:
            chat = await client.get_chat(cid)
            name = chat.title
        except Exception:
            name = "Unknown"
        lines.append(f"{idx}. <b>{name}</b> <code>({cid})</code> — {mode_label}")

    await message.reply_text("\n".join(lines))


@Bot.on_message(filters.command("fsubmode") & is_owner_or_admin)
async def cmd_fsub_mode(client: Bot, message: Message):
    """
    /fsubmode <channel_id> <on|off>
    Toggle join-request mode (on) or standard invite mode (off) for a FSub channel.
    """
    if len(message.command) != 3 or message.command[2].lower() not in ("on", "off"):
        return await message.reply_text(
            "ᴜsᴀɢᴇ: <code>/fsubmode &lt;channel_id&gt; &lt;on|off&gt;</code>\n\n"
            "<b>on</b>  → users must send a join request\n"
            "<b>off</b> → users get a direct invite link"
        )

    try:
        cid = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ID.")

    mode = message.command[2].lower()
    success = await set_fsub_channel_mode(cid, mode)

    if success:
        mode_label = "🟢 ʀᴇǫᴜᴇsᴛ ᴍᴏᴅᴇ" if mode == "on" else "🔵 ɪɴᴠɪᴛᴇ ᴍᴏᴅᴇ"
        await message.reply_text(
            f"✅ ᴄʜᴀɴɴᴇʟ <code>{cid}</code> sᴇᴛ ᴛᴏ {mode_label}."
        )
    else:
        await message.reply_text(f"❌ Fᴀɪʟᴇᴅ ᴛᴏ ᴜᴘᴅᴀᴛᴇ ᴍᴏᴅᴇ ғᴏʀ <code>{cid}</code>.")


# ═══════════════════════════════════════════════
#  Callback — "Try Again" button
# ═══════════════════════════════════════════════

@Bot.on_callback_query(filters.regex("^check_sub$"))
async def cb_check_sub(client: Bot, query: CallbackQuery):
    """Re-check subscription status when user taps ♻️ Try Again."""
    await query.answer()
    user_id = query.from_user.id
    fsub_channels = await get_fsub_channels()

    if not fsub_channels:
        await query.message.edit_caption(
            caption="✅ ᴀʟʟ ᴄʜᴀɴɴᴇʟs ᴊᴏɪɴᴇᴅ!\n\nᴜsᴇ /start ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ."
       )

    is_subscribed, sub_msg, sub_markup = await check_subscription_status(
        client, user_id, fsub_channels
    )

    if is_subscribed:
        await query.message.edit_caption(
            caption="✅ ᴀʟʟ ᴄʜᴀɴɴᴇʟs ᴊᴏɪɴᴇᴅ!\n\nᴜsᴇ /start ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ."
        )
    else:
        await query.message.edit_caption(
            caption=sub_msg,
            reply_markup=sub_markup,
        )


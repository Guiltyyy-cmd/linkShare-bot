# ╔══════════════════════════════════════════════╗
# ║         BotifyX_Pro_Botz — LinkVault Bot     ║
# ║     Channel Posts Module  (posts.py)         ║
# ╚══════════════════════════════════════════════╝

import asyncio
from datetime import datetime, timedelta

from pyrogram import filters
from pyrogram.errors import UserNotParticipant, FloodWait, ChatAdminRequired, RPCError
from pyrogram.errors import InviteHashExpired, InviteRequestSent
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot import Bot
from config import ADMINS
from database.db import (
    save_channel,
    delete_channel,
    get_channels,
    save_encoded_link,
    save_encoded_link2,
    channels_collection,
)
from helpers import is_owner_or_admin, encode

PAGE_SIZE = 6

# Cache for chat info (5-minute TTL)
_chat_cache: dict[int, tuple] = {}


# ── Invite-link auto-revoke task ───────────────────────────────────────────────

async def revoke_invite_after_5_minutes(
    client: Bot, channel_id: int, link: str, is_request: bool = False
):
    """Revoke a temporary invite link after 5 minutes."""
    await asyncio.sleep(300)
    try:
        await client.revoke_chat_invite_link(channel_id, link)
        kind = "request" if is_request else "invite"
        print(f"[Posts] Revoked {kind} link for channel {channel_id}")
    except Exception as e:
        print(f"[Posts] Failed to revoke link for channel {channel_id}: {e}")


# ── Chat info helper with TTL cache ───────────────────────────────────────────

async def get_chat_info(client: Bot, channel_id: int):
    if channel_id in _chat_cache:
        info, ts = _chat_cache[channel_id]
        if (datetime.now() - ts).total_seconds() < 300:
            return info
    info = await client.get_chat(channel_id)
    _chat_cache[channel_id] = (info, datetime.now())
    return info


# ── /addchat  /addch ───────────────────────────────────────────────────────────

@Bot.on_message((filters.command("addchat") | filters.command("addch")) & is_owner_or_admin)
async def cmd_add_chat(client: Bot, message: Message):
    try:
        channel_id = int(message.command[1])
    except (IndexError, ValueError):
        return await message.reply(
            "<b><blockquote expandable>ᴜsᴀɢᴇ: <code>/addchat &lt;channel_id&gt;</code></blockquote></b>"
        )

    try:
        chat = await client.get_chat(channel_id)

        # Basic permission check
        has_permission = False
        if chat.type.name in ("GROUP", "SUPERGROUP"):
            try:
                me = await client.get_chat_member(chat.id, (await client.get_me()).id)
                if me.status.name in ("ADMINISTRATOR", "OWNER", "CREATOR"):
                    has_permission = True
            except Exception:
                pass
        elif chat.permissions:
            if getattr(chat.permissions, "can_post_messages", False) or \
               getattr(chat.permissions, "can_edit_messages", False):
                has_permission = True

        if not has_permission:
            return await message.reply(
                f"<b><blockquote expandable>I ᴀᴍ ɪɴ <b>{chat.title}</b> ʙᴜᴛ ʟᴀᴄᴋ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs.</blockquote></b>"
            )

        await save_channel(channel_id)
        b64_invite  = await save_encoded_link(channel_id)
        b64_request = await encode(str(channel_id))
        await save_encoded_link2(channel_id, b64_request)

        normal_link  = f"https://t.me/{client.username}?start={b64_invite}"
        request_link = f"https://t.me/{client.username}?start=req_{b64_request}"

        await message.reply(
            f"<b><blockquote expandable>✅ <b>{chat.title}</b> (<code>{channel_id}</code>) ᴀᴅᴅᴇᴅ.</blockquote></b>\n\n"
            f"<b>🔗 Nᴏʀᴍᴀʟ ʟɪɴᴋ:</b> <code>{normal_link}</code>\n"
            f"<b>🔗 Rᴇǫᴜᴇsᴛ ʟɪɴᴋ:</b> <code>{request_link}</code>"
        )

    except UserNotParticipant:
        await message.reply(
            "<b><blockquote expandable>I ᴀᴍ ɴᴏᴛ ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜɪs ᴄʜᴀɴɴᴇʟ. Aᴅᴅ ᴍᴇ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</blockquote></b>"
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await cmd_add_chat(client, message)
    except RPCError as e:
        await message.reply(f"RPC Error: <code>{e}</code>")
    except Exception as e:
        await message.reply(f"Error: <code>{e}</code>")


# ── /delchat  /delch ───────────────────────────────────────────────────────────

@Bot.on_message((filters.command("delchat") | filters.command("delch")) & is_owner_or_admin)
async def cmd_del_chat(client: Bot, message: Message):
    try:
        channel_id = int(message.command[1])
    except (IndexError, ValueError):
        return await message.reply(
            "<b><blockquote expandable>ᴜsᴀɢᴇ: <code>/delchat &lt;channel_id&gt;</code></blockquote></b>"
        )
    await delete_channel(channel_id)
    await message.reply(
        f"<b><blockquote expandable>❌ Cʜᴀɴɴᴇʟ <code>{channel_id}</code> ʀᴇᴍᴏᴠᴇᴅ.</blockquote></b>"
    )


# ── /ch_links ──────────────────────────────────────────────────────────────────

@Bot.on_message(filters.command("ch_links") & is_owner_or_admin)
async def cmd_channel_links(client: Bot, message: Message):
    wait = await message.reply("⏳")
    channels = await get_channels()
    if not channels:
        await wait.delete()
        return await message.reply(
            "<b><blockquote expandable>ɴᴏ ᴄʜᴀɴɴᴇʟs ғᴏᴜɴᴅ. ᴜsᴇ /addch ᴛᴏ ᴀᴅᴅ ᴏɴᴇ.</blockquote></b>"
        )
    await _send_channel_page(client, message, channels, page=0, status_msg=wait)


async def _send_channel_page(client, message, channels, page, status_msg=None, edit=False):
    if status_msg:
        await status_msg.delete()

    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    slice_ = channels[page * PAGE_SIZE : (page + 1) * PAGE_SIZE]

    infos = await asyncio.gather(
        *[get_chat_info(client, cid) for cid in slice_], return_exceptions=True
    )
    row, buttons = [], []

    for i, info in enumerate(infos):
        cid = slice_[i]
        if isinstance(info, Exception) or info is None:
            continue
        try:
            b64 = await save_encoded_link(cid)
            link = f"https://t.me/{client.username}?start={b64}"
            row.append(InlineKeyboardButton(info.title, url=link))
            if len(row) == 2:
                buttons.append(row)
                row = []
        except Exception:
            pass

    if row:
        buttons.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("• Pʀᴇᴠɪᴏᴜs •", callback_data=f"channelpage_{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("• Nᴇxᴛ •", callback_data=f"channelpage_{page+1}"))
    if nav:
        buttons.append(nav)

    markup = InlineKeyboardMarkup(buttons)
    if edit:
        await message.edit_text("Sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ:", reply_markup=markup)
    else:
        await message.reply("Sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ:", reply_markup=markup)


@Bot.on_callback_query(filters.regex(r"^channelpage_(\d+)$"))
async def cb_paginate_channels(client: Bot, query):
    page = int(query.data.split("_")[1])
    wait = await query.message.edit_text("⏳")
    channels = await get_channels()
    await _send_channel_page(client, query.message, channels, page, status_msg=wait, edit=True)


# ── /reqlink ───────────────────────────────────────────────────────────────────

@Bot.on_message(filters.command("reqlink") & is_owner_or_admin)
async def cmd_req_links(client: Bot, message: Message):
    wait = await message.reply("⏳")
    channels = await get_channels()
    if not channels:
        await wait.delete()
        return await message.reply(
            "<b><blockquote expandable>ɴᴏ ᴄʜᴀɴɴᴇʟs ғᴏᴜɴᴅ.</blockquote></b>"
        )
    await _send_request_page(client, message, channels, page=0, status_msg=wait)


async def _send_request_page(client, message, channels, page, status_msg=None, edit=False):
    if status_msg:
        await status_msg.delete()

    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    slice_ = channels[page * PAGE_SIZE : (page + 1) * PAGE_SIZE]
    infos = await asyncio.gather(
        *[get_chat_info(client, cid) for cid in slice_], return_exceptions=True
    )
    row, buttons = [], []

    for i, info in enumerate(infos):
        cid = slice_[i]
        if isinstance(info, Exception) or info is None:
            continue
        try:
            b64 = await encode(str(cid))
            await save_encoded_link2(cid, b64)
            link = f"https://t.me/{client.username}?start=req_{b64}"
            row.append(InlineKeyboardButton(info.title, url=link))
            if len(row) == 2:
                buttons.append(row)
                row = []
        except Exception:
            pass

    if row:
        buttons.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("• Pʀᴇᴠɪᴏᴜs •", callback_data=f"reqpage_{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("• Nᴇxᴛ •", callback_data=f"reqpage_{page+1}"))
    if nav:
        buttons.append(nav)

    markup = InlineKeyboardMarkup(buttons)
    if edit:
        await message.edit_text("Sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ:", reply_markup=markup)
    else:
        await message.reply("Sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ:", reply_markup=markup)


@Bot.on_callback_query(filters.regex(r"^reqpage_(\d+)$"))
async def cb_paginate_requests(client: Bot, query):
    page = int(query.data.split("_")[1])
    wait = await query.message.edit_text("⏳")
    channels = await get_channels()
    await _send_request_page(client, query.message, channels, page, status_msg=wait, edit=True)


# ── /links ─────────────────────────────────────────────────────────────────────

@Bot.on_message(filters.command("links") & is_owner_or_admin)
async def cmd_show_links(client: Bot, message: Message):
    wait = await message.reply("⏳")
    channels = await get_channels()
    if not channels:
        await wait.delete()
        return await message.reply(
            "<b><blockquote expandable>ɴᴏ ᴄʜᴀɴɴᴇʟs ғᴏᴜɴᴅ.</blockquote></b>"
        )
    await _send_links_page(client, message, channels, page=0, status_msg=wait)


async def _send_links_page(client, message, channels, page, status_msg=None, edit=False):
    if status_msg:
        await status_msg.delete()

    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    slice_ = channels[page * PAGE_SIZE : (page + 1) * PAGE_SIZE]

    results = await asyncio.gather(
        *[
            asyncio.gather(
                get_chat_info(client, cid),
                save_encoded_link(cid),
                asyncio.coroutine(encode)(str(cid)) if False else encode(str(cid)),
                return_exceptions=True,
            )
            for cid in slice_
        ],
        return_exceptions=True,
    )

    text = "<b>➤ Aʟʟ Cʜᴀɴɴᴇʟ Lɪɴᴋs:</b>\n\n"
    for i, result in enumerate(results):
        idx = page * PAGE_SIZE + i + 1
        cid = slice_[i]
        if isinstance(result, Exception) or result is None:
            text += f"<b>{idx}. Channel {cid}</b> (Error)\n\n"
            continue
        chat_info, b64_inv, b64_req = result
        if isinstance(chat_info, Exception):
            text += f"<b>{idx}. Channel {cid}</b> (Error)\n\n"
            continue
        await save_encoded_link2(cid, b64_req)
        normal_link  = f"https://t.me/{client.username}?start={b64_inv}"
        request_link = f"https://t.me/{client.username}?start=req_{b64_req}"
        text += (
            f"<b>{idx}. {chat_info.title}</b>\n"
            f"<b>➥ Nᴏʀᴍᴀʟ:</b> <code>{normal_link}</code>\n"
            f"<b>➤ Rᴇǫᴜᴇsᴛ:</b> <code>{request_link}</code>\n\n"
        )

    text += f"<b>📄 Pᴀɢᴇ {page + 1} / {total_pages}</b>"
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("• Pʀᴇᴠɪᴏᴜs •", callback_data=f"linkspage_{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("• Nᴇxᴛ •", callback_data=f"linkspage_{page+1}"))

    markup = InlineKeyboardMarkup([nav]) if nav else None
    if edit:
        await message.edit_text(text, reply_markup=markup)
    else:
        await message.reply(text, reply_markup=markup)


@Bot.on_callback_query(filters.regex(r"^linkspage_(\d+)$"))
async def cb_paginate_links(client: Bot, query):
    page = int(query.data.split("_")[1])
    wait = await query.message.edit_text("⏳")
    channels = await get_channels()
    await _send_links_page(client, query.message, channels, page, status_msg=wait, edit=True)


# ── /bulklink ──────────────────────────────────────────────────────────────────

@Bot.on_message(filters.command("bulklink") & is_owner_or_admin)
async def cmd_bulk_link(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply(
            "<b><blockquote expandable>ᴜsᴀɢᴇ: <code>/bulklink &lt;id1&gt; &lt;id2&gt; ...</code></blockquote></b>"
        )
    text = "<b>➤ Bᴜʟᴋ Lɪɴᴋ Gᴇɴᴇʀᴀᴛɪᴏɴ:</b>\n\n"
    for idx, id_str in enumerate(message.command[1:], 1):
        try:
            cid = int(id_str)
            chat = await client.get_chat(cid)
            b64_inv = await save_encoded_link(cid)
            b64_req = await encode(str(cid))
            await save_encoded_link2(cid, b64_req)
            normal_link  = f"https://t.me/{client.username}?start={b64_inv}"
            request_link = f"https://t.me/{client.username}?start=req_{b64_req}"
            text += (
                f"<b>{idx}. {chat.title} (<code>{cid}</code>)</b>\n"
                f"<b>➥ Nᴏʀᴍᴀʟ:</b> <code>{normal_link}</code>\n"
                f"<b>➤ Rᴇǫᴜᴇsᴛ:</b> <code>{request_link}</code>\n\n"
            )
        except Exception as e:
            text += f"<b>{idx}. {id_str}</b> (Error: {e})\n\n"
    await message.reply(text)


# ── /genlink ───────────────────────────────────────────────────────────────────

@Bot.on_message(filters.command("genlink") & filters.private & is_owner_or_admin)
async def cmd_gen_link(client: Bot, message: Message):
    """Wrap any external link in a bot start-link."""
    if len(message.command) < 2:
        return await message.reply("<b>ᴜsᴀɢᴇ: <code>/genlink &lt;url&gt;</code></b>")

    from config import DATABASE_CHANNEL
    link = message.command[1]
    try:
        sent = await client.send_message(DATABASE_CHANNEL, f"#LINK\n{link}")
        channel_id = sent.id
        b64_inv = await save_encoded_link(channel_id)
        b64_req = await encode(str(channel_id))
        await save_encoded_link2(channel_id, b64_req)
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {"$set": {"original_link": link}},
            upsert=True,
        )
        normal_link  = f"https://t.me/{client.username}?start={b64_inv}"
        request_link = f"https://t.me/{client.username}?start=req_{b64_req}"
        await message.reply(
            f"<b>✅ Lɪɴᴋ sᴛᴏʀᴇᴅ.</b>\n\n"
            f"<b>🔗 Nᴏʀᴍᴀʟ:</b> <code>{normal_link}</code>\n"
            f"<b>🔗 Rᴇǫᴜᴇsᴛ:</b> <code>{request_link}</code>"
        )
    except Exception as e:
        await message.reply(f"<b>Error:</b> <code>{e}</code>")


# ── /channels ──────────────────────────────────────────────────────────────────

@Bot.on_message(filters.command("channels") & is_owner_or_admin)
async def cmd_show_channel_ids(client: Bot, message: Message):
    wait = await message.reply("⏳")
    channels = await get_channels()
    if not channels:
        await wait.delete()
        return await message.reply(
            "<b><blockquote expandable>ɴᴏ ᴄʜᴀɴɴᴇʟs ғᴏᴜɴᴅ.</blockquote></b>"
        )
    await _send_channel_ids_page(client, message, channels, page=0, status_msg=wait)


async def _send_channel_ids_page(client, message, channels, page, status_msg=None, edit=False):
    if status_msg:
        await status_msg.delete()

    _PS = 10
    total_pages = (len(channels) + _PS - 1) // _PS
    slice_ = channels[page * _PS : (page + 1) * _PS]
    infos = await asyncio.gather(
        *[get_chat_info(client, cid) for cid in slice_], return_exceptions=True
    )

    text = "<b>➤ Cᴏɴɴᴇᴄᴛᴇᴅ Cʜᴀɴɴᴇʟs:</b>\n\n"
    for i, info in enumerate(infos):
        idx = page * _PS + i + 1
        cid = slice_[i]
        if isinstance(info, Exception) or info is None:
            text += f"<b>{idx}. Channel {cid}</b> (Error)\n"
        else:
            text += f"<b>{idx}. {info.title}</b> <code>({cid})</code>\n"
    text += f"\n<b>📄 Pᴀɢᴇ {page + 1} / {total_pages}</b>"

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("• Pʀᴇᴠɪᴏᴜs •", callback_data=f"channelids_{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("• Nᴇxᴛ •", callback_data=f"channelids_{page+1}"))

    markup = InlineKeyboardMarkup([nav]) if nav else None
    if edit:
        await message.edit_text(text, reply_markup=markup)
    else:
        await message.reply(text, reply_markup=markup)


@Bot.on_callback_query(filters.regex(r"^channelids_(\d+)$"))
async def cb_paginate_channel_ids(client: Bot, query):
    page = int(query.data.split("_")[1])
    wait = await query.message.edit_text("⏳")
    channels = await get_channels()
    await _send_channel_ids_page(client, query.message, channels, page, status_msg=wait, edit=True)
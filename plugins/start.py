# ╔══════════════════════════════════════════════╗
# ║         BotifyX_Pro_Botz — LinkVault Bot     ║
# ╚══════════════════════════════════════════════╝

import asyncio
import time
from asyncio import Lock
from collections import defaultdict
from datetime import datetime, timedelta

from pyrogram import filters
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

from bot import Bot
from config import (
    ABOUT_TXT,
    ADMINS,
    CHANNELS_TXT,
    OWNER_ID,
    START_MSG,
    START_PIC,
    FORCE_PIC,
    FORCE_MSG,
    FSUB_LINK_EXPIRY,
    BOT_STATS_TEXT,
)
from database.db import (
    add_user,
    del_user,
    full_userbase,
    get_channel_by_encoded_link,
    get_channel_by_encoded_link2,
    get_current_invite_link,
    get_fsub_channels,
    get_link_creation_time,
    get_original_link,
    save_invite_link,
    shun,
)
from helpers import decode, encode, get_readable_time, is_owner_or_admin
from plugins.posts import revoke_invite_after_5_minutes
from plugins.fsub import is_sub


# Per-channel lock to avoid concurrent invite-link generation
channel_locks: dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)

# Spam-protection
user_banned_until: dict[int, datetime] = {}

# Broadcast cancel state
is_canceled = False
cancel_lock = Lock()


# ═══════════════════════════════════════════════
#  /start
# ═══════════════════════════════════════════════

@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Bot, message: Message):
    user_id = message.from_user.id

    # Spam-ban check
    if user_id in user_banned_until and datetime.now() < user_banned_until[user_id]:
        return await message.reply_text(
            "<b><blockquote expandable>⏳ ʏᴏᴜ ᴀʀᴇ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ʙᴀɴɴᴇᴅ ᴅᴜᴇ ᴛᴏ sᴘᴀᴍ. Tʀʏ ʟᴀᴛᴇʀ.</blockquote></b>",
            parse_mode=ParseMode.HTML,
        )

    await add_user(user_id)
    # ── FSub check ─────────────────────────────────────────────────────────
    fsub_channels = await get_fsub_channels()

    if fsub_channels:
        for cid in fsub_channels:
              if not await is_sub(client, user_id, cid):
                return await not_joined(client, message)

    # ── Handle deep-link payload ────────────────────────────────────────────
    text = message.text
    if len(text) > 7:
        try:
            b64 = text.split(" ", 1)[1]
            is_request = b64.startswith("req_")
            if is_request:
                b64 = b64[4:]
                channel_id = await get_channel_by_encoded_link2(b64)
            else:
                channel_id = await get_channel_by_encoded_link(b64)

            if not channel_id:
                return await message.reply_text(
                    "<b><blockquote expandable>❌ ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ ʟɪɴᴋ.</blockquote></b>",
                    parse_mode=ParseMode.HTML,
                )

            # Check if it's a /genlink (raw URL stored in DB)
            original = await get_original_link(channel_id)
            if original:
                return await message.reply_text(
                    "<b><blockquote expandable>ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ!</blockquote></b>",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("• Pʀᴏᴄᴇᴇᴅ ᴛᴏ Lɪɴᴋ •", url=original)]]
                    ),
                    parse_mode=ParseMode.HTML,
                )

            # ── Generate / reuse invite link with per-channel lock ──────────
            async with channel_locks[channel_id]:
                old = await get_current_invite_link(channel_id)
                now = datetime.now()

                if old:
                    created_at = await get_link_creation_time(channel_id)
                    if created_at and (now - created_at).total_seconds() < 240:
                        invite_link      = old["invite_link"]
                        is_request_link  = old["is_request"]
                    else:
                        try:
                            await client.revoke_chat_invite_link(channel_id, old["invite_link"])
                        except Exception:
                            pass
                        invite = await client.create_chat_invite_link(
                            chat_id=channel_id,
                            expire_date=now + timedelta(minutes=10),
                            creates_join_request=is_request,
                        )
                        invite_link     = invite.invite_link
                        is_request_link = is_request
                        await save_invite_link(channel_id, invite_link, is_request_link)
                else:
                    invite = await client.create_chat_invite_link(
                        chat_id=channel_id,
                        expire_date=now + timedelta(minutes=10),
                        creates_join_request=is_request,
                    )
                    invite_link     = invite.invite_link
                    is_request_link = is_request
                    await save_invite_link(channel_id, invite_link, is_request_link)

            btn_text = "• ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ •" if is_request_link else "• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •"
            markup   = InlineKeyboardMarkup(
                [[InlineKeyboardButton(btn_text, url=invite_link)]]
            )

            wait = await message.reply_text("⏳")
            await wait.delete()

            await message.reply_text(
                "<b><blockquote expandable>✅ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ! ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ.</blockquote></b>",
                reply_markup=markup,
                parse_mode=ParseMode.HTML,
            )

            note = await message.reply_text(
                "<u><b>📌 ɴᴏᴛᴇ: ɪғ ᴛʜᴇ ʟɪɴᴋ ɪs ᴇxᴘɪʀᴇᴅ, ᴄʟɪᴄᴋ ᴛʜᴇ ᴏʀɪɢɪɴᴀʟ ᴘᴏsᴛ ʟɪɴᴋ ᴀɢᴀɪɴ.</b></u>",
                parse_mode=ParseMode.HTML,
            )
            asyncio.create_task(_delete_after(note, 300))
            asyncio.create_task(
                revoke_invite_after_5_minutes(client, channel_id, invite_link, is_request_link)
            )

        except Exception as e:
            print(f"[Start] deep-link error: {e}")
            await message.reply_text(
                "<b><blockquote expandable>❌ ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ ʟɪɴᴋ.</blockquote></b>",
                parse_mode=ParseMode.HTML,
            )

    # ── No payload — show welcome screen ────────────────────────────────────
    else:
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
                InlineKeyboardButton("• ᴄʜᴀɴɴᴇʟs", callback_data="channels"),
            ],
            [InlineKeyboardButton("• Cʟᴏsᴇ •", callback_data="close")],
        ])

        wait = await message.reply_text("⏳")
        await asyncio.sleep(0.1)
        await wait.delete()

        try:
            await message.reply_photo(
                photo=START_PIC,
                caption=START_MSG,
                reply_markup=markup,
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            await message.reply_text(
                START_MSG, reply_markup=markup, parse_mode=ParseMode.HTML
            )


# ═══════════════════════════════════════════════
#  FSub — not-joined helper
# ═══════════════════════════════════════════════

_chat_data_cache: dict = {}


async def not_joined(client: Bot, message: Message):
    """Send force-subscribe prompt to user."""
    user_id = message.from_user.id
    buttons = []

    try:
        all_channels = await shun.show_channels()
        for cid in all_channels:
            mode = await shun.get_channel_mode(cid)
            if not await is_sub(client, user_id, cid):
                try:
                    if cid in _chat_data_cache:
                        data = _chat_data_cache[cid]
                    else:
                        data = await client.get_chat(cid)
                        _chat_data_cache[cid] = data

                    if mode == "on" and not data.username:
                        invite = await client.create_chat_invite_link(
                            cid,
                            creates_join_request=True,
                            expire_date=(
                                datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY)
                                if FSUB_LINK_EXPIRY
                                else None
                            ),
                        )
                        link = invite.invite_link
                    else:
                        link = (
                            f"https://t.me/{data.username}"
                            if data.username
                            else (
                                await client.create_chat_invite_link(
                                    cid,
                                    expire_date=(
                                        datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY)
                                        if FSUB_LINK_EXPIRY
                                        else None
                                    ),
                                )
                            ).invite_link
                        )
                    buttons.append([InlineKeyboardButton(data.title, url=link)])
                except Exception as e:
                    print(f"[not_joined] {cid}: {e}")
                    continue

        try:
            if len(message.command) > 1:
                retry_url = f"https://t.me/{client.username}?start={message.command[1]}"
            else:
                retry_url = f"https://t.me/{client.username}"
            buttons.append([
                InlineKeyboardButton(
                    "♻️ Tʀʏ Aɢᴀɪɴ",
                    url=retry_url,
                )
            ])
        except IndexError:
            pass

        await message.reply_photo(
            photo=FORCE_PIC,
            caption=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name or "",
                username=(
                    None
                    if not message.from_user.username
                    else f"@{message.from_user.username}"
                ),
                mention=message.from_user.mention,
                id=message.from_user.id,
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except Exception as e:
        print(f"[not_joined] final error: {e}")


# ═══════════════════════════════════════════════
#  /status
# ═══════════════════════════════════════════════

@Bot.on_message(filters.command("status") & filters.private & is_owner_or_admin)
async def cmd_status(client: Bot, message: Message):
    start = time.time()
    temp  = await message.reply("<b><i>Processing...</i></b>", parse_mode=ParseMode.HTML)
    ping  = (time.time() - start) * 1000

    users  = await full_userbase()
    delta  = datetime.now() - client.uptime
    uptime = get_readable_time(delta.seconds)

    await temp.edit(
        f"<b>👥 Users: {len(users)}\n⏱ Uptime: {uptime}\n📶 Ping: {ping:.2f} ms</b>",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("• Cʟᴏsᴇ •", callback_data="close")]]
        ),
        parse_mode=ParseMode.HTML,
    )


# ═══════════════════════════════════════════════
#  Broadcast
# ═══════════════════════════════════════════════

@Bot.on_message(filters.command("cancel") & filters.private & is_owner_or_admin)
async def cmd_cancel_broadcast(client: Bot, message: Message):
    global is_canceled
    async with cancel_lock:
        is_canceled = True
    await message.reply_text("⛔ Broadcast cancelled.")


@Bot.on_message(filters.private & filters.command("broadcast") & is_owner_or_admin)
async def cmd_broadcast(client: Bot, message: Message):
    global is_canceled
    args = message.text.split()[1:]

    if not message.reply_to_message:
        msg = await message.reply(
            "Reply to a message to broadcast.\n\n"
            "Modes:\n"
            "`/broadcast normal`\n"
            "`/broadcast pin`\n"
            "`/broadcast delete 30`\n"
            "`/broadcast pin delete 30`\n"
            "`/broadcast silent`"
        )
        await asyncio.sleep(8)
        return await msg.delete()

    do_pin = do_delete = silent = False
    duration = 0
    mode_text = []

    i = 0
    while i < len(args):
        arg = args[i].lower()
        if arg == "pin":
            do_pin = True
            mode_text.append("PIN")
        elif arg == "delete":
            do_delete = True
            try:
                duration = int(args[i + 1])
                i += 1
            except (IndexError, ValueError):
                return await message.reply("<b>Provide valid duration. E.g. /broadcast delete 30</b>")
            mode_text.append(f"DELETE({duration}s)")
        elif arg == "silent":
            silent = True
            mode_text.append("SILENT")
        else:
            mode_text.append(arg.upper())
        i += 1

    if not mode_text:
        mode_text.append("NORMAL")

    async with cancel_lock:
        is_canceled = False

    query = await full_userbase()
    broadcast_msg = message.reply_to_message
    total = len(query)
    successful = blocked = deleted = unsuccessful = 0
    pls_wait = await message.reply(f"<i>Broadcasting: <b>{' + '.join(mode_text)}</b>...</i>")
    bar_len = 20
    progress_bar = ""
    last_pct = 0

    for idx, chat_id in enumerate(query, 1):
        async with cancel_lock:
            if is_canceled:
                await pls_wait.edit(f"›› BROADCAST CANCELED ❌")
                return

        try:
            sent = await broadcast_msg.copy(chat_id, disable_notification=silent)
            if do_pin:
                await client.pin_chat_message(chat_id, sent.id, both_sides=True)
            if do_delete:
                asyncio.create_task(_auto_delete(sent, duration))
            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                sent = await broadcast_msg.copy(chat_id, disable_notification=silent)
                if do_pin:
                    await client.pin_chat_message(chat_id, sent.id, both_sides=True)
                if do_delete:
                    asyncio.create_task(_auto_delete(sent, duration))
                successful += 1
            except Exception:
                unsuccessful += 1
        except UserIsBlocked:
            await del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await del_user(chat_id)
            deleted += 1
        except Exception:
            unsuccessful += 1
            await del_user(chat_id)

        pct = idx / total
        if pct - last_pct >= 0.05 or last_pct == 0:
            filled = int(pct * bar_len)
            progress_bar = "●" * filled + "○" * (bar_len - filled)
            await pls_wait.edit(
                f"<b>›› BROADCAST IN PROGRESS…\n\n"
                f"<blockquote>⏳ [{progress_bar}] <code>{pct:.0%}</code></blockquote>\n\n"
                f"›› Total: <code>{total}</code>\n"
                f"›› Done: <code>{successful}</code>\n"
                f"›› Blocked: <code>{blocked}</code>\n"
                f"›› Deleted: <code>{deleted}</code>\n"
                f"›› Failed: <code>{unsuccessful}</code></b>\n\n"
                f"<i>➪ /cancel to stop</i>"
            )
            last_pct = pct

    await pls_wait.edit(
        f"<b>›› BROADCAST COMPLETE ✅\n\n"
        f"<blockquote>[{progress_bar}] {pct:.0%}</blockquote>\n\n"
        f"›› Total: <code>{total}</code>\n"
        f"›› Done: <code>{successful}</code>\n"
        f"›› Blocked: <code>{blocked}</code>\n"
        f"›› Deleted: <code>{deleted}</code>\n"
        f"›› Failed: <code>{unsuccessful}</code></b>"
    )


# ═══════════════════════════════════════════════
#  Callback query router
# ═══════════════════════════════════════════════

@Bot.on_callback_query()
async def cb_router(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except Exception:
            pass

    elif data == "about":
        await query.edit_message_media(
            InputMediaPhoto("https://envs.sh/Wdj.jpg", ABOUT_TXT),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("• ʙᴀᴄᴋ", callback_data="start"),
                    InlineKeyboardButton("ᴄʟᴏsᴇ •", callback_data="close"),
                ]
            ]),
        )

    elif data == "channels":
        await query.edit_message_media(
            InputMediaPhoto("https://envs.sh/Wdj.jpg", CHANNELS_TXT),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("• ʙᴀᴄᴋ", callback_data="start"),
                    InlineKeyboardButton("ʜᴏᴍᴇ •", callback_data="start"),
                ]
            ]),
        )

    elif data in ("start", "home"):
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
                InlineKeyboardButton("• ᴄʜᴀɴɴᴇʟs", callback_data="channels"),
            ],
            [InlineKeyboardButton("• Cʟᴏsᴇ •", callback_data="close")],
        ])
        try:
            await query.edit_message_media(
                InputMediaPhoto(START_PIC, START_MSG), reply_markup=markup
            )
        except Exception:
            await query.edit_message_text(
                START_MSG, reply_markup=markup, parse_mode=ParseMode.HTML
            )

    # FSub channel mode callbacks (from fsub.py panel)
    elif data.startswith("rfs_ch_"):
        cid = int(data.split("_")[2])
        try:
            chat = await client.get_chat(cid)
            mode = await shun.get_channel_mode(cid)
            status = "🟢 ᴏɴ" if mode == "on" else "🔴 ᴏғғ"
            new_mode = "off" if mode == "on" else "on"
            await query.message.edit_text(
                f"<b>Channel:</b> {chat.title}\n<b>FSub Mode:</b> {status}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}",
                        callback_data=f"rfs_toggle_{cid}_{new_mode}",
                    )],
                    [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")],
                ]),
            )
        except Exception:
            await query.answer("Failed to fetch channel info", show_alert=True)

    elif data.startswith("rfs_toggle_"):
        parts = data.split("_")
        cid, action = int(parts[2]), parts[3]
        mode = "on" if action == "on" else "off"
        await shun.set_channel_mode(cid, mode)
        await query.answer(f"Mode set to {mode.upper()}")
        chat = await client.get_chat(cid)
        status   = "🟢 ON" if mode == "on" else "🔴 OFF"
        new_mode = "off" if mode == "on" else "on"
        await query.message.edit_text(
            f"<b>Channel:</b> {chat.title}\n<b>FSub Mode:</b> {status}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}",
                    callback_data=f"rfs_toggle_{cid}_{new_mode}",
                )],
                [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")],
            ]),
        )

    elif data == "fsub_back":
        channels = await shun.show_channels()
        buttons = []
        for cid in channels:
            try:
                chat = await client.get_chat(cid)
                mode = await shun.get_channel_mode(cid)
                icon = "🟢" if mode == "on" else "🔴"
                buttons.append([InlineKeyboardButton(f"{icon} {chat.title}", callback_data=f"rfs_ch_{cid}")])
            except Exception:
                continue
        await query.message.edit_text(
            "sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴛᴏɢɢʟᴇ ɪᴛs ғsᴜʙ ᴍᴏᴅᴇ:",
            reply_markup=InlineKeyboardMarkup(buttons),
        )


# ═══════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════

async def _delete_after(msg, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass


async def _auto_delete(sent_msg, duration: int):
    await asyncio.sleep(duration)
    try:
        await sent_msg.delete()
    except Exception:
        pass
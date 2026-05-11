# ╔══════════════════════════════════════════════╗
# ║         BotifyX_Pro_Botz — LinkVault Bot     ║
# ╚══════════════════════════════════════════════╝

from pyrogram import Client, filters
from pyrogram.types import Message

from config import OWNER_ID
from database.db import set_approval_off, is_approval_off, add_admin, remove_admin, list_admins


@Client.on_message(filters.command("addadmin") & filters.user(OWNER_ID))
async def cmd_add_admin(client: Client, message: Message):
    if len(message.command) != 2 or not message.command[1].isdigit():
        return await message.reply_text("ᴜsᴀɢᴇ: <code>/addadmin {user_id}</code>")
    uid = int(message.command[1])
    if await add_admin(uid):
        await message.reply_text(f"✅ <code>{uid}</code> ᴀᴅᴅᴇᴅ ᴀs ᴀᴅᴍɪɴ.")
    else:
        await message.reply_text(f"❌ Fᴀɪʟᴇᴅ ᴛᴏ ᴀᴅᴅ <code>{uid}</code>.")


@Client.on_message(filters.command("deladmin") & filters.user(OWNER_ID))
async def cmd_del_admin(client: Client, message: Message):
    if len(message.command) != 2 or not message.command[1].isdigit():
        return await message.reply_text("ᴜsᴀɢᴇ: <code>/deladmin {user_id}</code>")
    uid = int(message.command[1])
    if await remove_admin(uid):
        await message.reply_text(f"✅ <code>{uid}</code> ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴀᴅᴍɪɴs.")
    else:
        await message.reply_text(f"❌ Fᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ <code>{uid}</code>.")


@Client.on_message(filters.command("admins") & filters.user(OWNER_ID))
async def cmd_list_admins(client: Client, message: Message):
    admins = await list_admins()
    if not admins:
        return await message.reply_text("ɴᴏ ᴀᴅᴍɪɴs ᴄᴏɴғɪɢᴜʀᴇᴅ.")
    text = "<b>🛡 Aᴅᴍɪɴ ʟɪsᴛ:</b>\n" + "\n".join(f"• <code>{uid}</code>" for uid in admins)
    await message.reply_text(text)
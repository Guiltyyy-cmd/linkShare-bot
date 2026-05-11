<div align="center">

<img src="https://i.pinimg.com/736x/3d/45/cb/3d45cbb976ed3fb5dc7265afd9dfbf82.jpg" alt="Linkshare Bot Banner" width="100%" style="border-radius:12px"/>

<h1 align="center">
  <img src="https://readme-typing-svg.herokuapp.com?color=FF69B4&width=500&lines=Welcome+to+LinkShareBot+by+BotifyXBotz;Your+Ultimate+Telegram+Link+Sharing+Bot" />
</h1>

<br/>

# 🎊 Link-Share Bot

### *Secure Temporary Invite Links for Telegram Channels*

<br/>

![Python](https://img.shields.io/badge/Python-3.11+-red?style=for-the-badge&logo=python&logoColor=white)
![Pyrogram](https://img.shields.io/badge/Pyrogram-v2-darkred?style=for-the-badge&logo=telegram&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Motor-grey?style=for-the-badge&logo=mongodb&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-black?style=for-the-badge)
![Maintained](https://img.shields.io/badge/Maintained-Yes-red?style=for-the-badge)

<br/>

[![BotifyX-Botz](https://img.shields.io/badge/🔥%20Hub-BotifyX__Pro__Botz-red?style=flat-square&logo=telegram)](https://t.me/BotifyX_Pro_Botz)
[![Support Group](https://img.shields.io/badge/💬%20Support-%20Group-darkgrey?style=flat-square&logo=telegram)](https://t.me/+ij3pcPOXv2U4MDll)

</div>

---

<div align="center">

> **LinkShare Bot** generates self-expiring Telegram invite links on demand, letting your channels stay safe from copyright takedowns, scrapers, and ban-waves — while giving real users a frictionless join experience.

</div>

---

## ✨ Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Environment Variables](#-environment-variables)
- [Deployment](#-deployment)
  - [Local (Python)](#local-python)
  - [Docker](#docker)
  - [Heroku / Railway](#heroku--railway)
- [Commands Reference](#-commands-reference)
- [Force-Subscribe (FSub)](#-force-subscribe-fsub)
- [Auto-Approve](#-auto-approve)
- [Broadcast](#-broadcast)
- [Credits](#-credits)

---

## 🔴 Features

| Feature | Description |
|---|---|
| 🔗 **Temp Invite Links** | Generates 10-minute expiring invite links per channel click |
| 🔒 **Request Links** | Optionally use join-request links (needs admin approval) |
| 📦 **Bulk Links** | Generate links for multiple channels at once |
| 🔁 **Smart Reuse** | Reuses unexpired links to reduce Telegram API calls |
| 🛡 **Force-Subscribe** | Users must join set channels before getting a link |
| ✅ **Auto-Approve** | Automatically approves join requests with welcome DM |
| 📢 **Broadcast** | Send messages to all bot users with pin/delete/silent modes |
| 🔑 **Admin System** | Owner can add/remove bot admins stored in MongoDB |
| 📊 **Status** | Real-time uptime and user-count stats |
| 🌐 **Web Health Check** | Aiohttp endpoint for uptime monitoring |
| 🐳 **Docker Ready** | Dockerfile + Procfile included |

---

## ⚫ Project Structure

```
LinkVaultBot/
│
├── main.py                  # Entry point
├── bot.py                   # Bot client (Pyrogram)
├── config.py                # All env vars & logging
├── helpers.py               # Filters, encode/decode, uptime
│
├── database/
│   └── db.py                # MongoDB collections + DataBase class
│
└── plugins/
    ├── __init__.py           # Aiohttp web server
    ├── route.py              # Health-check route
    ├── start.py              # /start, broadcast, callback router
    ├── posts.py              # Channel management & link commands
    ├── fsub.py               # Force-Subscribe system
    ├── autoapprove.py        # Auto-approve join requests
    ├── admin.py              # Bot admin management
    └── misc.py               # /stats and other small commands
```

---

## 🔴 Environment Variables

Create a `.env` file or set these in your hosting platform:

### Required

| Variable | Description |
|---|---|
| `TG_BOT_TOKEN` | Your bot token from [@BotFather](https://t.me/BotFather) |
| `APP_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Telegram API Hash |
| `DB_URI` | MongoDB connection URI (e.g. `mongodb+srv://...`) |

### Important

| Variable | Default | Description |
|---|---|---|
| `OWNER_ID` | `123456789` | Your Telegram user ID |
| `DATABASE_CHANNEL` | — | Channel ID where `/genlink` stores raw URLs |
| `DB_NAME` | `linkvault` | MongoDB database name |
| `PORT` | `8080` | Web server port |
| `ADMINS` | OWNER_ID | Space-separated extra admin IDs |

### Auto-Approve

| Variable | Default | Description |
|---|---|---|
| `CHAT_ID` | — | Space-separated channel IDs to watch for join requests |
| `APPROVED_WELCOME` | `on` | `on` / `off` — send welcome DM on approval |
| `APPROVED_WELCOME_TEXT` | *Built-in* | Custom welcome message (supports `{mention}`, `{title}`) |

### Force-Subscribe

| Variable | Default | Description |
|---|---|---|
| `FSUB_CHANNELS` | — | Space-separated channel IDs users must join |
| `FSUB_LINK_EXPIRY` | `0` | Seconds until FSub invite links expire (`0` = no expiry) |
| `FORCE_PIC` | *Built-in* | Image shown on the FSub prompt |
| `FORCE_MSG` | *Built-in* | Caption for FSub prompt (supports `{mention}`, `{id}`, `{username}`) |

### Appearance

| Variable | Default | Description |
|---|---|---|
| `START_PIC` | *Built-in* | Photo shown on `/start` |
| `START_MESSAGE` | *Built-in* | Caption on start |
| `HELP_MESSAGE` | *Built-in* | Help text |
| `ABOUT_MESSAGE` | *Built-in* | About text |

---

## ⚫ Deployment

### Local (Python)

```bash
# 1. Clone & enter
git clone https://github.com/botifyx-bots/linkShare-bot
cd linkShare-bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set env vars (copy and fill)
cp .env.example .env

# 4. Run
python main.py
```

### Docker

```dockerfile
# Dockerfile already included — just build & run:
docker build -t linkshare-bot .
docker run --env-file .env linkshare-bot
```

### Heroku / Railway

```bash
# Procfile already set:
#   worker: python main.py

# Push to Heroku:
heroku create
heroku config:set TG_BOT_TOKEN=... APP_ID=... API_HASH=... DB_URI=...
git push heroku main
```

---

## 🔴 Commands Reference

### 👤 User Commands

| Command | Description |
|---|---|
| `/start` | Launch the bot / get invite link via deep-link |

### 🛡 Admin / Owner Commands

#### Channel Management

| Command | Description |
|---|---|
| `/addchat <id>` | Add a channel to the bot |
| `/delchat <id>` | Remove a channel |
| `/channels` | List all connected channels (ID + name) |
| `/ch_links` | Browse channels with invite-link buttons |
| `/reqlink` | Browse channels with join-request-link buttons |
| `/links` | Show all channels with both link types (paginated) |
| `/bulklink <id1> <id2> ...` | Generate links for multiple channels at once |
| `/genlink <url>` | Wrap any external URL in a bot start-link |

#### Force-Subscribe

| Command | Description |
|---|---|
| `/addfsub <id>` | Add a channel to the FSub list |
| `/delfsub <id>` | Remove a channel from the FSub list |
| `/listfsub` | Show all FSub channels and their modes |
| `/fsubmode <id> <on\|off>` | Toggle request mode (`on`) vs invite mode (`off`) |

#### Auto-Approve

| Command | Description |
|---|---|
| `/reqtime <secs>` | Set delay before approving join requests |
| `/reqmode <on\|off>` | Enable or disable auto-approve globally |
| `/approveoff <id>` | Disable auto-approve for a specific channel |
| `/approveon <id>` | Re-enable auto-approve for a specific channel |

#### Bot Admin Management

| Command | Description |
|---|---|
| `/addadmin <user_id>` | Grant admin access to a user |
| `/deladmin <user_id>` | Revoke admin access |
| `/admins` | List all admins |

#### Miscellaneous

| Command | Description |
|---|---|
| `/status` | Show uptime, user count, and ping |
| `/stats` | Short uptime summary |
| `/broadcast` | Broadcast to all users (see below) |
| `/cancel` | Cancel an in-progress broadcast |

---

## 🔴 Force-Subscribe (FSub)

The FSub system blocks users from receiving invite links until they join your required channels.

**Setup:**
```
1. Add your bot as admin in the FSub channel.
2. /addfsub -100xxxxxxxxxx
3. Optionally: /fsubmode -100xxxxxxxxxx on   (request-link mode)
```

**Flow:**
- User clicks a post link → bot checks all FSub channels
- If not joined → bot shows "Join these channels" prompt with buttons
- User joins → taps ♻️ Try Again → link is delivered

**Modes per channel:**
- `off` (default) — standard direct invite link
- `on` — join-request link (requires admin approval, good for private channels)

---

## ⚫ Auto-Approve

When enabled, the bot automatically approves join requests for the channels specified in `CHAT_ID` and sends the user a personalized welcome DM.

**Toggle globally:**
```
/reqmode on
/reqmode off
```

**Per-channel override:**
```
/approveoff -100xxxxxxxxxx   # disable for this channel
/approveon  -100xxxxxxxxxx   # re-enable
```

---

## 🔴 Broadcast

Send a message to every bot user.

```
Reply to a message, then:
/broadcast normal           → plain send
/broadcast pin              → send + pin
/broadcast delete 60        → send + auto-delete after 60 seconds
/broadcast pin delete 30    → send + pin + auto-delete after 30 seconds
/broadcast silent           → send without notification sound
```

A live progress bar updates every 5%. Use `/cancel` to abort mid-broadcast.

---

## ⚫ Credits

<div align="center">

| Role | Person / Channel |
|---|---|
| 🔧 **Bot Hub** | [@BotifyX_Pro_Botz](https://t.me/BotifyX_Pro_Botz) |
| 💬 **Support** | [LinkVault Support](https://t.me/+ij3pcPOXv2U4MDll) |
| 🌐 **Original Base** | [proyato](https://github.com/Codeflix-Bots/Links-Share-Bot) |
| 📚 **Libraries** | [Pyrogram](https://docs.pyrogram.org/) · [Motor](https://motor.readthedocs.io/) · [aiohttp](https://docs.aiohttp.org/) |

</div>

<br/>

> ⚠️ **Note:** Do not remove credits. This project is maintained openly for the community. If you fork it, keep attribution intact.

---

<div align="center">

<img src="https://i.pinimg.com/736x/e1/14/e4/e114e4152e1a7035c958ee66594bf399.jpg" width="60px" style="border-radius:50%"/>

**Made with ❤️ by [BotifyX-Botz](https://t.me/BotifyX_Pro_Botz)**

[![Telegram](https://img.shields.io/badge/Telegram-Join%20Hub-red?style=for-the-badge&logo=telegram)](https://t.me/BotifyX_Pro_Botz)
[![Support](https://img.shields.io/badge/Support%20Chat-Join-darkgrey?style=for-the-badge&logo=telegram)](https://t.me/+ij3pcPOXv2U4MDll)

</div>

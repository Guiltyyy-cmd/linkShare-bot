from aiohttp import web

routes = web.RouteTableDef()
# ╔══════════════════════════════════════════════╗
# ║         BotifyX_Pro_Botz — Linkshare Bot     ║
# ║   Telegram: https://t.me/BotifyX_Pro_Botz    ║
# ╚══════════════════════════════════════════════╝

@routes.get("/", allow_head=True)
async def root_handler(request):
    return web.json_response({"status": "ok", "bot": "BotifyX — Linkshare Bot"})
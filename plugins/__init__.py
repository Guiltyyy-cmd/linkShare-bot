from aiohttp import web
from .route import routes
# ╔══════════════════════════════════════════════╗
# ║         BotifyX_Pro_Botz — Linkshare Bot     ║
# ║   Telegram: https://t.me/BotifyX_Pro_Botz    ║
# ╚══════════════════════════════════════════════╝
async def web_server():
    app = web.Application(client_max_size=30_000_000)
    app.add_routes(routes)
    return app
import os

# ─── Shared (both Vercel & Bot) ───
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID", "")
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")
DISCORD_REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI", "")
DISCORD_GUILD_ID = os.environ.get("DISCORD_GUILD_ID", "")
DISCORD_VERIFIED_ROLE_ID = os.environ.get("DISCORD_VERIFIED_ROLE_ID", "")
DISCORD_ADMIN_ROLE_ID = os.environ.get("DISCORD_ADMIN_ROLE_ID", "")
DISCORD_LOG_CHANNEL_ID = os.environ.get("DISCORD_LOG_CHANNEL_ID", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
OWNER_ID = os.environ.get("OWNER_ID", "")

# ─── Bot only ───
DATABASE_PATH = os.environ.get("DATABASE_PATH", "data.db")

# ─── Web only ───
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 5000))

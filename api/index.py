import os
import secrets
import requests
from flask import Flask, redirect, request, jsonify, render_template
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from supabase_db import *
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config["TEMPLATE_FOLDER"] = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
app.config["STATIC_FOLDER"] = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

DISCORD_API = "https://discord.com/api/v10"
SCOPES = "identify email guilds.join"
CLIENT_ID = config.DISCORD_CLIENT_ID
CLIENT_SECRET = config.DISCORD_CLIENT_SECRET
REDIRECT_URI = config.DISCORD_REDIRECT_URI
GUILD_ID = config.DISCORD_GUILD_ID
VERIFIED_ROLE_ID = config.DISCORD_VERIFIED_ROLE_ID
BOT_TOKEN = config.BOT_TOKEN
WEBHOOK_URL = config.WEBHOOK_URL


def exchange_code(code):
    data = {
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code", "code": code,
        "redirect_uri": REDIRECT_URI, "scope": SCOPES,
    }
    r = requests.post(f"{DISCORD_API}/oauth2/token", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    return r.json()


def get_user(access_token):
    r = requests.get(f"{DISCORD_API}/users/@me", headers={"Authorization": f"Bearer {access_token}"})
    return r.json()


def add_to_guild(user_id, access_token):
    r = requests.put(
        f"{DISCORD_API}/guilds/{GUILD_ID}/members/{user_id}",
        json={"access_token": access_token},
        headers={"Authorization": f"Bot {BOT_TOKEN}", "Content-Type": "application/json"},
    )
    return r.ok


def assign_role(user_id):
    r = requests.put(
        f"{DISCORD_API}/guilds/{GUILD_ID}/members/{user_id}/roles/{VERIFIED_ROLE_ID}",
        headers={"Authorization": f"Bot {BOT_TOKEN}"},
    )
    return r.ok


def send_webhook_embed(embed):
    if not WEBHOOK_URL:
        return
    requests.post(WEBHOOK_URL, json={"username": "Verification", "embeds": [embed]})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/verify")
def verify_page():
    state = secrets.token_urlsafe(16)
    discord_url = (
        f"https://discord.com/api/oauth2/authorize?"
        f"client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        f"&response_type=code&scope={SCOPES.replace(' ', '%20')}"
        f"&state={state}&prompt=consent"
    )
    return render_template("verify.html", discord_url=discord_url, error="")


@app.route("/callback")
def callback():
    code = request.args.get("code")
    error = request.args.get("error")
    if error or not code:
        return render_template("verify.html", discord_url="#", error="Authorization denied.")

    token_data = exchange_code(code)
    if "access_token" not in token_data:
        return render_template("verify.html", discord_url="#", error="Failed to authenticate.")

    user = get_user(token_data["access_token"])
    discord_id = user["id"]
    discord_tag = f"{user['username']}#{user['discriminator']}" if user.get("discriminator") and user["discriminator"] != "0" else user["username"]
    email = user.get("email", "")
    ip = request.headers.get("CF-Connecting-IP") or request.headers.get("X-Forwarded-For") or request.remote_addr or ""
    user_agent = request.headers.get("User-Agent", "")

    add_verification(discord_id, discord_tag, email, ip, user_agent)
    add_log(discord_id, "verified", f"Email: {email}", ip)

    add_to_guild(discord_id, token_data["access_token"])
    assign_role(discord_id)

    avatar = f"https://cdn.discordapp.com/avatars/{discord_id}/{user.get('avatar')}.png" if user.get("avatar") else ""
    send_webhook_embed({
        "title": "New Verification",
        "color": 0x57F287,
        "fields": [
            {"name": "User", "value": f"{discord_tag} (`{discord_id}`)", "inline": False},
            {"name": "Email", "value": f"||{email}||" if email else "None", "inline": True},
            {"name": "IP", "value": f"||{ip}||" if ip else "Unknown", "inline": True},
        ],
        "thumbnail": {"url": avatar} if avatar else {},
        "footer": {"text": f"UA: {user_agent[:60]}"},
    })

    return render_template("success.html", tag=discord_tag, email=email or "No email connected")


@app.route("/dashboard")
def dashboard():
    verifications = get_all_verifications()
    logs = get_logs(200)
    total, today = stats()
    return render_template("dashboard.html", verifications=verifications, logs=logs, total=total, today=today)


@app.route("/api/verifications")
def api_verifications():
    return jsonify(get_all_verifications())


@app.route("/api/stats")
def api_stats():
    total, today = stats()
    return jsonify({"total": total, "today": today})


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "")
    return jsonify(search_verifications(q))


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False)

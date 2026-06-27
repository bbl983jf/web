"""Supabase REST API wrapper — lightweight, no SDK needed."""
import requests
from config import SUPABASE_URL, SUPABASE_KEY

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in environment.")

BASE = f"{SUPABASE_URL}/rest/v1"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def _get(table, params=None):
    r = requests.get(f"{BASE}/{table}", headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()


def _post(table, data):
    r = requests.post(f"{BASE}/{table}", headers=HEADERS, json=data)
    r.raise_for_status()
    return r.json()


def _delete(table, query):
    headers = {**HEADERS, "Prefer": "return=representation"}
    r = requests.delete(f"{BASE}/{table}", headers=headers, params=query)
    r.raise_for_status()
    return r.json()


# ─── Verifications ───

def add_verification(discord_id, discord_tag, email, ip, user_agent=""):
    data = {
        "discord_id": discord_id,
        "discord_tag": discord_tag,
        "email": email,
        "ip": ip,
        "user_agent": user_agent,
    }
    # upsert
    headers = {**HEADERS, "Prefer": "resolution=merge-duplicates,return=representation"}
    r = requests.post(f"{BASE}/verifications", headers=headers, json=data, params={"on_conflict": "discord_id"})
    r.raise_for_status()
    return r.json()


def remove_verification(discord_id):
    return _delete("verifications", {"discord_id": f"eq.{discord_id}"})


def get_verification(discord_id):
    rows = _get("verifications", {"discord_id": f"eq.{discord_id}", "limit": 1})
    return rows[0] if rows else None


def get_all_verifications():
    return _get("verifications", {"order": "verified_at.desc"})


def search_verifications(term):
    or_query = f"discord_id.ilike.%{term}%,discord_tag.ilike.%{term}%,email.ilike.%{term}%,ip.ilike.%{term}%"
    return _get("verifications", {"or": f"({or_query})", "order": "verified_at.desc"})


def stats():
    all_v = get_all_verifications()
    total = len(all_v)
    from datetime import datetime, timezone
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    today = sum(1 for v in all_v if v.get("verified_at", "") >= today_start)
    return total, today


# ─── Warns ───

def add_warn(discord_id, moderator_id, reason):
    data = {"discord_id": discord_id, "moderator_id": moderator_id, "reason": reason}
    rows = _post("warns", data)
    count = len(_get("warns", {"discord_id": f"eq.{discord_id}"}))
    return count


def get_warns(discord_id):
    return _get("warns", {"discord_id": f"eq.{discord_id}", "order": "warned_at.desc"})


# ─── Logs ───

def add_log(discord_id, action, detail="", ip=""):
    return _post("logs", {"discord_id": discord_id, "action": action, "detail": detail, "ip": ip})


def get_logs(limit=100):
    return _get("logs", {"order": "id.desc", "limit": limit})

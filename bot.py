import os
import json
import logging
from pathlib import Path
from typing import Optional

from telegram import Update, ChatMemberUpdated
from telegram.constants import ChatType
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ChatMemberHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# === Config via environment variables ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
START_MESSAGE = os.getenv("START_MESSAGE", "✅ Bot active! Mujhe channel/group me admin banao (Ban permission) — jo bhi leave karega, main usko ban karke ban list me add kar dunga.")
OWNER_ID = os.getenv("OWNER_ID")  # optional: for owner-only commands like /unban

# Simple JSON storage (Heroku filesystem is ephemeral; use a DB/Redis for real persistence)
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
BANS_FILE = DATA_DIR / "bans.json"

def load_bans():
    try:
        with open(BANS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        logger.exception("Failed to load bans.json: %s", e)
        return {}

def save_bans(bans):
    try:
        with open(BANS_FILE, "w", encoding="utf-8") as f:
            json.dump(bans, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.exception("Failed to save bans.json: %s", e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(START_MESSAGE)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("pong ✅")

def is_owner(user_id: Optional[int]) -> bool:
    if not OWNER_ID:
        return False
    try:
        return int(OWNER_ID) == int(user_id)
    except:
        return False

async def banlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bans = load_bans()
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        return
    chat_key = str(chat_id)
    items = bans.get(chat_key, [])
    if not items:
        await update.message.reply_text("📭 Ban list khaali hai (is chat ke liye).")
        return

    lines = []
    for entry in items:
        user_id = entry.get("user_id")
        name = entry.get("name", "")
        lines.append(f"- {name} (ID: {user_id})")
    text = "🚫 Ban List:\n" + "\n".join(lines)
    await update.message.reply_text(text)

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Owner-only convenience command: /unban <user_id>
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Unauthorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /unban <user_id>")
        return
    try:
        target_id = int(context.args[0])
    except:
        await update.message.reply_text("Galat user_id.")
        return
    chat = update.effective_chat
    try:
        await context.bot.unban_chat_member(chat_id=chat.id, user_id=target_id, only_if_banned=True)
        await update.message.reply_text(f"User {target_id} unbanned (agar pehle banned tha to).")
    except Exception as e:
        await update.message.reply_text(f"Unban error: {e}")

async def on_bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmu: ChatMemberUpdated = update.my_chat_member
    chat = cmu.chat
    try:
        await context.bot.send_message(
            chat_id=chat.id,
            text="👋 Namaste! Main ready hoon. Mujhe admin banayein (ban permission) taki jo bhi leave kare, main usko turant ban karke ban list me add kar doon."
        )
    except Exception as e:
        logger.info("Could not greet in chat %s: %s", chat.id, e)

async def handle_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban users who leave a channel/group, then add to ban list."""
    cmu: ChatMemberUpdated = update.chat_member
    chat = cmu.chat
    new = cmu.new_chat_member
    user = cmu.from_user

    if chat.type not in (ChatType.CHANNEL, ChatType.SUPERGROUP, ChatType.GROUP):
        return

    left_now = new.status in ("left", "kicked")
    if not left_now:
        return

    try:
        await context.bot.ban_chat_member(chat_id=chat.id, user_id=user.id)

        bans = load_bans()
        chat_key = str(chat.id)
        bans.setdefault(chat_key, [])
        if not any(str(entry.get("user_id")) == str(user.id) for entry in bans[chat_key]):
            bans[chat_key].append({"user_id": user.id, "name": user.full_name})
            save_bans(bans)

        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"🚫 {user.full_name} (ID: {user.id}) left — banned & added to ban list."
            )
        except Exception:
            pass

    except Exception as e:
        logger.exception("Ban failed: %s", e)
        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"⚠️ {user.full_name} left, par ban nahi ho paya: {e}"
            )
        except Exception:
            pass

async def fallback_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Commands:\n/start – start msg\n/banlist – is chat ki ban list dekho\n/ping – health check")

def main():
    if not BOT_TOKEN:
        raise SystemExit("Please set BOT_TOKEN env var")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("banlist", banlist))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("unban", unban))

    app.add_handler(ChatMemberHandler(on_bot_added, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(ChatMemberHandler(handle_member_update, ChatMemberHandler.CHAT_MEMBER))

    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT, fallback_text))

    app.run_polling(allowed_updates=["message", "chat_member", "my_chat_member"])

if __name__ == "__main__":
    main()
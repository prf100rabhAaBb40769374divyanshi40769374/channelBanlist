import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BANLIST_FILE = "banlist.json"

# Banlist load/save helpers
def load_banlist():
    if not os.path.exists(BANLIST_FILE):
        return []
    with open(BANLIST_FILE, "r") as f:
        return json.load(f)

def save_banlist(banlist):
    with open(BANLIST_FILE, "w") as f:
        json.dump(banlist, f, indent=2)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await update.message.reply_text(
        f"✅ Bot activated in: {chat.title or 'Private Chat'}\n\n"
        "अब ये यहाँ leave hone wale members को ban करेगा और banlist में save करेगा।"
    )

# jab koi user leave kare
async def member_left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    left_user = update.message.left_chat_member

    try:
        # ban user
        await context.bot.ban_chat_member(chat.id, left_user.id)

        # banlist update
        banlist = load_banlist()
        ban_entry = {
            "user_id": left_user.id,
            "first_name": left_user.first_name,
            "chat_id": chat.id,
            "chat_title": chat.title
        }
        banlist.append(ban_entry)
        save_banlist(banlist)

        await update.message.reply_text(
            f"❌ {left_user.first_name} को ban किया गया और banlist में save कर दिया।"
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ban failed: {e}")

# /banlist
async def banlist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    banlist = load_banlist()
    if not banlist:
        await update.message.reply_text("📂 Banlist खाली है।")
        return

    text = "📂 Banlist:\n\n"
    for entry in banlist:
        text += f"👤 {entry['first_name']} (ID: {entry['user_id']}) in {entry['chat_title']}\n"

    await update.message.reply_text(text)

def main():
    TOKEN = os.environ.get("BOT_TOKEN")  # Token env variable se le raha hai (Heroku me set karna hoga)
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("banlist", banlist_cmd))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, member_left))

    app.run_polling()

if __name__ == "__main__":
    main()

from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

BOT_TOKEN = "8140165897:AAGIPaC4ReOYti0Y2mU8i5-EwStrZkIph5w"

# Banlist memory (chalega jab tak bot restart nahi hota)
banlist = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await update.message.reply_text(f"✅ Bot activated in: {chat.type}\n\nअब ये यहाँ leave hone wale members को ban करेगा और banlist में save करेगा।")

# Member left event
async def member_left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    left_user = update.message.left_chat_member

    try:
        # Ban user permanently
        await context.bot.ban_chat_member(chat.id, left_user.id)

        # Banlist me save karo
        if chat.id not in banlist:
            banlist[chat.id] = []
        banlist[chat.id].append(left_user.id)

        await context.bot.send_message(
            chat_id=chat.id,
            text=f"❌ {left_user.first_name} को ban कर दिया गया है। अब वो दोबारा इस channel को join नहीं कर पाएंगे।"
        )
    except Exception as e:
        print("Error banning:", e)

# Banlist check command
async def show_banlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.id not in banlist or len(banlist[chat.id]) == 0:
        await update.message.reply_text("📂 Banlist खाली है।")
    else:
        banned_users = "\n".join([str(uid) for uid in banlist[chat.id]])
        await update.message.reply_text(f"📂 Banlist:\n{banned_users}")

# Run the bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("banlist", show_banlist))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, member_left))

    app.run_polling()

if __name__ == "__main__":
    main()

from telegram.ext import ApplicationBuilder, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

BOT_TOKEN = "8140165897:AAGIPaC4ReOYti0Y2mU8i5-EwStrZkIph5w"

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot started! मैं अब इस channel/group को monitor कर रहा हूँ।")

# Member leave event
async def member_left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    left_user = update.message.left_chat_member

    try:
        await context.bot.ban_chat_member(chat.id, left_user.id)
        await update.message.reply_text(f"❌ {left_user.first_name} को ban कर दिया गया है क्योंकि उसने group छोड़ दिया।")
    except Exception as e:
        print("Error banning:", e)

# Run the bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.COMMAND & filters.Regex("^/start$"), start))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, member_left))

    app.run_polling()

if __name__ == "__main__":
    main()

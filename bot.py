import os
from telegram.ext import ApplicationBuilder, ChatMemberHandler, CommandHandler
from telegram import ChatMember, Update
from telegram.ext import ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ---------------- Starting SMS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\n"
        "✅ I am active.\n"
        "📢 Add me to any channel/group as admin (with Ban permission),\n"
        "so that I can automatically ban members who leave."
    )

# ---------------- Ban on Leave ----------------
async def track_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    status_change = result.difference().get("status")

    if status_change is None:
        return

    # agar user ne leave/ kick kiya hai
    if result.old_chat_member.status in [ChatMember.MEMBER, ChatMember.RESTRICTED] and \
       result.new_chat_member.status in [ChatMember.LEFT, ChatMember.KICKED]:
        user_id = result.old_chat_member.user.id
        chat_id = update.effective_chat.id

        try:
            await context.bot.ban_chat_member(chat_id, user_id)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🚫 {result.old_chat_member.user.mention_html()} left and has been banned.",
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Failed to ban user: {e}")

# ---------------- Main ----------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # /start command
    app.add_handler(CommandHandler("start", start))

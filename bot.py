import os
from telegram.ext import Updater, MessageHandler, Filters
from telegram import ChatMemberUpdated
from telegram.ext import CallbackContext

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

def member_update(update: ChatMemberUpdated, context: CallbackContext):
    if update.chat.id == CHANNEL_ID:
        old = update.old_chat_member
        new = update.new_chat_member

        if old.status in ["member", "restricted"] and new.status == "left":
            user_id = old.user.id
            try:
                context.bot.ban_chat_member(CHANNEL_ID, user_id)
                print(f"Banned user {user_id} for leaving the channel.")
            except Exception as e:
                print(f"Error banning user {user_id}: {e}")

def start_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.status_update, member_update))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    start_bot()

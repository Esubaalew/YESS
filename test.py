import asyncio
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from decouple import config

# Load the bot token from the .env file
TOKEN = config('TOKEN')

# Define states for conversation
ASK_MESSAGE = range(1)

# Group ID where the bot will send the message
GROUP_ID = -1002249761175  # Make sure to include the negative sign for groups


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any incoming messages to log the group chat details."""
    chat = update.effective_chat
    if chat.type in ['group', 'supergroup']:
        print(f"Message received from group: {chat.title} (ID: {chat.id})")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler."""
    await update.message.reply_text("Welcome! Use /sendmessage to send a message to the group.")


async def send_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask user for the message they want to send."""
    await update.message.reply_text(
        "Please enter the message you want to send to the group:",
        reply_markup=ForceReply(selective=True)
    )
    return ASK_MESSAGE


async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive the user's message and send it to the group."""
    message_to_send = update.message.text

    # Send the received message to the group
    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=message_to_send,
        message_thread_id=12
    )

    await update.message.reply_text("Your message has been sent to the group!")

    # End conversation after sending the message
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation."""
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END


if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    # Conversation handler to handle the send message flow
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('sendmessage', send_message_command)],
        states={
            ASK_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Register handlers
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    # Start polling for updates
    app.run_polling()

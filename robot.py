from decouple import config, UndefinedValueError
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler, ConversationHandler
from utils.db.tools import search_table_by_tg_id, insert_data

# Define states for the registration conversation
FIRST_NAME, LAST_NAME, GENDER, EMAIL, PHONE, ADDRESS, HIGHEST_EDUCATION, IS_EMPLOYED, NEEDS, BIO = range(10)

try:
    TOKEN = config('TOKEN')
except UndefinedValueError:
    print("Error: The TOKEN environment variable is not set.")
    exit(1)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    tg_id = update.effective_user.id
    is_registered = search_table_by_tg_id(tg_id)

    if is_registered:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome back!")
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="I'm YesRobot, an automated YesEthiopia client. Let's get to know each other! Please type /register "
                 "to start the registration."
        )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates the registration process."""
    if search_table_by_tg_id(update.effective_user.id):
        await update.message.reply_text("You are already registered.")
        return ConversationHandler.END
    await update.message.reply_text("Please enter your first name:")
    return FIRST_NAME


async def first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['first_name'] = update.message.text
    await update.message.reply_text("Please enter your last name:")
    return LAST_NAME


async def last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['last_name'] = update.message.text
    gender_keyboard = [['Male', 'Female']]
    await update.message.reply_text(
        "Please specify your gender:",
        reply_markup=ReplyKeyboardMarkup(gender_keyboard, one_time_keyboard=True)
    )
    return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['gender'] = update.message.text
    await update.message.reply_text("Please enter your email address:", reply_markup=ReplyKeyboardRemove())
    return EMAIL


async def email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text
    await update.message.reply_text("Please enter your phone number:")
    return PHONE


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Please enter your address:")
    return ADDRESS


async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text
    education_keyboard = [['High School', 'Undergraduate'], ['Graduate', 'Postgraduate']]
    await update.message.reply_text(
        "Please enter your highest education level:",
        reply_markup=ReplyKeyboardMarkup(education_keyboard, one_time_keyboard=True)
    )
    return HIGHEST_EDUCATION


async def highest_education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['highest_education'] = update.message.text
    employment_keyboard = [['Yes', 'No']]
    await update.message.reply_text(
        "Are you currently employed?",
        reply_markup=ReplyKeyboardMarkup(employment_keyboard, one_time_keyboard=True)
    )
    return IS_EMPLOYED


async def is_employed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['is_employed'] = update.message.text.lower() == 'yes'
    await update.message.reply_text("Please enter your needs (e.g., mentorship, job assistance):",
                                    reply_markup=ReplyKeyboardRemove())
    return NEEDS


async def needs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['needs'] = update.message.text
    await update.message.reply_text("Please provide a short bio:")
    return BIO


async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    username = update.effective_user.username
    first_name = context.user_data['first_name']
    last_name = context.user_data['last_name']
    gender = context.user_data['gender']
    email = context.user_data['email']
    phone = context.user_data['phone']
    address = context.user_data['address']
    highest_education = context.user_data['highest_education']
    is_employed = context.user_data['is_employed']
    needs = context.user_data['needs']
    bio = update.message.text

    data = (
        tg_id, username, first_name, last_name, gender, email, phone, address, highest_education, is_employed, needs,
        bio, None
    )
    insert_data(data)

    await update.message.reply_text("Registration complete! Thank you for providing your details.")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation."""
    await update.message.reply_text("Registration has been canceled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # Add a conversation handler for the registration process
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', register)],
        states={
            FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_name)],
            LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, last_name)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
            HIGHEST_EDUCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, highest_education)],
            IS_EMPLOYED: [MessageHandler(filters.TEXT & ~filters.COMMAND, is_employed)],
            NEEDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, needs)],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.COMMAND & ~filters.Regex('^/start$'), unknown))

    application.run_polling()

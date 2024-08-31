from decouple import config, UndefinedValueError
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler, ConversationHandler
from utils.db.tools import search_table_by_tg_id, insert_data
from utils.validation import is_valid_name, is_valid_email, is_valid_phone, is_valid_needs

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
        _, _, _, first_name, *rest = is_registered
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Welcome back, {first_name} 😊!")
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Selam 🙌 {update.effective_sender.first_name}! , I'm YesRobot, an automated YesEthiopia client. "
                 f"Let's get to know each other! Please type /register"
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
    name = update.message.text
    if is_valid_name(name):
        context.user_data['first_name'] = name
        await update.message.reply_text("Please enter your last name:")
        return LAST_NAME
    else:
        await update.message.reply_text(
            "Invalid first name. It should be at least 3 characters long and contain only letters. Please enter your "
            "first name again:")
        return FIRST_NAME


async def last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    if is_valid_name(name):
        context.user_data['last_name'] = name
        gender_keyboard = [['Male', 'Female']]
        await update.message.reply_text(
            "Please specify your gender:",
            reply_markup=ReplyKeyboardMarkup(gender_keyboard, one_time_keyboard=True)
        )
        return GENDER
    else:
        await update.message.reply_text(
            "Invalid last name. It should be at least 3 characters long and contain only letters. Please enter your "
            "last name again:")
        return LAST_NAME


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gender = update.message.text
    if gender in ['Male', 'Female']:
        context.user_data['gender'] = gender
        await update.message.reply_text("Please enter your email address:", reply_markup=ReplyKeyboardRemove())
        return EMAIL
    else:
        await update.message.reply_text("Invalid gender. Please choose from the keyboard options.")
        return GENDER


async def email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    if is_valid_email(email):
        context.user_data['email'] = email
        await update.message.reply_text("Please enter your phone number:")
        return PHONE
    else:
        await update.message.reply_text("Invalid email format. Please enter a valid email address:")
        return EMAIL


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if is_valid_phone(phone):
        context.user_data['phone'] = phone
        await update.message.reply_text("Please enter your address:")
        return ADDRESS
    else:
        await update.message.reply_text("Invalid phone number. Please enter a valid phone number with country code:")
        return PHONE


async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text
    education_keyboard = [['High School', 'Undergraduate'], ['Graduate', 'Postgraduate']]
    await update.message.reply_text(
        "Please enter your highest education level:",
        reply_markup=ReplyKeyboardMarkup(education_keyboard, one_time_keyboard=True)
    )
    return HIGHEST_EDUCATION


async def highest_education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    highest_education = update.message.text
    if highest_education in ['High School', 'Undergraduate', 'Graduate', 'Postgraduate']:
        context.user_data['highest_education'] = highest_education
        employment_keyboard = [['Yes', 'No']]
        await update.message.reply_text(
            "Are you currently employed?",
            reply_markup=ReplyKeyboardMarkup(employment_keyboard, one_time_keyboard=True)
        )
        return IS_EMPLOYED
    else:
        await update.message.reply_text("Invalid education level. Please choose from the keyboard options.")
        return HIGHEST_EDUCATION


async def is_employed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_employed = update.message.text.lower()
    if is_employed in ['yes', 'no']:
        context.user_data['is_employed'] = is_employed == 'yes'
        await update.message.reply_text("Please enter your needs (e.g., mentorship, job assistance):",
                                        reply_markup=ReplyKeyboardRemove())
        return NEEDS
    else:
        await update.message.reply_text("Invalid response. Please enter 'yes' or 'no'.")
        return IS_EMPLOYED


async def needs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    needs = update.message.text
    if is_valid_needs(needs):
        context.user_data['needs'] = needs
        await update.message.reply_text("Please provide a short bio:")
        return BIO
    else:
        await update.message.reply_text(
            "Invalid input. Needs should only contain letters and spaces. Please enter your needs again:")
        return NEEDS


async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bio = update.message.text
    if 10 <= len(bio) <= 300:  # Adjust limits as needed
        tg_id = update.effective_user.id
        username = update.effective_user.username
        first_name = context.user_data['first_name'].title()
        last_name = context.user_data['last_name'].title()
        gender = context.user_data['gender']
        email = context.user_data['email']
        phone = context.user_data['phone']
        address = context.user_data['address']
        highest_education = context.user_data['highest_education']
        is_employed = context.user_data['is_employed']
        needs = context.user_data['needs']

        data = (
            tg_id, username, first_name, last_name, gender, email, phone, address, highest_education, is_employed,
            needs,
            bio, None
        )
        insert_data(data)

        await update.message.reply_text("Registration complete! Thank you for providing your details.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Bio should be between 10 and 300 characters. Please provide a valid bio:")
        return BIO


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

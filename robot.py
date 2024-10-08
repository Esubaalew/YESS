from decouple import config, UndefinedValueError
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, \
    ChatMember
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler, ConversationHandler, \
    CallbackQueryHandler
from telegram.error import BadRequest
from utils.db.tools import search_table_by_tg_id, insert_data, search_table_by_email, search_table_by_phone, \
    is_joined_group
from utils.send_email import send_email
from utils.send_sms import send_sms

from utils.validation import is_valid_name, is_valid_email, is_valid_phone, is_valid_needs

# Define states for the registration conversation
FIRST_NAME, LAST_NAME, GENDER, EMAIL, PHONE, ADDRESS, HIGHEST_EDUCATION, IS_EMPLOYED, NEEDS, BIO = range(10)
ASK_MESSAGE, CHOOSE_TOPIC = range(10, 12)

try:
    TOKEN = config('TOKEN')
except UndefinedValueError:
    print("Error: The TOKEN environment variable is not set.")
    exit(1)
CHANNEL_USERNAME = "@yess_Ethiopic"
GROUP_ID = -1002249761175

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
                 "  to start the registration."
        )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


async def introduce(context: ContextTypes.DEFAULT_TYPE, user_data):
    """Introduce the new registered user to the group."""
    tg_id = user_data['tg_id']
    user_info = search_table_by_tg_id(tg_id)


    if user_info:
        first_name = user_info[3]
        last_name = user_info[4]
        highest_education = user_info[9]
        is_employed = "Employed" if user_info[10] else "Unemployed"
        address = user_info[8]

        introduction_message = (
            f"👋 Welcome our new member!\n"
            f"My name is {first_name} {last_name}.\n"
            f"My highest education level is {highest_education}.\n"
            f"I am currently {is_employed}.\n"
            f"I live in {address}.\n"

            f"Looking forward to contributing to YesEthiopia!"
        )

        await context.bot.send_message(chat_id=GROUP_ID, text=introduction_message)


async def send_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask user to choose a topic to send a message to."""
    tg_id = update.effective_user.id

    # Check if the user is registered
    is_registered = search_table_by_tg_id(tg_id)
    if not is_registered:
        await update.message.reply_text("You need to be registered to use this feature. Please use /register to start "
                                        "the registration process.")
        return

    # Check if the user has joined the channel
    user_status = await check_user_status(update, context)
    if user_status == "error":
        await update.message.reply_text("An error occurred. Please try again later.")
        return

    if user_status not in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
        await update.message.reply_text(
            f"Your current status: {user_status}\nPlease join {CHANNEL_USERNAME} before using the bot."
        )
        await send_join_channel_button(update.message.chat_id, context)
        return

    # Display topic selection keyboard
    keyboard = [
        [
            InlineKeyboardButton("General", callback_data="1"),
            InlineKeyboardButton("Employment", callback_data="7"),
        ],
        [
            InlineKeyboardButton("Training", callback_data="23"),
            InlineKeyboardButton("Business Idea", callback_data="5"),
            InlineKeyboardButton("Scholarship", callback_data="2"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Choose the topic for your message:", reply_markup=reply_markup
    )
    return CHOOSE_TOPIC


async def choose_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user's choice of topic and ask for the message content."""
    query = update.callback_query
    await query.answer()

    # Store chosen topic ID
    context.user_data["topic_id"] = query.data

    # Provide feedback to the user
    topic_name = {
        "1": "General",
        "7": "Employment",
        "23": "Training",
        "5": "Business Idea",
        "2": "Scholarship",
    }.get(query.data, "Unknown Topic")

    await query.edit_message_text(
        text=f"You chose {topic_name}. Please enter the message related to {topic_name}:"
    )

    return ASK_MESSAGE


async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive the user's message and send it to the group under the selected topic."""
    message_to_send = update.message.text
    topic_id = context.user_data.get("topic_id")
    tg_id = update.effective_user.id

    # Check if user is registered
    is_registered = search_table_by_tg_id(tg_id)
    if not is_registered:
        await update.message.reply_text("You need to be registered to send messages. Please use /register to start "
                                        "the registration process.")
        return ConversationHandler.END

    # Check if the user has joined the channel
    user_status = await check_user_status(update, context)
    if user_status not in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
        await send_join_channel_button(update.message.chat_id, context)
        await update.message.reply_text("Message failed. Please join our channel and try again.")
        return ConversationHandler.END

    # Send message based on topic selection
    if topic_id == "1":
        # Special case for "General" topic
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=message_to_send
        )
    else:
        # Send the message to the group with the specified thread ID
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=message_to_send,
            message_thread_id=int(topic_id),
        )

    await update.message.reply_text("Your message has been sent to the group!")
    return ConversationHandler.END


async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation."""
    await update.message.reply_text("Operation cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates the registration process."""
    user_status = await check_user_status(update, context)
    if user_status == "error":
        await update.message.reply_text("An error occurred. Please try again later.")
        return
    if user_status not in [
        ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER
    ]:
        await update.message.reply_text(
            f"Your current status: {user_status}\nPlease join {CHANNEL_USERNAME} before using the bot."
        )
        await send_join_channel_button(update.message.chat_id, context)
        return
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
        if search_table_by_email(email.lower()):
            await update.message.reply_text("This email is already in use. Please enter a different email address:")
            return EMAIL
        else:
            context.user_data['email'] = email
            await update.message.reply_text("Please enter your phone number:")
            return PHONE
    else:
        await update.message.reply_text("Invalid email format. Please enter a valid email address:")
        return EMAIL


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if is_valid_phone(phone):
        if search_table_by_phone(phone):
            await update.message.reply_text(
                "This phone number is already in use. Please enter a different phone number:")
            return PHONE
        else:
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

        user_status = await check_user_status(update, context)
        if user_status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
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
                needs, bio, None
            )
            insert_data(data)

            await update.message.reply_text("Registration complete! Thank you for providing your details.")
            send_email(email, "Welcome to YesEthiopia", f"Dear {first_name} {last_name}, your registration to "
                                                        f"YesEthiopia was successful. YesRobot will inform "
                                                        f"your details to the admin.")

            # Call the introduce function to announce the new user
            await introduce(context, {'tg_id': tg_id})
            return ConversationHandler.END
        else:
            await send_join_channel_button(update.effective_chat.id, context)
            await update.message.reply_text("Registration failed, Please join our channel to complete your "
                                            "registration.")
            return ConversationHandler.END
    else:
        await update.message.reply_text("Bio should be between 10 and 300 characters. Please provide a valid bio:")
        return BIO


async def send_join_channel_button(chat_id, context):
    button = InlineKeyboardButton("Join Channel", url="https://t.me/yess_Ethiopic")
    keyboard = [[button]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id,
                                   text="To use this bot, please join our channel:",
                                   reply_markup=reply_markup)


async def check_user_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_id = update.effective_user.id
    try:
        chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME,
                                                        user_id=user_id)

        user_status = chat_member.status
        print(f"User status: {user_status}")
        return user_status
    except BadRequest as e:
        print(f"Error: {e}")
        return "error"


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation."""
    await update.message.reply_text("Registration has been canceled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    # Add a conversation handler for the registration process
    registration_handler = ConversationHandler(
        entry_points=[CommandHandler("register", register)],
        states={
            FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_name)],
            LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, last_name)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
            HIGHEST_EDUCATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, highest_education)
            ],
            IS_EMPLOYED: [MessageHandler(filters.TEXT & ~filters.COMMAND, is_employed)],
            NEEDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, needs)],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Conversation handler to handle the message send flow
    send_message_handler = ConversationHandler(
        entry_points=[CommandHandler("sendmessage", send_message_command)],
        states={
            CHOOSE_TOPIC: [CallbackQueryHandler(choose_topic)],
            ASK_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message)],
        },
        fallbacks=[CommandHandler("leave", leave)],
    )

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(registration_handler)
    application.add_handler(send_message_handler)
    application.add_handler(MessageHandler(filters.COMMAND & ~filters.Regex("^/start$"), unknown))
    application.add_handler(MessageHandler(filters.ALL, echo))
    application.add_handler(CallbackQueryHandler(choose_topic))
    application.run_polling()

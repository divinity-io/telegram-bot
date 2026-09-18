from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

from database import save_user, get_user
from languages import get_text


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    try:
        existing_user = get_user(user.id)

        save_user(user)

        language = "English"

        if existing_user:
            language = existing_user[0].get("language", "English")

            await update.message.reply_text(
                f"{get_text('welcome_back', language, name=user.first_name)}\n\n"
                f"{get_text('already_registered', language)}\n\n"
                "Use /menu to open the control center.",
                reply_markup=ReplyKeyboardRemove()
            )

        else:
            await update.message.reply_text(
                f"{get_text('welcome', language, name=user.first_name)}\n\n"
                f"{get_text('registered', language)}\n\n"
                "Use /menu to open the control center.",
                reply_markup=ReplyKeyboardRemove()
            )

    except Exception as e:
        print(f"Database error: {e}")

        await update.message.reply_text(
            "👋 Welcome to DiviCore!\n\n"
            "⚠️ I couldn't access your profile right now.",
            reply_markup=ReplyKeyboardRemove()
        )

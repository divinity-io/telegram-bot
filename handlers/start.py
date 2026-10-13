from telegram import (
    Update,
    ReplyKeyboardMarkup,
)
from telegram.ext import ContextTypes

from database import save_user, get_user
from languages import get_text


def dashboard_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["🏠 Dashboard", "👤 My Profile"],
            ["🧰 Tools", "📜 History"],
            ["⭐ Favorites", "⚙️ Settings"],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Choose a DCORE feature...",
    )


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user = update.effective_user

    try:
        existing_user = get_user(user.id)
        save_user(user)

        language = "English"

        if existing_user:
            language = existing_user[0].get(
                "language", "English"
            )
            message = (
                f"{get_text('welcome_back', language, name=user.first_name)}\n\n"
                f"{get_text('already_registered', language)}\n\n"
                "Use the buttons below to open your dashboard."
            )
        else:
            message = (
                f"{get_text('welcome', language, name=user.first_name)}\n\n"
                f"{get_text('registered', language)}\n\n"
                "Use the buttons below to open your dashboard."
            )

        await update.effective_message.reply_text(
            message,
            reply_markup=dashboard_keyboard()
        )

    except Exception as e:
        print(f"Database error: {e}")

        await update.effective_message.reply_text(
            "👋 Welcome to DCORE!\n\n"
            "⚠️ I couldn't access your profile right now. "
            "Please try again later.",
            reply_markup=dashboard_keyboard()
        )

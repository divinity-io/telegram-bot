import os

from dotenv import load_dotenv
from telegram import BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
)

from handlers.start import start
from handlers.commands import help_command, about_command
from handlers.buttons import button_handler, show_menu

from handlers.tools import (
    tools_command,
    calculator,
    password_generator,
    base64_encode,
    base64_decode,
    json_formatter,
    timestamp_converter,
    qr_generator,
    url_checker,
    ip_information,
    hash_generator,
)


# Load environment variables
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


if not TOKEN:
    raise ValueError(
        "BOT_TOKEN is missing from your .env file."
    )


# Telegram native command menu
async def set_commands(application):
    commands = [
        BotCommand("start", "Start DiviCore"),
        BotCommand("menu", "Open control center"),
        BotCommand("tools", "Developer toolkit"),

        BotCommand("calc", "Calculator"),
        BotCommand("password", "Generate secure password"),

        BotCommand("base64encode", "Encode text with Base64"),
        BotCommand("base64decode", "Decode Base64"),

        BotCommand("json", "Format JSON"),
        BotCommand("timestamp", "Convert Unix timestamp"),

        BotCommand("qr", "Generate QR code"),
        BotCommand("url", "Check a URL"),
        BotCommand("ipinfo", "Get IP information"),
        BotCommand("hash", "Generate SHA-256 hash"),

        BotCommand("help", "Show help"),
        BotCommand("about", "About DiviCore"),
    ]

    await application.bot.set_my_commands(commands)


# Create application
application = (
    Application
    .builder()
    .token(TOKEN)
    .post_init(set_commands)
    .build()
)


# =========================
# GENERAL COMMANDS
# =========================

application.add_handler(
    CommandHandler("start", start)
)

application.add_handler(
    CommandHandler("menu", show_menu)
)

application.add_handler(
    CommandHandler("help", help_command)
)

application.add_handler(
    CommandHandler("about", about_command)
)


# =========================
# DEVELOPER TOOLS
# =========================

application.add_handler(
    CommandHandler("tools", tools_command)
)

application.add_handler(
    CommandHandler("calc", calculator)
)

application.add_handler(
    CommandHandler("password", password_generator)
)

application.add_handler(
    CommandHandler("base64encode", base64_encode)
)

application.add_handler(
    CommandHandler("base64decode", base64_decode)
)

application.add_handler(
    CommandHandler("json", json_formatter)
)

application.add_handler(
    CommandHandler("timestamp", timestamp_converter)
)

application.add_handler(
    CommandHandler("qr", qr_generator)
)

application.add_handler(
    CommandHandler("url", url_checker)
)

application.add_handler(
    CommandHandler("ipinfo", ip_information)
)

application.add_handler(
    CommandHandler("hash", hash_generator)
)


# =========================
# INLINE BUTTONS
# =========================

application.add_handler(
    CallbackQueryHandler(button_handler)
)


# =========================
# START BOT
# =========================

print("🚀 DiviCore is running...")

application.run_polling()

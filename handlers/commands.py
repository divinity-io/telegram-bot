from telegram import Update
from telegram.ext import ContextTypes

from database import get_user
from languages import get_text


def get_language(user_id):
    profile = get_user(user_id)

    if profile:
        return profile[0].get("language", "English")

    return "English"


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user = update.effective_user
    language = get_language(user.id)

    help_text = f"""{get_text('help', language)}

🤖 DCORE Commands

/start
→ Register your account and start DCORE.

/menu
→ Open the DCORE Control Center.

/help
→ Show this help page.

/about
→ Learn about DCORE, how it works, and its developer.

⚙️ Control Center

👤 Profile
→ View your DCORE account information.

⚙️ Settings
→ Manage your DCORE preferences.

🔔 Notifications
→ Turn notifications ON or OFF.

🌐 Language
→ Change the language used by DCORE.

ℹ️ About
→ Learn more about the project and its developer.

🚀 DCORE
→ Check the current bot status.

💡 Tip

You can use the buttons inside /menu to navigate DCORE without typing commands.

🚀 More features will be added as DCORE continues to grow.
"""

    await update.message.reply_text(help_text)


async def about_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user = update.effective_user
    language = get_language(user.id)

    await update.message.reply_text(
        get_text("about", language)
    )
